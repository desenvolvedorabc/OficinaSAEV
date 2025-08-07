#!/usr/bin/env python3
"""
Script para carregar dados dos arquivos Excel de alunos ES 
para a tabela alunos_es no banco DuckDB.

Arquivos de entrada:
- diag_ES_alunos_testes.xlsx  (833.564 registros)
- form1_ES_alunos_testes.xlsx (827.099 registros)

Total: ~1.6 milhões de registros (TODOS os registros, incluindo duplicatas)

Autor: Sistema SAEV
Data: 07/08/2025
"""

import pandas as pd
import duckdb
import sys
from pathlib import Path
import logging
from typing import List, Tuple

def setup_logging():
    """Configurar logging para acompanhar o processo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def validate_files():
    """Validar se os arquivos necessários existem"""
    excel_files = [
        Path("data/test/diag_ES_alunos_testes.xlsx"),
        Path("data/test/form1_ES_alunos_testes.xlsx")
    ]
    db_file = Path("db/avaliacao_prod.duckdb")
    
    for excel_file in excel_files:
        if not excel_file.exists():
            raise FileNotFoundError(f"❌ Arquivo Excel não encontrado: {excel_file}")
    
    if not db_file.exists():
        raise FileNotFoundError(f"❌ Banco de dados não encontrado: {db_file}")
    
    return excel_files, db_file

def load_excel_files(excel_files: List[Path]) -> pd.DataFrame:
    """Carregar e combinar dados dos arquivos Excel"""
    logger = logging.getLogger(__name__)
    
    dataframes = []
    total_records = 0
    
    for excel_file in excel_files:
        logger.info(f"📊 Carregando arquivo: {excel_file.name}")
        
        try:
            df = pd.read_excel(excel_file)
            
            # Validar colunas esperadas
            expected_columns = ['MUN_UF', 'MUN_NOME', 'ESC_ID', 'ESC_INEP', 'ESC_NOME', 
                              'SER_NOME', 'DIS_NOME', 'ALT_ALU_ID', 'ALU_NOME']
            missing_columns = set(expected_columns) - set(df.columns)
            
            if missing_columns:
                raise ValueError(f"❌ Colunas ausentes em {excel_file.name}: {missing_columns}")
            
            # Aplicar conversões de tipos conforme DDL
            df = convert_data_types(df)
            
            logger.info(f"✅ {excel_file.name}: {len(df):,} registros carregados")
            dataframes.append(df)
            total_records += len(df)
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar {excel_file.name}: {e}")
            raise
    
    # Combinar todos os DataFrames
    logger.info(f"🔗 Combinando {len(dataframes)} arquivos...")
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    logger.info(f"✅ Total combinado: {len(combined_df):,} registros")
    logger.info(f"📊 Mantendo TODOS os registros (incluindo múltiplas avaliações por aluno)")
    
    # Verificar duplicatas por ALT_ALU_ID apenas para informação (NÃO remover)
    duplicates = combined_df['ALT_ALU_ID'].duplicated().sum()
    unique_students = combined_df['ALT_ALU_ID'].nunique()
    if duplicates > 0:
        logger.info(f"📊 {duplicates} registros com ALT_ALU_ID repetido encontrados")
        logger.info(f"🎓 {unique_students} alunos únicos com múltiplas avaliações")
        logger.info(f"📚 Mantendo todos os registros para preservar histórico de avaliações")
    
    return combined_df

def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Converter tipos de dados conforme especificação da tabela"""
    logger = logging.getLogger(__name__)
    
    try:
        # Conversões conforme DDL:
        # MUN_UF CHAR(2) -> string limitada a 2 caracteres
        df['MUN_UF'] = df['MUN_UF'].astype(str).str[:2]
        
        # MUN_NOME VARCHAR(60) -> string limitada a 60 caracteres  
        df['MUN_NOME'] = df['MUN_NOME'].astype(str).str[:60]
        
        # ESC_ID INTEGER -> garantir tipo inteiro
        df['ESC_ID'] = pd.to_numeric(df['ESC_ID'], errors='coerce').astype('Int64')
        
        # ESC_INEP VARCHAR -> string (mantendo ESC_INEO conforme DDL fornecido)
        df['ESC_INEP'] = df['ESC_INEP'].astype(str)
        
        # ESC_NOME VARCHAR -> string
        df['ESC_NOME'] = df['ESC_NOME'].astype(str)
        
        # SER_NOME VARCHAR -> string
        df['SER_NOME'] = df['SER_NOME'].astype(str)
        
        # DIS_NOME VARCHAR -> string
        df['DIS_NOME'] = df['DIS_NOME'].astype(str)
        
        # ALT_ALU_ID INTEGER -> garantir tipo inteiro
        df['ALT_ALU_ID'] = pd.to_numeric(df['ALT_ALU_ID'], errors='coerce').astype('Int64')
        
        # ALU_NOME VARCHAR -> string
        df['ALU_NOME'] = df['ALU_NOME'].astype(str)
        
        logger.info("✅ Conversões de tipos aplicadas")
        
        # Verificar valores nulos após conversões
        null_counts = df.isnull().sum()
        if null_counts.any():
            logger.warning("⚠️ Valores nulos após conversões:")
            for col, count in null_counts[null_counts > 0].items():
                logger.warning(f"   {col}: {count} valores nulos")
        
        return df
        
    except Exception as e:
        logger.error(f"❌ Erro nas conversões de tipos: {e}")
        raise

def create_or_recreate_table(conn):
    """Criar ou recriar a tabela alunos_es"""
    logger = logging.getLogger(__name__)
    
    try:
        # Verificar se a tabela existe
        tables = conn.execute("SHOW TABLES").fetchall()
        table_names = [table[0] for table in tables]
        
        if 'alunos_es' in table_names:
            logger.info("📊 Tabela alunos_es existe - verificando registros...")
            count = conn.execute("SELECT COUNT(*) FROM alunos_es").fetchone()[0]
            logger.info(f"🗂️ Registros existentes: {count:,}")
            
            # Limpar tabela
            conn.execute("DELETE FROM alunos_es")
            logger.info("🗑️ Tabela limpa")
        else:
            # Criar tabela conforme DDL fornecido (com ESC_INEO)
            logger.info("🏗️ Criando tabela alunos_es...")
            create_table_sql = """
            CREATE TABLE alunos_es (
                MUN_UF CHAR(2),
                MUN_NOME VARCHAR(60),
                ESC_ID INTEGER,
                ESC_INEO VARCHAR,
                ESC_NOME VARCHAR,
                SER_NOME VARCHAR,
                DIS_NOME VARCHAR,
                ALT_ALU_ID INTEGER,
                ALU_NOME VARCHAR
            )
            """
            conn.execute(create_table_sql)
            logger.info("✅ Tabela criada com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar/limpar tabela: {e}")
        raise

def insert_data(conn, df: pd.DataFrame):
    """Inserir dados do DataFrame na tabela"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("📥 Iniciando inserção de dados...")
        logger.info(f"📊 Total de registros para inserir: {len(df):,}")
        
        # Preparar query de inserção (usando ESC_INEO conforme DDL)
        insert_query = """
        INSERT INTO alunos_es (MUN_UF, MUN_NOME, ESC_ID, ESC_INEO, ESC_NOME, 
                              SER_NOME, DIS_NOME, ALT_ALU_ID, ALU_NOME)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Converter DataFrame para lista de tuplas, tratando NaN
        data_tuples = []
        for _, row in df.iterrows():
            tuple_row = tuple(
                None if pd.isna(value) else value 
                for value in row
            )
            data_tuples.append(tuple_row)
        
        # Inserir dados em lotes para melhor performance
        batch_size = 5000  # Lotes maiores para arquivos grandes
        total_inserted = 0
        
        logger.info(f"🔄 Inserindo em lotes de {batch_size:,} registros...")
        
        for i in range(0, len(data_tuples), batch_size):
            batch = data_tuples[i:i + batch_size]
            conn.executemany(insert_query, batch)
            total_inserted += len(batch)
            
            # Log a cada 100k registros
            if total_inserted % 100000 == 0 or total_inserted == len(data_tuples):
                progress = (total_inserted / len(data_tuples)) * 100
                logger.info(f"📝 Inseridos {total_inserted:,}/{len(data_tuples):,} registros ({progress:.1f}%)")
        
        # Confirmar inserção
        final_count = conn.execute("SELECT COUNT(*) FROM alunos_es").fetchone()[0]
        logger.info(f"✅ Inserção concluída! Total de registros na tabela: {final_count:,}")
        
        # Estatísticas finais
        stats_query = """
        SELECT 
            COUNT(*) as total_registros,
            COUNT(DISTINCT ESC_ID) as total_escolas,
            COUNT(DISTINCT MUN_NOME) as total_municipios,
            COUNT(DISTINCT ALT_ALU_ID) as alunos_unicos
        FROM alunos_es
        """
        stats = conn.execute(stats_query).fetchone()
        logger.info(f"📊 Estatísticas finais:")
        logger.info(f"   � Total de registros: {stats[0]:,}")
        logger.info(f"   🏫 Escolas únicas: {stats[1]:,}")
        logger.info(f"   🏛️ Municípios únicos: {stats[2]:,}")
        logger.info(f"   🎓 Alunos únicos: {stats[3]:,}")
        logger.info(f"   📚 Média de registros por aluno: {stats[0]/stats[3]:.1f}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados: {e}")
        raise

def connect_database(db_file: Path):
    """Conectar ao banco DuckDB"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🔗 Conectando ao banco: {db_file}")
        
        # Tentar conexão com tratamento de lock
        try:
            conn = duckdb.connect(str(db_file))
        except Exception as e:
            if "Conflicting lock" in str(e):
                logger.error("❌ Banco está bloqueado por outro processo (DBeaver, etc.)")
                logger.error("💡 Feche o DBeaver ou outros clientes conectados ao banco")
                raise ValueError("Banco bloqueado por outro processo")
            else:
                raise
        
        logger.info("✅ Conexão estabelecida com sucesso")
        return conn
        
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao banco: {e}")
        raise

def main():
    """Função principal"""
    logger = setup_logging()
    
    try:
        logger.info("🚀 Iniciando carregamento de dados alunos ES")
        logger.info("📂 Arquivos: diag_ES_alunos_testes.xlsx + form1_ES_alunos_testes.xlsx")
        logger.info("🎯 Destino: Tabela alunos_es")
        logger.info("📚 MODO: Mantendo TODOS os registros (incluindo múltiplas avaliações)")
        logger.info("=" * 70)
        
        # 1. Validar arquivos
        excel_files, db_file = validate_files()
        
        # 2. Carregar e combinar dados dos Excel
        combined_df = load_excel_files(excel_files)
        
        # 3. Conectar ao banco
        conn = connect_database(db_file)
        
        # 4. Criar/limpar tabela
        create_or_recreate_table(conn)
        
        # 5. Inserir dados
        insert_data(conn, combined_df)
        
        # 6. Fechar conexão
        conn.close()
        
        logger.info("=" * 70)
        logger.info("🎉 Carregamento concluído com sucesso!")
        logger.info(f"📊 {len(combined_df):,} registros de alunos ES carregados")
        
    except Exception as e:
        logger.error(f"💥 Erro durante o processo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

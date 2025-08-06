#!/usr/bin/env python3
"""
Script para carregar dados da planilha escolas_es_saev.xlsx 
para a tabela escolas_es_saev no banco DuckDB.

Autor: Sistema SAEV
Data: 06/08/2025
"""

import pandas as pd
import duckdb
import sys
from pathlib import Path
import logging

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
    excel_file = Path("data/test/escolas_es_saev.xlsx")
    db_file = Path("db/avaliacao_prod.duckdb")
    
    if not excel_file.exists():
        raise FileNotFoundError(f"❌ Planilha não encontrada: {excel_file}")
    
    if not db_file.exists():
        raise FileNotFoundError(f"❌ Banco de dados não encontrado: {db_file}")
    
    return excel_file, db_file

def load_excel_data(excel_file):
    """Carregar dados da planilha Excel"""
    logger = logging.getLogger(__name__)
    
    logger.info(f"📊 Carregando planilha: {excel_file}")
    
    try:
        df = pd.read_excel(excel_file)
        logger.info(f"✅ Planilha carregada: {df.shape[0]} linhas x {df.shape[1]} colunas")
        
        # Validar colunas esperadas
        expected_columns = ['MUN_UF', 'MUN_ID', 'MUN_NOME', 'ESC_ID', 'ESC_INEP', 'ESC_NOME']
        missing_columns = set(expected_columns) - set(df.columns)
        
        if missing_columns:
            raise ValueError(f"❌ Colunas ausentes na planilha: {missing_columns}")
        
        # Filtrar apenas o estado do Espírito Santo (ES)
        total_before = len(df)
        df = df[df['MUN_UF'] == 'ES'].copy()
        logger.info(f"🎯 Filtrado para ES: {len(df)} linhas (de {total_before} originais)")
        
        if len(df) == 0:
            raise ValueError("❌ Nenhum registro encontrado para o estado ES")
        
        # Verificar dados nulos
        null_counts = df.isnull().sum()
        if null_counts.any():
            logger.warning("⚠️ Dados nulos encontrados:")
            for col, count in null_counts[null_counts > 0].items():
                logger.warning(f"   {col}: {count} valores nulos")
        
        # Mostrar algumas estatísticas
        logger.info(f"📋 Colunas: {list(df.columns)}")
        logger.info(f"🏫 Escolas únicas (ES): {df['ESC_ID'].nunique()}")
        logger.info(f"🏛️ Municípios únicos (ES): {df['MUN_ID'].nunique()}")
        
        return df
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar planilha: {e}")
        raise

def connect_database(db_file):
    """Conectar ao banco DuckDB"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🔗 Conectando ao banco: {db_file}")
        
        # Tentar conexão com timeout
        try:
            conn = duckdb.connect(str(db_file))
        except Exception as e:
            if "Conflicting lock" in str(e):
                logger.error("❌ Banco está bloqueado por outro processo (DBeaver, etc.)")
                logger.error("💡 Feche o DBeaver ou outros clientes conectados ao banco")
                logger.error(f"🔍 Erro detalhado: {e}")
                raise ValueError("Banco bloqueado por outro processo")
            else:
                raise
        
        # Verificar se a tabela existe
        tables = conn.execute("SHOW TABLES").fetchall()
        table_names = [table[0] for table in tables]
        
        if 'escolas_es_saev' not in table_names:
            raise ValueError("❌ Tabela 'escolas_es_saev' não encontrada no banco")
        
        logger.info("✅ Conexão estabelecida e tabela encontrada")
        return conn
        
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao banco: {e}")
        raise

def clear_table(conn):
    """Limpar dados existentes na tabela (automático para carga limpa)"""
    logger = logging.getLogger(__name__)
    
    try:
        # Verificar quantos registros existem
        count_before = conn.execute("SELECT COUNT(*) FROM escolas_es_saev").fetchone()[0]
        logger.info(f"📊 Registros existentes na tabela: {count_before}")
        
        if count_before > 0:
            conn.execute("DELETE FROM escolas_es_saev")
            logger.info(f"🗑️ Tabela limpa - {count_before} registros removidos")
        else:
            logger.info("ℹ️ Tabela já estava vazia")
        
    except Exception as e:
        logger.error(f"❌ Erro ao limpar tabela: {e}")
        raise

def insert_data(conn, df):
    """Inserir dados do DataFrame na tabela"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("📥 Iniciando inserção de dados...")
        
        # Preparar query de inserção
        insert_query = """
        INSERT INTO escolas_es_saev (MUN_UF, MUN_ID, MUN_NOME, ESC_ID, ESC_INEP, ESC_NOME)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        # Converter DataFrame para lista de tuplas
        data_tuples = list(df.itertuples(index=False, name=None))
        
        # Inserir dados em lotes para melhor performance
        batch_size = 1000
        total_inserted = 0
        
        for i in range(0, len(data_tuples), batch_size):
            batch = data_tuples[i:i + batch_size]
            conn.executemany(insert_query, batch)
            total_inserted += len(batch)
            logger.info(f"📝 Inseridos {total_inserted}/{len(data_tuples)} registros...")
        
        # Confirmar inserção
        final_count = conn.execute("SELECT COUNT(*) FROM escolas_es_saev").fetchone()[0]
        logger.info(f"✅ Inserção concluída! Total de registros na tabela: {final_count}")
        
        # Mostrar algumas estatísticas
        stats_query = """
        SELECT 
            COUNT(*) as total_escolas,
            COUNT(DISTINCT MUN_ID) as total_municipios,
            COUNT(DISTINCT MUN_UF) as total_ufs
        FROM escolas_es_saev
        """
        stats = conn.execute(stats_query).fetchone()
        logger.info(f"📊 Estatísticas finais:")
        logger.info(f"   🏫 Total de escolas (ES): {stats[0]}")
        logger.info(f"   🏛️ Total de municípios (ES): {stats[1]}")
        logger.info(f"   🗺️ Total de UFs: {stats[2]} (deve ser 1 - ES)")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados: {e}")
        raise

def main():
    """Função principal"""
    logger = setup_logging()
    
    try:
        logger.info("🚀 Iniciando carregamento de dados escolas_es_saev")
        logger.info("🎯 FOCO: Apenas estado do Espírito Santo (ES)")
        logger.info("🗑️ MODO: Limpeza automática da tabela antes de inserir")
        logger.info("=" * 60)
        
        # 1. Validar arquivos
        excel_file, db_file = validate_files()
        
        # 2. Carregar dados da planilha
        df = load_excel_data(excel_file)
        
        # 3. Conectar ao banco
        conn = connect_database(db_file)
        
        # 4. Limpar tabela (automático)
        clear_table(conn)
        
        # 5. Inserir dados
        insert_data(conn, df)
        
        # 6. Fechar conexão
        conn.close()
        
        logger.info("=" * 60)
        logger.info("🎉 Carregamento concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"💥 Erro durante o processo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

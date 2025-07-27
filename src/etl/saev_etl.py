"""
Módulo ETL (Extract, Transform, Load) para o Sistema SAEV
========================================================

Este módulo é responsável por:
1. Extrair dados dos arquivos CSV
2. Transformar os dados conforme necessário
3. Carregar no banco DuckDB
4. Criar estrutura Star Schema

Autor: Sistema SAEV
Data: 2025
"""

import os
import glob
import pandas as pd
import duckdb
from pathlib import Path
from datetime import datetime
import hashlib
import json
from typing import List, Dict, Optional, Tuple
import logging

# Configuração de logging
console_handler = logging.StreamHandler(sys.stdout, encoding='utf-8')
file_handler = logging.FileHandler('etl.log', encoding='utf-8')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        file_handler,
        console_handler
    ]
)
logger = logging.getLogger(__name__)

class SAEVETLProcessor:
    """
    Processador ETL para dados do Sistema SAEV
    """
    
    def __init__(self, db_path: str = "db/avaliacao_prod.duckdb", data_path: str = "data/raw"):
        """
        Inicializa o processador ETL
        
        Args:
            db_path: Caminho para o banco DuckDB
            data_path: Caminho para os arquivos CSV
        """
        self.db_path = db_path
        self.data_path = data_path
        self.metadata_file = "etl_metadata.json"
        
        # Cria diretórios se não existirem
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(data_path, exist_ok=True)
        
        # Schema das colunas esperadas
        self.expected_columns = [
            "MUN_UF", "MUN_NOME", "ESC_INEP", "ESC_NOME", "SER_NUMBER", "SER_NOME",
            "TUR_PERIODO", "TUR_NOME", "ALU_ID", "ALU_NOME", "ALU_CPF", "AVA_NOME",
            "AVA_ANO", "DIS_NOME", "TES_NOME", "TEG_ORDEM", "ATR_RESPOSTA", 
            "ATR_CERTO", "MTI_CODIGO", "MTI_DESCRITOR"
        ]
        
        # Conecta ao banco
        self.conn = duckdb.connect(self.db_path)
        logger.info(f"Conectado ao banco: {self.db_path}")
    
    def get_csv_files(self) -> List[str]:
        """
        Retorna lista de arquivos CSV no diretório de dados
        """
        pattern = os.path.join(self.data_path, "*.csv")
        files = glob.glob(pattern)
        logger.info(f"Encontrados {len(files)} arquivos CSV")
        return files
    
    def calculate_file_hash(self, filepath: str) -> str:
        """
        Calcula hash MD5 do arquivo para detectar mudanças
        """
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def load_metadata(self) -> Dict:
        """
        Carrega metadados de processamento anterior
        """
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"processed_files": {}, "last_full_load": None}
    
    def save_metadata(self, metadata: Dict):
        """
        Salva metadados de processamento
        """
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
    
    def get_new_files(self, csv_files: List[str]) -> List[str]:
        """
        Identifica arquivos novos ou modificados para carga incremental
        """
        metadata = self.load_metadata()
        new_files = []
        
        for file in csv_files:
            file_hash = self.calculate_file_hash(file)
            filename = os.path.basename(file)
            
            if (filename not in metadata["processed_files"] or 
                metadata["processed_files"][filename]["hash"] != file_hash):
                new_files.append(file)
                logger.info(f"Arquivo novo/modificado detectado: {filename}")
        
        return new_files
    
    def validate_csv_structure(self, filepath: str) -> bool:
        """
        Valida se o CSV tem a estrutura esperada
        """
        try:
            # Lê apenas o cabeçalho
            df_header = pd.read_csv(filepath, nrows=0)
            columns = df_header.columns.tolist()
            
            if len(columns) != len(self.expected_columns):
                logger.error(f"Erro no arquivo {filepath}: esperadas {len(self.expected_columns)} colunas, encontradas {len(columns)}")
                return False
            
            for i, col in enumerate(columns):
                if col != self.expected_columns[i]:
                    logger.error(f"Erro no arquivo {filepath}: coluna {i+1} deveria ser '{self.expected_columns[i]}', encontrada '{col}'")
                    return False
            
            logger.info(f"Estrutura validada com sucesso: {os.path.basename(filepath)}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao validar arquivo {filepath}: {str(e)}")
            return False
    
    def create_database_structure(self):
        """
        Cria a estrutura do banco de dados se não existir
        """
        logger.info("Criando estrutura do banco de dados...")
        
        # Cria tabela principal 'avaliacao'
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS avaliacao (
            MUN_UF         VARCHAR(2),              -- SIGLA DA UNIDADE DA FEDERAÇÃO
            MUN_NOME       VARCHAR(60),             -- NOME DO MUNICÍPIO
            ESC_INEP       VARCHAR(8),              -- CÓDIGO INEP DA ESCOLA
            ESC_NOME       VARCHAR(80),             -- NOME DA ESCOLA
            SER_NUMBER     INTEGER,                 -- NÚMERO DO ANO/SÉRIE
            SER_NOME       VARCHAR(30),             -- NOME DA SÉRIE
            TUR_PERIODO    VARCHAR(15),             -- TURNO DE ATIVIDADE (Manhã, Tarde)
            TUR_NOME       VARCHAR(20),             -- NOME DO TURNO
            ALU_ID         INTEGER,                 -- IDENTIFICAÇÃO DO ALUNO
            ALU_NOME       VARCHAR(80),             -- NOME DO ALUNO
            ALU_CPF        VARCHAR(15),             -- CPF DO ALUNO
            AVA_NOME       VARCHAR(50),             -- NOME DA AVALIAÇÃO
            AVA_ANO        INTEGER,                 -- ANO DA AVALIAÇÃO
            DIS_NOME       VARCHAR(30),             -- NOME DA DISCIPLINA
            TES_NOME       VARCHAR(30),             -- NOME DO TESTE
            TEG_ORDEM      INTEGER,                 -- ORDEM DA QUESTÃO DO TESTE
            ATR_RESPOSTA   VARCHAR(1),              -- RESPOSTA DO ALUNO NA QUESTÃO
            ATR_CERTO      INTEGER,                 -- SE 1 ACERTOU, SE 0 ERROU
            MTI_CODIGO     VARCHAR(15),             -- CÓDIGO DO DESCRITOR
            MTI_DESCRITOR  VARCHAR(512)             -- DESCRIÇÃO DO DESCRITOR
        );
        """
        
        self.conn.execute(create_table_sql)
        logger.info("Tabela 'avaliacao' criada/verificada com sucesso")
    
    def drop_star_schema(self):
        """
        Remove tabelas do Star Schema para recriação
        """
        logger.info("Removendo estrutura Star Schema existente...")
        
        drop_tables = [
            "DROP TABLE IF EXISTS fato_resposta_aluno;",
            "DROP TABLE IF EXISTS dim_descritor;",
            "DROP TABLE IF EXISTS dim_escola;", 
            "DROP TABLE IF EXISTS dim_aluno;",
            "DROP TABLE IF EXISTS teste;"
        ]
        
        for sql in drop_tables:
            self.conn.execute(sql)
        
        logger.info("Estrutura Star Schema removida")
    
    def create_star_schema(self):
        """
        Cria a estrutura Star Schema baseada na tabela avaliacao
        """
        logger.info("Criando estrutura Star Schema...")
        
        # Remove estruturas existentes
        self.drop_star_schema()
        
        # Cria dimensão de alunos
        dim_aluno_sql = """
        CREATE TABLE dim_aluno (
            ALU_ID INTEGER PRIMARY KEY,    -- Chave primária - ID único do aluno
            ALU_NOME VARCHAR(80),          -- Nome do aluno
            ALU_CPF VARCHAR(15)            -- CPF do aluno
        );
        """
        
        # Cria dimensão de escolas
        dim_escola_sql = """
        CREATE TABLE dim_escola (
            ESC_INEP VARCHAR(8) PRIMARY KEY,  -- Chave primária - Código INEP da escola
            ESC_NOME VARCHAR(80)              -- Nome da escola
        );
        """
        
        # Cria dimensão de descritores
        dim_descritor_sql = """
        CREATE TABLE dim_descritor (
            MTI_CODIGO VARCHAR(15) PRIMARY KEY,  -- Chave primária - Código do descritor
            MTI_DESCRITOR VARCHAR(512),          -- Descrição do descritor
            QTD INTEGER                          -- Quantidade de ocorrências
        );
        """
        
        # Executa criação das dimensões
        self.conn.execute(dim_aluno_sql)
        self.conn.execute(dim_escola_sql)
        self.conn.execute(dim_descritor_sql)
        
        # Popula dimensões
        self.populate_dimensions()
        
        # Cria tabela fato
        self.create_fact_table()
        
        logger.info("Estrutura Star Schema criada com sucesso")
    
    def populate_dimensions(self):
        """
        Popula as tabelas de dimensão
        """
        logger.info("Populando tabelas de dimensão...")
        
        # Popula dim_aluno
        populate_aluno_sql = """
        INSERT INTO dim_aluno (ALU_ID, ALU_NOME, ALU_CPF)  
        SELECT DISTINCT ALU_ID, ALU_NOME, ALU_CPF 
        FROM avaliacao;
        """
        
        # Popula dim_escola
        populate_escola_sql = """
        INSERT INTO dim_escola (ESC_INEP, ESC_NOME) 
        SELECT DISTINCT ESC_INEP, ESC_NOME 
        FROM avaliacao;
        """
        
        # Popula dim_descritor
        populate_descritor_sql = """
        INSERT INTO dim_descritor (MTI_CODIGO, MTI_DESCRITOR, QTD) 
        SELECT 
            MTI_CODIGO, 
            MAX(MTI_DESCRITOR) AS MTI_DESCRITOR,
            COUNT(*) AS QTD 
        FROM avaliacao 
        GROUP BY MTI_CODIGO;
        """
        
        self.conn.execute(populate_aluno_sql)
        self.conn.execute(populate_escola_sql)
        self.conn.execute(populate_descritor_sql)
        
        # Log de contadores
        alunos_count = self.conn.execute("SELECT COUNT(*) FROM dim_aluno").fetchone()[0]
        escolas_count = self.conn.execute("SELECT COUNT(*) FROM dim_escola").fetchone()[0]
        descritores_count = self.conn.execute("SELECT COUNT(*) FROM dim_descritor").fetchone()[0]
        
        logger.info(f"Dimensões populadas - Alunos: {alunos_count}, Escolas: {escolas_count}, Descritores: {descritores_count}")
    
    def create_fact_table(self):
        """
        Cria a tabela fato com agregações
        """
        logger.info("Criando tabela fato...")
        
        create_fact_sql = """
        CREATE TABLE fato_resposta_aluno AS 
        SELECT 
            -- Dimensões geográficas e administrativas
            MUN_UF,           -- Unidade da Federação
            MUN_NOME,         -- Nome do Município
            ESC_INEP,         -- Código da Escola (FK para dim_escola)
            
            -- Dimensões educacionais
            SER_NUMBER,       -- Número da Série
            SER_NOME,         -- Nome da Série
            TUR_PERIODO,      -- Período do Turno
            TUR_NOME,         -- Nome do Turno
            
            -- Dimensão do aluno
            ALU_ID,           -- ID do Aluno (FK para dim_aluno)
            
            -- Dimensões de avaliação
            AVA_NOME,         -- Nome da Avaliação
            AVA_ANO,          -- Ano da Avaliação
            DIS_NOME,         -- Disciplina
            TES_NOME,         -- Nome do Teste
            MTI_CODIGO,       -- Código do Descritor (FK para dim_descritor)
            
            -- MÉTRICAS DE NEGÓCIO (Fatos)
            SUM(CASE WHEN ATR_CERTO = 1 THEN 1 ELSE 0 END) AS ACERTO,  -- Total de acertos
            SUM(CASE WHEN ATR_CERTO = 0 THEN 1 ELSE 0 END) AS ERRO     -- Total de erros
        FROM avaliacao
        GROUP BY 
            MUN_UF, MUN_NOME, ESC_INEP, SER_NUMBER, SER_NOME, 
            TUR_PERIODO, TUR_NOME, ALU_ID, AVA_NOME, AVA_ANO, 
            DIS_NOME, TES_NOME, MTI_CODIGO;
        """
        
        self.conn.execute(create_fact_sql)
        
        fact_count = self.conn.execute("SELECT COUNT(*) FROM fato_resposta_aluno").fetchone()[0]
        logger.info(f"Tabela fato criada com {fact_count} registros")
    
    def load_csv_to_database(self, csv_files: List[str]):
        """
        Carrega arquivos CSV para o banco de dados
        """
        total_records = 0
        
        for csv_file in csv_files:
            logger.info(f"Processando arquivo: {os.path.basename(csv_file)}")
            
            try:
                # Valida estrutura do CSV
                if not self.validate_csv_structure(csv_file):
                    logger.error(f"Pulando arquivo com estrutura inválida: {csv_file}")
                    continue
                
                # Carrega CSV diretamente no DuckDB (mais eficiente para arquivos grandes)
                load_sql = f"""
                INSERT INTO avaliacao 
                SELECT * FROM read_csv_auto('{csv_file}', header=true);
                """
                
                self.conn.execute(load_sql)
                # Conta registros do arquivo
                count_sql = f"SELECT COUNT(*) FROM read_csv_auto('{csv_file}', header=true);"
                file_records = self.conn.execute(count_sql).fetchone()[0]
                total_records += file_records
                
                logger.info(f"Arquivo processado: {os.path.basename(csv_file)} - {file_records:,} registros")
                
            except Exception as e:
                logger.error(f"Erro ao processar arquivo {csv_file}: {str(e)}")
                raise
        
        logger.info(f"Total de registros carregados: {total_records:,}")
        return total_records
    
    def update_metadata(self, csv_files: List[str]):
        """
        Atualiza metadados após processamento
        """
        metadata = self.load_metadata()
        
        for file in csv_files:
            filename = os.path.basename(file)
            file_hash = self.calculate_file_hash(file)
            metadata["processed_files"][filename] = {
                "hash": file_hash,
                "processed_at": datetime.now().isoformat(),
                "file_size": os.path.getsize(file)
            }
        
        self.save_metadata(metadata)
        logger.info("Metadados atualizados")
    
    def execute_full_load(self):
        """
        Executa carga completa - recriar banco e processar todos os arquivos
        """
        logger.info("=== INICIANDO CARGA COMPLETA ===")
        
        # Remove banco existente e recria
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            logger.info("Banco de dados anterior removido")
        
        # Reconecta ao banco
        self.conn = duckdb.connect(self.db_path)
        
        # Cria estrutura
        self.create_database_structure()
        
        # Carrega todos os CSVs
        csv_files = self.get_csv_files()
        if not csv_files:
            logger.warning("Nenhum arquivo CSV encontrado!")
            return
        
        total_records = self.load_csv_to_database(csv_files)
        
        # Cria Star Schema
        self.create_star_schema()
        
        # Força flush dos dados
        self.conn.execute("CHECKPOINT;")
        
        # Atualiza metadados
        self.update_metadata(csv_files)
        metadata = self.load_metadata()
        metadata["last_full_load"] = datetime.now().isoformat()
        self.save_metadata(metadata)
        
        logger.info(f"=== CARGA COMPLETA FINALIZADA - {total_records:,} registros ===")
    
    def execute_incremental_load(self):
        """
        Executa carga incremental - apenas arquivos novos/modificados
        """
        logger.info("=== INICIANDO CARGA INCREMENTAL ===")
        
        # Cria estrutura se não existir
        self.create_database_structure()
        
        # Identifica arquivos novos
        csv_files = self.get_csv_files()
        new_files = self.get_new_files(csv_files)
        
        if not new_files:
            logger.info("Nenhum arquivo novo encontrado para processamento")
            return
        
        logger.info(f"Arquivos novos/modificados encontrados: {len(new_files)}")
        
        # Carrega apenas arquivos novos
        total_records = self.load_csv_to_database(new_files)
        
        # Recria Star Schema (necessário devido às agregações)
        self.create_star_schema()
        
        # Força flush dos dados
        self.conn.execute("CHECKPOINT;")
        
        # Atualiza metadados
        self.update_metadata(new_files)
        
        logger.info(f"=== CARGA INCREMENTAL FINALIZADA - {total_records:,} novos registros ===")
    
    def get_database_stats(self) -> Dict:
        """
        Retorna estatísticas do banco de dados
        """
        try:
            stats = {}
            
            # Contadores das tabelas
            tables = ['avaliacao', 'dim_aluno', 'dim_escola', 'dim_descritor', 'fato_resposta_aluno']
            for table in tables:
                try:
                    count = self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    stats[table] = count
                except:
                    stats[table] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {}
    
    def close(self):
        """
        Fecha conexão com o banco
        """
        if self.conn:
            self.conn.close()
            logger.info("Conexão com banco fechada")


def main():
    """
    Função principal do ETL
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='ETL do Sistema SAEV')
    parser.add_argument('--mode', choices=['full', 'incremental'], required=True,
                       help='Modo de carga: full (completa) ou incremental')
    parser.add_argument('--db-path', default='db/avaliacao_prod.duckdb',
                       help='Caminho para o banco DuckDB')
    parser.add_argument('--data-path', default='data/raw',
                       help='Caminho para os arquivos CSV')
    
    args = parser.parse_args()
    
    # Inicializa processador ETL
    etl = SAEVETLProcessor(db_path=args.db_path, data_path=args.data_path)
    
    try:
        if args.mode == 'full':
            etl.execute_full_load()
        else:
            etl.execute_incremental_load()
        
        # Mostra estatísticas finais
        stats = etl.get_database_stats()
        logger.info("=== ESTATÍSTICAS FINAIS ===")
        for table, count in stats.items():
            logger.info(f"{table}: {count:,} registros")
            
    except Exception as e:
        logger.error(f"Erro durante processamento ETL: {str(e)}")
        raise
    finally:
        etl.close()


if __name__ == "__main__":
    main()

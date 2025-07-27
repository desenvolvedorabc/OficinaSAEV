#!/usr/bin/env python3
"""
ETL Final SAEV - Sistema completo de ETL com carga completa e incremental
========================================================================

Implementa exatamente as especificações do README.md:
- Carga completa: Recria banco e processa todos os CSVs
- Carga incremental: Processa apenas arquivos novos/modificados
"""

import os
import glob
import duckdb
import json
import hashlib
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_saev.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SAEVETLFinal:
    def __init__(self, db_path="db/avaliacao_prod.duckdb", data_path="data/raw"):
        self.db_path = db_path
        self.data_path = data_path
        self.metadata_file = "etl_metadata.json"
        
        # Cria diretórios
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(data_path, exist_ok=True)
        
    def load_metadata(self):
        """Carrega metadados de processamento"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"processed_files": {}, "last_full_load": None}
    
    def save_metadata(self, metadata):
        """Salva metadados de processamento"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
    
    def calculate_file_hash(self, filepath):
        """Calcula hash MD5 do arquivo"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def get_csv_files(self):
        """Retorna lista de arquivos CSV"""
        return glob.glob(os.path.join(self.data_path, "*.csv"))
    
    def get_new_files(self, csv_files):
        """Identifica arquivos novos ou modificados"""
        metadata = self.load_metadata()
        new_files = []
        
        for file in csv_files:
            file_hash = self.calculate_file_hash(file)
            filename = os.path.basename(file)
            
            if (filename not in metadata["processed_files"] or 
                metadata["processed_files"][filename]["hash"] != file_hash):
                new_files.append(file)
                logger.info(f"📁 Arquivo novo/modificado: {filename}")
        
        return new_files
    
    def create_database_structure(self, conn):
        """Cria estrutura do banco (DDL do README)"""
        logger.info("🏗️ Criando estrutura do banco...")
        
        create_sql = """
        CREATE TABLE IF NOT EXISTS avaliacao (
            MUN_UF         CHAR(2),              -- SIGLA DA UNIDADE DA FEDERAÇÃO
            MUN_NOME       VARCHAR(60),          -- NOME DO MUNICÍPIO
            ESC_INEP       CHAR(8),              -- CÓDIGO INEP DA ESCOLA
            ESC_NOME       VARCHAR(80),          -- NOME DA ESCOLA
            SER_NUMBER     INTEGER,              -- NÚMERO DO ANO/SÉRIE
            SER_NOME       VARCHAR(30),          -- NOME DA SÉRIE
            TUR_PERIODO    VARCHAR(15),          -- TURNO DE ATIVIDADE (Manhã, Tarde)
            TUR_NOME       VARCHAR(20),          -- NOME DO TURNO
            ALU_ID         INTEGER,              -- IDENTIFICAÇÃO DO ALUNO
            ALU_NOME       VARCHAR(80),          -- NOME DO ALUNO
            ALU_CPF        VARCHAR(15),          -- CPF DO ALUNO
            AVA_NOME       VARCHAR(50),          -- NOME DA AVALIAÇÃO
            AVA_ANO        INTEGER,              -- ANO DA AVALIAÇÃO
            DIS_NOME       VARCHAR(30),          -- NOME DA DISCIPLINA
            TES_NOME       VARCHAR(30),          -- NOME DO TESTE
            TEG_ORDEM      INTEGER,              -- ORDEM DA QUESTÃO DO TESTE
            ATR_RESPOSTA   CHAR(1),              -- RESPOSTA DO ALUNO NA QUESTÃO
            ATR_CERTO      INTEGER,              -- SE 1 ACERTOU, SE 0 ERROU
            MTI_CODIGO     VARCHAR(15),          -- CÓDIGO DO DESCRITOR
            MTI_DESCRITOR  VARCHAR(512)          -- DESCRIÇÃO DO DESCRITOR
        );
        """
        
        conn.execute(create_sql)
        logger.info("✅ Tabela 'avaliacao' pronta")
    
    def load_csv_files(self, conn, csv_files):
        """Carrega arquivos CSV específicos"""
        total_records = 0
        
        for csv_file in csv_files:
            filename = os.path.basename(csv_file)
            logger.info(f"📂 Carregando: {filename}")
            
            try:
                load_sql = f"""
                INSERT INTO avaliacao 
                SELECT * FROM read_csv_auto('{csv_file}', header=true, ignore_errors=true);
                """
                
                conn.execute(load_sql)
                
                # Conta registros do arquivo
                count_sql = f"SELECT COUNT(*) FROM read_csv_auto('{csv_file}', header=true);"
                file_records = conn.execute(count_sql).fetchone()[0]
                total_records += file_records
                
                logger.info(f"✅ {filename}: {file_records:,} registros")
                
            except Exception as e:
                logger.error(f"❌ Erro ao carregar {filename}: {str(e)}")
                raise
        
        return total_records
    
    def create_star_schema(self, conn):
        """Cria Star Schema (exato do README)"""
        logger.info("⭐ Criando Star Schema...")
        
        # Remove estruturas existentes
        conn.execute("DROP TABLE IF EXISTS fato_resposta_aluno;")
        conn.execute("DROP TABLE IF EXISTS dim_descritor;")
        conn.execute("DROP TABLE IF EXISTS dim_escola;")
        conn.execute("DROP TABLE IF EXISTS dim_aluno;")
        conn.execute("DROP TABLE IF EXISTS teste;")
        
        # Cria dimensões
        conn.execute("""
        CREATE TABLE dim_aluno (
            ALU_ID INTEGER PRIMARY KEY,
            ALU_NOME VARCHAR(80),
            ALU_CPF VARCHAR(15)
        );
        """)
        
        conn.execute("""
        CREATE TABLE dim_escola (
            ESC_INEP CHAR(8) PRIMARY KEY,
            ESC_NOME VARCHAR(80)
        );
        """)
        
        conn.execute("""
        CREATE TABLE dim_descritor (
            MTI_CODIGO VARCHAR(15) PRIMARY KEY,
            MTI_DESCRITOR VARCHAR(512),
            QTD INTEGER
        );
        """)
        
        # Popula dimensões
        conn.execute("""
        INSERT INTO dim_aluno (ALU_ID, ALU_NOME, ALU_CPF)  
        SELECT DISTINCT ALU_ID, ALU_NOME, ALU_CPF FROM avaliacao;
        """)
        
        conn.execute("""
        INSERT INTO dim_escola (ESC_INEP, ESC_NOME) 
        SELECT DISTINCT ESC_INEP, ESC_NOME FROM avaliacao;
        """)
        
        conn.execute("""
        INSERT INTO dim_descritor (MTI_CODIGO, MTI_DESCRITOR, QTD) 
        SELECT MTI_CODIGO, MAX(MTI_DESCRITOR), COUNT(*) 
        FROM avaliacao GROUP BY MTI_CODIGO;
        """)
        
        # Cria tabela fato
        conn.execute("""
        CREATE TABLE fato_resposta_aluno AS 
        SELECT 
            MUN_UF, MUN_NOME, ESC_INEP, SER_NUMBER, SER_NOME, 
            TUR_PERIODO, TUR_NOME, ALU_ID, AVA_NOME, AVA_ANO, 
            DIS_NOME, TES_NOME, MTI_CODIGO,
            SUM(CASE WHEN ATR_CERTO = 1 THEN 1 ELSE 0 END) AS ACERTO,
            SUM(CASE WHEN ATR_CERTO = 0 THEN 1 ELSE 0 END) AS ERRO
        FROM avaliacao
        GROUP BY MUN_UF, MUN_NOME, ESC_INEP, SER_NUMBER, SER_NOME, 
                 TUR_PERIODO, TUR_NOME, ALU_ID, AVA_NOME, AVA_ANO, 
                 DIS_NOME, TES_NOME, MTI_CODIGO;
        """)
        
        # Estatísticas
        alunos = conn.execute("SELECT COUNT(*) FROM dim_aluno").fetchone()[0]
        escolas = conn.execute("SELECT COUNT(*) FROM dim_escola").fetchone()[0]
        descritores = conn.execute("SELECT COUNT(*) FROM dim_descritor").fetchone()[0]
        fatos = conn.execute("SELECT COUNT(*) FROM fato_resposta_aluno").fetchone()[0]
        
        logger.info(f"✅ Star Schema criado:")
        logger.info(f"   - dim_aluno: {alunos:,}")
        logger.info(f"   - dim_escola: {escolas:,}")
        logger.info(f"   - dim_descritor: {descritores:,}")
        logger.info(f"   - fato_resposta_aluno: {fatos:,}")
    
    def update_metadata(self, csv_files):
        """Atualiza metadados após processamento"""
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
    
    def execute_full_load(self):
        """Executa carga completa"""
        logger.info("🔄 === CARGA COMPLETA INICIADA ===")
        
        # Remove banco existente
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            logger.info("🗑️ Banco anterior removido")
        
        # Conecta e processa
        conn = duckdb.connect(self.db_path)
        logger.info(f"🔌 Conectado: {self.db_path}")
        
        try:
            # Estrutura
            self.create_database_structure(conn)
            
            # Carrega todos os arquivos
            csv_files = self.get_csv_files()
            if not csv_files:
                logger.warning("⚠️ Nenhum arquivo CSV encontrado!")
                return
            
            logger.info(f"📁 Encontrados {len(csv_files)} arquivos CSV")
            total_records = self.load_csv_files(conn, csv_files)
            
            # Star Schema
            self.create_star_schema(conn)
            
            # Atualiza metadados
            self.update_metadata(csv_files)
            metadata = self.load_metadata()
            metadata["last_full_load"] = datetime.now().isoformat()
            self.save_metadata(metadata)
            
            logger.info(f"✅ === CARGA COMPLETA FINALIZADA - {total_records:,} registros ===")
            
        finally:
            conn.close()
    
    def execute_incremental_load(self):
        """Executa carga incremental"""
        logger.info("➕ === CARGA INCREMENTAL INICIADA ===")
        
        # Conecta
        conn = duckdb.connect(self.db_path)
        logger.info(f"🔌 Conectado: {self.db_path}")
        
        try:
            # Garante estrutura
            self.create_database_structure(conn)
            
            # Identifica arquivos novos
            csv_files = self.get_csv_files()
            new_files = self.get_new_files(csv_files)
            
            if not new_files:
                logger.info("ℹ️ Nenhum arquivo novo encontrado")
                return
            
            logger.info(f"📁 Arquivos novos: {len(new_files)}")
            
            # Carrega apenas arquivos novos
            total_records = self.load_csv_files(conn, new_files)
            
            # Recria Star Schema (necessário devido às agregações)
            self.create_star_schema(conn)
            
            # Atualiza metadados
            self.update_metadata(new_files)
            
            logger.info(f"✅ === CARGA INCREMENTAL FINALIZADA - {total_records:,} novos registros ===")
            
        finally:
            conn.close()
    
    def show_stats(self):
        """Mostra estatísticas do banco"""
        conn = duckdb.connect(self.db_path)
        
        try:
            logger.info("📊 === ESTATÍSTICAS FINAIS ===")
            
            tables = ['avaliacao', 'dim_aluno', 'dim_escola', 'dim_descritor', 'fato_resposta_aluno']
            for table in tables:
                try:
                    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    logger.info(f"   {table}: {count:,} registros")
                except:
                    logger.info(f"   {table}: não encontrada")
        finally:
            conn.close()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='ETL SAEV Final')
    parser.add_argument('--mode', choices=['full', 'incremental'], required=True)
    parser.add_argument('--db-path', default='db/avaliacao_prod.duckdb')
    parser.add_argument('--data-path', default='data/raw')
    
    args = parser.parse_args()
    
    etl = SAEVETLFinal(db_path=args.db_path, data_path=args.data_path)
    
    try:
        if args.mode == 'full':
            etl.execute_full_load()
        else:
            etl.execute_incremental_load()
        
        etl.show_stats()
        
    except Exception as e:
        logger.error(f"❌ ERRO: {str(e)}")
        raise

if __name__ == "__main__":
    main()

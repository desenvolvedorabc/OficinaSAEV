#!/usr/bin/env python3
"""
Versão otimizada para Linux com processamento de grandes volumes
================================================================

Melhorias específicas para problemas de memória no Linux:
1. Configuração otimizada do DuckDB
2. Processamento em chunks/lotes
3. Monitoramento de memória
4. Checkpoint frequentes
5. Configurações específicas para o sistema Linux
"""

import os
import psutil
import gc
from saev_etl import SAEVETLFinal, logger

class SAEVETLLinuxOptimized(SAEVETLFinal):
    """
    Versão otimizada do ETL para Linux com grandes volumes de dados
    """
    
    def __init__(self, db_path="db/avaliacao_prod.duckdb", data_path="data/raw"):
        super().__init__(db_path, data_path)
        self.chunk_size = 1000000  # Processa 1M registros por vez
        
    def get_system_info(self):
        """Obtém informações do sistema para otimização"""
        memory_gb = psutil.virtual_memory().total / (1024**3)
        cpu_count = psutil.cpu_count()
        available_memory_gb = psutil.virtual_memory().available / (1024**3)
        
        logger.info(f"🖥️ Sistema Linux detectado:")
        logger.info(f"   - RAM Total: {memory_gb:.1f} GB")
        logger.info(f"   - RAM Disponível: {available_memory_gb:.1f} GB")
        logger.info(f"   - CPUs: {cpu_count}")
        
        return memory_gb, cpu_count, available_memory_gb
    
    def optimize_duckdb_for_linux(self, conn):
        """Otimiza configurações do DuckDB especificamente para Linux"""
        memory_gb, cpu_count, available_gb = self.get_system_info()
        
        # Calcula configurações baseadas no sistema
        max_memory = min(int(available_gb * 0.7), 8)  # Máximo 8GB ou 70% da RAM disponível
        max_threads = min(cpu_count, 6)  # Máximo 6 threads
        
        logger.info(f"🔧 Configurando DuckDB para otimização Linux:")
        logger.info(f"   - Limite de memória: {max_memory}GB")
        logger.info(f"   - Threads: {max_threads}")
        
        # Configurações otimizadas para Linux
        conn.execute(f"SET memory_limit = '{max_memory}GB';")
        conn.execute(f"SET threads = {max_threads};")
        conn.execute("SET enable_progress_bar = true;")
        conn.execute("SET preserve_insertion_order = false;")  # Melhora performance
        conn.execute("SET force_checkpoint = true;")  # Força escrita no disco
        
        # Configurações específicas para agregações grandes
        conn.execute("SET max_temp_directory_size = '10GB';")
        conn.execute("SET temp_directory = '/tmp/duckdb_temp';")
        
        # Cria diretório temporário se não existir
        os.makedirs('/tmp/duckdb_temp', exist_ok=True)
        
    def create_star_schema_optimized(self, conn):
        """Cria Star Schema com otimizações específicas para grandes volumes"""
        logger.info("⭐ Iniciando criação otimizada do Star Schema...")
        
        # Otimiza DuckDB para o sistema atual
        self.optimize_duckdb_for_linux(conn)
        
        # Remove estruturas existentes
        logger.info("🗑️ Removendo estruturas existentes...")
        conn.execute("DROP TABLE IF EXISTS fato_resposta_aluno;")
        conn.execute("DROP TABLE IF EXISTS dim_descritor;")
        conn.execute("DROP TABLE IF EXISTS dim_escola;")
        conn.execute("DROP TABLE IF EXISTS dim_aluno;")
        conn.execute("DROP TABLE IF EXISTS teste;")
        
        # Força checkpoint após drops
        conn.execute("CHECKPOINT;")
        
        # Cria e popula dimensões (são pequenas)
        self.create_dimensions_fast(conn)
        
        # Cria tabela fato com processamento otimizado
        self.create_fact_table_chunked(conn)
        
        # Checkpoint final
        logger.info("💾 Executando checkpoint final...")
        conn.execute("CHECKPOINT;")
        
        # Limpa cache Python
        gc.collect()
        
        # Estatísticas finais
        self.show_star_schema_stats(conn)
        
    def create_dimensions_fast(self, conn):
        """Cria e popula dimensões rapidamente"""
        logger.info("📊 Criando dimensões (rápido)...")
        
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
        logger.info("📊 Populando dim_aluno...")
        conn.execute("""
        INSERT INTO dim_aluno (ALU_ID, ALU_NOME, ALU_CPF)  
        SELECT DISTINCT ALU_ID, ALU_NOME, ALU_CPF FROM avaliacao;
        """)

        logger.info("📊 Populando dim_escola...")
        conn.execute("""
        INSERT INTO dim_escola (ESC_INEP, ESC_NOME) 
        SELECT DISTINCT ESC_INEP, ESC_NOME FROM avaliacao;
        """)

        logger.info("📊 Populando dim_descritor...")
        conn.execute("""
        INSERT INTO dim_descritor (MTI_CODIGO, MTI_DESCRITOR, QTD) 
        SELECT MTI_CODIGO, MAX(MTI_DESCRITOR), COUNT(*) 
        FROM avaliacao GROUP BY MTI_CODIGO;
        """)
        
        conn.execute("CHECKPOINT;")
        logger.info("✅ Dimensões criadas e populadas")
    
    def create_fact_table_chunked(self, conn):
        """Cria tabela fato usando processamento em chunks para economizar memória"""
        logger.info("⚡ Criando tabela fato com processamento otimizado...")
        
        # Cria estrutura da tabela fato
        conn.execute("""
        CREATE TABLE fato_resposta_aluno (
            MUN_UF CHAR(2),
            MUN_NOME VARCHAR(60),
            ESC_INEP CHAR(8),
            SER_NUMBER INTEGER,
            SER_NOME VARCHAR(30),
            TUR_PERIODO VARCHAR(15),
            TUR_NOME VARCHAR(20),
            ALU_ID INTEGER,
            AVA_NOME VARCHAR(50),
            AVA_ANO INTEGER,
            DIS_NOME VARCHAR(30),
            TES_NOME VARCHAR(30),
            MTI_CODIGO VARCHAR(15),
            ACERTO INTEGER,
            ERRO INTEGER
        );
        """)
        
        # Estratégia: processar por escola para dividir a carga
        logger.info("📊 Identificando escolas para processamento em lotes...")
        escolas = conn.execute("""
        SELECT ESC_INEP, COUNT(*) as registros
        FROM avaliacao 
        GROUP BY ESC_INEP 
        ORDER BY registros DESC
        """).fetchall()
        
        total_escolas = len(escolas)
        logger.info(f"📊 Processando {total_escolas} escolas em lotes otimizados...")
        
        # Processa escolas em grupos
        batch_size = 50  # Processa 50 escolas por vez
        processed = 0
        
        for i in range(0, total_escolas, batch_size):
            batch_escolas = escolas[i:i+batch_size]
            escola_list = "', '".join([e[0] for e in batch_escolas])
            
            logger.info(f"📊 Processando lote {i//batch_size + 1}/{(total_escolas-1)//batch_size + 1} "
                       f"({len(batch_escolas)} escolas)")
            
            # Insere dados do lote atual
            conn.execute(f"""
            INSERT INTO fato_resposta_aluno
            SELECT 
                MUN_UF, MUN_NOME, ESC_INEP, SER_NUMBER, SER_NOME, 
                TUR_PERIODO, TUR_NOME, ALU_ID, AVA_NOME, AVA_ANO, 
                DIS_NOME, TES_NOME, MTI_CODIGO,
                SUM(CASE WHEN ATR_CERTO = 1 THEN 1 ELSE 0 END) AS ACERTO,
                SUM(CASE WHEN ATR_CERTO = 0 THEN 1 ELSE 0 END) AS ERRO
            FROM avaliacao
            WHERE ESC_INEP IN ('{escola_list}')
            GROUP BY MUN_UF, MUN_NOME, ESC_INEP, SER_NUMBER, SER_NOME, 
                     TUR_PERIODO, TUR_NOME, ALU_ID, AVA_NOME, AVA_ANO, 
                     DIS_NOME, TES_NOME, MTI_CODIGO;
            """)
            
            processed += len(batch_escolas)
            
            # Checkpoint periódico para liberar memória
            if i % (batch_size * 4) == 0:  # A cada 4 lotes (200 escolas)
                conn.execute("CHECKPOINT;")
                gc.collect()  # Força limpeza do Python
                
                # Mostra progresso
                current_count = conn.execute("SELECT COUNT(*) FROM fato_resposta_aluno").fetchone()[0]
                logger.info(f"✅ Progresso: {processed}/{total_escolas} escolas, "
                           f"{current_count:,} registros na tabela fato")
        
        logger.info("✅ Tabela fato criada com sucesso!")
    
    def show_star_schema_stats(self, conn):
        """Mostra estatísticas finais do Star Schema"""
        logger.info("📊 === ESTATÍSTICAS FINAIS DO STAR SCHEMA ===")
        
        alunos = conn.execute("SELECT COUNT(*) FROM dim_aluno").fetchone()[0]
        escolas = conn.execute("SELECT COUNT(*) FROM dim_escola").fetchone()[0]
        descritores = conn.execute("SELECT COUNT(*) FROM dim_descritor").fetchone()[0]
        fatos = conn.execute("SELECT COUNT(*) FROM fato_resposta_aluno").fetchone()[0]
        
        logger.info(f"✅ Dimensões criadas:")
        logger.info(f"   - dim_aluno: {alunos:,} registros")
        logger.info(f"   - dim_escola: {escolas:,} registros")
        logger.info(f"   - dim_descritor: {descritores:,} registros")
        logger.info(f"   - fato_resposta_aluno: {fatos:,} registros")
        
        # Mostra tamanho do banco
        if os.path.exists(self.db_path):
            size_mb = os.path.getsize(self.db_path) / (1024 * 1024)
            logger.info(f"📁 Tamanho do banco: {size_mb:.1f} MB")
    
    def create_star_schema(self, conn):
        """Sobrescreve o método original com a versão otimizada"""
        return self.create_star_schema_optimized(conn)


def main():
    """Função principal usando a versão otimizada para Linux"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ETL SAEV Otimizado para Linux')
    parser.add_argument('--mode', choices=['full', 'incremental'], required=True)
    parser.add_argument('--db-path', default='db/avaliacao_prod.duckdb')
    parser.add_argument('--data-path', default='data/raw')
    
    args = parser.parse_args()
    
    # Usa a versão otimizada
    etl = SAEVETLLinuxOptimized(db_path=args.db_path, data_path=args.data_path)
    
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

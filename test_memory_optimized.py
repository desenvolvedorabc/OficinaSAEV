#!/usr/bin/env python3
"""
Teste da versão otimizada para resolver problemas de memória no Linux
=====================================================================

Esta versão implementa estratégias específicas para grandes volumes:
1. Configuração otimizada do DuckDB
2. Processamento em lotes
3. Monitoramento de memória
4. Checkpoints frequentes
"""

import os
import sys
import time
import psutil
import gc
from datetime import datetime

# Adiciona o diretório atual ao path para importar o módulo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from saev_etl import SAEVETLFinal, logger
except ImportError as e:
    print(f"❌ Erro ao importar saev_etl: {e}")
    print("Certifique-se de estar no diretório correto e que o arquivo saev_etl.py existe")
    sys.exit(1)

class SAEVETLMemoryOptimized(SAEVETLFinal):
    """
    Versão com otimizações específicas para problemas de memória
    """
    
    def __init__(self, db_path="db/avaliacao_prod.duckdb", data_path="data/raw"):
        super().__init__(db_path, data_path)
        self.start_time = time.time()
        
    def monitor_memory(self, operation=""):
        """Monitora uso de memória"""
        memory = psutil.virtual_memory()
        process = psutil.Process()
        
        logger.info(f"🔍 Memória {operation}:")
        logger.info(f"   Sistema: {memory.percent:.1f}% usado ({memory.used/1024**3:.1f}GB/{memory.total/1024**3:.1f}GB)")
        logger.info(f"   Processo: {process.memory_info().rss/1024**3:.1f} GB")
        
        if memory.percent > 85:
            logger.warning("⚠️ Uso de memória alto! Executando limpeza...")
            gc.collect()
    
    def create_star_schema_optimized(self, conn):
        """Versão otimizada do Star Schema para economizar memória"""
        logger.info("⭐ Iniciando criação otimizada do Star Schema...")
        
        start_time = time.time()
        self.monitor_memory("antes do Star Schema")
        
        # Configurações otimizadas do DuckDB
        logger.info("🔧 Configurando DuckDB para otimização de memória...")
        
        # Detecta memória disponível e configura limite
        available_gb = psutil.virtual_memory().available / (1024**3)
        memory_limit = max(2, min(int(available_gb * 0.6), 6))  # Entre 2GB e 6GB
        
        logger.info(f"   - Limite de memória: {memory_limit}GB")
        logger.info(f"   - Threads: 4 (otimizado)")
        
        conn.execute(f"SET memory_limit = '{memory_limit}GB';")
        conn.execute("SET threads = 4;")
        conn.execute("SET enable_progress_bar = true;")
        conn.execute("SET temp_directory = '/tmp';")
        
        # Remove estruturas existentes
        logger.info("🗑️ Removendo estruturas existentes...")
        tables_to_drop = [
            "fato_resposta_aluno",
            "dim_descritor", 
            "dim_escola",
            "dim_aluno",
            "teste"
        ]
        
        for table in tables_to_drop:
            conn.execute(f"DROP TABLE IF EXISTS {table};")
        
        conn.execute("CHECKPOINT;")
        self.monitor_memory("após remoção de tabelas")
        
        # Cria dimensões (são pequenas, sem problema)
        logger.info("📊 Criando e populando dimensões...")
        self.create_dimensions_optimized(conn)
        
        # Cria tabela fato usando estratégia otimizada
        logger.info("⚡ Criando tabela fato com estratégia de baixo uso de memória...")
        self.create_fact_table_memory_safe(conn)
        
        # Checkpoint final
        logger.info("💾 Executando checkpoint final...")
        conn.execute("CHECKPOINT;")
        
        # Estatísticas finais
        elapsed = time.time() - start_time
        self.show_final_stats(conn, elapsed)
        
        logger.info("✅ Star Schema criado com sucesso!")
    
    def create_dimensions_optimized(self, conn):
        """Cria dimensões de forma otimizada"""
        
        # Dimensão de alunos
        conn.execute("""
        CREATE TABLE dim_aluno (
            ALU_ID INTEGER PRIMARY KEY,
            ALU_NOME VARCHAR(80),
            ALU_CPF VARCHAR(15)
        );
        """)
        
        conn.execute("""
        INSERT INTO dim_aluno (ALU_ID, ALU_NOME, ALU_CPF)  
        SELECT DISTINCT ALU_ID, ALU_NOME, ALU_CPF FROM avaliacao;
        """)
        
        # Dimensão de escolas
        conn.execute("""
        CREATE TABLE dim_escola (
            ESC_INEP CHAR(8) PRIMARY KEY,
            ESC_NOME VARCHAR(80)
        );
        """)
        
        conn.execute("""
        INSERT INTO dim_escola (ESC_INEP, ESC_NOME) 
        SELECT DISTINCT ESC_INEP, ESC_NOME FROM avaliacao;
        """)
        
        # Dimensão de descritores
        conn.execute("""
        CREATE TABLE dim_descritor (
            MTI_CODIGO VARCHAR(15) PRIMARY KEY,
            MTI_DESCRITOR VARCHAR(512),
            QTD INTEGER
        );
        """)
        
        conn.execute("""
        INSERT INTO dim_descritor (MTI_CODIGO, MTI_DESCRITOR, QTD) 
        SELECT MTI_CODIGO, MAX(MTI_DESCRITOR), COUNT(*) 
        FROM avaliacao GROUP BY MTI_CODIGO;
        """)
        
        # Checkpoint após dimensões
        conn.execute("CHECKPOINT;")
        logger.info("✅ Dimensões criadas")
        self.monitor_memory("após criação das dimensões")
    
    def create_fact_table_memory_safe(self, conn):
        """Cria tabela fato de forma segura para memória"""
        
        # Cria estrutura da tabela fato vazia
        logger.info("📊 Criando estrutura da tabela fato...")
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
        
        # Conta total de registros para estimar progresso
        total_registros = conn.execute("SELECT COUNT(*) FROM avaliacao").fetchone()[0]
        logger.info(f"📊 Total de registros a processar: {total_registros:,}")
        
        # Estratégia: Processar por estado (MUN_UF) para dividir a carga
        estados = conn.execute("SELECT DISTINCT MUN_UF FROM avaliacao ORDER BY MUN_UF").fetchall()
        logger.info(f"📊 Processando {len(estados)} estados em lotes...")
        
        processed_total = 0
        
        for i, (estado,) in enumerate(estados):
            logger.info(f"📊 Processando estado {estado} ({i+1}/{len(estados)})...")
            
            # Conta registros do estado atual
            estado_count = conn.execute(
                "SELECT COUNT(*) FROM avaliacao WHERE MUN_UF = ?", 
                [estado]
            ).fetchone()[0]
            
            logger.info(f"   Estado {estado}: {estado_count:,} registros")
            
            # Insere dados do estado atual
            conn.execute(f"""
            INSERT INTO fato_resposta_aluno
            SELECT 
                MUN_UF, MUN_NOME, ESC_INEP, SER_NUMBER, SER_NOME, 
                TUR_PERIODO, TUR_NOME, ALU_ID, AVA_NOME, AVA_ANO, 
                DIS_NOME, TES_NOME, MTI_CODIGO,
                SUM(CASE WHEN ATR_CERTO = 1 THEN 1 ELSE 0 END) AS ACERTO,
                SUM(CASE WHEN ATR_CERTO = 0 THEN 1 ELSE 0 END) AS ERRO
            FROM avaliacao
            WHERE MUN_UF = '{estado}'
            GROUP BY MUN_UF, MUN_NOME, ESC_INEP, SER_NUMBER, SER_NOME, 
                     TUR_PERIODO, TUR_NOME, ALU_ID, AVA_NOME, AVA_ANO, 
                     DIS_NOME, TES_NOME, MTI_CODIGO;
            """)
            
            processed_total += estado_count
            progress = (processed_total / total_registros) * 100
            
            # Checkpoint a cada 3 estados
            if (i + 1) % 3 == 0:
                conn.execute("CHECKPOINT;")
                self.monitor_memory(f"após estado {estado}")
                gc.collect()  # Força limpeza do Python
            
            logger.info(f"✅ Estado {estado} concluído. Progresso: {progress:.1f}%")
        
        # Checkpoint final
        conn.execute("CHECKPOINT;")
        logger.info("✅ Tabela fato criada com sucesso!")
    
    def show_final_stats(self, conn, elapsed_time):
        """Mostra estatísticas finais"""
        logger.info("📊 === ESTATÍSTICAS FINAIS DO STAR SCHEMA ===")
        
        # Contadores das tabelas
        tables = {
            'dim_aluno': conn.execute("SELECT COUNT(*) FROM dim_aluno").fetchone()[0],
            'dim_escola': conn.execute("SELECT COUNT(*) FROM dim_escola").fetchone()[0],
            'dim_descritor': conn.execute("SELECT COUNT(*) FROM dim_descritor").fetchone()[0],
            'fato_resposta_aluno': conn.execute("SELECT COUNT(*) FROM fato_resposta_aluno").fetchone()[0]
        }
        
        for table, count in tables.items():
            logger.info(f"   {table}: {count:,} registros")
        
        # Tamanho do banco
        if os.path.exists(self.db_path):
            size_mb = os.path.getsize(self.db_path) / (1024 * 1024)
            logger.info(f"📁 Tamanho do banco: {size_mb:.1f} MB")
        
        # Tempo de processamento
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        
        if hours > 0:
            time_str = f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            time_str = f"{minutes}m {seconds}s"
        else:
            time_str = f"{seconds}s"
            
        logger.info(f"⏱️ Tempo total: {time_str}")
        
        # Estado final da memória
        self.monitor_memory("final")
    
    def create_star_schema(self, conn):
        """Sobrescreve o método original com a versão otimizada"""
        return self.create_star_schema_optimized(conn)


def main():
    """Função principal para testar a versão otimizada"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ETL SAEV Otimizado para Memória')
    parser.add_argument('--mode', choices=['full', 'incremental'], required=True,
                       help='Tipo de carga: full (completa) ou incremental')
    parser.add_argument('--db-path', default='db/avaliacao_prod.duckdb',
                       help='Caminho para o banco de dados')
    parser.add_argument('--data-path', default='data/raw',
                       help='Caminho para os arquivos CSV')
    
    args = parser.parse_args()
    
    # Verifica recursos do sistema
    memory = psutil.virtual_memory()
    available_gb = memory.available / (1024**3)
    
    logger.info("🐧 ETL SAEV - Versão Otimizada para Linux")
    logger.info("=" * 50)
    logger.info(f"💾 RAM disponível: {available_gb:.1f} GB")
    logger.info(f"🖥️ CPU cores: {psutil.cpu_count()}")
    
    if available_gb < 2:
        logger.warning("⚠️ AVISO: Pouca RAM disponível. O processamento pode ser lento.")
        response = input("Continuar mesmo assim? (s/N): ")
        if response.lower() not in ['s', 'sim', 'y', 'yes']:
            logger.info("Processamento cancelado pelo usuário.")
            return
    
    # Cria instância otimizada
    etl = SAEVETLMemoryOptimized(db_path=args.db_path, data_path=args.data_path)
    
    try:
        logger.info(f"🚀 Iniciando carga {args.mode}...")
        start_time = time.time()
        
        if args.mode == 'full':
            etl.execute_full_load()
        else:
            etl.execute_incremental_load()
        
        etl.show_stats()
        
        total_time = time.time() - start_time
        logger.info(f"⏱️ Tempo total de execução: {total_time/60:.1f} minutos")
        logger.info("🎉 ETL concluído com sucesso!")
        
    except KeyboardInterrupt:
        logger.warning("⚠️ Processamento interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ ERRO: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    main()

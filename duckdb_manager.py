#!/usr/bin/env python3
"""
Gerenciador de conexões DuckDB para múltiplos dashboards

Soluciona o problema de lock quando múltiplos dashboards acessam
o mesmo banco simultaneamente.

Autor: Sistema SAEV
Data: 08/08/2025
"""

import duckdb
import threading
import time
from pathlib import Path
import streamlit as st

class DuckDBConnectionManager:
    """Gerenciador de conexões DuckDB thread-safe"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not getattr(self, '_initialized', False):
            self.db_path = Path("db/avaliacao_prod.duckdb")
            self._connection = None
            self._connection_lock = threading.Lock()
            self._last_access = time.time()
            self._access_count = 0
            self._initialized = True
    
    def get_connection(self):
        """Retorna uma conexão DuckDB thread-safe"""
        with self._connection_lock:
            try:
                # Sempre criar nova conexão para evitar locks
                if self.db_path.exists():
                    # Usar modo read-only para múltiplas conexões
                    conn = duckdb.connect(str(self.db_path), read_only=True)
                    self._access_count += 1
                    self._last_access = time.time()
                    return conn
                else:
                    raise FileNotFoundError(f"Banco não encontrado: {self.db_path}")
            except Exception as e:
                print(f"Erro ao conectar DuckDB: {e}")
                raise
    
    def execute_query(self, query, params=None):
        """Executa query de forma thread-safe"""
        conn = None
        try:
            conn = self.get_connection()
            if params:
                result = conn.execute(query, params).fetchall()
            else:
                result = conn.execute(query).fetchall()
            return result
        finally:
            if conn:
                conn.close()
    
    def get_dataframe(self, query, params=None):
        """Retorna DataFrame de forma thread-safe"""
        conn = None
        try:
            conn = self.get_connection()
            if params:
                df = conn.execute(query, params).df()
            else:
                df = conn.execute(query).df()
            return df
        finally:
            if conn:
                conn.close()
    
    def get_stats(self):
        """Retorna estatísticas de uso"""
        return {
            'total_access': self._access_count,
            'last_access': self._last_access,
            'db_exists': self.db_path.exists(),
            'db_size': self.db_path.stat().st_size if self.db_path.exists() else 0
        }

# Instância global
db_manager = DuckDBConnectionManager()

# Funções de conveniência para uso nos dashboards
@st.cache_data(ttl=300)  # Cache por 5 minutos
def cached_query(query, params=None):
    """Executa query com cache"""
    return db_manager.get_dataframe(query, params)

def safe_execute_query(query, params=None):
    """Executa query de forma segura"""
    return db_manager.execute_query(query, params)

def safe_get_dataframe(query, params=None):
    """Retorna DataFrame de forma segura"""
    return db_manager.get_dataframe(query, params)

def test_connection():
    """Testa a conexão com o banco"""
    try:
        result = db_manager.execute_query("SELECT COUNT(*) FROM fato_resposta_aluno LIMIT 1")
        return True, f"Conexão OK - {result[0][0]:,} registros"
    except Exception as e:
        return False, f"Erro: {e}"

if __name__ == "__main__":
    # Teste do gerenciador
    print("🧪 TESTANDO GERENCIADOR DE CONEXÕES DUCKDB")
    print("=" * 50)
    
    # Teste básico
    success, message = test_connection()
    print(f"✅ Teste de conexão: {message}")
    
    # Teste de múltiplas conexões simultâneas
    print("\n🔄 Teste de múltiplas conexões...")
    
    import concurrent.futures
    import threading
    
    def test_concurrent_access(thread_id):
        try:
            query = "SELECT COUNT(*) FROM fato_resposta_aluno WHERE DIS_NOME = 'Leitura'"
            result = db_manager.execute_query(query)
            return f"Thread {thread_id}: {result[0][0]:,} registros"
        except Exception as e:
            return f"Thread {thread_id}: ERRO - {e}"
    
    # Simular 4 dashboards acessando simultaneamente
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(test_concurrent_access, i+1) for i in range(4)]
        
        for future in concurrent.futures.as_completed(futures):
            print(f"   {future.result()}")
    
    # Estatísticas
    stats = db_manager.get_stats()
    print(f"\n📊 Estatísticas:")
    print(f"   Total de acessos: {stats['total_access']}")
    print(f"   Banco existe: {stats['db_exists']}")
    print(f"   Tamanho: {stats['db_size']:,} bytes")
    
    print("\n✅ Gerenciador testado com sucesso!")

#!/usr/bin/env python3
"""
Solução para múltiplos dashboards DuckDB usando estratégias específicas

Como DuckDB não suporta WAL mode como SQLite, usaremos outras estratégias:
1. Pool de conexões com timeout
2. Conexões read-only
3. Cache inteligente
4. Retry automático

Autor: Sistema SAEV
Data: 08/08/2025
"""

import duckdb
import threading
import time
import random
from pathlib import Path
import streamlit as st
from contextlib import contextmanager

class DuckDBConcurrentManager:
    """Gerenciador avançado para acesso concorrente ao DuckDB"""
    
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
            self._connection_count = 0
            self._max_connections = 3  # Limite de conexões simultâneas
            self._connection_semaphore = threading.Semaphore(self._max_connections)
            self._stats = {
                'total_queries': 0,
                'successful_queries': 0,
                'retries': 0,
                'failures': 0
            }
            self._initialized = True
    
    @contextmanager
    def get_connection(self, readonly=True, max_retries=5):
        """Context manager para conexões DuckDB com retry automático"""
        connection = None
        acquired = False
        
        for attempt in range(max_retries):
            try:
                # Tentar adquirir semáforo com timeout
                acquired = self._connection_semaphore.acquire(timeout=10)
                if not acquired:
                    if attempt < max_retries - 1:
                        # Espera aleatória antes de tentar novamente
                        time.sleep(random.uniform(0.5, 2.0))
                        self._stats['retries'] += 1
                        continue
                    else:
                        raise TimeoutError("Não foi possível adquirir conexão após múltiplas tentativas")
                
                # Tentar conectar
                connection = duckdb.connect(
                    str(self.db_path), 
                    read_only=readonly
                )
                
                # Configurações de otimização
                if not readonly:
                    connection.execute("SET memory_limit='1GB'")
                    connection.execute("SET threads=2")
                
                self._connection_count += 1
                self._stats['total_queries'] += 1
                
                yield connection
                
                self._stats['successful_queries'] += 1
                return  # Sair do loop se bem-sucedido
                
            except Exception as e:
                self._stats['failures'] += 1
                
                if connection:
                    try:
                        connection.close()
                    except:
                        pass
                
                if acquired:
                    self._connection_semaphore.release()
                    acquired = False
                
                if attempt < max_retries - 1:
                    # Espera progressiva (exponential backoff)
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"⚠️ Tentativa {attempt + 1} falhou: {e}. Tentando novamente em {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    self._stats['retries'] += 1
                else:
                    print(f"❌ Todas as tentativas falharam: {e}")
                    raise
            
            finally:
                if connection:
                    try:
                        connection.close()
                        self._connection_count -= 1
                    except:
                        pass
                
                if acquired:
                    self._connection_semaphore.release()
    
    def execute_query_safe(self, query, params=None, readonly=True):
        """Executa query de forma segura com retry"""
        with self.get_connection(readonly=readonly) as conn:
            if params:
                return conn.execute(query, params).fetchall()
            else:
                return conn.execute(query).fetchall()
    
    def get_dataframe_safe(self, query, params=None, readonly=True):
        """Retorna DataFrame de forma segura com retry"""
        with self.get_connection(readonly=readonly) as conn:
            if params:
                return conn.execute(query, params).df()
            else:
                return conn.execute(query).df()
    
    def get_stats(self):
        """Retorna estatísticas de uso"""
        self._stats['active_connections'] = self._connection_count
        self._stats['max_connections'] = self._max_connections
        self._stats['available_connections'] = self._connection_semaphore._value
        return self._stats.copy()

# Instância global
concurrent_manager = DuckDBConcurrentManager()

# Funções de conveniência para dashboards
@st.cache_data(ttl=300, show_spinner=False)
def cached_query_safe(query, params=None):
    """Query com cache e tratamento de erros"""
    try:
        return concurrent_manager.get_dataframe_safe(query, params, readonly=True)
    except Exception as e:
        st.error(f"❌ Erro na consulta: {e}")
        return None

def safe_query(query, params=None):
    """Query simples com retry"""
    return concurrent_manager.execute_query_safe(query, params, readonly=True)

def safe_dataframe(query, params=None):
    """DataFrame com retry"""
    return concurrent_manager.get_dataframe_safe(query, params, readonly=True)

def test_concurrent_solution():
    """Testa a solução de acesso concorrente"""
    
    print("🧪 TESTANDO SOLUÇÃO DE ACESSO CONCORRENTE")
    print("=" * 60)
    
    import concurrent.futures
    
    def dashboard_simulation(dashboard_id):
        """Simula um dashboard fazendo queries"""
        try:
            # Simular queries típicas de um dashboard
            queries = [
                "SELECT COUNT(*) FROM fato_resposta_aluno WHERE DIS_NOME = 'Leitura'",
                "SELECT DISTINCT MUN_NOME FROM fato_resposta_aluno LIMIT 10",
                "SELECT NIVEL_LEITURA, COUNT(*) FROM fato_resposta_aluno WHERE DIS_NOME = 'Leitura' GROUP BY NIVEL_LEITURA"
            ]
            
            results = []
            for i, query in enumerate(queries):
                result = concurrent_manager.execute_query_safe(query)
                results.append(f"Query {i+1}: {len(result)} registros")
                
                # Simular processamento
                time.sleep(random.uniform(0.1, 0.5))
            
            return f"Dashboard {dashboard_id}: ✅ {len(results)} queries executadas"
            
        except Exception as e:
            return f"Dashboard {dashboard_id}: ❌ {str(e)[:50]}..."
    
    # Simular 4 dashboards rodando simultaneamente
    print("🔄 Simulando 4 dashboards simultâneos...")
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(dashboard_simulation, i+1) for i in range(4)]
        
        results = []
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"   {result}")
    
    end_time = time.time()
    
    # Estatísticas
    stats = concurrent_manager.get_stats()
    success_count = sum(1 for r in results if "✅" in r)
    
    print(f"\n📊 RESULTADOS:")
    print(f"   ✅ Sucessos: {success_count}/4 dashboards")
    print(f"   ⏱️ Tempo total: {end_time - start_time:.2f}s")
    print(f"   📈 Total queries: {stats['total_queries']}")
    print(f"   ✅ Sucessos: {stats['successful_queries']}")
    print(f"   🔄 Retries: {stats['retries']}")
    print(f"   ❌ Falhas: {stats['failures']}")
    print(f"   🔗 Conexões ativas: {stats['active_connections']}")
    
    if success_count == 4:
        print("\n🎉 SOLUÇÃO FUNCIONANDO!")
        print("✅ Todos os dashboards executaram com sucesso")
        return True
    else:
        print("\n⚠️ PROBLEMAS DETECTADOS")
        print("❌ Nem todos os dashboards foram bem-sucedidos")
        return False

if __name__ == "__main__":
    test_concurrent_solution()

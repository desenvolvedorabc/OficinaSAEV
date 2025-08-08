#!/usr/bin/env python3
"""
Configuração do DuckDB para suporte a múltiplas conexões simultâneas

Este script configura o banco DuckDB para usar WAL mode,
permitindo que múltiplos dashboards acessem simultaneamente.

Autor: Sistema SAEV
Data: 08/08/2025
"""

import duckdb
from pathlib import Path
import shutil
import time

def configure_duckdb_for_concurrent_access():
    """Configura DuckDB para acesso concorrente"""
    
    db_path = Path("db/avaliacao_prod.duckdb")
    
    if not db_path.exists():
        print("❌ Banco de dados não encontrado!")
        return False
    
    print("🔧 CONFIGURANDO DUCKDB PARA ACESSO CONCORRENTE")
    print("=" * 60)
    
    # Backup do banco original
    backup_path = db_path.with_suffix('.duckdb.backup')
    print(f"💾 Criando backup: {backup_path}")
    shutil.copy2(db_path, backup_path)
    
    try:
        # Conectar ao banco
        print("🔌 Conectando ao banco...")
        conn = duckdb.connect(str(db_path))
        
        # Configurar para WAL mode (permite múltiplas conexões de leitura)
        print("⚙️ Configurando WAL mode...")
        conn.execute("PRAGMA journal_mode=WAL")
        
        # Otimizações para acesso concorrente
        print("⚡ Aplicando otimizações...")
        conn.execute("PRAGMA synchronous=NORMAL")  # Balance entre performance e segurança
        conn.execute("PRAGMA cache_size=10000")    # Aumentar cache
        conn.execute("PRAGMA temp_store=memory")   # Usar memória para temporários
        conn.execute("PRAGMA mmap_size=268435456") # 256MB de mmap
        
        # Verificar configurações
        print("🔍 Verificando configurações aplicadas...")
        
        journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        synchronous = conn.execute("PRAGMA synchronous").fetchone()[0]
        cache_size = conn.execute("PRAGMA cache_size").fetchone()[0]
        
        print(f"   📋 Journal mode: {journal_mode}")
        print(f"   🔄 Synchronous: {synchronous}")
        print(f"   💾 Cache size: {cache_size}")
        
        # Testar acesso concorrente
        print("\n🧪 Testando acesso concorrente...")
        
        # Criar múltiplas conexões para teste
        test_connections = []
        for i in range(4):
            try:
                test_conn = duckdb.connect(str(db_path), read_only=True)
                result = test_conn.execute("SELECT COUNT(*) FROM fato_resposta_aluno LIMIT 1").fetchone()
                test_connections.append(test_conn)
                print(f"   ✅ Conexão {i+1}: {result[0]:,} registros")
            except Exception as e:
                print(f"   ❌ Conexão {i+1}: {e}")
                return False
        
        # Fechar conexões de teste
        for test_conn in test_connections:
            test_conn.close()
        
        conn.close()
        
        print("\n✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("🚀 DuckDB configurado para múltiplas conexões simultâneas")
        print(f"💾 Backup salvo em: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante configuração: {e}")
        
        # Restaurar backup em caso de erro
        if backup_path.exists():
            print("🔄 Restaurando backup...")
            shutil.copy2(backup_path, db_path)
            print("✅ Backup restaurado")
        
        return False

def test_concurrent_access():
    """Testa acesso concorrente ao banco"""
    
    print("\n🧪 TESTE DE ACESSO CONCORRENTE")
    print("=" * 40)
    
    db_path = Path("db/avaliacao_prod.duckdb")
    
    if not db_path.exists():
        print("❌ Banco não encontrado")
        return False
    
    import concurrent.futures
    import threading
    
    def test_connection(thread_id):
        """Testa uma conexão individual"""
        try:
            conn = duckdb.connect(str(db_path), read_only=True)
            
            # Query de teste
            query = "SELECT COUNT(*) FROM fato_resposta_aluno WHERE DIS_NOME = 'Leitura'"
            result = conn.execute(query).fetchone()
            
            conn.close()
            
            return f"Thread {thread_id}: ✅ {result[0]:,} registros"
            
        except Exception as e:
            return f"Thread {thread_id}: ❌ {str(e)[:50]}..."
    
    # Simular 4 dashboards acessando simultaneamente
    print("🔄 Simulando 4 dashboards simultâneos...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(test_connection, i+1) for i in range(4)]
        
        results = []
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"   {result}")
    
    # Verificar se todos foram bem-sucedidos
    success_count = sum(1 for r in results if "✅" in r)
    
    print(f"\n📊 Resultado: {success_count}/4 conexões bem-sucedidas")
    
    if success_count == 4:
        print("✅ TESTE PASSOU - Acesso concorrente funcionando!")
        return True
    else:
        print("❌ TESTE FALHOU - Problema de acesso concorrente")
        return False

def main():
    """Função principal"""
    
    print("🚀 CONFIGURADOR DUCKDB PARA MÚLTIPLOS DASHBOARDS")
    print("=" * 70)
    print("Objetivo: Resolver problema de lock com 4+ dashboards simultâneos")
    print("Data:", time.strftime("%d/%m/%Y %H:%M:%S"))
    print("=" * 70)
    
    # Passo 1: Configurar banco
    print("\n📝 PASSO 1: Configuração do banco")
    config_success = configure_duckdb_for_concurrent_access()
    
    if not config_success:
        print("❌ Falha na configuração. Abortando.")
        return False
    
    # Passo 2: Testar acesso concorrente
    print("\n📝 PASSO 2: Teste de acesso concorrente")
    test_success = test_concurrent_access()
    
    if test_success:
        print("\n🎉 CONFIGURAÇÃO COMPLETA!")
        print("✅ DuckDB pronto para múltiplos dashboards")
        print("🚀 Agora você pode executar a opção 5 (todos os aplicativos)")
        print("\n💡 Para testar:")
        print("   ./start_saev_universal.sh")
        print("   Escolha opção 5")
        return True
    else:
        print("\n⚠️ CONFIGURAÇÃO PARCIAL")
        print("❌ Ainda há problemas de acesso concorrente")
        print("💡 Tente usar o gerenciador de conexões como alternativa")
        return False

if __name__ == "__main__":
    main()

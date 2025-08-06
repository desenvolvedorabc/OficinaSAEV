#!/usr/bin/env python3
"""Script para debugar lentidão na inicialização do Streamlit"""

import time
import sys
import os

def time_import(module_name):
    """Mede tempo de import de um módulo"""
    start = time.time()
    try:
        __import__(module_name)
        duration = time.time() - start
        print(f"✅ {module_name}: {duration:.3f}s")
        return duration
    except ImportError as e:
        print(f"❌ {module_name}: {e}")
        return 0

def main():
    print("🚀 Diagnóstico detalhado da inicialização Streamlit\n")
    
    # 1. Teste de imports básicos
    print("📦 1. Testando imports principais:")
    total_import_time = 0
    modules = [
        'streamlit',
        'pandas', 
        'numpy',
        'plotly',
        'duckdb',
        'altair',
        'matplotlib'
    ]
    
    for module in modules:
        total_import_time += time_import(module)
    
    print(f"\n⏱️ Tempo total de imports: {total_import_time:.3f}s\n")
    
    # 2. Teste de inicialização do Streamlit
    print("🔧 2. Testando inicialização interna do Streamlit:")
    
    start = time.time()
    import streamlit as st
    print(f"✅ import streamlit: {time.time() - start:.3f}s")
    
    start = time.time()
    from streamlit import config
    print(f"✅ streamlit.config: {time.time() - start:.3f}s")
    
    start = time.time()
    from streamlit.web import bootstrap
    print(f"✅ streamlit.web.bootstrap: {time.time() - start:.3f}s")
    
    # 3. Teste de rede
    print("\n🌐 3. Testando configurações de rede:")
    import socket
    
    start = time.time()
    try:
        socket.gethostbyname('localhost')
        print(f"✅ Resolução localhost: {time.time() - start:.3f}s")
    except Exception as e:
        print(f"❌ Resolução localhost: {e}")
    
    # 4. Informações do sistema
    print("\n💻 4. Informações do sistema:")
    print(f"   Python: {sys.version}")
    print(f"   Plataforma: {sys.platform}")
    print(f"   Arquitetura: {sys.implementation.name}")
    
    # 5. Cache do Python
    print("\n🗂️ 5. Informações de cache:")
    pyc_files = 0
    for root, dirs, files in os.walk('.'):
        pyc_files += len([f for f in files if f.endswith('.pyc')])
    print(f"   Arquivos .pyc no projeto: {pyc_files}")
    
    print(f"\n🎯 Diagnóstico concluído!")

if __name__ == "__main__":
    main()

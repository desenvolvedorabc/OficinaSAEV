#!/usr/bin/env python3
"""Script para testar apenas o servidor Streamlit sem app"""

import streamlit as st
import time
import threading
import requests
import sys
from streamlit.web import bootstrap

def test_streamlit_server():
    print("🔥 Teste direto do servidor Streamlit (sem streamlit run)")
    
    # Criar um app mínimo na memória
    app_script = '''
import streamlit as st
st.write("Servidor funcionando!")
'''
    
    with open('/tmp/minimal_streamlit_test.py', 'w') as f:
        f.write(app_script)
    
    print("📡 Iniciando servidor diretamente...")
    start_time = time.time()
    
    # Simular o que streamlit run faz internamente
    sys.argv = ['streamlit', 'run', '/tmp/minimal_streamlit_test.py', '--server.port=8590', '--server.headless=true']
    
    try:
        from streamlit.web.cli import main_run
        print(f"⚙️ Servidor configurado em: {time.time() - start_time:.3f}s")
        
        # O server vai rodar em background
        def run_server():
            main_run(['/tmp/minimal_streamlit_test.py'], 
                    flag_options={'server.port': 8590, 'server.headless': True})
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Aguardar servidor estar pronto
        for i in range(300):  # 30 segundos máximo
            try:
                response = requests.get('http://localhost:8590', timeout=1)
                if response.status_code == 200:
                    total_time = time.time() - start_time
                    print(f"✅ Servidor respondendo em: {total_time:.3f}s")
                    return
            except:
                pass
            time.sleep(0.1)
        
        print("❌ Timeout: servidor não respondeu em 30s")
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
    finally:
        import os
        try:
            os.remove('/tmp/minimal_streamlit_test.py')
        except:
            pass

if __name__ == "__main__":
    test_streamlit_server()

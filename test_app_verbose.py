import streamlit as st
import time
import sys
import os

# Log de debug
print(f"🚀 {time.strftime('%H:%M:%S')} - Iniciando app de teste", file=sys.stderr)
print(f"🔧 {time.strftime('%H:%M:%S')} - Python PID: {os.getpid()}", file=sys.stderr)

st.write("App de teste inicializado!")
st.write(f"Hora de início: {time.strftime('%H:%M:%S')}")

print(f"✅ {time.strftime('%H:%M:%S')} - App configurado", file=sys.stderr)

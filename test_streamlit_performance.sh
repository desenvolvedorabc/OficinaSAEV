#!/bin/bash
# 🕒 Script para medir tempo de startup do Streamlit

echo "⏱️ Medindo tempo de startup do Streamlit..."
echo "📊 Testando com app mínimo..."

# Criar app mínimo para teste
cat > /tmp/test_streamlit_minimal.py << 'EOF'
import streamlit as st
import time

st.write("App minimal - teste de performance")
st.write(f"Carregado em: {time.time()}")
EOF

echo "🚀 Iniciando Streamlit..."
START_TIME=$(date +%s)

cd /Users/rcaratti/Desktop/ABC/SAEV/OficinaSAEV
source venv_saev/bin/activate

# Capturar output e extrair tempo quando server estiver pronto
streamlit run /tmp/test_streamlit_minimal.py --server.port 8499 --server.headless true > /tmp/streamlit_output.log 2>&1 &
STREAMLIT_PID=$!

# Aguardar até o servidor estar pronto (máximo 30 segundos)
for i in {1..300}; do
    if curl -s http://localhost:8499 >/dev/null 2>&1; then
        STARTUP_TIME=$((i * 100))  # tempo em milissegundos
        break
    fi
    sleep 0.1
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "✅ Streamlit mínimo pronto em: ${STARTUP_TIME}ms (${DURATION}s total)"

# Mostrar início do log para debug
echo "Log do Streamlit mínimo (primeiras 20 linhas):"
head -20 /tmp/streamlit_output.log

# Limpar
kill $STREAMLIT_PID 2>/dev/null
wait $STREAMLIT_PID 2>/dev/null
rm -f /tmp/test_streamlit_minimal.py /tmp/streamlit_output.log

# Testar agora com app real do SAEV
echo ""
echo "📊 Testando com app SAEV real..."
START_TIME=$(date +%s)

streamlit run saev_streamlit.py --server.port 8498 --server.headless true > /tmp/saev_streamlit_output.log 2>&1 &
STREAMLIT_PID=$!

# Aguardar até o servidor estar pronto (máximo 60 segundos para app real)
for i in {1..600}; do
    if curl -s http://localhost:8498 >/dev/null 2>&1; then
        SAEV_STARTUP_TIME=$((i * 100))  # tempo em milissegundos
        break
    fi
    sleep 0.1
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "✅ SAEV app pronto em: ${SAEV_STARTUP_TIME}ms (${DURATION}s total)"

# Mostrar log do SAEV
echo "Log do SAEV app (primeiras 30 linhas):"
head -30 /tmp/saev_streamlit_output.log

# Limpar
kill $STREAMLIT_PID 2>/dev/null
wait $STREAMLIT_PID 2>/dev/null
rm -f /tmp/saev_streamlit_output.log

echo ""
echo "🎯 Diagnóstico completo!"

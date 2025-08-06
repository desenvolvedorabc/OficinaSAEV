#!/bin/bash
# 🚀 Script para executar apps Streamlit com inicialização rápida

echo "🚀 SAEV Streamlit - Inicialização Otimizada"
echo "==========================================="

cd /Users/rcaratti/Desktop/ABC/SAEV/OficinaSAEV
source venv_saev/bin/activate

# Verificar se otimização está aplicada
if grep -q "serverAddress.*localhost" .streamlit/config.toml; then
    echo "✅ Configuração otimizada detectada"
else
    echo "⚠️ Aplicando otimização..."
    if ! grep -q "\[browser\]" .streamlit/config.toml; then
        echo -e "\n[browser]" >> .streamlit/config.toml
    fi
    if ! grep -q "serverAddress" .streamlit/config.toml; then
        sed -i '' '/\[browser\]/a\
serverAddress = "localhost"' .streamlit/config.toml
    fi
fi

APP_FILE=${1:-saev_streamlit.py}
PORT=${2:-8501}

echo "📊 Iniciando $APP_FILE na porta $PORT..."
echo "🌐 Acesse: http://localhost:$PORT"
echo "⚡ Inicialização otimizada (sem descoberta de IP externo)"
echo ""

streamlit run $APP_FILE --server.port $PORT

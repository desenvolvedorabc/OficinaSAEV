#!/bin/bash

# 🚀 Script de Inicialização do SAEV Streamlit
# Executa o aplicativo web com todas as configurações otimizadas

echo "📊 SAEV - Sistema de Análise Educacional"
echo "🚀 Iniciando aplicativo Streamlit..."
echo "=========================================="

# Verificar se estamos na pasta correta
if [ ! -f "streamlit_app.py" ]; then
    echo "❌ Erro: Execute este script na pasta raiz do projeto OficinaSAEV"
    exit 1
fi

# Verificar se o banco de dados existe
if [ ! -f "db/avaliacao_prod.duckdb" ]; then
    echo "❌ Erro: Banco de dados não encontrado em db/avaliacao_prod.duckdb"
    echo "💡 Execute o ETL primeiro: python run_etl.py full"
    exit 1
fi

# Parar qualquer processo Streamlit rodando na porta 8501
echo "🧹 Parando processos Streamlit anteriores..."
lsof -ti:8501 | xargs kill -9 2>/dev/null || echo "✅ Nenhum processo anterior encontrado"

# Verificar dependências
echo "🔍 Verificando dependências..."
python -c "import streamlit, plotly, pandas, duckdb" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
fi

echo "✅ Dependências verificadas!"
echo ""

# Configurações do Streamlit
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Obter IP local (compatível com macOS)
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')

# Iniciar aplicativo
echo "🌐 Iniciando servidor Streamlit..."
echo "📍 URL Local: http://localhost:8501"
if [ -n "$LOCAL_IP" ]; then
    echo "📍 URL de Rede: http://$LOCAL_IP:8501"
else
    echo "📍 URL de Rede: Não disponível"
fi
echo ""
echo "💡 Dica: Use Ctrl+C para parar o servidor"
echo "=========================================="

streamlit run streamlit_app.py \
    --server.port=8501 \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false

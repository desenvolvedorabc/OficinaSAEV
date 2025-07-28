#!/bin/bash

# SAEV Streamlit 2 - Script de Inicialização
# Dashboard Interativo com Filtros
# Arquivo: start_streamlit2.sh

echo "🚀 Iniciando SAEV Streamlit 2 - Dashboard com Filtros..."
echo "================================================="

# Verificar se estamos no diretório correto
EXPECTED_DIR="/Users/rcaratti/Desktop/ABC/SAEV/OficinaSAEV"
CURRENT_DIR=$(pwd)

if [ "$CURRENT_DIR" != "$EXPECTED_DIR" ]; then
    echo "⚠️  Mudando para o diretório correto..."
    cd "$EXPECTED_DIR" || {
        echo "❌ Erro: Não foi possível acessar o diretório $EXPECTED_DIR"
        exit 1
    }
fi

echo "📂 Diretório atual: $(pwd)"

# Verificar se o arquivo do aplicativo existe
if [ ! -f "saev_streamlit2.py" ]; then
    echo "❌ Erro: Arquivo saev_streamlit2.py não encontrado!"
    echo "   Certifique-se de que o arquivo está no diretório correto."
    exit 1
fi

# Verificar se o banco de dados existe
if [ ! -f "db/avaliacao_prod.duckdb" ]; then
    echo "❌ Erro: Banco de dados db/avaliacao_prod.duckdb não encontrado!"
    echo "   Execute primeiro o script de preparação dos dados."
    exit 1
fi

# Verificar se o Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Erro: Python3 não está instalado ou não está no PATH"
    exit 1
fi

echo "🐍 Python encontrado: $(python3 --version)"

# Verificar se o Streamlit está instalado
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "❌ Erro: Streamlit não está instalado!"
    echo "   Execute: pip install streamlit"
    exit 1
fi

echo "📊 Streamlit encontrado: $(python3 -c "import streamlit; print(streamlit.__version__)")"

# Verificar dependências essenciais
echo "🔍 Verificando dependências..."

dependencies=("duckdb" "pandas" "plotly")
for dep in "${dependencies[@]}"; do
    if ! python3 -c "import $dep" &> /dev/null; then
        echo "❌ Erro: $dep não está instalado!"
        echo "   Execute: pip install $dep"
        exit 1
    else
        version=$(python3 -c "import $dep; print($dep.__version__)" 2>/dev/null || echo "versão não detectada")
        echo "✅ $dep: $version"
    fi
done

# Obter endereço IP local (método compatível com macOS)
if command -v ifconfig &> /dev/null; then
    LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
else
    LOCAL_IP="localhost"
fi

# Definir porta (evitar conflito com o primeiro app)
PORT=8502

echo ""
echo "🌐 Configuração de Rede:"
echo "   Local: http://localhost:$PORT"
if [ "$LOCAL_IP" != "localhost" ]; then
    echo "   Rede:  http://$LOCAL_IP:$PORT"
fi

echo ""
echo "🎯 Características do Dashboard:"
echo "   ✅ Filtros Interativos: Município, Disciplina, Série, Teste"
echo "   ✅ 8 Métricas Principais (KPIs)"
echo "   ✅ 6 Visualizações Interativas"
echo "   ✅ Tabelas Detalhadas"
echo "   ✅ Interface Responsiva"

echo ""
echo "📊 Executando SAEV Streamlit 2..."
echo "   Arquivo: saev_streamlit2.py"
echo "   Porta: $PORT"
echo ""
echo "⏳ Carregando aplicação..."
echo "   (Pressione Ctrl+C para parar)"

# Executar o Streamlit na porta 8502
streamlit run saev_streamlit2.py --server.port=$PORT --server.headless=true --server.fileWatcherType=none

echo ""
echo "🛑 SAEV Streamlit 2 foi interrompido."
echo "   Para reiniciar, execute novamente: ./start_streamlit2.sh"

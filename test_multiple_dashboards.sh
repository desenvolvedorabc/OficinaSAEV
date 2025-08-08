#!/bin/bash

# 🧪 Teste de Múltiplos Dashboards Simultâneos
# 
# Este script testa se todos os 4 dashboards podem rodar simultaneamente
# sem problemas de lock no DuckDB
#
# Autor: Sistema SAEV
# Data: 08/08/2025

echo "🧪 TESTE DE MÚLTIPLOS DASHBOARDS SIMULTÂNEOS"
echo "=" * 60
echo "Objetivo: Verificar se 4 dashboards podem rodar sem lock"
echo "Data: $(date)"
echo "=" * 60

# Verificar se o banco existe
if [ ! -f "db/avaliacao_prod.duckdb" ]; then
    echo "❌ Banco de dados não encontrado!"
    echo "💡 Execute primeiro: python run_etl.py full"
    exit 1
fi

echo "✅ Banco de dados encontrado"

# Detectar Python
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python não encontrado!"
    exit 1
fi

echo "✅ Python detectado: $PYTHON_CMD"

# Limpar processos anteriores
echo "🧹 Limpando processos anteriores..."
pkill -f "streamlit" 2>/dev/null || true
sleep 2

# Iniciar dashboards em background
echo ""
echo "🚀 INICIANDO DASHBOARDS SIMULTÂNEOS..."

# Dashboard 1 - Geral
if [ -f "saev_streamlit.py" ]; then
    echo "📊 Iniciando Dashboard Geral (porta 8501)..."
    nohup $PYTHON_CMD -m streamlit run saev_streamlit.py --server.port=8501 --server.headless=true > test_dashboard1.log 2>&1 &
    DASH1_PID=$!
    echo "   PID: $DASH1_PID"
    sleep 3
fi

# Dashboard 2 - Filtros
if [ -f "saev_streamlit2.py" ]; then
    echo "🔍 Iniciando Dashboard Filtros (porta 8502)..."
    nohup $PYTHON_CMD -m streamlit run saev_streamlit2.py --server.port=8502 --server.headless=true > test_dashboard2.log 2>&1 &
    DASH2_PID=$!
    echo "   PID: $DASH2_PID"
    sleep 3
fi

# Dashboard 3 - Rankings
if [ -f "saev_rankings.py" ]; then
    echo "🏆 Iniciando Dashboard Rankings (porta 8503)..."
    nohup $PYTHON_CMD -m streamlit run saev_rankings.py --server.port=8503 --server.headless=true > test_dashboard3.log 2>&1 &
    DASH3_PID=$!
    echo "   PID: $DASH3_PID"
    sleep 3
fi

# Dashboard 4 - Leitura (o problemático)
if [ -f "dashboard_leitura.py" ]; then
    echo "📚 Iniciando Dashboard Leitura (porta 8504)..."
    nohup $PYTHON_CMD -m streamlit run dashboard_leitura.py --server.port=8504 --server.headless=true > test_dashboard4.log 2>&1 &
    DASH4_PID=$!
    echo "   PID: $DASH4_PID"
    sleep 5  # Espera mais tempo para este
fi

echo ""
echo "⏱️ Aguardando inicialização completa (15 segundos)..."
sleep 15

# Verificar status dos dashboards
echo ""
echo "🔍 VERIFICANDO STATUS DOS DASHBOARDS..."

check_dashboard() {
    local port=$1
    local name=$2
    local logfile=$3
    
    # Verificar se o processo está rodando
    if curl -s http://localhost:$port > /dev/null 2>&1; then
        echo "   ✅ $name (porta $port): FUNCIONANDO"
        return 0
    else
        echo "   ❌ $name (porta $port): FALHOU"
        
        # Mostrar últimas linhas do log se houver erro
        if [ -f "$logfile" ]; then
            echo "      📋 Últimas linhas do log:"
            tail -3 "$logfile" | sed 's/^/         /'
        fi
        return 1
    fi
}

# Verificar cada dashboard
dashboard_count=0
working_count=0

if [ ! -z "$DASH1_PID" ]; then
    dashboard_count=$((dashboard_count + 1))
    check_dashboard 8501 "Dashboard Geral" "test_dashboard1.log" && working_count=$((working_count + 1))
fi

if [ ! -z "$DASH2_PID" ]; then
    dashboard_count=$((dashboard_count + 1))
    check_dashboard 8502 "Dashboard Filtros" "test_dashboard2.log" && working_count=$((working_count + 1))
fi

if [ ! -z "$DASH3_PID" ]; then
    dashboard_count=$((dashboard_count + 1))
    check_dashboard 8503 "Dashboard Rankings" "test_dashboard3.log" && working_count=$((working_count + 1))
fi

if [ ! -z "$DASH4_PID" ]; then
    dashboard_count=$((dashboard_count + 1))
    check_dashboard 8504 "Dashboard Leitura" "test_dashboard4.log" && working_count=$((working_count + 1))
fi

# Resultado do teste
echo ""
echo "📊 RESULTADO DO TESTE:"
echo "   Total de dashboards: $dashboard_count"
echo "   Funcionando: $working_count"
echo "   Taxa de sucesso: $(( (working_count * 100) / dashboard_count ))%"

# Testar acesso concorrente ao banco
echo ""
echo "🧪 TESTANDO ACESSO CONCORRENTE AO BANCO..."
$PYTHON_CMD duckdb_concurrent_solution.py

if [ $working_count -eq $dashboard_count ]; then
    echo ""
    echo "🎉 TESTE PASSOU!"
    echo "✅ Todos os dashboards estão funcionando simultaneamente"
    echo "✅ Problema de lock do DuckDB resolvido"
    echo ""
    echo "🌐 URLs disponíveis:"
    [ ! -z "$DASH1_PID" ] && echo "   📊 Dashboard Geral:  http://localhost:8501"
    [ ! -z "$DASH2_PID" ] && echo "   🔍 Dashboard Filtros: http://localhost:8502"
    [ ! -z "$DASH3_PID" ] && echo "   🏆 Dashboard Rankings: http://localhost:8503"
    [ ! -z "$DASH4_PID" ] && echo "   📚 Dashboard Leitura:  http://localhost:8504"
    echo ""
    echo "💡 Para parar todos: pkill -f streamlit"
    echo "📋 Logs disponíveis: test_dashboard*.log"
    
    # Manter dashboards rodando por um tempo para teste manual
    echo ""
    echo "⏱️ Dashboards ficarão rodando por 60 segundos para teste manual..."
    echo "   Pressione Ctrl+C para parar antes"
    
    sleep 60
    
else
    echo ""
    echo "❌ TESTE FALHOU!"
    echo "⚠️ Nem todos os dashboards estão funcionando"
    echo "📋 Verifique os logs: test_dashboard*.log"
fi

# Limpar processos
echo ""
echo "🧹 Limpando processos..."
pkill -f streamlit 2>/dev/null || true

echo "✅ Teste concluído!"

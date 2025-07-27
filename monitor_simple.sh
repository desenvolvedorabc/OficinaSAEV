#!/bin/bash

# Script simples para monitorar o ETL
echo "🔍 Monitor ETL SAEV - Pressione Ctrl+C para sair"
echo "================================================"
echo ""
echo "💡 DICAS:"
echo "   - Abra outro terminal para executar: python test_memory_optimized.py --mode full"
echo "   - Use 'htop' em outro terminal para detalhes do sistema"
echo ""

while true; do
    # Cabeçalho com timestamp
    clear
    echo "🕐 $(date '+%H:%M:%S') - Status do ETL SAEV"
    echo "========================================"
    echo ""
    
    # Memória do sistema
    echo "💾 MEMÓRIA:"
    free -h | head -2
    echo ""
    
    # Processos Python relacionados ao ETL
    echo "🐍 PROCESSOS PYTHON:"
    ps aux | grep -i python | grep -v grep | grep -E "(saev|etl)" | head -3 || echo "   Nenhum processo ETL ativo"
    echo ""
    
    # Tamanho do banco de dados se existir
    if [ -f "db/avaliacao_prod.duckdb" ]; then
        size=$(du -h db/avaliacao_prod.duckdb 2>/dev/null | cut -f1 || echo "N/A")
        echo "📁 BANCO: ${size}"
    else
        echo "📁 BANCO: Não encontrado"
    fi
    echo ""
    
    # Últimas linhas do log se existir
    if [ -f "etl_saev.log" ]; then
        echo "📝 ÚLTIMAS ATIVIDADES:"
        tail -3 etl_saev.log 2>/dev/null | sed 's/^/   /' || echo "   Log não disponível"
    else
        echo "📝 LOG: Não encontrado"
    fi
    echo ""
    
    # Espaço em disco
    echo "💿 ESPAÇO EM DISCO:"
    df -h . | tail -1
    echo ""
    
    echo "⏰ Próxima atualização em 5 segundos..."
    sleep 5
done

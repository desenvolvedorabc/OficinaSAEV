#!/bin/bash

# 🧹 Script de Limpeza dos Artefatos Gerados pelos Scripts R
# Remove todos os arquivos gerados pelos scripts R que não devem ser versionados

echo "🧹 === LIMPEZA DOS ARTEFATOS GERADOS PELOS SCRIPTS R ==="
echo ""

# Função para remover arquivos com segurança
safe_remove() {
    local pattern="$1"
    local description="$2"
    
    # Contar arquivos antes da remoção
    local count=$(find R/ -name "$pattern" 2>/dev/null | wc -l | tr -d ' ')
    
    if [ "$count" -gt 0 ]; then
        echo "🗑️  Removendo $description ($count arquivos)..."
        find R/ -name "$pattern" -type f -delete 2>/dev/null
        echo "   ✅ $count arquivo(s) removido(s)"
    else
        echo "   ℹ️  Nenhum arquivo encontrado: $description"
    fi
}

# Função para remover diretórios com segurança
safe_remove_dir() {
    local dir="$1"
    local description="$2"
    
    if [ -d "$dir" ] && [ "$(ls -A $dir 2>/dev/null | grep -v README)" ]; then
        echo "📁 Removendo conteúdo de $description..."
        # Remove tudo exceto README.md
        find "$dir" -type f ! -name "README.md" -delete 2>/dev/null
        find "$dir" -type d -empty -delete 2>/dev/null
        echo "   ✅ Conteúdo removido de $dir"
    else
        echo "   ℹ️  Diretório vazio ou não existe: $description"
    fi
}

echo "📋 Removendo arquivos por tipo..."
echo ""

# 1. Relatórios Markdown gerados
echo "1️⃣ Relatórios Markdown gerados:"
safe_remove "relatorio_*.md" "relatórios Markdown"
safe_remove "*_relatorio_*.md" "relatórios Markdown alternativos"

# 2. Gráficos e visualizações
echo ""
echo "2️⃣ Gráficos e visualizações:"
safe_remove "*.png" "imagens PNG"
safe_remove "*.jpg" "imagens JPG"
safe_remove "*.jpeg" "imagens JPEG"
safe_remove "*.pdf" "arquivos PDF"
safe_remove "*.svg" "imagens SVG"

# 3. Dashboards HTML
echo ""
echo "3️⃣ Dashboards HTML:"
safe_remove "*.html" "arquivos HTML"

# 4. Dados CSV exportados
echo ""
echo "4️⃣ Dados CSV exportados:"
safe_remove "dados_*.csv" "dados CSV"
safe_remove "resultado_*.csv" "resultados CSV"
safe_remove "painel_*.csv" "dados de painel CSV"
safe_remove "relatorio_*.csv" "relatórios CSV"
safe_remove "analise_*.csv" "análises CSV"

# 5. Arquivos temporários do R
echo ""
echo "5️⃣ Arquivos temporários do R:"
safe_remove ".Rhistory" "histórico do R"
safe_remove ".RData" "dados do R"
safe_remove ".Ruserdata" "dados do usuário R"
safe_remove "Rplots.pdf" "gráficos padrão do R"

# 6. Logs
echo ""
echo "6️⃣ Logs e arquivos temporários:"
safe_remove "*.log" "arquivos de log"
safe_remove "log_*.txt" "logs de texto"

# 7. Diretórios de saída (preservando README.md)
echo ""
echo "7️⃣ Limpando diretórios de saída:"
safe_remove_dir "R/painel_graficos" "gráficos do painel"
safe_remove_dir "R/painel_html" "HTML do painel"
safe_remove_dir "R/painel_dados" "dados do painel"
safe_remove_dir "R/output" "saída geral"
safe_remove_dir "R/exports" "exportações"
safe_remove_dir "R/generated" "arquivos gerados"
safe_remove_dir "R/graficos" "gráficos"
safe_remove_dir "R/dashboard" "dashboard"
safe_remove_dir "R/.cache" "cache do R"
safe_remove_dir "R/cache" "cache alternativo"

echo ""
echo "🎯 === RESUMO DA LIMPEZA ==="
echo ""

# Mostrar estrutura atual da pasta R
echo "📁 Estrutura atual da pasta R/ (apenas arquivos versionados):"
find R/ -type f -name "*.R" -o -name "*.md" | grep -E "\.(R|md)$" | sort

echo ""
echo "📋 Arquivos que DEVEM ser versionados:"
echo "   ✅ Scripts R (*.R)"
echo "   ✅ Documentação (README*.md, *INSTRUCOES*.md, etc.)"
echo "   ✅ Arquivos de configuração"

echo ""
echo "🚫 Arquivos que NÃO devem ser versionados (foram removidos):"
echo "   ❌ Relatórios gerados (relatorio_*.md)"
echo "   ❌ Dados CSV gerados (dados_*.csv, resultado_*.csv)"
echo "   ❌ Gráficos (*.png, *.jpg, *.pdf)"
echo "   ❌ Dashboards HTML (*.html)"
echo "   ❌ Arquivos temporários do R"

echo ""
echo "✅ Limpeza concluída!"
echo ""
echo "💡 DICA: Execute este script sempre que quiser limpar os artefatos gerados:"
echo "   bash clean_r_artifacts.sh"
echo ""
echo "📝 NOTA: O .gitignore foi atualizado para evitar que esses arquivos sejam versionados no futuro."

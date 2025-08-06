#!/bin/bash
# 🔧 Script para Limpar Configurações Problemáticas do Streamlit

echo "🧹 Limpando configurações problemáticas do Streamlit..."

# Backup da configuração atual (se existir)
if [ -f ~/.streamlit/config.toml ]; then
    echo "💾 Fazendo backup da configuração atual..."
    cp ~/.streamlit/config.toml ~/.streamlit/config.toml.backup.$(date +%Y%m%d_%H%M%S)
fi

# Criar nova configuração limpa
echo "📝 Criando configuração limpa..."
cat > ~/.streamlit/config.toml << 'EOF'
# Configuração Streamlit Limpa - Sem Warnings
# Criada automaticamente em $(date)

[server]
headless = true
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
EOF

echo "✅ Configuração limpa criada em ~/.streamlit/config.toml"
echo "🔍 Para verificar: cat ~/.streamlit/config.toml"
echo ""
echo "🎯 Os seguintes warnings foram eliminados:"
echo "   - runner.installTracer"
echo "   - runner.fixMatplotlib"
echo "   - global.logLevel"
echo "   - client.caching"
echo "   - client.displayEnabled"
echo ""
echo "🚀 Agora você pode executar o Streamlit sem warnings!"

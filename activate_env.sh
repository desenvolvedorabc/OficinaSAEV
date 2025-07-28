#!/bin/bash

# =============================================================================
# Script de Ativação do Ambiente Virtual - OficinaSAEV
# =============================================================================

echo "🐍 Ativando ambiente virtual do SAEV..."

# Verifica se está no diretório correto
if [ ! -d "venv_saev" ]; then
    echo "❌ Erro: Diretório venv_saev não encontrado!"
    echo "   Certifique-se de estar no diretório do projeto OficinaSAEV"
    echo "   Diretório atual: $(pwd)"
    exit 1
fi

# Verifica se o arquivo activate existe
if [ ! -f "venv_saev/bin/activate" ]; then
    echo "❌ Erro: Arquivo activate não encontrado!"
    echo "   O ambiente virtual pode estar corrompido."
    echo "   Execute: python3 -m venv venv_saev"
    exit 1
fi

# Ativa o ambiente virtual
source venv_saev/bin/activate

# Verifica se a ativação funcionou
if [[ "$VIRTUAL_ENV" == *"venv_saev"* ]]; then
    echo "✅ Ambiente virtual ativado com sucesso!"
    echo "🐍 Python: $(python --version)"
    echo "📍 Localização: $(which python)"
    echo ""
    echo "🚀 Agora você pode executar:"
    echo "   python run_etl.py full          # Carga completa"
    echo "   python run_etl.py incremental   # Carga incremental"
    echo ""
    echo "💡 Para desativar: deactivate"
else
    echo "❌ Falha ao ativar o ambiente virtual"
    echo "🔧 Tente o método alternativo:"
    echo "   bash -c \"source venv_saev/bin/activate && exec bash\""
fi

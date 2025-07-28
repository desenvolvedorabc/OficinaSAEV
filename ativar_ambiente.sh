#!/bin/bash

# Script para ativar o ambiente conda SAEV
# Uso: source ativar_ambiente.sh

# Garantir que o conda está inicializado
export PATH="$HOME/miniconda/bin:$PATH"

# Inicializar conda se necessário
if ! command -v conda &> /dev/null; then
    echo "Inicializando conda..."
    source "$HOME/miniconda/etc/profile.d/conda.sh"
fi

# Ativar ambiente saev
conda activate saev

# Forçar o PATH para usar o Python do ambiente saev
export PATH="/Users/rcaratti/miniconda/envs/saev/bin:$PATH"

echo "🔹 Ambiente SAEV ativado com sucesso!"
echo "🔹 Python: $(which python)"
echo "🔹 Versão do Python: $(python --version)"
echo "🔹 Streamlit: $(streamlit --version)"

echo ""
echo "Para executar o SAEV:"
echo "  python run_etl.py"
echo "  streamlit run src/dashboard/app.py"

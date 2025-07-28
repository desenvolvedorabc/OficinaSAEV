#!/bin/bash

# Script para ativar o ambiente conda SAEV
# Uso: source ativar_ambiente.sh

export PATH="$HOME/miniconda/bin:$PATH"
conda activate saev

echo "🔹 Ambiente SAEV ativado com sucesso!"
echo "🔹 Python: $(which python)"
echo "🔹 Versão do Python: $(python --version)"
echo "🔹 Streamlit: $(streamlit --version)"

echo ""
echo "Para executar o SAEV:"
echo "  python run_etl.py"
echo "  streamlit run src/dashboard/app.py"

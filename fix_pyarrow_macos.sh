#!/bin/bash

# =============================================================================
# Script de Recuperação - Instalação do PyArrow no macOS
# Para quando o setup principal falha com problemas de compilação
# =============================================================================

set -e

echo "🔧 Script de Recuperação - Problema com PyArrow"
echo "================================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se o ambiente virtual existe
if [ ! -d "venv_saev" ]; then
    print_error "Ambiente virtual não encontrado. Execute primeiro o setup_macos.sh"
    exit 1
fi

# Ativar ambiente virtual
print_message "Ativando ambiente virtual..."
source venv_saev/bin/activate

# Limpar cache do pip
print_message "Limpando cache do pip..."
pip cache purge

# Tentar instalar PyArrow usando conda-forge (alternativa mais estável)
print_message "Tentando instalar miniconda para usar conda-forge..."
if ! command -v conda &> /dev/null; then
    print_warning "Conda não encontrado. Instalando miniconda..."
    
    # Baixar e instalar miniconda
    curl -o miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
    bash miniconda.sh -b -p $HOME/miniconda
    rm miniconda.sh
    
    # Adicionar conda ao PATH
    export PATH="$HOME/miniconda/bin:$PATH"
    echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.zshrc
fi

# Usar conda para instalar PyArrow
print_message "Instalando PyArrow via conda-forge..."
conda install -c conda-forge pyarrow -y

# Instalar dependências restantes via pip
print_message "Instalando dependências restantes..."
pip install pandas numpy duckdb streamlit plotly altair scikit-learn scipy openpyxl xlsxwriter reportlab jupyter ipykernel pathlib2 python-dotenv streamlit-aggrid streamlit-option-menu

print_success "=============================================="
print_success "🎉 Recuperação concluída com sucesso!"
print_success "=============================================="
echo ""
print_warning "Alternativa usada: PyArrow instalado via conda-forge"
echo "Para futuros problemas similares, considere usar conda ao invés de pip para pacotes complexos."

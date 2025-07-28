#!/bin/bash

# =============================================================================
# Script de Recuperação - Problemas PyArrow/Arrow/Thrift no macOS
# Resolve: CMake, ArrowCompute, ThriftConfig e problemas de compilação
# =============================================================================

set -e

echo "🔧 Script de Recuperação - Problemas Arrow/PyArrow"
echo "🎯 Resolve: CMake, Thrift, ArrowCompute, compilação"
echo "=================================================="

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

# Verificar se estamos no diretório correto
if [ ! -f "requirements.txt" ]; then
    print_error "Execute este script no diretório raiz do projeto OficinaSAEV"
    exit 1
fi

# Parar qualquer processo pip em andamento
print_message "Parando processos pip em andamento..."
pkill -f "pip install" 2>/dev/null || true
sleep 2

# Limpar completamente instalações problemáticas
print_message "Limpeza completa de instalações problemáticas..."
rm -rf venv_saev 2>/dev/null || true
pip cache purge 2>/dev/null || true

# Remover instalações problemáticas do Homebrew
print_warning "Removendo instalações problemáticas do Arrow/Thrift via Homebrew..."
brew uninstall --ignore-dependencies apache-arrow 2>/dev/null || true
brew uninstall --ignore-dependencies arrow 2>/dev/null || true  
brew uninstall --ignore-dependencies thrift 2>/dev/null || true
brew uninstall --ignore-dependencies parquet-cpp 2>/dev/null || true

# Limpar cache do Homebrew
brew cleanup 2>/dev/null || true

print_success "Limpeza concluída"

# Verificar se miniconda está disponível
if ! command -v conda &> /dev/null; then
    print_message "Instalando Miniconda para evitar problemas de compilação..."
    
    # Detectar arquitetura
    if [[ $(uname -m) == "arm64" ]]; then
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
        print_message "Detectado: Mac Apple Silicon (ARM64)"
    else
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
        print_message "Detectado: Mac Intel (x86_64)"
    fi
    
    curl -o miniconda.sh "$MINICONDA_URL"
    bash miniconda.sh -b -p "$HOME/miniconda"
    rm miniconda.sh
    
    # Configurar PATH
    export PATH="$HOME/miniconda/bin:$PATH"
    echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.zshrc
    
    # Inicializar conda
    "$HOME/miniconda/bin/conda" init zsh 2>/dev/null || true
    
    print_success "Miniconda instalado"
else
    print_success "Conda já disponível"
    export PATH="$HOME/miniconda/bin:$PATH"
fi

# Remover ambiente conda anterior se existir
print_message "Removendo ambiente conda anterior..."
conda env remove -n saev -y 2>/dev/null || true

# Criar novo ambiente conda
print_message "Criando novo ambiente conda..."
conda create -n saev python=3.11 -y

# Ativar ambiente
print_message "Ativando ambiente conda..."
source "$HOME/miniconda/bin/activate" saev

# Instalar PyArrow e dependências críticas via conda-forge
# Isso evita completamente os problemas de compilação
print_message "Instalando PyArrow via conda-forge (sem compilação)..."
conda install -c conda-forge -y \
    pyarrow \
    pandas \
    numpy \
    duckdb \
    cmake

print_success "PyArrow instalado via conda-forge"

# Testar PyArrow
print_message "Testando PyArrow..."
if python -c "import pyarrow; print(f'✅ PyArrow {pyarrow.__version__} funcionando')" 2>/dev/null; then
    print_success "PyArrow teste passou!"
else
    print_error "PyArrow ainda com problemas"
    exit 1
fi

# Instalar dependências restantes via pip
print_message "Instalando dependências restantes via pip..."
pip install \
    streamlit \
    plotly \
    altair \
    scikit-learn \
    scipy \
    openpyxl \
    xlsxwriter \
    reportlab \
    jupyter \
    ipykernel \
    pathlib2 \
    python-dotenv \
    streamlit-aggrid \
    streamlit-option-menu

# Criar scripts de conveniência
print_message "Criando scripts de conveniência..."

cat > activate_saev.sh << 'EOF'
#!/bin/bash
echo "🔄 Ativando ambiente SAEV (conda)..."
export PATH="$HOME/miniconda/bin:$PATH"
source "$HOME/miniconda/bin/activate" saev
echo "✅ Ambiente ativo! Use 'conda deactivate' para sair"
bash  # Manter shell ativo
EOF

chmod +x activate_saev.sh

cat > test_environment.sh << 'EOF'
#!/bin/bash
echo "🧪 Testando ambiente SAEV..."
export PATH="$HOME/miniconda/bin:$PATH"
source "$HOME/miniconda/bin/activate" saev

echo "Testando dependências críticas:"
python -c "
import sys
print(f'Python: {sys.version}')

try:
    import pyarrow
    print(f'✅ PyArrow: {pyarrow.__version__}')
except ImportError as e:
    print(f'❌ PyArrow: {e}')

try:
    import pandas as pd
    print(f'✅ Pandas: {pd.__version__}')
except ImportError as e:
    print(f'❌ Pandas: {e}')

try:
    import duckdb
    print(f'✅ DuckDB: {duckdb.__version__}')
except ImportError as e:
    print(f'❌ DuckDB: {e}')

try:
    import streamlit as st
    print(f'✅ Streamlit: {st.__version__}')
except ImportError as e:
    print(f'❌ Streamlit: {e}')

print('\\n🎯 Se todos os testes passaram, o ambiente está pronto!')
"
EOF

chmod +x test_environment.sh

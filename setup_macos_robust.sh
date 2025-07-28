#!/bin/bash

# =============================================================================
# Script de Instalação SAEV - Versão Robusta para macOS
# Resolve problemas de PyArrow, Arrow, Thrift e CMake
# =============================================================================

set -e

echo "🔧 SAEV - Instalação Robusta para macOS"
echo "🎯 Foca em resolver problemas de PyArrow e dependências"
echo "=============================================="

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

# Limpar instalações problemáticas anteriores
print_message "Limpando instalações anteriores..."
rm -rf venv_saev 2>/dev/null || true
pip cache purge 2>/dev/null || true

# Verificar e instalar Homebrew
if ! command -v brew &> /dev/null; then
    print_warning "Instalando Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Configurar PATH para Homebrew
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
else
    print_success "Homebrew já instalado"
fi

# Atualizar Homebrew
print_message "Atualizando Homebrew..."
brew update

# Remover instalações problemáticas do Arrow/Thrift (se existirem)
print_message "Removendo versões problemáticas do Arrow/Thrift..."
brew uninstall --ignore-dependencies apache-arrow 2>/dev/null || true
brew uninstall --ignore-dependencies arrow 2>/dev/null || true
brew uninstall --ignore-dependencies thrift 2>/dev/null || true

# Instalar Python 3.11
if ! command -v python3.11 &> /dev/null; then
    print_message "Instalando Python 3.11..."
    brew install python@3.11
else
    print_success "Python 3.11 já instalado"
fi

# Verificar se miniconda está disponível, se não, instalar
if ! command -v conda &> /dev/null; then
    print_message "Instalando Miniconda para gerenciamento de dependências..."
    
    # Detectar arquitetura
    if [[ $(uname -m) == "arm64" ]]; then
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
    else
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
    fi
    
    curl -o miniconda.sh "$MINICONDA_URL"
    bash miniconda.sh -b -p "$HOME/miniconda"
    rm miniconda.sh
    
    # Adicionar conda ao PATH
    export PATH="$HOME/miniconda/bin:$PATH"
    echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.zshrc
    
    # Inicializar conda
    conda init zsh 2>/dev/null || true
else
    print_success "Conda já instalado"
    export PATH="$HOME/miniconda/bin:$PATH"
fi

# Criar ambiente conda específico para SAEV
print_message "Criando ambiente conda para SAEV..."
conda create -n saev python=3.11 -y

# Ativar ambiente conda
print_message "Ativando ambiente conda..."
source "$HOME/miniconda/bin/activate" saev

# Instalar PyArrow e dependências críticas via conda-forge (evita problemas de compilação)
print_message "Instalando PyArrow e dependências via conda-forge..."
conda install -c conda-forge -y \
    pyarrow \
    pandas \
    numpy \
    duckdb

# Instalar dependências restantes via pip
print_message "Instalando dependências adicionais via pip..."
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

# Criar estrutura de diretórios
print_message "Criando estrutura de diretórios..."
mkdir -p data/raw
mkdir -p data/test
mkdir -p db
mkdir -p src/data
mkdir -p src/dashboard
mkdir -p src/reports
mkdir -p src/analytics
mkdir -p reports
mkdir -p tests

# Criar scripts de ativação convenientes
print_message "Criando scripts de conveniência..."

# Script para ativar ambiente
cat > activate_saev_conda.sh << 'EOF'
#!/bin/bash
echo "🔄 Ativando ambiente SAEV..."
export PATH="$HOME/miniconda/bin:$PATH"
source "$HOME/miniconda/bin/activate" saev
echo "✅ Ambiente SAEV ativo!"
echo "💡 Para executar o ETL: python run_etl.py full"
echo "💡 Para Streamlit: streamlit run src/dashboard/main.py"
EOF

chmod +x activate_saev_conda.sh

# Script para executar ETL
cat > run_etl_conda.sh << 'EOF'
#!/bin/bash
echo "🔄 Executando ETL SAEV..."
export PATH="$HOME/miniconda/bin:$PATH"
source "$HOME/miniconda/bin/activate" saev
python run_etl.py full
EOF

chmod +x run_etl_conda.sh

# Criar READMEs informativos
cat > data/README.md << 'EOF'
# 📊 Diretório de Dados - SAEV

## ⚠️ DADOS SIGILOSOS - NÃO VERSIONADO

### 📁 Estrutura
- `raw/` - Arquivos CSV originais
- `test/` - Dados de teste anonimizados

### 🔒 Segurança
- Contém CPF e dados pessoais
- Protegido por .gitignore
- Use apenas dados anonimizados para desenvolvimento
EOF

cat > db/README.md << 'EOF'
# 💾 Banco de Dados - SAEV

## ⚠️ DADOS SIGILOSOS - NÃO VERSIONADO

### 🗄️ Bancos
- `avaliacao_prod.duckdb` - Produção
- `avaliacao_teste.duckdb` - Desenvolvimento

### 🔒 Segurança
- Contém dados processados sensíveis
- Faça backup regular
- Protegido por .gitignore
EOF

print_success "=============================================="
print_success "🎉 Instalação robusta concluída!"
print_success "=============================================="
echo ""
print_message "📋 Próximos passos:"
echo "1. Ativar ambiente: ./activate_saev_conda.sh"
echo "2. OU manualmente: source ~/miniconda/bin/activate saev"
echo "3. Colocar arquivos CSV em data/raw/"
echo "4. Executar ETL: ./run_etl_conda.sh"
echo "5. OU manualmente: python run_etl.py full"
echo ""
print_warning "⚠️ IMPORTANTE: Esta instalação usa Conda em vez de venv"
print_warning "   Use 'conda activate saev' em vez de 'source venv_saev/bin/activate'"
echo ""
print_success "✅ PyArrow instalado via conda-forge (sem problemas de compilação)"

# Teste final
print_message "Testando instalação..."
if python -c "import pyarrow, pandas, duckdb, streamlit; print('✅ Todas as dependências funcionando!')" 2>/dev/null; then
    print_success "✅ Teste passou - instalação bem-sucedida!"
else
    print_warning "⚠️ Teste falhou - pode haver problemas residuais"
fi

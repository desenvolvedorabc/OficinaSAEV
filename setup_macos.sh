#!/bin/bash

# =============================================================================
# Script de Configuração do Ambiente Python - macOS
# OficinaSAEV - Sistema de Análise de Avaliações Educacionais
# =============================================================================

set -e  # Para o script se houver erro

echo "🍎 Iniciando configuração do ambiente Python para macOS..."
echo "=================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
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

# Verificar se o Homebrew está instalado
if ! command -v brew &> /dev/null; then
    print_warning "Homebrew não encontrado. Instalando Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Adicionar Homebrew ao PATH
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
else
    print_success "Homebrew já está instalado"
fi

# Atualizar Homebrew
print_message "Atualizando Homebrew..."
brew update

# Instalar dependências necessárias para compilação
print_message "Instalando dependências de compilação..."
brew install cmake
brew install arrow
brew install boost
brew install llvm

# Instalar Python 3.11 se não estiver instalado
if ! command -v python3.11 &> /dev/null; then
    print_message "Instalando Python 3.11..."
    brew install python@3.11
else
    print_success "Python 3.11 já está instalado"
fi

# Instalar Git se não estiver instalado
if ! command -v git &> /dev/null; then
    print_message "Instalando Git..."
    brew install git
else
    print_success "Git já está instalado"
fi

# Verificar se estamos no diretório correto
if [ ! -f "requirements.txt" ]; then
    print_error "Arquivo requirements.txt não encontrado. Execute este script no diretório do projeto."
    exit 1
fi

# Criar ambiente virtual
print_message "Criando ambiente virtual Python..."
python3.11 -m venv venv_saev

# Ativar ambiente virtual
print_message "Ativando ambiente virtual..."
source venv_saev/bin/activate

# Atualizar pip
print_message "Atualizando pip..."
pip install --upgrade pip setuptools wheel

# Configurar variáveis de ambiente para compilação do PyArrow
export ARROW_HOME=$(brew --prefix arrow)
export PARQUET_HOME=$(brew --prefix arrow)
export CMAKE_PREFIX_PATH=$CMAKE_PREFIX_PATH:$(brew --prefix arrow)

# Instalar PyArrow separadamente com configurações específicas
print_message "Instalando PyArrow (pode demorar alguns minutos)..."
pip install --no-cache-dir --verbose pyarrow

# Instalar dependências restantes
print_message "Instalando dependências do projeto..."
pip install -r requirements.txt

# Criar estrutura de diretórios necessários (dados sigilosos não versionados)
print_message "Criando estrutura de diretórios para dados sigilosos..."
mkdir -p data/raw
mkdir -p data/test
mkdir -p db
mkdir -p src/data
mkdir -p src/dashboard
mkdir -p src/reports
mkdir -p src/analytics
mkdir -p reports
mkdir -p tests

# Criar READMEs informativos nos diretórios de dados
print_message "Criando arquivos informativos..."
cat > data/README.md << 'EOF'
# 📊 Diretório de Dados

## ⚠️ IMPORTANTE - DADOS SIGILOSOS

Este diretório contém dados sigilosos e NÃO é versionado no Git.

## 📁 Estrutura

- **`raw/`** - Dados CSV originais do SAEV
- **`test/`** - Dados de teste e amostras (anonimizadas)

## 📋 Instruções

1. Coloque os arquivos CSV do SAEV em `raw/`
2. Use dados anonimizados em `test/` para desenvolvimento
3. **NUNCA** commite dados com informações pessoais

## 🔒 Segurança

- CPF, nomes e dados pessoais devem ser protegidos
- Use dados sintéticos ou anonimizados para testes
- Esta pasta está no .gitignore por segurança
EOF

cat > db/README.md << 'EOF'
# 💾 Diretório de Banco de Dados

## ⚠️ IMPORTANTE - DADOS SIGILOSOS

Este diretório contém bancos de dados sigilosos e NÃO é versionado no Git.

## 🗄️ Bancos Padrão

- **`avaliacao_teste.duckdb`** - Banco para desenvolvimento
- **`avaliacao_prod.duckdb`** - Banco de produção

## 🔒 Segurança

- Bancos contêm dados sensíveis
- Faça backup regular dos bancos
- Configure adequadamente as permissões
- Esta pasta está no .gitignore por segurança
EOF

# Instalar extensões do Jupyter (se necessário)
print_message "Configurando Jupyter..."
python -m ipykernel install --user --name=venv_saev --display-name="Python (SAEV)"

print_success "=============================================="
print_success "🎉 Configuração concluída com sucesso!"
print_success "=============================================="
echo ""
echo "Para ativar o ambiente virtual, execute:"
echo "  source venv_saev/bin/activate"
echo ""
echo "Para iniciar o Jupyter Notebook:"
echo "  jupyter notebook"
echo ""
echo "Para executar o dashboard Streamlit (quando disponível):"
echo "  streamlit run src/dashboard/main.py"
echo ""
print_warning "Lembre-se de sempre ativar o ambiente virtual antes de trabalhar no projeto!"

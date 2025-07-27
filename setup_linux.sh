#!/bin/bash

# =============================================================================
# Script de Configuração do Ambiente Python - Linux (Ubuntu/Debian)
# OficinaSAEV - Sistema de Análise de Avaliações Educacionais
# =============================================================================

set -e  # Para o script se houver erro

echo "🐧 Iniciando configuração do ambiente Python para Linux (Ubuntu)..."
echo "======================================================="

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

# Verificar se é Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    print_error "Este script é específico para sistemas baseados em Debian/Ubuntu"
    exit 1
fi

# Atualizar repositórios
print_message "Atualizando repositórios do sistema..."
sudo apt update

# Instalar dependências do sistema
print_message "Instalando dependências do sistema..."
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    git \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    tk-dev \
    libpng-dev \
    libfreetype6-dev

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

# Instalar dependências
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

# Instalar extensões do Jupyter
print_message "Configurando Jupyter..."
python -m ipykernel install --user --name=venv_saev --display-name="Python (SAEV)"

# Configurar permissões
print_message "Configurando permissões..."
chmod +x setup_linux.sh

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
echo ""
echo "DICA: Adicione o seguinte alias ao seu ~/.bashrc ou ~/.zshrc:"
echo "  alias saev='cd $(pwd) && source venv_saev/bin/activate'"

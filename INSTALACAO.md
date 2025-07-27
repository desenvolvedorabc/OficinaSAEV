# 🚀 Guia de Instalação - OficinaSAEV

Este guia irá orientá-lo através do processo de configuração do ambiente de desenvolvimento para o projeto OficinaSAEV em diferentes sistemas operacionais.

## 📋 Pré-requisitos

### Para todos os sistemas:
- **Python 3.11+** (recomendado: Python 3.11)
- **Git** (para controle de versão)
- **Conexão com a internet** (para download das dependências)

## 🍎 Instalação no macOS

### Método Automático (Recomendado)
```bash
# 1. Clone ou baixe o projeto
cd /caminho/para/o/projeto

# 2. Execute o script de instalação
./setup_macos.sh
```

### Método Manual
```bash
# 1. Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Instalar Python 3.11
brew install python@3.11

# 3. Criar ambiente virtual
python3.11 -m venv venv_saev

# 4. Ativar ambiente virtual
source venv_saev/bin/activate

# 5. Instalar dependências
pip install -r requirements.txt
```

## 🐧 Instalação no Linux (Ubuntu/Debian)

### Método Automático (Recomendado)
```bash
# 1. Clone ou baixe o projeto
cd /caminho/para/o/projeto

# 2. Tornar o script executável e executar
chmod +x setup_linux.sh
./setup_linux.sh
```

### Método Manual
```bash
# 1. Atualizar repositórios
sudo apt update

# 2. Instalar dependências do sistema
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip git

# 3. Criar ambiente virtual
python3.11 -m venv venv_saev

# 4. Ativar ambiente virtual
source venv_saev/bin/activate

# 5. Instalar dependências
pip install -r requirements.txt
```

## 🪟 Instalação no Windows

### Pré-requisitos Windows
1. **Instalar Python 3.11+**: Baixe de [python.org](https://python.org)
   - ⚠️ **IMPORTANTE**: Marque "Add Python to PATH" durante a instalação
2. **Instalar Git** (opcional): Baixe de [git-scm.com](https://git-scm.com/)

### Método Automático (Recomendado)
```cmd
# 1. Abra o Prompt de Comando ou PowerShell
cd C:\caminho\para\o\projeto

# 2. Execute o script de instalação
setup_windows.bat
```

### Método Manual
```cmd
# 1. Criar ambiente virtual
python -m venv venv_saev

# 2. Ativar ambiente virtual
venv_saev\Scripts\activate.bat

# 3. Atualizar pip
python -m pip install --upgrade pip

# 4. Instalar dependências
pip install -r requirements.txt
```

## 🔧 Verificação da Instalação

Após a instalação, verifique se tudo está funcionando:

```bash
# Ativar ambiente virtual
# macOS/Linux:
source venv_saev/bin/activate

# Windows:
venv_saev\Scripts\activate.bat

# Verificar instalação
python -c "import pandas, streamlit, duckdb, plotly; print('✅ Todas as dependências instaladas com sucesso!')"
```

## 🚀 Executando o Projeto

### Dashboard Streamlit
```bash
# Ativar ambiente virtual primeiro
source venv_saev/bin/activate  # macOS/Linux
# OU
venv_saev\Scripts\activate.bat  # Windows

# Executar dashboard (quando disponível)
streamlit run src/dashboard/main.py
```

### Jupyter Notebook
```bash
# Ativar ambiente virtual primeiro
source venv_saev/bin/activate  # macOS/Linux
# OU
venv_saev\Scripts\activate.bat  # Windows

# Iniciar Jupyter
jupyter notebook
```

## 📁 Estrutura de Diretórios

### 🔒 **Importante - Dados Sigilosos**

Por questões de **segurança e privacidade**, os diretórios `data/` e `db/` **NÃO são versionados** no Git, pois contêm informações sigilosas (CPF, nomes, dados educacionais).

### Estrutura após instalação:

```
OficinaSAEV/
├── .gitignore              # Arquivos ignorados pelo Git
├── README.md               # Documentação principal
├── INSTALACAO.md           # Este guia de instalação
├── requirements.txt        # Dependências Python
├── setup_macos.sh         # Script de instalação macOS
├── setup_linux.sh         # Script de instalação Linux
├── setup_windows.bat      # Script de instalação Windows
├── data/                  # 🚫 NÃO VERSIONADO - Criado pelos scripts
│   ├── README.md          # Instruções de segurança
│   ├── raw/               # Dados CSV originais do SAEV
│   └── test/              # Dados de teste (anonimizados)
├── db/                    # 🚫 NÃO VERSIONADO - Criado pelos scripts
│   ├── README.md          # Instruções de segurança
│   ├── avaliacao_teste.duckdb    # Banco de desenvolvimento
│   └── avaliacao_prod.duckdb     # Banco de produção
├── src/
│   ├── config.py         # Configurações do projeto
│   ├── data/             # Scripts ETL
│   ├── dashboard/        # Dashboard Streamlit
│   ├── reports/          # Gerador de relatórios
│   └── analytics/        # Análises avançadas
├── reports/              # Relatórios gerados
├── tests/                # Testes unitários
└── venv_saev/            # Ambiente virtual (criado pelos scripts)
```

### 🔐 **Política de Segurança**

1. **Dados sensíveis**: CPF, nomes e informações pessoais **NUNCA** devem ser commitados
2. **Desenvolvimento**: Use dados anonimizados ou sintéticos em `data/test/`
3. **Produção**: Dados reais ficam apenas em `data/raw/` (local)
4. **Bancos**: Todos os arquivos `.duckdb` são ignorados pelo Git
5. **Backup**: Faça backup regular dos dados e bancos (fora do Git)

## 🆘 Solução de Problemas

### Erro: "Python não encontrado"
- **Windows**: Reinstale Python marcando "Add Python to PATH"
- **macOS**: Use `python3.11` em vez de `python`
- **Linux**: Instale com `sudo apt install python3.11`

### Erro de permissão no Linux/macOS
```bash
chmod +x setup_macos.sh    # ou setup_linux.sh
```

### Erro de dependências no Windows
```cmd
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Ambiente virtual não ativa
```bash
# Certifique-se de estar no diretório correto
cd /caminho/para/OficinaSAEV

# Ative novamente
source venv_saev/bin/activate  # macOS/Linux
venv_saev\Scripts\activate.bat  # Windows
```

## 💡 Dicas Úteis

### Alias para facilitar o uso (macOS/Linux)
Adicione ao seu `~/.bashrc` ou `~/.zshrc`:
```bash
alias saev='cd /caminho/para/OficinaSAEV && source venv_saev/bin/activate'
```

### Scripts de conveniência (Windows)
Após a instalação automática, você terá:
- `activate_saev.bat` - Ativa o ambiente
- `start_jupyter.bat` - Inicia Jupyter Notebook
- `start_dashboard.bat` - Inicia dashboard Streamlit

## 📞 Suporte

Se encontrar problemas durante a instalação, verifique:
1. Se você tem Python 3.11+ instalado
2. Se o Python está no PATH do sistema
3. Se você tem conexão com a internet
4. Se tem permissões para criar diretórios e instalar pacotes

Para mais ajuda, consulte a documentação oficial das ferramentas ou abra uma issue no repositório do projeto.

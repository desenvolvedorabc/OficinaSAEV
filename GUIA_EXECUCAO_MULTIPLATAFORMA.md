# 🌐 SAEV Streamlit - Guia de Execução Multiplataforma

## 📋 **Visão Geral**

Este guia explica como executar os aplicativos SAEV Streamlit em **qualquer sistema operacional** usando caminhos relativos e scripts otimizados para portabilidade.

## 🚀 **Scripts Disponíveis**

### **🌍 Universal (Recomendado)**
```bash
./start_saev_universal.sh    # Linux, macOS, WSL, Git Bash
# ✨ NOVO: Abre navegador automaticamente!
```

### **🐧 Linux / 🍎 macOS**
```bash
./start_streamlit.sh         # SAEV 1 - Dashboard Geral
./start_streamlit2.sh        # SAEV 2 - Dashboard com Filtros
```

### **🪟 Windows**
```batch
start_saev_windows.bat       # Interface amigável para Windows
# ✨ NOVO: Opção de abertura automática do navegador!
```

## 📁 **Estrutura do Projeto (Relativa)**

```
OficinaSAEV/                 ← Diretório raiz (execute scripts aqui)
├── db/
│   └── avaliacao_prod.duckdb    ← Banco de dados (caminho relativo)
├── saev_streamlit.py            ← App 1: Dashboard geral
├── saev_streamlit2.py           ← App 2: Dashboard com filtros
├── start_saev_universal.sh      ← Script universal
├── start_saev_windows.bat       ← Script para Windows
├── start_streamlit.sh           ← Script específico App 1
└── start_streamlit2.sh          ← Script específico App 2
```

## 🔧 **Instruções por Sistema**

### **🐧 Linux**

#### **Preparação:**
```bash
# Navegue para o diretório do projeto
cd /caminho/para/OficinaSAEV

# Torne os scripts executáveis
chmod +x *.sh

# Verifique as dependências
python3 -c "import streamlit, duckdb, pandas, plotly"
```

#### **Execução:**
```bash
# Opção 1: Script universal (recomendado) - COM NAVEGADOR AUTOMÁTICO
./start_saev_universal.sh
# ✨ Escolha o app → Escolha se quer abrir navegador → Automático!

# Opção 2: Scripts específicos
./start_streamlit.sh         # Dashboard geral (porta 8501)
./start_streamlit2.sh        # Dashboard com filtros (porta 8502)
```

### **🍎 macOS**

#### **Preparação:**
```bash
# Navegue para o diretório do projeto
cd /Users/seu_usuario/caminho/para/OficinaSAEV

# Torne os scripts executáveis
chmod +x *.sh
```

#### **Execução:**
```bash
# Mesmos comandos do Linux
./start_saev_universal.sh    # Recomendado
```

### **🪟 Windows**

#### **Via PowerShell/CMD:**
```batch
REM Navegue para o diretório do projeto
cd C:\caminho\para\OficinaSAEV

REM Execute o script (NOVO: com opção de navegador automático)
start_saev_windows.bat
```

#### **Via WSL (Windows Subsystem for Linux):**
```bash
# Dentro do WSL
cd /mnt/c/caminho/para/OficinaSAEV
chmod +x *.sh
./start_saev_universal.sh
```

#### **Via Git Bash:**
```bash
# No Git Bash
cd /c/caminho/para/OficinaSAEV
./start_saev_universal.sh
```

## 🎯 **Aplicativos Disponíveis**

### **📊 SAEV 1 - Dashboard Geral**
- **Arquivo:** `saev_streamlit.py`
- **Porta:** 8501
- **Características:**
  - ✅ Visão executiva completa
  - ✅ 7 métricas principais
  - ✅ 6 visualizações fixas
  - ✅ Performance otimizada

### **🔍 SAEV 2 - Dashboard com Filtros**
- **Arquivo:** `saev_streamlit2.py`
- **Porta:** 8502
- **Características:**
  - ✅ 4 filtros interativos
  - ✅ 8 métricas dinâmicas
  - ✅ 6 visualizações adaptáveis
  - ✅ Análise exploratória

## 🌐 **Nova Funcionalidade: Abertura Automática do Navegador**

### **✨ O que há de novo:**
- **🚀 Abertura automática** do navegador na URL correta
- **🎯 Menu interativo** para escolher se quer abrir o navegador
- **🌍 Compatibilidade total** com Linux, macOS e Windows
- **⏱️ Delay inteligente** aguarda carregamento do Streamlit

### **🎮 Como usar:**
```bash
./start_saev_universal.sh

# Menu aparece:
# 1) SAEV 1 - Dashboard Geral 
# 2) SAEV 2 - Dashboard com Filtros
# 3) Ambos

# Digite: 1

# 🌐 Abrir navegador automaticamente?
# y) Sim - Abrir navegador após inicialização  
# n) Não - Apenas iniciar o servidor

# Digite: y (padrão)

# ✅ Navegador abre automaticamente em 5 segundos!
```

### **🔧 Detecção por Sistema:**
- **🐧 Linux:** `xdg-open`, `gnome-open`, `firefox`, `chrome`
- **🍎 macOS:** `open` (comando nativo)
- **🪟 Windows:** `start` com delay otimizado

📋 **Documentação completa:** `NAVEGADOR_AUTOMATICO.md`

## 🌐 **URLs de Acesso**

### **Local (todas as máquinas):**
- **SAEV 1:** http://localhost:8501
- **SAEV 2:** http://localhost:8502

### **Rede local (IP detectado automaticamente):**
- **SAEV 1:** http://SEU_IP:8501
- **SAEV 2:** http://SEU_IP:8502

## ⚙️ **Detecção Automática de Sistema**

### **🔍 Detecção de Python:**
Os scripts detectam automaticamente:
- `python3` (preferência)
- `python` (se for versão 3.x)
- Valida versão antes de usar

### **🌐 Detecção de IP:**
```bash
# Linux moderno
ip route get 1 | awk '{print $7; exit}'

# Linux com hostname
hostname -I | awk '{print $1}'

# macOS
ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}'

# Windows
ipconfig | findstr /c:"IPv4"
```

### **📦 Verificação de Dependências:**
Automaticamente verifica:
- streamlit
- duckdb  
- pandas
- plotly

## 🐛 **Solução de Problemas**

### **❌ "Arquivo não encontrado"**
```bash
# Certifique-se de estar no diretório correto
pwd                          # Deve mostrar .../OficinaSAEV
ls saev_streamlit*.py        # Deve listar os arquivos Python
```

### **❌ "Banco de dados não encontrado"**
```bash
# Verifique o banco
ls db/avaliacao_prod.duckdb

# Se não existir, execute o ETL
python run_etl.py full
```

### **❌ "Python não encontrado"**
```bash
# Linux/macOS
sudo apt install python3          # Ubuntu/Debian
brew install python3              # macOS com Homebrew

# Windows
# Baixe de python.org e adicione ao PATH
```

### **❌ "Dependência não instalada"**
```bash
# Instalar dependências
pip install streamlit duckdb pandas plotly

# Ou usar requirements.txt (se disponível)
pip install -r requirements.txt
```

### **❌ "Porta em uso"**
```bash
# Verificar processos usando as portas
lsof -i :8501    # Linux/macOS
lsof -i :8502

# Parar processos Streamlit
pkill -f streamlit

# Windows
netstat -ano | findstr :8501
taskkill /PID [PID_NUMBER] /F
```

## 🔧 **Personalização**

### **🌐 Mudar Porta:**
Edite os scripts e altere:
```bash
PORT=8503    # Nova porta
```

### **🔒 Configurações de Segurança:**
```bash
# Para acesso apenas local
--server.address=localhost

# Para acesso na rede
--server.address=0.0.0.0
```

### **📊 Configurações do Streamlit:**
```bash
# Desabilitar coleta de dados
--browser.gatherUsageStats=false

# Modo headless (sem abrir browser)
--server.headless=true

# CORS para desenvolvimento
--server.enableCORS=false
```

## 🎯 **Melhores Práticas**

### **📁 Organização:**
1. **Mantenha a estrutura de diretórios**
2. **Execute sempre da pasta raiz** (OficinaSAEV/)
3. **Use caminhos relativos** em personalizações

### **🔄 Versionamento:**
1. **Scripts universais** funcionam em qualquer ambiente
2. **Não hardcode caminhos absolutos**
3. **Teste em diferentes sistemas** antes de distribuir

### **🚀 Performance:**
1. **Use o script universal** para melhor compatibilidade
2. **Feche aplicativos não usados** para liberar portas
3. **Execute ETL completo** após mudanças nos dados

## 📞 **Suporte**

### **🆘 Em caso de problemas:**

1. **Verifique pré-requisitos:**
   - Python 3.7+ instalado
   - Dependências instaladas
   - Banco de dados disponível

2. **Execute diagnóstico:**
   ```bash
   python3 --version
   python3 -c "import streamlit; print(streamlit.__version__)"
   ls -la db/avaliacao_prod.duckdb
   ```

3. **Logs de debug:**
   ```bash
   # Executar com logs detalhados
   streamlit run saev_streamlit.py --logger.level=debug
   ```

---

## 🎊 **Resumo de Comandos Rápidos**

### **🚀 Início Rápido (qualquer sistema):**
```bash
cd /caminho/para/OficinaSAEV    # Navegar para projeto
chmod +x *.sh                   # Linux/macOS: tornar executável
./start_saev_universal.sh       # Executar script universal
```

### **🪟 Windows (início rápido):**
```batch
cd C:\caminho\para\OficinaSAEV
start_saev_windows.bat
```

### **🛑 Parar aplicativos:**
```bash
# Linux/macOS
pkill -f streamlit

# Windows
taskkill /IM python.exe /F
```

---

*🌐 Scripts universais para máxima portabilidade*  
*🔧 Caminhos relativos para flexibilidade total*  
*🚀 Execução simples em qualquer ambiente*

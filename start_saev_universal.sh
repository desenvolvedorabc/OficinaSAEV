#!/bin/bash

# 🌐 SAEV Streamlit - Script Universal de Inicialização
# Compatível com Linux, macOS e Windows (via WSL/Git Bash)
# Versão: 1.0

# Cores para output (compatível com múltiplos terminais)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Função para exibir mensagens coloridas
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Banner
echo "================================================="
echo "🚀 SAEV - Sistema de Avaliação Educacional"
echo "📊 Script Universal de Inicialização"
echo "🌐 Compatível: Linux | macOS | Windows"
echo "================================================="

# Detectar sistema operacional
OS="unknown"
case "$(uname -s)" in
    Linux*)     OS="Linux";;
    Darwin*)    OS="macOS";;
    CYGWIN*)    OS="Windows";;
    MINGW*)     OS="Windows";;
    MSYS*)      OS="Windows";;
esac

print_info "Sistema detectado: $OS"

# Verificar se estamos no diretório correto
if [ ! -f "saev_streamlit.py" ] && [ ! -f "saev_streamlit2.py" ]; then
    print_error "Execute este script na pasta raiz do projeto OficinaSAEV"
    print_error "Arquivos esperados: saev_streamlit.py ou saev_streamlit2.py"
    exit 1
fi

print_status "Diretório correto verificado"

# 🔧 CORREÇÃO: Ativar ambiente conda antes de verificar dependências
print_info "Ativando ambiente conda SAEV..."

# Detectar e configurar ambiente Python
print_info "Detectando ambiente Python..."

# Verificar se miniconda está instalado e tem ambiente saev
if [ -d "$HOME/miniconda" ] && [ -d "$HOME/miniconda/envs/saev" ]; then
    export PATH="$HOME/miniconda/bin:$PATH"
    
    # Inicializar conda se necessário
    if ! command -v conda &> /dev/null; then
        source "$HOME/miniconda/etc/profile.d/conda.sh"
    fi
    
    source "$HOME/miniconda/bin/activate" saev
    
    # Forçar o PATH para usar o Python do ambiente saev
    export PATH="$HOME/miniconda/envs/saev/bin:$PATH"
    
    PYTHON_CMD="python"
    print_status "Ambiente conda 'saev' ativado"
    
# Verificar se existe ambiente virtual venv_saev
elif [ -d "venv_saev" ] && [ -f "venv_saev/bin/activate" ]; then
    print_info "Ativando ambiente virtual venv_saev..."
    source venv_saev/bin/activate
    PYTHON_CMD="python"
    print_status "Ambiente virtual 'venv_saev' ativado"
    
# Fallback para Python do sistema
else
    print_warning "Nenhum ambiente conda ou venv encontrado, usando Python do sistema..."
    
    # Detectar Python disponível
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        # Verificar se é Python 3
        PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1)
        if [ "$PYTHON_VERSION" = "3" ]; then
            PYTHON_CMD="python"
        fi
    fi
    
    if [ -z "$PYTHON_CMD" ]; then
        print_error "Python 3 não encontrado!"
        print_warning "Instale Python 3 ou configure um ambiente virtual"
        print_info "Para criar um ambiente virtual, execute:"
        print_info "  python3 -m venv venv_saev"
        print_info "  source venv_saev/bin/activate"
        print_info "  pip install -r requirements.txt"
        exit 1
    else
        print_status "Usando Python do sistema: $PYTHON_CMD"
    fi
fi

# Verificar se o banco de dados existe
if [ ! -f "db/avaliacao_prod.duckdb" ]; then
    print_error "Banco de dados não encontrado em: db/avaliacao_prod.duckdb"
    print_warning "Execute o ETL primeiro: $PYTHON_CMD run_etl.py full"
    exit 1
fi

print_status "Banco de dados encontrado"

# Verificar versão do Python
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
print_status "Python encontrado: $PYTHON_VERSION"

# Verificar dependências
print_info "Verificando dependências..."

dependencies=("streamlit" "duckdb" "pandas" "plotly")
for dep in "${dependencies[@]}"; do
    if ! $PYTHON_CMD -c "import $dep" &> /dev/null; then
        print_error "$dep não está instalado!"
        print_warning "Execute: pip install $dep"
        exit 1
    else
        version=$($PYTHON_CMD -c "import $dep; print($dep.__version__)" 2>/dev/null || echo "versão não detectada")
        print_status "$dep: $version"
    fi
done

# Obter IP local (compatível com múltiplos sistemas)
get_local_ip() {
    local ip="localhost"
    
    # Tentar diferentes métodos baseados no sistema
    case "$OS" in
        "Linux")
            if command -v ip &> /dev/null; then
                ip=$(ip route get 1 2>/dev/null | awk '{print $7; exit}')
            elif command -v hostname &> /dev/null; then
                ip=$(hostname -I 2>/dev/null | awk '{print $1}')
            elif command -v ifconfig &> /dev/null; then
                ip=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
            fi
            ;;
        "macOS")
            if command -v ifconfig &> /dev/null; then
                ip=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
            fi
            ;;
        "Windows")
            if command -v ipconfig &> /dev/null; then
                ip=$(ipconfig | grep "IPv4" | head -1 | awk '{print $NF}' | tr -d '\r')
            fi
            ;;
    esac
    
    # Validar IP
    if [ -z "$ip" ] || [ "$ip" = " " ] || [[ ! "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        ip="localhost"
    fi
    
    echo "$ip"
}

# Função para abrir navegador (multiplataforma)
open_browser() {
    local url="$1"
    local delay="${2:-3}"  # Delay padrão de 3 segundos
    
    print_info "Aguardando $delay segundos para abrir o navegador..."
    sleep $delay
    
    case "$OS" in
        "Linux")
            if command -v xdg-open &> /dev/null; then
                xdg-open "$url" &> /dev/null &
                print_status "Navegador aberto via xdg-open"
            elif command -v gnome-open &> /dev/null; then
                gnome-open "$url" &> /dev/null &
                print_status "Navegador aberto via gnome-open"
            elif command -v firefox &> /dev/null; then
                firefox "$url" &> /dev/null &
                print_status "Firefox aberto diretamente"
            elif command -v google-chrome &> /dev/null; then
                google-chrome "$url" &> /dev/null &
                print_status "Chrome aberto diretamente"
            else
                print_warning "Não foi possível abrir o navegador automaticamente"
                print_info "Abra manualmente: $url"
            fi
            ;;
        "macOS")
            if command -v open &> /dev/null; then
                open "$url"
                print_status "Navegador aberto via open (macOS)"
            else
                print_warning "Comando 'open' não encontrado"
                print_info "Abra manualmente: $url"
            fi
            ;;
        "Windows")
            if command -v start &> /dev/null; then
                start "$url"
                print_status "Navegador aberto via start (Windows)"
            elif command -v cmd &> /dev/null; then
                cmd /c start "$url" &> /dev/null
                print_status "Navegador aberto via cmd"
            else
                print_warning "Não foi possível abrir o navegador automaticamente"
                print_info "Abra manualmente: $url"
            fi
            ;;
        *)
            print_warning "Sistema não reconhecido para abertura de navegador"
            print_info "Abra manualmente: $url"
            ;;
    esac
}

LOCAL_IP=$(get_local_ip)

# Menu de seleção
echo ""
print_info "Escolha o aplicativo para executar:"
echo "1) SAEV Streamlit 1 - Dashboard Geral (porta 8501)"
echo "2) SAEV Streamlit 2 - Dashboard com Filtros (porta 8502)"
echo "3) SAEV Rankings - Rankings e Classificações (porta 8503)"
echo "4) Todos os aplicativos (portas 8501, 8502 e 8503)"
echo ""

read -p "Digite sua escolha (1, 2, 3 ou 4): " choice

# Pergunta sobre abertura automática do navegador
echo ""
print_info "🌐 Abrir navegador automaticamente?"
echo "y) Sim - Abrir navegador após inicialização"
echo "n) Não - Apenas iniciar o servidor"
echo ""

read -p "Abrir navegador? (y/n) [padrão: y]: " open_browser_choice
open_browser_choice=${open_browser_choice:-y}  # Padrão é 'y' se vazio

case $choice in
    1)
        APP_FILE="saev_streamlit.py"
        PORT=8501
        APP_NAME="SAEV Streamlit 1 - Dashboard Geral"
        ;;
    2)
        APP_FILE="saev_streamlit2.py"
        PORT=8502
        APP_NAME="SAEV Streamlit 2 - Dashboard com Filtros"
        ;;
    3)
        APP_FILE="saev_rankings.py"
        PORT=8503
        APP_NAME="SAEV Rankings - Rankings e Classificações"
        ;;
    4)
        print_info "Iniciando todos os aplicativos..."
        if [ -f "saev_streamlit.py" ]; then
            print_info "Iniciando SAEV Dashboard Geral em background (porta 8501)..."
            nohup $PYTHON_CMD -m streamlit run saev_streamlit.py --server.port=8501 --server.headless=true > streamlit1.log 2>&1 &
            STREAMLIT1_PID=$!
            sleep 2
        fi
        if [ -f "saev_streamlit2.py" ]; then
            print_info "Iniciando SAEV Dashboard com Filtros em background (porta 8502)..."
            nohup $PYTHON_CMD -m streamlit run saev_streamlit2.py --server.port=8502 --server.headless=true > streamlit2.log 2>&1 &
            STREAMLIT2_PID=$!
            sleep 2
        fi
        if [ -f "saev_rankings.py" ]; then
            print_info "Iniciando SAEV Rankings em background (porta 8503)..."
            nohup $PYTHON_CMD -m streamlit run saev_rankings.py --server.port=8503 --server.headless=true > streamlit3.log 2>&1 &
            STREAMLIT3_PID=$!
            sleep 2
        fi
        
        echo ""
        print_status "Todos os aplicativos iniciados!"
        print_info "URLs disponíveis:"
        print_info "  SAEV Dashboard Geral: http://localhost:8501"
        print_info "  SAEV Dashboard Filtros: http://localhost:8502"
        print_info "  SAEV Rankings: http://localhost:8503"
        if [ "$LOCAL_IP" != "localhost" ]; then
            print_info "  SAEV Dashboard Geral (rede): http://$LOCAL_IP:8501"
            print_info "  SAEV Dashboard Filtros (rede): http://$LOCAL_IP:8502"
            print_info "  SAEV Rankings (rede): http://$LOCAL_IP:8503"
        fi
        print_info ""
        print_info "Para parar os aplicativos, execute: pkill -f streamlit"
        print_info "Logs: streamlit1.log, streamlit2.log e streamlit3.log"
        echo ""
        
        # Abrir navegadores se solicitado
        if [[ "$open_browser_choice" =~ ^[Yy]$ ]]; then
            print_info "🌐 Abrindo navegadores automaticamente..."
            (open_browser "http://localhost:8501" 3) &
            (open_browser "http://localhost:8502" 6) &
            (open_browser "http://localhost:8503" 9) &
            print_status "Navegadores sendo abertos em background"
        else
            print_info "🌐 Navegadores não serão abertos automaticamente"
            print_info "Acesse manualmente:"
            print_info "  SAEV Dashboard Geral: http://localhost:8501"
            print_info "  SAEV Dashboard Filtros: http://localhost:8502"
            print_info "  SAEV Rankings: http://localhost:8503"
        fi
        
        print_warning "Para parar todos os serviços: pkill -f streamlit"
        exit 0
        ;;
    *)
        print_error "Escolha inválida!"
        exit 1
        ;;
esac

# Verificar se o arquivo existe
if [ ! -f "$APP_FILE" ]; then
    print_error "Arquivo não encontrado: $APP_FILE"
    exit 1
fi

# Configurações do Streamlit
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Exibir informações do servidor
echo ""
print_status "Iniciando $APP_NAME"
print_info "Arquivo: $APP_FILE"
print_info "Porta: $PORT"
print_info "Sistema: $OS"
echo ""
print_info "URLs de acesso:"
print_info "  Local: http://localhost:$PORT"
if [ "$LOCAL_IP" != "localhost" ]; then
    print_info "  Rede:  http://$LOCAL_IP:$PORT"
fi
echo ""
print_warning "Pressione Ctrl+C para parar o servidor"
echo "================================================="

# Abrir navegador em background se solicitado
if [[ "$open_browser_choice" =~ ^[Yy]$ ]]; then
    print_info "🌐 Navegador será aberto automaticamente em 5 segundos..."
    (open_browser "http://localhost:$PORT" 5) &
else
    print_info "🌐 Acesse manualmente: http://localhost:$PORT"
fi

# Iniciar o Streamlit
$PYTHON_CMD -m streamlit run "$APP_FILE" \
    --server.port=$PORT \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false

echo ""
print_info "Servidor Streamlit encerrado."
print_info "Para reiniciar, execute: ./start_saev_universal.sh"

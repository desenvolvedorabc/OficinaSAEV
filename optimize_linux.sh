#!/bin/bash

# =============================================================================
# Script de Otimização Linux para ETL SAEV - Grandes Volumes
# OficinaSAEV - Sistema de Análise de Avaliações Educacionais
# =============================================================================

set -e

echo "🐧 Otimizando ambiente Linux para processamento de grandes volumes..."
echo "================================================================="

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

# Função para verificar memória disponível
check_system_resources() {
    print_message "Verificando recursos do sistema..."
    
    # Memória RAM
    total_ram_gb=$(free -g | awk 'NR==2{printf "%.1f", $2}')
    available_ram_gb=$(free -g | awk 'NR==2{printf "%.1f", $7}')
    
    # CPU
    cpu_cores=$(nproc)
    
    # Espaço em disco
    disk_free_gb=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    
    print_message "Recursos detectados:"
    echo "   - RAM Total: ${total_ram_gb} GB"
    echo "   - RAM Disponível: ${available_ram_gb} GB"
    echo "   - CPU Cores: ${cpu_cores}"
    echo "   - Espaço livre: ${disk_free_gb} GB"
    
    # Verificações de requisitos mínimos
    if (( $(echo "$available_ram_gb < 2" | bc -l) )); then
        print_warning "RAM disponível baixa (${available_ram_gb}GB). Recomendado: 4GB+"
        print_warning "O processamento pode ser lento ou falhar com volumes grandes"
    fi
    
    if (( disk_free_gb < 10 )); then
        print_warning "Espaço em disco baixo (${disk_free_gb}GB). Recomendado: 20GB+"
    fi
    
    if [[ $cpu_cores -lt 2 ]]; then
        print_warning "Poucos CPU cores (${cpu_cores}). Recomendado: 4+"
    fi
}

# Função para otimizar configurações do sistema
optimize_system() {
    print_message "Aplicando otimizações do sistema Linux..."
    
    # Cria diretório temporário otimizado
    print_message "Configurando diretório temporário..."
    sudo mkdir -p /tmp/duckdb_temp
    sudo chmod 777 /tmp/duckdb_temp
    
    # Limpa arquivos temporários antigos
    print_message "Limpando arquivos temporários antigos..."
    rm -rf /tmp/duckdb_temp/*
    
    # Configurações de memória virtual (se tiver permissão)
    if [[ $EUID -eq 0 ]]; then
        print_message "Otimizando configurações de memória virtual..."
        # Reduz swappiness para usar mais RAM
        echo 10 > /proc/sys/vm/swappiness
        # Aumenta dirty ratio para melhor performance de I/O
        echo 15 > /proc/sys/vm/dirty_ratio
        print_success "Configurações de memória otimizadas"
    else
        print_warning "Execute como root para otimizações avançadas de sistema"
        print_message "Alternativa: sudo sysctl vm.swappiness=10"
    fi
}

# Função para instalar dependências extras se necessário
install_monitoring_tools() {
    print_message "Verificando ferramentas de monitoramento..."
    
    # Verifica se htop está instalado
    if ! command -v htop &> /dev/null; then
        print_message "Instalando htop para monitoramento..."
        sudo apt update
        sudo apt install -y htop
    fi
    
    # Verifica se iotop está instalado
    if ! command -v iotop &> /dev/null; then
        print_message "Instalando iotop para monitoramento de I/O..."
        sudo apt install -y iotop
    fi
    
    print_success "Ferramentas de monitoramento prontas"
}

# Função para configurar ambiente Python
setup_python_optimizations() {
    print_message "Configurando otimizações Python..."
    
    # Instala psutil se não estiver instalado
    if ! python3 -c "import psutil" 2>/dev/null; then
        print_message "Instalando psutil para monitoramento de sistema..."
        pip install psutil
    fi
    
    # Configura variáveis de ambiente para otimização
    export PYTHONUNBUFFERED=1
    export PYTHONHASHSEED=0
    
    print_success "Ambiente Python otimizado"
}

# Função para criar script de monitoramento
create_monitoring_script() {
    print_message "Criando script de monitoramento..."
    
    cat > monitor_etl.sh << 'EOL'
#!/bin/bash
# Script para monitorar o ETL em execução

echo "🔍 Monitoramento do ETL SAEV - Pressione Ctrl+C para sair"
echo "======================================================="

while true; do
    clear
    echo "$(date) - Status do Sistema:"
    echo ""
    
    # Memória
    echo "💾 MEMÓRIA:"
    free -h | head -2
    echo ""
    
    # CPU e Processos Python
    echo "🖥️  PROCESSOS PYTHON:"
    ps aux | grep python | grep -v grep | head -5
    echo ""
    
    # Tamanho do banco de dados
    if [ -f "db/avaliacao_prod.duckdb" ]; then
        size=$(du -h db/avaliacao_prod.duckdb | cut -f1)
        echo "📁 BANCO DE DADOS: ${size}"
    else
        echo "📁 BANCO DE DADOS: Não encontrado"
    fi
    echo ""
    
    # I/O do disco
    echo "💿 I/O DISCO (últimos 5 processos):"
    sudo iotop -ao -d 1 -n 1 2>/dev/null | head -10 | tail -5 2>/dev/null || echo "iotop não disponível"
    echo ""
    
    sleep 5
done
EOL
    
    chmod +x monitor_etl.sh
    print_success "Script de monitoramento criado: ./monitor_etl.sh"
}

# Função para criar versão otimizada do requirements.txt
create_optimized_requirements() {
    print_message "Criando requirements otimizado para Linux..."
    
    cat > requirements_linux_optimized.txt << 'EOL'
# Requirements otimizado para Linux - Processamento de grandes volumes
pandas>=2.0.0
numpy>=1.24.0
duckdb>=0.9.0
psutil>=5.9.0

# Visualização (essencial)
streamlit>=1.28.0
plotly>=5.17.0
altair<5.0.0,>=4.2.1

# Machine Learning (essencial)
scikit-learn>=1.3.0
scipy>=1.11.0

# Exportação (essencial)
openpyxl>=3.1.0
xlsxwriter>=3.1.0
reportlab>=4.0.0

# Jupyter (essencial)
jupyter>=1.0.0
ipykernel>=6.25.0

# Utilitários
pathlib2>=2.3.7
python-dotenv>=1.0.0

# Monitoramento e otimização específica para Linux
psutil>=5.9.0
memory-profiler>=0.60.0

# Streamlit plugins (opcionais - instalar apenas se necessário)
# streamlit-aggrid>=0.3.4
# streamlit-option-menu>=0.3.6
EOL

    print_success "Requirements otimizado criado: requirements_linux_optimized.txt"
}

# Função principal
main() {
    print_message "Iniciando otimização do ambiente Linux..."
    
    check_system_resources
    echo ""
    
    optimize_system
    echo ""
    
    install_monitoring_tools
    echo ""
    
    setup_python_optimizations
    echo ""
    
    create_monitoring_script
    echo ""
    
    create_optimized_requirements
    echo ""
    
    print_success "=============================================="
    print_success "🎉 Otimização do Linux concluída!"
    print_success "=============================================="
    echo ""
    echo "📋 Próximos passos para usar o ETL otimizado:"
    echo ""
    echo "1. Para monitorar o ETL em tempo real:"
    echo "   ./monitor_etl.sh"
    echo ""
    echo "2. Para executar o ETL otimizado:"
    echo "   python saev_etl_linux_optimized.py --mode full"
    echo ""
    echo "3. Para instalar dependências otimizadas:"
    echo "   pip install -r requirements_linux_optimized.txt"
    echo ""
    print_warning "IMPORTANTE: Para grandes volumes (26M+ registros):"
    print_warning "- Execute em horário de menor uso do sistema"
    print_warning "- Monitore o uso de memória durante o processamento"
    print_warning "- Tenha pelo menos 4GB de RAM disponível"
    print_warning "- Reserve pelo menos 10GB de espaço em disco"
    echo ""
    echo "🔍 Use 'htop' em outro terminal para monitorar recursos"
    echo "📊 Use './monitor_etl.sh' para monitoramento específico do ETL"
}

# Executa função principal
main

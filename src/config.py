"""
Configurações do projeto OficinaSAEV
Sistema de Análise de Avaliações Educacionais
"""

import os
from pathlib import Path

# Caminhos base do projeto
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
TEST_DATA_DIR = DATA_DIR / "test"
DB_DIR = BASE_DIR / "db"
REPORTS_DIR = BASE_DIR / "reports"

# Configurações do banco de dados
DATABASE_CONFIG = {
    "test": {
        "path": DB_DIR / "avaliacao_teste.duckdb",
        "description": "Banco de dados para testes e desenvolvimento"
    },
    "production": {
        "path": DB_DIR / "avaliacao_prod.duckdb",
        "description": "Banco de dados de produção"
    }
}

# Configurações CSV
CSV_CONFIG = {
    "separator": ",",
    "text_delimiter": '"',
    "encoding": "utf-8",
    "header_row": 0
}

# Colunas esperadas no CSV
CSV_COLUMNS = [
    "MUN_UF", "MUN_NOME", "ESC_INEP", "ESC_NOME", "SER_NUMBER", "SER_NOME",
    "TUR_PERIODO", "TUR_NOME", "ALU_ID", "ALU_NOME", "ALU_CPF", "AVA_NOME",
    "AVA_ANO", "DIS_NOME", "TES_NOME", "TEG_ORDEM", "ATR_RESPOSTA", 
    "ATR_CERTO", "MTI_CODIGO", "MTI_DESCRITOR"
]

# Configurações do Streamlit
STREAMLIT_CONFIG = {
    "page_title": "SAEV Dashboard",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Configurações de relatórios
REPORT_CONFIG = {
    "formats": ["xlsx", "pdf"],
    "default_format": "xlsx",
    "date_format": "%d/%m/%Y",
    "number_format": "0.00"
}

def get_database_path(environment="test"):
    """
    Retorna o caminho do banco de dados para o ambiente especificado
    
    Args:
        environment (str): 'test' ou 'production'
    
    Returns:
        Path: Caminho para o banco de dados
    """
    return DATABASE_CONFIG[environment]["path"]

def ensure_directories():
    """
    Garante que todos os diretórios necessários existam
    """
    directories = [DATA_DIR, RAW_DATA_DIR, TEST_DATA_DIR, DB_DIR, REPORTS_DIR]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("✅ Estrutura de diretórios verificada")

if __name__ == "__main__":
    # Verificar configuração
    print("🔧 Configuração do Projeto SAEV")
    print(f"📁 Diretório base: {BASE_DIR}")
    print(f"📊 Diretório de dados: {DATA_DIR}")
    print(f"🗄️ Diretório do banco: {DB_DIR}")
    print(f"📈 Diretório de relatórios: {REPORTS_DIR}")
    
    ensure_directories()

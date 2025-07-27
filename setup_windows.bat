@echo off
REM =============================================================================
REM Script de Configuração do Ambiente Python - Windows
REM OficinaSAEV - Sistema de Análise de Avaliações Educacionais
REM =============================================================================

echo 🪟 Iniciando configuração do ambiente Python para Windows...
echo ==================================================

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python não encontrado. Por favor, instale Python 3.11+ de https://python.org
    echo Certifique-se de marcar "Add Python to PATH" durante a instalação.
    pause
    exit /b 1
)

REM Verificar versão do Python
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python versão encontrada: %PYTHON_VERSION%

REM Verificar se Git está instalado
git --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Git não encontrado. Recomendamos instalar Git de https://git-scm.com/
    echo Você pode continuar sem Git, mas não poderá clonar repositórios.
    pause
)

REM Verificar se estamos no diretório correto
if not exist "requirements.txt" (
    echo [ERROR] Arquivo requirements.txt não encontrado.
    echo Execute este script no diretório do projeto.
    pause
    exit /b 1
)

echo [INFO] Criando ambiente virtual Python...
python -m venv venv_saev

REM Ativar ambiente virtual
echo [INFO] Ativando ambiente virtual...
call venv_saev\Scripts\activate.bat

REM Atualizar pip
echo [INFO] Atualizando pip...
python -m pip install --upgrade pip setuptools wheel

REM Instalar dependências
echo [INFO] Instalando dependências do projeto...
pip install -r .\requirements.txt

REM Criar estrutura de diretórios necessários (dados sigilosos não versionados)
echo [INFO] Criando estrutura de diretórios para dados sigilosos...
if not exist "data\raw" mkdir data\raw
if not exist "data\test" mkdir data\test
if not exist "db" mkdir db
if not exist "src\data" mkdir src\data
if not exist "src\dashboard" mkdir src\dashboard
if not exist "src\reports" mkdir src\reports
if not exist "src\analytics" mkdir src\analytics
if not exist "reports" mkdir reports
if not exist "tests" mkdir tests

REM Criar READMEs informativos nos diretórios de dados
echo [INFO] Criando arquivos informativos...
(
echo # 📊 Diretório de Dados
echo.
echo ## ⚠️ IMPORTANTE - DADOS SIGILOSOS
echo.
echo Este diretório contém dados sigilosos e NÃO é versionado no Git.
echo.
echo ## 📁 Estrutura
echo.
echo - **`raw/`** - Dados CSV originais do SAEV
echo - **`test/`** - Dados de teste e amostras ^(anonimizadas^)
echo.
echo ## 📋 Instruções
echo.
echo 1. Coloque os arquivos CSV do SAEV em `raw/`
echo 2. Use dados anonimizados em `test/` para desenvolvimento
echo 3. **NUNCA** commite dados com informações pessoais
echo.
echo ## 🔒 Segurança
echo.
echo - CPF, nomes e dados pessoais devem ser protegidos
echo - Use dados sintéticos ou anonimizados para testes
echo - Esta pasta está no .gitignore por segurança
) > data\README.md

(
echo # 💾 Diretório de Banco de Dados
echo.
echo ## ⚠️ IMPORTANTE - DADOS SIGILOSOS
echo.
echo Este diretório contém bancos de dados sigilosos e NÃO é versionado no Git.
echo.
echo ## 🗄️ Bancos Padrão
echo.
echo - **`avaliacao_teste.duckdb`** - Banco para desenvolvimento
echo - **`avaliacao_prod.duckdb`** - Banco de produção
echo.
echo ## 🔒 Segurança
echo.
echo - Bancos contêm dados sensíveis
echo - Faça backup regular dos bancos
echo - Configure adequadamente as permissões
echo - Esta pasta está no .gitignore por segurança
) > db\README.md

REM Instalar extensões do Jupyter
echo [INFO] Configurando Jupyter...
python -m ipykernel install --user --name=venv_saev --display-name="Python (SAEV)"

REM Criar scripts de ativação convenientes
echo [INFO] Criando scripts de conveniência...

REM Script para ativar ambiente
echo @echo off > activate_saev.bat
echo call venv_saev\Scripts\activate.bat >> activate_saev.bat
echo echo Ambiente SAEV ativado! >> activate_saev.bat
echo echo Para desativar, digite: deactivate >> activate_saev.bat

REM Script para executar Jupyter
echo @echo off > start_jupyter.bat
echo call venv_saev\Scripts\activate.bat >> start_jupyter.bat
echo jupyter notebook >> start_jupyter.bat

REM Script para executar Streamlit (quando disponível)
echo @echo off > start_dashboard.bat
echo call venv_saev\Scripts\activate.bat >> start_dashboard.bat
echo streamlit run src\dashboard\main.py >> start_dashboard.bat

echo.
echo [SUCCESS] ==============================================
echo [SUCCESS] 🎉 Configuração concluída com sucesso!
echo [SUCCESS] ==============================================
echo.
echo Para ativar o ambiente virtual, execute:
echo   venv_saev\Scripts\activate.bat
echo   OU clique duplo em: activate_saev.bat
echo.
echo Para iniciar o Jupyter Notebook:
echo   jupyter notebook
echo   OU clique duplo em: start_jupyter.bat
echo.
echo Para executar o dashboard Streamlit (quando disponível):
echo   streamlit run src\dashboard\main.py
echo   OU clique duplo em: start_dashboard.bat
echo.
echo [WARNING] Lembre-se de sempre ativar o ambiente virtual antes de trabalhar no projeto!
echo.

pause

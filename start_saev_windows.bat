@echo off
REM SAEV Streamlit - Script para Windows
REM Compatível com Windows 10/11

title SAEV - Sistema de Avaliacao Educacional

echo ================================================
echo 🚀 SAEV - Sistema de Avaliacao Educacional
echo 📊 Iniciando Streamlit no Windows
echo ================================================

REM Verificar se estamos no diretório correto
if not exist "saev_streamlit.py" (
    if not exist "saev_streamlit2.py" (
        if not exist "saev_rankings.py" (
            echo ❌ Erro: Execute este script na pasta raiz do projeto
            echo    Arquivos esperados: saev_streamlit.py, saev_streamlit2.py ou saev_rankings.py
            pause
            exit /b 1
        )
    )
)

echo ✅ Diretorio correto verificado

REM Verificar banco de dados
if not exist "db\avaliacao_prod.duckdb" (
    echo ❌ Erro: Banco de dados nao encontrado
    echo    Caminho esperado: db\avaliacao_prod.duckdb
    echo    Execute o ETL primeiro: python run_etl.py full
    pause
    exit /b 1
)

echo ✅ Banco de dados encontrado

REM Detectar Python
set PYTHON_CMD=
where python >nul 2>&1
if %errorlevel% == 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    for /f "tokens=1 delims=." %%a in ("%PYTHON_VERSION%") do set MAJOR_VERSION=%%a
    if "%MAJOR_VERSION%"=="3" (
        set PYTHON_CMD=python
    )
)

if "%PYTHON_CMD%"=="" (
    where python3 >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON_CMD=python3
    )
)

if "%PYTHON_CMD%"=="" (
    echo ❌ Erro: Python 3 nao encontrado!
    echo    Instale Python 3 ou adicione ao PATH
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python encontrado: %PYTHON_VERSION%

REM Verificar dependências
echo 🔍 Verificando dependencias...

%PYTHON_CMD% -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Streamlit nao instalado!
    echo    Execute: pip install streamlit
    pause
    exit /b 1
)

%PYTHON_CMD% -c "import duckdb" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ DuckDB nao instalado!
    echo    Execute: pip install duckdb
    pause
    exit /b 1
)

%PYTHON_CMD% -c "import pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Pandas nao instalado!
    echo    Execute: pip install pandas
    pause
    exit /b 1
)

%PYTHON_CMD% -c "import plotly" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Plotly nao instalado!
    echo    Execute: pip install plotly
    pause
    exit /b 1
)

echo ✅ Todas as dependencias verificadas

REM Menu de seleção
echo.
echo 🎯 Escolha o aplicativo:
echo 1) SAEV Dashboard Geral (porta 8501)
echo 2) SAEV Dashboard com Filtros (porta 8502)
echo 3) SAEV Rankings e Classificacoes (porta 8503)
echo.

set /p choice="Digite sua escolha (1, 2 ou 3): "

REM Pergunta sobre abertura do navegador
echo.
echo 🌐 Abrir navegador automaticamente?
echo y) Sim - Abrir navegador apos inicializacao
echo n) Nao - Apenas iniciar o servidor
echo.

set /p open_browser="Abrir navegador? (y/n) [padrao: y]: "
if "%open_browser%"=="" set open_browser=y

if "%choice%"=="1" (
    set APP_FILE=saev_streamlit.py
    set PORT=8501
    set APP_NAME=SAEV Dashboard Geral
) else if "%choice%"=="2" (
    set APP_FILE=saev_streamlit2.py
    set PORT=8502
    set APP_NAME=SAEV Dashboard com Filtros
) else if "%choice%"=="3" (
    set APP_FILE=saev_rankings.py
    set PORT=8503
    set APP_NAME=SAEV Rankings e Classificacoes
) else (
    echo ❌ Escolha invalida!
    pause
    exit /b 1
)

REM Verificar se arquivo existe
if not exist "%APP_FILE%" (
    echo ❌ Arquivo nao encontrado: %APP_FILE%
    pause
    exit /b 1
)

REM Obter IP local
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4"') do set LOCAL_IP=%%i
set LOCAL_IP=%LOCAL_IP: =%

echo.
echo ================================================
echo 🚀 Iniciando %APP_NAME%
echo ================================================
echo 📁 Arquivo: %APP_FILE%
echo 🌐 Porta: %PORT%
echo 💻 Sistema: Windows
echo.
echo 📍 URLs de acesso:
echo    Local: http://localhost:%PORT%
if not "%LOCAL_IP%"=="" echo    Rede:  http://%LOCAL_IP%:%PORT%
echo.
echo 💡 Pressione Ctrl+C para parar o servidor
echo ================================================

REM Configurar variáveis de ambiente
set STREAMLIT_SERVER_HEADLESS=true
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

REM Abrir navegador se solicitado
if /i "%open_browser%"=="y" (
    echo 🌐 Navegador sera aberto automaticamente em 5 segundos...
    start "" /min cmd /c "timeout /t 5 >nul && start http://localhost:%PORT%"
) else (
    echo 🌐 Acesse manualmente: http://localhost:%PORT%
)

REM Iniciar Streamlit
%PYTHON_CMD% -m streamlit run %APP_FILE% --server.port=%PORT% --server.headless=true --browser.gatherUsageStats=false

echo.
echo 📊 Servidor Streamlit encerrado.
echo 🔄 Para reiniciar, execute novamente este script.
pause

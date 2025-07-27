# 📊 Painel Interativo SAEV - Dashboard HTML
# Script para criar painel web interativo com análises SAEV
# Autor: Sistema SAEV
# Data: 2025-07-27

# ============================================================================
# 📦 INSTALAÇÃO E CARREGAMENTO DE PACOTES
# ============================================================================

# Configurar mirror CRAN
options(repos = c(CRAN = "https://cran.rstudio.com/"))

# Função para instalar pacotes se necessário
install_if_missing <- function(packages) {
  new_packages <- packages[!(packages %in% installed.packages()[,"Package"])]
  if(length(new_packages)) {
    cat("📦 Instalando pacotes:", paste(new_packages, collapse = ", "), "\n")
    install.packages(new_packages, dependencies = TRUE, quiet = TRUE)
  }
}

# Lista de pacotes necessários para dashboard interativo
required_packages <- c(
  "DBI",           # Interface de banco de dados
  "duckdb",        # Conector DuckDB
  "dplyr",         # Manipulação de dados
  "plotly",        # Gráficos interativos
  "DT",            # Tabelas interativas
  "htmlwidgets",   # Widgets HTML
  "htmltools",     # Ferramentas HTML
  "crosstalk",     # Interação entre widgets
  "flexdashboard", # Dashboard em R
  "knitr"          # Geração de relatórios
)

# Tentar instalar apenas os pacotes essenciais primeiro
essential_packages <- c("DBI", "duckdb", "dplyr")

suppressPackageStartupMessages({
  install_if_missing(essential_packages)
  
  # Carregar pacotes essenciais
  library(DBI)
  library(duckdb)
  library(dplyr)
})

# Tentar carregar pacotes para interatividade (opcionais)
use_interactive <- TRUE
tryCatch({
  if (!require("plotly", quietly = TRUE)) {
    install.packages("plotly")
    library(plotly)
  }
  if (!require("DT", quietly = TRUE)) {
    install.packages("DT")
    library(DT)
  }
  if (!require("htmlwidgets", quietly = TRUE)) {
    install.packages("htmlwidgets")
    library(htmlwidgets)
  }
}, error = function(e) {
  cat("⚠️ Pacotes interativos não disponíveis, usando versão simplificada\n")
  use_interactive <<- FALSE
})

cat("📊 === PAINEL INTERATIVO SAEV ===\n\n")

# ============================================================================
# 🔌 CONEXÃO COM O BANCO DE DADOS
# ============================================================================

cat("🔌 Conectando ao banco DuckDB...\n")

# Caminho do banco de dados
db_path <- "db/avaliacao_prod.duckdb"

# Verificar se o banco existe
if (!file.exists(db_path)) {
  stop("❌ Erro: Banco de dados não encontrado em: ", db_path, 
       "\n   Execute o ETL primeiro: python run_etl.py full")
}

# Conectar ao DuckDB
con <- dbConnect(duckdb::duckdb(), dbdir = db_path)

cat("✅ Conectado ao banco:", db_path, "\n\n")

# ============================================================================
# 📊 COLETA DE DADOS PRINCIPAIS
# ============================================================================

cat("📊 Coletando dados principais...\n")

# 1. Dados por disciplina
dados_disciplina <- dbGetQuery(con, "
SELECT 
    f.DIS_NOME,
    COUNT(DISTINCT f.ALU_ID) as total_alunos,
    SUM(f.ACERTO) as total_acertos,
    SUM(f.ERRO) as total_erros,
    ROUND((SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2) as taxa_acerto_pct
FROM fato_resposta_aluno f
GROUP BY f.DIS_NOME
ORDER BY taxa_acerto_pct DESC
")

# 2. Dados por município (top 20)
dados_municipio <- dbGetQuery(con, "
SELECT 
    f.MUN_NOME,
    COUNT(DISTINCT f.ALU_ID) as total_alunos,
    SUM(f.ACERTO) as total_acertos,
    SUM(f.ERRO) as total_erros,
    ROUND((SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2) as taxa_acerto_pct
FROM fato_resposta_aluno f
GROUP BY f.MUN_NOME
HAVING SUM(f.ACERTO + f.ERRO) > 5000
ORDER BY taxa_acerto_pct DESC
LIMIT 20
")

# 3. Dados por escola (top 30)
dados_escola <- dbGetQuery(con, "
SELECT 
    e.ESC_NOME,
    f.MUN_NOME,
    COUNT(DISTINCT f.ALU_ID) as total_alunos,
    SUM(f.ACERTO) as total_acertos,
    SUM(f.ERRO) as total_erros,
    ROUND((SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2) as taxa_acerto_pct
FROM fato_resposta_aluno f
JOIN dim_escola e ON f.ESC_INEP = e.ESC_INEP
GROUP BY e.ESC_NOME, f.MUN_NOME
HAVING SUM(f.ACERTO + f.ERRO) > 1000
ORDER BY taxa_acerto_pct DESC
LIMIT 30
")

# 4. Dados disciplina vs série
dados_disc_serie <- dbGetQuery(con, "
SELECT 
    f.DIS_NOME,
    f.SER_NOME,
    COUNT(DISTINCT f.ALU_ID) as total_alunos,
    ROUND((SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2) as taxa_acerto_pct
FROM fato_resposta_aluno f
GROUP BY f.DIS_NOME, f.SER_NOME
ORDER BY f.DIS_NOME, f.SER_NOME
")

# 5. Indicadores gerais
total_alunos <- dbGetQuery(con, "SELECT COUNT(DISTINCT ALU_ID) as total FROM fato_resposta_aluno")$total
total_escolas <- dbGetQuery(con, "SELECT COUNT(DISTINCT ESC_INEP) as total FROM fato_resposta_aluno")$total
total_municipios <- dbGetQuery(con, "SELECT COUNT(DISTINCT MUN_NOME) as total FROM fato_resposta_aluno")$total
taxa_geral <- dbGetQuery(con, "SELECT ROUND((SUM(ACERTO) * 100.0) / SUM(ACERTO + ERRO), 2) as taxa FROM fato_resposta_aluno")$taxa

cat("✅ Dados coletados com sucesso!\n\n")

# ============================================================================
# 🎨 CRIAÇÃO DO PAINEL HTML
# ============================================================================

cat("🎨 Criando painel HTML...\n")

# Criar diretório para o painel
painel_dir <- "R/painel_html"
if (!dir.exists(painel_dir)) {
  dir.create(painel_dir, recursive = TRUE)
}

# Função para criar gráfico (compatível com ou sem plotly)
create_plot <- function(data, x, y, title, type = "bar") {
  if (use_interactive && require("plotly", quietly = TRUE)) {
    if (type == "bar") {
      p <- plot_ly(data, x = ~get(x), y = ~get(y), type = 'bar',
                   text = ~paste(get(y), "%"), textposition = 'outside') %>%
        layout(title = title, xaxis = list(title = x), yaxis = list(title = y))
    }
    return(p)
  } else {
    # Fallback para gráfico estático
    return(paste("Gráfico:", title, "(plotly não disponível)"))
  }
}

# Função para criar tabela (compatível com ou sem DT)
create_table <- function(data, caption = "") {
  if (use_interactive && require("DT", quietly = TRUE)) {
    return(datatable(data, caption = caption, options = list(
      pageLength = 10,
      scrollX = TRUE,
      dom = 'Bfrtip'
    )))
  } else {
    # Fallback para tabela simples
    return(knitr::kable(data, caption = caption))
  }
}

# ============================================================================
# 📝 GERAÇÃO DO ARQUIVO HTML
# ============================================================================

# Criar conteúdo HTML
html_content <- paste0('
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel SAEV - Dashboard de Análises</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f5f5f5; 
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background-color: white; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            border-bottom: 2px solid #007bff; 
            padding-bottom: 20px; 
        }
        .kpi-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .kpi-card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 20px; 
            border-radius: 8px; 
            text-align: center; 
        }
        .kpi-number { 
            font-size: 2em; 
            font-weight: bold; 
            margin-bottom: 5px; 
        }
        .kpi-label { 
            font-size: 0.9em; 
            opacity: 0.9; 
        }
        .section { 
            margin-bottom: 40px; 
            padding: 20px; 
            background-color: #fafafa; 
            border-radius: 8px; 
        }
        .section h2 { 
            color: #333; 
            border-bottom: 2px solid #007bff; 
            padding-bottom: 10px; 
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 15px; 
        }
        th, td { 
            padding: 12px; 
            text-align: left; 
            border-bottom: 1px solid #ddd; 
        }
        th { 
            background-color: #007bff; 
            color: white; 
        }
        tr:hover { 
            background-color: #f5f5f5; 
        }
        .taxa-alta { color: #28a745; font-weight: bold; }
        .taxa-media { color: #ffc107; font-weight: bold; }
        .taxa-baixa { color: #dc3545; font-weight: bold; }
        .footer { 
            text-align: center; 
            margin-top: 40px; 
            padding-top: 20px; 
            border-top: 1px solid #ddd; 
            color: #666; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Painel SAEV - Dashboard de Análises</h1>
            <p><strong>Sistema de Análise de Avaliações Educacionais</strong></p>
            <p>📅 Gerado em: ', format(Sys.time(), "%d/%m/%Y às %H:%M"), '</p>
        </div>

        <!-- KPIs Principais -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-number">', format(total_alunos, big.mark = ","), '</div>
                <div class="kpi-label">Total de Alunos</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-number">', format(total_escolas, big.mark = ","), '</div>
                <div class="kpi-label">Total de Escolas</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-number">', format(total_municipios, big.mark = ","), '</div>
                <div class="kpi-label">Total de Municípios</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-number">', taxa_geral, '%</div>
                <div class="kpi-label">Taxa de Acerto Geral</div>
            </div>
        </div>

        <!-- Seção 1: Taxa de Acerto por Disciplina -->
        <div class="section">
            <h2>📚 Taxa de Acerto por Disciplina</h2>
            <table>
                <thead>
                    <tr>
                        <th>Disciplina</th>
                        <th>Total de Alunos</th>
                        <th>Total de Acertos</th>
                        <th>Total de Erros</th>
                        <th>Taxa de Acerto (%)</th>
                    </tr>
                </thead>
                <tbody>')

# Adicionar dados de disciplina
for (i in 1:nrow(dados_disciplina)) {
  taxa_class <- if (dados_disciplina$taxa_acerto_pct[i] >= 70) "taxa-alta" 
               else if (dados_disciplina$taxa_acerto_pct[i] >= 50) "taxa-media" 
               else "taxa-baixa"
  
  html_content <- paste0(html_content, '
                    <tr>
                        <td>', dados_disciplina$DIS_NOME[i], '</td>
                        <td>', format(dados_disciplina$total_alunos[i], big.mark = ","), '</td>
                        <td>', format(dados_disciplina$total_acertos[i], big.mark = ","), '</td>
                        <td>', format(dados_disciplina$total_erros[i], big.mark = ","), '</td>
                        <td class="', taxa_class, '">', dados_disciplina$taxa_acerto_pct[i], '%</td>
                    </tr>')
}

html_content <- paste0(html_content, '
                </tbody>
            </table>
        </div>

        <!-- Seção 2: Top 20 Municípios -->
        <div class="section">
            <h2>🏙️ Top 20 Municípios por Taxa de Acerto</h2>
            <table>
                <thead>
                    <tr>
                        <th>Posição</th>
                        <th>Município</th>
                        <th>Total de Alunos</th>
                        <th>Taxa de Acerto (%)</th>
                    </tr>
                </thead>
                <tbody>')

# Adicionar dados de município
for (i in 1:nrow(dados_municipio)) {
  taxa_class <- if (dados_municipio$taxa_acerto_pct[i] >= 70) "taxa-alta" 
               else if (dados_municipio$taxa_acerto_pct[i] >= 50) "taxa-media" 
               else "taxa-baixa"
  
  html_content <- paste0(html_content, '
                    <tr>
                        <td>', i, 'º</td>
                        <td>', dados_municipio$MUN_NOME[i], '</td>
                        <td>', format(dados_municipio$total_alunos[i], big.mark = ","), '</td>
                        <td class="', taxa_class, '">', dados_municipio$taxa_acerto_pct[i], '%</td>
                    </tr>')
}

html_content <- paste0(html_content, '
                </tbody>
            </table>
        </div>

        <!-- Seção 3: Top 30 Escolas -->
        <div class="section">
            <h2>🏫 Top 30 Escolas por Taxa de Acerto</h2>
            <table>
                <thead>
                    <tr>
                        <th>Posição</th>
                        <th>Escola</th>
                        <th>Município</th>
                        <th>Total de Alunos</th>
                        <th>Taxa de Acerto (%)</th>
                    </tr>
                </thead>
                <tbody>')

# Adicionar dados de escola
for (i in 1:nrow(dados_escola)) {
  taxa_class <- if (dados_escola$taxa_acerto_pct[i] >= 70) "taxa-alta" 
               else if (dados_escola$taxa_acerto_pct[i] >= 50) "taxa-media" 
               else "taxa-baixa"
  
  html_content <- paste0(html_content, '
                    <tr>
                        <td>', i, 'º</td>
                        <td>', dados_escola$ESC_NOME[i], '</td>
                        <td>', dados_escola$MUN_NOME[i], '</td>
                        <td>', format(dados_escola$total_alunos[i], big.mark = ","), '</td>
                        <td class="', taxa_class, '">', dados_escola$taxa_acerto_pct[i], '%</td>
                    </tr>')
}

html_content <- paste0(html_content, '
                </tbody>
            </table>
        </div>

        <!-- Seção 4: Matriz Disciplina vs Série -->
        <div class="section">
            <h2>📊 Taxa de Acerto por Disciplina e Série</h2>
            <table>
                <thead>
                    <tr>
                        <th>Disciplina</th>
                        <th>Série</th>
                        <th>Total de Alunos</th>
                        <th>Taxa de Acerto (%)</th>
                    </tr>
                </thead>
                <tbody>')

# Adicionar dados disciplina vs série
for (i in 1:nrow(dados_disc_serie)) {
  taxa_class <- if (dados_disc_serie$taxa_acerto_pct[i] >= 70) "taxa-alta" 
               else if (dados_disc_serie$taxa_acerto_pct[i] >= 50) "taxa-media" 
               else "taxa-baixa"
  
  html_content <- paste0(html_content, '
                    <tr>
                        <td>', dados_disc_serie$DIS_NOME[i], '</td>
                        <td>', dados_disc_serie$SER_NOME[i], '</td>
                        <td>', format(dados_disc_serie$total_alunos[i], big.mark = ","), '</td>
                        <td class="', taxa_class, '">', dados_disc_serie$taxa_acerto_pct[i], '%</td>
                    </tr>')
}

html_content <- paste0(html_content, '
                </tbody>
            </table>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>📊 <strong>Sistema SAEV</strong> - Análise de Avaliações Educacionais</p>
            <p>Dados extraídos do banco DuckDB com arquitetura Star Schema</p>
            <p>Gerado automaticamente pelo script R em ', format(Sys.time(), "%d/%m/%Y às %H:%M"), '</p>
        </div>
    </div>
</body>
</html>')

# Salvar arquivo HTML
html_file <- file.path(painel_dir, "painel_saev_dashboard.html")
writeLines(html_content, html_file, useBytes = TRUE)

# ============================================================================
# 📊 EXPORTAR DADOS PARA CSV
# ============================================================================

cat("📊 Exportando dados para CSV...\n")

# Exportar todos os dados para CSV
write.csv(dados_disciplina, file.path(painel_dir, "dados_disciplina.csv"), row.names = FALSE)
write.csv(dados_municipio, file.path(painel_dir, "dados_municipio.csv"), row.names = FALSE)
write.csv(dados_escola, file.path(painel_dir, "dados_escola.csv"), row.names = FALSE)
write.csv(dados_disc_serie, file.path(painel_dir, "dados_disciplina_serie.csv"), row.names = FALSE)

# Criar arquivo de indicadores
indicadores_df <- data.frame(
  Indicador = c("Total de Alunos", "Total de Escolas", "Total de Municípios", "Taxa de Acerto Geral"),
  Valor = c(total_alunos, total_escolas, total_municipios, taxa_geral),
  stringsAsFactors = FALSE
)
write.csv(indicadores_df, file.path(painel_dir, "indicadores_gerais.csv"), row.names = FALSE)

# ============================================================================
# 🎯 FINALIZAÇÃO
# ============================================================================

# Fechar conexão
dbDisconnect(con)

cat("\n✅ === PAINEL INTERATIVO CRIADO COM SUCESSO! ===\n")
cat("📁 Arquivos gerados em:", painel_dir, "\n")
cat("🌐 Arquivo principal:", html_file, "\n")
cat("📊 Dados CSV exportados para análises adicionais\n")
cat("\n🚀 Para visualizar o painel:\n")
cat("   1. Abra o arquivo:", html_file, "\n")
cat("   2. Ou execute: open", html_file, "(macOS)\n")
cat("   3. Ou execute: xdg-open", html_file, "(Linux)\n")

cat("\n📈 Resumo dos Dados:\n")
cat(sprintf("   👥 Total de Alunos: %s\n", format(total_alunos, big.mark = ",")))
cat(sprintf("   🏫 Total de Escolas: %s\n", format(total_escolas, big.mark = ",")))
cat(sprintf("   🏙️ Total de Municípios: %s\n", format(total_municipios, big.mark = ",")))
cat(sprintf("   🎯 Taxa de Acerto Geral: %s%%\n", taxa_geral))

cat("\n🎨 O painel inclui:\n")
cat("   • KPIs principais em cards visuais\n")
cat("   • Tabelas interativas com classificação por cores\n")
cat("   • Dados exportados em CSV para análises adicionais\n")
cat("   • Layout responsivo para diferentes dispositivos\n")

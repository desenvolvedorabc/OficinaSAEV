# 📊 Análise de Dados SAEV - Relatório em Markdown
# Script R para gerar relatório completo em formato Markdown
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
    install.packages(new_packages, dependencies = TRUE)
  }
}

# Lista de pacotes necessários
required_packages <- c(
  "DBI",           # Interface de banco de dados
  "duckdb",        # Conector DuckDB
  "dplyr",         # Manipulação de dados
  "ggplot2",       # Visualizações
  "scales",        # Formatação de escalas
  "knitr",         # Tabelas formatadas
  "kableExtra"     # Tabelas HTML/Markdown
)

# Instalar pacotes faltantes
cat("🔧 Verificando e instalando pacotes necessários...\n")
install_if_missing(required_packages)

# Carregar pacotes
suppressPackageStartupMessages({
  library(DBI)
  library(duckdb)
  library(dplyr)
  library(ggplot2)
  library(scales)
  library(knitr)
  library(kableExtra)
})

cat("✅ Pacotes carregados com sucesso!\n\n")

# ============================================================================
# 🔌 CONEXÃO COM O BANCO DUCKDB
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
# 📝 CRIAR ARQUIVO MARKDOWN
# ============================================================================

# Nome do arquivo de relatório
relatorio_file <- paste0("R/relatorio_saev_", format(Sys.Date(), "%Y%m%d"), ".md")

# Função para escrever no relatório
write_md <- function(text, file = relatorio_file, append = TRUE) {
  cat(text, file = file, append = append)
}

# Inicializar relatório
write_md("", append = FALSE)  # Limpar arquivo

# Cabeçalho do relatório
header <- paste0(
  "# 📊 Relatório de Análise SAEV\n\n",
  "**Sistema de Análise de Avaliações Educacionais**\n\n",
  "📅 **Data de Geração:** ", format(Sys.time(), "%d/%m/%Y às %H:%M"), "\n",
  "🏛️ **Fonte:** Banco DuckDB - Star Schema\n",
  "⚙️ **Gerado por:** Script R automatizado\n\n",
  "---\n\n"
)
write_md(header)

cat("📝 Iniciando geração do relatório Markdown...\n")

# ============================================================================
# 📋 VERIFICAÇÃO DA ESTRUTURA DO BANCO
# ============================================================================

# Listar tabelas
tabelas <- dbListTables(con)

# Função para obter estatísticas das tabelas
get_table_stats <- function(table_name) {
  query <- paste("SELECT COUNT(*) as registros FROM", table_name)
  result <- dbGetQuery(con, query)
  return(result$registros)
}

# Seção de estrutura do banco
estrutura_md <- paste0(
  "## 🗄️ Estrutura do Banco de Dados\n\n",
  "O banco DuckDB contém as seguintes tabelas:\n\n",
  "| Tabela | Registros |\n",
  "|--------|----------:|\n"
)

for (tabela in tabelas) {
  registros <- get_table_stats(tabela)
  estrutura_md <- paste0(estrutura_md, 
    "| `", tabela, "` | ", format(registros, big.mark = ","), " |\n")
}

estrutura_md <- paste0(estrutura_md, "\n")
write_md(estrutura_md)

# ============================================================================
# 📊 ANÁLISE 1: NÚMERO DE ALUNOS POR MUNICÍPIO E SÉRIE
# ============================================================================

cat("📊 Processando Análise 1: Alunos por Município e Série...\n")

# Query para alunos por município e série
query_alunos_municipio_serie <- "
SELECT 
    f.MUN_NOME,
    f.SER_NOME,
    COUNT(DISTINCT f.ALU_ID) as total_alunos
FROM fato_resposta_aluno f
GROUP BY f.MUN_NOME, f.SER_NOME
ORDER BY total_alunos DESC
"

alunos_mun_serie <- dbGetQuery(con, query_alunos_municipio_serie)

# Alunos por série (agregado)
alunos_por_serie <- alunos_mun_serie %>%
  group_by(SER_NOME) %>%
  summarise(total_alunos = sum(total_alunos)) %>%
  arrange(desc(total_alunos))

# Escrever seção no Markdown
analise1_md <- paste0(
  "## 📊 Análise 1: Distribuição de Alunos\n\n",
  "### 📈 Alunos por Série\n\n"
)

# Tabela de alunos por série
analise1_md <- paste0(analise1_md, 
  "| Série | Total de Alunos |\n",
  "|-------|---------------:|\n"
)

for (i in 1:nrow(alunos_por_serie)) {
  analise1_md <- paste0(analise1_md,
    "| ", alunos_por_serie$SER_NOME[i], " | ", 
    format(alunos_por_serie$total_alunos[i], big.mark = ","), " |\n"
  )
}

# Top 10 município/série
analise1_md <- paste0(analise1_md, 
  "\n### 🏆 Top 10 Município/Série por Número de Alunos\n\n",
  "| Município | Série | Total de Alunos |\n",
  "|-----------|-------|---------------:|\n"
)

top10_mun_serie <- head(alunos_mun_serie, 10)
for (i in 1:nrow(top10_mun_serie)) {
  analise1_md <- paste0(analise1_md,
    "| ", top10_mun_serie$MUN_NOME[i], " | ", 
    top10_mun_serie$SER_NOME[i], " | ", 
    format(top10_mun_serie$total_alunos[i], big.mark = ","), " |\n"
  )
}

analise1_md <- paste0(analise1_md, "\n")
write_md(analise1_md)

# Gerar gráfico
p1 <- ggplot(alunos_por_serie, aes(x = reorder(SER_NOME, total_alunos), y = total_alunos)) +
  geom_col(fill = "steelblue", alpha = 0.8) +
  coord_flip() +
  labs(
    title = "Distribuição de Alunos por Série",
    x = "Série",
    y = "Número de Alunos"
  ) +
  scale_y_continuous(labels = comma_format()) +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5))

ggsave("R/grafico_alunos_por_serie.png", p1, width = 10, height = 6, dpi = 300)

# ============================================================================
# 📊 ANÁLISE 2: TAXA DE ACERTO POR MUNICÍPIO
# ============================================================================

cat("📊 Processando Análise 2: Taxa de Acerto por Município...\n")

# Query para taxa de acerto por município
query_taxa_acerto_municipio <- "
SELECT 
    f.MUN_NOME,
    COUNT(DISTINCT f.ALU_ID) as total_alunos,
    SUM(f.ACERTO) as total_acertos,
    SUM(f.ERRO) as total_erros,
    ROUND(
        (SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2
    ) as taxa_acerto_pct
FROM fato_resposta_aluno f
GROUP BY f.MUN_NOME
HAVING SUM(f.ACERTO + f.ERRO) > 1000
ORDER BY taxa_acerto_pct DESC
"

taxa_acerto_municipio <- dbGetQuery(con, query_taxa_acerto_municipio)

# Escrever seção no Markdown
analise2_md <- paste0(
  "## 📊 Análise 2: Taxa de Acerto por Município\n\n",
  "### 🏆 Top 15 Municípios por Taxa de Acerto\n\n",
  "| Município | Alunos | Acertos | Erros | Taxa de Acerto (%) |\n",
  "|-----------|-------:|--------:|------:|------------------:|\n"
)

top15_municipios <- head(taxa_acerto_municipio, 15)
for (i in 1:nrow(top15_municipios)) {
  analise2_md <- paste0(analise2_md,
    "| ", top15_municipios$MUN_NOME[i], " | ", 
    format(top15_municipios$total_alunos[i], big.mark = ","), " | ", 
    format(top15_municipios$total_acertos[i], big.mark = ","), " | ", 
    format(top15_municipios$total_erros[i], big.mark = ","), " | ", 
    top15_municipios$taxa_acerto_pct[i], "% |\n"
  )
}

analise2_md <- paste0(analise2_md, "\n")
write_md(analise2_md)

# Gerar gráfico
top_municipios <- head(taxa_acerto_municipio, 20)
p2 <- ggplot(top_municipios, aes(x = reorder(MUN_NOME, taxa_acerto_pct), y = taxa_acerto_pct)) +
  geom_col(fill = "darkgreen", alpha = 0.8) +
  coord_flip() +
  labs(
    title = "Taxa de Acerto por Município (Top 20)",
    x = "Município",
    y = "Taxa de Acerto (%)"
  ) +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5))

ggsave("R/grafico_taxa_acerto_municipio.png", p2, width = 12, height = 8, dpi = 300)

# ============================================================================
# 📊 ANÁLISE 3: DESEMPENHO POR DISCIPLINA E SÉRIE
# ============================================================================

cat("📊 Processando Análise 3: Desempenho por Disciplina e Série...\n")

# Query para desempenho por disciplina e série
query_desempenho_disciplina_serie <- "
SELECT 
    f.DIS_NOME,
    f.SER_NOME,
    COUNT(DISTINCT f.ALU_ID) as total_alunos,
    SUM(f.ACERTO) as total_acertos,
    SUM(f.ERRO) as total_erros,
    ROUND(
        (SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2
    ) as taxa_acerto_pct
FROM fato_resposta_aluno f
GROUP BY f.DIS_NOME, f.SER_NOME
ORDER BY f.DIS_NOME, f.SER_NOME
"

desempenho_disc_serie <- dbGetQuery(con, query_desempenho_disciplina_serie)

# Escrever seção no Markdown
analise3_md <- paste0(
  "## 📊 Análise 3: Desempenho por Disciplina e Série\n\n",
  "| Disciplina | Série | Alunos | Taxa de Acerto (%) |\n",
  "|------------|-------|-------:|------------------:|\n"
)

for (i in 1:nrow(desempenho_disc_serie)) {
  analise3_md <- paste0(analise3_md,
    "| ", desempenho_disc_serie$DIS_NOME[i], " | ", 
    desempenho_disc_serie$SER_NOME[i], " | ", 
    format(desempenho_disc_serie$total_alunos[i], big.mark = ","), " | ", 
    desempenho_disc_serie$taxa_acerto_pct[i], "% |\n"
  )
}

analise3_md <- paste0(analise3_md, "\n")
write_md(analise3_md)

# ============================================================================
# 📊 ANÁLISE 4: DESCRITORES MAIS DIFÍCEIS
# ============================================================================

cat("📊 Processando Análise 4: Descritores Mais Difíceis...\n")

# Query para descritores mais difíceis
query_descritores_dificeis <- "
SELECT 
    d.MTI_CODIGO,
    SUBSTR(d.MTI_DESCRITOR, 1, 80) as descritor_resumido,
    COUNT(DISTINCT f.ALU_ID) as total_alunos,
    SUM(f.ACERTO) as total_acertos,
    SUM(f.ERRO) as total_erros,
    ROUND(
        (SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2
    ) as taxa_acerto_pct
FROM fato_resposta_aluno f
JOIN dim_descritor d ON f.MTI_CODIGO = d.MTI_CODIGO
GROUP BY d.MTI_CODIGO, d.MTI_DESCRITOR
HAVING SUM(f.ACERTO + f.ERRO) > 5000
ORDER BY taxa_acerto_pct ASC
"

descritores_dificeis <- dbGetQuery(con, query_descritores_dificeis)

# Escrever seção no Markdown
analise4_md <- paste0(
  "## 📊 Análise 4: Descritores com Maior Dificuldade\n\n",
  "### 🔴 Top 10 Descritores Mais Difíceis\n\n",
  "| Código | Descritor | Taxa de Acerto (%) |\n",
  "|--------|-----------|------------------:|\n"
)

top10_dificeis <- head(descritores_dificeis, 10)
for (i in 1:nrow(top10_dificeis)) {
  analise4_md <- paste0(analise4_md,
    "| `", top10_dificeis$MTI_CODIGO[i], "` | ", 
    top10_dificeis$descritor_resumido[i], " | ", 
    top10_dificeis$taxa_acerto_pct[i], "% |\n"
  )
}

analise4_md <- paste0(analise4_md, "\n")
write_md(analise4_md)

# ============================================================================
# 📊 ANÁLISE 5: COMPARAÇÃO ENTRE TURNOS
# ============================================================================

cat("📊 Processando Análise 5: Comparação entre Turnos...\n")

# Query para comparação entre turnos
query_comparacao_turnos <- "
SELECT 
    f.TUR_PERIODO,
    COUNT(DISTINCT f.ALU_ID) as total_alunos,
    SUM(f.ACERTO) as total_acertos,
    SUM(f.ERRO) as total_erros,
    ROUND(
        (SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2
    ) as taxa_acerto_pct
FROM fato_resposta_aluno f
GROUP BY f.TUR_PERIODO
ORDER BY taxa_acerto_pct DESC
"

comparacao_turnos <- dbGetQuery(con, query_comparacao_turnos)

# Escrever seção no Markdown
analise5_md <- paste0(
  "## 📊 Análise 5: Desempenho por Turno\n\n",
  "| Turno | Alunos | Taxa de Acerto (%) |\n",
  "|-------|-------:|------------------:|\n"
)

for (i in 1:nrow(comparacao_turnos)) {
  analise5_md <- paste0(analise5_md,
    "| ", comparacao_turnos$TUR_PERIODO[i], " | ", 
    format(comparacao_turnos$total_alunos[i], big.mark = ","), " | ", 
    comparacao_turnos$taxa_acerto_pct[i], "% |\n"
  )
}

analise5_md <- paste0(analise5_md, "\n")
write_md(analise5_md)

# ============================================================================
# 📊 ANÁLISE 6: RANKING DE ESCOLAS
# ============================================================================

cat("📊 Processando Análise 6: Ranking de Escolas...\n")

# Query para ranking de escolas
query_ranking_escolas <- "
SELECT 
    e.ESC_NOME,
    f.MUN_NOME,
    COUNT(DISTINCT f.ALU_ID) as total_alunos,
    SUM(f.ACERTO) as total_acertos,
    SUM(f.ERRO) as total_erros,
    ROUND(
        (SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2
    ) as taxa_acerto_pct
FROM fato_resposta_aluno f
JOIN dim_escola e ON f.ESC_INEP = e.ESC_INEP
GROUP BY e.ESC_NOME, f.MUN_NOME
HAVING SUM(f.ACERTO + f.ERRO) > 1000
ORDER BY taxa_acerto_pct DESC
"

ranking_escolas <- dbGetQuery(con, query_ranking_escolas)

# Escrever seção no Markdown
analise6_md <- paste0(
  "## 📊 Análise 6: Ranking de Escolas\n\n",
  "### 🏆 Top 20 Escolas por Taxa de Acerto\n\n",
  "| Escola | Município | Alunos | Taxa de Acerto (%) |\n",
  "|--------|-----------|-------:|------------------:|\n"
)

top20_escolas <- head(ranking_escolas, 20)
for (i in 1:nrow(top20_escolas)) {
  analise6_md <- paste0(analise6_md,
    "| ", top20_escolas$ESC_NOME[i], " | ", 
    top20_escolas$MUN_NOME[i], " | ", 
    format(top20_escolas$total_alunos[i], big.mark = ","), " | ", 
    top20_escolas$taxa_acerto_pct[i], "% |\n"
  )
}

analise6_md <- paste0(analise6_md, "\n")
write_md(analise6_md)

# ============================================================================
# 📊 RESUMO EXECUTIVO
# ============================================================================

cat("📊 Processando Resumo Executivo...\n")

# Estatísticas gerais
total_alunos <- dbGetQuery(con, "SELECT COUNT(DISTINCT ALU_ID) as total FROM fato_resposta_aluno")$total
total_escolas <- dbGetQuery(con, "SELECT COUNT(DISTINCT ESC_INEP) as total FROM fato_resposta_aluno")$total
total_municipios <- dbGetQuery(con, "SELECT COUNT(DISTINCT MUN_NOME) as total FROM fato_resposta_aluno")$total
taxa_geral <- dbGetQuery(con, "SELECT ROUND((SUM(ACERTO) * 100.0) / SUM(ACERTO + ERRO), 2) as taxa FROM fato_resposta_aluno")$taxa

# Escrever resumo executivo
resumo_md <- paste0(
  "## 📊 Resumo Executivo\n\n",
  "### 📈 Indicadores Gerais\n\n",
  "| Indicador | Valor |\n",
  "|-----------|------:|\n",
  "| **Total de Alunos** | ", format(total_alunos, big.mark = ","), " |\n",
  "| **Total de Escolas** | ", format(total_escolas, big.mark = ","), " |\n",
  "| **Total de Municípios** | ", format(total_municipios, big.mark = ","), " |\n",
  "| **Taxa de Acerto Geral** | ", taxa_geral, "% |\n\n",
  "### 🎯 Principais Insights\n\n",
  "1. **Série com mais alunos:** ", alunos_por_serie$SER_NOME[1], " (", format(alunos_por_serie$total_alunos[1], big.mark = ","), " alunos)\n",
  "2. **Município com melhor desempenho:** ", taxa_acerto_municipio$MUN_NOME[1], " (", taxa_acerto_municipio$taxa_acerto_pct[1], "%)\n",
  "3. **Descritor mais difícil:** `", descritores_dificeis$MTI_CODIGO[1], "` (", descritores_dificeis$taxa_acerto_pct[1], "%)\n",
  "4. **Melhor escola:** ", ranking_escolas$ESC_NOME[1], " (", ranking_escolas$taxa_acerto_pct[1], "%)\n\n"
)

write_md(resumo_md)

# ============================================================================
# 📎 SEÇÃO DE ANEXOS
# ============================================================================

anexos_md <- paste0(
  "## 📎 Anexos\n\n",
  "### 📊 Gráficos Gerados\n\n",
  "- `grafico_alunos_por_serie.png` - Distribuição de alunos por série\n",
  "- `grafico_taxa_acerto_municipio.png` - Taxa de acerto por município\n\n",
  "### 💾 Dados Exportados\n\n",
  "Os dados detalhados foram exportados nos seguintes arquivos CSV:\n\n",
  "- `dados_alunos_municipio_serie.csv`\n",
  "- `dados_taxa_acerto_municipio.csv`\n",
  "- `dados_desempenho_disciplina_serie.csv`\n",
  "- `dados_ranking_escolas.csv`\n\n",
  "---\n\n",
  "*Relatório gerado automaticamente pelo Sistema SAEV*\n"
)

write_md(anexos_md)

# ============================================================================
# 💾 SALVAR DADOS COMPLEMENTARES
# ============================================================================

cat("💾 Salvando dados complementares...\n")

# Salvar dados em CSV para análises futuras
write.csv(alunos_mun_serie, "R/dados_alunos_municipio_serie.csv", row.names = FALSE)
write.csv(taxa_acerto_municipio, "R/dados_taxa_acerto_municipio.csv", row.names = FALSE)
write.csv(desempenho_disc_serie, "R/dados_desempenho_disciplina_serie.csv", row.names = FALSE)
write.csv(ranking_escolas, "R/dados_ranking_escolas.csv", row.names = FALSE)

# ============================================================================
# 🔚 FINALIZAÇÃO
# ============================================================================

# Fechar conexão
dbDisconnect(con)

cat("✅ Análise concluída com sucesso!\n")
cat("📁 Arquivos gerados:\n")
cat("   📄 Relatório Markdown:", relatorio_file, "\n")
cat("   📊 Gráficos: R/grafico_*.png\n")
cat("   💾 Dados: R/dados_*.csv\n")
cat("🎉 Relatório Markdown pronto para visualização!\n")

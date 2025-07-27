# 📊 Análise de Dados SAEV - Modelo Star Schema
# Script R para explorar o banco DuckDB com dados educacionais
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
  "plotly",        # Gráficos interativos
  "corrplot",      # Matriz de correlação
  "RColorBrewer",  # Paletas de cores
  "gridExtra"      # Arranjo de gráficos
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
  library(plotly)
  library(corrplot)
  library(RColorBrewer)
  library(gridExtra)
})

cat("✅ Pacotes carregados com sucesso!\n\n")

# ============================================================================
# 🔌 CONEXÃO COM O BANCO DUCKDB
# ============================================================================

cat("🔌 Conectando ao banco DuckDB...\n")

# Caminho do banco de dados
db_path <- "../db/avaliacao_prod.duckdb"

# Verificar se o banco existe
if (!file.exists(db_path)) {
  stop("❌ Erro: Banco de dados não encontrado em: ", db_path, 
       "\n   Execute o ETL primeiro: python run_etl.py full")
}

# Conectar ao DuckDB
con <- dbConnect(duckdb::duckdb(), dbdir = db_path)

cat("✅ Conectado ao banco:", db_path, "\n\n")

# ============================================================================
# 📋 VERIFICAÇÃO DA ESTRUTURA DO BANCO
# ============================================================================

cat("📋 === ESTRUTURA DO BANCO DE DADOS ===\n")

# Listar tabelas
tabelas <- dbListTables(con)
cat("📁 Tabelas encontradas:", paste(tabelas, collapse = ", "), "\n\n")

# Função para obter estatísticas das tabelas
get_table_stats <- function(table_name) {
  query <- paste("SELECT COUNT(*) as registros FROM", table_name)
  result <- dbGetQuery(con, query)
  return(result$registros)
}

# Estatísticas gerais
cat("📊 Estatísticas Gerais:\n")
for (tabela in tabelas) {
  registros <- get_table_stats(tabela)
  cat(sprintf("   %-20s: %s registros\n", tabela, format(registros, big.mark = ",")))
}
cat("\n")

# ============================================================================
# 📊 ANÁLISE 1: NÚMERO DE ALUNOS POR MUNICÍPIO E SÉRIE
# ============================================================================

cat("📊 === ANÁLISE 1: ALUNOS POR MUNICÍPIO E SÉRIE ===\n")

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

# Exibir top 10
cat("🏆 Top 10 Município/Série por número de alunos:\n")
print(kable(head(alunos_mun_serie, 10), format = "simple"))
cat("\n")

# Gráfico: Alunos por Série (agregado)
alunos_por_serie <- alunos_mun_serie %>%
  group_by(SER_NOME) %>%
  summarise(total_alunos = sum(total_alunos)) %>%
  arrange(desc(total_alunos))

p1 <- ggplot(alunos_por_serie, aes(x = reorder(SER_NOME, total_alunos), y = total_alunos)) +
  geom_col(fill = "steelblue", alpha = 0.8) +
  coord_flip() +
  labs(
    title = "📊 Distribuição de Alunos por Série",
    x = "Série",
    y = "Número de Alunos"
  ) +
  scale_y_continuous(labels = comma_format()) +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5))

print(p1)
ggsave("R/grafico_alunos_por_serie.png", p1, width = 10, height = 6, dpi = 300)

# ============================================================================
# 📊 ANÁLISE 2: TAXA DE ACERTO POR MUNICÍPIO
# ============================================================================

cat("📊 === ANÁLISE 2: TAXA DE ACERTO POR MUNICÍPIO ===\n")

# Query para taxa de acerto por município
query_taxa_acerto_municipio <- "
SELECT 
    f.MUN_NOME,
    COUNT(DISTINCT f.ALU_ID) as total_alunos,
    SUM(f.ACERTO) as total_acertos,
    SUM(f.ERRO) as total_erros,
    SUM(f.ACERTO + f.ERRO) as total_questoes,
    ROUND(
        (SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2
    ) as taxa_acerto_pct
FROM fato_resposta_aluno f
GROUP BY f.MUN_NOME
HAVING SUM(f.ACERTO + f.ERRO) > 1000  -- Filtrar municípios com dados suficientes
ORDER BY taxa_acerto_pct DESC
"

taxa_acerto_municipio <- dbGetQuery(con, query_taxa_acerto_municipio)

# Exibir resultados
cat("🏆 Taxa de Acerto por Município (Top 15):\n")
print(kable(head(taxa_acerto_municipio, 15), format = "simple"))
cat("\n")

# Gráfico: Taxa de acerto por município (Top 20)
top_municipios <- head(taxa_acerto_municipio, 20)

p2 <- ggplot(top_municipios, aes(x = reorder(MUN_NOME, taxa_acerto_pct), y = taxa_acerto_pct)) +
  geom_col(fill = "darkgreen", alpha = 0.8) +
  coord_flip() +
  labs(
    title = "📊 Taxa de Acerto por Município (Top 20)",
    x = "Município",
    y = "Taxa de Acerto (%)"
  ) +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5))

print(p2)
ggsave("R/grafico_taxa_acerto_municipio.png", p2, width = 12, height = 8, dpi = 300)

# ============================================================================
# 📊 ANÁLISE 3: DESEMPENHO POR DISCIPLINA E SÉRIE
# ============================================================================

cat("📊 === ANÁLISE 3: DESEMPENHO POR DISCIPLINA E SÉRIE ===\n")

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

# Exibir resultados
cat("📚 Desempenho por Disciplina e Série:\n")
print(kable(desempenho_disc_serie, format = "simple"))
cat("\n")

# Gráfico: Heatmap de desempenho
p3 <- ggplot(desempenho_disc_serie, aes(x = SER_NOME, y = DIS_NOME, fill = taxa_acerto_pct)) +
  geom_tile(color = "white") +
  scale_fill_gradient2(
    low = "red", mid = "yellow", high = "green",
    midpoint = 50, name = "Taxa de\nAcerto (%)"
  ) +
  labs(
    title = "📊 Heatmap: Taxa de Acerto por Disciplina e Série",
    x = "Série",
    y = "Disciplina"
  ) +
  theme_minimal() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1),
    plot.title = element_text(hjust = 0.5)
  ) +
  geom_text(aes(label = paste0(taxa_acerto_pct, "%")), size = 3)

print(p3)
ggsave("R/grafico_heatmap_disciplina_serie.png", p3, width = 12, height = 6, dpi = 300)

# ============================================================================
# 📊 ANÁLISE 4: TOP DESCRITORES COM MAIOR DIFICULDADE
# ============================================================================

cat("📊 === ANÁLISE 4: DESCRITORES COM MAIOR DIFICULDADE ===\n")

# Query para descritores mais difíceis
query_descritores_dificeis <- "
SELECT 
    d.MTI_CODIGO,
    LEFT(d.MTI_DESCRITOR, 80) as descritor_resumido,
    COUNT(DISTINCT f.ALU_ID) as total_alunos,
    SUM(f.ACERTO) as total_acertos,
    SUM(f.ERRO) as total_erros,
    ROUND(
        (SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2
    ) as taxa_acerto_pct
FROM fato_resposta_aluno f
JOIN dim_descritor d ON f.MTI_CODIGO = d.MTI_CODIGO
GROUP BY d.MTI_CODIGO, d.MTI_DESCRITOR
HAVING SUM(f.ACERTO + f.ERRO) > 5000  -- Filtrar descritores com dados suficientes
ORDER BY taxa_acerto_pct ASC
"

descritores_dificeis <- dbGetQuery(con, query_descritores_dificeis)

# Exibir top 10 mais difíceis
cat("🔴 Top 10 Descritores Mais Difíceis:\n")
print(kable(head(descritores_dificeis, 10), format = "simple"))
cat("\n")

# Gráfico: Descritores mais difíceis
top_dificeis <- head(descritores_dificeis, 15)

p4 <- ggplot(top_dificeis, aes(x = reorder(MTI_CODIGO, taxa_acerto_pct), y = taxa_acerto_pct)) +
  geom_col(fill = "darkred", alpha = 0.8) +
  coord_flip() +
  labs(
    title = "📊 Top 15 Descritores Mais Difíceis",
    x = "Código do Descritor",
    y = "Taxa de Acerto (%)"
  ) +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5))

print(p4)
ggsave("R/grafico_descritores_dificeis.png", p4, width = 10, height = 8, dpi = 300)

# ============================================================================
# 📊 ANÁLISE 5: ANÁLISE TEMPORAL (ANO DA AVALIAÇÃO)
# ============================================================================

cat("📊 === ANÁLISE 5: ANÁLISE TEMPORAL ===\n")

# Query para evolução temporal
query_evolucao_temporal <- "
SELECT 
    f.AVA_ANO,
    COUNT(DISTINCT f.ALU_ID) as total_alunos,
    SUM(f.ACERTO) as total_acertos,
    SUM(f.ERRO) as total_erros,
    ROUND(
        (SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2
    ) as taxa_acerto_pct
FROM fato_resposta_aluno f
GROUP BY f.AVA_ANO
ORDER BY f.AVA_ANO
"

evolucao_temporal <- dbGetQuery(con, query_evolucao_temporal)

# Exibir resultados
cat("📅 Evolução Temporal do Desempenho:\n")
print(kable(evolucao_temporal, format = "simple"))
cat("\n")

# Gráfico: Evolução temporal
p5 <- ggplot(evolucao_temporal, aes(x = as.factor(AVA_ANO), y = taxa_acerto_pct)) +
  geom_line(group = 1, color = "blue", size = 1.2) +
  geom_point(color = "darkblue", size = 3) +
  labs(
    title = "📊 Evolução da Taxa de Acerto ao Longo dos Anos",
    x = "Ano da Avaliação",
    y = "Taxa de Acerto (%)"
  ) +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5))

print(p5)
ggsave("R/grafico_evolucao_temporal.png", p5, width = 10, height = 6, dpi = 300)

# ============================================================================
# 📊 ANÁLISE 6: COMPARAÇÃO ENTRE TURNOS
# ============================================================================

cat("📊 === ANÁLISE 6: COMPARAÇÃO ENTRE TURNOS ===\n")

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

# Exibir resultados
cat("🌅 Comparação de Desempenho por Turno:\n")
print(kable(comparacao_turnos, format = "simple"))
cat("\n")

# Gráfico: Comparação turnos
p6 <- ggplot(comparacao_turnos, aes(x = TUR_PERIODO, y = taxa_acerto_pct, fill = TUR_PERIODO)) +
  geom_col(alpha = 0.8) +
  scale_fill_brewer(palette = "Set2") +
  labs(
    title = "📊 Taxa de Acerto por Turno",
    x = "Turno",
    y = "Taxa de Acerto (%)"
  ) +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5),
    legend.position = "none"
  ) +
  geom_text(aes(label = paste0(taxa_acerto_pct, "%")), vjust = -0.5)

print(p6)
ggsave("R/grafico_comparacao_turnos.png", p6, width = 8, height = 6, dpi = 300)

# ============================================================================
# 📊 ANÁLISE 7: RANKING DE ESCOLAS
# ============================================================================

cat("📊 === ANÁLISE 7: RANKING DE ESCOLAS ===\n")

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
HAVING SUM(f.ACERTO + f.ERRO) > 1000  -- Filtrar escolas com dados suficientes
ORDER BY taxa_acerto_pct DESC
"

ranking_escolas <- dbGetQuery(con, query_ranking_escolas)

# Exibir top 20 escolas
cat("🏆 Top 20 Escolas por Taxa de Acerto:\n")
print(kable(head(ranking_escolas, 20), format = "simple"))
cat("\n")

# ============================================================================
# 📊 RESUMO EXECUTIVO
# ============================================================================

cat("📊 === RESUMO EXECUTIVO ===\n")

# Estatísticas gerais
total_alunos <- dbGetQuery(con, "SELECT COUNT(DISTINCT ALU_ID) as total FROM fato_resposta_aluno")$total
total_escolas <- dbGetQuery(con, "SELECT COUNT(DISTINCT ESC_INEP) as total FROM fato_resposta_aluno")$total
total_municipios <- dbGetQuery(con, "SELECT COUNT(DISTINCT MUN_NOME) as total FROM fato_resposta_aluno")$total
taxa_geral <- dbGetQuery(con, "SELECT ROUND((SUM(ACERTO) * 100.0) / SUM(ACERTO + ERRO), 2) as taxa FROM fato_resposta_aluno")$taxa

cat("📈 INDICADORES GERAIS:\n")
cat(sprintf("   👥 Total de Alunos: %s\n", format(total_alunos, big.mark = ",")))
cat(sprintf("   🏫 Total de Escolas: %s\n", format(total_escolas, big.mark = ",")))
cat(sprintf("   🏛️  Total de Municípios: %s\n", format(total_municipios, big.mark = ",")))
cat(sprintf("   ✅ Taxa de Acerto Geral: %.2f%%\n", taxa_geral))
cat("\n")

cat("🎯 PRINCIPAIS INSIGHTS:\n")
cat("   1. Série com mais alunos:", alunos_por_serie$SER_NOME[1], "\n")
cat("   2. Município com melhor desempenho:", taxa_acerto_municipio$MUN_NOME[1], 
    "(", taxa_acerto_municipio$taxa_acerto_pct[1], "%)\n")
cat("   3. Descritor mais difícil:", descritores_dificeis$MTI_CODIGO[1],
    "(", descritores_dificeis$taxa_acerto_pct[1], "%)\n")
cat("   4. Melhor escola:", ranking_escolas$ESC_NOME[1],
    "(", ranking_escolas$taxa_acerto_pct[1], "%)\n")
cat("\n")

# ============================================================================
# 🔚 FINALIZAÇÃO
# ============================================================================

cat("💾 Salvando dados processados...\n")

# Salvar dados em CSV para análises futuras
write.csv(alunos_mun_serie, "R/dados_alunos_municipio_serie.csv", row.names = FALSE)
write.csv(taxa_acerto_municipio, "R/dados_taxa_acerto_municipio.csv", row.names = FALSE)
write.csv(desempenho_disc_serie, "R/dados_desempenho_disciplina_serie.csv", row.names = FALSE)
write.csv(ranking_escolas, "R/dados_ranking_escolas.csv", row.names = FALSE)

# Fechar conexão
dbDisconnect(con)

cat("✅ Análise concluída com sucesso!\n")
cat("📁 Arquivos gerados:\n")
cat("   📊 Gráficos: R/grafico_*.png\n")
cat("   💾 Dados: R/dados_*.csv\n")
cat("🎉 Explore os resultados nos arquivos gerados!\n")

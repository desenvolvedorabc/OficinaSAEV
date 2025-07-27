# 📊 Painel de Análises SAEV - Dashboard em R
# Script para construir painel com análises gerais sobre taxa de acerto
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
    install.packages(new_packages, dependencies = TRUE)
  }
}

# Lista de pacotes necessários
required_packages <- c(
  "DBI",           # Interface de banco de dados
  "duckdb",        # Conector DuckDB
  "dplyr",         # Manipulação de dados
  "ggplot2",       # Visualizações
  "plotly",        # Gráficos interativos
  "DT",            # Tabelas interativas
  "htmlwidgets",   # Widgets HTML
  "gridExtra",     # Layout de gráficos
  "scales",        # Formatação de escalas
  "viridis",       # Paleta de cores
  "corrplot",      # Matriz de correlação
  "leaflet"        # Mapas (se necessário)
)

# Instalar pacotes que não estão disponíveis
suppressPackageStartupMessages({
  install_if_missing(required_packages)
  
  # Carregar apenas pacotes essenciais
  library(DBI)
  library(duckdb)
  library(dplyr)
  library(ggplot2)
  library(gridExtra)
  library(scales)
  library(viridis)
})

cat("📊 === PAINEL DE ANÁLISES SAEV ===\n\n")

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
# 📊 FUNÇÃO PARA CRIAR DIRETÓRIO DE SAÍDA
# ============================================================================

# Criar diretório para salvar os gráficos
output_dir <- "R/painel_graficos"
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
  cat("📁 Diretório criado:", output_dir, "\n")
}

# ============================================================================
# 📈 PAINEL 1: TAXA DE ACERTO POR DISCIPLINA
# ============================================================================

cat("📊 === PAINEL 1: ANÁLISE POR DISCIPLINA ===\n")

# Query para taxa de acerto por disciplina
query_disciplina <- "
SELECT 
    f.DIS_NOME,
    COUNT(DISTINCT f.ALU_ID) as total_alunos,
    SUM(f.ACERTO) as total_acertos,
    SUM(f.ERRO) as total_erros,
    SUM(f.ACERTO + f.ERRO) as total_questoes,
    ROUND(
        (SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2
    ) as taxa_acerto_pct
FROM fato_resposta_aluno f
GROUP BY f.DIS_NOME
ORDER BY taxa_acerto_pct DESC
"

dados_disciplina <- dbGetQuery(con, query_disciplina)

# Exibir resultados
cat("📚 Taxa de Acerto por Disciplina:\n")
print(dados_disciplina)
cat("\n")

# Gráfico 1: Taxa de acerto por disciplina
p1 <- ggplot(dados_disciplina, aes(x = reorder(DIS_NOME, taxa_acerto_pct), y = taxa_acerto_pct)) +
  geom_col(fill = "steelblue", alpha = 0.8) +
  geom_text(aes(label = paste0(taxa_acerto_pct, "%")), 
            hjust = -0.1, size = 3.5, color = "black") +
  coord_flip() +
  labs(
    title = "Taxa de Acerto por Disciplina",
    subtitle = paste("Total de", format(sum(dados_disciplina$total_alunos), big.mark = ","), "alunos"),
    x = "Disciplina",
    y = "Taxa de Acerto (%)",
    caption = "Fonte: Sistema SAEV - DuckDB"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 12),
    axis.text = element_text(size = 10)
  ) +
  ylim(0, max(dados_disciplina$taxa_acerto_pct) * 1.1)

# Salvar gráfico
ggsave(file.path(output_dir, "01_taxa_acerto_disciplina.png"), p1, 
       width = 10, height = 6, dpi = 300)

# ============================================================================
# 📈 PAINEL 2: TAXA DE ACERTO POR TESTE
# ============================================================================

cat("📊 === PAINEL 2: ANÁLISE POR TESTE ===\n")

# Query para taxa de acerto por teste
query_teste <- "
SELECT 
    f.TES_NOME,
    f.DIS_NOME,
    COUNT(DISTINCT f.ALU_ID) as total_alunos,
    SUM(f.ACERTO) as total_acertos,
    SUM(f.ERRO) as total_erros,
    ROUND(
        (SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2
    ) as taxa_acerto_pct
FROM fato_resposta_aluno f
GROUP BY f.TES_NOME, f.DIS_NOME
HAVING SUM(f.ACERTO + f.ERRO) > 10000  -- Filtrar testes com dados suficientes
ORDER BY taxa_acerto_pct DESC
"

dados_teste <- dbGetQuery(con, query_teste)

# Exibir resultados
cat("📝 Taxa de Acerto por Teste (Top 15):\n")
print(head(dados_teste, 15))
cat("\n")

# Gráfico 2: Taxa de acerto por teste (top 15)
top15_testes <- head(dados_teste, 15)

p2 <- ggplot(top15_testes, aes(x = reorder(paste(TES_NOME, "-", DIS_NOME), taxa_acerto_pct), 
                               y = taxa_acerto_pct, fill = DIS_NOME)) +
  geom_col(alpha = 0.8) +
  geom_text(aes(label = paste0(taxa_acerto_pct, "%")), 
            hjust = -0.1, size = 3, color = "black") +
  coord_flip() +
  scale_fill_viridis_d(name = "Disciplina") +
  labs(
    title = "Top 15 Testes por Taxa de Acerto",
    subtitle = "Filtrados testes com mais de 10.000 questões respondidas",
    x = "Teste - Disciplina",
    y = "Taxa de Acerto (%)",
    caption = "Fonte: Sistema SAEV - DuckDB"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 12),
    axis.text = element_text(size = 9),
    legend.position = "bottom"
  ) +
  ylim(0, max(top15_testes$taxa_acerto_pct) * 1.1)

# Salvar gráfico
ggsave(file.path(output_dir, "02_taxa_acerto_teste.png"), p2, 
       width = 12, height = 8, dpi = 300)

# ============================================================================
# 📈 PAINEL 3: TAXA DE ACERTO POR MUNICÍPIO (TOP 20)
# ============================================================================

cat("📊 === PAINEL 3: ANÁLISE POR MUNICÍPIO ===\n")

# Query para taxa de acerto por município
query_municipio <- "
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
HAVING SUM(f.ACERTO + f.ERRO) > 5000  -- Filtrar municípios com dados suficientes
ORDER BY taxa_acerto_pct DESC
LIMIT 20
"

dados_municipio <- dbGetQuery(con, query_municipio)

# Exibir resultados
cat("🏙️ Top 20 Municípios por Taxa de Acerto:\n")
print(dados_municipio)
cat("\n")

# Gráfico 3: Taxa de acerto por município (top 20)
p3 <- ggplot(dados_municipio, aes(x = reorder(MUN_NOME, taxa_acerto_pct), y = taxa_acerto_pct)) +
  geom_col(fill = "forestgreen", alpha = 0.8) +
  geom_text(aes(label = paste0(taxa_acerto_pct, "%")), 
            hjust = -0.1, size = 3, color = "black") +
  coord_flip() +
  labs(
    title = "Top 20 Municípios por Taxa de Acerto",
    subtitle = "Filtrados municípios com mais de 5.000 questões respondidas",
    x = "Município",
    y = "Taxa de Acerto (%)",
    caption = "Fonte: Sistema SAEV - DuckDB"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 12),
    axis.text = element_text(size = 10)
  ) +
  ylim(0, max(dados_municipio$taxa_acerto_pct) * 1.1)

# Salvar gráfico
ggsave(file.path(output_dir, "03_taxa_acerto_municipio.png"), p3, 
       width = 12, height = 8, dpi = 300)

# ============================================================================
# 📈 PAINEL 4: TAXA DE ACERTO POR ESCOLA (TOP 20)
# ============================================================================

cat("📊 === PAINEL 4: ANÁLISE POR ESCOLA ===\n")

# Query para taxa de acerto por escola
query_escola <- "
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
LIMIT 20
"

dados_escola <- dbGetQuery(con, query_escola)

# Exibir resultados
cat("🏫 Top 20 Escolas por Taxa de Acerto:\n")
print(dados_escola)
cat("\n")

# Gráfico 4: Taxa de acerto por escola (top 20)
p4 <- ggplot(dados_escola, aes(x = reorder(paste(ESC_NOME, "-", MUN_NOME), taxa_acerto_pct), 
                               y = taxa_acerto_pct)) +
  geom_col(fill = "orange", alpha = 0.8) +
  geom_text(aes(label = paste0(taxa_acerto_pct, "%")), 
            hjust = -0.1, size = 3, color = "black") +
  coord_flip() +
  labs(
    title = "Top 20 Escolas por Taxa de Acerto",
    subtitle = "Filtradas escolas com mais de 1.000 questões respondidas",
    x = "Escola - Município",
    y = "Taxa de Acerto (%)",
    caption = "Fonte: Sistema SAEV - DuckDB"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 12),
    axis.text = element_text(size = 9)
  ) +
  ylim(0, max(dados_escola$taxa_acerto_pct) * 1.1)

# Salvar gráfico
ggsave(file.path(output_dir, "04_taxa_acerto_escola.png"), p4, 
       width = 12, height = 10, dpi = 300)

# ============================================================================
# 📈 PAINEL 5: ANÁLISE CRUZADA - DISCIPLINA vs SÉRIE
# ============================================================================

cat("📊 === PAINEL 5: ANÁLISE DISCIPLINA vs SÉRIE ===\n")

# Query para análise cruzada disciplina vs série
query_disc_serie <- "
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

dados_disc_serie <- dbGetQuery(con, query_disc_serie)

# Exibir resultados
cat("📚 Taxa de Acerto por Disciplina e Série:\n")
print(dados_disc_serie)
cat("\n")

# Gráfico 5: Heatmap disciplina vs série
p5 <- ggplot(dados_disc_serie, aes(x = SER_NOME, y = DIS_NOME, fill = taxa_acerto_pct)) +
  geom_tile(color = "white", size = 0.5) +
  geom_text(aes(label = paste0(taxa_acerto_pct, "%")), color = "white", size = 3, fontface = "bold") +
  scale_fill_viridis_c(name = "Taxa de\nAcerto (%)", option = "plasma") +
  labs(
    title = "Heatmap: Taxa de Acerto por Disciplina e Série",
    subtitle = "Visualização da performance acadêmica por disciplina e série",
    x = "Série",
    y = "Disciplina",
    caption = "Fonte: Sistema SAEV - DuckDB"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 12),
    axis.text.x = element_text(angle = 45, hjust = 1),
    axis.text = element_text(size = 10),
    legend.position = "right"
  )

# Salvar gráfico
ggsave(file.path(output_dir, "05_heatmap_disciplina_serie.png"), p5, 
       width = 12, height = 6, dpi = 300)

# ============================================================================
# 📈 PAINEL 6: DISTRIBUIÇÃO DE ALUNOS POR SÉRIE E TURNO
# ============================================================================

cat("📊 === PAINEL 6: DISTRIBUIÇÃO POR SÉRIE E TURNO ===\n")

# Query para distribuição por série e turno
query_serie_turno <- "
SELECT 
    f.SER_NOME,
    f.TUR_PERIODO,
    COUNT(DISTINCT f.ALU_ID) as total_alunos,
    ROUND(
        (SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2
    ) as taxa_acerto_pct
FROM fato_resposta_aluno f
GROUP BY f.SER_NOME, f.TUR_PERIODO
ORDER BY f.SER_NOME, f.TUR_PERIODO
"

dados_serie_turno <- dbGetQuery(con, query_serie_turno)

# Exibir resultados
cat("🕐 Distribuição por Série e Turno:\n")
print(dados_serie_turno)
cat("\n")

# Gráfico 6: Distribuição de alunos por série e turno
p6a <- ggplot(dados_serie_turno, aes(x = SER_NOME, y = total_alunos, fill = TUR_PERIODO)) +
  geom_col(position = "dodge", alpha = 0.8) +
  geom_text(aes(label = format(total_alunos, big.mark = ",")), 
            position = position_dodge(width = 0.9), vjust = -0.5, size = 3) +
  scale_fill_viridis_d(name = "Turno") +
  labs(
    title = "Distribuição de Alunos por Série e Turno",
    subtitle = "Número de alunos por série em cada turno",
    x = "Série",
    y = "Número de Alunos",
    caption = "Fonte: Sistema SAEV - DuckDB"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 12),
    axis.text.x = element_text(angle = 45, hjust = 1),
    axis.text = element_text(size = 10),
    legend.position = "bottom"
  )

# Gráfico 6b: Taxa de acerto por série e turno
p6b <- ggplot(dados_serie_turno, aes(x = SER_NOME, y = taxa_acerto_pct, fill = TUR_PERIODO)) +
  geom_col(position = "dodge", alpha = 0.8) +
  geom_text(aes(label = paste0(taxa_acerto_pct, "%")), 
            position = position_dodge(width = 0.9), vjust = -0.5, size = 3) +
  scale_fill_viridis_d(name = "Turno") +
  labs(
    title = "Taxa de Acerto por Série e Turno",
    subtitle = "Performance acadêmica por série em cada turno",
    x = "Série",
    y = "Taxa de Acerto (%)",
    caption = "Fonte: Sistema SAEV - DuckDB"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 12),
    axis.text.x = element_text(angle = 45, hjust = 1),
    axis.text = element_text(size = 10),
    legend.position = "bottom"
  )

# Salvar gráficos
ggsave(file.path(output_dir, "06a_distribuicao_serie_turno.png"), p6a, 
       width = 12, height = 8, dpi = 300)
ggsave(file.path(output_dir, "06b_taxa_acerto_serie_turno.png"), p6b, 
       width = 12, height = 8, dpi = 300)

# ============================================================================
# 📈 PAINEL 7: INDICADORES GERAIS DO SISTEMA
# ============================================================================

cat("📊 === PAINEL 7: INDICADORES GERAIS ===\n")

# Consultas para indicadores gerais
total_alunos <- dbGetQuery(con, "SELECT COUNT(DISTINCT ALU_ID) as total FROM fato_resposta_aluno")$total
total_escolas <- dbGetQuery(con, "SELECT COUNT(DISTINCT ESC_INEP) as total FROM fato_resposta_aluno")$total
total_municipios <- dbGetQuery(con, "SELECT COUNT(DISTINCT MUN_NOME) as total FROM fato_resposta_aluno")$total
total_questoes <- dbGetQuery(con, "SELECT SUM(ACERTO + ERRO) as total FROM fato_resposta_aluno")$total
taxa_geral <- dbGetQuery(con, "SELECT ROUND((SUM(ACERTO) * 100.0) / SUM(ACERTO + ERRO), 2) as taxa FROM fato_resposta_aluno")$taxa

# Criar dataframe com indicadores
indicadores <- data.frame(
  Indicador = c("Total de Alunos", "Total de Escolas", "Total de Municípios", 
                "Total de Questões", "Taxa de Acerto Geral"),
  Valor = c(format(total_alunos, big.mark = ","),
            format(total_escolas, big.mark = ","),
            format(total_municipios, big.mark = ","),
            format(total_questoes, big.mark = ","),
            paste0(taxa_geral, "%")),
  stringsAsFactors = FALSE
)

# Exibir indicadores
cat("📈 INDICADORES GERAIS DO SISTEMA:\n")
print(indicadores)
cat("\n")

# ============================================================================
# 📊 EXPORTAR DADOS PARA ANÁLISES ADICIONAIS
# ============================================================================

cat("📊 === EXPORTANDO DADOS PARA CSV ===\n")

# Criar diretório para CSVs
csv_dir <- "R/painel_dados"
if (!dir.exists(csv_dir)) {
  dir.create(csv_dir, recursive = TRUE)
  cat("📁 Diretório criado:", csv_dir, "\n")
}

# Exportar dados
write.csv(dados_disciplina, file.path(csv_dir, "painel_disciplinas.csv"), row.names = FALSE)
write.csv(dados_teste, file.path(csv_dir, "painel_testes.csv"), row.names = FALSE)
write.csv(dados_municipio, file.path(csv_dir, "painel_municipios.csv"), row.names = FALSE)
write.csv(dados_escola, file.path(csv_dir, "painel_escolas.csv"), row.names = FALSE)
write.csv(dados_disc_serie, file.path(csv_dir, "painel_disciplina_serie.csv"), row.names = FALSE)
write.csv(dados_serie_turno, file.path(csv_dir, "painel_serie_turno.csv"), row.names = FALSE)
write.csv(indicadores, file.path(csv_dir, "painel_indicadores_gerais.csv"), row.names = FALSE)

cat("💾 Dados exportados para:", csv_dir, "\n")

# ============================================================================
# 🎯 RESUMO FINAL
# ============================================================================

cat("\n📊 === RESUMO DO PAINEL DE ANÁLISES ===\n")
cat("🎯 Análises Realizadas:\n")
cat("   1. Taxa de Acerto por Disciplina\n")
cat("   2. Taxa de Acerto por Teste (Top 15)\n")
cat("   3. Taxa de Acerto por Município (Top 20)\n")
cat("   4. Taxa de Acerto por Escola (Top 20)\n")
cat("   5. Heatmap Disciplina vs Série\n")
cat("   6. Distribuição por Série e Turno\n")
cat("   7. Indicadores Gerais do Sistema\n\n")

cat("📁 Arquivos Gerados:\n")
cat("   - Gráficos salvos em:", output_dir, "\n")
cat("   - Dados CSV salvos em:", csv_dir, "\n\n")

cat("📈 Indicadores Principais:\n")
cat(sprintf("   👥 Total de Alunos: %s\n", format(total_alunos, big.mark = ",")))
cat(sprintf("   🏫 Total de Escolas: %s\n", format(total_escolas, big.mark = ",")))
cat(sprintf("   🏙️ Total de Municípios: %s\n", format(total_municipios, big.mark = ",")))
cat(sprintf("   📝 Total de Questões: %s\n", format(total_questoes, big.mark = ",")))
cat(sprintf("   🎯 Taxa de Acerto Geral: %s%%\n", taxa_geral))

# Fechar conexão
dbDisconnect(con)

cat("\n✅ Painel de análises gerado com sucesso!\n")
cat("📊 Execute: ls -la", output_dir, "para ver os gráficos gerados\n")

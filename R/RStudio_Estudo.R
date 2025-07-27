# Instale se necessário:
# install.packages("DBI")
# install.packages("duckdb")
# install.packages("dplyr")
# install.packages("ggplot2")

library(DBI)
library(duckdb)
library(dplyr)
library(ggplot2)

# Caminho do banco DuckDB
db_path <- "/Users/rcaratti/Desktop/ABC/SAEV/OficinaSAEV/db/avaliacao_prod.duckdb"
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = TRUE)

# Carregando as tabelas necessárias
fato <- dbReadTable(con, "fato_resposta_aluno")
escola <- dbReadTable(con, "dim_escola")
descritor <- dbReadTable(con, "dim_descritor")

# Junta tabelas para análises detalhadas
dados <- fato %>%
  left_join(escola, by = "ESC_INEP") %>%
  left_join(descritor, by = "MTI_CODIGO")

# Percentual de acertos por município
muni_perf <- dados %>%
  group_by(MUN_NOME) %>%
  summarise(
    total_acertos = sum(ACERTO, na.rm = TRUE),
    total_questoes = sum(ACERTO + ERRO, na.rm = TRUE),
    perc_acerto = 100 * total_acertos / total_questoes
  ) %>%
  arrange(desc(perc_acerto))

print("Top 10 Municípios:")
print(head(muni_perf, 10))
# Veja a tabela completa no RStudio com:
# View(muni_perf)

# Percentual de acertos por escola
esc_perf <- dados %>%
  group_by(ESC_INEP, ESC_NOME) %>%
  summarise(
    total_acertos = sum(ACERTO, na.rm = TRUE),
    total_questoes = sum(ACERTO + ERRO, na.rm = TRUE),
    perc_acerto = 100 * total_acertos / total_questoes
  ) %>%
  arrange(desc(perc_acerto))

print("Top 10 Escolas:")
print(head(esc_perf, 10))
# View(esc_perf)

# Percentual de acertos por descritor (questão/habilidade)
desc_perf <- dados %>%
  group_by(MTI_CODIGO, MTI_DESCRITOR) %>%
  summarise(
    total_acertos = sum(ACERTO, na.rm = TRUE),
    total_questoes = sum(ACERTO + ERRO, na.rm = TRUE),
    perc_acerto = 100 * total_acertos / total_questoes
  ) %>%
  arrange(perc_acerto)

print("5 descritores mais difíceis:")
print(head(desc_perf, 5))
print("5 descritores mais fáceis:")
print(tail(desc_perf, 5))

# Gráfico: Percentual de acertos por descritor (as 30 mais frequentes, para visualização)
top_desc <- desc_perf %>%
  arrange(perc_acerto) %>%
  tail(30)

ggplot(top_desc, aes(x = reorder(MTI_DESCRITOR, perc_acerto), y = perc_acerto)) +
  geom_bar(stat = "identity", fill = "steelblue") +
  coord_flip() +
  labs(title = "Percentual de Acertos (30 principais descritores)",
       x = "Descritor",
       y = "Percentual de Acertos") +
  theme_minimal()

# Escolas abaixo da média estadual
media_estadual <- mean(esc_perf$perc_acerto, na.rm = TRUE)
escolas_baixo <- esc_perf %>%
  filter(perc_acerto < media_estadual)

print("Escolas abaixo da média estadual:")
print(escolas_baixo)
# View(escolas_baixo)

# Recomendações automáticas
cat("\n==== Recomendações ====\n")
cat(sprintf("A média estadual de acertos é %.2f%%.\n", media_estadual))
cat("Descritores mais críticos (baixa performance):\n")
print(head(desc_perf, 5))
cat("Sugestão: Promover formação continuada de professores nesses descritores, oferecer reforço escolar direcionado, revisar materiais didáticos e monitorar avanços após intervenções.\n")

# Encerrar conexão
dbDisconnect(con, shutdown=TRUE)

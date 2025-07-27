# Instale os pacotes se necessário:
# install.packages("DBI")
# install.packages("duckdb")
# install.packages("dplyr")
# install.packages("ggplot2")

library(DBI)
library(duckdb)
library(dplyr)
library(ggplot2)

# Caminho para o banco DuckDB já atualizado
db_path <- "db/avaliacao_prod.duckdb"

# Conectando ao banco DuckDB
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

print(head(muni_perf, 10)) # Top 10 municípios

# Percentual de acertos por escola
esc_perf <- dados %>%
  group_by(ESC_INEP, ESC_NOME) %>%
  summarise(
    total_acertos = sum(ACERTO, na.rm = TRUE),
    total_questoes = sum(ACERTO + ERRO, na.rm = TRUE),
    perc_acerto = 100 * total_acertos / total_questoes
  ) %>%
  arrange(desc(perc_acerto))

print(head(esc_perf, 10)) # Top 10 escolas

# Percentual de acertos por descritor (questão/habilidade)
desc_perf <- dados %>%
  group_by(MTI_CODIGO, MTI_DESCRITOR) %>%
  summarise(
    total_acertos = sum(ACERTO, na.rm = TRUE),
    total_questoes = sum(ACERTO + ERRO, na.rm = TRUE),
    perc_acerto = 100 * total_acertos / total_questoes
  ) %>%
  arrange(perc_acerto)

print(head(desc_perf, 5)) # 5 descritores mais difíceis
print(tail(desc_perf, 5)) # 5 descritores mais fáceis

# Gráfico: Percentual de acertos por descritor
ggplot(desc_perf, aes(x = reorder(MTI_DESCRITOR, perc_acerto), y = perc_acerto)) +
  geom_bar(stat = "identity") +
  coord_flip() +
  labs(title = "Percentual de Acertos por Descritor",
       x = "Descritor",
       y = "Percentual de Acertos") +
  theme_minimal()

# Identificação de escolas abaixo da média estadual
media_estadual <- mean(esc_perf$perc_acerto, na.rm = TRUE)
escolas_baixo <- esc_perf %>%
  filter(perc_acerto < media_estadual)

print(escolas_baixo)

# Recomendações automáticas
cat("\n==== Recomendações ====\n")
cat(sprintf("A média estadual de acertos é %.2f%%.\n", media_estadual))
cat("Descritores mais críticos (baixa performance):\n")
print(head(desc_perf, 5))
cat("Sugestão: Promover formação continuada de professores nesses descritores, oferecer reforço escolar direcionado, revisar materiais didáticos e monitorar avanços após intervenções.\n")

# Encerra conexão
dbDisconnect(con, shutdown=TRUE)

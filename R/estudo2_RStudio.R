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

# Carregando a tabela fato
fato <- dbReadTable(con, "fato_resposta_aluno")

# Calculando a participação: alunos únicos por município, por avaliação e por ano
participacao <- fato %>%
  group_by(MUN_NOME, AVA_NOME, AVA_ANO) %>%
  summarise(
    alunos_participantes = n_distinct(ALU_ID)
  ) %>%
  arrange(AVA_ANO, AVA_NOME, desc(alunos_participantes))

print("Taxa de participação (alunos participantes) por município, avaliação e ano:")
print(head(participacao, 20))  # Mostra as 20 primeiras linhas

# Gráfico: Participação por município em um ano ou teste específico
# Exemplo: filtrar por um ano/avaliação (ajuste conforme necessário)
ano_foco <- max(participacao$AVA_ANO, na.rm = TRUE)
avaliacao_foco <- unique(participacao$AVA_NOME)[1]

participacao_filtro <- participacao %>%
  filter(AVA_ANO == ano_foco, AVA_NOME == avaliacao_foco)

ggplot(participacao_filtro, aes(x = reorder(MUN_NOME, alunos_participantes), y = alunos_participantes)) +
  geom_bar(stat = "identity", fill = "darkgreen") +
  coord_flip() +
  labs(title = paste("Participação dos municípios em", avaliacao_foco, ano_foco),
       x = "Município",
       y = "Alunos participantes") +
  theme_minimal()

# Dica: para ver toda a tabela no RStudio, use:
# View(participacao)

dbDisconnect(con, shutdown=TRUE)

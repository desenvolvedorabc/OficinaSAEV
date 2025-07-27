# Teste rápido de conexão DuckDB
# Configurar mirror CRAN
options(repos = c(CRAN = "https://cran.rstudio.com/"))

# Instalar pacotes se necessário
if (!require("DBI", quietly = TRUE)) install.packages("DBI")
if (!require("duckdb", quietly = TRUE)) install.packages("duckdb")

library(DBI)
library(duckdb)

# Conectar ao banco
cat("🔌 Testando conexão com DuckDB...\n")
con <- dbConnect(duckdb::duckdb(), dbdir = "../db/avaliacao_prod.duckdb")

# Testar consulta simples
tabelas <- dbListTables(con)
cat("📁 Tabelas encontradas:", paste(tabelas, collapse = ", "), "\n")

# Contar registros na tabela fato
if ("fato_resposta_aluno" %in% tabelas) {
  registros <- dbGetQuery(con, "SELECT COUNT(*) as total FROM fato_resposta_aluno")
  cat("📊 Registros na tabela fato:", format(registros$total, big.mark = ","), "\n")
}

# Fechar conexão
dbDisconnect(con)
cat("✅ Teste concluído com sucesso!\n")

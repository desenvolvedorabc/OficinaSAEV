# 📊 Análise Simples SAEV - Exemplo Funcional
# Script R simplificado para demonstrar análises do DuckDB

# Configurar mirror CRAN
options(repos = c(CRAN = "https://cran.rstudio.com/"))

# Carregar apenas pacotes essenciais
suppressPackageStartupMessages({
  if (!require("DBI", quietly = TRUE)) install.packages("DBI")
  if (!require("duckdb", quietly = TRUE)) install.packages("duckdb")  
  if (!require("dplyr", quietly = TRUE)) install.packages("dplyr")
  
  library(DBI)
  library(duckdb)
  library(dplyr)
})

cat("📊 === ANÁLISE SIMPLES SAEV ===\n\n")

# Conectar ao banco
cat("🔌 Conectando ao DuckDB...\n")
con <- dbConnect(duckdb::duckdb(), dbdir = "db/avaliacao_prod.duckdb")

# Verificar estrutura
cat("📋 Estrutura do banco:\n")
tabelas <- dbListTables(con)
for (tabela in tabelas) {
  registros <- dbGetQuery(con, paste("SELECT COUNT(*) as n FROM", tabela))$n
  cat(sprintf("   %-20s: %s registros\n", tabela, format(registros, big.mark = ",")))
}
cat("\n")

# ANÁLISE 1: Alunos por município (top 10)
cat("📊 === TOP 10 MUNICÍPIOS POR NÚMERO DE ALUNOS ===\n")
query1 <- "
SELECT 
    MUN_NOME,
    COUNT(DISTINCT ALU_ID) as total_alunos
FROM fato_resposta_aluno 
GROUP BY MUN_NOME 
ORDER BY total_alunos DESC 
LIMIT 10
"
result1 <- dbGetQuery(con, query1)
print(result1)
cat("\n")

# ANÁLISE 2: Taxa de acerto por município (top 10)
cat("📊 === TOP 10 MUNICÍPIOS POR TAXA DE ACERTO ===\n")
query2 <- "
SELECT 
    MUN_NOME,
    COUNT(DISTINCT ALU_ID) as alunos,
    SUM(ACERTO) as acertos,
    SUM(ERRO) as erros,
    ROUND((SUM(ACERTO) * 100.0) / SUM(ACERTO + ERRO), 2) as taxa_acerto_pct
FROM fato_resposta_aluno 
GROUP BY MUN_NOME 
HAVING SUM(ACERTO + ERRO) > 5000
ORDER BY taxa_acerto_pct DESC 
LIMIT 10
"
result2 <- dbGetQuery(con, query2)
print(result2)
cat("\n")

# ANÁLISE 3: Desempenho por série
cat("📊 === DESEMPENHO POR SÉRIE ===\n")
query3 <- "
SELECT 
    SER_NOME,
    COUNT(DISTINCT ALU_ID) as alunos,
    ROUND((SUM(ACERTO) * 100.0) / SUM(ACERTO + ERRO), 2) as taxa_acerto_pct
FROM fato_resposta_aluno 
GROUP BY SER_NOME 
ORDER BY taxa_acerto_pct DESC
"
result3 <- dbGetQuery(con, query3)
print(result3)
cat("\n")

# ANÁLISE 4: Descritores mais difíceis
cat("📊 === TOP 10 DESCRITORES MAIS DIFÍCEIS ===\n")
query4 <- "
SELECT 
    d.MTI_CODIGO,
    SUBSTR(d.MTI_DESCRITOR, 1, 60) as descritor_resumido,
    SUM(f.ACERTO) as acertos,
    SUM(f.ERRO) as erros,
    ROUND((SUM(f.ACERTO) * 100.0) / SUM(f.ACERTO + f.ERRO), 2) as taxa_acerto_pct
FROM fato_resposta_aluno f
JOIN dim_descritor d ON f.MTI_CODIGO = d.MTI_CODIGO
GROUP BY d.MTI_CODIGO, d.MTI_DESCRITOR
HAVING SUM(f.ACERTO + f.ERRO) > 10000
ORDER BY taxa_acerto_pct ASC
LIMIT 10
"
result4 <- dbGetQuery(con, query4)
print(result4)
cat("\n")

# ANÁLISE 5: Comparação entre turnos
cat("📊 === DESEMPENHO POR TURNO ===\n")
query5 <- "
SELECT 
    TUR_PERIODO,
    COUNT(DISTINCT ALU_ID) as alunos,
    ROUND((SUM(ACERTO) * 100.0) / SUM(ACERTO + ERRO), 2) as taxa_acerto_pct
FROM fato_resposta_aluno 
GROUP BY TUR_PERIODO 
ORDER BY taxa_acerto_pct DESC
"
result5 <- dbGetQuery(con, query5)
print(result5)
cat("\n")

# RESUMO EXECUTIVO
cat("📊 === RESUMO EXECUTIVO ===\n")
total_alunos <- dbGetQuery(con, "SELECT COUNT(DISTINCT ALU_ID) as total FROM fato_resposta_aluno")$total
total_escolas <- dbGetQuery(con, "SELECT COUNT(DISTINCT ESC_INEP) as total FROM fato_resposta_aluno")$total
total_municipios <- dbGetQuery(con, "SELECT COUNT(DISTINCT MUN_NOME) as total FROM fato_resposta_aluno")$total
taxa_geral <- dbGetQuery(con, "SELECT ROUND((SUM(ACERTO) * 100.0) / SUM(ACERTO + ERRO), 2) as taxa FROM fato_resposta_aluno")$taxa

cat(sprintf("🎯 Total de Alunos: %s\n", format(total_alunos, big.mark = ",")))
cat(sprintf("🏫 Total de Escolas: %s\n", format(total_escolas, big.mark = ",")))
cat(sprintf("🏛️  Total de Municípios: %s\n", format(total_municipios, big.mark = ",")))
cat(sprintf("✅ Taxa de Acerto Geral: %.2f%%\n", taxa_geral))
cat("\n")

cat("🎯 PRINCIPAIS INSIGHTS:\n")
cat("   1. Município com mais alunos:", result1$MUN_NOME[1], "(", format(result1$total_alunos[1], big.mark = ","), "alunos )\n")
cat("   2. Município com melhor desempenho:", result2$MUN_NOME[1], "(", result2$taxa_acerto_pct[1], "%)\n")
cat("   3. Série com melhor desempenho:", result3$SER_NOME[1], "(", result3$taxa_acerto_pct[1], "%)\n")
cat("   4. Descritor mais difícil:", result4$MTI_CODIGO[1], "(", result4$taxa_acerto_pct[1], "%)\n")

# Salvar resultados
write.csv(result1, "R/resultado_municipios_alunos.csv", row.names = FALSE)
write.csv(result2, "R/resultado_municipios_desempenho.csv", row.names = FALSE)
write.csv(result3, "R/resultado_series_desempenho.csv", row.names = FALSE)
write.csv(result4, "R/resultado_descritores_dificeis.csv", row.names = FALSE)

cat("\n💾 Resultados salvos em R/resultado_*.csv\n")

# Fechar conexão
dbDisconnect(con)
cat("✅ Análise concluída!\n")

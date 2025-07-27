# 🧪 Teste de Padronização - Verificação de Todos os Scripts R
# Script para testar se todos os scripts podem acessar o banco de dados
# corretamente a partir da pasta raiz

cat("🧪 === TESTE DE PADRONIZAÇÃO DOS SCRIPTS R ===\n\n")

# Lista de scripts para testar
scripts <- c(
  "R/teste_conexao.R",
  "R/analise_simples.R", 
  "R/analise_saev.R",
  "R/gerar_relatorio_simples.R",
  "R/painel_analises.R",
  "R/painel_interativo.R"
)

cat("📋 Scripts a serem testados:\n")
for (i in 1:length(scripts)) {
  cat(sprintf("   %d. %s\n", i, scripts[i]))
}
cat("\n")

# Testar conexão básica
cat("🔌 Testando conexão básica ao banco...\n")

suppressPackageStartupMessages({
  if (!require("DBI", quietly = TRUE)) {
    stop("❌ Pacote DBI não encontrado. Execute: install.packages('DBI')")
  }
  if (!require("duckdb", quietly = TRUE)) {
    stop("❌ Pacote duckdb não encontrado. Execute: install.packages('duckdb')")
  }
  
  library(DBI)
  library(duckdb)
})

# Verificar se o banco existe
db_path <- "db/avaliacao_prod.duckdb"
cat(sprintf("📁 Verificando banco em: %s\n", db_path))

if (!file.exists(db_path)) {
  stop("❌ Banco de dados não encontrado!\n",
       "   Certifique-se de que:\n",
       "   1. Você está executando este script da pasta raiz\n",
       "   2. O ETL foi executado (python run_etl.py full)\n",
       "   3. O arquivo existe em: ", db_path)
}

# Testar conexão
tryCatch({
  con <- dbConnect(duckdb::duckdb(), dbdir = db_path)
  
  # Verificar tabelas
  tabelas <- dbListTables(con)
  cat("📊 Tabelas encontradas:", paste(tabelas, collapse = ", "), "\n")
  
  # Verificar dados
  total_registros <- dbGetQuery(con, "SELECT COUNT(*) as total FROM fato_resposta_aluno")$total
  cat(sprintf("📈 Registros na tabela fato: %s\n", format(total_registros, big.mark = ",")))
  
  # Fechar conexão
  dbDisconnect(con)
  
  cat("✅ Conexão testada com sucesso!\n\n")
  
}, error = function(e) {
  stop("❌ Erro na conexão: ", e$message)
})

# Verificar caminhos nos scripts
cat("🔍 Verificando padronização dos caminhos nos scripts...\n")

scripts_verificados <- 0
scripts_corretos <- 0

for (script in scripts) {
  if (file.exists(script)) {
    scripts_verificados <- scripts_verificados + 1
    
    # Ler conteúdo do script
    conteudo <- readLines(script, warn = FALSE)
    
    # Verificar se usa caminho padronizado
    usa_padrao <- any(grepl('db/avaliacao_prod\\.duckdb', conteudo))
    usa_relativo <- any(grepl('\\.\\./db/avaliacao_prod\\.duckdb', conteudo))
    
    if (usa_padrao && !usa_relativo) {
      cat(sprintf("   ✅ %s - Caminho padronizado\n", script))
      scripts_corretos <- scripts_corretos + 1
    } else if (usa_relativo) {
      cat(sprintf("   ❌ %s - Ainda usa caminho relativo (../db/)\n", script))
    } else {
      cat(sprintf("   ⚠️  %s - Caminho não identificado\n", script))
    }
  } else {
    cat(sprintf("   ❓ %s - Arquivo não encontrado\n", script))
  }
}

cat("\n📊 Resumo da Verificação:\n")
cat(sprintf("   Scripts verificados: %d/%d\n", scripts_verificados, length(scripts)))
cat(sprintf("   Scripts padronizados: %d/%d\n", scripts_corretos, scripts_verificados))

if (scripts_corretos == scripts_verificados) {
  cat("\n🎉 SUCESSO: Todos os scripts estão padronizados!\n")
  cat("✅ Todos podem ser executados a partir da pasta raiz com:\n")
  cat("   Rscript R/nome_do_script.R\n")
} else {
  cat("\n⚠️  ATENÇÃO: Alguns scripts ainda precisam ser corrigidos!\n")
}

cat("\n📋 Instruções de Uso:\n")
cat("1. Execute sempre a partir da pasta raiz: cd /caminho/para/OficinaSAEV\n")
cat("2. Use o formato: Rscript R/nome_do_script.R\n")
cat("3. Verifique se o banco existe em: db/avaliacao_prod.duckdb\n")
cat("4. Execute o ETL se necessário: python run_etl.py full\n")

cat("\n✅ Teste de padronização concluído!\n")

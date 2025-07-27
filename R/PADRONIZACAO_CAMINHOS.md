# 🔧 Padronização de Caminhos - Scripts R SAEV

## 📋 Problema Identificado

Os scripts R do sistema SAEV estavam usando caminhos inconsistentes para acessar o banco de dados DuckDB:

- **Alguns scripts** usavam `"../db/avaliacao_prod.duckdb"` (executar de dentro da pasta R/)
- **Outros scripts** usavam `"db/avaliacao_prod.duckdb"` (executar da pasta raiz)

Isso causava confusão sobre de onde executar cada script.

## ✅ Solução Implementada

**Padronização:** Todos os scripts agora usam o caminho relativo `"db/avaliacao_prod.duckdb"`

**Execução:** Todos os scripts devem ser executados **a partir da pasta raiz** do projeto

## 📝 Scripts Corrigidos

### Scripts que foram alterados:
1. `R/analise_saev.R` - Caminho alterado de `"../db/"` para `"db/"`
2. `R/teste_conexao.R` - Caminho alterado de `"../db/"` para `"db/"`

### Scripts que já estavam corretos:
1. `R/analise_simples.R` ✅
2. `R/gerar_relatorio_md.R` ✅
3. `R/gerar_relatorio_simples.R` ✅
4. `R/painel_analises.R` ✅
5. `R/painel_interativo.R` ✅

## 🚀 Como Executar os Scripts (PADRONIZADO)

### Todos os scripts devem ser executados a partir da pasta raiz:

```bash
# Navegar para a pasta raiz do projeto
cd /caminho/para/OficinaSAEV

# Executar qualquer script R
Rscript R/analise_simples.R
Rscript R/analise_saev.R
Rscript R/teste_conexao.R
Rscript R/gerar_relatorio_simples.R
Rscript R/painel_analises.R
Rscript R/painel_interativo.R
```

### ❌ NÃO faça mais isso:
```bash
# INCORRETO - não execute de dentro da pasta R/
cd R/
Rscript analise_saev.R  # Isso não funcionará mais
```

## 📁 Estrutura de Arquivos Esperada

```
OficinaSAEV/
├── db/
│   └── avaliacao_prod.duckdb    # Banco de dados
├── R/
│   ├── analise_simples.R        # Scripts R
│   ├── analise_saev.R
│   ├── teste_conexao.R
│   ├── gerar_relatorio_simples.R
│   ├── painel_analises.R
│   └── painel_interativo.R
└── [outros arquivos do projeto]
```

## 🔍 Verificação de Funcionamento

Todos os scripts foram testados e estão funcionando corretamente:

### Exemplo de execução bem-sucedida:
```bash
cd /caminho/para/OficinaSAEV
Rscript R/analise_simples.R
```

**Resultado esperado:**
```
📊 === ANÁLISE SIMPLES SAEV ===
🔌 Conectando ao DuckDB...
📋 Estrutura do banco:
   avaliacao           : 26,379,711 registros
   dim_aluno           : 313,573 registros
   [... resto da análise]
✅ Análise concluída!
```

## 🛠️ Código Alterado

### Antes (inconsistente):
```r
# Em alguns scripts
db_path <- "../db/avaliacao_prod.duckdb"

# Em outros scripts  
db_path <- "db/avaliacao_prod.duckdb"
```

### Depois (padronizado):
```r
# Em TODOS os scripts
db_path <- "db/avaliacao_prod.duckdb"
```

## 📋 Lista de Comandos Padronizados

### Análises Básicas:
```bash
# Teste de conexão
Rscript R/teste_conexao.R

# Análise simples
Rscript R/analise_simples.R

# Análise completa com gráficos
Rscript R/analise_saev.R
```

### Relatórios:
```bash
# Relatório simples em Markdown
Rscript R/gerar_relatorio_simples.R

# Relatório completo em Markdown
Rscript R/gerar_relatorio_md.R
```

### Painéis e Dashboards:
```bash
# Painel com gráficos estáticos
Rscript R/painel_analises.R

# Dashboard HTML interativo
Rscript R/painel_interativo.R
```

## 🎯 Benefícios da Padronização

1. **Consistência:** Todos os scripts seguem o mesmo padrão
2. **Simplicidade:** Uma única forma de executar todos os scripts
3. **Documentação Clara:** Instruções uniformes em toda a documentação
4. **Menos Erros:** Elimina confusão sobre caminhos de execução
5. **Manutenibilidade:** Facilita futuras modificações e atualizações

## ⚠️ Importante

- **Sempre execute os scripts a partir da pasta raiz** (`OficinaSAEV/`)
- **Verifique se o banco de dados existe** em `db/avaliacao_prod.duckdb`
- **Execute o ETL primeiro** se o banco não existir
- **Mantenha a estrutura de pastas** conforme especificado

---

*Padronização realizada em 27/07/2025*
*Todos os scripts testados e funcionando corretamente*

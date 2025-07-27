# 📊 Análises Estatísticas em R - SAEV

Este diretório contém scripts R para análise avançada dos dados educacionais do SAEV usando o modelo Star Schema no DuckDB.

## 🎯 Objetivo

Explorar o banco de dados DuckDB com análises estatísticas avançadas, visualizações e relatórios em R, aproveitando a estrutura Star Schema para análises de Business Intelligence.

## 📋 Pré-requisitos

### 1. R Instalado
Certifique-se de ter R instalado (versão 4.0+):
```bash
# Verificar versão do R
R --version
```

### 2. Banco de Dados ETL
O banco DuckDB deve estar criado e populado:
```bash
# Execute o ETL primeiro se necessário
cd ..
python run_etl.py full
```

### 3. Estrutura Esperada
```
OficinaSAEV/
├── db/
│   └── avaliacao_prod.duckdb    # Banco DuckDB populado
├── R/
│   ├── analise_saev.R           # Script principal
│   └── README.md                # Este arquivo
```

## 🚀 Execução das Análises

### Método 1: Relatório Markdown (Recomendado)
```bash
# Navegar para o diretório do projeto
cd /caminho/para/OficinaSAEV

# Gerar relatório completo em Markdown
Rscript R/gerar_relatorio_simples.R

# Arquivo gerado: R/relatorio_saev_YYYYMMDD.md
```

### Método 2: Análise Interativa Simples
```bash
# Análise rápida no console
Rscript R/analise_simples.R
```

### Método 3: Análise Completa com Gráficos
```bash
# Análise completa (requer pacotes adicionais)
Rscript R/analise_saev.R
```

### Método 4: RStudio
1. Abra o RStudio
2. Abra o arquivo desejado: `R/gerar_relatorio_simples.R`
3. Execute o script completo (Ctrl+Shift+Enter)

## 📊 Análises Realizadas

### 1. **📈 Número de Alunos por Município e Série**
- Distribuição de alunos por localização e nível educacional
- Identificação de concentrações e padrões demográficos

### 2. **🎯 Taxa de Acerto por Município**
- Ranking de municípios por desempenho
- Identificação de disparidades regionais

### 3. **📚 Desempenho por Disciplina e Série**
- Heatmap de desempenho cruzado
- Análise de dificuldade por matéria e nível

### 4. **🔴 Descritores com Maior Dificuldade**
- Competências mais desafiadoras
- Priorização para intervenções pedagógicas

### 5. **📅 Análise Temporal**
- Evolução do desempenho ao longo dos anos
- Tendências e padrões temporais

### 6. **🌅 Comparação entre Turnos**
- Diferenças de desempenho entre manhã/tarde
- Insights sobre impactos do horário escolar

### 7. **🏆 Ranking de Escolas**
- Classificação de escolas por taxa de acerto
- Benchmarking e boas práticas

## 📁 Arquivos Gerados

### 📄 Relatórios
- `relatorio_saev_YYYYMMDD.md` - Relatório completo em Markdown
- Visualização: VS Code, Typora, GitHub, ou qualquer editor Markdown
- Conversão para PDF: `pandoc relatorio_saev_YYYYMMDD.md -o relatorio.pdf`

### 📊 Visualizações (PNG)
- `grafico_alunos_por_serie.png` - Distribuição de alunos
- `grafico_taxa_acerto_municipio.png` - Performance municipal
- `grafico_heatmap_disciplina_serie.png` - Matriz de desempenho
- `grafico_descritores_dificeis.png` - Competências desafiadoras
- `grafico_evolucao_temporal.png` - Tendências anuais
- `grafico_comparacao_turnos.png` - Análise de turnos

### 💾 Dados Processados (CSV)
- `dados_alunos_municipio_serie.csv` - Dataset de distribuição
- `dados_taxa_acerto_municipio.csv` - Performance municipal
- `dados_desempenho_disciplina_serie.csv` - Matriz disciplina/série
- `dados_ranking_escolas.csv` - Ranking completo de escolas

## 🔧 Pacotes R Utilizados

O script instala automaticamente os pacotes necessários:

```r
# Pacotes principais
- DBI, duckdb          # Conexão com DuckDB
- dplyr                # Manipulação de dados
- ggplot2, plotly      # Visualizações
- scales               # Formatação
- corrplot             # Correlações
- RColorBrewer         # Paletas de cores
- gridExtra           # Arranjo de gráficos
- knitr               # Tabelas formatadas
```

## 📊 Exemplos de Saída

### Console Output
```
📊 === ANÁLISE 1: ALUNOS POR MUNICÍPIO E SÉRIE ===
🏆 Top 10 Município/Série por número de alunos:
|MUN_NOME          |SER_NOME    | total_alunos|
|:-----------------|:-----------|------------:|
|São Paulo         |9º Ano EF   |        12450|
|Rio de Janeiro    |8º Ano EF   |         9870|
...

📊 === RESUMO EXECUTIVO ===
📈 INDICADORES GERAIS:
   👥 Total de Alunos: 313,573
   🏫 Total de Escolas: 1,481
   🏛️  Total de Municípios: 145
   ✅ Taxa de Acerto Geral: 65.23%
```

## ⚠️ Resolução de Problemas

### Erro: "Banco não encontrado"
```bash
# Verifique se o ETL foi executado
ls -la ../db/avaliacao_prod.duckdb

# Se não existir, execute:
cd ..
python run_etl.py full
```

### Erro: "Pacote não encontrado"
```r
# No R, instale manualmente:
install.packages(c("DBI", "duckdb", "dplyr", "ggplot2"))
```

### Erro de Memória
- Use máquina com mais RAM (recomendado: 8GB+)
- Feche outros programas durante a execução

## 🎯 Próximos Passos

1. **Análises Avançadas**: Clustering, análise de variância
2. **Relatórios Automatizados**: RMarkdown para relatórios PDF
3. **Dashboard Interativo**: Shiny para visualizações web
4. **Modelagem Preditiva**: Machine learning para predição de desempenho

## 📞 Suporte

Para dúvidas sobre as análises em R:
1. Verifique se o banco DuckDB existe e está populado
2. Confirme que o R está instalado corretamente
3. Execute o script passo a passo para identificar erros
4. Consulte a documentação dos pacotes R utilizados

---

**💡 Dica**: Execute as análises após cada atualização do ETL para manter os insights atualizados!

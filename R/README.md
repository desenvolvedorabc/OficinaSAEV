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

**IMPORTANTE:** Todos os scripts devem ser executados **a partir da pasta raiz** do projeto:

```bash
# Navegar para a pasta raiz
cd /caminho/para/OficinaSAEV

# Executar scripts (PADRONIZADO)
Rscript R/teste_conexao.R           # Teste de conexão
Rscript R/analise_simples.R         # Análise básica
Rscript R/analise_saev.R            # Análise completa com gráficos
Rscript R/gerar_relatorio_simples.R # Relatório Markdown
Rscript R/painel_analises.R         # Painel com gráficos
Rscript R/painel_interativo.R       # Dashboard HTML
```

### ⚠️ Mudança Importante
Todos os caminhos foram padronizados para usar `"db/avaliacao_prod.duckdb"`. 
**NÃO execute mais** os scripts de dentro da pasta `R/`.

📋 **Ver detalhes:** `R/PADRONIZACAO_CAMINHOS.md`

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

## 🎯 Painéis de Análises (NOVO!)

Agora o sistema inclui **painéis interativos** para visualização das análises:

### 📊 Scripts de Painel Disponíveis

1. **`painel_analises.R`** - Gera gráficos estáticos em PNG
   ```bash
   Rscript R/painel_analises.R
   ```
   - 7 análises com gráficos de alta qualidade
   - Saída: `R/painel_graficos/*.png`

2. **`painel_interativo.R`** - Cria dashboard HTML interativo
   ```bash
   Rscript R/painel_interativo.R
   ```
   - Interface web responsiva com KPIs visuais
   - Saída: `R/painel_html/painel_saev_dashboard.html`

### 📈 Análises dos Painéis

- **Taxa de Acerto por Disciplina:** Matemática (61.02%) vs Língua Portuguesa (62.99%)
- **Top 20 Municípios:** Alegre (77.90%), Pancas (77.80%), Brejetuba (77.02%)
- **Top 20 Escolas:** EMPEF BREJO GRANDE DO SUL (97.63%)
- **Heatmap Disciplina vs Série:** Visualização da progressão do aprendizado
- **Distribuição por Turno:** Integral (63.24%), Tarde (63.22%), Manhã (60.69%)

### 🎨 Recursos dos Painéis

- **KPIs Visuais:** 313,573 alunos, 1,481 escolas, 78 municípios
- **Classificação por Cores:** Verde (≥70%), Amarelo (50-69%), Vermelho (<50%)
- **Exportação CSV:** Todos os dados disponíveis para análises adicionais
- **Layout Responsivo:** Otimizado para desktop e mobile

**📋 Documentação Completa:** Veja `R/README_PAINEIS.md` para detalhes completos

## 🎯 Próximos Passos

- **Análises Temporais:** Comparação de dados ao longo do tempo
- **Análises Preditivas:** Modelos de machine learning para identificar fatores de sucesso
- **Drill-down Interativo:** Navegação detalhada por escola e aluno
- **Alertas Automáticos:** Sistema de notificação para escolas com baixa performance
- **Relatórios Automatizados:** Geração periódica de dashboards

## 📞 Suporte

Para dúvidas ou problemas com as análises em R:

1. **Verificar Pré-requisitos:** Confirmar que o banco DuckDB está disponível
2. **Logs de Execução:** Verificar mensagens de erro nos scripts
3. **Pacotes R:** Confirmar instalação dos pacotes necessários (DBI, duckdb, dplyr, ggplot2)
4. **Dados:** Verificar se o ETL foi executado com sucesso
5. **Painéis:** Para problemas específicos com dashboards, consulte `R/README_PAINEIS.md`

---

**💡 Dica**: Execute as análises após cada atualização do ETL para manter os insights atualizados!

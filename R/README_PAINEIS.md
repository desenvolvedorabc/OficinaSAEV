# 📊 Painéis de Análises SAEV - Dashboard em R

Este diretório contém scripts R para construir painéis interativos com análises gerais sobre taxa de acerto por disciplina, teste, escola e município, usando dados do sistema SAEV no DuckDB.

## 🎯 Objetivo

Criar painéis visuais e interativos para análise da performance educacional, permitindo:
- Visualização rápida de indicadores-chave (KPIs)
- Comparação de desempenho entre diferentes dimensões
- Identificação de padrões e tendências
- Exportação de dados para análises adicionais

## 📊 Scripts Disponíveis

### 1. `painel_analises.R` - Painel com Gráficos Estáticos
**Descrição:** Script principal que gera gráficos em PNG com análises detalhadas

**Recursos:**
- 7 análises diferentes com gráficos de alta qualidade
- Exportação de dados em CSV
- Indicadores gerais do sistema
- Visualizações otimizadas para relatórios

**Execução:**
```bash
Rscript R/painel_analises.R
```

**Saídas:**
- `R/painel_graficos/` - Gráficos em PNG (300 DPI)
- `R/painel_dados/` - Dados em CSV para análises adicionais

### 2. `painel_interativo.R` - Dashboard HTML
**Descrição:** Cria um painel web interativo com tabelas e KPIs visuais

**Recursos:**
- Interface HTML responsiva
- KPIs em cards visuais coloridos
- Tabelas com classificação por cores (verde/amarelo/vermelho)
- Layout otimizado para diferentes dispositivos

**Execução:**
```bash
Rscript R/painel_interativo.R
```

**Saídas:**
- `R/painel_html/painel_saev_dashboard.html` - Dashboard principal
- `R/painel_html/*.csv` - Dados estruturados

## 📈 Análises Realizadas

### 1. Taxa de Acerto por Disciplina
- **Matemática:** 61.02%
- **Língua Portuguesa:** 62.99%

### 2. Taxa de Acerto por Teste (Top 15)
Análise dos testes com melhor performance:
- Testes diagnósticos vs formativos
- Performance por série e disciplina

### 3. Taxa de Acerto por Município (Top 20)
Ranking dos municípios com melhor desempenho:
- **1º lugar:** Alegre (77.90%)
- **2º lugar:** Pancas (77.80%)
- **3º lugar:** Brejetuba (77.02%)

### 4. Taxa de Acerto por Escola (Top 20)
Identificação das escolas com melhor performance educacional

### 5. Heatmap Disciplina vs Série
Matriz visual mostrando a performance por série e disciplina:
- Identificação de pontos críticos
- Progressão do aprendizado
- Comparação entre disciplinas

### 6. Distribuição por Série e Turno
Análise da distribuição de alunos e performance por:
- Séries (1º ao 9º ano EF)
- Turnos (Manhã, Tarde, Integral)

### 7. Indicadores Gerais do Sistema
- **Total de Alunos:** 313,573
- **Total de Escolas:** 1,481
- **Total de Municípios:** 78
- **Taxa de Acerto Geral:** 62.01%

## 🎨 Recursos Visuais

### Gráficos Estáticos (PNG)
- **01_taxa_acerto_disciplina.png** - Comparação entre disciplinas
- **02_taxa_acerto_teste.png** - Top 15 testes por performance
- **03_taxa_acerto_municipio.png** - Ranking de municípios
- **04_taxa_acerto_escola.png** - Ranking de escolas
- **05_heatmap_disciplina_serie.png** - Matriz disciplina vs série
- **06a_distribuicao_serie_turno.png** - Distribuição de alunos
- **06b_taxa_acerto_serie_turno.png** - Performance por turno

### Dashboard HTML
- Layout responsivo
- KPIs em cards coloridos
- Tabelas com classificação visual por cores:
  - 🟢 **Verde:** Taxa ≥ 70% (Boa)
  - 🟡 **Amarelo:** Taxa 50-69% (Média)
  - 🔴 **Vermelho:** Taxa < 50% (Precisa Melhorar)

## 🔧 Dependências

### Pacotes Essenciais (sempre instalados)
```r
DBI          # Interface de banco de dados
duckdb       # Conector DuckDB
dplyr        # Manipulação de dados
ggplot2      # Visualizações básicas
gridExtra    # Layout de gráficos
scales       # Formatação de escalas
viridis      # Paleta de cores
```

### Pacotes Opcionais (para interatividade)
```r
plotly       # Gráficos interativos
DT           # Tabelas interativas
htmlwidgets  # Widgets HTML
```

**Nota:** O sistema funciona mesmo se os pacotes opcionais não estiverem disponíveis, usando versões simplificadas.

## 📊 Dados Exportados

### CSV Gerados
- `painel_disciplinas.csv` - Dados por disciplina
- `painel_testes.csv` - Dados por teste
- `painel_municipios.csv` - Top 20 municípios
- `painel_escolas.csv` - Top 20 escolas
- `painel_disciplina_serie.csv` - Matriz disciplina vs série
- `painel_serie_turno.csv` - Dados por série e turno
- `painel_indicadores_gerais.csv` - KPIs do sistema

### Formato dos Dados
```csv
# Exemplo: painel_municipios.csv
MUN_NOME,total_alunos,total_acertos,total_erros,taxa_acerto_pct
Alegre,1322,81531,23125,77.90
Pancas,1083,65725,18759,77.80
```

## 🚀 Como Usar

### Execução Completa
```bash
# 1. Gerar gráficos estáticos
cd /caminho/para/OficinaSAEV
Rscript R/painel_analises.R

# 2. Gerar dashboard HTML
Rscript R/painel_interativo.R

# 3. Visualizar o dashboard
open R/painel_html/painel_saev_dashboard.html  # macOS
xdg-open R/painel_html/painel_saev_dashboard.html  # Linux
```

### Visualização dos Resultados
1. **Gráficos:** Abrir arquivos PNG em `R/painel_graficos/`
2. **Dashboard:** Abrir `R/painel_html/painel_saev_dashboard.html` no navegador
3. **Dados:** Importar CSVs para Excel, Python ou outras ferramentas

## 📋 Estrutura de Arquivos Gerada

```
R/
├── painel_analises.R           # Script principal (gráficos)
├── painel_interativo.R         # Script HTML interativo
├── painel_graficos/            # Gráficos PNG gerados
│   ├── 01_taxa_acerto_disciplina.png
│   ├── 02_taxa_acerto_teste.png
│   ├── 03_taxa_acerto_municipio.png
│   ├── 04_taxa_acerto_escola.png
│   ├── 05_heatmap_disciplina_serie.png
│   ├── 06a_distribuicao_serie_turno.png
│   └── 06b_taxa_acerto_serie_turno.png
├── painel_dados/               # Dados CSV (versão completa)
│   ├── painel_disciplinas.csv
│   ├── painel_testes.csv
│   ├── painel_municipios.csv
│   ├── painel_escolas.csv
│   ├── painel_disciplina_serie.csv
│   ├── painel_serie_turno.csv
│   └── painel_indicadores_gerais.csv
├── painel_html/                # Dashboard HTML
│   ├── painel_saev_dashboard.html
│   ├── dados_disciplina.csv
│   ├── dados_municipio.csv
│   ├── dados_escola.csv
│   ├── dados_disciplina_serie.csv
│   └── indicadores_gerais.csv
└── README_PAINEIS.md           # Esta documentação
```

## 🔍 Insights Principais

### Performance por Disciplina
- **Língua Portuguesa** tem melhor performance geral (62.99%)
- **Matemática** apresenta maior desafio (61.02%)
- Gap de 1.97 pontos percentuais entre disciplinas

### Performance por Série
- **Séries iniciais** (1º-2º ano) têm melhor desempenho
- **Séries intermediárias** (6º-8º ano) apresentam maiores desafios
- **9º ano** mostra recuperação parcial

### Performance por Município
- **Top 3:** Alegre, Pancas, Brejetuba (>77%)
- Diferença significativa entre melhor (77.9%) e média geral (62.01%)
- 15.89 pontos percentuais de diferença entre extremos

### Performance por Turno
- **Integral:** 63.24% (melhor performance)
- **Tarde:** 63.22% (equivalente ao integral)
- **Manhã:** 60.69% (menor performance)

## 🎯 Próximos Passos

1. **Análises Temporais:** Comparar dados ao longo do tempo
2. **Análises Preditivas:** Identificar fatores de sucesso
3. **Drill-down:** Permitir navegação detalhada por escola
4. **Alertas:** Sistema de notificação para baixa performance
5. **Relatórios Automatizados:** Geração periódica de relatórios

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar se o banco DuckDB está disponível em `db/avaliacao_prod.duckdb`
2. Confirmar que o ETL foi executado com sucesso
3. Verificar se os pacotes R essenciais estão instalados
4. Consultar logs de execução para identificar erros específicos

---

*Painéis gerados automaticamente pelo Sistema SAEV em R*
*Dados extraídos do banco DuckDB com arquitetura Star Schema*

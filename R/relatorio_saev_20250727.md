# 📊 Relatório de Análise SAEV

**Sistema de Análise de Avaliações Educacionais**

📅 **Data de Geração:** 27/07/2025 às 12:25
🏛️ **Fonte:** Banco DuckDB - Star Schema
⚙️ **Gerado por:** Script R automatizado

---

## 🗄️ Estrutura do Banco de Dados

O banco DuckDB contém as seguintes tabelas:

| Tabela | Registros |
|--------|----------:|
| `avaliacao` | 26,379,711 |
| `dim_aluno` | 313,573 |
| `dim_descritor` | 161 |
| `dim_escola` | 1,481 |
| `fato_resposta_aluno` | 18,243,121 |

## 📊 Análise 1: Distribuição de Alunos

### 📈 Alunos por Série

| Série | Total de Alunos |
|-------|---------------:|
| 2º Ano EF | 47,657 |
| 3º Ano EF | 44,601 |
| 5º Ano EF | 43,389 |
| 4º Ano EF | 42,400 |
| 1º Ano EF | 36,657 |
| 6º Ano EF | 28,514 |
| 7º Ano EF | 24,713 |
| 8º Ano EF | 24,522 |
| 9º Ano EF | 22,280 |

### 🏆 Top 10 Município/Série por Número de Alunos

| Município | Série | Total de Alunos |
|-----------|-------|---------------:|
| Serra | 2º Ano EF | 7,181 |
| Serra | 3º Ano EF | 6,969 |
| Serra | 1º Ano EF | 6,580 |
| Serra | 4º Ano EF | 6,403 |
| Serra | 5º Ano EF | 6,021 |
| Vila Velha | 4º Ano EF | 4,666 |
| Vila Velha | 5º Ano EF | 4,628 |
| Cariacica | 2º Ano EF | 4,515 |
| Vila Velha | 2º Ano EF | 4,488 |
| Cariacica | 3º Ano EF | 4,487 |

## 📊 Análise 2: Taxa de Acerto por Município

### 🏆 Top 15 Municípios por Taxa de Acerto

| Município | Alunos | Acertos | Erros | Taxa de Acerto (%) |
|-----------|-------:|--------:|------:|------------------:|
| Alegre | 1,322 | 81,531 | 23,125 | 77.9% |
| Pancas | 1,083 | 65,725 | 18,759 | 77.8% |
| Brejetuba | 702 | 43,986 | 13,124 | 77.02% |
| Dores do Rio Preto | 574 | 34,085 | 11,081 | 75.47% |
| Itarana | 625 | 37,065 | 12,295 | 75.09% |
| Divino de São Lourenço | 320 | 19,029 | 6,317 | 75.08% |
| Ecoporanga | 1,170 | 68,199 | 24,229 | 73.79% |
| Ibatiba | 1,817 | 104,690 | 38,086 | 73.32% |
| Mantenópolis | 842 | 48,349 | 17,857 | 73.03% |
| Pedro Canário | 1,741 | 99,635 | 36,957 | 72.94% |
| Rio Novo do Sul | 735 | 42,194 | 15,788 | 72.77% |
| Itaguaçu | 809 | 46,354 | 17,478 | 72.62% |
| Alto Rio Novo | 592 | 34,215 | 12,905 | 72.61% |
| Água Doce do Norte | 794 | 46,011 | 17,543 | 72.4% |
| Iconha | 532 | 30,705 | 12,023 | 71.86% |

## 📊 Análise 3: Desempenho por Disciplina e Série

| Disciplina | Série | Alunos | Taxa de Acerto (%) |
|------------|-------|-------:|------------------:|
| Língua Portuguesa | 1º Ano EF | 36,443 | 74.24% |
| Língua Portuguesa | 2º Ano EF | 47,408 | 75.54% |
| Língua Portuguesa | 3º Ano EF | 44,385 | 69.46% |
| Língua Portuguesa | 4º Ano EF | 42,247 | 59.7% |
| Língua Portuguesa | 5º Ano EF | 43,256 | 57.87% |
| Língua Portuguesa | 6º Ano EF | 28,388 | 55.28% |
| Língua Portuguesa | 7º Ano EF | 24,600 | 54.55% |
| Língua Portuguesa | 8º Ano EF | 24,421 | 54.6% |
| Língua Portuguesa | 9º Ano EF | 22,185 | 61.29% |
| Matemática | 1º Ano EF | 36,440 | 83.67% |
| Matemática | 2º Ano EF | 47,383 | 81.5% |
| Matemática | 3º Ano EF | 44,387 | 71.66% |
| Matemática | 4º Ano EF | 42,236 | 65.86% |
| Matemática | 5º Ano EF | 43,230 | 59.47% |
| Matemática | 6º Ano EF | 28,359 | 48.93% |
| Matemática | 7º Ano EF | 24,565 | 42.39% |
| Matemática | 8º Ano EF | 24,414 | 38.89% |
| Matemática | 9º Ano EF | 22,188 | 39.77% |

## 📊 Análise 4: Descritores com Maior Dificuldade

### 🔴 Top 10 Descritores Mais Difíceis

| Código | Descritor | Taxa de Acerto (%) |
|--------|-----------|------------------:|
| `M070` | Identificar quadriláteros observando as posições relativas entre seus lados (par | 21.71% |
| `M065` | Resolver problema envolvendo o cálculo do perímetro de figuras planas, desenhada | 22.99% |
| `M094` | Identificar números primos | 23.59% |
| `M064` | Resolver problema envolvendo o cálculo de perímetro de figuras planas | 25.01% |
| `M076` | Resolver problema utilizando propriedades dos polígonos (soma de seus ângulos in | 25.58% |
| `M027` | Resolver situação problema utilizando mínimo múltiplo comum ou máximo divisor co | 26.12% |
| `M028` | Identificar a expressão algébrica que expressa uma regularidade observada em seq | 26.6% |
| `M023` | Identificar frações equivalentes. | 27.6% |
| `M022` | Efetuar cálculos simples com valores aproximados de radicais | 27.8% |
| `M018` | Reconhecer as diferentes representações de números racionais ou irracionais | 28.3% |

## 📊 Análise 5: Desempenho por Turno

| Turno | Alunos | Taxa de Acerto (%) |
|-------|-------:|------------------:|
| Integral | 33,564 | 63.24% |
| Tarde | 133,469 | 63.22% |
| Manhã | 150,016 | 60.69% |

## 📊 Análise 6: Ranking de Escolas

### 🏆 Top 20 Escolas por Taxa de Acerto

| Escola | Município | Alunos | Taxa de Acerto (%) |
|--------|-----------|-------:|------------------:|
| EMPEF BREJO GRANDE DO SUL | Itapemirim | 19 | 97.63% |
| EMPEF ROZARIA DA SILVEIRA NUNES | Itapemirim | 28 | 97.24% |
| UMEF PROFESSOR ERNANI SOUZA | Vila Velha | 365 | 92.33% |
| EMEIEF SANTA LUZIA DO NORTE | Ecoporanga | 35 | 91.81% |
| EMPEF SAO RAFAEL | Domingos Martins | 15 | 91.29% |
| EEEFM MARLENE BRANDAO | Brejetuba | 56 | 89.55% |
| EMEIF PR. LIBERALINO DE SOUSA PROÊZA | Brejetuba | 27 | 89.11% |
| EEEFM José Corrente | Alegre | 36 | 89.07% |
| EUMEF CABECEIRA DO CORREGO BOLIVIA | Governador Lindenberg | 16 | 88.76% |
| EMUEIEF ALTO BATUTA | Baixo Guandu | 27 | 88.5% |
| EEEFM ALARICO JOSE DE LIMA | Nova Venécia | 36 | 88.4% |
| EMPEIEF CACHOEIRINHA | Rio Novo do Sul | 17 | 88.4% |
| EMEF FAZENDA BOA VISTA | Pancas | 15 | 88.17% |
| EMEIEF FAZENDA ALBERTO LITTIG | Laranja da Terra | 13 | 87.41% |
| EEEFM JANUÁRIO RIBEIRO  | Pancas | 51 | 87.4% |
| EEEFM MARGEM DO ITAUNINHAS | Pinheiros | 15 | 87.07% |
| EMEF CRUBIXA | Alfredo Chaves | 30 | 86.98% |
| EEFM Padre Afonso Braz | Iúna | 65 | 86.9% |
| EMEIEF ANGELO BRAVIN | Marilândia | 41 | 86.73% |
| EEEFM José Teixeira Fialho | Ecoporanga | 30 | 86.69% |

## 📊 Resumo Executivo

### 📈 Indicadores Gerais

| Indicador | Valor |
|-----------|------:|
| **Total de Alunos** | 313,573 |
| **Total de Escolas** | 1,481 |
| **Total de Municípios** | 78 |
| **Taxa de Acerto Geral** | 62.01% |

### 🎯 Principais Insights

1. **Série com mais alunos:** 2º Ano EF (47,657 alunos)
2. **Município com melhor desempenho:** Alegre (77.9%)
3. **Descritor mais difícil:** `M070` (21.71%)
4. **Melhor escola:** EMPEF BREJO GRANDE DO SUL (97.63%)

## 📎 Anexos

### 💾 Dados Exportados

Os dados detalhados foram exportados nos seguintes arquivos CSV:

- `dados_alunos_municipio_serie.csv` - Distribuição de alunos por município e série
- `dados_taxa_acerto_municipio.csv` - Taxa de acerto por município
- `dados_desempenho_disciplina_serie.csv` - Desempenho por disciplina e série
- `dados_ranking_escolas.csv` - Ranking completo de escolas

### 🔍 Metodologia

**Fonte dos Dados:** Banco DuckDB com arquitetura Star Schema

**Tabelas Utilizadas:**
- `fato_resposta_aluno` - Tabela fato com métricas agregadas
- `dim_aluno` - Dimensão de alunos
- `dim_escola` - Dimensão de escolas
- `dim_descritor` - Dimensão de descritores/competências

**Filtros Aplicados:**
- Municípios: Mínimo de 1.000 questões respondidas
- Escolas: Mínimo de 1.000 questões respondidas
- Descritores: Mínimo de 5.000 questões respondidas

---

*Relatório gerado automaticamente pelo Sistema SAEV em 27/07/2025 às 12:25*

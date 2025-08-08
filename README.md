# # SAEV - Sistema de Análise Educacional

## ⚠️ **TRATAMENTO ESPECIAL: DISCIPLINA LEITURA**

📚 **IMPORTANTE**: A disciplina "Leitura" possui métricas baseadas em **proficiência** (níveis 1-6), não em acerto/erro.  
� **Documentação completa**: Consulte `DISCIPLINA_LEITURA.md` para detalhes específicos.

---📊 OficinaSAEV

## � SAEV - Sistema de Avaliação Educacional com Rankings e Classificações

Este projeto oferece uma suíte completa de dashboards interativos para análise dos dados do Sistema de Avaliação Educacional de Vitória (SAEV), incluindo funcionalidades avançadas de **rankings e classificações**.

Esta oficina tem como objetivo orientar os técnicos e analistas sobre como utilizar ferramentas livres integradas com IA para análise de dados educacionais.

---

## 🏆 **NOVA FUNCIONALIDADE: Rankings e Classificações**

### 🎯 **O que faz:**
- **Top 50 Alunos**: Ranking dos melhores alunos por disciplina e teste específico
- **Top 10 Escolas**: Ranking das melhores escolas por disciplina e teste
- **Estatísticas Gerais**: Métricas completas de desempenho do teste selecionado
- **Visualizações Interativas**: Gráficos dos top performers
- **Download CSV**: Exportação completa dos rankings

### 🔍 **Critérios de Ranking:**

#### **👥 Ranking de Alunos:**
- **Filtro mínimo:** 5 questões respondidas
- **Ordenação:** Taxa de acerto (DESC) → Total de acertos (DESC)
- **Dados exibidos:** Nome, escola, município, série, turno, performance

#### **🏫 Ranking de Escolas:**
- **Filtro mínimo:** 10 alunos e 100 questões respondidas
- **Ordenação:** Taxa de acerto (DESC) → Total de alunos (DESC)
- **Dados exibidos:** Nome, município, nº alunos, taxa, séries atendidas


## 🎯 Objetivos do Projeto

- **Visualização Interativa**: Dashboards dinâmicos para análise de desempenho educacional
- **Relatórios Automatizados**: Geração de relatórios detalhados em Excel ou PDF
- **Análises Avançadas**: Clustering, análise de tendências e correlações
- **Monitoramento de Equidade**: Identificação de gaps educacionais
- **Interface Intuitiva**: Painel web responsivo e fácil de usar


## 🚀 Funcionalidades Principais

### 📈 Dashboard Interativo
- Visão geral de desempenho por município e escola
- Análise por competências e descritores
- Filtros dinâmicos por ano, disciplina, teste e série
- Gráficos interativos com Plotly

### 📋 Sistema de Relatórios
- Relatórios municipais comparativos
- Análise de desempenho por escola
- Relatórios de competências e descritores
- Análises comparativas entre anos
- Exportação automática para Excel

### 🔬 Análises Avançadas
- Clustering de escolas por perfil de desempenho
- Análise de equidade educacional
- Correlação entre competências
- Análise de tendências temporais
- Identificação de gaps entre séries

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **Streamlit**: Framework para dashboard web
- **Plotly**: Visualizações interativas
- **Pandas**: Manipulação de dados
- **DuckDB**: Banco de dados local (arquitetura OLAP)
- **Scikit-learn**: Análises de machine learning
- **SciPy**: Análises estatísticas

## 🚀 Instalação e Configuração

Para configurar o ambiente de desenvolvimento, consulte o **[Guia de Instalação](INSTALACAO.md)** que contém instruções detalhadas para:

- 🍎 **macOS** - Script automatizado com Homebrew
- 🐧 **Linux (Ubuntu/Debian)** - Script com dependências do sistema
- 🪟 **Windows** - Script batch com verificações

### Instalação Rápida

```bash
# macOS
./setup_macos.sh

# Linux (Ubuntu/Debian)  
./setup_linux.sh

# Windows
setup_windows.bat
```

## 🔒 Segurança e Privacidade de Dados

### ⚠️ **IMPORTANTE - Dados Sigilosos**

Este projeto trabalha com **dados educacionais sensíveis** contendo:
- CPF de alunos
- Nomes pessoais  
- Informações escolares confidenciais

### 🛡️ **Medidas de Segurança Implementadas**

1. **Exclusão do Git**: As pastas `data/` e `db/` estão no `.gitignore`
2. **Isolamento**: Dados ficam apenas no ambiente local
3. **Documentação**: READMEs explicativos sobre segurança
4. **Configuração**: Ambientes separados (teste/produção)

### 📋 **Boas Práticas**

- ✅ Use dados anonimizados para desenvolvimento
- ✅ Mantenha backups seguros dos dados reais
- ✅ Configure adequadamente permissões de acesso
- ❌ **NUNCA** commite dados com informações pessoais
- ❌ **NUNCA** compartilhe dados reais em repositórios públicos

## 📁 Estrutura de Diretórios Sugerida para o Projeto

```
oficinaIA/
├── README.md
├── data/
│   ├── raw/                      # Dados CSV originais
│   └── test/                     # Dados de teste
├── db/
├── src/
│   ├── config.py                 # Configurações e gerenciamento de ambientes
├── reports/                      # Relatórios gerados
└── tests/                        # Testes unitários
```

### Tabela "avaliacao"

A tabela a ser carregada no banco de dados DuckDB com o nome "avaliacao" deve conter a estrutura apresentada a seguir:


| Nome da Coluna  | Tipo de Dados  | Tamanho | Descrição |  
| ----------------| -------------- | ------- | --------- |
| MUN_UF          | CHAR(2)        |    2    | SIGLA DA UNIDADE DA FEDERAÇÃO |       
| MUN_NOME        | VARCHAR(60)    |   60    | NOME DO MUNICÍPIO |
| ESC_INEP        | CHAR(8)        |    8    | CÓDIGO INEP DA ESCOLA |
| ESC_NOME        | VARCHAR(80)    |   80    | NOME DA ESCOLA |
| SER_NUMBER      | INTEGER        |         | NÚMERO DO ANO/SÉRIE |
| SER_NOME        | VARCHAR(30)    |   30    | NOME DA SÉRIE |
| TUR_PERIODO     | VARCHAR(15)    |   15    | TURNO DE ATIVIDADE (Manhã, Tarde) |
| TUR_NOME        | VARCHAR(15)    |   20    | NOME DO TURNO |
| ALU_ID          | LONG           |         | IDENTIFICAÇÃO DO ALUNO |  
| ALU_NOME        | VARCHAR(80)    |   80    | NOME DO ALUNO |
| ALU_CPF         | VARCHAR(11)    |   15    | CPF DO ALUNO  |
| AVA_NOME        | VARCHAR(50)    |   50    | NOME DA AVALIAÇÃO |  
| AVA_ANO         | INTEGER        |         | ANO DA AVALIAÇÃO |
| DIS_NOME        | VARCHAR(30)    |   30    | NOME DA DISCIPLINA  |
| TES_NOME        | VARCHAR(30)    |   30    | NOME DO TESTE |
| TEG_ORDEM       | INTEGER        |         | ORDEM DA QUESTÃO DO TESTE |
| ATR_RESPOSTA    | VARCHAR(15)    |   15    | RESPOSTA DO ALUNO NA QUESTÃO (*) |
| ATR_CERTO       | INTEGER        |         | SE 1 ACERTOU SE 0 ERROU (*) |   
| MTI_CODIGO      | VARCHAR(15)    |   15    | CÓDIGO DO DESCRITOR |
| MTI_DESCRITOR   | VARCHAR(512)   |   512   | DESCRIÇÃO DO DESCRITOR | 


#### DDL para Criação da Tabela

A seguir tem-se o comando DDL para criação da tabela no DuckDB. Tanto o banco de dados quanto a tabela "avaliacao" devem ser criados caso não existam. 

```sql
CREATE TABLE avaliacao (
    MUN_UF         CHAR(2),              -- SIGLA DA UNIDADE DA FEDERAÇÃO
    MUN_NOME       VARCHAR(60),          -- NOME DO MUNICÍPIO
    ESC_INEP       CHAR(8),              -- CÓDIGO INEP DA ESCOLA
    ESC_NOME       VARCHAR(80),          -- NOME DA ESCOLA
    SER_NUMBER     INTEGER,              -- NÚMERO DO ANO/SÉRIE
    SER_NOME       VARCHAR(30),          -- NOME DA SÉRIE
    TUR_PERIODO    VARCHAR(15),          -- TURNO DE ATIVIDADE (Manhã, Tarde)
    TUR_NOME       VARCHAR(20),          -- NOME DO TURNO
    ALU_ID         INTEGER,              -- IDENTIFICAÇÃO DO ALUNO
    ALU_NOME       VARCHAR(80),          -- NOME DO ALUNO
    ALU_CPF        VARCHAR(15),          -- CPF DO ALUNO
    AVA_NOME       VARCHAR(50),          -- NOME DA AVALIAÇÃO
    AVA_ANO        INTEGER,              -- ANO DA AVALIAÇÃO
    DIS_NOME       VARCHAR(30),          -- NOME DA DISCIPLINA
    TES_NOME       VARCHAR(30),          -- NOME DO TESTE
    TEG_ORDEM      INTEGER,              -- ORDEM DA QUESTÃO DO TESTE
    ATR_RESPOSTA   VARCHAR(15),          -- RESPOSTA DO ALUNO NA QUESTÃO
    ATR_CERTO      INTEGER,              -- SE 1 ACERTOU, SE 0 ERROU
    MTI_CODIGO     VARCHAR(15),          -- CÓDIGO DO DESCRITOR
    MTI_DESCRITOR  VARCHAR(512)          -- DESCRIÇÃO DO DESCRITOR
);

### ⚠️ **IMPORTANTE: Tratamento Especial para Disciplina "Leitura"**

A disciplina **"Leitura"** tem características especiais:

- **ATR_CERTO**: Sempre 0 (não aplicável)
- **ATR_RESPOSTA**: Contém o nível de proficiência do aluno
- **Métrica**: Baseada em níveis de leitura, não em acerto/erro

#### 📚 **Níveis de Proficiência em Leitura:**

| **Código** | **Descrição** | **Nível** |
|------------|---------------|-----------|
| `nao_leitor` | Não Leitor | 1 (Iniciante) |
| `silabas` | Leitor de Sílabas | 2 |
| `palavras` | Leitor de Palavras | 3 |
| `frases` | Leitor de Frases | 4 |
| `nao_fluente` | Não Fluente | 5 |
| `fluente` | Leitor Fluente | 6 (Avançado) |

#### 🎯 **Impacto nos Dashboards:**

- **Análises tradicionais** (Português/Matemática): Baseadas em taxa de acerto
- **Análises de Leitura**: Baseadas na distribuição de níveis de proficiência
- **Métricas específicas**: Percentual de alunos por nível, evolução da proficiência

## ⭐ Arquitetura Star Schema

Para análises de alta performance e Business Intelligence, o sistema deve oferecer uma estrutura monolítica em um modelo Star Schema otimizado.
Isto é, além de permitir consultas eventuais na tabela primária "avaliacao", deverá criar uma estrutura Star Schema como apresentada a seguir.

### 🏗️ Estrutura do Star Schema

#### 📋 Tabelas de Dimensão

| **Tabela** | **Propósito** | **Chave Primária** | **Descrição** |
|------------|---------------|-------------------|---------------|
| **`dim_aluno`** | Dimensão de Alunos | `ALU_ID` | Dados únicos de cada aluno (ID, nome, CPF) |
| **`dim_escola`** | Dimensão de Escolas | `ESC_INEP` | Dados únicos de cada escola (código INEP, nome) |
| **`dim_descritor`** | Dimensão de Descritores | `MTI_CODIGO` | Competências/descritores com estatísticas de uso |

#### ⭐ Tabela Fato

| **Tabela** | **Propósito** | **Métricas** |
|------------|---------------|--------------|
| **`fato_resposta_aluno`** | Fatos agregados por aluno e descritor | `ACERTO`, `ERRO` |

#### 🔧 Tabela Auxiliar

| **Tabela** | **Propósito** | **Descrição** |
|------------|---------------|---------------|
| **`teste`** | Versão normalizada | Dados da tabela original sem redundâncias das dimensões |

### 📊 Diagrama do Star Schema

```
                    ┌─────────────────┐
                    │   dim_aluno     │
                    │                 │
                    │ • ALU_ID (PK)   │
                    │ • ALU_NOME      │
                    │ • ALU_CPF       │
                    └─────────┬───────┘
                              │
                              │
        ┌─────────────────┐   │   ┌──────────────────┐
        │   dim_escola    │   │   │  dim_descritor   │
        │                 │   │   │                  │
        │ • ESC_INEP (PK) │   │   │ • MTI_CODIGO(PK) │
        │ • ESC_NOME      │   │   │ • MTI_DESCRITOR  │
        └─────────┬───────┘   │   │ • QTD            │
                  │           │   └─────────┬────────┘
                  │           │             │
                  └───────────┼─────────────┘
                              │
                    ┌─────────▼───────┐
                    │fato_resposta_   │
                    │     aluno       │
                    │                 │
                    │ • ALU_ID (FK)   │
                    │ • ESC_INEP (FK) │
                    │ • MTI_CODIGO(FK)│
                    │ • MUN_NOME      │
                    │ • SER_NOME      │
                    │ • DIS_NOME      │
                    │ • TES_NOME      │
                    │ • ACERTO ⭐     │
                    │ • ERRO ⭐       │
                    └─────────────────┘
```

#### Criação da Estrutura Star Schema com base na tabela "avaliacao"

```sql
DROP TABLE IF EXISTS dim_aluno;
DROP TABLE IF EXISTS dim_escola; 
DROP TABLE IF EXISTS dim_descritor;
DROP TABLE IF EXISTS teste; 
DROP TABLE IF EXISTS fato_resposta_aluno;

-- Cria a dimensão de alunos
CREATE TABLE dim_aluno (
    ALU_ID INTEGER PRIMARY KEY,    -- Chave primária - ID único do aluno
    ALU_NOME VARCHAR(60),          -- Nome do aluno (pode estar criptografado)
    ALU_CPF CHAR(11)               -- CPF do aluno (pode estar criptografado)
);

-- Popula a dimensão com alunos únicosINSERT INTO dim_aluno (ALU_ID, ALU_NOME, ALU_CPF)  
SELECT DISTINCT ALU_ID, ALU_NOME, ALU_CPF 
FROM avaliacao;

SELECT COUNT(*) FROM dim_aluno;

-- Cria a dimensão de escolas

CREATE TABLE dim_escola (
    ESC_INEP CHAR(8) PRIMARY KEY,  -- Chave primária - Código INEP da escola
    ESC_NOME VARCHAR(60)           -- Nome da escola (pode estar criptografado)
);

-- Popula a dimensão com escolas únicas
INSERT INTO dim_escola (ESC_INEP, ESC_NOME) 
SELECT DISTINCT ESC_INEP, ESC_NOME 
FROM avaliacao;
SELECT COUNT(*) FROM dim_escola;

-- Cria tabela de dimensão de descritores com código, descrição e quantidade
CREATE TABLE dim_descritor (
    MTI_CODIGO VARCHAR(15) PRIMARY KEY,  -- Chave primária - Código do descritor
    MTI_DESCRITOR VARCHAR(512),          -- Descrição do descritor
    QTD INTEGER                          -- Quantidade de ocorrências
);

-- Popula a dimensão com descritores únicos e suas estatísticas
-- Usa MAX() para pegar uma versão da descrição quando há variações
INSERT INTO dim_descritor (MTI_CODIGO, MTI_DESCRITOR, QTD) 
SELECT 
    MTI_CODIGO, 
    MAX(MTI_DESCRITOR) AS MTI_DESCRITOR,  -- Pega uma versão da descrição
    COUNT(*) AS QTD 
FROM avaliacao 
GROUP BY MTI_CODIGO;

SELECT COUNT(*) FROM dim_descritor;

-- ----------------------------------------------------------------------------
-- TABELA FATO: fato_resposta_aluno
-- Agregação por aluno, descritor e contexto, com métricas de acerto/erro
-- É o coração do Star Schema - onde ficam as métricas de negócio
-- ----------------------------------------------------------------------------
CREATE TABLE fato_resposta_aluno AS 
SELECT 
    -- Dimensões geográficas e administrativas
    MUN_UF,           -- Unidade da Federação
    MUN_NOME,         -- Nome do Município
    ESC_INEP,         -- Código da Escola (FK para dim_escola)
    
    -- Dimensões educacionais
    SER_NUMBER,       -- Número da Série
    SER_NOME,         -- Nome da Série
    TUR_PERIODO,      -- Período do Turno
    TUR_NOME,         -- Nome do Turno
    
    -- Dimensão do aluno
    ALU_ID,           -- ID do Aluno (FK para dim_aluno)
    
    -- Dimensões de avaliação
    AVA_NOME,         -- Nome da Avaliação
    AVA_ANO,          -- Ano da Avaliação
    DIS_NOME,         -- Disciplina
    TES_NOME,         -- Nome do Teste
    MTI_CODIGO,       -- Código do Descritor (FK para dim_descritor)
    
    -- MÉTRICAS DE NEGÓCIO (Fatos)
    SUM(CASE WHEN ATR_CERTO = 1 THEN 1 ELSE 0 END) AS ACERTO,  -- Total de acertos
    SUM(CASE WHEN ATR_CERTO = 0 THEN 1 ELSE 0 END) AS ERRO     -- Total de erros
FROM avaliacao
GROUP BY 
    MUN_UF, MUN_NOME, ESC_INEP, SER_NUMBER, SER_NOME, 
    TUR_PERIODO, TUR_NOME, ALU_ID, AVA_NOME, AVA_ANO, 
    DIS_NOME, TES_NOME, MTI_CODIGO;

SELECT COUNT(*) FROM fato_resposta_aluno;

```

## 📊 ETL - Extração e Carga de Dados

O sistema ETL processa arquivos CSV com dados de avaliações educacionais e os carrega em um banco de dados DuckDB com arquitetura Star Schema.

### 🚀 **Execução Rápida**

```bash
# Ativar ambiente virtual
source venv_saev/bin/activate

# Iniciar sistema (menu interativo)
./start_saev_universal.sh

# Opções disponíveis:
# 1) Dashboard Geral (porta 8501)
# 2) Dashboard com Filtros (porta 8502) 
# 3) Rankings e Classificações (porta 8503)
# 4) Análise de Leitura (porta 8504) ← NOVO!
# 5) Todos os aplicativos (portas 8501-8504) ← ATUALIZADO!
```

### 📊 **Dashboards Disponíveis**

| **Opção** | **Dashboard** | **Porta** | **Funcionalidade** |
|-----------|---------------|-----------|-------------------|
| **1** | Dashboard Geral | 8501 | Visão geral, análises por município/escola |
| **2** | Dashboard Filtros | 8502 | Filtros avançados, análises detalhadas |
| **3** | Rankings | 8503 | Top alunos, escolas, classificações |
| **4** | **Análise Leitura** | **8504** | **Proficiência em leitura (níveis 1-6)** |
| **5** | **Todos** | **8501-8504** | **Inicia todos simultaneamente** |

### 🎯 **Disciplina Leitura - Funcionalidades Especiais**

- **📚 Métricas Específicas**: Baseadas em proficiência, não acerto/erro
- **📊 6 Níveis de Proficiência**: Não leitor → Fluente
- **📈 Visualizações Exclusivas**: Distribuições, rankings por nível
- **🔍 Análises Detalhadas**: Por município, escola, série
- **📋 Dashboard Dedicado**: http://localhost:8504

### 📖 **Documentação Completa**

Para instruções detalhadas de execução, configuração e resolução de problemas, consulte o **[Guia de Execução do ETL](EXECUCAO_ETL.md)**.

### 📋 **Especificações Técnicas**

Os arquivos no formato CSV estão armazenados no diretório `data/raw` do projeto. Todos os arquivos armazenados neste diretório têm a mesma estrutura e devem popular a tabela "avaliacao".

O processo de carga oferece duas opções:
- **Carga Completa**: Recria o banco de dados e processa todos os arquivos
- **Carga Incremental**: Processa apenas arquivos novos ou modificados (usando hash MD5)

### Estrutura CSV

1) A primeira linha contém os nomes dos campos (colunas): "MUN_UF","MUN_NOME","ESC_INEP","ESC_NOME","SER_NUMBER","SER_NOME","TUR_PERIODO","TUR_NOME","ALU_ID","ALU_NOME","ALU_CPF","AVA_NOME","AVA_ANO","DIS_NOME","TES_NOME","TEG_ORDEM","ATR_RESPOSTA","ATR_CERTO","MTI_CODIGO","MTI_DESCRITOR";
2) O separador de coluna utilizado é a vírgula (","); 
3) O delimitador de campos texto é o caractere aspas duplas ("); Contudo, alguns campos texto no arquivo CSV não possuem este delimitador (isso não é um problema para o ETL).




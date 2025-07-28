# 🎯 SAEV Streamlit 2 - Dashboard Interativo com Filtros

## 📊 **Visão Geral**

O `saev_streamlit2.py` é a **segunda versão** do dashboard SAEV, projetado especificamente para oferecer **filtros interativos avançados**. Enquanto o primeiro aplicativo (`saev_streamlit.py`) mostra uma visão geral de todos os dados, este segundo foca na **análise personalizada** através de filtros dinâmicos.

## 🎯 **Principais Características**

### **🔍 Filtros Interativos:**
- **🏙️ Município:** Seleção múltipla de municípios
- **📚 Disciplina:** Português, Matemática, etc.
- **🎓 Série:** Todas as séries disponíveis
- **📝 Teste:** Diferentes tipos de avaliações

### **📊 Interface:**
- **Sidebar Dedicada:** Todos os filtros organizados na barra lateral
- **Filtros Múltiplos:** Combine diferentes critérios de análise
- **Limpeza Rápida:** Botão para resetar todos os filtros
- **Status em Tempo Real:** Visualização dos filtros aplicados

## 🎨 **Layout e Funcionalidades**

### **📈 Métricas Principais (8 KPIs):**
1. **👨‍🎓 Total de Alunos** - Contagem única filtrada
2. **🏫 Total de Escolas** - Escolas nos critérios selecionados
3. **🏙️ Total de Municípios** - Municípios ativos nos filtros
4. **📝 Total de Testes** - Testes que atendem os filtros
5. **❓ Total de Questões** - Soma de acertos + erros
6. **✅ Total de Acertos** - Questões respondidas corretamente
7. **📊 Taxa de Acerto Geral** - Percentual global filtrado
8. **❌ Total de Erros** - Questões respondidas incorretamente

### **📊 6 Visualizações Dinâmicas:**

#### **1. 🏆 Top 10 Municípios por Taxa de Acerto**
- **Tipo:** Gráfico de barras horizontal
- **Filtro de Qualidade:** ≥ 1000 questões
- **Cores:** Escala RdYlGn (vermelho → amarelo → verde)
- **Interatividade:** Hover com detalhes

#### **2. 👨‍🎓 Distribuição de Alunos por Município**
- **Tipo:** Gráfico de barras horizontal
- **Foco:** Top 15 municípios por volume
- **Cores:** Escala azul por intensidade
- **Dados:** Total de alunos únicos

#### **3. 📚 Taxa de Acerto por Série e Disciplina**
- **Tipo:** Barras agrupadas
- **Comparação:** Disciplinas lado a lado
- **Análise:** Progressão educacional por série
- **Filtros:** Dinâmico conforme seleção

#### **4. 📖 Performance por Disciplina**
- **Tipo:** Gráfico de pizza
- **Métrica:** Distribuição de questões
- **Cores:** Automáticas por disciplina
- **Hover:** Taxa de acerto específica

#### **5. 📋 Detalhes dos Municípios**
- **Tipo:** Tabela interativa
- **Colunas:** Município, Alunos, Taxa (%)
- **Filtro:** ≥ 500 questões para confiabilidade
- **Ordenação:** Por taxa de acerto decrescente

#### **6. 🎯 Descritores Mais Difíceis**
- **Tipo:** Barras horizontais
- **Foco:** 10 competências com menor taxa
- **Cores:** Escala vermelha (dificuldade)
- **Filtro:** ≥ 500 questões para confiabilidade

## 🏗️ **Arquitetura Técnica**

### **📁 Estrutura de Dados:**
```sql
-- Star Schema utilizado:
fato_resposta_aluno     # Tabela principal (ACERTO/ERRO)
├── dim_escola          # ESC_INEP, ESC_NOME, MUN_NOME
├── dim_aluno           # ALU_ID, ALU_NOME
└── dim_descritor       # MTI_CODIGO, MTI_DESCRITOR
```

### **⚡ Performance e Cache:**
- **`@st.cache_resource`** - Conexão com banco reutilizada
- **`@st.cache_data`** - Dados dos filtros e métricas em cache
- **Queries Otimizadas** - SQL eficiente com agregações
- **Filtros de Qualidade** - Apenas dados confiáveis

### **🔍 Sistema de Filtros:**
```python
# Construção dinâmica de WHERE clauses
where_conditions = ["1=1"]  # Base sempre verdadeira

if municipios_selecionados:
    where_conditions.append("e.MUN_NOME IN (...)")
if disciplinas_selecionadas:
    where_conditions.append("f.DIS_NOME IN (...)")
# ... outros filtros

where_clause = " AND ".join(where_conditions)
```

## 🚀 **Como Usar**

### **🖥️ Execução:**
```bash
cd /Users/rcaratti/Desktop/ABC/SAEV/OficinaSAEV

# Método recomendado
./start_streamlit2.sh

# Execução direta
streamlit run saev_streamlit2.py --server.port=8502
```

### **🌐 URLs de Acesso:**
- **Local:** http://localhost:8502
- **Rede:** http://192.168.18.108:8502

### **📱 Navegação:**
1. **Abra a sidebar** (pode estar recolhida em telas pequenas)
2. **Selecione os filtros** desejados nos campos múltiplos
3. **Observe as métricas** se atualizando automaticamente
4. **Explore os gráficos** com interatividade Plotly
5. **Use "Limpar Filtros"** para resetar a visualização

## 🎯 **Diferenças entre os Aplicativos**

| Característica | SAEV Streamlit 1 | **SAEV Streamlit 2** |
|----------------|------------------|----------------------|
| **Foco** | Visão geral completa | **Análise filtrada** |
| **Filtros** | Nenhum | **4 filtros interativos** |
| **Porta** | 8501 | **8502** |
| **Interface** | Layout principal | **Sidebar + principal** |
| **Uso** | Dashboard executivo | **Análise exploratória** |
| **Métricas** | 7 KPIs fixos | **8 KPIs dinâmicos** |
| **Interatividade** | Básica | **Avançada** |

## 🔧 **Casos de Uso**

### **👥 Para Gestores Educacionais:**
- Comparar performance entre municípios específicos
- Analisar disciplinas problemáticas em determinadas séries
- Focar em tipos específicos de testes
- Drill-down por critérios combinados

### **📊 Para Analistas de Dados:**
- Segmentação avançada dos dados
- Análise comparativa personalizada
- Identificação de padrões específicos
- Validação de hipóteses educacionais

### **🎯 Para Coordenadores Pedagógicos:**
- Análise por disciplina e série
- Identificação de descritores problemáticos
- Comparação entre diferentes avaliações
- Monitoramento de municípios específicos

## 🛠️ **Configuração Técnica**

### **📦 Dependências:**
```txt
streamlit==1.46.1
duckdb==1.3.2
pandas==2.1.4
plotly==6.2.0
```

### **🔌 Conexão com Banco:**
```python
conn = duckdb.connect('db/avaliacao_prod.duckdb', read_only=True)
```

### **⚙️ Configurações do Streamlit:**
- **Layout:** Wide (uso completo da tela)
- **Sidebar:** Expandida por padrão
- **Cache:** Ativo para performance
- **Tema:** Padrão do Streamlit

## 📊 **Exemplos de Análises**

### **🔍 Análise por Município:**
1. Selecione municípios específicos
2. Compare suas performances
3. Identifique pontos fortes/fracos
4. Analise distribuição de alunos

### **📚 Análise por Disciplina:**
1. Filtre por Português OU Matemática
2. Compare entre diferentes séries
3. Identifique descritores difíceis
4. Analise progressão educacional

### **🎓 Análise por Série:**
1. Foque em séries específicas
2. Compare disciplinas
3. Analise evolução por município
4. Identifique gaps educacionais

## 🎉 **Vantagens do Segundo Aplicativo**

### **🎯 Flexibilidade:**
- ✅ Análises personalizadas por usuário
- ✅ Combinação livre de filtros
- ✅ Foco em segmentos específicos
- ✅ Exploração interativa

### **⚡ Performance:**
- ✅ Cache inteligente por combinação de filtros
- ✅ Queries otimizadas dinamicamente
- ✅ Carregamento rápido mesmo com filtros
- ✅ Interface responsiva

### **🔍 Insights:**
- ✅ Descoberta de padrões ocultos
- ✅ Comparações específicas
- ✅ Análise de subgrupos
- ✅ Validação de hipóteses

## 🚨 **Avisos Importantes**

### **⚠️ Filtros de Qualidade:**
- Gráficos mostram apenas dados com ≥ 500 ou ≥ 1000 questões
- Filtros muito restritivos podem resultar em "Sem dados"
- Use combinações equilibradas para melhores resultados

### **💾 Cache e Performance:**
- Primeira execução pode ser mais lenta
- Cache melhora performance em usos subsequentes
- Limpeza de filtros reinicia rapidamente

### **🌐 Conectividade:**
- Aplicativo roda localmente (offline após carregamento)
- Banco de dados deve estar disponível
- Porta 8502 deve estar livre

---

## 🎊 **Resumo**

O **SAEV Streamlit 2** é a evolução natural do primeiro dashboard, oferecendo **máxima flexibilidade** para análises educacionais personalizadas. Com seus **4 filtros interativos** e **8 métricas dinâmicas**, permite exploração detalhada dos dados do Sistema de Avaliação da Educação do Espírito Santo.

**🌟 Ideal para:** Análises exploratórias, comparações específicas, drill-down detalhado, e descoberta de insights educacionais.

**🚀 Acesse agora:** http://localhost:8502

---

*🎯 Dashboard inteligente para análises educacionais avançadas*  
*📊 Baseado em Star Schema com performance otimizada*  
*🔍 Filtros interativos para máxima flexibilidade analítica*

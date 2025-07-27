# 📊 SAEV Streamlit - Galeria de Painéis Educacionais

## 🎯 Visão Geral

O **SAEV Streamlit** é um aplicativo web interativo desenvolvido para análise dos dados educacionais do Sistema de Avaliação da Educação do Espírito Santo. O aplicativo oferece uma interface intuitiva com filtros avançados e múltiplos painéis de visualização.

## 🚀 Como Executar

### 1. Pré-requisitos
```bash
# Navegar para a pasta do projeto
cd /Users/rcaratti/Desktop/ABC/SAEV/OficinaSAEV

# Verificar se as dependências estão instaladas
pip install -r requirements.txt
```

### 2. Iniciar o Aplicativo
```bash
# Executar o Streamlit
streamlit run streamlit_app.py

# Ou com configurações específicas
streamlit run streamlit_app.py --server.port=8501 --server.headless=true
```

### 3. Acessar no Navegador
- **URL Local:** http://localhost:8501
- **URL de Rede:** http://192.168.18.108:8501

## 📋 Funcionalidades Principais

### 🔍 Sistema de Filtros Avançados

O aplicativo oferece **6 filtros principais** com múltipla seleção:

#### 1. 📅 **Filtro por Ano**
- Seleciona períodos específicos de avaliação
- Múltipla seleção disponível
- Dados disponíveis: 2025

#### 2. 🏙️ **Filtro por Município**
- Lista todos os municípios do Espírito Santo
- Botão "Todos" para seleção completa
- Múltipla seleção para comparações
- 78 municípios disponíveis

#### 3. 🏫 **Filtro por Escola**
- Lista todas as escolas do sistema
- Botão "Todos" para seleção completa
- Filtro dinâmico baseado nos municípios selecionados
- Centenas de escolas disponíveis

#### 4. 📚 **Filtro por Disciplina**
- Disciplinas: Língua Portuguesa e Matemática
- Permite análises comparativas entre matérias
- Múltipla seleção disponível

#### 5. 🎓 **Filtro por Série**
- Séries: 1º ao 9º Ano do Ensino Fundamental
- Análise da progressão educacional
- Comparações entre diferentes anos escolares

#### 6. 📝 **Filtro por Teste**
- Tipos: Diagnóstico (Diag) e Formativo (Form1)
- Análise temporal do progresso
- Comparação entre diferentes momentos avaliativos

### 🎨 Galeria de Painéis

## 📊 **Painel 1: Visão Geral dos Dados**

### Métricas Principais
- 👨‍🎓 **Total de Alunos**: Número único de estudantes
- 🏫 **Total de Escolas**: Instituições participantes
- 🏙️ **Total de Municípios**: Abrangência geográfica
- 📝 **Total de Testes**: Avaliações realizadas

### Visualizações Incluídas:

#### 1. **Alunos por Município** (Gráfico de Barras Horizontal)
- Top 15 municípios por número de alunos
- Identificação de centros educacionais
- Análise de distribuição populacional estudantil

#### 2. **Testes por Disciplina** (Gráfico de Pizza)
- Distribuição de avaliações por matéria
- Balanceamento entre Português e Matemática
- Visão geral da cobertura disciplinar

#### 3. **Municípios com Maiores Taxas de Acerto** (Gráfico de Barras)
- Top 10 municípios por performance
- Ranking de excelência educacional
- Mapa de calor por cores (RdYlGn)

#### 4. **Taxa de Acerto por Disciplina e Série** (Gráfico de Barras Agrupadas)
- Comparação entre Português e Matemática
- Análise de progressão por série
- Identificação de padrões educacionais

## 📈 **Painel 2: Taxa de Acerto - Análises Detalhadas**

### Estrutura em Abas:

#### 🏙️ **Aba 1: Por Município**

**Visualizações:**
1. **Gráfico de Barras Agrupadas**: Taxa de acerto por município e disciplina
2. **Heatmap**: Cruzamento município × série com escala de cores
3. **Ranking**: Top 15 municípios por taxa média de acerto

**Insights Fornecidos:**
- Identificação de municípios com melhor performance
- Comparação regional de resultados
- Análise de disparidades geográficas

#### 🏫 **Aba 2: Por Escola**

**Visualizações:**
1. **Ranking de Escolas**: Top 20 escolas por taxa de acerto
2. **Scatter Plot**: Relação entre número de questões e performance
3. **Análise Comparativa**: Escolas por município e disciplina

**Insights Fornecidos:**
- Identificação de escolas exemplares
- Análise de correlação volume × qualidade
- Benchmarking educacional

#### 📚 **Aba 3: Por Disciplina**

**Visualizações:**
1. **Gráfico de Linhas**: Evolução da taxa por série
2. **Box Plot**: Distribuição de performance por disciplina  
3. **Gráfico de Barras**: Performance por tipo de teste

**Insights Fornecidos:**
- Progressão educacional por série
- Comparação Português vs Matemática
- Análise diagnóstico vs formativo

#### 🎯 **Aba 4: Por Descritor (Habilidades)**

**Visualizações:**
1. **Descritores Mais Difíceis**: 15 habilidades com menor taxa de acerto
2. **Descritores Mais Fáceis**: 15 habilidades com maior sucesso
3. **Histograma**: Distribuição geral das taxas por descritor

**Insights Fornecidos:**
- Identificação de lacunas de aprendizagem
- Habilidades que precisam de reforço
- Mapeamento de competências desenvolvidas

## 🎛️ Recursos Interativos

### ✨ **Funcionalidades Especiais:**

1. **Múltipla Seleção em Todos os Filtros**
   - Comparação simultânea de múltiplas categorias
   - Análises cruzadas complexas

2. **Botões "Todos" Estratégicos**
   - Seleção rápida de todos os municípios
   - Seleção rápida de todas as escolas
   - Economia de tempo na configuração

3. **Filtros Iniciando Vazios**
   - Usuário controla completamente a visualização
   - Evita sobrecarga inicial de dados
   - Interface limpa e focada

4. **Cache Inteligente** (@st.cache_data)
   - Carregamento rápido de dados
   - Performance otimizada
   - Experiência fluida do usuário

5. **Feedback Visual Contínuo**
   - Contador de registros encontrados
   - Indicadores de loading
   - Mensagens de orientação

## 💾 Tecnologias Utilizadas

### 🐍 **Backend Python:**
- **Streamlit 1.46.1**: Framework principal da aplicação
- **DuckDB 1.3.2**: Banco de dados analítico de alta performance
- **Pandas 2.1.4**: Manipulação e análise de dados
- **NumPy 1.26.4**: Computação numérica

### 📊 **Visualização:**
- **Plotly Express 6.2.0**: Gráficos interativos principais
- **Plotly Graph Objects**: Visualizações customizadas
- **Plotly Subplots**: Layouts complexos

### 🎨 **Interface:**
- **HTML/CSS**: Estilização customizada
- **Markdown**: Documentação integrada
- **Layout Responsivo**: Colunas adaptativas

## 📁 Estrutura de Arquivos

```
OficinaSAEV/
├── streamlit_app.py          # Aplicativo principal
├── requirements.txt          # Dependências Python
├── db/
│   └── avaliacao_prod.duckdb # Banco de dados
└── README.md                 # Documentação
```

## 🔧 Configuração Técnica

### **Conexão com Banco:**
```python
# Conexão DuckDB otimizada
con = duckdb.connect('db/avaliacao_prod.duckdb', read_only=True)
```

### **Cache de Performance:**
```python
# Cache para otimização
@st.cache_data
def carregar_opcoes_filtros():
    # Carregamento otimizado de filtros
```

### **Configuração da Página:**
```python
st.set_page_config(
    page_title="SAEV - Painéis Educacionais",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

## 📊 Dados Suportados

### **Volume de Dados:**
- **~18.2 milhões** de registros de respostas
- **78 municípios** do Espírito Santo
- **Centenas de escolas** participantes
- **2 disciplinas** principais
- **9 séries** do Ensino Fundamental
- **36 tipos de testes** diferentes

### **Estrutura dos Dados:**
- **Fato Principal**: `fato_resposta_aluno`
- **Dimensões**: `dim_escola`, `dim_aluno`, `dim_descritor`
- **Campos Calculados**: Taxa de acerto, totalizações

## 🎯 Casos de Uso

### 👨‍💼 **Para Gestores Educacionais:**
- Monitoramento de performance por região
- Identificação de escolas que precisam de suporte
- Análise de efetividade de políticas públicas

### 👩‍🏫 **Para Coordenadores Pedagógicos:**
- Análise de descritores com baixa performance
- Comparação entre diferentes tipos de avaliação
- Planejamento de intervenções pedagógicas

### 📊 **Para Analistas de Dados:**
- Exploração interativa de grandes volumes de dados
- Geração de insights através de visualizações
- Análises estatísticas comparativas

### 🏛️ **Para Secretarias de Educação:**
- Relatórios executivos visuais
- Acompanhamento de indicadores educacionais
- Tomada de decisão baseada em dados

## 🚨 Troubleshooting

### **Problema: Aplicativo não inicia**
```bash
# Verificar instalação do Streamlit
pip install streamlit

# Verificar se o banco existe
ls -la db/avaliacao_prod.duckdb
```

### **Problema: Erro de conexão com banco**
```bash
# Verificar integridade do banco
python -c "import duckdb; print('OK')"
```

### **Problema: Performance lenta**
- Reduzir número de filtros selecionados
- Usar filtros mais específicos
- Aguardar cache ser populado

## 🔄 Atualizações e Manutenção

### **Para Atualizar Dados:**
1. Execute o ETL principal: `python run_etl.py full`
2. Reinicie o aplicativo Streamlit
3. Cache será automaticamente invalidado

### **Para Adicionar Novos Filtros:**
1. Modifique a função `criar_filtros()`
2. Atualize `construir_query_base()`
3. Teste com dados de exemplo

## 📈 Roadmap Futuro

### **Melhorias Planejadas:**
- [ ] Exportação de relatórios em PDF
- [ ] Filtros por período específico
- [ ] Comparação temporal entre anos
- [ ] Dashboard para dispositivos móveis
- [ ] Alertas automáticos de performance
- [ ] Integração com outras bases de dados

## 📞 Suporte

Para suporte técnico ou dúvidas sobre o aplicativo:
- Verifique a documentação completa
- Teste com filtros reduzidos primeiro
- Consulte os logs do Streamlit para debugging

---

**📊 SAEV Streamlit - Transformando dados educacionais em insights acionáveis**

*Desenvolvido com ❤️ para a educação do Espírito Santo*

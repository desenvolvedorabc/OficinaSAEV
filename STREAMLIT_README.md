# 📊 SAEV Streamlit - Guia Rápido

## 🚀 Inicialização Rápida

### Método 1: Script Automatizado (Recomendado)
```bash
cd /Users/rcaratti/Desktop/ABC/SAEV/OficinaSAEV
./start_streamlit.sh
```

### Método 2: Comando Manual
```bash
cd /Users/rcaratti/Desktop/ABC/SAEV/OficinaSAEV
streamlit run streamlit_app.py
```

## 🌐 Acesso ao Aplicativo

Após iniciar, acesse em seu navegador:
- **Local:** http://localhost:8501
- **Rede:** http://192.168.18.108:8501

## 🎯 Como Usar

### 1️⃣ **Configurar Filtros**
- Na barra lateral, selecione os filtros desejados
- Use múltipla seleção para comparações
- Clique "Todos" para municípios/escolas completos

### 2️⃣ **Escolher Painel**
- **Painel 1:** Visão geral com estatísticas principais
- **Painel 2:** Análises detalhadas de taxa de acerto

### 3️⃣ **Explorar Visualizações**
- Gráficos interativos com Plotly
- Hover para detalhes adicionais
- Zoom e pan disponíveis

## 📋 Filtros Disponíveis

| Filtro | Opções | Funcionalidade |
|--------|---------|----------------|
| 📅 **Ano** | 2025 | Período da avaliação |
| 🏙️ **Município** | 78 municípios | Localização + botão "Todos" |
| 🏫 **Escola** | Centenas | Instituição + botão "Todos" |
| 📚 **Disciplina** | Português, Matemática | Matéria avaliada |
| 🎓 **Série** | 1º ao 9º Ano EF | Ano escolar |
| 📝 **Teste** | Diagnóstico, Formativo | Tipo de avaliação |

## 📊 Painéis Disponíveis

### 🎯 **Painel 1: Visão Geral**
- Métricas principais (alunos, escolas, municípios)
- Distribuição de alunos por município
- Ranking de municípios por taxa de acerto
- Taxa de acerto por disciplina e série

### 📈 **Painel 2: Análises Detalhadas**
- **Por Município:** Rankings, heatmaps, comparações
- **Por Escola:** Performance individual, correlações
- **Por Disciplina:** Evolução por série, distribuições
- **Por Descritor:** Habilidades mais/menos dominadas

## 🔧 Requisitos Técnicos

- **Python 3.11+**
- **Streamlit 1.46.1+**
- **DuckDB 1.3.2+**
- **Plotly 6.2.0+**
- **Pandas 2.1.4+**

## 💡 Dicas de Uso

### ✅ **Boas Práticas:**
- Inicie com poucos filtros para exploração inicial
- Use "Todos" em municípios para visão completa
- Combine disciplinas para análises comparativas
- Explore diferentes séries para ver progressão

### ⚠️ **Evitar:**
- Não selecione todos os filtros simultaneamente (pode ser lento)
- Não feche o terminal durante uso do aplicativo
- Aguarde carregamento completo antes de mudanças

## 🎨 Funcionalidades Especiais

### 🔍 **Interatividade:**
- Gráficos com zoom e pan
- Hover com informações detalhadas
- Filtros dinâmicos em tempo real

### 🎯 **Análises Avançadas:**
- Correlações visuais
- Heatmaps educacionais
- Rankings dinâmicos
- Distribuições estatísticas

### 📊 **Visualizações:**
- Gráficos de barras (horizontal/vertical)
- Gráficos de linhas temporais
- Scatter plots (correlações)
- Box plots (distribuições)
- Heatmaps (cruzamentos)
- Gráficos de pizza (proporções)

## 🚨 Solução de Problemas

### **Aplicativo não carrega:**
```bash
# Verificar se o banco existe
ls -la db/avaliacao_prod.duckdb

# Reinstalar dependências
pip install -r requirements.txt
```

### **Erro de porta ocupada:**
```bash
# Usar porta alternativa
streamlit run streamlit_app.py --server.port=8502
```

### **Performance lenta:**
- Use menos filtros simultâneos
- Aguarde cache ser construído
- Feche outras aplicações pesadas

## 📱 Compatibilidade

### ✅ **Navegadores Suportados:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### ✅ **Sistemas Operacionais:**
- macOS 10.14+
- Windows 10+
- Linux Ubuntu 18.04+

## 🔄 Atualizações

Para atualizar dados:
1. Execute ETL: `python run_etl.py full`
2. Reinicie Streamlit: `Ctrl+C` e execute novamente

## 📞 Suporte Rápido

| Problema | Solução |
|----------|---------|
| Não inicia | Verificar banco de dados existe |
| Sem dados | Selecionar pelo menos um filtro |
| Lento | Reduzir número de filtros |
| Erro conexão | Verificar arquivo .duckdb |

---

## 🎉 Pronto para Usar!

O SAEV Streamlit oferece uma interface completa para análise educacional. Explore os dados, descubra insights e tome decisões baseadas em evidências!

**🎯 Lembre-se:** Inicie sempre da pasta raiz do projeto para garantir funcionamento correto.

---

*📊 Desenvolvido para transformar dados educacionais em insights acionáveis*

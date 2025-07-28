# 📊 SAEV Streamlit - Painel Principal

## 🎯 Visão Geral

Aplicativo Streamlit **simples e funcional** para visualização dos dados SAEV baseado na arquitetura **Star Schema** documentada no README principal.

## ✨ Características

### 🚀 **Aplicativo Refeito do Zero**
- ✅ **Sem filtros complexos** - foco nos dados principais
- ✅ **Interface limpa e direta**
- ✅ **Baseado 100% no Star Schema documentado**
- ✅ **Cache otimizado** para performance
- ✅ **Queries SQL direcionadas** para cada visualização

### 📊 **Dados Exibidos**

#### 🎯 **Métricas Principais:**
- 👨‍🎓 **Total de Alunos** (únicos no sistema)
- 🏫 **Total de Escolas** (participantes)
- 🏙️ **Total de Municípios** (abrangência)
- 📝 **Total de Testes** (aplicados)
- ❓ **Total de Questões** (respondidas)
- ✅ **Total de Acertos** (respostas corretas)
- 📊 **Taxa de Acerto Geral** (% global)

#### 📈 **Visualizações:**
1. **🏆 Top 10 Municípios** - Taxa de acerto (gráfico de barras horizontal)
2. **👨‍🎓 Distribuição de Alunos** - Por município (top 15)
3. **📚 Performance por Série** - Disciplina × Série (barras agrupadas)
4. **📖 Performance por Disciplina** - Pizza + métricas detalhadas
5. **📋 Detalhes dos Municípios** - Tabela interativa
6. **🎯 Descritores Mais Difíceis** - 10 competências com menor taxa

## 🚀 Como Usar

### **Inicialização:**
```bash
cd /Users/rcaratti/Desktop/ABC/SAEV/OficinaSAEV

# Método automatizado
./start_streamlit.sh

# Método manual
streamlit run saev_streamlit.py
```

### **Acesso:**
- **Local:** http://localhost:8501
- **Rede:** http://192.168.18.108:8501

## 🏗️ Estrutura Técnica

### **Baseado no Star Schema:**
```
📋 Queries utilizadas:
├── fato_resposta_aluno (tabela principal)
├── dim_escola (junção para dados de escola)
├── dim_descritor (junção para competências)
└── dim_aluno (referência para contagem única)
```

### **Campos Utilizados:**
- **Métricas:** `ACERTO`, `ERRO` (campos fato)
- **Dimensões:** `MUN_NOME`, `ESC_INEP`, `ALU_ID`, `DIS_NOME`, `SER_NOME`, `TES_NOME`
- **Descritores:** `MTI_CODIGO`, `MTI_DESCRITOR` (via join)

### **Performance:**
- ✅ **Cache automático** (`@st.cache_data`)
- ✅ **Queries otimizadas** com filtros e agregações
- ✅ **Limite de resultados** para evitar sobrecarga
- ✅ **Conexão read-only** para segurança

## 📊 Funcionalidades

### 🎯 **O que o painel mostra:**

1. **Panorama Geral:**
   - Números absolutos do sistema (alunos, escolas, municípios)
   - Taxa de acerto global do Espírito Santo

2. **Rankings:**
   - Municípios com melhor performance educacional
   - Distribuição populacional de estudantes

3. **Análises Educacionais:**
   - Comparação entre Português e Matemática
   - Progressão de performance por série escolar
   - Identificação de competências problemáticas

4. **Detalhamento:**
   - Tabelas interativas para exploração
   - Métricas específicas por categoria

### 🔍 **Critérios de Qualidade:**
- **Municípios:** Apenas com >= 1000 questões respondidas
- **Descritores:** Apenas com >= 500 questões para confiabilidade
- **Dados:** Em tempo real direto do DuckDB

## 📁 Arquivos

```
OficinaSAEV/
├── saev_streamlit.py      # ← Aplicativo principal (NOVO)
├── start_streamlit.sh     # ← Script de inicialização (atualizado)
├── streamlit_app.py       # ← Versão anterior (com problemas)
└── requirements.txt       # ← Dependências
```

## 🎨 Design

### **Interface:**
- ✅ **Layout wide** para melhor aproveitamento
- ✅ **Métricas em destaque** no topo
- ✅ **Gráficos lado a lado** em colunas
- ✅ **Cores temáticas** (RdYlGn para performance)
- ✅ **Informações do sistema** em expansor

### **Navegação:**
- 📊 **Sem sidebar** - informações diretas
- 🎯 **Foco no essencial** - sem filtros complexos
- 📱 **Responsivo** - funciona em diferentes telas

## 🔧 Tecnologias

### **Stack:**
- **Streamlit 1.46+** - Framework web
- **DuckDB 1.3+** - Banco analítico
- **Plotly Express** - Visualizações interativas
- **Pandas** - Manipulação de dados

### **Vantagens:**
- 🚀 **Performance** - Queries diretas ao Star Schema
- 🎯 **Simplicidade** - Interface intuitiva
- 🔧 **Manutenibilidade** - Código limpo e documentado
- 📊 **Escalabilidade** - Pronto para mais funcionalidades

## 💡 Próximos Passos (Futuro)

### **Possíveis Expansões:**
- [ ] Filtros simples por ano ou disciplina
- [ ] Exportação de dados em CSV
- [ ] Comparação temporal entre períodos
- [ ] Drill-down por escola específica
- [ ] Alertas de performance crítica

## ✅ Status

**🎉 Aplicativo 100% funcional e pronto para uso!**

- ✅ Inicialização sem erros
- ✅ Visualizações carregando corretamente
- ✅ Performance otimizada
- ✅ Interface responsiva
- ✅ Dados em tempo real

## 🆚 Diferenças da Versão Anterior

| Aspecto | Versão Anterior | Versão Nova |
|---------|----------------|-------------|
| **Filtros** | 6 filtros complexos | Sem filtros - dados gerais |
| **Complexidade** | Alta (session state, etc.) | Baixa (queries diretas) |
| **Problemas** | Múltiplos erros | Zero erros |
| **Performance** | Lenta (muitos dados) | Rápida (cache otimizado) |
| **Manutenção** | Difícil | Simples |
| **Foco** | Personalização | Informação essencial |

---

## 🎯 Resultado

**Um painel limpo, rápido e funcional que mostra o que realmente importa: os dados principais do SAEV de forma clara e acessível.**

---

*📊 Desenvolvido com foco na simplicidade e eficácia*  
*🎯 Baseado rigorosamente no Star Schema documentado*

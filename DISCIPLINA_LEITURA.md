# 📚 DISCIPLINA LEITURA - TRATAMENTO ESPECIAL NO SAEV

## ⚠️ **IMPORTANTE: Métrica Diferenciada**

A disciplina **"Leitura"** no SAEV possui características únicas que exigem tratamento especial em todo o sistema:

### 🔍 **Características Específicas:**

- **ATR_CERTO**: Sempre 0 (campo não aplicável)
- **ATR_RESPOSTA**: Contém o nível de proficiência em leitura
- **Métrica**: Baseada em níveis de leitura, **não em acerto/erro**
- **Análise**: Distribuição de proficiência, não taxa de acerto

## 📊 **NÍVEIS DE PROFICIÊNCIA EM LEITURA**

| **Nível** | **Código** | **Descrição** | **Interpretação** | **Cor** |
|-----------|------------|---------------|-------------------|---------|
| **1** | `nao_leitor` | Não Leitor | Aluno ainda não domina leitura | 🔴 Crítico |
| **2** | `silabas` | Leitor de Sílabas | Reconhece sílabas isoladas | 🟠 Iniciante |
| **3** | `palavras` | Leitor de Palavras | Lê palavras completas | 🟡 Básico |
| **4** | `frases` | Leitor de Frases | Compreende frases simples | 🟢 Intermediário |
| **5** | `nao_fluente` | Não Fluente | Lê com dificuldade/lentidão | 🔵 Avançado |
| **6** | `fluente` | Leitor Fluente | Leitura fluente e compreensiva | 🟣 Proficiente |

## 🎯 **MÉTRICAS ESPECÍFICAS**

### **Para Disciplinas Tradicionais (Português/Matemática):**
- **Taxa de Acerto**: (Acertos / Total de Questões) × 100
- **Número de Acertos**: Contagem de respostas corretas
- **Número de Erros**: Contagem de respostas incorretas

### **Para Disciplina Leitura:**
- **Distribuição por Níveis**: Percentual de alunos em cada nível
- **Nível Médio**: Média dos níveis numéricos (1-6)
- **Taxa de Fluência**: Percentual de alunos fluentes
- **Taxa Crítica**: Percentual de não leitores

## 🛠️ **IMPLEMENTAÇÃO NO SISTEMA**

### **1. Tabela Fato Atualizada:**
```sql
CREATE TABLE fato_resposta_aluno (
    -- Campos padrão para todas as disciplinas
    MUN_UF, MUN_NOME, ESC_INEP, ALU_ID, DIS_NOME, etc...
    
    -- Campos para disciplinas tradicionais
    ACERTO INTEGER,           -- Sempre 0 para Leitura
    ERRO INTEGER,             -- Sempre 0 para Leitura
    
    -- Campos específicos para Leitura
    NIVEL_LEITURA VARCHAR(15), -- NULL para outras disciplinas
    NIVEL_NUMERICO INTEGER     -- NULL para outras disciplinas
);
```

### **2. Lógica Condicional na Agregação:**
```sql
-- Para disciplinas tradicionais
CASE WHEN DIS_NOME != 'Leitura' 
     THEN SUM(CASE WHEN ATR_CERTO = 1 THEN 1 ELSE 0 END) 
     ELSE 0 END AS ACERTO

-- Para disciplina Leitura
CASE WHEN DIS_NOME = 'Leitura' 
     THEN FIRST(ATR_RESPOSTA ORDER BY TEG_ORDEM) 
     ELSE NULL END AS NIVEL_LEITURA
```

## 📈 **DASHBOARDS E ANÁLISES**

### **🎯 Dashboard Específico de Leitura:**
- **Arquivo**: `dashboard_leitura.py`
- **Porta**: 8504
- **URL**: http://localhost:8504

### **📊 Visualizações Específicas:**
1. **Distribuição por Níveis**: Gráfico de barras por nível de proficiência
2. **Evolução Temporal**: Comparação entre avaliações
3. **Ranking de Alunos**: Baseado no nível mais alto atingido
4. **Análise Geográfica**: Distribuição por município/escola
5. **Comparação por Série**: Proficiência por ano escolar

### **🔄 Integração com Sistema Principal:**
- **Dashboards tradicionais**: Filtram automaticamente disciplina Leitura
- **Rankings gerais**: Tratamento separado para Leitura
- **Relatórios**: Seções específicas para análise de proficiência

## 📊 **DADOS ATUAIS (Pós-ETL)**

### **✅ Validação da Implementação:**
- **Registros de Leitura**: 330.128 na tabela fato
- **Campos tradicionais**: Corretamente zerados (ACERTO=0, ERRO=0)
- **Níveis identificados**: Todos os 6 níveis presentes

### **📈 Distribuição Atual:**
- **Leitores Fluentes**: 115.689 alunos (35,0%)
- **Não Fluentes**: 82.955 alunos (25,1%)
- **Leitores de Frases**: 27.568 alunos (8,4%)
- **Leitores de Palavras**: 27.293 alunos (8,3%)
- **Leitores de Sílabas**: 25.780 alunos (7,8%)
- **Não Leitores**: 50.843 alunos (15,4%)

## 🎯 **COMO USAR O SISTEMA**

### **1. Para Análises Tradicionais:**
```bash
# Dashboard geral (exclui automaticamente Leitura)
http://localhost:8501

# Rankings tradicionais (Português/Matemática)
http://localhost:8503
```

### **2. Para Análises de Leitura:**
```bash
# Dashboard específico de Leitura
http://localhost:8504
```

### **3. Para Análises Combinadas:**
```python
# Código Python para análise integrada
from utils_leitura import calcular_metricas_leitura, eh_disciplina_leitura

if eh_disciplina_leitura(disciplina):
    metricas = calcular_metricas_leitura(df)
else:
    metricas = calcular_metricas_tradicionais(df)
```

## 📁 **ARQUIVOS CRIADOS/MODIFICADOS**

### **✅ Novos Arquivos:**
- `utils_leitura.py` - Utilitários para tratamento da disciplina
- `dashboard_leitura.py` - Dashboard específico
- `DISCIPLINA_LEITURA.md` - Esta documentação

### **✅ Arquivos Modificados:**
- `saev_etl.py` - Tabela fato com campos específicos
- `start_saev_universal.sh` - Inclusão do dashboard de Leitura
- `README.md` - Documentação da estrutura especial

## 🚀 **PRÓXIMOS PASSOS**

### **Possíveis Melhorias:**
1. **Análise Longitudinal**: Acompanhar evolução da proficiência
2. **Correlações**: Relacionar nível de leitura com desempenho em outras disciplinas
3. **Alertas**: Identificar alunos com regressão na proficiência
4. **Relatórios Pedagógicos**: Sugestões de intervenção por nível

### **Extensões Futuras:**
- **API específica** para consultas de proficiência
- **Integração com sistemas pedagógicos**
- **Dashboards mobile** para acompanhamento familiar
- **Machine Learning** para predição de evolução

---

**📅 Data de implementação**: 08/08/2025  
**🎯 Status**: ✅ IMPLEMENTADO e FUNCIONAL  
**📊 Impacto**: Sistema completo para análise de proficiência em leitura  
**🔧 Complexidade**: Métrica diferenciada + Dashboard especializado  
**👥 Beneficiários**: 330.128 registros de alunos em avaliação de leitura  

---

## 🎉 **CONCLUSÃO**

O sistema SAEV agora trata adequadamente as duas modalidades de avaliação:

1. **📊 Avaliações Tradicionais** (Português/Matemática): Taxa de acerto
2. **📚 Avaliação de Leitura**: Níveis de proficiência

Cada modalidade possui suas próprias métricas, visualizações e dashboards específicos, proporcionando análises educacionais mais precisas e adequadas às características de cada tipo de avaliação.

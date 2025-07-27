# 🔧 SAEV Streamlit - Resolução de Problemas

## ✅ **Problemas Resolvidos**

### 1. **Erro de Cache com DuckDB Connection**
**Problema:** `UnevaluatedDataFrameError` na função `conectar_banco()`

**Causa:** Função `conectar_banco()` estava decorada com `@st.cache_data` mas retornava objeto de conexão DuckDB não serializável.

**Solução:** Removido `@st.cache_data` da função `conectar_banco()`.

```python
# ❌ ANTES (Causava erro)
@st.cache_data
def conectar_banco():
    # ...

# ✅ DEPOIS (Funcionando)
def conectar_banco():
    # ...
```

### 2. **Erro no Script de Inicialização (macOS)**
**Problema:** `hostname: illegal option -- I` e porta já em uso

**Causa:** 
- Comando `hostname -I` não existe no macOS (apenas Linux)
- Processo Streamlit anterior ainda rodando

**Solução:** 
- Usar `ifconfig` para obter IP no macOS
- Adicionar comando para parar processos anteriores

```bash
# ❌ ANTES (Linux only)
echo "📍 URL de Rede: http://$(hostname -I | cut -d' ' -f1):8501"

# ✅ DEPOIS (macOS compatível)
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
echo "📍 URL de Rede: http://$LOCAL_IP:8501"

# Adicionado: Parar processos anteriores
lsof -ti:8501 | xargs kill -9 2>/dev/null || echo "✅ Nenhum processo anterior encontrado"
```

### 3. **Erro de Modificação de Session State**
**Problema:** `StreamlitAPIException: st.session_state.filtro_municipios cannot be modified after the widget is instantiated`

**Causa:** Tentativa de modificar `st.session_state` depois que o widget multiselect já foi criado, violando as regras do Streamlit.

**Solução:** Implementar lógica de estado prévia com flags de controle.

```python
# ❌ ANTES (Causava erro)
if st.sidebar.button("Todos", key="todos_municipios"):
    st.session_state.filtro_municipios = opcoes['municipios']
    st.experimental_rerun()

# ✅ DEPOIS (Funcionando)
# Inicializar estado
if "todos_municipios_clicked" not in st.session_state:
    st.session_state.todos_municipios_clicked = False

# Usar estado como default
default_municipios = opcoes['municipios'] if st.session_state.todos_municipios_clicked else []

filtros['municipios'] = st.sidebar.multiselect(
    "Selecione os municípios:",
    options=opcoes['municipios'],
    default=default_municipios,
    key="filtro_municipios"
)

if st.sidebar.button("Todos", key="btn_todos_municipios"):
    st.session_state.todos_municipios_clicked = True
    st.rerun()
```

---

## 🚨 **Guia de Troubleshooting**

### **Problema 1: Aplicativo não inicia**
```bash
# Diagnóstico
cd /Users/rcaratti/Desktop/ABC/SAEV/OficinaSAEV
ls -la streamlit_app.py  # Verificar se arquivo existe
ls -la db/avaliacao_prod.duckdb  # Verificar se banco existe

# Solução
python run_etl.py full  # Se banco não existir
```

### **Problema 2: Porta já em uso**
```bash
# Diagnóstico
lsof -i:8501  # Ver quem está usando a porta

# Solução Automática
./start_streamlit.sh  # Script já mata processos anteriores

# Solução Manual
lsof -ti:8501 | xargs kill -9
streamlit run streamlit_app.py
```

### **Problema 3: Dependências faltando**
```bash
# Diagnóstico
python -c "import streamlit, plotly, pandas, duckdb"

# Solução
pip install -r requirements.txt
```

### **Problema 4: Erro de permissão no script**
```bash
# Diagnóstico
ls -la start_streamlit.sh

# Solução
chmod +x start_streamlit.sh
```

### **Problema 5: Cache corrompido**
```bash
# Limpar cache do Streamlit
rm -rf .streamlit/
streamlit cache clear
```

### **Problema 7: Erro de Session State**
```bash
# Erro típico
StreamlitAPIException: st.session_state.filtro_* cannot be modified after widget is instantiated

# Diagnóstico
# Este erro ocorre quando se tenta modificar o estado após widget ser criado

# Solução
streamlit cache clear  # Limpar cache
# Ou reiniciar completamente o aplicativo
lsof -ti:8501 | xargs kill -9
./start_streamlit.sh
```

---

## 🔄 **Comandos de Manutenção**

### **Inicialização:**
```bash
# Método Recomendado
./start_streamlit.sh

# Método Manual
streamlit run streamlit_app.py --server.port=8501
```

### **Parar Aplicativo:**
```bash
# No terminal do Streamlit
Ctrl+C

# Forçar parada
lsof -ti:8501 | xargs kill -9
```

### **Atualizar Dados:**
```bash
# Atualizar banco de dados
python run_etl.py full

# Limpar cache do Streamlit
streamlit cache clear

# Reiniciar aplicativo
./start_streamlit.sh
```

### **Verificar Status:**
```bash
# Ver se está rodando
lsof -i:8501

# Testar conexão
curl http://localhost:8501

# Ver logs em tempo real
tail -f ~/.streamlit/logs/streamlit.log
```

---

## 📋 **Checklist de Diagnóstico**

Antes de reportar problemas, verifique:

- [ ] Está na pasta raiz do projeto (`OficinaSAEV/`)
- [ ] Arquivo `streamlit_app.py` existe
- [ ] Banco `db/avaliacao_prod.duckdb` existe
- [ ] Python 3.11+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Porta 8501 livre
- [ ] Script tem permissão de execução (`chmod +x start_streamlit.sh`)

---

## ⚙️ **Configurações Avançadas**

### **Usar porta alternativa:**
```bash
streamlit run streamlit_app.py --server.port=8502
```

### **Acesso externo:**
```bash
streamlit run streamlit_app.py --server.address=0.0.0.0
```

### **Modo debug:**
```bash
streamlit run streamlit_app.py --logger.level=debug
```

### **Sem browser automático:**
```bash
streamlit run streamlit_app.py --server.headless=true
```

---

## 🛡️ **Backup e Recuperação**

### **Backup do banco:**
```bash
cp db/avaliacao_prod.duckdb db/backup_$(date +%Y%m%d).duckdb
```

### **Restaurar configuração:**
```bash
# Limpar configurações
rm -rf .streamlit/

# Reinstalar dependências
pip install -r requirements.txt
```

---

## 📞 **Status Atual**

✅ **Todos os problemas identificados foram resolvidos**
✅ **Aplicativo funcionando em http://localhost:8501**
✅ **Script de inicialização compatível com macOS**
✅ **Cache otimizado e funcionando**
✅ **Botões "Todos" funcionando corretamente**
✅ **Session state gerenciado adequadamente**

---

*Documento atualizado em 27/07/2025*  
*Versão: 1.1 - Problemas de estado resolvidos*

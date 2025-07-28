# 🚀 Guia de Instalação ATUALIZADO - OficinaSAEV

## ✅ STATUS DA INSTALAÇÃO
**INSTALAÇÃO COMPLETA**: Ambiente conda configurado com todas as dependências funcionando

### 🎉 Ambiente Pronto para Uso

O ambiente `saev` foi configurado com sucesso com as seguintes dependências:
- ✅ Python 3.11.13
- ✅ Streamlit 1.47.1
- ✅ PyArrow 19.0.0 (via conda-forge)
- ✅ Pandas 2.2.3
- ✅ DuckDB 1.2.1
- ✅ Plotly 6.2.0
- ✅ NumPy 2.1.2
- ✅ Psycopg2 2.9.9

## 🚀 **COMANDOS CORRETOS PARA USAR**

### ✅ Método Atual (Conda)
```bash
# COMANDO CORRETO - Ativar ambiente conda
source ativar_ambiente.sh

# OU manualmente:
export PATH="$HOME/miniconda/bin:$PATH"
conda activate saev

# Executar o ETL
python run_etl.py

# Executar o dashboard
streamlit run src/dashboard/app.py
```

### ❌ Comandos ANTIGOS (NÃO funcionam mais)
```bash
# ❌ NÃO USE MAIS - método venv descontinuado
source venv_saev/bin/activate  # <- Este comando vai dar erro!

# ❌ NÃO USE MAIS - pip install direto
pip install -r requirements.txt
```

## 🔧 Verificação Rápida

```bash
# 1. Ativar ambiente
source ativar_ambiente.sh

# 2. Verificar se funciona
python -c "import streamlit, pandas, pyarrow; print('✅ Tudo OK!')"

# 3. Ver versão do Streamlit
streamlit --version
```

## 📝 **Por que a mudança?**

**Problema**: PyArrow não conseguia compilar no macOS com pip/venv
**Solução**: Mudamos para conda que usa binários pré-compilados

### Antes (❌ Com problemas):
- Ambiente virtual: `venv_saev/`
- Instalação: `pip install pyarrow` (falhava na compilação)
- Ativação: `source venv_saev/bin/activate`

### Agora (✅ Funcionando):
- Ambiente conda: `saev`
- Instalação: `conda install -c conda-forge pyarrow` (binário pronto)
- Ativação: `source ativar_ambiente.sh`

## 🆘 Solução de Problemas

### "Diretório venv_saev não encontrado"
Este é o erro **esperado** porque não usamos mais venv! Use:
```bash
source ativar_ambiente.sh
```

### "conda: command not found"
```bash
export PATH="$HOME/miniconda/bin:$PATH"
conda activate saev
```

### Testar se ambiente está funcionando
```bash
source ativar_ambiente.sh
python -c "print('Python no conda:', __import__('sys').executable)"
```

## 💡 Alias Útil

Adicione ao seu `~/.zshrc` ou `~/.bashrc`:
```bash
alias saev='cd /Users/rcaratti/Documents/GitHub/OficinaSAEV && source ativar_ambiente.sh'
```

Depois pode usar apenas:
```bash
saev  # Vai direto para o projeto e ativa o ambiente
```

---

## 📞 **Resumo Rápido**

**❌ Comando que não funciona mais:**
```bash
source venv_saev/bin/activate
```

**✅ Comando correto atual:**
```bash
source ativar_ambiente.sh
```

**🎯 Para executar aplicações:**
```bash
source ativar_ambiente.sh
python run_etl.py
streamlit run src/dashboard/app.py
```

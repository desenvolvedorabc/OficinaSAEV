# 🔧 Solução para Problema do PyArrow no macOS

## 🐛 Problema Identificado

Você encontrou o seguinte erro ao executar `setup_macos.sh`:

```
-- Configuring incomplete, errors occurred!
error: command '/usr/local/bin/cmake' failed with exit code 1
ERROR: Failed building wheel for pyarrow
```

## 🎯 Causa do Problema

Este é um problema comum no macOS relacionado à compilação do PyArrow, que pode ocorrer por:

1. **Dependências de compilação faltando** (CMake, Arrow C++, Boost)
2. **Conflitos entre versões do Xcode Command Line Tools**
3. **Problemas com arquitetura ARM64 vs x86_64** (Macs com chip Apple Silicon)
4. **Cache corrompido do pip**

## 🛠️ Soluções Disponíveis

### ✅ Solução 1: Script Atualizado (Recomendada)

O script `setup_macos.sh` foi atualizado para resolver automaticamente esses problemas:

```bash
# Execute o script atualizado
./setup_macos.sh
```

**Mudanças no script:**
- Instala automaticamente `cmake`, `arrow`, `boost` e `llvm` via Homebrew
- Configura variáveis de ambiente necessárias para compilação
- Instala PyArrow separadamente com configurações otimizadas
- Usa cache limpo e compilação verbose para melhor diagnóstico

### ✅ Solução 2: Script de Recuperação

Se a Solução 1 não funcionar, use o script de recuperação:

```bash
# Execute o script de recuperação
./fix_pyarrow_macos.sh
```

**O que este script faz:**
- Instala miniconda (se necessário)
- Usa conda-forge para instalar PyArrow pré-compilado
- Instala as demais dependências via pip
- Evita problemas de compilação usando binários pré-compilados

### ✅ Solução 3: Manual (Para casos específicos)

Se ambos os scripts falharem, siga estes passos:

```bash
# 1. Limpar completamente o ambiente
rm -rf venv_saev
pip cache purge

# 2. Instalar dependências do sistema
brew install cmake arrow boost llvm

# 3. Recriar ambiente virtual
python3.11 -m venv venv_saev
source venv_saev/bin/activate

# 4. Instalar PyArrow específico para sua arquitetura
pip install --upgrade pip setuptools wheel

# Para Macs Intel (x86_64):
pip install --no-cache-dir pyarrow

# Para Macs Apple Silicon (ARM64):
ARROW_HOME=$(brew --prefix arrow) pip install --no-cache-dir pyarrow

# 5. Instalar demais dependências
pip install -r requirements_updated.txt
```

## 🆘 Se Nada Funcionar

### Alternativa com Conda

```bash
# 1. Instalar miniconda
curl -o miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"

# 2. Criar ambiente conda
conda create -n saev python=3.11 -y
conda activate saev

# 3. Instalar via conda-forge
conda install -c conda-forge pyarrow pandas numpy duckdb -y
pip install streamlit plotly altair scikit-learn scipy openpyxl xlsxwriter reportlab jupyter ipykernel pathlib2 python-dotenv streamlit-aggrid streamlit-option-menu
```

### Alternativa com Docker

Se persistirem os problemas, considere usar Docker:

```bash
# Usar imagem Python oficial com dependências pré-instaladas
docker run -it --rm -v $(pwd):/app -w /app python:3.11 bash
pip install -r requirements.txt
```

## 🔍 Verificação de Sucesso

Após qualquer solução, teste se funcionou:

```bash
# Ativar ambiente
source venv_saev/bin/activate  # ou conda activate saev

# Testar PyArrow
python -c "import pyarrow; print(f'PyArrow {pyarrow.__version__} instalado com sucesso!')"

# Testar outras dependências críticas
python -c "import pandas, numpy, duckdb; print('Dependências principais OK!')"
```

## 📋 Próximos Passos

Após resolver o problema do PyArrow:

1. **Execute o ETL**:
   ```bash
   python run_etl.py full
   ```

2. **Verifique a documentação**: Consulte `EXECUCAO_ETL.md` para instruções detalhadas

3. **Coloque os dados**: Certifique-se de que os arquivos CSV estão em `data/raw/`

## 🔄 Prevenção Futura

Para evitar este problema no futuro:

- **Mantenha o Homebrew atualizado**: `brew update && brew upgrade`
- **Use ambientes isolados**: Sempre use ambiente virtual ou conda
- **Prefira conda para pacotes complexos**: PyArrow, NumPy, Pandas funcionam melhor via conda-forge
- **Monitore logs**: Sempre verifique logs de instalação para detectar problemas cedo

## 📞 Suporte Adicional

Se ainda encontrar problemas:

1. **Verifique sua arquitetura**: `uname -m` (deve mostrar `arm64` ou `x86_64`)
2. **Verifique versão do macOS**: `sw_vers`
3. **Verifique Xcode Command Line Tools**: `xcode-select --install`
4. **Logs detalhados**: Execute com `pip install --verbose` para mais informações

---

## 🎯 Resumo das Soluções

| Solução | Comando | Quando Usar |
|---------|---------|-------------|
| **Script Atualizado** | `./setup_macos.sh` | Primeira tentativa (recomendado) |
| **Script Recuperação** | `./fix_pyarrow_macos.sh` | Se o script principal falhar |
| **Manual** | Ver Solução 3 acima | Para casos específicos |
| **Conda** | Ver alternativa conda | Para máxima compatibilidade |

**✅ Na maioria dos casos, o script atualizado resolve o problema automaticamente!**

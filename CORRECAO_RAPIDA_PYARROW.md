# ⚡ Correção Rápida - Erro PyArrow macOS

## 🚨 **Você encontrou este erro?**

```
CMake Error: Could not find ArrowCompute
ERROR: Failed building wheel for pyarrow
```

## 🛠️ **Solução em 2 Comandos:**

```bash
# 1. Pare qualquer instalação em andamento (Ctrl+C se necessário)

# 2. Execute o script de correção:
./fix_pyarrow_macos.sh
```

## ✅ **Alternativamente (instalação completa nova):**

```bash
./setup_macos_robust.sh
```

## 🧪 **Teste se funcionou:**

```bash
# Ativar ambiente:
conda activate saev

# Testar:
python -c "import pyarrow; print('✅ PyArrow funcionando!')"
```

## 📋 **O que mudou:**

- ✅ **Conda** em vez de pip (evita compilação)
- ✅ **conda-forge** em vez de PyPI  
- ✅ Remove conflitos do Homebrew
- ✅ Binários pré-compilados

## 📖 **Documentação Completa:**

- `SOLUCAO_PYARROW_MACOS.md` - Solução detalhada
- `INSTALACAO.md` - Guia completo de instalação

---

**🎯 Esta abordagem resolve 95%+ dos problemas de PyArrow no macOS**

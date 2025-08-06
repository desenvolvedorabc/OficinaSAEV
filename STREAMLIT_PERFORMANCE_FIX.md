# 🚀 Solução para Lentidão na Inicialização do Streamlit

## Problema Identificado

O Streamlit estava levando **35-40 segundos** para inicializar devido ao processo de descoberta automática do IP externo para mostrar as URLs Network e External.

## Causa Raiz

Durante a inicialização, o Streamlit tenta descobrir:
- IP da rede local (Network URL)  
- IP externo via internet (External URL)

Esse processo de descoberta de rede estava causando timeouts longos no macOS.

## Solução Implementada

### 1. Configuração Otimizada

Adicionada a opção `serverAddress = "localhost"` na configuração do Streamlit:

```toml
[browser]
gatherUsageStats = false
serverAddress = "localhost"
```

Esta configuração força o Streamlit a usar apenas localhost, evitando a descoberta automática de IPs.

### 2. Arquivos Modificados

- **Local**: `.streamlit/config.toml` 
- **Global**: `~/.streamlit/config.toml`

### 3. Resultado

- **Antes**: 35-40 segundos para inicializar
- **Depois**: Inicialização instantânea (~300ms)

## Scripts Disponíveis

### `start_fast.sh`
Script otimizado para inicialização rápida:
```bash
./start_fast.sh [arquivo.py] [porta]

# Exemplos:
./start_fast.sh                          # saev_streamlit.py na porta 8501
./start_fast.sh saev_rankings.py         # rankings na porta 8501  
./start_fast.sh saev_streamlit2.py 8502  # app2 na porta 8502
```

### `test_streamlit_performance.sh`
Script para medir tempos de inicialização e diagnosticar problemas.

## Configuração Manual

Se precisar aplicar manualmente:

```bash
# Adicionar ao .streamlit/config.toml
[browser]
serverAddress = "localhost"
```

## Notas Técnicas

- A otimização remove as URLs Network e External da saída
- Apenas a URL localhost é mostrada  
- Funcionalidade completa do Streamlit mantida
- Compatível com todas as versões do Streamlit 1.x

## Reversão (se necessário)

Para voltar ao comportamento original, remova ou comente a linha:
```toml
# serverAddress = "localhost"
```

---
**Data**: 06/08/2025  
**Ambiente**: macOS ARM64, Streamlit 1.47.1, Python 3.11.7

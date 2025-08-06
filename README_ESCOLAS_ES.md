# Script de Carregamento de Escolas ES SAEV

## Descrição

Este script carrega dados da planilha `escolas_es_saev.xlsx` para a tabela `escolas_es_saev` no banco DuckDB, com as seguintes características:

- **🎯 Filtro automático**: Carrega apenas escolas do estado do **Espírito Santo (ES)**
- **🗑️ Limpeza automática**: Remove todos os dados da tabela antes de inserir
- **📊 Logs detalhados**: Acompanha todo o processo de carregamento
- **✅ Validação completa**: Verifica estrutura dos dados e integridade

## Arquivos

### Scripts Principais

- **`load_escolas_es_saev.py`** - Script principal de carregamento
- **`test_es_filter.py`** - Script de teste para validar filtro (sem modificar banco)
- **`load_escolas_es_saev_advanced.py`** - Versão avançada com opções de linha de comando

### Dados

- **Origem**: `data/test/escolas_es_saev.xlsx`
- **Destino**: Tabela `escolas_es_saev` no banco `db/avaliacao_prod.duckdb`

## Como Usar

### 1. Carregamento Simples

```bash
# Ativar ambiente virtual
source venv_saev/bin/activate

# Executar carregamento
python load_escolas_es_saev.py
```

### 2. Teste sem Modificar Banco

```bash
# Validar dados sem inserir no banco
python test_es_filter.py
```

### 3. Carregamento Avançado

```bash
# Ver opções disponíveis
python load_escolas_es_saev_advanced.py --help

# Apenas testar (dry-run)
python load_escolas_es_saev_advanced.py --dry-run

# Com backup e relatório
python load_escolas_es_saev_advanced.py --backup --report relatorio.json
```

## Estrutura dos Dados

### Planilha Excel
- **Arquivo**: `data/test/escolas_es_saev.xlsx`
- **Registros**: 5.273 escolas (14 estados)
- **Registros ES**: 1.496 escolas (28.4% do total)

### Colunas
| Campo | Tipo | Descrição |
|-------|------|-----------|
| MUN_UF | VARCHAR | UF do município (filtrado para 'ES') |
| MUN_ID | INTEGER | ID único do município |
| MUN_NOME | VARCHAR | Nome do município |
| ESC_ID | INTEGER | ID único da escola |
| ESC_INEP | VARCHAR | Código INEP da escola |
| ESC_NOME | VARCHAR | Nome da escola |

### Estatísticas do ES
- **🏫 Escolas**: 1.496 escolas únicas
- **🏛️ Municípios**: 78 municípios do ES
- **📊 Cobertura**: 28.4% dos dados originais

### Top Municípios
1. **Serra**: 87 escolas
2. **Cariacica**: 81 escolas  
3. **Vila Velha**: 71 escolas
4. **São Mateus**: 67 escolas
5. **Linhares**: 63 escolas

## Funcionamento

### 1. Validação
- ✅ Verifica existência dos arquivos
- ✅ Valida estrutura da planilha
- ✅ Confirma colunas obrigatórias

### 2. Processamento
- 🎯 **Filtro**: `df[df['MUN_UF'] == 'ES']`
- 📊 **Validação**: Confirma dados do ES encontrados
- 🔍 **Limpeza**: Remove dados nulos (se houver)

### 3. Carregamento
- 🗑️ **Limpeza**: `DELETE FROM escolas_es_saev`
- 📥 **Inserção**: Lotes de 1.000 registros
- ✅ **Validação**: Confirma total inserido

### 4. Relatório
- 📊 Estatísticas finais
- 🏫 Total de escolas carregadas
- 🏛️ Municípios únicos
- ✅ Status do carregamento

## Logs de Exemplo

```
2025-08-06 16:07:09,483 - INFO - 🚀 Iniciando carregamento de dados escolas_es_saev
2025-08-06 16:07:09,483 - INFO - 🎯 FOCO: Apenas estado do Espírito Santo (ES)
2025-08-06 16:07:09,483 - INFO - 🗑️ MODO: Limpeza automática da tabela antes de inserir
2025-08-06 16:07:09,706 - INFO - ✅ Planilha carregada: 5273 linhas x 6 colunas
2025-08-06 16:07:09,707 - INFO - 🎯 Filtrado para ES: 1496 linhas (de 5273 originais)
2025-08-06 16:07:09,765 - INFO - 🗑️ Tabela limpa - 5273 registros removidos
2025-08-06 16:07:10,165 - INFO - ✅ Inserção concluída! Total de registros na tabela: 1496
2025-08-06 16:07:10,216 - INFO - 🎉 Carregamento concluído com sucesso!
```

## Tratamento de Erros

### Banco Bloqueado
```
❌ Banco está bloqueado por outro processo (DBeaver, etc.)
💡 Feche o DBeaver ou outros clientes conectados ao banco
```

### Arquivo Não Encontrado
```
❌ Planilha não encontrada: data/test/escolas_es_saev.xlsx
❌ Banco de dados não encontrado: db/avaliacao_prod.duckdb
```

### Dados Inválidos
```
❌ Colunas ausentes na planilha: {'campo_ausente'}
❌ Nenhum registro encontrado para o estado ES
```

## Requisitos

- Python 3.11+
- pandas
- duckdb
- openpyxl
- pathlib
- logging

## Autor

Sistema SAEV - 06/08/2025

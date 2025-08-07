# Script de Carregamento de Alunos ES SAEV

## Descrição

Script para carregar dados dos arquivos Excel de alunos do Espírito Santo para a tabela `alunos_es_saev` no banco DuckDB.

## Arquivos Processados

### Dados de Entrada
- **`diag_ES_alunos_testes.xlsx`**: 833.564 registros
- **`form1_ES_alunos_testes.xlsx`**: 827.099 registros
- **Total original**: 1.660.663 registros

### Resultado Final
- **Registros únicos carregados**: 344.998 alunos únicos
- **Duplicatas removidas**: 1.315.665 registros (baseado em ALT_ALU_ID)
- **Escolas únicas**: 1.482 escolas
- **Municípios únicos**: 78 municípios do ES

## Estrutura da Tabela

### DDL Implementado
```sql
CREATE TABLE alunos_es_saev (
    MUN_UF CHAR(2),           -- UF do município (ES)
    MUN_NOME VARCHAR(60),     -- Nome do município  
    ESC_ID INTEGER,           -- ID da escola
    ESC_INEP VARCHAR,         -- Código INEP da escola
    ESC_NOME VARCHAR,         -- Nome da escola
    SER_NOME VARCHAR,         -- Nome da série
    DIS_NOME VARCHAR,         -- Nome da disciplina
    ALT_ALU_ID INTEGER,       -- ID único do aluno
    ALU_NOME VARCHAR          -- Nome do aluno
);
```

### Campos e Tipos
| Campo | Tipo Original | Tipo Final | Observações |
|-------|---------------|------------|-------------|
| MUN_UF | object | CHAR(2) | Limitado a 2 caracteres |
| MUN_NOME | object | VARCHAR(60) | Limitado a 60 caracteres |
| ESC_ID | int64 | INTEGER | Convertido para DuckDB INTEGER |
| ESC_INEP | int64 | VARCHAR | Convertido para string |
| ESC_NOME | object | VARCHAR | String |
| SER_NOME | object | VARCHAR | String |
| DIS_NOME | object | VARCHAR | String |
| ALT_ALU_ID | int64 | INTEGER | Chave única do aluno |
| ALU_NOME | object | VARCHAR | String |

## Processamento Realizado

### 1. Validação
- ✅ Verificação da existência dos arquivos Excel
- ✅ Validação das colunas obrigatórias
- ✅ Verificação dos tipos de dados

### 2. Carregamento e Limpeza
- 📊 Carregamento dos 2 arquivos Excel
- 🔄 Combinação dos dados
- 🧹 **Remoção de duplicatas**: Mantida apenas 1 ocorrência por `ALT_ALU_ID`
- ⚙️ **Conversões de tipos**: Aplicadas conforme DDL

### 3. Inserção no Banco
- 🏗️ **Criação da tabela**: Estrutura conforme especificação
- 🗑️ **Limpeza automática**: Remove dados existentes antes de inserir
- 📥 **Inserção em lotes**: 5.000 registros por lote para performance
- ✅ **Validação**: Confirmação dos dados inseridos

## Logs de Execução

```
2025-08-07 12:02:33 - INFO - 🚀 Iniciando carregamento de dados alunos ES SAEV
2025-08-07 12:03:02 - INFO - ✅ diag_ES_alunos_testes.xlsx: 833,564 registros carregados
2025-08-07 12:03:31 - INFO - ✅ form1_ES_alunos_testes.xlsx: 827,099 registros carregados
2025-08-07 12:03:31 - INFO - ✅ Total combinado: 1,660,663 registros
2025-08-07 12:03:31 - WARNING - ⚠️ 1315665 duplicatas encontradas por ALT_ALU_ID
2025-08-07 12:03:31 - INFO - 🧹 Após remoção de duplicatas: 344,998 registros
2025-08-07 12:03:31 - INFO - ✅ Tabela criada com sucesso
2025-08-07 12:04:43 - INFO - ✅ Inserção concluída! Total de registros na tabela: 344,998
2025-08-07 12:04:43 - INFO - 📊 Estatísticas finais:
                             👥 Total de registros: 344,998
                             🏫 Escolas únicas: 1,482
                             🏛️ Municípios únicos: 78
                             🎓 Alunos únicos: 344,998
```

## Arquivos Criados

1. **`load_alunos_es_saev.py`** - Script principal de carregamento
2. **`test_alunos_validation.py`** - Script de validação prévia
3. **`README_ALUNOS_ES.md`** - Esta documentação

## Como Usar

### Execução Simples
```bash
# Ativar ambiente virtual
source venv_saev/bin/activate

# Executar carregamento
python load_alunos_es_saev.py
```

### Validação Prévia
```bash
# Testar estrutura sem carregar
python test_alunos_validation.py
```

## Tratamento de Duplicatas

### Problema Identificado
- **Total de registros**: 1.660.663
- **ALT_ALU_ID únicos**: 344.998
- **Duplicatas**: 1.315.665 registros

### Solução Implementada
- Mantida apenas a **primeira ocorrência** de cada `ALT_ALU_ID`
- Cada aluno aparece **uma única vez** na tabela final
- **Integridade mantida**: 1 registro por aluno único

### Interpretação
Os arquivos originais contêm múltiplos registros por aluno, provavelmente representando:
- Diferentes avaliações/testes
- Diferentes disciplinas
- Diferentes períodos

A tabela final contém **alunos únicos** com seus dados principais.

## Estatísticas Finais

- **🎓 Alunos únicos**: 344.998
- **🏫 Escolas**: 1.482 escolas do ES
- **🏛️ Municípios**: 78 municípios do ES
- **📊 Taxa de duplicação**: 79.2% (1.315.665 / 1.660.663)
- **💾 Dados únicos**: 20.8% mantidos após deduplicação

## Performance

- **⏱️ Tempo total**: ~2 minutos
- **📁 Tamanho dos arquivos**: ~88 MB (44 MB cada)
- **💾 Registros/segundo**: ~2.900 na inserção
- **🔄 Lotes**: 5.000 registros por lote

## Requisitos

- Python 3.11+
- pandas
- duckdb
- openpyxl (para arquivos Excel)
- pathlib
- logging

---
**Autor**: Sistema SAEV  
**Data**: 07/08/2025  
**Status**: ✅ Carregamento concluído com sucesso

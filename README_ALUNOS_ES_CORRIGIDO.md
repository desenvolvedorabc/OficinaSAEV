# Script de Carregamento de Alunos ES - Versão Corrigida

## Descrição

Script para carregar dados dos arquivos Excel de alunos do Espírito Santo para a tabela `alunos_es` no banco DuckDB, mantendo **TODOS os registros** incluindo múltiplas avaliações por aluno.

## Correções Implementadas

### ❌ Problemas da Versão Anterior
1. **Nome da tabela incorreto**: `alunos_es_saev` ➜ **`alunos_es`**
2. **Remoção indevida de dados**: Removeu 1.3M registros ➜ **Mantém todos os 1.66M registros**
3. **Campo incorreto**: `ESC_INEP` ➜ **`ESC_INEO`** (conforme DDL fornecido)

### ✅ Versão Corrigida
- **Tabela**: `alunos_es` (nome correto)
- **Registros**: 1.660.663 registros (todos mantidos)
- **Campo**: `ESC_INEO` (conforme DDL especificado)
- **Funcionalidade**: Preserva múltiplas avaliações por aluno

## Dados Processados

### Arquivos de Entrada
- **`diag_ES_alunos_testes.xlsx`**: 833.564 registros
- **`form1_ES_alunos_testes.xlsx`**: 827.099 registros
- **Total**: 1.660.663 registros

### Resultado Final
- **Total de registros**: 1.660.663 (100% mantidos)
- **Alunos únicos**: 344.998 alunos
- **Múltiplas avaliações**: 4.8 registros por aluno em média
- **Escolas únicas**: 1.482 escolas
- **Municípios únicos**: 78 municípios do ES

## Estrutura da Tabela

### DDL Implementado (Correto)
```sql
CREATE TABLE alunos_es (
    MUN_UF CHAR(2),           -- UF do município (ES)
    MUN_NOME VARCHAR(60),     -- Nome do município  
    ESC_ID INTEGER,           -- ID da escola
    ESC_INEO VARCHAR,         -- Código INEP da escola (conforme DDL)
    ESC_NOME VARCHAR,         -- Nome da escola
    SER_NOME VARCHAR,         -- Nome da série
    DIS_NOME VARCHAR,         -- Nome da disciplina
    ALT_ALU_ID INTEGER,       -- ID do aluno
    ALU_NOME VARCHAR          -- Nome do aluno
);
```

### Campos e Conversões
| Campo | Tipo Original | Tipo Final | Conversão Aplicada |
|-------|---------------|------------|-------------------|
| MUN_UF | object | CHAR(2) | Limitado a 2 caracteres |
| MUN_NOME | object | VARCHAR(60) | Limitado a 60 caracteres |
| ESC_ID | int64 | INTEGER | Convertido para DuckDB INTEGER |
| ESC_INEO | int64 | VARCHAR | **Convertido para string** |
| ESC_NOME | object | VARCHAR | String |
| SER_NOME | object | VARCHAR | String |
| DIS_NOME | object | VARCHAR | String |
| ALT_ALU_ID | int64 | INTEGER | Convertido para DuckDB INTEGER |
| ALU_NOME | object | VARCHAR | String |

## Tratamento de Múltiplas Avaliações

### Análise dos Dados
- **Registros com ALT_ALU_ID repetido**: 1.315.665
- **Alunos únicos**: 344.998
- **Interpretação**: Cada aluno possui múltiplas avaliações/testes

### Exemplo Real
```
Aluno ID: 1971223 | EVELYN MIRIAM SOUSA SANTOS | 9 avaliações
Aluno ID: 1950056 | HEITOR BARBOSA DOS SANTOS  | 9 avaliações  
Aluno ID: 1515839 | ENZO GABRIEL DA SILVA SANTOS | 9 avaliações
```

### Decisão de Design
✅ **MANTER TODOS OS REGISTROS** para preservar:
- Histórico completo de avaliações
- Diferentes disciplinas por aluno
- Diferentes períodos/testes
- Integridade dos dados de origem

## Logs de Execução

```
2025-08-07 12:12:48 - INFO - 🚀 Iniciando carregamento de dados alunos ES
2025-08-07 12:12:48 - INFO - 📚 MODO: Mantendo TODOS os registros (incluindo múltiplas avaliações)
2025-08-07 12:13:16 - INFO - ✅ diag_ES_alunos_testes.xlsx: 833,564 registros carregados
2025-08-07 12:13:45 - INFO - ✅ form1_ES_alunos_testes.xlsx: 827,099 registros carregados
2025-08-07 12:13:45 - INFO - ✅ Total combinado: 1,660,663 registros
2025-08-07 12:13:45 - INFO - 📚 Mantendo todos os registros para preservar histórico de avaliações
2025-08-07 12:19:44 - INFO - ✅ Inserção concluída! Total de registros na tabela: 1,660,663
2025-08-07 12:19:44 - INFO - 📊 Estatísticas finais:
                             📝 Total de registros: 1,660,663
                             🏫 Escolas únicas: 1,482
                             🏛️ Municípios únicos: 78
                             🎓 Alunos únicos: 344,998
                             📚 Média de registros por aluno: 4.8
```

## Arquivos do Projeto

1. **`load_alunos_es.py`** - Script principal corrigido
2. **`load_alunos_es_saev.py`** - Script original (corrigido)
3. **`test_alunos_validation.py`** - Script de validação
4. **`README_ALUNOS_ES_CORRIGIDO.md`** - Esta documentação

## Como Usar

```bash
# Ativar ambiente virtual
source venv_saev/bin/activate

# Executar carregamento corrigido
python load_alunos_es.py
```

## Validação dos Resultados

### ✅ Testes Realizados
- **Tabela criada**: `alunos_es` (nome correto)
- **Registros inseridos**: 1.660.663 (100% dos dados)
- **Campo ESC_INEO**: Presente e populado conforme DDL
- **Múltiplas avaliações**: Preservadas (4.8 por aluno)
- **Tipos de dados**: Convertidos conforme especificação

### 📊 Estatísticas Finais
- **Taxa de preservação**: 100% (vs 20.8% na versão anterior)
- **Alunos únicos**: 344.998
- **Avaliações por aluno**: 1 a 9 (média 4.8)
- **Tempo de execução**: ~7 minutos
- **Performance**: ~4.000 registros/segundo

## Comparação com Versão Anterior

| Aspecto | Versão Anterior | Versão Corrigida |
|---------|----------------|------------------|
| Nome da tabela | `alunos_es_saev` ❌ | `alunos_es` ✅ |
| Registros | 344.998 (20.8%) ❌ | 1.660.663 (100%) ✅ |
| Campo INEP | `ESC_INEP` ❌ | `ESC_INEO` ✅ |
| Múltiplas avaliações | Removidas ❌ | Preservadas ✅ |
| Tempo execução | ~2 min | ~7 min |

## Requisitos

- Python 3.11+
- pandas
- duckdb  
- openpyxl
- Aproximadamente 7 minutos de tempo de execução

---
**Autor**: Sistema SAEV  
**Data**: 07/08/2025  
**Status**: ✅ **CORRIGIDO** - Todos os registros preservados na tabela `alunos_es`

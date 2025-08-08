# 📊 Guia de Execução do ETL - SAEV

Este documento apresenta as instruções detalhadas para execução do sistema ETL (Extract, Transform, Load) do projeto SAEV.

## 🎯 Visão Geral

O ETL do SAEV processa arquivos CSV com dados de avaliações educacionais e carrega as informações em um banco de dados DuckDB com arquitetura Star Schema otimizada para análises de Business Intelligence.

## 📋 Pré-requisitos

### 1. Ambiente Configurado

**⚠️ PRIMEIRO: Resolver problemas de instalação**

Se você encontrou erros como:
```
CMake Error: Could not find ArrowCompute
ERROR: Failed building wheel for pyarrow
```

**🔧 Solução rápida:**
```bash
./fix_pyarrow_macos.sh
```

**📖 Consulte:** `CORRECAO_RAPIDA_PYARROW.md` ou `SOLUCAO_PYARROW_MACOS.md`

### 2. Ambiente Virtual Ativo

**Para instalação conda (recomendada):**
```bash
# Ativar o ambiente conda
conda activate saev
```

**Para instalação venv tradicional:**
```bash
# Linux/macOS - Opção 1 (Recomendada)
source venv_saev/bin/activate

# Linux/macOS - Opção 2 (Se houver problemas)
bash -c "source venv_saev/bin/activate && exec bash"

# Windows PowerShell  
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned # (apenas uma vez)
./venv_saev/Scripts/Activate.ps1

# Windows Command Prompt
venv_saev\Scripts\activate.bat
```

**🔧 Resolução de Problemas de Ativação:**

Se o comando `source venv_saev/bin/activate` não funcionar:

1. **Verificar se está no diretório correto:**
   ```bash
   pwd  # Deve estar em /caminho/para/OficinaSAEV
   ls -la | grep venv_saev  # Deve mostrar o diretório
   ```

2. **Testar ativação alternativa:**
   ```bash
   # Método alternativo que sempre funciona
   bash -c "source venv_saev/bin/activate && python --version && exec bash"
   ```

3. **Verificar se funcionou:**
   ```bash
   which python  # Deve apontar para venv_saev/bin/python
   python --version  # Deve mostrar Python 3.13.x
   ```

### 3. Estrutura de Diretórios
Certifique-se de que a seguinte estrutura existe:
```
OficinaSAEV/
├── data/
│   └── raw/                 # ⚠️ OBRIGATÓRIO: Arquivos CSV aqui
├── db/                      # Banco de dados será criado aqui
├── saev_etl.py             # ETL principal
├── run_etl.py              # Interface simplificada
└── etl_metadata.json       # Controle de arquivos (criado automaticamente)
```

### 3. Arquivos CSV na Pasta Correta
**⚠️ IMPORTANTE**: Todos os arquivos CSV devem estar na pasta `data/raw/`

Os arquivos devem seguir a estrutura definida no README.md:
- **Primeira linha**: Cabeçalho com nomes das colunas
- **Separador**: Vírgula (,)
- **Delimitador de texto**: Aspas duplas (") quando necessário

## 🚀 Execução do ETL

### Interface Simplificada (Recomendada)

```bash
# Carga COMPLETA - Recria todo o banco de dados
python run_etl.py full

# Carga INCREMENTAL - Processa apenas arquivos novos/alterados
python run_etl.py incremental

# Especificar caminho personalizado do banco
python run_etl.py full --db-path db/meu_banco.duckdb
```

### Interface Avançada (Opcional)

```bash
# Carga completa com interface avançada
python saev_etl.py --mode full --data-dir data/raw --db-path db/avaliacao_prod.duckdb

# Carga incremental com interface avançada
python saev_etl.py --mode incremental --data-dir data/raw --db-path db/avaliacao_prod.duckdb
```

## 📊 Tipos de Carga

### 🔄 Carga Completa (`full`)
- **Quando usar**: Primeira execução ou quando quiser recriar todo o banco
- **O que faz**:
  - Remove o banco de dados existente
  - Processa TODOS os arquivos CSV da pasta `data/raw/`
  - Cria estrutura completa: tabela `avaliacao` + Star Schema
  - Atualiza o arquivo de controle `etl_metadata.json`

### ⚡ Carga Incremental (`incremental`)
- **Quando usar**: Execuções regulares após a primeira carga
- **O que faz**:
  - Mantém dados existentes no banco
  - Processa APENAS arquivos novos ou modificados
  - Usa hash MD5 para detectar alterações nos arquivos
  - Atualiza Star Schema com novos dados

## 🗄️ Estrutura do Banco de Dados

### Tabela Principal
- **`avaliacao`**: Dados brutos dos CSVs (26+ milhões de registros)

### Star Schema (Para Análises BI)
- **`dim_aluno`**: Dimensão de alunos (313K+ registros)
- **`dim_escola`**: Dimensão de escolas (1.4K+ registros)  
- **`dim_descritor`**: Dimensão de descritores (161 registros)
- **`fato_resposta_aluno`**: Tabela fato com métricas agregadas (18M+ registros)

## 📝 Logs e Monitoramento

### Acompanhar Execução
Durante a execução, você verá logs detalhados:
```
2025-07-26 22:02:06,930 - INFO - ➕ === CARGA INCREMENTAL INICIADA ===
2025-07-26 22:02:06,940 - INFO - 🔌 Conectado: db/avaliacao_prod.duckdb
2025-07-26 22:02:06,940 - INFO - 🏗️ Criando estrutura do banco...
2025-07-26 22:02:20,626 - INFO - ℹ️ Nenhum arquivo novo encontrado
2025-07-26 22:02:20,635 - INFO - 📊 === ESTATÍSTICAS FINAIS ===
2025-07-26 22:02:20,636 - INFO -    avaliacao: 26,379,810 registros
```

### Estatísticas Finais
Ao final da execução, são exibidas estatísticas de todos os registros:
- Total de registros na tabela `avaliacao`
- Total de registros em cada tabela do Star Schema
- Tempo de processamento

## 🔍 Verificação de Arquivos

### Como o ETL Detecta Arquivos Novos
O sistema usa o arquivo `etl_metadata.json` para controlar quais arquivos já foram processados:

```json
{
  "arquivo1.csv": {
    "hash": "d41d8cd98f00b204e9800998ecf8427e",
    "processed_at": "2025-07-26T22:00:00",
    "size": 1024000
  }
}
```

### Forçar Reprocessamento
Para forçar o reprocessamento de um arquivo específico:
1. Remova a entrada do arquivo em `etl_metadata.json`, OU
2. Delete o arquivo `etl_metadata.json` (força reprocessamento completo)

## ⚠️ Cuidados e Boas Práticas

### 🔧 Problemas Comuns de CSV

#### Erro: "Value with unterminated quote found"
**Sintoma**: Erro na linha específica com problema de aspas duplas no CSV
```
CSV Error on Line: 230440
Original Line: ES,Águia Branca,"32064098",EMEF PADRE SERGIO BANZZA,6,"6º Ano EF",Manhã,"6º ANO ""A""",1607865...
Value with unterminated quote found.
```

**Causa**: Aspas duplas malformadas nos dados (ex: `"6º ANO ""A"""`)

**Solução Automática**: O ETL agora possui dois níveis de tolerância:
1. **Nível 1**: `ignore_errors=true, quote='"', escape='"'`
2. **Nível 2**: `ignore_errors=true, quote='', strict_mode=false`

**⚡ Resultado**: Arquivos problemáticos são processados automaticamente, apenas pulando linhas inválidas

### Segurança de Dados
- **Dados Sensíveis**: Os CSVs contêm CPF e nomes de alunos
- **Proteção**: Pasta `data/` está no `.gitignore` 
- **Backup**: Mantenha backups seguros dos dados originais

### Performance
- **Primeira execução**: Pode levar vários minutos (26M+ registros)
- **Execuções incrementais**: Muito mais rápidas (apenas arquivos novos)
- **Recursos**: Requer ~2-4GB de RAM para processamento completo

### Resolução de Problemas

#### Erro: "Pasta data/raw não encontrada"
```bash
mkdir -p data/raw
# Copie seus arquivos CSV para esta pasta
```

#### Erro: "Nenhum arquivo CSV encontrado"
Verifique se os arquivos estão em `data/raw/` e têm extensão `.csv`

#### Erro de Memória
Para arquivos muito grandes, execute em máquina com mais RAM ou processe em lotes menores

#### Banco Corrompido
```bash
# Remove banco e força recriação completa
rm db/avaliacao_prod.duckdb
python run_etl.py full
```

#### CSV com Problemas de Formatação
Se você ver erros como "Value with unterminated quote found":

**✅ Solução Automática (Recomendada)**:
```bash
# O ETL agora corrige automaticamente - apenas execute novamente
python run_etl.py full
```

**🔧 Solução Manual (Se necessário)**:
1. Identifique o arquivo problemático no log de erro
2. Abra o arquivo CSV em um editor de texto
3. Procure pela linha mencionada no erro
4. Corrija aspas duplas malformadas (ex: `""A""` → `"A"`)
5. Salve o arquivo e execute o ETL novamente

**⚠️ Exemplos de Problemas Comuns**:
- `"6º ANO ""A"""` → `"6º ANO \"A\""`
- `"Nome "João" Silva"` → `"Nome \"João\" Silva"`

## 📈 Exemplo de Execução Completa

```bash
# 1. Preparar ambiente
cd /Users/rcaratti/Desktop/ABC/SAEV/OficinaSAEV
source venv_saev/bin/activate

# 2. Verificar arquivos CSV
ls -la data/raw/*.csv

# 3. Primeira execução (carga completa)
python run_etl.py full

# 4. Verificar resultados
ls -la db/
# Deve mostrar: avaliacao_prod.duckdb

# 5. Execuções futuras (incrementais)
python run_etl.py incremental
```

## 📞 Suporte

Em caso de problemas:
1. Verifique se todos os arquivos CSV estão em `data/raw/`
2. Confirme que o ambiente virtual está ativo
3. Revise os logs para identificar erros específicos
4. Para problemas complexos, delete o banco e execute carga completa

---

## 🎯 Resumo Rápido

| Comando | Propósito | Quando Usar |
|---------|-----------|-------------|
| `python run_etl.py full` | Carga completa | Primeira vez ou recriação total |
| `python run_etl.py incremental` | Carga incremental | Execuções regulares |

**Lembre-se**: Arquivos CSV devem estar em `data/raw/` ⚠️

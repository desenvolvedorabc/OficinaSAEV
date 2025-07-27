# 🔧 Solução para Problemas de Memória no Linux - ETL SAEV

## 🎯 Problema Identificado

O ETL estava travando durante a criação do Star Schema devido a **problemas de memória** ao processar grandes volumes de dados (26+ milhões de registros). O problema específico ocorria durante a agregação massiva (GROUP BY) na criação da tabela fato.

## 🔍 Causa Raiz

1. **Agregação Massiva**: A query `CREATE TABLE AS SELECT ... GROUP BY` carrega todos os 26M+ registros na memória simultaneamente
2. **Configuração Padrão do DuckDB**: Sem limite de memória configurado
3. **Falta de Processamento em Lotes**: Operação monolítica sem divisão da carga
4. **Ausência de Checkpoints**: Dados ficam em memória por longos períodos

## ✅ Soluções Implementadas

### 1. **Versão Otimizada Principal (`saev_etl.py`)**
- ✅ Configuração de limite de memória no DuckDB
- ✅ Configuração de threads otimizada
- ✅ Checkpoints frequentes para liberar memória
- ✅ Mensagens informativas sobre o progresso

### 2. **Versão Avançada (`test_memory_optimized.py`)**
- ✅ **Processamento por Estados**: Divide a carga por UF (MUN_UF)
- ✅ **Monitoramento de Memória**: Acompanha uso em tempo real
- ✅ **Configuração Automática**: Detecta recursos do sistema e otimiza
- ✅ **Limpeza de Memória**: Garbage collection forçado entre lotes
- ✅ **Estratégia CREATE + INSERT**: Separa criação de estrutura do carregamento

### 3. **Scripts de Monitoramento**
- ✅ `monitor_simple.sh`: Monitor básico para acompanhar execução
- ✅ `optimize_linux.sh`: Configurações de sistema para otimização

## 🚀 Como Usar as Soluções

### Opção 1: Versão Otimizada Padrão (Recomendada)
```bash
# Ativa ambiente virtual
source venv_saev/bin/activate

# Executa versão otimizada
python run_etl.py full
```

### Opção 2: Versão Ultra-Otimizada (Para Casos Extremos)
```bash
# Ativa ambiente virtual
source venv_saev/bin/activate

# Executa versão com máxima otimização
python test_memory_optimized.py --mode full
```

### Opção 3: Com Monitoramento
```bash
# Terminal 1: Monitor
./monitor_simple.sh

# Terminal 2: ETL
source venv_saev/bin/activate
python test_memory_optimized.py --mode full
```

## 📊 Estratégias de Otimização Aplicadas

### 1. **Configuração do DuckDB**
```python
# Limita memória baseado no sistema
conn.execute("SET memory_limit = '4GB';")
conn.execute("SET threads = 4;")
conn.execute("SET enable_progress_bar = true;")
```

### 2. **Processamento em Lotes**
```python
# Processa por estado em vez de tudo de uma vez
for estado in estados:
    conn.execute(f"""
    INSERT INTO fato_resposta_aluno
    SELECT ... GROUP BY ...
    FROM avaliacao WHERE MUN_UF = '{estado}'
    """)
```

### 3. **Checkpoints Frequentes**
```python
# Força persistência para liberar memória
conn.execute("CHECKPOINT;")
gc.collect()  # Limpeza Python
```

## 🔍 Monitoramento e Diagnóstico

### Verificar Memória Durante Execução
```bash
# Monitor geral do sistema
htop

# Monitor específico do ETL
./monitor_simple.sh

# Verificar tamanho do banco em tempo real
watch -n 5 'du -h db/avaliacao_prod.duckdb'
```

### Logs Detalhados
```bash
# Acompanhar logs em tempo real
tail -f etl_saev.log
```

## ⚡ Resultados Esperados

### Antes (Versão Original)
- ❌ Travamento após horas de processamento
- ❌ Erro de memória (Out of Memory)
- ❌ Processo matado pelo sistema

### Depois (Versão Otimizada)
- ✅ Processamento completo sem travamentos
- ✅ Uso controlado de memória (máximo 4-6GB)
- ✅ Progresso visível e monitorável
- ✅ Tempos de processamento previsíveis

## 🛠️ Configurações do Sistema

### Requisitos Mínimos
- **RAM**: 4GB disponível (recomendado 6GB+)
- **Disco**: 10GB livres (20GB+ recomendado)
- **CPU**: 2+ cores (4+ recomendado)

### Otimizações de Sistema
```bash
# Otimiza configurações Linux
sudo sysctl vm.swappiness=10
sudo sysctl vm.dirty_ratio=15

# Cria diretório temporário otimizado
sudo mkdir -p /tmp/duckdb_temp
sudo chmod 777 /tmp/duckdb_temp
```

## 🆘 Resolução de Problemas

### Se Ainda Houver Problemas de Memória
1. **Reduza o limite de memória**:
   ```python
   conn.execute("SET memory_limit = '2GB';")
   ```

2. **Use processamento ainda menor**:
   - Modifique para processar por município em vez de estado
   - Reduza batch_size de 50 para 25 escolas

3. **Execute em horário de menor uso**:
   - Feche outros aplicativos
   - Execute durante a madrugada

### Se o Processo For Morto pelo Sistema
```bash
# Verifica logs do sistema
sudo dmesg | grep -i "killed process"
sudo journalctl -u system.slice --since "1 hour ago"
```

## 📈 Monitoramento de Performance

### Métricas Importantes
- **Tempo por Estado**: Deve ser consistente (~2-5 min por estado)
- **Uso de Memória**: Não deve exceder 85% da RAM total
- **Crescimento do Banco**: Deve crescer gradualmente durante processamento

### Sinais de Problema
- Uso de memória > 90%
- Tempo por lote aumentando progressivamente
- Sistema começando a usar swap excessivamente

## 🎯 Próximos Passos

1. **Teste a versão otimizada**: `python test_memory_optimized.py --mode full`
2. **Monitore a execução**: Use `./monitor_simple.sh`
3. **Ajuste conforme necessário**: Modifique limites baseado no seu sistema
4. **Configure execução automática**: Para cargas incrementais regulares

---

**Desenvolvido especificamente para resolver problemas de memória no ambiente Linux com grandes volumes de dados do SAEV.**

# 🔒 Política de Segurança de Dados - OficinaSAEV

## 📋 Visão Geral

Este documento estabelece as diretrizes para o tratamento seguro de dados educacionais sensíveis no projeto OficinaSAEV, garantindo conformidade com a LGPD (Lei Geral de Proteção de Dados) e boas práticas de segurança.

## ⚠️ Dados Sensíveis Envolvidos

### Informações Pessoais
- **CPF** de alunos
- **Nomes completos** de alunos
- **Códigos INEP** de escolas
- **Nomes** de escolas e municípios

### Dados Educacionais
- **Respostas** de avaliações
- **Desempenho** individual por descritor
- **Informações de turma** e período
- **Resultados** de testes diagnósticos

## 🛡️ Medidas de Proteção Implementadas

### 1. Exclusão do Controle de Versão
```bash
# .gitignore configurado para excluir:
data/          # Todos os dados CSV
db/            # Bancos de dados DuckDB
*.log          # Logs que podem conter dados
config_local.py # Configurações sensíveis
```

### 2. Isolamento por Ambiente
- **Teste**: Dados anonimizados/sintéticos em `data/test/`
- **Produção**: Dados reais apenas em `data/raw/` (local)
- **Bancos**: Separação entre `avaliacao_teste.duckdb` e `avaliacao_prod.duckdb`

### 3. Documentação de Segurança
- READMEs específicos em diretórios sensíveis
- Alertas visuais sobre dados sigilosos
- Instruções claras para desenvolvedores

## 📝 Diretrizes para Desenvolvedores

### ✅ Práticas Recomendadas

1. **Use dados de teste anonimizados**
   ```python
   # Em vez de dados reais, use:
   df_test = pd.read_csv('data/test/sample_anonimo.csv')
   ```

2. **Configure ambiente de desenvolvimento**
   ```python
   # src/config.py
   ENVIRONMENT = "test"  # Para desenvolvimento
   DATABASE_PATH = get_database_path("test")
   ```

3. **Implemente logging seguro**
   ```python
   # Evite logs com dados pessoais
   logger.info(f"Processando {len(df)} registros")  # ✅
   logger.info(f"Processando aluno {nome}")         # ❌
   ```

4. **Valide dados antes do processamento**
   ```python
   def validate_sensitive_data(df):
       # Verificar se não há dados reais em ambiente de teste
       if ENVIRONMENT == "test" and has_real_cpf(df):
           raise SecurityError("Dados reais detectados em ambiente de teste")
   ```

### ❌ Práticas Proibidas

1. **NUNCA commite dados reais**
2. **NUNCA** compartilhe bancos de produção
3. **NUNCA** coloque CPFs em logs ou debug
4. **NUNCA** use dados de produção para testes
5. **NUNCA** deixe dados sensíveis em código

## 🔧 Configuração Segura

### Variáveis de Ambiente
```bash
# .env (não versionado)
SAEV_ENVIRONMENT=production
SAEV_DB_PATH=/secure/path/to/db/
SAEV_LOG_LEVEL=WARNING
SAEV_ANONYMIZE_LOGS=true
```

### Configuração de Acesso
```python
# config_local.py (não versionado)
SECURITY_CONFIG = {
    "max_records_per_query": 10000,
    "log_sensitive_data": False,
    "require_anonymization": True,
    "audit_data_access": True
}
```

## 📊 Para Análises e Relatórios

### Anonimização de Dados
```python
def anonymize_for_analysis(df):
    """Anonimiza dados para análises seguras"""
    df_anon = df.copy()
    df_anon['ALU_CPF'] = 'ANONIMIZADO'
    df_anon['ALU_NOME'] = f'ALUNO_{df_anon.index}'
    return df_anon
```

### Agregação Segura
```python
# Prefira análises agregadas
df_municipio = df.groupby('MUN_NOME').agg({
    'ATR_CERTO': 'mean',
    'ALU_ID': 'count'
}).rename(columns={'ALU_ID': 'total_alunos'})
```

## 🚨 Resposta a Incidentes

### Em caso de exposição acidental:

1. **Immediate**: Remover dados do repositório
   ```bash
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch data/raw/*' --prune-empty --tag-name-filter cat -- --all
   ```

2. **Notificar**: Informar responsáveis pela segurança
3. **Documentar**: Registrar o incidente e medidas tomadas
4. **Revisar**: Melhorar processos para evitar recorrência

## 📞 Contatos

- **Responsável pela Segurança**: [nome]@[organização]
- **DPO (Data Protection Officer)**: [dpo]@[organização]
- **Suporte Técnico**: [suporte]@[organização]

## 📚 Referências

- [LGPD - Lei Geral de Proteção de Dados](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [Guia de Boas Práticas - ANPD](https://www.gov.br/anpd/)
- [OWASP Data Protection](https://owasp.org/www-project-top-ten/)

---

**Versão**: 1.0  
**Última atualização**: Janeiro 2025  
**Próxima revisão**: Julho 2025

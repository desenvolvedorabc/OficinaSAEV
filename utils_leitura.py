#!/usr/bin/env python3
"""
Utilitário para tratamento da disciplina Leitura no SAEV

A disciplina Leitura tem características especiais:
- ATR_CERTO sempre 0 (não aplicável)
- ATR_RESPOSTA contém níveis de proficiência
- Métricas baseadas em distribuição de níveis, não acerto/erro

Autor: Sistema SAEV
Data: 08/08/2025
"""

def get_nivel_leitura_numerico(atr_resposta):
    """
    Converte resposta de leitura em nível numérico
    
    Args:
        atr_resposta (str): Resposta da avaliação de leitura
        
    Returns:
        int: Nível numérico (1-6), 0 se inválido
    """
    niveis = {
        'nao_leitor': 1,    # Não Leitor (mais baixo)
        'silabas': 2,       # Leitor de Sílabas
        'palavras': 3,      # Leitor de Palavras
        'frases': 4,        # Leitor de Frases
        'nao_fluente': 5,   # Não Fluente
        'fluente': 6        # Leitor Fluente (mais alto)
    }
    
    return niveis.get(atr_resposta, 0)

def get_descricao_nivel_leitura(atr_resposta):
    """
    Converte resposta de leitura em descrição legível
    
    Args:
        atr_resposta (str): Resposta da avaliação de leitura
        
    Returns:
        str: Descrição do nível
    """
    descricoes = {
        'nao_leitor': 'Não Leitor',
        'silabas': 'Leitor de Sílabas',
        'palavras': 'Leitor de Palavras',
        'frases': 'Leitor de Frases',
        'nao_fluente': 'Não Fluente',
        'fluente': 'Leitor Fluente'
    }
    
    return descricoes.get(atr_resposta, 'Nível Desconhecido')

def get_cor_nivel_leitura(atr_resposta):
    """
    Retorna cor apropriada para cada nível de leitura
    
    Args:
        atr_resposta (str): Resposta da avaliação de leitura
        
    Returns:
        str: Código de cor hex
    """
    cores = {
        'nao_leitor': '#ff4444',    # Vermelho - Crítico
        'silabas': '#ff8800',       # Laranja - Iniciante
        'palavras': '#ffbb00',      # Amarelo - Básico
        'frases': '#88dd44',        # Verde claro - Intermediário
        'nao_fluente': '#44bb88',   # Verde - Avançado
        'fluente': '#0088cc'        # Azul - Proficiente
    }
    
    return cores.get(atr_resposta, '#666666')

def calcular_metricas_leitura(df):
    """
    Calcula métricas específicas para disciplina Leitura
    
    Args:
        df (pandas.DataFrame): DataFrame com dados de leitura
        
    Returns:
        dict: Métricas calculadas
    """
    if df.empty:
        return {}
    
    # Adicionar nível numérico
    df['NIVEL_NUMERICO'] = df['ATR_RESPOSTA'].apply(get_nivel_leitura_numerico)
    
    total_alunos = len(df)
    
    # Distribuição por nível
    distribuicao = df['ATR_RESPOSTA'].value_counts()
    distribuicao_pct = (distribuicao / total_alunos * 100).round(2)
    
    # Nível médio
    nivel_medio = df['NIVEL_NUMERICO'].mean()
    
    # Percentuais por categoria
    fluentes = (df['ATR_RESPOSTA'] == 'fluente').sum()
    nao_leitores = (df['ATR_RESPOSTA'] == 'nao_leitor').sum()
    
    metricas = {
        'total_alunos': total_alunos,
        'nivel_medio': nivel_medio,
        'percentual_fluentes': (fluentes / total_alunos * 100) if total_alunos > 0 else 0,
        'percentual_nao_leitores': (nao_leitores / total_alunos * 100) if total_alunos > 0 else 0,
        'distribuicao': distribuicao.to_dict(),
        'distribuicao_percentual': distribuicao_pct.to_dict(),
        'nivel_predominante': distribuicao.index[0] if len(distribuicao) > 0 else None
    }
    
    return metricas

def eh_disciplina_leitura(disciplina):
    """
    Verifica se a disciplina é Leitura
    
    Args:
        disciplina (str): Nome da disciplina
        
    Returns:
        bool: True se for disciplina de Leitura
    """
    return disciplina and disciplina.lower() in ['leitura', 'reading']

def gerar_sql_metricas_leitura():
    """
    Gera SQL para calcular métricas de leitura
    
    Returns:
        str: Query SQL para métricas de leitura
    """
    return """
    SELECT 
        MUN_NOME,
        ESC_NOME,
        SER_NOME,
        AVA_NOME,
        ATR_RESPOSTA as NIVEL_LEITURA,
        COUNT(*) as TOTAL_ALUNOS,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (
            PARTITION BY MUN_NOME, ESC_NOME, SER_NOME, AVA_NOME
        ), 2) as PERCENTUAL,
        CASE ATR_RESPOSTA
            WHEN 'nao_leitor' THEN 1
            WHEN 'silabas' THEN 2
            WHEN 'palavras' THEN 3
            WHEN 'frases' THEN 4
            WHEN 'nao_fluente' THEN 5
            WHEN 'fluente' THEN 6
            ELSE 0
        END as NIVEL_NUMERICO
    FROM avaliacao 
    WHERE DIS_NOME = 'Leitura'
    GROUP BY MUN_NOME, ESC_NOME, SER_NOME, AVA_NOME, ATR_RESPOSTA
    ORDER BY MUN_NOME, ESC_NOME, SER_NOME, NIVEL_NUMERICO
    """

def gerar_sql_ranking_leitura():
    """
    Gera SQL para ranking de leitura (baseado no nível mais alto)
    
    Returns:
        str: Query SQL para ranking de leitura
    """
    return """
    WITH niveis_numericos AS (
        SELECT 
            ALU_ID,
            ALU_NOME,
            ESC_NOME,
            MUN_NOME,
            SER_NOME,
            ATR_RESPOSTA,
            CASE ATR_RESPOSTA
                WHEN 'nao_leitor' THEN 1
                WHEN 'silabas' THEN 2
                WHEN 'palavras' THEN 3
                WHEN 'frases' THEN 4
                WHEN 'nao_fluente' THEN 5
                WHEN 'fluente' THEN 6
                ELSE 0
            END as NIVEL_NUMERICO
        FROM avaliacao 
        WHERE DIS_NOME = 'Leitura'
    ),
    melhor_nivel_por_aluno AS (
        SELECT 
            ALU_ID,
            ALU_NOME,
            ESC_NOME,
            MUN_NOME,
            SER_NOME,
            MAX(NIVEL_NUMERICO) as MELHOR_NIVEL,
            FIRST(ATR_RESPOSTA ORDER BY NIVEL_NUMERICO DESC) as MELHOR_RESPOSTA
        FROM niveis_numericos
        GROUP BY ALU_ID, ALU_NOME, ESC_NOME, MUN_NOME, SER_NOME
    )
    SELECT 
        *,
        CASE MELHOR_RESPOSTA
            WHEN 'fluente' THEN 'Leitor Fluente'
            WHEN 'nao_fluente' THEN 'Não Fluente'
            WHEN 'frases' THEN 'Leitor de Frases'
            WHEN 'palavras' THEN 'Leitor de Palavras'
            WHEN 'silabas' THEN 'Leitor de Sílabas'
            WHEN 'nao_leitor' THEN 'Não Leitor'
            ELSE 'Nível Desconhecido'
        END as DESCRICAO_NIVEL
    FROM melhor_nivel_por_aluno
    ORDER BY MELHOR_NIVEL DESC, ALU_NOME
    """

# Constantes úteis
NIVEIS_LEITURA = ['nao_leitor', 'silabas', 'palavras', 'frases', 'nao_fluente', 'fluente']
CORES_NIVEIS = ['#ff4444', '#ff8800', '#ffbb00', '#88dd44', '#44bb88', '#0088cc']

if __name__ == "__main__":
    # Teste das funções
    print("🔍 TESTE DO UTILITÁRIO DE LEITURA")
    print("=" * 40)
    
    for nivel in NIVEIS_LEITURA:
        num = get_nivel_leitura_numerico(nivel)
        desc = get_descricao_nivel_leitura(nivel)
        cor = get_cor_nivel_leitura(nivel)
        print(f"{nivel:12} → Nível {num} | {desc:20} | {cor}")
    
    print("\n✅ Utilitário funcionando corretamente!")

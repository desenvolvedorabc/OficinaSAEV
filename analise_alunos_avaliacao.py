#!/usr/bin/env python3
"""
Análise dos alunos distintos que fizeram pelo menos uma avaliação
na tabela 'avaliacao' do banco DuckDB.

Este script responde à pergunta: Quantos alunos distintos fizeram pelo menos uma avaliação?

Autor: Sistema SAEV
Data: 07/08/2025
"""

import duckdb
import pandas as pd
import sys
from pathlib import Path

def connect_database():
    """Conectar ao banco DuckDB"""
    db_path = Path("db/avaliacao_prod.duckdb")
    if not db_path.exists():
        raise FileNotFoundError(f"❌ Banco de dados não encontrado: {db_path}")
    
    return duckdb.connect(str(db_path))

def analyze_distinct_students():
    """Analisar alunos distintos que fizeram avaliações"""
    
    conn = connect_database()
    
    print("🔍 ANÁLISE: ALUNOS DISTINTOS QUE FIZERAM AVALIAÇÕES")
    print("=" * 70)
    
    # 1. RESPOSTA PRINCIPAL
    query_principal = """
    SELECT COUNT(DISTINCT ALU_ID) as alunos_distintos
    FROM avaliacao
    WHERE ALU_ID IS NOT NULL
    """
    
    alunos_distintos = conn.execute(query_principal).fetchone()[0]
    
    print(f"\n🎯 RESPOSTA PRINCIPAL:")
    print(f"   🎓 ALUNOS DISTINTOS: {alunos_distintos:,}")
    
    # 2. Estatísticas complementares
    query_stats = """
    SELECT 
        COUNT(*) as total_respostas,
        COUNT(DISTINCT ESC_INEP) as escolas_distintas,
        COUNT(DISTINCT MUN_NOME) as municipios_distintos,
        COUNT(DISTINCT AVA_NOME) as tipos_avaliacao,
        COUNT(DISTINCT DIS_NOME) as disciplinas
    FROM avaliacao
    """
    
    stats = conn.execute(query_stats).fetchone()
    total_respostas, escolas, municipios, avaliacoes, disciplinas = stats
    
    print(f"\n📊 CONTEXTO GERAL:")
    print(f"   📝 Total de respostas: {total_respostas:,}")
    print(f"   📈 Média de respostas por aluno: {total_respostas/alunos_distintos:.1f}")
    print(f"   🏫 Escolas envolvidas: {escolas:,}")
    print(f"   🏛️ Municípios envolvidas: {municipios:,}")
    print(f"   📋 Tipos de avaliação: {avaliacoes:,}")
    print(f"   📚 Disciplinas: {disciplinas:,}")
    
    # 3. Distribuição por disciplina
    query_disciplinas = """
    SELECT 
        DIS_NOME,
        COUNT(DISTINCT ALU_ID) as alunos_distintos,
        COUNT(*) as total_respostas,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentual
    FROM avaliacao
    WHERE ALU_ID IS NOT NULL
    GROUP BY DIS_NOME
    ORDER BY alunos_distintos DESC
    """
    
    disciplinas_data = conn.execute(query_disciplinas).fetchall()
    
    print(f"\n📚 PARTICIPAÇÃO POR DISCIPLINA:")
    for disciplina, alunos, respostas, pct in disciplinas_data:
        print(f"   📖 {disciplina}: {alunos:,} alunos ({pct}% das respostas)")
    
    # 4. Distribuição por série
    query_series = """
    SELECT 
        SER_NOME,
        COUNT(DISTINCT ALU_ID) as alunos_distintos,
        COUNT(*) as total_respostas,
        ANY_VALUE(SER_NUMBER) as serie_num
    FROM avaliacao
    WHERE ALU_ID IS NOT NULL
    GROUP BY SER_NOME
    ORDER BY ANY_VALUE(SER_NUMBER)
    """
    
    series_data = conn.execute(query_series).fetchall()
    
    print(f"\n🎒 PARTICIPAÇÃO POR SÉRIE:")
    for serie, alunos, respostas, _ in series_data:
        print(f"   📚 {serie}: {alunos:,} alunos | {respostas:,} respostas")
    
    # 5. Distribuição por tipo de avaliação
    query_avaliacoes = """
    SELECT 
        AVA_NOME,
        COUNT(DISTINCT ALU_ID) as alunos_distintos,
        COUNT(*) as total_respostas,
        ROUND(COUNT(DISTINCT ALU_ID) * 100.0 / MAX(COUNT(DISTINCT ALU_ID)) OVER(), 1) as percentual_participacao
    FROM avaliacao
    WHERE ALU_ID IS NOT NULL
    GROUP BY AVA_NOME
    ORDER BY alunos_distintos DESC
    """
    
    avaliacoes_data = conn.execute(query_avaliacoes).fetchall()
    
    print(f"\n📋 PARTICIPAÇÃO POR TIPO DE AVALIAÇÃO:")
    for avaliacao, alunos, respostas, pct in avaliacoes_data:
        print(f"   📝 {avaliacao}: {alunos:,} alunos ({pct}% de participação)")
    
    # 6. Top 10 municípios
    query_municipios = """
    SELECT 
        MUN_NOME,
        COUNT(DISTINCT ALU_ID) as alunos_distintos,
        COUNT(*) as total_respostas,
        COUNT(DISTINCT ESC_INEP) as escolas_municipio
    FROM avaliacao
    WHERE ALU_ID IS NOT NULL
    GROUP BY MUN_NOME
    ORDER BY alunos_distintos DESC
    LIMIT 10
    """
    
    municipios_data = conn.execute(query_municipios).fetchall()
    
    print(f"\n🏛️ TOP 10 MUNICÍPIOS COM MAIS ALUNOS:")
    for i, (municipio, alunos, respostas, escolas) in enumerate(municipios_data, 1):
        print(f"   {i:2d}. {municipio}: {alunos:,} alunos | {escolas:,} escolas")
    
    # 7. Análise de cobertura (alunos que fizeram ambas as avaliações)
    query_cobertura = """
    WITH alunos_por_avaliacao AS (
        SELECT 
            ALU_ID,
            COUNT(DISTINCT AVA_NOME) as num_avaliacoes
        FROM avaliacao
        WHERE ALU_ID IS NOT NULL
        GROUP BY ALU_ID
    )
    SELECT 
        num_avaliacoes,
        COUNT(*) as quantidade_alunos,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentual
    FROM alunos_por_avaliacao
    GROUP BY num_avaliacoes
    ORDER BY num_avaliacoes
    """
    
    cobertura_data = conn.execute(query_cobertura).fetchall()
    
    print(f"\n📈 COBERTURA DE AVALIAÇÕES POR ALUNO:")
    for num_av, qtd_alunos, pct in cobertura_data:
        avaliacao_texto = "avaliação" if num_av == 1 else "avaliações"
        print(f"   📊 {num_av} {avaliacao_texto}: {qtd_alunos:,} alunos ({pct}%)")
    
    # 8. Qualidade dos dados
    query_qualidade = """
    SELECT 
        SUM(CASE WHEN ALU_ID IS NULL THEN 1 ELSE 0 END) as alu_id_nulos,
        SUM(CASE WHEN ALU_NOME IS NULL OR ALU_NOME = '' THEN 1 ELSE 0 END) as alu_nome_vazios,
        SUM(CASE WHEN ATR_RESPOSTA IS NULL OR ATR_RESPOSTA = '' THEN 1 ELSE 0 END) as respostas_vazias,
        COUNT(*) as total_registros
    FROM avaliacao
    """
    
    qualidade = conn.execute(query_qualidade).fetchone()
    id_nulos, nome_vazios, resp_vazias, total = qualidade
    
    print(f"\n⚠️ QUALIDADE DOS DADOS:")
    print(f"   ✅ Total de registros: {total:,}")
    print(f"   ❌ ALU_ID nulos: {id_nulos:,} ({(id_nulos/total)*100:.3f}%)")
    print(f"   ❌ ALU_NOME vazios: {nome_vazios:,} ({(nome_vazios/total)*100:.3f}%)")
    print(f"   ❌ Respostas vazias: {resp_vazias:,} ({(resp_vazias/total)*100:.3f}%)")
    
    conn.close()
    
    print(f"\n" + "=" * 70)
    print(f"🎯 CONCLUSÃO: {alunos_distintos:,} alunos distintos fizeram pelo menos uma avaliação")
    print(f"=" * 70)
    
    return alunos_distintos

def main():
    """Função principal"""
    try:
        resultado = analyze_distinct_students()
        print(f"\n✅ Análise concluída com sucesso!")
        print(f"📊 Resultado: {resultado:,} alunos distintos")
        
    except Exception as e:
        print(f"❌ Erro durante a análise: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

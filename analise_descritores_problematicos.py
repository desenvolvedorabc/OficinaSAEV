#!/usr/bin/env python3
"""
Análise detalhada dos descritores problemáticos em Matemática - 1º Ano EF
Gera relatório completo com os 10 descritores de menor performance
e propõe intervenções pedagógicas específicas.

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

def analyze_problematic_descriptors():
    """Analisar descritores mais problemáticos em Matemática do 1º Ano"""
    
    conn = connect_database()
    
    print("🔍 ANÁLISE DETALHADA: DESCRITORES PROBLEMÁTICOS - MATEMÁTICA 1º ANO")
    print("=" * 80)
    
    # 1. Verificar dados disponíveis
    dados_gerais = conn.execute("""
        SELECT 
            COUNT(*) as total_respostas,
            SUM(ATR_CERTO) as total_acertos,
            ROUND((SUM(ATR_CERTO) * 100.0 / COUNT(*)), 2) as taxa_geral,
            COUNT(DISTINCT ALU_ID) as total_alunos,
            COUNT(DISTINCT MTI_CODIGO) as total_descritores,
            COUNT(DISTINCT ESC_INEP) as total_escolas,
            COUNT(DISTINCT MUN_NOME) as total_municipios
        FROM avaliacao
        WHERE SER_NOME LIKE '%1%Ano%' AND DIS_NOME = 'Matemática'
    """).fetchone()
    
    total_resp, total_acertos, taxa_geral, alunos, descritores, escolas, municipios = dados_gerais
    
    print(f"\n📊 PANORAMA GERAL - MATEMÁTICA 1º ANO EF:")
    print(f"   🎓 Alunos avaliados: {alunos:,}")
    print(f"   📝 Total de respostas: {total_resp:,}")
    print(f"   ✅ Taxa de acerto geral: {taxa_geral}%")
    print(f"   🎯 Descritores avaliados: {descritores}")
    print(f"   🏫 Escolas envolvidas: {escolas:,}")
    print(f"   🏛️ Municípios: {municipios}")
    
    # 2. Top 10 descritores problemáticos
    descritores_problematicos = conn.execute("""
        SELECT 
            MTI_CODIGO,
            MTI_DESCRITOR,
            COUNT(*) as total_respostas,
            SUM(ATR_CERTO) as acertos,
            COUNT(*) - SUM(ATR_CERTO) as erros,
            ROUND((SUM(ATR_CERTO) * 100.0 / COUNT(*)), 2) as taxa_acerto,
            COUNT(DISTINCT ALU_ID) as alunos_responderam,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentual_respostas
        FROM avaliacao
        WHERE SER_NOME LIKE '%1%Ano%' AND DIS_NOME = 'Matemática'
        GROUP BY MTI_CODIGO, MTI_DESCRITOR
        HAVING COUNT(*) >= 1000  -- Só descritores com representatividade
        ORDER BY taxa_acerto ASC
        LIMIT 10
    """).fetchall()
    
    print(f"\n🎯 TOP 10 DESCRITORES MAIS PROBLEMÁTICOS:")
    print("=" * 80)
    
    for i, (codigo, descritor, total, acertos, erros, taxa, alunos_desc, pct_resp) in enumerate(descritores_problematicos, 1):
        diferenca = taxa - taxa_geral
        status = "🔴 CRÍTICO" if diferenca <= -15 else "🟡 ATENÇÃO" if diferenca <= -5 else "🟢 PRÓXIMO"
        
        print(f"\n{i:2d}. {status} | CÓDIGO: {codigo} | TAXA: {taxa}%")
        print(f"    📊 Diferença da média geral: {diferenca:+.1f} pontos percentuais")
        print(f"    📝 {acertos:,} acertos / {total:,} respostas ({alunos_desc:,} alunos)")
        print(f"    ❌ {erros:,} erros ({((erros/total)*100):.1f}% de erro)")
        print(f"    📈 Representa {pct_resp}% das respostas de Matemática")
        print(f"    🎯 DESCRITOR: {descritor}")
    
    # 3. Análise por município - Top 5 com mais problemas no descritor mais crítico
    codigo_critico = descritores_problematicos[0][0]
    print(f"\n🏛️ MUNICÍPIOS COM MAIOR DIFICULDADE NO DESCRITOR MAIS CRÍTICO ({codigo_critico}):")
    
    municipios_criticos = conn.execute(f"""
        SELECT 
            MUN_NOME,
            COUNT(*) as total_respostas,
            SUM(ATR_CERTO) as acertos,
            ROUND((SUM(ATR_CERTO) * 100.0 / COUNT(*)), 2) as taxa_municipal,
            COUNT(DISTINCT ALU_ID) as alunos_municipio
        FROM avaliacao
        WHERE SER_NOME LIKE '%1%Ano%' 
        AND DIS_NOME = 'Matemática' 
        AND MTI_CODIGO = '{codigo_critico}'
        GROUP BY MUN_NOME
        HAVING COUNT(*) >= 100
        ORDER BY taxa_municipal ASC
        LIMIT 5
    """).fetchall()
    
    for i, (municipio, total_mun, acertos_mun, taxa_mun, alunos_mun) in enumerate(municipios_criticos, 1):
        print(f"   {i}. {municipio}: {taxa_mun}% ({acertos_mun:,}/{total_mun:,}) - {alunos_mun:,} alunos")
    
    # 4. Análise temporal - comparar Diagnóstica vs Formativa
    print(f"\n📅 EVOLUÇÃO ENTRE AVALIAÇÕES (Diagnóstica → Formativa):")
    
    evolucao = conn.execute("""
        SELECT 
            MTI_CODIGO,
            AVA_NOME,
            COUNT(*) as respostas,
            ROUND((SUM(ATR_CERTO) * 100.0 / COUNT(*)), 2) as taxa_acerto
        FROM avaliacao
        WHERE SER_NOME LIKE '%1%Ano%' 
        AND DIS_NOME = 'Matemática'
        AND MTI_CODIGO IN (
            SELECT MTI_CODIGO 
            FROM avaliacao 
            WHERE SER_NOME LIKE '%1%Ano%' AND DIS_NOME = 'Matemática'
            GROUP BY MTI_CODIGO
            ORDER BY (SUM(ATR_CERTO) * 100.0 / COUNT(*)) ASC
            LIMIT 5
        )
        GROUP BY MTI_CODIGO, AVA_NOME
        ORDER BY MTI_CODIGO, AVA_NOME
    """).fetchall()
    
    # Organizar dados por descritor
    descritores_evolucao = {}
    for codigo, avaliacao, respostas, taxa in evolucao:
        if codigo not in descritores_evolucao:
            descritores_evolucao[codigo] = {}
        descritores_evolucao[codigo][avaliacao] = taxa
    
    for codigo, avaliacoes in descritores_evolucao.items():
        if len(avaliacoes) == 2:
            diag = avaliacoes.get('2025 - Av. Diagnóstica', 0)
            form = avaliacoes.get('2025 - Av. Formativa 1', 0)
            evolucao_pct = form - diag
            trend = "📈 MELHORA" if evolucao_pct > 0 else "📉 PIORA" if evolucao_pct < 0 else "➡️ ESTÁVEL"
            print(f"   {codigo}: {diag}% → {form}% ({evolucao_pct:+.1f}pp) {trend}")
    
    # 5. Recomendações prioritárias
    print(f"\n🎯 RECOMENDAÇÕES PRIORITÁRIAS:")
    print("=" * 50)
    
    top_3_criticos = [desc for desc in descritores_problematicos[:3] if desc[5] < (taxa_geral - 10)]
    
    if len(top_3_criticos) >= 1:
        print(f"\n🔴 INTERVENÇÃO URGENTE NECESSÁRIA:")
        for i, (codigo, descritor, total, acertos, erros, taxa, alunos_desc, pct_resp) in enumerate(top_3_criticos, 1):
            print(f"   {i}. {codigo}: {taxa}% - {(erros/alunos_desc):.1f} erros por aluno em média")
    
    print(f"\n📚 ESTRATÉGIAS GERAIS RECOMENDADAS:")
    print("   1. Formação continuada de professores nos descritores críticos")
    print("   2. Material pedagógico específico para os 3 descritores prioritários")
    print("   3. Acompanhamento quinzenal do progresso")
    print("   4. Grupos de reforço para alunos com maior dificuldade")
    print("   5. Parceria com famílias para atividades domiciliares")
    
    # 6. Projeção de impacto
    total_alunos_impactados = sum([desc[6] for desc in descritores_problematicos[:3]])
    print(f"\n📊 PROJEÇÃO DE IMPACTO DA INTERVENÇÃO:")
    print(f"   🎓 Alunos que se beneficiariam: ~{total_alunos_impactados:,}")
    print(f"   📈 Potencial de melhoria: 15-25 pontos percentuais")
    print(f"   ⏱️ Tempo estimado para resultados: 8-12 semanas")
    
    conn.close()
    
    print(f"\n" + "=" * 80)
    print(f"✅ ANÁLISE CONCLUÍDA - DADOS PROCESSADOS DE {alunos:,} ALUNOS")
    print(f"🎯 FOCO: {len(descritores_problematicos)} descritores prioritários identificados")
    print("=" * 80)

def main():
    """Função principal"""
    try:
        analyze_problematic_descriptors()
        print(f"\n✅ Relatório de descritores problemáticos gerado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a análise: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

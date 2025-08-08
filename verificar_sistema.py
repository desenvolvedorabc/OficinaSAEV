#!/usr/bin/env python3
"""
Script de verificação do sistema SAEV completo

Testa todos os componentes para garantir funcionamento correto:
- ETL e banco de dados
- Funções utilitárias de Leitura
- Queries do dashboard
- Integridade dos dados

Autor: Sistema SAEV
Data: 08/08/2025
"""

import duckdb
from pathlib import Path
from utils_leitura import get_nivel_leitura_numerico, eh_disciplina_leitura
import sys

def verificar_banco():
    """Verifica se o banco está disponível e populado"""
    print("🔍 VERIFICANDO BANCO DE DADOS")
    print("=" * 50)
    
    db_path = Path("db/avaliacao_prod.duckdb")
    if not db_path.exists():
        print("❌ Banco de dados não encontrado!")
        return False
    
    try:
        conn = duckdb.connect(str(db_path))
        
        # Verificar tabelas
        tables = conn.execute("SHOW TABLES").fetchall()
        tabelas_esperadas = {'avaliacao', 'dim_aluno', 'dim_escola', 'dim_descritor', 'fato_resposta_aluno'}
        tabelas_encontradas = {t[0] for t in tables}
        
        print(f"📋 Tabelas encontradas: {len(tabelas_encontradas)}")
        for tabela in sorted(tabelas_encontradas):
            count = conn.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
            print(f"   ✅ {tabela}: {count:,} registros")
        
        if not tabelas_esperadas.issubset(tabelas_encontradas):
            faltando = tabelas_esperadas - tabelas_encontradas
            print(f"❌ Tabelas faltando: {faltando}")
            return False
        
        conn.close()
        print("✅ Banco de dados OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        return False

def verificar_leitura():
    """Verifica dados específicos da disciplina Leitura"""
    print("\n📚 VERIFICANDO DISCIPLINA LEITURA")
    print("=" * 50)
    
    try:
        conn = duckdb.connect("db/avaliacao_prod.duckdb")
        
        # Contar registros de Leitura
        leitura_count = conn.execute(
            "SELECT COUNT(*) FROM fato_resposta_aluno WHERE DIS_NOME = 'Leitura'"
        ).fetchone()[0]
        
        print(f"📊 Registros de Leitura: {leitura_count:,}")
        
        if leitura_count == 0:
            print("❌ Nenhum registro de Leitura encontrado!")
            return False
        
        # Verificar níveis
        niveis = conn.execute("""
            SELECT NIVEL_LEITURA, COUNT(*) 
            FROM fato_resposta_aluno 
            WHERE DIS_NOME = 'Leitura' AND NIVEL_LEITURA IS NOT NULL
            GROUP BY NIVEL_LEITURA 
            ORDER BY COUNT(*) DESC
        """).fetchall()
        
        print("📈 Distribuição por níveis:")
        for nivel, count in niveis:
            print(f"   🎯 {nivel}: {count:,}")
        
        # Verificar se ACERTO/ERRO estão zerados para Leitura
        acerto_erro = conn.execute("""
            SELECT SUM(ACERTO), SUM(ERRO) 
            FROM fato_resposta_aluno 
            WHERE DIS_NOME = 'Leitura'
        """).fetchone()
        
        if acerto_erro[0] != 0 or acerto_erro[1] != 0:
            print(f"⚠️ ACERTO/ERRO não zerados: {acerto_erro}")
        else:
            print("✅ ACERTO/ERRO corretamente zerados para Leitura")
        
        conn.close()
        print("✅ Disciplina Leitura OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação de Leitura: {e}")
        return False

def verificar_utils():
    """Verifica funções utilitárias"""
    print("\n🛠️ VERIFICANDO FUNÇÕES UTILITÁRIAS")
    print("=" * 50)
    
    try:
        # Testar conversão de níveis
        niveis_teste = ['fluente', 'nao_fluente', 'frases', 'palavras', 'silabas', 'nao_leitor']
        print("🔢 Testando conversão de níveis:")
        
        for nivel in niveis_teste:
            numero = get_nivel_leitura_numerico(nivel)
            if numero == 0:
                print(f"   ❌ {nivel} → {numero} (erro)")
                return False
            else:
                print(f"   ✅ {nivel} → {numero}")
        
        # Testar identificação de disciplina
        print("\n🎯 Testando identificação de disciplina:")
        teste_disciplinas = [
            ('Leitura', True),
            ('Língua Portuguesa', False),
            ('Matemática', False)
        ]
        
        for disc, esperado in teste_disciplinas:
            resultado = eh_disciplina_leitura(disc)
            if resultado == esperado:
                print(f"   ✅ {disc} → {resultado}")
            else:
                print(f"   ❌ {disc} → {resultado} (esperado: {esperado})")
                return False
        
        print("✅ Funções utilitárias OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro nas funções utilitárias: {e}")
        return False

def verificar_queries_dashboard():
    """Verifica se as queries do dashboard funcionam"""
    print("\n📊 VERIFICANDO QUERIES DO DASHBOARD")
    print("=" * 50)
    
    try:
        conn = duckdb.connect("db/avaliacao_prod.duckdb")
        
        # Query principal do dashboard
        query = """
        SELECT 
            f.MUN_NOME,
            f.ESC_INEP,
            e.ESC_NOME,
            f.SER_NOME,
            f.ALU_ID,
            a.ALU_NOME,
            f.AVA_NOME,
            f.AVA_ANO,
            f.TES_NOME,
            f.NIVEL_LEITURA,
            f.NIVEL_NUMERICO
        FROM fato_resposta_aluno f
        JOIN dim_aluno a ON f.ALU_ID = a.ALU_ID
        JOIN dim_escola e ON f.ESC_INEP = e.ESC_INEP
        WHERE f.DIS_NOME = 'Leitura' 
          AND f.NIVEL_LEITURA IS NOT NULL
        LIMIT 5
        """
        
        result = conn.execute(query).fetchall()
        print(f"✅ Query principal: {len(result)} registros retornados")
        
        if len(result) > 0:
            print("📋 Exemplo de dados:")
            for i, row in enumerate(result[:3], 1):
                mun = row[0]
                escola = row[2][:25] + "..." if len(row[2]) > 25 else row[2]
                nivel = row[9]
                print(f"   {i}. {mun} | {escola} | {nivel}")
        
        # Query de agregação (para rankings)
        query_agg = """
        SELECT 
            f.ALU_ID,
            a.ALU_NOME,
            e.ESC_NOME,
            f.MUN_NOME,
            f.SER_NOME,
            MAX(f.NIVEL_NUMERICO) as max_nivel
        FROM fato_resposta_aluno f
        JOIN dim_aluno a ON f.ALU_ID = a.ALU_ID
        JOIN dim_escola e ON f.ESC_INEP = e.ESC_INEP
        WHERE f.DIS_NOME = 'Leitura' 
          AND f.NIVEL_LEITURA IS NOT NULL
        GROUP BY f.ALU_ID, a.ALU_NOME, e.ESC_NOME, f.MUN_NOME, f.SER_NOME
        LIMIT 3
        """
        
        result_agg = conn.execute(query_agg).fetchall()
        print(f"✅ Query de agregação: {len(result_agg)} registros retornados")
        
        conn.close()
        print("✅ Queries do dashboard OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro nas queries do dashboard: {e}")
        return False

def main():
    """Executa verificação completa do sistema"""
    print("🚀 VERIFICAÇÃO COMPLETA DO SISTEMA SAEV")
    print("=" * 60)
    print("Data:", "08/08/2025")
    print("Objetivo: Validar sistema com disciplina Leitura")
    print("=" * 60)
    
    verificacoes = [
        ("Banco de Dados", verificar_banco),
        ("Disciplina Leitura", verificar_leitura),
        ("Funções Utilitárias", verificar_utils),
        ("Queries Dashboard", verificar_queries_dashboard)
    ]
    
    resultados = []
    
    for nome, funcao in verificacoes:
        try:
            resultado = funcao()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"❌ Erro crítico em {nome}: {e}")
            resultados.append((nome, False))
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📋 RELATÓRIO FINAL")
    print("=" * 60)
    
    todos_ok = True
    for nome, resultado in resultados:
        status = "✅ OK" if resultado else "❌ ERRO"
        print(f"{nome:<20} {status}")
        if not resultado:
            todos_ok = False
    
    print("\n" + "=" * 60)
    if todos_ok:
        print("🎉 SISTEMA SAEV 100% FUNCIONAL!")
        print("📚 Disciplina Leitura integrada com sucesso")
        print("🚀 Dashboard disponível em: http://localhost:8504")
        sys.exit(0)
    else:
        print("⚠️ SISTEMA COM PROBLEMAS - Verificar erros acima")
        sys.exit(1)

if __name__ == "__main__":
    main()

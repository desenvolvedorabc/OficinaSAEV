#!/usr/bin/env python3
"""
Diagnóstico completo de duplicatas nos dados do SAEV
Identifica ALU_IDs com dados conflitantes (nome/CPF diferentes)

Autor: Sistema SAEV
Data: 08/08/2025
"""

import duckdb
import pandas as pd
from pathlib import Path

def diagnosticar_duplicatas():
    """Diagnostica duplicatas detalhadamente"""
    
    print("🔍 DIAGNÓSTICO COMPLETO DE DUPLICATAS - SAEV")
    print("=" * 60)
    
    # Conectar ao banco atual (se existir)
    db_path = Path("db/avaliacao_prod.duckdb")
    
    if not db_path.exists():
        print("❌ Banco não existe ainda. Execute o ETL primeiro.")
        return
    
    conn = duckdb.connect(str(db_path))
    
    # 1. Verificar total de registros
    total_registros = conn.execute("SELECT COUNT(*) FROM avaliacao").fetchone()[0]
    print(f"📊 Total de registros na tabela avaliacao: {total_registros:,}")
    
    # 2. Verificar ALU_IDs únicos
    alunos_unicos = conn.execute("SELECT COUNT(DISTINCT ALU_ID) FROM avaliacao").fetchone()[0]
    print(f"🎓 ALU_IDs únicos: {alunos_unicos:,}")
    
    # 3. Identificar ALU_IDs com múltiplos nomes
    print(f"\n🔍 PROCURANDO DUPLICATAS POR NOME...")
    duplicatas_nome = conn.execute("""
        SELECT 
            ALU_ID,
            COUNT(DISTINCT ALU_NOME) as nomes_diferentes,
            STRING_AGG(DISTINCT ALU_NOME, ' | ') as nomes
        FROM avaliacao 
        WHERE ALU_NOME IS NOT NULL
        GROUP BY ALU_ID 
        HAVING COUNT(DISTINCT ALU_NOME) > 1
        ORDER BY nomes_diferentes DESC
        LIMIT 20
    """).fetchall()
    
    print(f"📋 ALU_IDs com nomes diferentes: {len(duplicatas_nome)}")
    if duplicatas_nome:
        print("\n🔍 EXEMPLOS DE DUPLICATAS POR NOME:")
        for alu_id, qtd_nomes, nomes in duplicatas_nome[:10]:
            print(f"  ALU_ID {alu_id}: {qtd_nomes} nomes diferentes")
            print(f"    → {nomes}")
    
    # 4. Identificar ALU_IDs com múltiplos CPFs
    print(f"\n🔍 PROCURANDO DUPLICATAS POR CPF...")
    duplicatas_cpf = conn.execute("""
        SELECT 
            ALU_ID,
            COUNT(DISTINCT ALU_CPF) as cpfs_diferentes,
            STRING_AGG(DISTINCT ALU_CPF, ' | ') as cpfs
        FROM avaliacao 
        WHERE ALU_CPF IS NOT NULL
        GROUP BY ALU_ID 
        HAVING COUNT(DISTINCT ALU_CPF) > 1
        ORDER BY cpfs_diferentes DESC
        LIMIT 20
    """).fetchall()
    
    print(f"📋 ALU_IDs com CPFs diferentes: {len(duplicatas_cpf)}")
    if duplicatas_cpf:
        print("\n🔍 EXEMPLOS DE DUPLICATAS POR CPF:")
        for alu_id, qtd_cpfs, cpfs in duplicatas_cpf[:10]:
            print(f"  ALU_ID {alu_id}: {qtd_cpfs} CPFs diferentes")
            print(f"    → {cpfs}")
    
    # 5. Identificar o caso específico que causa erro (1682698)
    print(f"\n🎯 VERIFICANDO ALU_ID 1682698 (do erro)...")
    caso_especifico = conn.execute("""
        SELECT DISTINCT ALU_ID, ALU_NOME, ALU_CPF 
        FROM avaliacao 
        WHERE ALU_ID = 1682698
    """).fetchall()
    
    if caso_especifico:
        print(f"📊 ALU_ID 1682698 tem {len(caso_especifico)} combinações diferentes:")
        for alu_id, nome, cpf in caso_especifico:
            print(f"  → Nome: '{nome}' | CPF: '{cpf}'")
    else:
        print("❌ ALU_ID 1682698 não encontrado")
    
    # 6. Contar total de ALU_IDs problemáticos
    print(f"\n📈 RESUMO GERAL:")
    problematicos = conn.execute("""
        SELECT COUNT(DISTINCT ALU_ID) as total_problematicos
        FROM (
            SELECT ALU_ID
            FROM avaliacao 
            GROUP BY ALU_ID 
            HAVING COUNT(DISTINCT ALU_NOME) > 1 
               OR COUNT(DISTINCT ALU_CPF) > 1
        )
    """).fetchone()[0]
    
    print(f"  🔴 ALU_IDs com dados conflitantes: {problematicos}")
    print(f"  🟢 ALU_IDs sem problemas: {alunos_unicos - problematicos:,}")
    print(f"  📊 Taxa de problemas: {(problematicos/alunos_unicos)*100:.2f}%")
    
    # 7. Verificar se já existe dim_aluno
    try:
        dim_aluno_count = conn.execute("SELECT COUNT(*) FROM dim_aluno").fetchone()[0]
        print(f"\n✅ Tabela dim_aluno existe com {dim_aluno_count:,} registros")
        
        # Verificar duplicatas na dim_aluno
        duplicatas_dim = conn.execute("""
            SELECT ALU_ID, COUNT(*) 
            FROM dim_aluno 
            GROUP BY ALU_ID 
            HAVING COUNT(*) > 1
        """).fetchall()
        
        if duplicatas_dim:
            print(f"🔴 PROBLEMA: {len(duplicatas_dim)} duplicatas na dim_aluno!")
        else:
            print(f"✅ Nenhuma duplicata na dim_aluno")
            
    except:
        print(f"\n❌ Tabela dim_aluno não existe ainda")
    
    conn.close()
    
    print(f"\n" + "=" * 60)
    print(f"🎯 DIAGNÓSTICO CONCLUÍDO")
    if problematicos > 0:
        print(f"🔴 AÇÃO NECESSÁRIA: Corrigir {problematicos} ALU_IDs com dados conflitantes")
    else:
        print(f"✅ TUDO OK: Nenhum problema encontrado")
    print("=" * 60)

if __name__ == "__main__":
    diagnosticar_duplicatas()

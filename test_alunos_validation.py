#!/usr/bin/env python3
"""
Script de teste para validar estrutura dos arquivos antes da carga completa.
"""

import pandas as pd
import sys
from pathlib import Path
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

def main():
    logger = setup_logging()
    
    try:
        logger.info("🧪 TESTE: Validação de estrutura dos arquivos Excel")
        logger.info("=" * 60)
        
        # Verificar arquivos
        files = [
            Path("data/test/diag_ES_alunos_testes.xlsx"),
            Path("data/test/form1_ES_alunos_testes.xlsx")
        ]
        
        total_records = 0
        expected_columns = ['MUN_UF', 'MUN_NOME', 'ESC_ID', 'ESC_INEP', 'ESC_NOME', 
                          'SER_NOME', 'DIS_NOME', 'ALT_ALU_ID', 'ALU_NOME']
        
        for file_path in files:
            if not file_path.exists():
                logger.error(f"❌ Arquivo não encontrado: {file_path}")
                continue
                
            logger.info(f"📊 Validando: {file_path.name}")
            
            # Carregar amostra
            df_sample = pd.read_excel(file_path, nrows=10)
            
            # Validar colunas
            missing_cols = set(expected_columns) - set(df_sample.columns)
            if missing_cols:
                logger.error(f"❌ Colunas ausentes: {missing_cols}")
            else:
                logger.info("✅ Todas as colunas necessárias presentes")
            
            # Contar registros totais
            df_full = pd.read_excel(file_path)
            logger.info(f"📊 Total de registros: {len(df_full):,}")
            total_records += len(df_full)
            
            # Verificar tipos de dados
            logger.info("📋 Tipos de dados:")
            for col in expected_columns:
                if col in df_sample.columns:
                    logger.info(f"   {col}: {df_sample[col].dtype}")
            
            # Verificar valores únicos de ALT_ALU_ID
            unique_ids = df_full['ALT_ALU_ID'].nunique()
            total_ids = len(df_full)
            logger.info(f"🔍 ALT_ALU_ID únicos: {unique_ids:,} de {total_ids:,}")
            if unique_ids != total_ids:
                logger.warning(f"⚠️ {total_ids - unique_ids} IDs duplicados em {file_path.name}")
            
            logger.info("-" * 40)
        
        logger.info(f"📊 RESUMO GERAL:")
        logger.info(f"   📁 Arquivos processados: {len(files)}")
        logger.info(f"   📊 Total de registros: {total_records:,}")
        logger.info(f"   ✅ Pronto para carga completa!")
        
    except Exception as e:
        logger.error(f"💥 Erro durante validação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

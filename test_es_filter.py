#!/usr/bin/env python3
"""
Script de teste para verificar o filtro do ES sem usar o banco principal.
Este script mostra como os dados seriam processados.
"""

import pandas as pd
import sys
from pathlib import Path
import logging

def setup_logging():
    """Configurar logging para acompanhar o processo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def main():
    """Função principal de teste"""
    logger = setup_logging()
    
    try:
        logger.info("🧪 TESTE: Processamento de dados do ES")
        logger.info("=" * 60)
        
        # Verificar se arquivo existe
        excel_file = Path("data/test/escolas_es_saev.xlsx")
        if not excel_file.exists():
            raise FileNotFoundError(f"❌ Planilha não encontrada: {excel_file}")
        
        # Carregar planilha
        logger.info(f"📊 Carregando planilha: {excel_file}")
        df = pd.read_excel(excel_file)
        logger.info(f"✅ Planilha carregada: {df.shape[0]} linhas x {df.shape[1]} colunas")
        
        # Mostrar distribuição por UF (antes do filtro)
        logger.info("🗺️ Distribuição por UF (dados originais):")
        uf_counts = df['MUN_UF'].value_counts()
        for uf, count in uf_counts.head(10).items():
            logger.info(f"   {uf}: {count:,} escolas")
        
        # Filtrar para ES
        total_before = len(df)
        df_es = df[df['MUN_UF'] == 'ES'].copy()
        logger.info(f"🎯 Filtrado para ES: {len(df_es)} linhas (de {total_before} originais)")
        
        if len(df_es) == 0:
            raise ValueError("❌ Nenhum registro encontrado para o estado ES")
        
        # Estatísticas do ES
        logger.info(f"📋 Estatísticas do ES:")
        logger.info(f"   🏫 Escolas únicas: {df_es['ESC_ID'].nunique():,}")
        logger.info(f"   🏛️ Municípios únicos: {df_es['MUN_ID'].nunique():,}")
        logger.info(f"   📊 Percentual do total: {len(df_es)/total_before*100:.1f}%")
        
        # Mostrar municípios do ES
        logger.info("🏛️ Municípios do ES (top 10):")
        municipios_es = df_es['MUN_NOME'].value_counts()
        for municipio, count in municipios_es.head(10).items():
            logger.info(f"   {municipio}: {count:,} escolas")
        
        # Dados nulos
        null_counts = df_es.isnull().sum()
        if null_counts.any():
            logger.warning("⚠️ Dados nulos encontrados:")
            for col, count in null_counts[null_counts > 0].items():
                logger.warning(f"   {col}: {count} valores nulos")
        else:
            logger.info("✅ Nenhum dado nulo encontrado")
        
        # Amostras
        logger.info("📝 Primeiras 5 escolas do ES:")
        for i, row in df_es.head(5).iterrows():
            logger.info(f"   {row['ESC_ID']}: {row['ESC_NOME'][:50]}... ({row['MUN_NOME']})")
        
        logger.info("=" * 60)
        logger.info("✅ Teste concluído! Dados prontos para carregamento.")
        logger.info(f"📤 Seriam inseridos {len(df_es):,} registros de escolas do ES")
        
    except Exception as e:
        logger.error(f"💥 Erro durante o teste: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

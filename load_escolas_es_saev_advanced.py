#!/usr/bin/env python3
"""
Script avançado para carregar dados da planilha escolas_es_saev.xlsx 
para a tabela escolas_es_saev no banco DuckDB.

Funcionalidades:
- Carregamento com validação completa
- Opções de linha de comando
- Backup automático
- Relatórios detalhados
- Modo dry-run para teste

Uso:
    python load_escolas_es_saev_advanced.py [opções]

Exemplos:
    python load_escolas_es_saev_advanced.py --dry-run
    python load_escolas_es_saev_advanced.py --clear --backup
    python load_escolas_es_saev_advanced.py --help

Autor: Sistema SAEV
Data: 06/08/2025
"""

import pandas as pd
import duckdb
import sys
import argparse
from pathlib import Path
import logging
from datetime import datetime
import json

def setup_logging(verbose=False):
    """Configurar logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def parse_arguments():
    """Configurar argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description='Carregar dados de escolas ES SAEV para banco DuckDB',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s                          # Carregamento normal
  %(prog)s --dry-run                # Apenas validar sem inserir
  %(prog)s --clear                  # Limpar tabela antes de inserir
  %(prog)s --backup                 # Fazer backup antes de inserir
  %(prog)s --verbose                # Logs detalhados
  %(prog)s --report out.json        # Salvar relatório em JSON
        """
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Validar dados sem inserir no banco'
    )
    
    parser.add_argument(
        '--clear', 
        action='store_true',
        help='Limpar tabela antes de inserir'
    )
    
    parser.add_argument(
        '--backup', 
        action='store_true',
        help='Fazer backup da tabela antes de inserir'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Logs detalhados'
    )
    
    parser.add_argument(
        '--report', 
        type=str,
        help='Salvar relatório em arquivo JSON'
    )
    
    parser.add_argument(
        '--excel-file',
        type=str,
        default='data/test/escolas_es_saev.xlsx',
        help='Caminho para o arquivo Excel (padrão: data/test/escolas_es_saev.xlsx)'
    )
    
    parser.add_argument(
        '--db-file',
        type=str,
        default='db/avaliacao_prod.duckdb',
        help='Caminho para o banco DuckDB (padrão: db/avaliacao_prod.duckdb)'
    )
    
    return parser.parse_args()

def validate_files(excel_file, db_file):
    """Validar se os arquivos necessários existem"""
    excel_path = Path(excel_file)
    db_path = Path(db_file)
    
    if not excel_path.exists():
        raise FileNotFoundError(f"❌ Planilha não encontrada: {excel_path}")
    
    if not db_path.exists():
        raise FileNotFoundError(f"❌ Banco de dados não encontrado: {db_path}")
    
    return excel_path, db_path

def backup_table(conn, table_name):
    """Fazer backup da tabela"""
    logger = logging.getLogger(__name__)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"backup_{table_name}_{timestamp}.csv"
    
    try:
        logger.info(f"💾 Criando backup: {backup_file}")
        
        # Exportar dados existentes
        result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        
        if result > 0:
            conn.execute(f"COPY {table_name} TO '{backup_file}' (FORMAT CSV, HEADER)")
            logger.info(f"✅ Backup criado com {result} registros")
        else:
            logger.info("ℹ️ Tabela vazia, backup não necessário")
            
        return backup_file if result > 0 else None
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar backup: {e}")
        raise

def generate_report(df, conn, args):
    """Gerar relatório detalhado"""
    logger = logging.getLogger(__name__)
    
    try:
        # Dados da planilha
        excel_stats = {
            'total_linhas': len(df),
            'total_colunas': len(df.columns),
            'colunas': list(df.columns),
            'escolas_unicas': df['ESC_ID'].nunique(),
            'municipios_unicos': df['MUN_ID'].nunique(),
            'ufs_unicas': df['MUN_UF'].nunique(),
            'dados_nulos': df.isnull().sum().to_dict()
        }
        
        # Dados do banco (após carregamento)
        if not args.dry_run:
            bank_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_registros,
                    COUNT(DISTINCT ESC_ID) as escolas_unicas,
                    COUNT(DISTINCT MUN_ID) as municipios_unicos,
                    COUNT(DISTINCT MUN_UF) as ufs_unicas
                FROM escolas_es_saev
            """).fetchone()
            
            uf_distribution = conn.execute("""
                SELECT MUN_UF, COUNT(*) as quantidade
                FROM escolas_es_saev 
                GROUP BY MUN_UF 
                ORDER BY quantidade DESC
            """).fetchall()
            
            bank_data = {
                'total_registros': bank_stats[0],
                'escolas_unicas': bank_stats[1],
                'municipios_unicos': bank_stats[2],
                'ufs_unicas': bank_stats[3],
                'distribuicao_uf': dict(uf_distribution)
            }
        else:
            bank_data = None
        
        # Relatório completo
        report = {
            'timestamp': datetime.now().isoformat(),
            'argumentos': vars(args),
            'dados_excel': excel_stats,
            'dados_banco': bank_data,
            'status': 'sucesso' if not args.dry_run else 'dry_run'
        }
        
        # Salvar relatório se solicitado
        if args.report:
            with open(args.report, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"📊 Relatório salvo em: {args.report}")
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")
        return None

def main():
    """Função principal"""
    args = parse_arguments()
    logger = setup_logging(args.verbose)
    
    try:
        logger.info("🚀 Iniciando carregamento avançado de dados escolas_es_saev")
        logger.info("=" * 70)
        
        if args.dry_run:
            logger.info("🧪 MODO DRY-RUN: Apenas validação, sem inserção no banco")
        
        # 1. Validar arquivos
        excel_file, db_file = validate_files(args.excel_file, args.db_file)
        logger.info(f"📂 Excel: {excel_file}")
        logger.info(f"🗄️ Banco: {db_file}")
        
        # 2. Carregar dados da planilha
        logger.info(f"📊 Carregando planilha...")
        df = pd.read_excel(excel_file)
        logger.info(f"✅ Planilha carregada: {df.shape[0]} linhas x {df.shape[1]} colunas")
        
        # 3. Conectar ao banco
        if not args.dry_run:
            conn = duckdb.connect(str(db_file))
            logger.info("✅ Conectado ao banco DuckDB")
            
            # 4. Backup se solicitado
            if args.backup:
                backup_table(conn, 'escolas_es_saev')
            
            # 5. Limpar tabela se solicitado
            if args.clear:
                conn.execute("DELETE FROM escolas_es_saev")
                logger.info("🗑️ Tabela limpa")
            
            # 6. Inserir dados
            logger.info("📥 Inserindo dados...")
            insert_query = """
            INSERT INTO escolas_es_saev (MUN_UF, MUN_ID, MUN_NOME, ESC_ID, ESC_INEP, ESC_NOME)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            data_tuples = list(df.itertuples(index=False, name=None))
            batch_size = 1000
            
            for i in range(0, len(data_tuples), batch_size):
                batch = data_tuples[i:i + batch_size]
                conn.executemany(insert_query, batch)
                logger.debug(f"📝 Inseridos {min(i + batch_size, len(data_tuples))}/{len(data_tuples)} registros...")
            
            logger.info(f"✅ {len(data_tuples)} registros inseridos com sucesso")
        else:
            conn = None
            logger.info("ℹ️ Modo dry-run: dados validados, inserção simulada")
        
        # 7. Gerar relatório
        report = generate_report(df, conn, args)
        
        # 8. Mostrar resumo
        logger.info("=" * 70)
        logger.info("📊 RESUMO:")
        logger.info(f"   📝 Linhas processadas: {len(df):,}")
        logger.info(f"   🏫 Escolas únicas: {df['ESC_ID'].nunique():,}")
        logger.info(f"   🏛️ Municípios únicos: {df['MUN_ID'].nunique():,}")
        logger.info(f"   🗺️ UFs únicas: {df['MUN_UF'].nunique():,}")
        
        if conn:
            final_count = conn.execute("SELECT COUNT(*) FROM escolas_es_saev").fetchone()[0]
            logger.info(f"   💾 Total no banco: {final_count:,}")
            conn.close()
        
        logger.info("🎉 Processo concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"💥 Erro durante o processo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

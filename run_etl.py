#!/usr/bin/env python3
"""
Script principal para executar o ETL do Sistema SAEV
===================================================

Uso:
    python run_etl.py full         # Carga completa
    python run_etl.py incremental  # Carga incremental
    
Exemplos:
    python run_etl.py full --db-path db/teste.duckdb
    python run_etl.py incremental --data-path data/raw
"""

import sys
import os
from saev_etl import main

if __name__ == "__main__":
    # Adiciona argumentos padrão se não fornecidos
    if len(sys.argv) == 1:
        print("Uso: python run_etl.py [full|incremental] [opções]")
        print("\nExemplos:")
        print("  python run_etl.py full")
        print("  python run_etl.py incremental")
        print("  python run_etl.py full --db-path db/teste.duckdb")
        sys.exit(1)
    
    # Se apenas o modo foi fornecido, adiciona --mode
    if len(sys.argv) == 2 and sys.argv[1] in ['full', 'incremental']:
        sys.argv.insert(1, '--mode')
    
    main()

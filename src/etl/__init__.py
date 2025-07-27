"""
Módulo ETL do Sistema SAEV
=========================

Este módulo contém as funcionalidades de ETL (Extract, Transform, Load)
para processamento dos dados de avaliação educacional do SAEV.

Classes principais:
- SAEVETLProcessor: Processador principal de ETL
"""

from .saev_etl import SAEVETLProcessor

__version__ = "1.0.0"
__author__ = "Sistema SAEV"

__all__ = ["SAEVETLProcessor"]

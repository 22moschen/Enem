"""
ENEMAnalytics - Plataforma de análise de dados educacionais do ENEM.

Módulo principal para processamento e análise de microdados do ENEM
com foco em Altamira-PA.
"""

__version__ = "2.0.0"
__author__ = "ENEMAnalytics Team"
__description__ = "Plataforma profissional para análise educacional"

from .core.logger import get_logger

__all__ = ["get_logger"]

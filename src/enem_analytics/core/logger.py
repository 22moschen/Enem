"""
Sistema centralizado de logging para ENEMAnalytics.

Fornece logger configurado com múltiplos handlers (arquivo e console)
com níveis de log apropriados por ambiente.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def get_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Obter logger configurado para o módulo.

    Args:
        name: Nome do logger (geralmente __name__)
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho para arquivo de log

    Returns:
        Logger configurado
    """
    from config.settings import LOG_LEVEL, LOG_FILE, LOG_FORMAT

    logger = logging.getLogger(name)
    
    # Evitar duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(level or LOG_LEVEL)

    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level or LOG_LEVEL)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Handler para arquivo
    if log_file or LOG_FILE:
        file_path = log_file or LOG_FILE
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(level or LOG_LEVEL)
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

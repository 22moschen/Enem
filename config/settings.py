"""
Configurações centralizadas do projeto ENEMAnalytics.

Define todas as configurações de ambiente, caminhos, database e logging
de forma centralizada e escalável.
"""

import os
from pathlib import Path
from enum import Enum
from typing import Optional
from dataclasses import dataclass


class Environment(str, Enum):
    """Ambientes de execução suportados."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


# Diretórios base
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"

# Criar diretórios se não existirem
for directory in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Configurações de ambiente
ENVIRONMENT = Environment(os.getenv("ENV", "development"))
DEBUG = ENVIRONMENT == Environment.DEVELOPMENT

# Configurações de banco de dados
DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "enem_analysis.db"))
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Configurações de dados
DATA_SOURCES_PATH = os.getenv("DATA_SOURCES_PATH", str(BASE_DIR / "DataSources"))
DW_STORAGE_PATH = os.getenv("DW_STORAGE_PATH", str(BASE_DIR / "DWStorage"))
PROCESSED_DATA_PATH = os.getenv("PROCESSED_DATA_PATH", str(DATA_DIR / "processed"))

# Configurações de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if not DEBUG else "DEBUG")
LOG_FILE = LOGS_DIR / "enem_analytics.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configurações de Streamlit
STREAMLIT_CONFIG = {
    "theme": {
        "primaryColor": "#2E86AB",
        "backgroundColor": "#F5F7F9",
        "secondaryBackgroundColor": "#FFFFFF",
        "textColor": "#262730",
        "font": "sans serif"
    },
    "client": {
        "showErrorDetails": DEBUG,
    }
}

# Configurações de processamento de dados
BATCH_SIZE = 10000
CHUNK_SIZE = 5000
N_JOBS = -1  # Usar todos os cores disponíveis

# Configurações de validação
VALIDATION_THRESHOLD = 0.95  # 95% de qualidade mínima
MAX_MISSING_PERCENT = 0.30  # 30% máximo de valores faltantes

# Configurações de filtros padrão (Altamira-PA)
DEFAULT_MUNICIPALITY_CODE = 150070
DEFAULT_MUNICIPALITY_NAME = "Altamira"
DEFAULT_STATE = "PA"

@dataclass
class DatabaseConfig:
    """Configuração de banco de dados."""
    path: str = DATABASE_PATH
    url: str = DATABASE_URL
    timeout: int = 30
    check_same_thread: bool = False

@dataclass
class ETLConfig:
    """Configuração de pipeline ETL."""
    batch_size: int = BATCH_SIZE
    chunk_size: int = CHUNK_SIZE
    n_jobs: int = N_JOBS
    validate_on_load: bool = True
    drop_duplicates: bool = True

# Instâncias padrão
db_config = DatabaseConfig()
etl_config = ETLConfig()

# Validar configurações
if not os.path.exists(DATABASE_PATH) and ENVIRONMENT != Environment.TESTING:
    os.makedirs(os.path.dirname(DATABASE_PATH) or ".", exist_ok=True)

if not os.path.exists(DATA_SOURCES_PATH):
    raise FileNotFoundError(f"DataSources path not found: {DATA_SOURCES_PATH}")

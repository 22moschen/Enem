"""
Implementação de carregamento de dados (Load - ETL).

Implementa IDataLoader seguindo princípios SOLID.
"""

import sqlite3
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from src.enem_analytics.core.logger import get_logger
from src.enem_analytics.etl.interfaces import IDataLoader
from config.settings import DATABASE_PATH

logger = get_logger(__name__)


class SQLiteDataLoader(IDataLoader):
    """Carregador de dados para SQLite."""

    def __init__(self, database_path: str = DATABASE_PATH):
        """
        Inicializa carregador SQLite.

        Args:
            database_path: Caminho do banco de dados
        """
        self.database_path = database_path
        self._ensure_database_exists()

    def validate_destination(self, destination: str) -> bool:
        """Valida acesso ao banco de dados."""
        try:
            conn = sqlite3.connect(destination, timeout=5)
            conn.execute("SELECT 1")
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao validar destino {destination}: {e}")
            return False

    def _ensure_database_exists(self) -> None:
        """Garante que banco de dados existe."""
        try:
            import os
            os.makedirs(os.path.dirname(self.database_path), exist_ok=True)

            conn = sqlite3.connect(self.database_path)
            conn.close()
            logger.info(f"Banco de dados pronto: {self.database_path}")
        except Exception as e:
            logger.error(f"Erro ao criar banco: {e}", exc_info=True)
            raise

    def load(self, data: Dict[str, Any], destination: str = None, **kwargs) -> bool:
        """
        Carrega dados no banco SQLite.

        Args:
            data: Dicionário com dados transformados
            destination: Caminho do banco (padrão: DATABASE_PATH)
            **kwargs: Argumentos adicionais

        Returns:
            True se sucesso
        """
        destination = destination or self.database_path

        if not self.validate_destination(destination):
            logger.error(f"Destino inválido: {destination}")
            return False

        logger.info(f"Iniciando carga em {destination}")

        try:
            conn = sqlite3.connect(destination)

            # Carregar dados principais
            if "students" in data and isinstance(data["students"], pd.DataFrame):
                df_students = data["students"]
                df_students.to_sql("students", conn, if_exists="append", index=False)
                logger.info(f"Carregados {len(df_students)} registros de estudantes")

            # Carregar agregações
            if "by_location" in data:
                df_location = pd.DataFrame(data["by_location"]).T
                df_location.to_sql("performance_by_location", conn, if_exists="replace")
                logger.debug("Agregação por localização carregada")

            if "by_school_type" in data:
                df_school = pd.DataFrame(data["by_school_type"]).T
                df_school.to_sql("performance_by_school_type", conn, if_exists="replace")
                logger.debug("Agregação por tipo de escola carregada")

            # Carregar correlações
            if "correlations" in data:
                df_corr = pd.DataFrame(data["correlations"])
                df_corr.to_sql("correlations", conn, if_exists="replace")
                logger.debug("Correlações carregadas")

            # Carregar estatísticas descritivas
            if "descriptive_stats" in data:
                stats = data["descriptive_stats"]
                df_stats = pd.DataFrame(stats).T
                df_stats.to_sql("descriptive_statistics", conn, if_exists="replace")
                logger.debug("Estatísticas descritivas carregadas")

            conn.commit()
            conn.close()

            logger.info("Carga concluída com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}", exc_info=True)
            return False

    def load_metadata(
        self,
        file_path: str,
        year: int,
        checksum: str,
        status: str = "completed",
        destination: str = None,
    ) -> bool:
        """
        Carrega metadados de processamento.

        Args:
            file_path: Caminho do arquivo processado
            year: Ano dos dados
            checksum: Checksum do arquivo
            status: Status do processamento
            destination: Banco de dados

        Returns:
            True se sucesso
        """
        destination = destination or self.database_path

        try:
            conn = sqlite3.connect(destination)
            cursor = conn.cursor()

            # Criar tabela se não existir
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS etl_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    year INTEGER,
                    checksum TEXT,
                    status TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    error_message TEXT
                )
                """
            )

            # Inserir registro
            cursor.execute(
                """
                INSERT INTO etl_metadata (file_path, year, checksum, status, processed_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (file_path, year, checksum, status, datetime.now()),
            )

            conn.commit()
            conn.close()

            logger.info(f"Metadados carregados para {file_path}")
            return True

        except Exception as e:
            logger.error(f"Erro ao carregar metadados: {e}", exc_info=True)
            return False

    def check_file_already_processed(
        self, file_path: str, checksum: str, destination: str = None
    ) -> bool:
        """
        Verifica se arquivo já foi processado.

        Args:
            file_path: Caminho do arquivo
            checksum: Checksum do arquivo
            destination: Banco de dados

        Returns:
            True se já foi processado
        """
        destination = destination or self.database_path

        try:
            conn = sqlite3.connect(destination)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT status FROM etl_metadata
                WHERE file_path = ? AND checksum = ?
                AND status = 'completed'
                LIMIT 1
                """,
                (file_path, checksum),
            )

            result = cursor.fetchone()
            conn.close()

            return result is not None

        except Exception as e:
            logger.debug(f"Erro ao verificar arquivo processado: {e}")
            return False


class DataLoaderFactory:
    """Factory para criar loaders apropriados."""

    _loaders = {
        "sqlite": SQLiteDataLoader,
        "sqlite3": SQLiteDataLoader,
    }

    @staticmethod
    def create_loader(loader_type: str = "sqlite", **kwargs) -> IDataLoader:
        """
        Cria loader apropriado.

        Args:
            loader_type: Tipo de loader
            **kwargs: Argumentos para inicialização

        Returns:
            Instância de IDataLoader
        """
        if loader_type not in DataLoaderFactory._loaders:
            logger.warning(f"Loader desconhecido {loader_type}, usando sqlite")
            loader_type = "sqlite"

        loader_class = DataLoaderFactory._loaders[loader_type]
        logger.info(f"Usando loader: {loader_class.__name__}")
        return loader_class(**kwargs)

    @staticmethod
    def register_loader(loader_type: str, loader_class: type) -> None:
        """Registra novo loader."""
        DataLoaderFactory._loaders[loader_type] = loader_class
        logger.info(f"Novo loader registrado: {loader_type}")

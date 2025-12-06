"""
Abstrações e interfaces para ETL (Princípios SOLID).

Define contratos para implementações de Extract, Transform, Load.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from enum import Enum


class DataSourceType(str, Enum):
    """Tipos de fonte de dados suportados."""
    CSV = "csv"
    EXCEL = "excel"
    DATABASE = "database"


class IDataExtractor(ABC):
    """Interface para extração de dados (Dependency Inversion Principle)."""

    @abstractmethod
    def extract(self, source: str, **kwargs) -> pd.DataFrame:
        """
        Extrai dados da fonte.

        Args:
            source: Caminho ou identificador da fonte
            **kwargs: Argumentos específicos da fonte

        Returns:
            DataFrame com dados brutos
        """
        pass

    @abstractmethod
    def validate_source(self, source: str) -> bool:
        """Valida se a fonte está acessível e é válida."""
        pass


class IDataTransformer(ABC):
    """Interface para transformação de dados."""

    @abstractmethod
    def transform(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Transforma dados brutos.

        Args:
            data: DataFrame com dados brutos

        Returns:
            Dicionário com dados transformados
        """
        pass

    @abstractmethod
    def validate(self, data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Valida dados de entrada.

        Returns:
            Tupla (é_válido, lista_de_erros)
        """
        pass


class IDataLoader(ABC):
    """Interface para carregamento de dados."""

    @abstractmethod
    def load(self, data: Dict[str, Any], destination: str, **kwargs) -> bool:
        """
        Carrega dados no destino.

        Args:
            data: Dicionário com dados transformados
            destination: Caminho ou identificador de destino
            **kwargs: Argumentos específicos do destino

        Returns:
            True se sucesso, False se falha
        """
        pass

    @abstractmethod
    def validate_destination(self, destination: str) -> bool:
        """Valida se o destino está acessível."""
        pass


class IPipelineOrchestrator(ABC):
    """Interface para orquestração do pipeline ETL."""

    @abstractmethod
    def execute(
        self,
        source: str,
        destination: str,
        **options
    ) -> Dict[str, Any]:
        """
        Executa pipeline ETL completo.

        Returns:
            Dicionário com resultados e métricas
        """
        pass


class IDataValidator(ABC):
    """Interface para validação de dados (Single Responsibility)."""

    @abstractmethod
    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Valida integridade dos dados.

        Returns:
            Dicionário com resultado da validação
        """
        pass


class IQualityMetrics(ABC):
    """Interface para cálculo de métricas de qualidade."""

    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calcula métricas de qualidade."""
        pass


class IDataCache(ABC):
    """Interface para cache de dados (Open/Closed Principle)."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Armazena valor em cache."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Verifica se chave existe no cache."""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Limpa todo o cache."""
        pass


class ILogger(ABC):
    """Interface para logging (Dependency Inversion)."""

    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Log de informação."""
        pass

    @abstractmethod
    def error(self, message: str, exc_info: bool = False) -> None:
        """Log de erro."""
        pass

    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Log de debug."""
        pass

    @abstractmethod
    def warning(self, message: str) -> None:
        """Log de aviso."""
        pass

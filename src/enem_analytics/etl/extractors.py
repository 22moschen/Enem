"""
Implementação de extração de dados (Extract - ETL).

Implementa IDataExtractor seguindo princípios SOLID.
"""

import pandas as pd
import os
from typing import Optional
from src.enem_analytics.core.logger import get_logger
from src.enem_analytics.etl.interfaces import IDataExtractor
from config.settings import DEFAULT_MUNICIPALITY_CODE, BATCH_SIZE

logger = get_logger(__name__)


class CSVDataExtractor(IDataExtractor):
    """Extrator de dados de arquivos CSV."""

    ALTAMIRA_MUNICIPALITY_CODE = DEFAULT_MUNICIPALITY_CODE

    def __init__(self, encoding: str = "latin-1", batch_size: int = BATCH_SIZE):
        """
        Inicializa extrator CSV.

        Args:
            encoding: Encoding do arquivo
            batch_size: Tamanho do chunk para leitura
        """
        self.encoding = encoding
        self.batch_size = batch_size

    def validate_source(self, source: str) -> bool:
        """Valida se arquivo CSV existe."""
        if not os.path.exists(source):
            logger.error(f"Arquivo não encontrado: {source}")
            return False

        if not source.lower().endswith((".csv", ".xlsx", ".xls")):
            logger.error(f"Arquivo não é CSV/Excel: {source}")
            return False

        return True

    def extract(self, source: str, **kwargs) -> pd.DataFrame:
        """
        Extrai dados do arquivo.

        Args:
            source: Caminho do arquivo
            **kwargs: Argumentos adicionais (usecols, nrows, etc)

        Returns:
            DataFrame com dados extraídos
        """
        if not self.validate_source(source):
            raise FileNotFoundError(f"Arquivo inválido: {source}")

        logger.info(f"Iniciando extração de {source}")

        try:
            # Detectar tipo de arquivo
            if source.lower().endswith((".xlsx", ".xls")):
                df = pd.read_excel(source, **kwargs)
                logger.info(f"Arquivo Excel lido: {source}")
            else:
                # Ler CSV
                df = pd.read_csv(
                    source,
                    encoding=self.encoding,
                    dtype=self._get_dtype_spec(),
                    **kwargs
                )
                logger.info(f"Arquivo CSV lido: {source} ({len(df)} registros)")

            # Validações básicas
            if df.empty:
                logger.warning(f"DataFrame vazio: {source}")
                return df

            logger.info(
                f"Extração concluída: {len(df)} registros, "
                f"{len(df.columns)} colunas"
            )
            return df

        except Exception as e:
            logger.error(f"Erro ao ler {source}: {str(e)}", exc_info=True)
            raise

    def filter_by_municipality(
        self, df: pd.DataFrame, municipality_code: int = None
    ) -> pd.DataFrame:
        """
        Filtra dados por município.

        Args:
            df: DataFrame original
            municipality_code: Código do município (padrão: Altamira)

        Returns:
            DataFrame filtrado
        """
        if municipality_code is None:
            municipality_code = self.ALTAMIRA_MUNICIPALITY_CODE

        # Coluna pode estar em diferentes nomes
        possible_cols = ["CO_MUNICIPIO_ESC", "CO_MUNICIPIO_PROVA", "CO_MUNICIPIO"]
        municipality_col = None

        for col in possible_cols:
            if col in df.columns:
                municipality_col = col
                break

        if municipality_col is None:
            logger.warning("Coluna de município não encontrada")
            return df

        original_count = len(df)
        df_filtered = df[df[municipality_col] == municipality_code].copy()

        logger.info(
            f"Filtrados {len(df_filtered)} / {original_count} registros "
            f"para município {municipality_code}"
        )

        return df_filtered

    @staticmethod
    def _get_dtype_spec() -> dict:
        """Especificação de tipos para otimização."""
        return {
            "NU_INSCRICAO": "Int64",
            "TP_PRESENCA_CN": "Int32",
            "TP_PRESENCA_CH": "Int32",
            "TP_PRESENCA_LC": "Int32",
            "TP_PRESENCA_MT": "Int32",
            "NU_NOTA_CN": "float32",
            "NU_NOTA_CH": "float32",
            "NU_NOTA_LC": "float32",
            "NU_NOTA_MT": "float32",
            "NU_NOTA_REDACAO": "float32",
            "TP_LOCALIZACAO_ESC": "Int32",
            "TP_DEPENDENCIA_ADM_ESC": "Int32",
            "CO_MUNICIPIO_ESC": "Int32",
            "NU_ANO": "Int32",
        }


class ExcelDataExtractor(CSVDataExtractor):
    """Extrator especializado para arquivos Excel."""

    def validate_source(self, source: str) -> bool:
        """Valida se arquivo é Excel válido."""
        if not super().validate_source(source):
            return False

        if not source.lower().endswith((".xlsx", ".xls")):
            logger.error(f"Arquivo não é Excel: {source}")
            return False

        return True

    def extract(self, source: str, sheet_name: int = 0, **kwargs) -> pd.DataFrame:
        """
        Extrai dados de arquivo Excel.

        Args:
            source: Caminho do arquivo
            sheet_name: Nome ou índice da sheet
            **kwargs: Argumentos adicionais
        """
        if not self.validate_source(source):
            raise FileNotFoundError(f"Arquivo Excel inválido: {source}")

        logger.info(f"Extraindo Excel: {source} (sheet={sheet_name})")

        try:
            df = pd.read_excel(
                source,
                sheet_name=sheet_name,
                dtype=self._get_dtype_spec(),
                **kwargs
            )
            logger.info(f"Excel extraído: {len(df)} registros")
            return df
        except Exception as e:
            logger.error(f"Erro ao ler Excel {source}: {str(e)}", exc_info=True)
            raise


class ExtractorFactory:
    """Factory para criar extractors apropriados (Factory Pattern)."""

    _extractors = {
        ".csv": CSVDataExtractor,
        ".xlsx": ExcelDataExtractor,
        ".xls": ExcelDataExtractor,
    }

    @staticmethod
    def create_extractor(file_path: str) -> IDataExtractor:
        """
        Cria extrator apropriado baseado na extensão.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Instância de IDataExtractor apropriada
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext not in ExtractorFactory._extractors:
            logger.warning(f"Tipo desconhecido {ext}, usando CSV")
            return CSVDataExtractor()

        extractor_class = ExtractorFactory._extractors[ext]
        logger.info(f"Usando extrator: {extractor_class.__name__}")
        return extractor_class()

    @staticmethod
    def register_extractor(extension: str, extractor_class: type) -> None:
        """Permite registrar novos extractors."""
        ExtractorFactory._extractors[extension] = extractor_class
        logger.info(f"Novo extrator registrado: {extension} -> {extractor_class.__name__}")

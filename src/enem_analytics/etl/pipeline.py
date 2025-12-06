"""
Orquestrador do pipeline ETL (Pipeline Orchestrator).

Coordena Extract, Transform, Load de forma desacoplada.
"""

import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd

from src.enem_analytics.core.logger import get_logger
from src.enem_analytics.etl.interfaces import (
    IPipelineOrchestrator,
    IDataExtractor,
    IDataTransformer,
    IDataLoader,
)
from src.enem_analytics.etl.extractors import ExtractorFactory
from src.enem_analytics.etl.transformers import DataTransformer
from src.enem_analytics.etl.loaders import DataLoaderFactory

logger = get_logger(__name__)


class ETLPipeline(IPipelineOrchestrator):
    """Orquestrador de pipeline ETL."""

    def __init__(
        self,
        extractor: Optional[IDataExtractor] = None,
        transformer: Optional[IDataTransformer] = None,
        loader: Optional[IDataLoader] = None,
    ):
        """
        Inicializa pipeline ETL.

        Args:
            extractor: Implementação de IDataExtractor
            transformer: Implementação de IDataTransformer
            loader: Implementação de IDataLoader
        """
        self.extractor = extractor
        self.transformer = transformer or DataTransformer()
        self.loader = loader or DataLoaderFactory.create_loader()

    def execute(
        self,
        source: str,
        destination: str,
        **options
    ) -> Dict[str, Any]:
        """
        Executa pipeline ETL completo.

        Args:
            source: Fonte de dados
            destination: Destino de dados
            **options: Opções adicionais (filter_municipality, year, etc)

        Returns:
            Dicionário com resultados e métricas
        """
        logger.info(f"Iniciando pipeline ETL")
        logger.info(f"  Fonte: {source}")
        logger.info(f"  Destino: {destination}")

        start_time = datetime.now()
        result = {
            "source": source,
            "destination": destination,
            "status": "failed",
            "stages": {},
            "metrics": {},
        }

        try:
            # Stage 1: Extract
            logger.info("=" * 50)
            logger.info("STAGE 1: EXTRACT")
            logger.info("=" * 50)

            extract_result = self._execute_extract(source, options)
            result["stages"]["extract"] = extract_result

            if extract_result["status"] == "failed":
                raise Exception(extract_result.get("error", "Erro na extração"))

            # Stage 2: Transform
            logger.info("=" * 50)
            logger.info("STAGE 2: TRANSFORM")
            logger.info("=" * 50)

            transform_result = self._execute_transform(
                extract_result["data"],
                options
            )
            result["stages"]["transform"] = transform_result

            if transform_result["status"] == "failed":
                raise Exception(transform_result.get("error", "Erro na transformação"))

            # Stage 3: Load
            logger.info("=" * 50)
            logger.info("STAGE 3: LOAD")
            logger.info("=" * 50)

            load_result = self._execute_load(
                transform_result["data"],
                destination,
                source,
                options
            )
            result["stages"]["load"] = load_result

            if load_result["status"] == "failed":
                raise Exception(load_result.get("error", "Erro no carregamento"))

            # Sucesso
            result["status"] = "success"
            result["metrics"] = self._calculate_metrics(start_time, extract_result)

            logger.info("=" * 50)
            logger.info("PIPELINE CONCLUÍDO COM SUCESSO")
            logger.info("=" * 50)

        except Exception as e:
            logger.error(f"Erro no pipeline: {e}", exc_info=True)
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    def _execute_extract(self, source: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Executa stage de extração."""
        try:
            # Criar extractor se não fornecido
            if self.extractor is None:
                self.extractor = ExtractorFactory.create_extractor(source)

            # Extrair dados
            df = self.extractor.extract(source)

            # Aplicar filtros
            if options.get("filter_municipality"):
                municipality = options.get("municipality_code")
                df = self.extractor.filter_by_municipality(df, municipality)

            logger.info(f"Extração bem-sucedida: {len(df)} registros")

            # Calcular checksum
            checksum = self._calculate_checksum(source)

            return {
                "status": "success",
                "data": df,
                "records": len(df),
                "columns": len(df.columns),
                "checksum": checksum,
            }

        except Exception as e:
            logger.error(f"Erro na extração: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
            }

    def _execute_transform(
        self, data: pd.DataFrame, options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executa stage de transformação."""
        try:
            # Transformar dados
            transformed_data = self.transformer.transform(data)

            logger.info(f"Transformação bem-sucedida")

            return {
                "status": "success",
                "data": transformed_data,
                "records_processed": len(data),
            }

        except Exception as e:
            logger.error(f"Erro na transformação: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
            }

    def _execute_load(
        self,
        data: Dict[str, Any],
        destination: str,
        source: str,
        options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Executa stage de carregamento."""
        try:
            # Carregar dados
            success = self.loader.load(data, destination)

            if not success:
                raise Exception("Carregamento retornou falso")

            # Carregar metadados
            checksum = options.get("checksum", "")
            year = options.get("year", 0)

            self.loader.load_metadata(
                source,
                year,
                checksum,
                "completed",
                destination
            )

            logger.info(f"Carregamento bem-sucedido em {destination}")

            return {
                "status": "success",
                "destination": destination,
            }

        except Exception as e:
            logger.error(f"Erro no carregamento: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
            }

    @staticmethod
    def _calculate_checksum(file_path: str) -> str:
        """Calcula checksum MD5 do arquivo."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"Erro ao calcular checksum: {e}")
            return ""

    @staticmethod
    def _calculate_metrics(start_time: datetime, extract_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas de execução."""
        elapsed = (datetime.now() - start_time).total_seconds()
        records = extract_result.get("records", 0)

        return {
            "elapsed_seconds": round(elapsed, 2),
            "records_per_second": round(records / elapsed, 0) if elapsed > 0 else 0,
            "total_records": records,
        }


class PipelineBuilder:
    """Builder para configurar pipeline ETL (Builder Pattern)."""

    def __init__(self):
        """Inicializa builder."""
        self._extractor: Optional[IDataExtractor] = None
        self._transformer: Optional[IDataTransformer] = None
        self._loader: Optional[IDataLoader] = None

    def with_extractor(self, extractor: IDataExtractor) -> "PipelineBuilder":
        """Define extractor."""
        self._extractor = extractor
        return self

    def with_transformer(self, transformer: IDataTransformer) -> "PipelineBuilder":
        """Define transformer."""
        self._transformer = transformer
        return self

    def with_loader(self, loader: IDataLoader) -> "PipelineBuilder":
        """Define loader."""
        self._loader = loader
        return self

    def build(self) -> ETLPipeline:
        """Constrói pipeline."""
        return ETLPipeline(
            extractor=self._extractor,
            transformer=self._transformer,
            loader=self._loader,
        )

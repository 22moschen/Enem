"""
Implementação de transformação de dados (Transform - ETL).

Implementa IDataTransformer seguindo princípios SOLID.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from src.enem_analytics.core.logger import get_logger
from src.enem_analytics.etl.interfaces import IDataTransformer, IDataValidator
from config.settings import VALIDATION_THRESHOLD, MAX_MISSING_PERCENT

logger = get_logger(__name__)


class DataValidator(IDataValidator):
    """Validador de integridade de dados (Single Responsibility)."""

    def __init__(self, required_columns: List[str] = None):
        """
        Inicializa validador.

        Args:
            required_columns: Colunas obrigatórias
        """
        self.required_columns = required_columns or [
            "NU_INSCRICAO",
            "NU_ANO",
            "TP_LOCALIZACAO_ESC",
            "TP_DEPENDENCIA_ADM_ESC",
        ]

    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Valida integridade dos dados.

        Returns:
            Dicionário com resultado da validação
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "stats": {},
        }

        # Verificar se DataFrame está vazio
        if data.empty:
            result["is_valid"] = False
            result["errors"].append("DataFrame vazio")
            return result

        # Verificar colunas obrigatórias
        missing_cols = set(self.required_columns) - set(data.columns)
        if missing_cols:
            result["is_valid"] = False
            result["errors"].append(f"Colunas faltando: {missing_cols}")

        # Verificar valores nulos excessivos
        null_rate = data.isnull().sum() / len(data)
        for col, rate in null_rate.items():
            if rate > MAX_MISSING_PERCENT:
                result["warnings"].append(
                    f"Coluna '{col}' com {rate*100:.1f}% nulos"
                )

        # Calcular estatísticas
        result["stats"] = {
            "total_rows": len(data),
            "total_cols": len(data.columns),
            "null_rate": float(null_rate.mean()),
            "memory_usage_mb": float(data.memory_usage(deep=True).sum() / 1024 / 1024),
        }

        if result["is_valid"]:
            logger.info(f"Dados validados: {len(data)} registros, {len(data.columns)} colunas")
        else:
            logger.error(f"Validação falhou: {result['errors']}")

        return result


class DataCleaner:
    """Limpeza de dados (Single Responsibility)."""

    @staticmethod
    def handle_missing_grades(
        df: pd.DataFrame, strategy: str = "median_by_group"
    ) -> pd.DataFrame:
        """
        Trata valores faltantes em notas.

        Args:
            df: DataFrame
            strategy: Estratégia de imputação

        Returns:
            DataFrame limpo
        """
        df_clean = df.copy()
        grade_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT"]

        logger.info(f"Tratando valores faltantes com estratégia: {strategy}")

        if strategy == "median_by_group":
            for col in grade_cols:
                if col not in df_clean.columns:
                    continue

                missing_mask = df_clean[col].isna()
                if missing_mask.sum() == 0:
                    continue

                # Imputar por mediana do grupo (urbano/rural)
                if "TP_LOCALIZACAO_ESC" in df_clean.columns:
                    group_medians = df_clean[~missing_mask].groupby(
                        "TP_LOCALIZACAO_ESC"
                    )[col].median()

                    for group_val, median_val in group_medians.items():
                        mask = (df_clean["TP_LOCALIZACAO_ESC"] == group_val) & missing_mask
                        df_clean.loc[mask, col] = median_val

                # Valores ainda faltando: usar mediana global
                still_missing = df_clean[col].isna()
                if still_missing.sum() > 0:
                    global_median = df_clean[~missing_mask][col].median()
                    df_clean.loc[still_missing, col] = global_median

                logger.debug(f"{col}: {missing_mask.sum()} valores imputados")

        return df_clean

    @staticmethod
    def treat_outliers(df: pd.DataFrame, method: str = "capping") -> pd.DataFrame:
        """
        Trata outliers em notas.

        Args:
            df: DataFrame
            method: Método de tratamento (capping, removal)

        Returns:
            DataFrame sem outliers
        """
        df_treated = df.copy()
        grade_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT"]

        logger.info(f"Tratando outliers com método: {method}")

        for col in grade_cols:
            if col not in df_treated.columns:
                continue

            Q1 = df_treated[col].quantile(0.25)
            Q3 = df_treated[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            if method == "capping":
                df_treated[col] = df_treated[col].clip(lower_bound, upper_bound)
            elif method == "removal":
                mask = (df_treated[col] >= lower_bound) & (df_treated[col] <= upper_bound)
                df_treated = df_treated[mask]

        logger.debug(f"Outliers tratados: {len(df_treated)} registros restantes")
        return df_treated


class DataTransformer(IDataTransformer):
    """Transformação de dados (Transform - ETL)."""

    def __init__(
        self,
        validator: IDataValidator = None,
        cleaner: Any = None,
    ):
        """
        Inicializa transformador.

        Args:
            validator: Instância de IDataValidator
            cleaner: Instância de DataCleaner
        """
        self.validator = validator or DataValidator()
        self.cleaner = cleaner or DataCleaner()

    def validate(self, data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Valida dados de entrada."""
        validation_result = self.validator.validate(data)
        errors = validation_result.get("errors", [])
        return validation_result["is_valid"], errors

    def transform(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Transforma dados brutos em dados processados.

        Args:
            data: DataFrame bruto

        Returns:
            Dicionário com dados transformados
        """
        logger.info("Iniciando transformação de dados")

        # Validar dados
        is_valid, errors = self.validate(data)
        if not is_valid:
            logger.error(f"Validação falhou: {errors}")
            raise ValueError(f"Dados inválidos: {errors}")

        # Limpar dados
        df_clean = self.cleaner.handle_missing_grades(data)
        df_clean = self.cleaner.treat_outliers(df_clean)

        # Agrupar e agregar
        result = self._aggregate_data(df_clean)

        logger.info(f"Transformação concluída: {len(result['students'])} estudantes processados")

        return result

    @staticmethod
    def _aggregate_data(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Agrega dados por diferentes dimensões.

        Returns:
            Dicionário com agregações
        """
        grade_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT"]

        result = {
            "students": df,
            "by_location": df.groupby("TP_LOCALIZACAO_ESC")[grade_cols].mean().to_dict(),
            "by_school_type": df.groupby("TP_DEPENDENCIA_ADM_ESC")[grade_cols].mean().to_dict(),
            "correlations": df[grade_cols].corr().to_dict(),
            "descriptive_stats": {
                col: {
                    "mean": df[col].mean(),
                    "median": df[col].median(),
                    "std": df[col].std(),
                    "min": df[col].min(),
                    "max": df[col].max(),
                }
                for col in grade_cols
            },
        }

        return result

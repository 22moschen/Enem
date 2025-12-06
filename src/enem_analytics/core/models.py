"""
Modelos e schemas de dados para ENEMAnalytics.

Utiliza Pydantic para validação e type safety.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class Environment(str, Enum):
    """Tipos de localização de escola."""
    URBAN = 1
    RURAL = 2


class SchoolType(str, Enum):
    """Tipos de dependência administrativa."""
    FEDERAL = 1
    STATE = 2
    MUNICIPAL = 3
    PRIVATE = 4


class PresenceType(int, Enum):
    """Tipo de presença na prova."""
    PRESENT = 0
    ABSENT = 1
    DISQUALIFIED = 2
    EXEMPT = 3


class GradeSchema(BaseModel):
    """Schema para nota individual."""
    natural_sciences: float = Field(alias="NU_NOTA_CN")
    humanities: float = Field(alias="NU_NOTA_CH")
    languages: float = Field(alias="NU_NOTA_LC")
    mathematics: float = Field(alias="NU_NOTA_MT")
    essay: float = Field(alias="NU_NOTA_REDACAO")

    @validator("*", pre=True)
    def convert_to_float(cls, v):
        """Converte para float, retornando None se inválido."""
        if v is None or (isinstance(v, float) and v != v):  # NaN check
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    class Config:
        allow_population_by_field_name = True


class PresenceSchema(BaseModel):
    """Schema para presença em provas."""
    natural_sciences: PresenceType = Field(alias="TP_PRESENCA_CN")
    humanities: PresenceType = Field(alias="TP_PRESENCA_CH")
    languages: PresenceType = Field(alias="TP_PRESENCA_LC")
    mathematics: PresenceType = Field(alias="TP_PRESENCA_MT")

    class Config:
        allow_population_by_field_name = True


class StudentRecordSchema(BaseModel):
    """Schema para registro de estudante do ENEM."""
    enrollment_number: int = Field(alias="NU_INSCRICAO")
    year: int = Field(alias="NU_ANO")
    grades: GradeSchema
    presence: PresenceSchema
    school_location: Environment = Field(alias="TP_LOCALIZACAO_ESC")
    school_type: SchoolType = Field(alias="TP_DEPENDENCIA_ADM_ESC")
    school_municipality: int = Field(alias="CO_MUNICIPIO_ESC")

    class Config:
        allow_population_by_field_name = True


class QualityMetricsSchema(BaseModel):
    """Schema para métricas de qualidade."""
    total_records: int
    records_with_all_grades: int
    records_with_any_grade: int
    missing_rate: float = Field(ge=0, le=1)
    average_grade: float
    median_grade: float
    std_deviation: float
    processed_at: datetime = Field(default_factory=datetime.now)

    @validator("*", pre=True)
    def round_floats(cls, v):
        """Arredonda floats para 2 casas decimais."""
        if isinstance(v, float):
            return round(v, 2)
        return v


class ETLStatusSchema(BaseModel):
    """Schema para status de processamento ETL."""
    file_path: str
    year: int
    checksum: str
    status: str = Field(regex="^(pending|processing|completed|failed)$")
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class AnalysisResultSchema(BaseModel):
    """Schema para resultados de análise."""
    metric_name: str
    value: Any
    grouped_by: Optional[str] = None
    count: int
    timestamp: datetime = Field(default_factory=datetime.now)

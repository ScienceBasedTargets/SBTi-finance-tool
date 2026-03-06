from enum import Enum
from typing import Optional, Dict, List

import pandas as pd
from pydantic import BaseModel, field_validator, model_validator, Field


class AggregationContribution(BaseModel):
    company_name: str
    company_id: str
    temperature_score: float
    contribution_relative: Optional[float] = None
    contribution: Optional[float] = None

    def __getitem__(self, item):
        return getattr(self, item)


class Aggregation(BaseModel):
    score: float
    proportion: float
    contributions: List[AggregationContribution]

    def __getitem__(self, item):
        return getattr(self, item)


class ScoreAggregation(BaseModel):
    all: Aggregation
    influence_percentage: float
    grouped: Dict[str, Aggregation]

    def __getitem__(self, item):
        return getattr(self, item)


class ScoreAggregationScopes(BaseModel):
    S1S2: Optional[ScoreAggregation] = None
    S3: Optional[ScoreAggregation] = None
    S1S2S3: Optional[ScoreAggregation] = None

    def __getitem__(self, item):
        return getattr(self, item)


class ScoreAggregations(BaseModel):
    short: Optional[ScoreAggregationScopes] = None
    mid: Optional[ScoreAggregationScopes] = None
    long: Optional[ScoreAggregationScopes] = None

    def __getitem__(self, item):
        return getattr(self, item)


class ScenarioInterface(BaseModel):
    number: int
    engagement_type: Optional[str] = None


class PortfolioCompany(BaseModel):
    company_name: str
    company_id: str
    company_isin: Optional[str] = None
    company_lei: Optional[str] = 'nan'
    investment_value: float
    engagement_target: Optional[bool] = False
    user_fields: Optional[dict] = None


class IDataProviderCompany(BaseModel):
    company_name: str
    company_id: str
    isic: Optional[str] = None
    ghg_s1s2: Optional[float] = None
    ghg_s3: Optional[float] = None

    country: Optional[str] = None
    region: Optional[str] = None
    sector: Optional[str] = None
    industry_level_1: Optional[str] = None
    industry_level_2: Optional[str] = None
    industry_level_3: Optional[str] = None
    industry_level_4: Optional[str] = None

    company_revenue: Optional[float] = None
    company_market_cap: Optional[float] = None
    company_enterprise_value: Optional[float] = None
    company_total_assets: Optional[float] = None
    company_cash_equivalents: Optional[float] = None

    sbti_validated: bool = Field(
        False,
        description='True if the SBTi target status is "Target set", false otherwise',
    )

    @model_validator(mode='before')
    @classmethod
    def coerce_nan_to_none(cls, data):
        if isinstance(data, dict):
            return {k: None if isinstance(v, float) and pd.isna(v) else v
                    for k, v in data.items()}
        return data


class SortableEnum(Enum):
    def __str__(self):
        return self.name

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            order = list(self.__class__)
            return order.index(self) >= order.index(other)
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            order = list(self.__class__)
            return order.index(self) > order.index(other)
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            order = list(self.__class__)
            return order.index(self) <= order.index(other)
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            order = list(self.__class__)
            return order.index(self) < order.index(other)
        return NotImplemented


class EScope(SortableEnum):
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S1S2 = "S1+S2"
    S1S2S3 = "S1+S2+S3"

    @classmethod
    def get_result_scopes(cls) -> List["EScope"]:
        """
        Get a list of scopes that should be calculated if the user leaves it open.

        :return: A list of EScope objects
        """
        return [cls.S1S2, cls.S3, cls.S1S2S3]


class ETimeFrames(SortableEnum):
    SHORT = "short"
    MID = "mid"
    LONG = "long"


class IDataProviderTarget(BaseModel):
    company_id: str
    target_type: str
    intensity_metric: Optional[str] = None
    scope: EScope
    coverage_s1: float
    coverage_s2: float
    coverage_s3: float
    reduction_ambition: float
    base_year: int
    base_year_ghg_s1: float
    base_year_ghg_s2: float
    base_year_ghg_s3: float
    start_year: Optional[int] = None
    end_year: int
    time_frame: Optional[ETimeFrames] = None
    achieved_reduction: Optional[float] = 0

    @field_validator("intensity_metric", "time_frame", mode="before")
    @classmethod
    def coerce_nan_str_to_none(cls, val):
        if isinstance(val, float) and pd.isna(val):
            return None
        return val

    @field_validator("start_year", mode="before")
    @classmethod
    def validate_e(cls, val):
        if val == "" or val == "nan" or pd.isnull(val):
            return None
        return val

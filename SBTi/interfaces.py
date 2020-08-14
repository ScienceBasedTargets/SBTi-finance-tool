from enum import Enum
from typing import Optional, Dict, List

from pydantic import BaseModel


class AggregationContribution(BaseModel):
    company_name: str
    company_id: str
    temperature_score: float
    contribution_relative: float
    contribution: float


class Aggregation(BaseModel):
    score: float
    contributions: List[AggregationContribution]


class ScoreAggregation(BaseModel):
    all: Aggregation
    influence_percentage: float
    grouped: Optional[Dict[str, Aggregation]]


class ScoreAggregationScopes(BaseModel):
    S1S2: Optional[ScoreAggregation]
    S3: Optional[ScoreAggregation]
    S1S2S3: Optional[ScoreAggregation]


class ScoreAggregations(BaseModel):
    short: Optional[ScoreAggregationScopes]
    mid: Optional[ScoreAggregation]
    long: Optional[ScoreAggregation]


class ScenarioInterface(BaseModel):
    number: int
    engagement_type: Optional[str]


class PortfolioCompany(BaseModel):
    company_name: str
    company_id: str
    investment_value: float
    engagement_target: Optional[str] = "False"


class IDataProviderCompany(BaseModel):
    company_name: str
    company_id: str
    ghg_s1s2: float
    ghg_s3: float

    country: Optional[str]
    region: Optional[str]
    sector: Optional[str]
    industry_level_1: Optional[str]
    industry_level_2: Optional[str]
    industry_level_3: Optional[str]
    industry_level_4: Optional[str]

    company_revenue: Optional[float]
    company_market_cap: Optional[float]
    company_enterprise_value: Optional[float]
    company_total_assets: Optional[float]
    company_cash_equivalents: Optional[float]


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


class ETimeFrames(SortableEnum):
    SHORT = "short"
    MID = "mid"
    LONG = "long"


class IDataProviderTarget(BaseModel):
    company_id: str
    target_type: str
    intensity_metric: Optional[str]
    scope: EScope
    coverage_s1: float
    coverage_s2: float
    coverage_s3: float
    reduction_ambition: float
    base_year: int
    base_year_ghg_s1: float
    base_year_ghg_s2: float
    base_year_ghg_s3: float
    start_year: Optional[int]
    end_year: int
    achieved_reduction: Optional[float] = 0

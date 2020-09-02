import unittest
from SBTi.interfaces import (
    EScope,
    ETimeFrames,
    IDataProviderCompany,
    IDataProviderTarget,
    PortfolioCompany,
)
from SBTi.target_validation import TargetProtocol
from SBTi.temperature_score import TemperatureScore
from SBTi.data.data_provider import DataProvider
from SBTi.portfolio_aggregation import PortfolioAggregationMethod

import SBTi
from typing import List


class TestDataProvider(DataProvider):
    def __init__(
        self, targets: List[IDataProviderTarget], companies: List[IDataProviderCompany]
    ):
        self.targets = targets
        self.companies = companies

    # def set_targets(self, targets: List[IDataProviderTarget]):
    #     self.targets = targets

    # def set_company_data(self, companies: List[IDataProviderCompany]):
    #     self.companies = companies

    def get_sbti_targets(self, companies: list) -> list:
        return []

    def get_targets(self, company_ids: List[str]) -> List[IDataProviderTarget]:
        return self.targets

    def get_company_data(self, company_ids: List[str]) -> List[IDataProviderCompany]:
        return self.companies


class CoreTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_basic(self):

        company_id = "A"

        # define company
        company = IDataProviderCompany(
            company_name=company_id,
            company_id="A",
            ghg_s1s2=100,
            ghg_s3=0,
            company_revenue=100,
            company_market_cap=100,
            company_enterprise_value=100,
            company_total_assets=100,
            company_cash_equivalents=100,
        )
        # define targets
        target = IDataProviderTarget(
            company_id=company_id,
            target_type="absolute",
            scope=EScope.S1S2,
            coverage_s1=0.95,
            coverage_s2=0.95,
            coverage_s3=0,
            reduction_ambition=0.8,
            base_year=2019,
            base_year_ghg_s1=100,
            base_year_ghg_s2=0,
            base_year_ghg_s3=0,
            end_year=2030,
        )

        # test provider
        data_provider = TestDataProvider(companies=[company], targets=[target])

        tv = TargetProtocol()

        validated = tv.validate(target)
        assert validated

        # process data
        data = tv.process([target], [company])

        temp_score = TemperatureScore(
            time_frames=[ETimeFrames.MID],
            scopes=[EScope.S1S2],
            aggregation_method=PortfolioAggregationMethod.WATS,
        )

        scores = temp_score.calculate(data)
        # print(scores.head(10))

        # portfolio data
        pf_company = PortfolioCompany(
            company_name=company_id,
            company_id=company_id,
            investment_value=100,
            company_isin=company_id,
        )
        portfolio_data = SBTi.utils.get_data([data_provider], [pf_company])
        # print(portfolio_data.head(10))

        agg_scores = temp_score.aggregate_scores(portfolio_data)
        print(agg_scores.head(10))

        assert True

    def test_chaos(self):
        pass

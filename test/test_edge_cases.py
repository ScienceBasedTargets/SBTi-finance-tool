import unittest
from unittest.case import SkipTest
from SBTi.interfaces import (
    EScope,
    ETimeFrames,
    IDataProviderCompany,
    IDataProviderTarget,
    PortfolioCompany,
)

from SBTi.temperature_score import (
    EngagementType,
    Scenario,
    TemperatureScore,
)
from SBTi.portfolio_aggregation import PortfolioAggregationMethod
import copy
import SBTi
from typing import List
from SBTi.data.data_provider import DataProvider
from typing import List
from SBTi.interfaces import IDataProviderCompany, IDataProviderTarget


class TestDataProvider(DataProvider):
    def __init__(
        self, targets: List[IDataProviderTarget], companies: List[IDataProviderCompany]
    ):
        self.targets = targets
        self.companies = companies

    def get_sbti_targets(self, companies: list) -> list:
        return []

    def get_targets(self, company_ids: List[str]) -> List[IDataProviderTarget]:
        return self.targets

    def get_company_data(self, company_ids: List[str]) -> List[IDataProviderCompany]:
        return self.companies


class EdgeCasesTest(unittest.TestCase):
    def setUp(self):
        company_id = "BaseCompany"
        self.BASE_COMP_SCORE = 0.43
        self.company_base = IDataProviderCompany(
            company_name=company_id,
            company_id=company_id,
            # ghg_s1s2=100,
            # ghg_s3=0,
            company_revenue=100,
            company_market_cap=100,
            company_enterprise_value=100,
            company_total_assets=100,
            company_cash_equivalents=100,
            isic="A12",
        )
        # define targets
        self.target_base = IDataProviderTarget(
            company_id=company_id,
            target_type="abs",
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

        # pf
        self.pf_base = PortfolioCompany(
            company_name=company_id,
            company_id=company_id,
            investment_value=100,
            company_isin=company_id,
        )

    def test_missing_s1s2s3_values(self):
        """
        This test is going all the way to the aggregated calculations
        """

        companies, targets, pf_companies = self.create_base_companies(["A", "B"])

        data_provider = TestDataProvider(companies=companies, targets=targets)

        # Calculate scores & Aggregated values
        temp_score = TemperatureScore(
            time_frames=[ETimeFrames.MID],
            scopes=[EScope.S1S2, EScope.S1S2S3],
            aggregation_method=PortfolioAggregationMethod.WATS,
        )

        portfolio_data = SBTi.utils.get_data([data_provider], pf_companies)
        scores = temp_score.calculate(portfolio_data)
        agg_scores = temp_score.aggregate_scores(scores)

        # verify that results exist
        self.assertEqual(agg_scores.mid.S1S2.all.score, self.BASE_COMP_SCORE)

    def create_base_companies(self, company_ids: List[str]):
        """
        This is a helper method to create base companies that can be used for the test cases
        """
        companies: List[IDataProviderCompany] = []
        targets: List[IDataProviderTarget] = []
        pf_companies: List[PortfolioCompany] = []
        for company_id in company_ids:
            # company
            company = copy.deepcopy(self.company_base)
            company.company_id = company_id
            companies.append(company)

            # pf company
            pf_company = PortfolioCompany(
                company_name=company_id,
                company_id=company_id,
                investment_value=100,
                company_isin=company_id,
            )

            target = copy.deepcopy(self.target_base)
            target.company_id = company_id

            pf_companies.append(pf_company)
            targets.append(target)

        return companies, targets, pf_companies


if __name__ == "__main__":
    test = EdgeCasesTest()
    test.setUp()
    test.test_missing_s2s3_values()

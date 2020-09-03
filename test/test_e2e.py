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
import copy

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
        company_id = "BaseCompany"
        self.company_base = IDataProviderCompany(
            company_name=company_id,
            company_id=company_id,
            ghg_s1s2=100,
            ghg_s3=0,
            company_revenue=100,
            company_market_cap=100,
            company_enterprise_value=100,
            company_total_assets=100,
            company_cash_equivalents=100,
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

        #pf
        self.pf_base = PortfolioCompany(
            company_name=company_id,
            company_id=company_id,
            investment_value=100,
            company_isin=company_id,
        )

    def test_basic(self):

        company = copy.deepcopy(self.company_base)
        target = copy.deepcopy(self.target_base)
        # test provider
        data_provider = TestDataProvider(companies=[company], targets=[target])

        temp_score = TemperatureScore(
            time_frames=[ETimeFrames.MID, ETimeFrames.SHORT, ETimeFrames.LONG],
            scopes=[EScope.S1S2],
            aggregation_method=PortfolioAggregationMethod.WATS,
        )

        # portfolio data
        pf_company = copy.deepcopy(self.pf_base)
        portfolio_data = SBTi.utils.get_data([data_provider], [pf_company])
        print(portfolio_data.head(10))

        scores = temp_score.calculate(portfolio_data)
        print(scores)

        assert True

    def test_chaos(self):
        # TODO: go thru lots of different parameters on company & target level and try to break it
        pass

    def test_basic_flow(self):
        # 2 Companies
        company_ids = ["A", "B"]
        companies: List[IDataProviderCompany] = []
        targets: List[IDataProviderTarget] = []
        pf_companies: List[PortfolioCompany] = []
        for company_id in company_ids:

            # company
            company = copy.deepcopy(self.company_base)
            company.company_id = company_id
            companies.append(company)

            # target
            target = copy.deepcopy(self.target_base)
            target.company_id = company_id
            targets.append(target)

            # pf company
            pf_company = PortfolioCompany(
                company_name=company_id,
                company_id=company_id,
                investment_value=100,
                company_isin=company_id,
            )
            pf_companies.append(pf_company)

        # test provider
        data_provider = TestDataProvider(companies=companies, targets=targets)

        # tv = TargetProtocol()

        # validated = tv.validate(target)
        # assert validated

        # # process data
        # data = tv.process([target], [company])

        temp_score = TemperatureScore(
            time_frames=[ETimeFrames.MID],
            scopes=[EScope.S1S2],
            aggregation_method=PortfolioAggregationMethod.WATS,
        )

        # portfolio data

        portfolio_data = SBTi.utils.get_data([data_provider], pf_companies)
        print(portfolio_data.head(10))

        scores = temp_score.calculate(portfolio_data)
        # print(scores.head(10))

        agg_scores = temp_score.aggregate_scores(scores)
        print(agg_scores)

        assert True

    # Test with 10000+ companies
    def test_regression(self):

        pass


if __name__ == "__main__":
    test = CoreTest()
    test.setUp()
    test.test_basic()

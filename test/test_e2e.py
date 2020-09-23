import unittest
from unittest.case import SkipTest
from SBTi.interfaces import (
    EScope,
    ETimeFrames,
    IDataProviderCompany,
    IDataProviderTarget,
    PortfolioCompany,
)
from SBTi.target_validation import TargetProtocol
from SBTi.temperature_score import EngagementType, Scenario, ScenarioType, TemperatureScore
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

    def get_sbti_targets(self, companies: list) -> list:
        return []

    def get_targets(self, company_ids: List[str]) -> List[IDataProviderTarget]:
        return self.targets

    def get_company_data(self, company_ids: List[str]) -> List[IDataProviderCompany]:
        return self.companies


class EndToEndTest(unittest.TestCase):
    """
    This class is containing a set of end to end tests:
    - basic flow from creating companies/targets up to calculating aggregated values
    - edge cases for scenarios and grouping
    - high load tests (>1000 targets)
    - testing of all different input values and running thru the whole process (tbd)
    """

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
            isic='A12'
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

    def test_basic(self):
        """
        This test is just a very basic workflow going thru all calculations up to temp score
        """

        # Setup test provider
        company = copy.deepcopy(self.company_base)
        target = copy.deepcopy(self.target_base)
        data_provider = TestDataProvider(companies=[company], targets=[target])

        # Calculat4e Temp Scores
        temp_score = TemperatureScore(
            time_frames=[ETimeFrames.MID, ETimeFrames.SHORT, ETimeFrames.LONG],
            scopes=[EScope.S1S2],
            aggregation_method=PortfolioAggregationMethod.WATS,
        )

        # portfolio data
        pf_company = copy.deepcopy(self.pf_base)
        portfolio_data = SBTi.utils.get_data([data_provider], [pf_company])

        # Verify data
        scores = temp_score.calculate(portfolio_data)
        self.assertIsNotNone(scores)
        self.assertEqual(len(scores.index), 3)

    def test_chaos(self):
        # TODO: go thru lots of different parameters on company & target level and try to break it
        pass

    def test_target_grouping(self):
        """
        This test is checking the target grouping in the target validation from begin to end.
        """

        companies, targets, pf_companies = self.create_base_companies(["A", "B", "C", "D"])
        target = copy.deepcopy(self.target_base)
        target.company_id = 'A'
        target.coverage_s1 = 0.75
        target.coverage_s2 = 0.75
        target.coverage_s3 = 0.75
        targets.append(target)

        target = copy.deepcopy(self.target_base)
        target.company_id = 'A'
        target.coverage_s1 = 0.99
        target.coverage_s2 = 0.99
        target.coverage_s3 = 0.99
        targets.append(target)

        target = copy.deepcopy(self.target_base)
        target.company_id = 'B'
        target.scope = EScope.S3
        target.coverage_s1 = 0.75
        target.coverage_s2 = 0.75
        target.coverage_s3 = 0.49
        targets.append(target)

        target = copy.deepcopy(self.target_base)
        target.company_id = 'B'
        target.scope = EScope.S3
        target.coverage_s1 = 0.99
        target.coverage_s2 = 0.99
        target.coverage_s3 = 0.49
        targets.append(target)

        target = copy.deepcopy(self.target_base)
        target.company_id = 'D'
        target.coverage_s1 = 0.95
        target.coverage_s2 = 0.95
        target.target_type = 'int'
        target.intensity_metric = 'Revenue'
        targets.append(target)

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
        self.assertAlmostEqual(agg_scores.mid.S1S2.all.score, 0.4300, places=4)

    def test_basic_flow(self):
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
        self.assertEqual(agg_scores.mid.S1S2.all.score, 0.43)

    # Run some regression tests
    # @unittest.skip("only run for longer test runs")
    def test_regression_companies(self):

        nr_companies = 1000

        # test 10000 companies
        companies: List[IDataProviderCompany] = []
        targets: List[IDataProviderTarget] = []
        pf_companies: List[PortfolioCompany] = []

        for i in range(nr_companies):
            company_id = f"Company {str(i)}"
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

        data_provider = TestDataProvider(companies=companies, targets=targets)

        # Calculate scores & Aggregated values
        temp_score = TemperatureScore(
            time_frames=[ETimeFrames.MID],
            scopes=[EScope.S1S2],
            aggregation_method=PortfolioAggregationMethod.WATS,
        )

        portfolio_data = SBTi.utils.get_data([data_provider], pf_companies)
        scores = temp_score.calculate(portfolio_data)
        agg_scores = temp_score.aggregate_scores(scores)

        self.assertAlmostEqual(agg_scores.mid.S1S2.all.score, 0.43)

    def test_grouping(self):
        """
        Testing the grouping feature with two different industry levels and making sure the results are present
        """
        # make 2+ companies and group them together
        industry_levels = ["Manufacturer", "Energy"]
        company_ids = ["A", "B"]
        companies_all: List[IDataProviderCompany] = []
        targets_all: List[IDataProviderTarget] = []
        pf_companies_all: List[PortfolioCompany] = []

        for ind_level in industry_levels:

            company_ids_with_level = [f"{ind_level}_{company_id}" for company_id in company_ids]

            companies, targets, pf_companies = self.create_base_companies(company_ids_with_level)
            for company in companies:
                company.industry_level_1 = ind_level

            companies_all.extend(companies)
            targets_all.extend(targets)
            pf_companies_all.extend(pf_companies)

        data_provider = TestDataProvider(companies=companies_all, targets=targets_all)

        temp_score = TemperatureScore(
            time_frames=[ETimeFrames.MID],
            scopes=[EScope.S1S2],
            aggregation_method=PortfolioAggregationMethod.WATS,
            grouping=["industry_level_1"]
        )

        portfolio_data = SBTi.utils.get_data([data_provider], pf_companies_all)
        scores = temp_score.calculate(portfolio_data)
        agg_scores = temp_score.aggregate_scores(scores)

        for ind_level in industry_levels:
            self.assertAlmostEqual(agg_scores.mid.S1S2.grouped[ind_level].score, 0.43)

    def test_score_cap(self):

        companies, targets, pf_companies = self.create_base_companies(["A"])
        data_provider = TestDataProvider(companies=companies, targets=targets)

        # add a Scenario that will trigger the score cap function
        scenario = Scenario()
        scenario.engagement_type = EngagementType.SET_TARGETS
        scenario.scenario_type = ScenarioType.APPROVED_TARGETS

        temp_score = TemperatureScore(
            time_frames=[ETimeFrames.MID],
            scopes=[EScope.S1S2],
            aggregation_method=PortfolioAggregationMethod.WATS,
            scenario=scenario
        )

        portfolio_data = SBTi.utils.get_data([data_provider], pf_companies)
        scores = temp_score.calculate(portfolio_data)
        agg_scores = temp_score.aggregate_scores(scores)

        # add verification

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
    test = EndToEndTest()
    test.setUp()
    test.test_basic()
    test.test_basic_flow()
    test.test_regression_companies()
    test.test_score_cap()
    test.test_target_grouping()

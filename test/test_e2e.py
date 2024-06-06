import copy
import datetime
import unittest
from typing import List

import SBTi
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
    ScenarioType,
    TemperatureScore,
)
from SBTi.portfolio_aggregation import PortfolioAggregationMethod
from SBTi.data.data_provider import DataProvider


class TestDataProvider(DataProvider):
    def __init__(
        self, targets: List[IDataProviderTarget], companies: List[IDataProviderCompany]
    ):
        super().__init__()
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
    This class is containing a set of end-to-end tests:
    - basic flow from creating companies/targets up to calculating aggregated values
    - edge cases for scenarios and grouping
    - high load tests (>1000 targets)
    - testing of all different input values and running through the whole process (tbd)
    """

    def setUp(self):
        company_id = "BaseCompany"
        self.BASE_COMP_SCORE = 0.43

        # target end years which align to (short, mid, long) time frames
        self.short_end_year = datetime.datetime.now().year + 2
        self.mid_end_year = datetime.datetime.now().year + 5
        self.long_end_year = datetime.datetime.now().year + 25

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
            isic="A12",
        )
        # define targets
        self.target_base = self._create_target_with_defaults(company_id)

        # pf
        self.pf_base = PortfolioCompany(
            company_name=company_id,
            company_id=company_id,
            investment_value=100,
            company_isin=company_id,
        )

    def _create_target_with_defaults(self, company_id: str, **kwargs) -> IDataProviderTarget:
        """
        calls IDataProviderTarget constructor with defaults
        can override specific params with kwargs
        """
        defaults = dict(
            company_id=company_id,
            target_type="abs",
            scope=EScope.S1S2,
            coverage_s1=0.45,
            coverage_s2=0.45,
            coverage_s3=0,
            reduction_ambition=0.8,
            base_year=2019,
            base_year_ghg_s1=100,
            base_year_ghg_s2=100,
            base_year_ghg_s3=0,
            end_year=self.mid_end_year,
            target_ids="target_base"
        )
        defaults.update(kwargs)
        return IDataProviderTarget(**defaults)

    def test_basic(self):
        """
        This test is just a very basic workflow going through all calculations up to temp score
        """

        # Setup test provider
        company = copy.deepcopy(self.company_base)
        target = self._create_target_with_defaults(company_id=company.company_id)
        data_provider = TestDataProvider(companies=[company], targets=[target])

        # Calculate Temp Scores
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

    def test_fallback_score(self):
        """
        test fallback score assignment
        """
        # Setup test provider
        company = copy.deepcopy(self.company_base)
        target = self._create_target_with_defaults(company_id=company.company_id)
        data_provider = TestDataProvider(companies=[company], targets=[target])

        # Calculate Temp Scores
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

        companies, targets, pf_companies = self.create_base_companies(
            ["A", "B", "C", "D"]
        )
        target = self._create_target_with_defaults(
            company_id="A",
            coverage_s1=0.75,
            coverage_s2=0.75,
            coverage_s3=0.75,
        )

        targets.append(target)
        target = self._create_target_with_defaults(
            company_id="A",
            coverage_s1=0.99,
            coverage_s2=0.99,
            coverage_s3=0.99,
        )
        targets.append(target)

        target = self._create_target_with_defaults(
            company_id="B",
            scope=EScope.S3,
            coverage_s1=0.75,
            coverage_s2=0.75,
            coverage_s3=0.49,
        )
        targets.append(target)

        target = self._create_target_with_defaults(
            company_id="B",
            scope=EScope.S3,
            coverage_s1=0.99,
            coverage_s2=0.99,
            coverage_s3=0.49,
            end_year=2035,
        )
        targets.append(target)

        target = self._create_target_with_defaults(
            company_id="D",
            coverage_s1=0.95,
            coverage_s2=0.95,
            target_type="int",
            intensity_metric="Revenue",
        )
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
        self.assertAlmostEqual(
            agg_scores.mid.S1S2.all.score, self.BASE_COMP_SCORE, places=4
        )

    def test_target_ids(self):
        """
        test handling of target_ids:
            - select correct target from multiple candidates
            - combined (S1 and S2 into S1S2)
            - split (S1S2S3 into S1S2 and S3)
            - multiple different targets with the same target_id.
              possible bc source data don't enforce target uniqueness.
              Companies can submit targets that map to multiple SBTi targets.
        """
        # given
        companies, targets, pf_companies = self.create_base_companies(
            ["A", "B", "C", "D"]
        )
        should_drop_targets, should_use_targets = [], [*targets]

        # more 'interesting' if Company's ghg3 not all 0 so that company_score S1S2S3 considers combined targets
        for idx, company in enumerate(companies):
            new_ghg3 = (idx / len(companies)) * 100
            company.ghg_s3 = new_ghg3

        target = self._create_target_with_defaults(
            company_id="A",
            scope=EScope.S1,
            end_year=self.mid_end_year,
            coverage_s1=0.75,
            target_ids="A_target-1: should be combined with A_target-2",
        )
        should_use_targets.append(target)
        target = self._create_target_with_defaults(
            company_id="A",
            scope=EScope.S2,
            end_year=self.mid_end_year,
            coverage_s2=0.99,
            target_ids="A_target-2: should be combined with A_target-1",
        )
        should_use_targets.append(target)
        target = self._create_target_with_defaults(
            company_id="A",
            scope=EScope.S2,
            end_year=self.short_end_year,  # v high coverage but SHORT time frame so should be dropped
            coverage_s2=1,
            target_ids=("A_target-3: despite high coverage, should be dropped bc TemperatureScore "
                        "params don't include SHORT time frame"),
        )
        should_drop_targets.append(target)
        target = self._create_target_with_defaults(
            company_id="A",
            scope=EScope.S1S2S3,
            end_year=self.long_end_year,
            target_ids="A_target-4: should be split and used for S1S2 and S3 for LONG time frame scores",
        )
        should_use_targets.append(target)
        target = self._create_target_with_defaults(
            company_id="B",
            end_year=self.long_end_year - 1,
            target_ids="B_target-1",
        )
        should_drop_targets.append(target)
        target = self._create_target_with_defaults(
            company_id="B",
            end_year=self.long_end_year,  # same as target-1 but later base year so should be selected by sorting
            target_ids="B_target-2: should be used over target-1 for LONG time frame",
        )
        should_use_targets.append(target)
        target = self._create_target_with_defaults(
            company_id="D",
            coverage_s1=1,
            coverage_s2=1,
            target_type="int",
            target_ids="D_target-1: high coverage but should not be used over target_base bc type==intensity",
        )
        should_drop_targets.append(target)
        target = self._create_target_with_defaults(
            company_id="D",
            scope=EScope.S3,
            coverage_s1=0.95,
            coverage_s2=0.95,
            target_ids="D_target-2: should be combined with target_base for S1S2S3 scope score",
        )
        should_use_targets.append(target)

        # when
        data_provider = TestDataProvider(companies=companies, targets=[*should_use_targets, *should_drop_targets])
        # Calculate scores & Aggregated values
        temp_score = TemperatureScore(
            time_frames=[
                ETimeFrames.MID,
                ETimeFrames.LONG,
            ],
            scopes=[EScope.S1S2, EScope.S1S2S3],
            aggregation_method=PortfolioAggregationMethod.WATS,
        )
        portfolio_data = SBTi.utils.get_data([data_provider], pf_companies)
        scores = temp_score.calculate(portfolio_data)

        # then - assert should_use_targets are contained in scores, should_drop_targets are not
        actually_used_target_ids = set([target_id for targets in scores["target_ids"].tolist() for target_id in targets or []])
        should_drop_target_ids = set([target for provider in should_drop_targets for target in provider.target_ids])
        should_use_target_ids = set([target for provider in should_use_targets for target in provider.target_ids])

        assert not should_use_target_ids.symmetric_difference(actually_used_target_ids)
        assert not should_drop_target_ids.intersection(actually_used_target_ids)

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
        self.assertEqual(agg_scores.mid.S1S2.all.score, self.BASE_COMP_SCORE)

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

        self.assertAlmostEqual(agg_scores.mid.S1S2.all.score, self.BASE_COMP_SCORE)

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
            company_ids_with_level = [
                f"{ind_level}_{company_id}" for company_id in company_ids
            ]

            companies, targets, pf_companies = self.create_base_companies(
                company_ids_with_level
            )
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
            grouping=["industry_level_1"],
        )

        portfolio_data = SBTi.utils.get_data([data_provider], pf_companies_all)
        scores = temp_score.calculate(portfolio_data)
        agg_scores = temp_score.aggregate_scores(scores)

        for ind_level in industry_levels:
            self.assertAlmostEqual(
                agg_scores.mid.S1S2.grouped[ind_level].score, self.BASE_COMP_SCORE
            )

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
            scenario=scenario,
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

            target = self._create_target_with_defaults(company_id=company_id)

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

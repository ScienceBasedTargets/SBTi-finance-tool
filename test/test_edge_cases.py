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
        self.BASE_COMP_SCORE = 1.14
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
        self.target_base = IDataProviderTarget(
            company_id=company_id,
            target_type="abs",
            scope=EScope.S1,
            coverage_s1=0.95,
            coverage_s2=0.95,
            coverage_s3=0,
            reduction_ambition=0.8,
            base_year=2019,
            base_year_ghg_s1=100,
            base_year_ghg_s2=0,
            base_year_ghg_s3=0,
            end_year=2035,
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


    def test_target_selection_order_independence(self):
        """
        Verify that target selection produces identical temperature scores
        regardless of input row order when a company has multiple targets
        for the same scope/timeframe with identical selection criteria.
        """
        company_id = "OrderTestCo"
        company = IDataProviderCompany(
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

        # Target with complete data — can produce a real score
        target_good = IDataProviderTarget(
            company_id=company_id,
            target_type="abs",
            scope=EScope.S1,
            coverage_s1=0.95,
            coverage_s2=0.95,
            coverage_s3=0,
            reduction_ambition=0.8,
            base_year=2019,
            base_year_ghg_s1=100,
            base_year_ghg_s2=50,
            base_year_ghg_s3=0,
            end_year=2035,
        )

        # Target with same coverage/end_year/type but missing reduction_ambition
        # — would produce fallback score if selected
        target_bad = IDataProviderTarget(
            company_id=company_id,
            target_type="abs",
            scope=EScope.S1,
            coverage_s1=0.95,
            coverage_s2=0.95,
            coverage_s3=0,
            reduction_ambition=float("nan"),
            base_year=2019,
            base_year_ghg_s1=100,
            base_year_ghg_s2=50,
            base_year_ghg_s3=0,
            end_year=2035,
        )

        pf_company = PortfolioCompany(
            company_name=company_id,
            company_id=company_id,
            investment_value=100,
            company_isin=company_id,
        )

        temp_score = TemperatureScore(
            time_frames=[ETimeFrames.MID],
            scopes=[EScope.S1S2],
        )

        # Order 1: good target first
        provider1 = TestDataProvider(
            targets=[copy.deepcopy(target_good), copy.deepcopy(target_bad)],
            companies=[company],
        )
        data1 = SBTi.utils.get_data([provider1], [pf_company])
        scores1 = temp_score.calculate(data1)
        score1 = scores1[
            (scores1["scope"] == EScope.S1S2)
            & (scores1["company_id"] == company_id)
        ]["temperature_score"].iloc[0]

        # Order 2: bad target first
        provider2 = TestDataProvider(
            targets=[copy.deepcopy(target_bad), copy.deepcopy(target_good)],
            companies=[company],
        )
        data2 = SBTi.utils.get_data([provider2], [pf_company])
        scores2 = temp_score.calculate(data2)
        score2 = scores2[
            (scores2["scope"] == EScope.S1S2)
            & (scores2["company_id"] == company_id)
        ]["temperature_score"].iloc[0]

        # Both orderings must produce the same score
        self.assertEqual(
            score1, score2,
            f"Score differs by input order: {score1} vs {score2}",
        )
        # And it should NOT be the fallback score
        self.assertNotEqual(
            score1, 3.2,
            "Good target should have been selected, not fallback",
        )


    def test_power_sector_intensity_mapping(self):
        """
        Verify that Power sector intensity targets use the correct SR15 variable
        (INT.emCO2EI_elecGen) and produce a valid temperature score.

        The methodology Annex 1 references 'INT.emCO2Elec_elecGen' but the
        sr15_mapping.xlsx (source of truth for the tool) maps Power to
        'INT.emCO2EI_elecGen'. Both variables exist in regression_model_summary.xlsx.
        This test ensures the mapping remains consistent and produces valid scores.
        """
        company_id = "PowerCo"
        company = IDataProviderCompany(
            company_name=company_id,
            company_id=company_id,
            ghg_s1s2=500,
            ghg_s3=0,
            company_revenue=1000,
            company_market_cap=5000,
            company_enterprise_value=6000,
            company_total_assets=8000,
            company_cash_equivalents=200,
            isic="D35",  # Power generation ISIC code
        )

        # Intensity target for Power sector
        target = IDataProviderTarget(
            company_id=company_id,
            target_type="int",
            intensity_metric="Power",
            scope=EScope.S1S2,
            coverage_s1=0.95,
            coverage_s2=0.95,
            coverage_s3=0,
            reduction_ambition=0.5,
            base_year=2019,
            base_year_ghg_s1=400,
            base_year_ghg_s2=100,
            base_year_ghg_s3=0,
            end_year=2035,
        )

        pf_company = PortfolioCompany(
            company_name=company_id,
            company_id=company_id,
            investment_value=100,
            company_isin=company_id,
        )

        temp_score = TemperatureScore(
            time_frames=[ETimeFrames.MID],
            scopes=[EScope.S1S2],
        )

        provider = TestDataProvider(
            targets=[target],
            companies=[company],
        )
        data = SBTi.utils.get_data([provider], [pf_company])
        scores = temp_score.calculate(data)

        row = scores[
            (scores["scope"] == EScope.S1S2)
            & (scores["company_id"] == company_id)
        ].iloc[0]

        # Verify the correct SR15 variable was used
        self.assertEqual(
            row["sr15"],
            "INT.emCO2EI_elecGen",
            "Power sector intensity target should map to INT.emCO2EI_elecGen",
        )

        # Verify a valid (non-fallback) temperature score was produced
        self.assertNotEqual(
            row["temperature_score"],
            3.2,
            "Power sector intensity target should produce a calculated score, not fallback",
        )
        # Score should be a reasonable temperature value
        self.assertGreater(row["temperature_score"], 0.0)
        self.assertLess(row["temperature_score"], 4.0)


if __name__ == "__main__":
    test = EdgeCasesTest()
    test.setUp()
    test.test_missing_s2s3_values()

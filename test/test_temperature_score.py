import os
import unittest

import pandas as pd
from SBTi.temperature_score import TemperatureScore, PortfolioAggregationMethod


class TestTemperatureScore(unittest.TestCase):
    """
    Test the reporting functionality. We'll use the Example data provider as the output of this provider is known in
    advance.
    """

    def setUp(self) -> None:
        """
        Create the provider and reporting instance which we'll use later on.
        :return:
        """
        self.temperature_score = TemperatureScore()
        self.data = pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), "inputs",
                                             "data_test_temperature_score.csv"))

    def test_temp_score(self) -> None:
        """
        Test whether the temperature score is calculated as expected.

        :return:
        """
        scores = self.temperature_score.calculate(self.data)
        assert round(scores[
                   (scores["company_name"] == "Company T") &
                   (scores["scope_category"] == "s1s2")
               ]["temperature_score"].iloc[0], 4) == 1.7699, "The temp score was incorrect"
        assert round(scores[
                   (scores["company_name"] == "Company E") &
                   (scores["scope_category"] == "s1s2")
               ]["temperature_score"].iloc[0], 1) == 3.2, "The fallback temp score was incorrect"
        assert round(scores[
                   (scores["company_name"] == "Company AA") &
                   (scores["time_frame"] == "mid") &
                   (scores["scope_category"] == "s1s2s3")
               ]["temperature_score"].iloc[0], 4) == 1.9075, "The aggregated temp score was incorrect"
        assert round(scores[
                   (scores["company_name"] == "Company AA") &
                   (scores["time_frame"] == "long") &
                   (scores["scope_category"] == "s1s2s3")
               ]["temperature_score"].iloc[0], 1) == 3.2, "The aggregated fallback temp score was incorrect"

    def test_portfolio_aggregations(self):
        scores = self.temperature_score.calculate(self.data)
        aggregations_wats = self.temperature_score.aggregate_scores(scores, PortfolioAggregationMethod.WATS)
        assert round(aggregations_wats["short"], 4) == 3.0994, "Short WATS aggregation failed"
        assert round(aggregations_wats["mid"], 4) == 2.9981, "Mid WATS aggregation failed"
        assert round(aggregations_wats["long"], 4) == 3.2000, "Long WATS aggregation failed"
        aggregations_tets = self.temperature_score.aggregate_scores(scores, PortfolioAggregationMethod.TETS)
        assert round(aggregations_tets["short"], 4) == 3.0289, "Short TETS aggregation failed"
        assert round(aggregations_tets["mid"], 4) == 3.0241, "Mid TETS aggregation failed"
        assert round(aggregations_tets["long"], 4) == 3.2000, "Long TETS aggregation failed"

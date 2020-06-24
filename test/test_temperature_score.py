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
        self.assertAlmostEqual(scores[
                   (scores["company_name"] == "Company T") &
                   (scores["scope_category"] == "s1s2")
               ]["temperature_score"].iloc[0], 1.7699, places=4, msg="The temp score was incorrect")
        self.assertAlmostEqual(scores[
                   (scores["company_name"] == "Company E") &
                   (scores["scope_category"] == "s1s2")
               ]["temperature_score"].iloc[0], 3.2, places=4, msg="The fallback temp score was incorrect")
        self.assertAlmostEqual(scores[
                   (scores["company_name"] == "Company AA") &
                   (scores["time_frame"] == "mid") &
                   (scores["scope_category"] == "s1s2s3")
               ]["temperature_score"].iloc[0], 1.9075, places=4, msg="The aggregated temp score was incorrect")
        self.assertAlmostEqual(scores[
                   (scores["company_name"] == "Company AA") &
                   (scores["time_frame"] == "long") &
                   (scores["scope_category"] == "s1s2s3")
               ]["temperature_score"].iloc[0], 3.2, places=5, msg="The aggregated fallback temp score was incorrect")

    def test_portfolio_aggregations(self):
        scores = self.temperature_score.calculate(self.data)
        aggregations = self.temperature_score.aggregate_scores(scores, PortfolioAggregationMethod.WATS)
        assert round(aggregations["short"], 4) == 3.0994, "Short WATS aggregation failed"
        assert round(aggregations["mid"], 4) == 2.9981, "Mid WATS aggregation failed"
        assert round(aggregations["long"], 4) == 3.2000, "Long WATS aggregation failed"
        aggregations = self.temperature_score.aggregate_scores(scores, PortfolioAggregationMethod.TETS)
        assert round(aggregations["short"], 4) == 3.0289, "Short TETS aggregation failed"
        assert round(aggregations["mid"], 4) == 3.0241, "Mid TETS aggregation failed"
        assert round(aggregations["long"], 4) == 3.2000, "Long TETS aggregation failed"
        aggregations = self.temperature_score.aggregate_scores(scores, PortfolioAggregationMethod.MOTS)
        assert round(aggregations["short"], 4) == 3.0363, "Short MOTS aggregation failed"
        assert round(aggregations["mid"], 4) == 3.0293, "Mid MOTS aggregation failed"
        assert round(aggregations["long"], 4) == 3.2000, "Long MOTS aggregation failed"
        aggregations = self.temperature_score.aggregate_scores(scores, PortfolioAggregationMethod.EOTS)
        assert round(aggregations["short"], 4) == 3.0641, "Short EOTS aggregation failed"
        assert round(aggregations["mid"], 4) == 3.0359, "Mid EOTS aggregation failed"
        assert round(aggregations["long"], 4) == 3.2000, "Long EOTS aggregation failed"
        aggregations = self.temperature_score.aggregate_scores(scores, PortfolioAggregationMethod.ECOTS)
        assert round(aggregations["short"], 4) == 3.0363, "Short ECOTS aggregation failed"
        assert round(aggregations["mid"], 4) == 3.0293, "Mid ECOTS aggregation failed"
        assert round(aggregations["long"], 4) == 3.2000, "Long ECOTS aggregation failed"
        aggregations = self.temperature_score.aggregate_scores(scores, PortfolioAggregationMethod.AOTS)
        assert round(aggregations["short"], 4) == 3.0363, "Short AOTS aggregation failed"
        assert round(aggregations["mid"], 4) == 3.0293, "Mid AOTS aggregation failed"
        assert round(aggregations["long"], 4) == 3.2000, "Long AOTS aggregation failed"


if __name__ == "__main__":
    test = TestTemperatureScore()
    test.setUp()
    test.test_temp_score()
    test.test_portfolio_aggregations()

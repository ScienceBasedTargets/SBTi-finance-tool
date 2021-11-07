import os
import unittest

import pandas as pd

from SBTi.configs import ColumnsConfig
from SBTi.interfaces import ETimeFrames, EScope
from SBTi.temperature_score import TemperatureScore
from SBTi.portfolio_aggregation import PortfolioAggregationMethod


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
        self.temperature_score = TemperatureScore(
            time_frames=list(ETimeFrames), scopes=EScope.get_result_scopes()
        )
        self.data = pd.read_csv(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "inputs",
                "data_test_temperature_score.csv",
            )
        )
        scope_map = {"S1+S2": EScope.S1S2, "S3": EScope.S3, "S1+S2+S3": EScope.S1S2S3}
        self.data[ColumnsConfig.SCOPE] = self.data[ColumnsConfig.SCOPE].map(scope_map)
        time_frame_map = {
            "short": ETimeFrames.SHORT,
            "mid": ETimeFrames.MID,
            "long": ETimeFrames.LONG,
        }
        self.data[ColumnsConfig.TIME_FRAME] = self.data[ColumnsConfig.TIME_FRAME].map(
            time_frame_map
        )

    def test_temp_score(self) -> None:
        """
        Test whether the temperature score is calculated as expected.

        :return:
        """
        scores = self.temperature_score.calculate(self.data)
        self.assertAlmostEqual(
            scores[
                (scores["company_name"] == "Company T")
                & (scores["scope"] == EScope.S1S2)
            ]["temperature_score"].iloc[0],
            1.77,
            places=2,
            msg="The temp score was incorrect",
        )
        self.assertAlmostEqual(
            scores[
                (scores["company_name"] == "Company E")
                & (scores["scope"] == EScope.S1S2)
            ]["temperature_score"].iloc[0],
            3.2,
            places=2,
            msg="The fallback temp score was incorrect",
        )
        self.assertAlmostEqual(
            scores[
                (scores["company_name"] == "Company AA")
                & (scores["time_frame"] == ETimeFrames.MID)
                & (scores["scope"] == EScope.S1S2S3)
            ]["temperature_score"].iloc[0],
            1.97,
            places=2,
            msg="The aggregated temp score was incorrect",
        )
        self.assertAlmostEqual(
            scores[
                (scores["company_name"] == "Company AA")
                & (scores["time_frame"] == ETimeFrames.LONG)
                & (scores["scope"] == EScope.S1S2S3)
            ]["temperature_score"].iloc[0],
            3.2,
            places=5,
            msg="The aggregated fallback temp score was incorrect",
        )

    def test_portfolio_aggregations(self):
        scores = self.temperature_score.calculate(self.data)
        aggregations = self.temperature_score.aggregate_scores(scores)
        self.assertAlmostEqual(
            aggregations.short.S1S2.all.score,
            2.73,
            places=2,
            msg="Short WATS aggregation failed",
        )
        self.assertAlmostEqual(
            aggregations.mid.S1S2.all.score,
            2.89,
            places=2,
            msg="Mid WATS aggregation failed",
        )
        self.assertAlmostEqual(
            aggregations.long.S1S2.all.score,
            3.2,
            places=2,
            msg="Long WATS aggregation failed",
        )
        self.temperature_score.aggregation_method = PortfolioAggregationMethod.TETS
        aggregations = self.temperature_score.aggregate_scores(scores)
        self.assertAlmostEqual(
            aggregations.short.S1S2.all.score,
            2.86,
            places=2,
            msg="Short TETS aggregation failed",
        )
        self.assertAlmostEqual(
            aggregations.mid.S1S2.all.score,
            3.41,
            places=2,
            msg="Mid TETS aggregation failed",
        )
        self.assertAlmostEqual(
            aggregations.long.S1S2.all.score,
            3.2,
            places=2,
            msg="Long TETS aggregation failed",
        )
        self.temperature_score.aggregation_method = PortfolioAggregationMethod.MOTS
        aggregations = self.temperature_score.aggregate_scores(scores)
        self.assertAlmostEqual(
            aggregations.short.S1S2.all.score,
            2.88,
            places=2,
            msg="Short MOTS aggregation failed",
        )
        self.assertAlmostEqual(
            aggregations.mid.S1S2.all.score,
            3.43,
            places=2,
            msg="Mid MOTS aggregation failed",
        )
        self.assertAlmostEqual(
            aggregations.long.S1S2.all.score,
            3.2,
            places=2,
            msg="Long MOTS aggregation failed",
        )
        self.temperature_score.aggregation_method = PortfolioAggregationMethod.EOTS
        aggregations = self.temperature_score.aggregate_scores(scores)
        self.assertAlmostEqual(
            aggregations.short.S1S2.all.score,
            2.93,
            places=2,
            msg="Short EOTS aggregation failed",
        )
        self.assertAlmostEqual(
            aggregations.mid.S1S2.all.score,
            3.48,
            places=2,
            msg="Mid EOTS aggregation failed",
        )
        self.assertAlmostEqual(
            aggregations.long.S1S2.all.score,
            3.2,
            places=2,
            msg="Long EOTS aggregation failed",
        )
        self.temperature_score.aggregation_method = PortfolioAggregationMethod.ECOTS
        aggregations = self.temperature_score.aggregate_scores(scores)
        self.assertAlmostEqual(
            aggregations.short.S1S2.all.score,
            2.93,
            places=2,
            msg="Short ECOTS aggregation failed",
        )
        self.assertAlmostEqual(
            aggregations.mid.S1S2.all.score,
            3.48,
            places=2,
            msg="Mid ECOTS aggregation failed",
        )
        self.assertAlmostEqual(
            aggregations.long.S1S2.all.score,
            3.2,
            places=2,
            msg="Long ECOTS aggregation failed",
        )
        self.temperature_score.aggregation_method = PortfolioAggregationMethod.AOTS
        aggregations = self.temperature_score.aggregate_scores(scores)
        self.assertAlmostEqual(
            aggregations.short.S1S2.all.score,
            2.88,
            places=2,
            msg="Short AOTS aggregation failed",
        )
        self.assertAlmostEqual(
            aggregations.mid.S1S2.all.score,
            3.43,
            places=2,
            msg="Mid AOTS aggregation failed",
        )
        self.assertAlmostEqual(
            aggregations.long.S1S2.all.score,
            3.2,
            places=2,
            msg="Long AOTS aggregation failed",
        )


if __name__ == "__main__":
    test = TestTemperatureScore()
    test.setUp()
    test.test_temp_score()
    test.test_portfolio_aggregations()

import os
import unittest

import pandas as pd

from SBTi.portfolio_aggregation import PortfolioAggregationMethod
from SBTi.portfolio_coverage_tvp import PortfolioCoverageTVP


class TestPortfolioCoverageTVP(unittest.TestCase):
    """
    Test the TVP portfolio coverage (checking which companies have a valid SBTi approved target.
    """

    def setUp(self) -> None:
        """
        Create the portfolio coverage tvp instance.
        :return:
        """
        self.portfolio_coverage_tvp = PortfolioCoverageTVP()
        self.data = pd.read_csv(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "inputs",
                "data_test_portfolio_coverage.csv",
            )
        )

    def test_coverage(self) -> None:
        """
        Test whether the test companies are assigned the right status.

        :return:
        """
        coverage = self.portfolio_coverage_tvp.get_portfolio_coverage(
            self.data, PortfolioAggregationMethod.WATS
        )
        self.assertAlmostEqual(
            coverage, 32.0663, places=4, msg="The portfolio coverage was not correct"
        )


if __name__ == "__main__":
    test = TestPortfolioCoverageTVP()
    test.setUp()
    test.test_coverage()

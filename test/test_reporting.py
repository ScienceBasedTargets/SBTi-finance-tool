import unittest

from SBTi.data.example_provider import ExampleProvider
from SBTi.reporting import Reporting


class TestReporting(unittest.TestCase):
    """
    Test the reporting functionality. We'll use the Example data provider as the output of this provider is known in
    advance.
    """

    def setUp(self) -> None:
        """
        Create the provider and reporting instance which we'll use later on.
        :return:
        """
        self.provider = ExampleProvider()
        self.reporting = Reporting(-1.0, 3.2)

    def test_temp_score(self) -> None:
        assert self.reporting.get_temp_score(self.provider, "Ortec Finance B.V.") == 0.0, "The temp score was incorrect"
        assert self.reporting.get_temp_score(self.provider, "Ortec Finance Data Analytics B.V.") == 3.2, \
            "The fallback temp score was incorrect"

    def test_emissions(self) -> None:
        """
        Test the emissions report
        :return:
        """
        assert self.reporting.get_emissions(self.provider, "Ortec Finance B.V.") == 0.0, "The emissions were incorrect"
        assert self.reporting.get_emissions(self.provider, "Ortec Finance Data Analytics B.V.") == -1.0, \
            "The fallback emissions were incorrect"

    def test_report(self) -> None:
        """
        Test the report.
        :return:
        """
        # We're testing with 2 shares of Ortec Finance and 3 shares of Ortec Finance Data Analytics
        portfolio = [{"id": "Ortec Finance B.V.", "proportion": 2},
                     {"id": "Ortec Finance Data Analytics B.V.", "proportion": 3}]
        portfolio, coverage, weighted_emissions, weighted_temp_score = self.reporting.get_report(self.provider,
                                                                                                 portfolio)

        assert coverage == 0.5, "The coverage was not 50%"
        assert round(weighted_emissions * 100) / 100 == -0.6, "The weighted emissions were not -0.6"
        assert round(weighted_temp_score * 100) / 100 == 1.92, "The weighted temperature score was not 1.92"

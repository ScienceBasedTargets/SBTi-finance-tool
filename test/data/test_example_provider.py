import unittest

from SBTi.data.data_provider import CompanyNotFoundException
from SBTi.data.example_provider import ExampleProvider


class TestDataProviderExample(unittest.TestCase):
    """
    Test the example data provider. This test case may be used as a starting point for new data providers.
    """

    def setUp(self) -> None:
        """
        Create the provider which we'll use later on.
        :return:
        """
        self.provider = ExampleProvider()

    def test_report(self) -> None:
        """
        Test the report, this should return 0.0 for both the emissions and the temp score.
        :return:
        """
        emissions, temp_score = self.provider.get_report("Ortec Finance B.V.")
        self.assertEqual(emissions, 0.0)
        self.assertEqual(temp_score, 0.0)

    def test_unknown_company(self) -> None:
        """
        Test an unknown company. This should return a CompanyNotFoundException.
        :return:
        """
        try:
            _, _ = self.provider.get_report("Ortec Finance Data Analytics B.V.")
            self.assertTrue(False)
        except CompanyNotFoundException:
            self.assertTrue(True)

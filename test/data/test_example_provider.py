import unittest


class TestDataProviderExample(unittest.TestCase):
    """
    Test the example data provider. This test case may be used as a starting point for new data providers.
    """

    def setUp(self) -> None:
        """
        Create the provider which we'll use later on.
        :return:
        """
        pass

    def test_targets(self) -> None:
        """
        Test the report, this should return 0.0 for both the emissions and the temp score.
        :return:
        """
        # TODO: Test the targets returned from the Excel connector
        pass

    def test_company_data(self) -> None:
        """
        Test an unknown company. This should return a CompanyNotFoundException.
        :return:
        """
        # TODO: Test the company data from the Excel connector
        pass

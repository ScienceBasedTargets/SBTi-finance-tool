import unittest

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

    def test_coverage(self) -> None:
        """
        Test whether the test companies are assigned the right status.

        :return:
        """
        companies = [
            {"company_id": "US0079031078", "company_name": "Advanced Micro Devices, Inc"},
            {"company_name": "Capitas Finance Limited"},
            {"company_id": "TST123456789", "company_name": "Non existant test company"},
        ]
        self.portfolio_coverage_tvp.get_coverage(companies, inplace=True)
        result_map = {"Advanced Micro Devices, Inc": "Targets Set",
                      "Capitas Finance Limited": "Committed",
                      "Non existant test company": "No target"}

        for company in companies:
            assert company["sbti_target_status"] == result_map[company["company_name"]], "The target was not correct"


if __name__ == "__main__":
    test = TestPortfolioCoverageTVP()
    test.setUp()
    test.test_coverage()

import SBTi.data
from SBTi.data.csv import CSVProvider

import os
import unittest


class TestWaterfall(unittest.TestCase):
    """
    Test the waterfall method for loading data from the data providers.
    """

    def setUp(self) -> None:
        """
        Create the providers and list of companies which we'll use later on.
        """
        self.companies = [
            {"company_name": "Company A", "company_id": "JP0000000001"},
            {"company_name": "Company D", "company_id": "SE0000000004"},
            {"company_name": "Capgemini Group", "company_id": "FR0000125338"},
            {"company_name": "Company N", "company_id": "TST0000000001"},
        ]
        self.data_providers = [
            CSVProvider(
                path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "../", "inputs",
                                  "data_test_waterfall_a.csv"),
                path_targets=os.path.join(os.path.dirname(os.path.realpath(__file__)), "../", "inputs",
                                          "data_test_temperature_score_targets.csv"),
                encoding="iso-8859-1"
            ),
            CSVProvider(
                path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "../", "inputs",
                                  "data_test_waterfall_b.csv"),
                path_targets=os.path.join(os.path.dirname(os.path.realpath(__file__)), "../", "inputs",
                                          "data_test_temperature_score_targets.csv"),
                encoding="iso-8859-1"
            ),
        ]

    def test_company_data(self) -> None:
        """
        Test whether data is retrieved as expected.
        """
        company_data = SBTi.data.get_company_data(
            self.data_providers, [company["company_id"] for company in self.companies])
        assert len(set([company.company_id for company in company_data])) == 3, \
            "The numbers of companies does not match"


if __name__ == "__main__":
    test = TestWaterfall()
    test.setUp()
    test.test_company_data()

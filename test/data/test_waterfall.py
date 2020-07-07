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
            {"company_name": "Company AA", "company_id": None},
            {"company_name": "Company F", "company_id": None},
            {"company_name": "Company Q", "company_id": None},
            {"company_name": "Company N", "company_id": None},
        ]
        self.data_providers = [
            CSVProvider(
                path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "../", "inputs",
                                  "data_test_waterfall_a.csv"),
                path_targets=os.path.join(os.path.dirname(os.path.realpath(__file__)), "../", "inputs",
                                          "data_test_temperature_score_targets.csv")
            ),
            CSVProvider(
                path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "../", "inputs",
                                  "data_test_waterfall_b.csv"),
                path_targets=os.path.join(os.path.dirname(os.path.realpath(__file__)), "../", "inputs",
                                          "data_test_temperature_score_targets.csv")
            ),
            CSVProvider(
                path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "../", "inputs",
                                  "data_test_waterfall_c.csv"),
                path_targets=os.path.join(os.path.dirname(os.path.realpath(__file__)), "../", "inputs",
                                          "data_test_temperature_score_targets.csv")
            ),
        ]

    def test_company_data(self) -> None:
        """
        Test whether data is retrieved as expected.
        """
        company_data = SBTi.data.get_company_data(self.data_providers, self.companies)
        assert len(company_data) == 3, "The numbers of companies does not match"


if __name__ == "__main__":
    test = TestWaterfall()
    test.setUp()
    test.test_company_data()
from typing import Optional, List

import requests

from SBTi.data.data_provider import DataProvider
from SBTi.interfaces import IDataProviderTarget, IDataProviderCompany


class Bloomberg(DataProvider):
    """
    Data provider skeleton for Bloomberg.
    """

    def _request(self, endpoint: str, data: dict) -> Optional[object]:
        """
        Request data from the server.
        Note: This request does in no way reflect the actual implementation, this is only a stub to show what a
        potential API request COULD look like.

        :param endpoint: The endpoint of the API
        :param data: The data to send as a body
        :return: The returned data, None in case of an error.
        """
        try:
            headers = {"Authorization": "Basic: {}:{}".format("username", "password")}
            r = requests.post(
                "{}{}".format("host", endpoint), json=data, headers=headers
            )
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            return None
        return None

    def get_targets(self, company_ids: List[str]) -> List[IDataProviderTarget]:
        """
        Get all relevant targets for a list of company ids (ISIN). This method should return a list of
        IDataProviderTarget instances.

        :param company_ids: A list of company IDs (ISINs)
        :return: A list containing the targets
        """
        # TODO: Make an API request
        # TODO: Transform the result into a dataframe
        # TODO: Make sure the columns align with those defined in the docstring
        raise NotImplementedError

    def get_company_data(self, company_ids: List[str]) -> List[IDataProviderCompany]:
        """
        Get all relevant data for a list of company ids (ISIN). This method should return a list of IDataProviderCompany
        instances.

        :param company_ids: A list of company IDs (ISINs)
        :return: A list containing the company data
        """
        # TODO: Make an API request
        # TODO: Transform the result into a dataframe
        # TODO: Make sure the columns align with those defined in the docstring
        raise NotImplementedError

    def get_sbti_targets(self, companies: list) -> list:
        """
        For each of the companies, get the status of their target (Target set, Committed or No target) as it's known to
        the SBTi.

        :param companies: A list of companies. Each company should be a dict with a "company_name" and "company_id"
                            field.
        :return: The original list, enriched with a field called "sbti_target_status"
        """
        # TODO: Make an API request
        # TODO: Extract the SBTi target status from the response
        # TODO: Enrich the original list with this data
        raise NotImplementedError

from typing import List

from SBTi.data.data_provider import DataProvider
from SBTi.interfaces import IDataProviderCompany, IDataProviderTarget


class Trucost(DataProvider):
    """
    Data provider skeleton for Trucost.
    """

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

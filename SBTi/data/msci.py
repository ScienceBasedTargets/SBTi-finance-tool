import pandas as pd
from SBTi.data.data_provider import DataProvider


class MSCI(DataProvider):
    """
    Data provider skeleton for MSCI.
    """

    def get_targets(self, companies: list) -> pd.DataFrame:
        """
        Get all the targets for the whole portfolio of companies. This should return a dataframe, containing at least
        the following columns:

        * company_name: The name of the company
        * company_id: The ID of the company
        * target_reference_number: Int *x* of Abs *x*
        * target_reference_number: Int *x* of Abs *x*
        * scope: The scope of the target. This should be a valid scope in the SR15 mapping
        * base_year: The base year of the target
        * start_year: The start year of the target
        * target_year: The year when the target should be achieved
        * reduction_from_base_year: Targeted reduction in emissions from the base year
        * emissions_in_scope: Company emissions in the target's scope at start of the base year
        * achieved_reduction: The emission reduction that has already been achieved

        :param companies: A list of companies. Each company should be a dict with a "company_name" and "company_id"
                            field.
        :return: A dataframe containing the targets
        """
        # TODO: Make an API request
        # TODO: Transform the result into a dataframe
        # TODO: Make sure the columns align with those defined in the docstring
        raise NotImplementedError

    def get_company_data(self, companies: list) -> pd.DataFrame:
        """
        Get all relevant data for a certain company. Should return a dataframe, containing at least the following
        columns:

        * company_name: The name of the company
        * company_id: The ID of the company
        * industry: The industry the company is working in. This should be a valid industry in the SR15 mapping. If not
            it will be converted to "Others" (or whichever value is set in the config as the default
        * s1s2_emissions: Total company emissions in the S1 + S2 scope
        * s3_emissions: Total company emissions in the S3 scope
        * portfolio_weight: The weight of the company in the portfolio. Only required to use the WATS portfolio
            aggregation.
        * market_cap: Market capitalization of the company. Only required to use the MOTS portfolio aggregation.
        * investment_value: The investment value of the investment in this company. Only required to use the MOTS, EOTS,
            ECOTS and AOTS portfolio aggregation.
        * company_enterprise_value: The enterprise value of the company. Only required to use the EOTS portfolio
            aggregation.
        * company_ev_plus_cash: The enterprise value of the company plus cash. Only required to use the ECOTS portfolio
            aggregation.
        * company_total_assets: The total assets of the company. Only required to use the AOTS portfolio aggregation.


        :param companies: A list of companies. Each company should be a dict with a "company_name" and "company_id"
                            field.
        :return: A dataframe containing the company data
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

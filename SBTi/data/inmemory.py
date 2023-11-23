from typing import Type, List
from pydantic import ValidationError
import pandas as pd
from SBTi.data.data_provider import DataProvider
from SBTi.interfaces import IDataProviderCompany, IDataProviderTarget
from SBTi.configs import ColumnsConfig

class_definitions = {
    "fundamental": {
        "company_name": str,
        "company_id": str,
        "isic": str,
        "country": str,
        "region": str,
        "industry_level_1": str,
        "industry_level_2": str,
        "industry_level_3": str,
        "industry_level_4": str,
        "sector": str,
        "ghg_s1s2": str,
        "ghg_s3": str,
        "company_revenue": str,
        "company_market_cap": str,
        "company_enterprise_value": str,
        "company_total_assets": str,
        "company_cash_equivalents": str,
    },
    "target": {
        "company_name": str,
        "company_id": str,
        "target_type": str,
        "intensity_metric": str,
        "scope": str,
        "coverage_s1": str,
        "coverage_s2": str,
        "coverage_s3": str,
        "reduction_ambition": str,
        "base_year": str,
        "end_year": str,
        "start_year": str,
        "base_year_ghg_s1": str,
        "base_year_ghg_s2": str,
        "base_year_ghg_s3": str,
        "achieved_reduction": str,
    },
}


class InMemoryProvider(DataProvider):
    """
    Data provider to read in-memory dict.

    :param fundamental: A dictionary with the fundamental data
    :param targets: A dictionary with the target data
    """

    def __init__(
        self,
        fundamental: class_definitions["fundamental"],
        targets: class_definitions["target"],
        config: Type[ColumnsConfig] = ColumnsConfig,
    ):
        super().__init__()
        self.data_fundamental = pd.DataFrame(fundamental)
        self.data_targets = pd.DataFrame(targets)
        self.c = config

    def get_targets(self, company_ids: list) -> List[IDataProviderTarget]:
        """
        Get all relevant targets for a list of company ids (ISIN). This method should return a list of
        IDataProviderTarget instances.

        :param company_ids: A list of company IDs (ISINs)
        :return: A list containing the targets
        """
        model_targets = self._target_df_to_model(self.data_targets)
        model_targets = [
            target for target in model_targets if target.company_id in company_ids
        ]
        return model_targets

    def _target_df_to_model(self, df_targets):
        """
        transforms target Dataframe into list of IDataProviderTarget instances

        :param df_targets: pandas Dataframe with targets
        :return: A list containing the targets
        """
        targets = df_targets.to_dict(orient="records")
        model_targets: List[IDataProviderTarget] = []

        for target in targets:
            try:
                model_targets.append(IDataProviderTarget.parse_obj(target))
            except ValidationError as e:
                print(
                    "(one of) the target(s) of company %s is invalid and will be skipped"
                    % target[self.c.COMPANY_NAME]
                )
                continue

        return model_targets

    def get_company_data(self, company_ids: list) -> List[IDataProviderCompany]:
        """
        Get all relevant data for a list of company ids (ISIN). This method should return a list of IDataProviderCompany
        instances.

        :param company_ids: A list of company IDs (ISINs)
        :return: A list containing the company data
        """
        companies = self.data_fundamental.to_dict(orient="records")
        model_companies: List[IDataProviderCompany] = [
            IDataProviderCompany.parse_obj(company) for company in companies
        ]
        model_companies = [
            target for target in model_companies if target.company_id in company_ids
        ]
        return model_companies

    def get_sbti_targets(self, companies: list) -> list:
        """
        For each of the companies, get the status of their target (Target set, Committed or No target) as it's known to
        the SBTi.

        :param companies: A list of companies. Each company should be a dict with a "company_name" and "company_id"
                            field.
        :return: The original list, enriched with a field called "sbti_target_status"
        """
        return self.data_fundamental[
            (
                self.data_fundamental["company_id"].isin(
                    [company["company_id"] for company in companies]
                )
                & self.data_fundamental["company_id"].notnull()
            )
        ].copy()

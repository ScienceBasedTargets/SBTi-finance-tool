from typing import List, Type
import requests
import pandas as pd

from SBTi.configs import PortfolioCoverageTVPConfig
from SBTi.interfaces import IDataProviderCompany


class SBTi:
    """
    Data provider skeleton for SBTi. This class only provides the sbti_validated field for existing companies.
    """

    def __init__(
        self, config: Type[PortfolioCoverageTVPConfig] = PortfolioCoverageTVPConfig
    ):
        self.c = config
        # Fetch CTA file from SBTi website
        resp = requests.get(self.c.CTA_FILE_URL)
        # Write CTA file to disk
        with open(self.c.FILE_TARGETS, 'wb') as output:
            output.write(resp.content)
            print(resp.status_code)
        # Read CTA file into pandas dataframe
        self.targets = pd.read_excel(self.c.FILE_TARGETS)

    # def get_sbti_targets(
    #     self, companies: List[IDataProviderCompany], isin_map: dict
    # ) -> List[IDataProviderCompany]:
    #     """
    #     Check for each company if they have an SBTi validated target.

    #     :param companies: A list of IDataProviderCompany instances
    #     :param isin_map: A map from company id to ISIN
    #     :return: A list of IDataProviderCompany instances, supplemented with the SBTi information
    #     """
    #     for company in companies:
    #         targets = self.targets[
    #             self.targets[self.c.COL_COMPANY_ISIN]
    #             == isin_map.get(company.company_id)
    #         ]
    #         if len(targets) > 0:
    #             company.sbti_validated = (
    #                 self.c.VALUE_TARGET_SET in targets[self.c.COL_TARGET_STATUS].values
    #             )

    #     return companies

    def get_sbti_targets(
        self, companies: List[IDataProviderCompany], id_map: dict
    ) -> List[IDataProviderCompany]:
        """
        Check for each company if they have an SBTi validated target, first using the company LEI, 
        if available, and then using the ISIN.
        
        :param companies: A list of IDataProviderCompany instances
        :param id_map: A map from company id to a tuple of (ISIN, LEI)
        :return: A list of IDataProviderCompany instances, supplemented with the SBTi information
        """
        for company in companies:
            isin, lei = id_map.get(company.company_id)
            # Check lei and length of lei to avoid zeros 
            if not lei.lower() == 'nan' and len(lei) > 3:
                targets = self.targets[
                    self.targets[self.c.COL_COMPANY_LEI] == lei
                ]
            elif not isin.lower() == 'nan':
                targets = self.targets[
                    self.targets[self.c.COL_COMPANY_ISIN] == isin
                ]
            else:
                continue
            if len(targets) > 0:
                company.sbti_validated = (
                    self.c.VALUE_TARGET_SET in targets[self.c.COL_TARGET_STATUS].values
                )
        return companies

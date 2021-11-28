from typing import List, Type

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
        self.targets = pd.read_excel(self.c.FILE_TARGETS)

    def get_sbti_targets(
        self, companies: List[IDataProviderCompany], isin_map: dict
    ) -> List[IDataProviderCompany]:
        """
        Check for each company if they have an SBTi validated target.

        :param companies: A list of IDataProviderCompany instances
        :param isin_map: A map from company id to ISIN
        :return: A list of IDataProviderCompany instances, supplemented with the SBTi information
        """
        for company in companies:
            targets = self.targets[
                self.targets[self.c.COL_COMPANY_ISIN]
                == isin_map.get(company.company_id)
            ]
            if len(targets) > 0:
                company.sbti_validated = (
                    self.c.VALUE_TARGET_SET in targets[self.c.COL_TARGET_STATUS].values
                )

        return companies

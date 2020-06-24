import copy

import pandas as pd

from SBTi.configs import PortfolioCoverageTVPConfig


class PortfolioCoverageTVP:
    """
    Lookup the companies in the given portfolio and determine whether they have a SBTi approved target.

    :param config: A class defining the constants that are used throughout this class. This parameter is only required
                    if you'd like to overwrite a constant. This can be done by extending the PortfolioCoverageTVPConfig
                    class and overwriting one of the parameters.
    """

    def __init__(self, config: PortfolioCoverageTVPConfig = PortfolioCoverageTVPConfig):
        self.c = config
        self.targets = pd.read_excel(self.c.FILE_TARGETS)

    def get_coverage(self, companies: list, inplace=True) -> list:
        """
        For each of the companies, get the status of their target (Target set, Committed or No target) as it's known to
        the SBTi. Matching will be done primarily on the company ID (ASIN) and secondary on the company name.

        :param companies: A list of companies defined by a dictionary, which has at least the following fields:
                            company_name, company_id.
        :param inplace: If true, the given list is updated in place, if false a copy of the list is made and returned
        :return: The original list, enriched with a field called "sbti_target_status"
        """
        if not inplace:
            companies = copy.deepcopy(companies)

        for i, company in enumerate(companies):
            if company.get(self.c.INPUT_COMPANY_ID) is not None:
                targets = self.targets[self.targets[self.c.COL_COMPANY_ID] == company[self.c.INPUT_COMPANY_ID]]
            else:
                targets = []

            if len(targets) == 0:
                targets = self.targets[self.targets[self.c.COL_COMPANY_NAME] == company[self.c.INPUT_COMPANY_NAME]]
            if len(targets) > 1:
                raise ValueError("There is more than one target classification available for company: {}".format(
                    company[self.c.INPUT_COMPANY_NAME]))
            elif len(targets) == 0:
                companies[i][self.c.OUTPUT_TARGET] = self.c.VALUE_NO_TARGET
            else:
                companies[i][self.c.OUTPUT_TARGET] = targets.iloc[0][self.c.COL_TARGET_STATUS]

        return companies

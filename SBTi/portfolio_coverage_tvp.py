from typing import Type, Optional

import pandas as pd

from SBTi.configs import PortfolioCoverageTVPConfig
from SBTi.portfolio_aggregation import PortfolioAggregation, PortfolioAggregationMethod


class PortfolioCoverageTVP(PortfolioAggregation):
    """
    Lookup the companies in the given portfolio and determine whether they have a SBTi approved target.

    :param config: A class defining the constants that are used throughout this class. This parameter is only required
                    if you'd like to overwrite a constant. This can be done by extending the PortfolioCoverageTVPConfig
                    class and overwriting one of the parameters.
    """

    def __init__(self, config: Type[PortfolioCoverageTVPConfig] = PortfolioCoverageTVPConfig):
        super().__init__(config)
        self.c: Type[PortfolioCoverageTVPConfig] = config
        self.targets = pd.read_excel(self.c.FILE_TARGETS)

    def _get_target_status(self, company: pd.Series) -> str:
        """
        Get the target status (Target set, Committed or No target) as it's known to the SBTi for a certain row out of
        the company data dataframe.

        :param company: The company data
        :return: The SBTi status of the target
        """
        if self.c.COLS.COMPANY_ID in company and company[self.c.COLS.COMPANY_ID] is not None:
            if not pd.isna(company[self.c.COLS.COMPANY_ID]):
                try:
                    targets = self.targets[self.targets[self.c.COL_COMPANY_ID] == company[self.c.COL_COMPANY_ID]]
                except:
                    targets = []
            else:
                targets = []
        else:
            targets = []

        if len(targets) == 0:
            targets = self.targets[self.targets[self.c.COL_COMPANY_NAME] == company[self.c.COLS.COMPANY_NAME]]
        if len(targets) > 1:
            raise ValueError("There is more than one target classification available for company: {}".format(
                company[self.c.COLS.COMPANY_NAME]))
        elif len(targets) == 0:
            return self.c.VALUE_TARGET_NO
        else:
            return targets.iloc[0][self.c.COL_TARGET_STATUS]

    def get_portfolio_coverage(self, company_data: pd.DataFrame,
                               portfolio_aggregation_method: Type[PortfolioAggregationMethod]) -> Optional[float]:
        """
        For each of the companies, get the status of their target (Target set, Committed or No target) as it's known to
        the SBTi. Matching will be done primarily on the company ID (ASIN) and secondary on the company name.

        :param company_data: The company as it is returned from the data provider's get_company_data call.
        :param portfolio_aggregation_method: PortfolioAggregationMethod: The aggregation method to use
        :return: The aggregated score
        """
        # If the target status is not included in the data provider data, we'll look for the target in our Excel file
        if self.c.OUTPUT_TARGET_STATUS not in company_data.columns:
            company_data[self.c.OUTPUT_TARGET_STATUS] = company_data.apply(lambda row: self._get_target_status(row),
                                                                           axis=1)
        company_data[self.c.OUTPUT_TARGET_STATUS] = company_data.apply(
            lambda row: self.c.TARGET_SCORE_MAP[row[self.c.OUTPUT_TARGET_STATUS]], axis=1
        )

        return self._calculate_aggregate_score(company_data, self.c.OUTPUT_TARGET_STATUS,
                                               self.c.OUTPUT_WEIGHTED_TARGET_STATUS, portfolio_aggregation_method).sum()


# Testing
# from SBTi.portfolio_aggregation import PortfolioAggregationMethod
# portfolio_data = pd.read_excel('C:/Projects/SBTi/testing_2.xlsx')
# portfolio_data.drop(columns='Unnamed: 0',inplace=True)
# x = PortfolioCoverageTVP()
# coverage = x.get_portfolio_coverage(portfolio_data,PortfolioAggregationMethod.WATS)

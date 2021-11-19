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

    def __init__(
        self, config: Type[PortfolioCoverageTVPConfig] = PortfolioCoverageTVPConfig
    ):
        super().__init__(config)
        self.c: Type[PortfolioCoverageTVPConfig] = config

    def get_portfolio_coverage(
        self,
        company_data: pd.DataFrame,
        portfolio_aggregation_method: PortfolioAggregationMethod,
    ) -> Optional[float]:
        """
        Get the TVP portfolio coverage (i.e. what part of the portfolio has a SBTi validated target).

        :param company_data: The company as it is returned from the data provider's get_company_data call.
        :param portfolio_aggregation_method: PortfolioAggregationMethod: The aggregation method to use
        :return: The aggregated score
        """
        company_data[self.c.OUTPUT_TARGET_STATUS] = company_data.apply(
            lambda row: 100 if row[self.c.COLS.SBTI_VALIDATED] else 0, axis=1
        )

        return self._calculate_aggregate_score(
            company_data, self.c.OUTPUT_TARGET_STATUS, portfolio_aggregation_method
        ).sum()

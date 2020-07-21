from abc import ABC
from enum import Enum
from typing import Type, Optional

import pandas as pd
from .configs import PortfolioAggregationConfig


class PortfolioAggregationMethod(Enum):
    """
    The portfolio aggregation method determines how the temperature scores for the individual companies are aggregated
    into a single portfolio score.
    """
    WATS = 1
    TETS = 2
    MOTS = 3
    EOTS = 4
    ECOTS = 5
    AOTS = 6
    ROTS = 7


class PortfolioAggregation(ABC):
    """
    This class is a base class that provides portfolio aggregation calculation.

    :param config: A class defining the constants that are used throughout this class. This parameter is only required
                    if you'd like to overwrite a constant. This can be done by extending the PortfolioAggregationConfig
                    class and overwriting one of the parameters.
    """

    def __init__(self, config: Type[PortfolioAggregationConfig] = PortfolioAggregationConfig):
        self.c = config

    def _calculate_aggregate_score(self, data: pd.DataFrame, input_column: str, output_column: str,
                                   portfolio_aggregation_method: Type[PortfolioAggregationMethod]) -> pd.Series:
        """
        Aggregate the scores in a given column based on a certain portfolio aggregation method.

        :param data: The data to run the calculations on
        :param input_column: The input column (containing the scores)
        :param output_column: The output column
        :param portfolio_aggregation_method: The method to use
        :return: The aggregates score
        """
        if portfolio_aggregation_method == PortfolioAggregationMethod.WATS:
            total_portfolio_weight = data[self.c.COLS.PORTFOLIO_WEIGHT].sum()
            data[output_column] = data.apply(
                lambda row: (row[self.c.COLS.PORTFOLIO_WEIGHT] * row[input_column]) / total_portfolio_weight, axis=1)

            # We're dividing by the portfolio weight. This is not done in the methodology, but we need it to account
            # for rounding errors.
            try:
                return data[output_column]
            except ZeroDivisionError:
                raise ValueError("The portfolio weight is not allowed to be zero")

        # Total emissions weighted temperature score (TETS)
        elif portfolio_aggregation_method == PortfolioAggregationMethod.TETS:
            # Calculate the total emissions of all companies
            emissions = data[self.c.COLS.GHG_SCOPE12].sum() + data[
                self.c.COLS.GHG_SCOPE3].sum()
            try:
                data[output_column] = data.apply(
                    lambda row: (row[self.c.COLS.GHG_SCOPE12] + row[self.c.COLS.GHG_SCOPE3]) / emissions * row[
                        input_column],
                    axis=1
                )
            except ZeroDivisionError:
                raise ValueError("The total emissions should be higher than zero")

            return data[output_column]
        # Market Owned emissions weighted temperature score (MOTS)
        # Enterprise Owned emissions weighted temperature score (EOTS)
        # Enterprise Value + Cash emissions weighted temperature score (ECOTS)
        # Total Assets emissions weighted temperature score (AOTS)
        # Revenue owned emissions weighted temperature score (ROTS)
        elif portfolio_aggregation_method == PortfolioAggregationMethod.MOTS or \
                portfolio_aggregation_method == PortfolioAggregationMethod.EOTS or \
                portfolio_aggregation_method == PortfolioAggregationMethod.ECOTS or \
                portfolio_aggregation_method == PortfolioAggregationMethod.AOTS or \
                portfolio_aggregation_method == PortfolioAggregationMethod.ROTS:
            # These four methods only differ in the way the company is valued.
            value_column = self.c.COLS.MARKET_CAP
            if portfolio_aggregation_method == PortfolioAggregationMethod.EOTS:
                value_column = self.c.COLS.COMPANY_ENTERPRISE_VALUE
            elif portfolio_aggregation_method == PortfolioAggregationMethod.ECOTS:
                value_column = self.c.COLS.COMPANY_EV_PLUS_CASH
            elif portfolio_aggregation_method == PortfolioAggregationMethod.AOTS:
                value_column = self.c.COLS.COMPANY_TOTAL_ASSETS
            elif portfolio_aggregation_method == PortfolioAggregationMethod.ROTS:
                value_column = self.c.COLS.COMPANY_REVENUE

            # Calculate the total owned emissions of all companies
            try:
                data[self.c.COLS.OWNED_EMISSIONS] = data.apply(
                    lambda row: (row[self.c.COLS.INVESTMENT_VALUE] / row[value_column]) * (
                            row[self.c.COLS.GHG_SCOPE12] + row[self.c.COLS.GHG_SCOPE3]),
                    axis=1
                )
            except ZeroDivisionError:
                raise ValueError("To calculate the aggregation, the {} column may not be zero".format(value_column))
            owned_emissions = data[self.c.COLS.OWNED_EMISSIONS].sum()

            try:
                # Calculate the MOTS value per company
                data[output_column] = data.apply(
                    lambda row: (row[self.c.COLS.OWNED_EMISSIONS] / owned_emissions) * row[input_column],
                    axis=1
                )
            except ZeroDivisionError:
                raise ValueError("The total owned emissions can not be zero")

            return data[output_column]
        else:
            raise ValueError("The specified portfolio aggregation method is invalid")

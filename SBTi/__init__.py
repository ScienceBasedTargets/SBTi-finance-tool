"""
This package helps companies and financial institutions to assess the temperature alignment of current
targets, commitments, and investment and lending portfolios, and to use this information to develop
targets for official validation by the SBTi.
"""
from typing import List, Optional, Tuple

import pandas as pd
from .portfolio_coverage_tvp import PortfolioCoverageTVP
from .target_validation import TargetValidation

from .temperature_score import Scenario, TemperatureScore
from .portfolio_aggregation import PortfolioAggregationMethod

from .data.data_provider import DataProvider
from .data import get_company_data, get_targets


def pipeline(data_providers: List[DataProvider],
             portfolio: pd.DataFrame,
             fallback_score: float,
             aggregation_method: PortfolioAggregationMethod,
             grouping: Optional[List[str]],
             scenario: Optional[Scenario],
             anonymize: bool) -> Tuple[pd.DataFrame, dict, Optional[float], Optional[dict]]:
    """
    This pipeline is a helper that runs through all of the possible steps in the SBTi module and returns the result of each of these steps.

    :param data_providers: A list of data providers that should be used
    :param portfolio: A portfolio represented as a data frame
    :param fallback_score: The fallback score to use while calculating the temperature score
    :param aggregation_method: The aggregation method to use
    :param grouping: The names of the columns to group on
    :param scenario: The scenario to play
    :param anonymize: Whether to anonymize the resulting data set or not
    :return: The scores, the aggregations, the coverage and the column distribution
    """
    company_data = get_company_data(data_providers, portfolio["company_id"].tolist())
    target_data = get_targets(data_providers, portfolio["company_id"].tolist())
    company_data = pd.merge(left=company_data, right=portfolio.drop("company_name", axis=1), how="left",
                            on=["company_id"])
    if len(company_data) == 0:
        raise ValueError("None of the companies in your portfolio could be found by the data providers")

    ts = TemperatureScore(fallback_score=fallback_score, scenario=scenario, grouping=grouping,
                          aggregation_method=aggregation_method)

    portfolio_data = TargetValidation(target_data, company_data).target_validation()
    scores = ts.calculate(portfolio_data)
    aggregations = ts.aggregate_scores(scores)
    coverage = PortfolioCoverageTVP().get_portfolio_coverage(portfolio_data, aggregation_method)

    column_distribution = None
    if grouping:
        column_distribution = ts.columns_percentage_distribution(portfolio_data, grouping)

    if anonymize:
        scores = ts.anonymize_data_dump(scores)

    return scores, aggregations, coverage, column_distribution

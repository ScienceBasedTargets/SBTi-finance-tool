from typing import List, Optional, Tuple

import pandas as pd
from .interfaces import PortfolioCompany, EScope, ETimeFrames, ScoreAggregations
from .target_validation import TargetValidation

from .temperature_score import Scenario, TemperatureScore
from .portfolio_aggregation import PortfolioAggregationMethod

from .data.data_provider import DataProvider
from .data import get_company_data, get_targets


def _flatten_user_fields(record: PortfolioCompany):
    """
    Flatten the user fields in a portfolio company and return it as a dictionary.

    :param record: The record to flatten
    :return:
    """
    record_dict = record.dict(exclude_none=True)
    if record.user_fields is not None:
        for key, value in record_dict["user_fields"].items():
            record_dict[key] = value
        del record_dict["user_fields"]

    return record_dict


def get_data(data_providers: List[DataProvider], portfolio: List[PortfolioCompany]) -> pd.DataFrame:
    """
    Get the required data from the data provider(s), validate the targets and return a 9-box grid for each company.

    :param data_providers: A list of DataProvider instances
    :param portfolio: A list of PortfolioCompany models
    :return: A data frame containing the relevant company-target data
    """
    df_portfolio = pd.DataFrame.from_records([_flatten_user_fields(c) for c in portfolio])
    company_data = get_company_data(data_providers, df_portfolio["company_id"].tolist())
    target_data = get_targets(data_providers, df_portfolio["company_id"].tolist())

    # Prepare the data
    portfolio_data = TargetValidation(target_data, company_data).target_validation()
    portfolio_data = pd.merge(left=portfolio_data, right=df_portfolio.drop("company_name", axis=1), how="left",
                              on=["company_id"])

    if len(company_data) == 0:
        raise ValueError("None of the companies in your portfolio could be found by the data providers")

    return portfolio_data


def calculate(portfolio_data: pd.DataFrame, fallback_score: float, aggregation_method: PortfolioAggregationMethod,
              grouping: Optional[List[str]], scenario: Optional[Scenario], time_frames: List[ETimeFrames],
              scopes: List[EScope], anonymize: bool, aggregate: bool = True) -> Tuple[pd.DataFrame,
                                                                                      Optional[ScoreAggregations]]:
    """
    Calculate the different parts of the temperature score (actual scores, aggregations, column distribution).

    :param portfolio_data: The portfolio data, already processed by the target validation module
    :param fallback_score: The fallback score to use while calculating the temperature score
    :param aggregation_method: The aggregation method to use
    :param time_frames: The time frames that the temperature scores should be calculated for  (None to calculate all)
    :param scopes: The scopes that the temperature scores should be calculated for (None to calculate all)
    :param grouping: The names of the columns to group on
    :param scenario: The scenario to play
    :param anonymize: Whether to anonymize the resulting data set or not
    :param aggregate: Whether to aggregate the scores or not
    :return: The scores, the aggregations and the column distribution (if a
    """
    ts = TemperatureScore(time_frames=time_frames, scopes=scopes, fallback_score=fallback_score, scenario=scenario,
                          grouping=grouping, aggregation_method=aggregation_method)

    scores = ts.calculate(portfolio_data)
    aggregations = None
    if aggregate:
        aggregations = ts.aggregate_scores(scores)

    if anonymize:
        scores = ts.anonymize_data_dump(scores)

    return scores, aggregations

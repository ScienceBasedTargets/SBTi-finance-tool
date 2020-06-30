from typing import Optional, Tuple
from enum import Enum
import pandas as pd
import numpy as np

from SBTi.portfolio_aggregation import PortfolioAggregation, PortfolioAggregationMethod
from .configs import TemperatureScoreConfig


class BoundaryCoverageOption(Enum):
    """
    The boundary coverage determines how partial targets are processed.
    * DEFAULT: Target is always valid, % uncovered is given default score in temperature score module.
    * THRESHOLD: For S1+S2 targets: coverage% must be above 95%, for S3 targets coverage must be above 67%.
    * WEIGHTED: Thresholds are still 95% and 67%, target is always valid. Below threshold ambition is scaled.*
        New target ambition = input target ambition * coverage
    """
    DEFAULT = 3
    THRESHOLD = 1
    WEIGHTED = 2


class TemperatureScore(PortfolioAggregation):
    """
    This class is provides a temperature score based on the climate goals.

    :param fallback_score: The temp score if a company is not found
    :param model: The regression model to use
    :param boundary_coverage_option: The technique the boundary coverage is calculated
    :param config: A class defining the constants that are used throughout this class. This parameter is only required
                    if you'd like to overwrite a constant. This can be done by extending the TemperatureScoreConfig
                    class and overwriting one of the parameters.
    """

    def __init__(self, fallback_score: float = 3.2, model: int = 4,
                 boundary_coverage_option: BoundaryCoverageOption = BoundaryCoverageOption.DEFAULT,
                 config: TemperatureScoreConfig = TemperatureScoreConfig):
        super().__init__(config)
        self.fallback_score = fallback_score
        self.model = model
        self.boundary_coverage_option = boundary_coverage_option
        self.c = config

        # Load the mappings from industry to SR15 goal
        self.mapping = pd.read_excel(self.c.FILE_SR15_MAPPING, header=0)
        self.regression_model = pd.read_excel(self.c.FILE_REGRESSION_MODEL_SUMMARY, header=0)

    def get_target_mapping(self, target: pd.Series) -> Optional[str]:
        """
        Map the target onto an SR15 target (None if not available).

        :param target: The target as a row of a dataframe
        :return: The mapped SR15 target
        """

        # Check if the industry exists, if not use a default
        industry = target[self.c.COLS.INDUSTRY] \
            if target[self.c.COLS.INDUSTRY] in self.mapping[self.c.COLS.INDUSTRY] \
            else self.c.DEFAULT_INDUSTRY

        # Map the target reference numbers (Int 1, Abs 1, etc. to target types (Intensity or Absolute)
        target_type = self.c.VALUE_TARGET_REFERENCE_INTENSITY \
            if type(target[self.c.COLS.TARGET_REFERENCE_NUMBER]) == str and \
               target[self.c.COLS.TARGET_REFERENCE_NUMBER].strip().startswith(
                   self.c.VALUE_TARGET_REFERENCE_INTENSITY_BASE) \
            else self.c.VALUE_TARGET_REFERENCE_ABSOLUTE

        mappings = self.mapping[(self.mapping[self.c.COLS.INDUSTRY] == industry) &
                                (self.mapping[self.c.COLS.TARGET_TYPE] == target_type) &
                                (self.mapping[self.c.COLS.SCOPE] == target[self.c.COLS.SCOPE_CATEGORY])]

        if len(mappings) == 0:
            return None
        elif len(mappings) > 1:
            # There should never be more than one potential mapping
            raise ValueError("There is more than one potential mapping to a SR15 goal.")
        else:
            return mappings.iloc[0][self.c.COLS.SR15]

    def get_annual_reduction_rate(self, target: pd.Series) -> Optional[float]:
        """
        Get the annual reduction rate (or None if not available).

        :param target: The target as a row of a dataframe
        :return: The annual reduction
        """
        if np.isnan(target[self.c.COLS.REDUCTION_FROM_BASE_YEAR]):
            return None

        try:
            return target[self.c.COLS.REDUCTION_FROM_BASE_YEAR] / float(target[self.c.COLS.TARGET_YEAR] -
                                                                        target[self.c.COLS.START_YEAR])
        except ZeroDivisionError:
            raise ValueError("Couldn't calculate the annual reduction rate because the start and target year are the "
                             "same")

    def get_regression(self, target: pd.Series) -> Tuple[Optional[float], Optional[float]]:
        """
        Get the regression parameter and intercept from the model's output.

        :param target: The target as a row of a dataframe
        :return:The regression parameter and intercept
        """
        if target[self.c.COLS.SR15] is None:
            return None, None

        regression = self.regression_model[
            (self.regression_model[self.c.COLS.VARIABLE] == target[self.c.COLS.SR15]) &
            (self.regression_model[self.c.COLS.SLOPE] == self.c.SLOPE_MAP[target[self.c.COLS.TIME_FRAME]]) &
            (self.regression_model[self.c.COLS.MODEL] == self.model)]
        if len(regression) == 0:
            return None, None
        elif len(regression) > 1:
            # There should never be more than one potential mapping
            raise ValueError("There is more than one potential regression parameter for this SR15 goal.")
        else:
            return regression.iloc[0][self.c.COLS.PARAM], regression.iloc[0][self.c.COLS.INTERCEPT]


    def get_score(self, target: pd.Series) -> float:
        """
        Get the temperature score for a certain target based on the annual reduction rate and the regression parameters.

        :param target: The target as a row of a dataframe
        :return: The temperature score
        """
        if np.isnan(target[self.c.COLS.REGRESSION_PARAM]) or np.isnan(target[self.c.COLS.REGRESSION_INTERCEPT]) \
                or np.isnan(target[self.c.COLS.ANNUAL_REDUCTION_RATE]):
            return self.fallback_score
        return target[self.c.COLS.REGRESSION_PARAM] * target[self.c.COLS.ANNUAL_REDUCTION_RATE] + target[
            self.c.COLS.REGRESSION_INTERCEPT]

    def process_score(self, target: pd.Series) -> float:
        """
        Process the temperature score, such that it's relative to the emissions in the scope.

        :param target: The target as a row of a dataframe
        :return: The relative temperature score
        """
        if self.boundary_coverage_option == BoundaryCoverageOption.DEFAULT:
            if np.isnan(target[self.c.COLS.EMISSIONS_IN_SCOPE]) or np.isnan(target[self.c.COLS.TEMPERATURE_SCORE]):
                return self.fallback_score
            else:
                try:
                    return target[self.c.COLS.EMISSIONS_IN_SCOPE] / 100 * target[self.c.COLS.TEMPERATURE_SCORE] + \
                           (1 - (target[self.c.COLS.EMISSIONS_IN_SCOPE] / 100)) * self.fallback_score
                except ZeroDivisionError:
                    raise ValueError(
                        "The temperature score for company {} is zero".format(target[self.c.COLS.COMPANY_NAME]))
        else:
            return target[self.c.COLS.TEMPERATURE_SCORE]

    def get_ghc_temperature_score(self, data: pd.DataFrame, company: str, time_frame: str):
        """
        Get the aggregated temperature score for a certain company based on the emissions of company.

        :param data:
        :param company: The company name
        :param time_frame: The time_frame (short, mid, long)
        :return: The aggregated temperature score for a company
        """
        filtered_data = data[(data[self.c.COLS.COMPANY_NAME] == company) & (data[self.c.COLS.TIME_FRAME] == time_frame)]
        s1s2 = filtered_data[filtered_data[self.c.COLS.SCOPE_CATEGORY] == self.c.VALUE_SCOPE_CATEGORY_S1S2]
        s3 = filtered_data[filtered_data[self.c.COLS.SCOPE_CATEGORY] == self.c.VALUE_SCOPE_CATEGORY_S3]
        try:
            return (s1s2[self.c.COLS.TEMPERATURE_SCORE].mean() * s1s2[self.c.COLS.S1S2_EMISSIONS].mean() +
                    s3[self.c.COLS.TEMPERATURE_SCORE].mean() * s3[self.c.COLS.S3_EMISSIONS].mean()) / \
                   (s1s2[self.c.COLS.S1S2_EMISSIONS].mean() + s3[self.c.COLS.S3_EMISSIONS].mean())
        except ZeroDivisionError:
            raise ValueError("The mean of the S1+S2 plus the S3 emissions is zero")

    def calculate(self, data: pd.DataFrame):
        """
        Calculate the temperature for a dataframe of company data.
        Required columns:
        * target_reference_number: Int *x* of Abs *x*
        * scope: The scope of the target. This should be a valid scope in the SR15 mapping
        * scope_category: The scope category, options: "s1s2", "s3", "s1s2s3"
        * base_year: The base year of the target
        * start_year: The start year of the target
        * target_year: The year when the target should be achieved
        * time_frame: The time frame of the target (short, mid, long) -> This field is calculated by the target
            valuation protocol.
        * reduction_from_base_year: Targeted reduction in emissions from the base year
        * emissions_in_scope: Company emissions in the target's scope at start of the base year
        * achieved_reduction: The emission reduction that has already been achieved
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

        :param data:
        :return: A data frame containing all relevant information for the targets and companies
        """
        data[self.c.COLS.SR15] = data.apply(lambda row: self.get_target_mapping(row), axis=1)
        data[self.c.COLS.ANNUAL_REDUCTION_RATE] = data.apply(lambda row: self.get_annual_reduction_rate(row), axis=1)
        data[self.c.COLS.REGRESSION_PARAM], data[self.c.COLS.REGRESSION_INTERCEPT] = zip(
            *data.apply(lambda row: self.get_regression(row), axis=1)
        )
        data[self.c.COLS.TEMPERATURE_SCORE] = data.apply(lambda row: self.get_score(row), axis=1)
        data[self.c.COLS.TEMPERATURE_SCORE] = data.apply(lambda row: self.process_score(row), axis=1)

        combined_data = []
        company_columns = [column for column in self.c.COLS.COMPANY_COLUMNS if column in data.columns]
        for company in data[self.c.COLS.COMPANY_NAME].unique():
            for time_frame in self.c.VALUE_TIME_FRAMES:
                # We always include all company specific data
                company_data = {column: data[data[self.c.COLS.COMPANY_NAME] == company][column].mode().iloc[0]
                                for column in company_columns}
                company_data[self.c.COLS.COMPANY_NAME] = company
                company_data[self.c.COLS.SCOPE] = self.c.VALUE_SCOPE_S1S2S3
                company_data[self.c.COLS.SCOPE_CATEGORY] = self.c.VALUE_SCOPE_CATEGORY_S1S2S3
                company_data[self.c.COLS.TIME_FRAME] = time_frame
                company_data[self.c.COLS.TEMPERATURE_SCORE] = self.get_ghc_temperature_score(data, company, time_frame)
                combined_data.append(company_data)

        return pd.concat([data, pd.DataFrame(combined_data)])

    def aggregate_scores(self, data: pd.DataFrame, portfolio_aggregation_method: PortfolioAggregationMethod):
        """
        Aggregate scores to create a portfolio score per time_frame (short, mid, long).

        :param data: The results of the calculate method
        :param portfolio_aggregation_method: PortfolioAggregationMethod: The aggregation method to use
        :return: A weighted temperature score for the portfolio
        """
        portfolio_scores = {}
        for time_frame in self.c.VALUE_TIME_FRAMES:
            # Weighted average temperature score (WATS)
            filtered_data = data[(data[self.c.COLS.TIME_FRAME] == time_frame) & (
                    data[self.c.COLS.SCOPE_CATEGORY] == self.c.VALUE_SCOPE_CATEGORY_S1S2S3)].copy()

            portfolio_scores[time_frame] = self._calculate_aggregate_score(filtered_data, self.c.COLS.TEMPERATURE_SCORE,
                                                                           self.c.COLS.WEIGHTED_TEMPERATURE_SCORE,
                                                                           portfolio_aggregation_method)

        return portfolio_scores

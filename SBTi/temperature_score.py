from typing import Optional, Tuple
from enum import Enum
import pandas as pd
import numpy as np
import os


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


class TemperatureScore:
    """
    This class is provides a temperature score based on the climate goals.

    :param fallback_score: The temp score if a company is not found
    :param model: The regression model to use
    :param boundary_coverage_option: The technique the boundary coverage is calculated
    """

    def __init__(self, fallback_score: float = 3.2, model: int = 4,
                 boundary_coverage_option: BoundaryCoverageOption = BoundaryCoverageOption.DEFAULT):
        self.fallback_score = fallback_score
        self.model = model
        self.boundary_coverage_option = boundary_coverage_option

        # Load the mappings from industry to SR15 goal
        self.mapping = pd.read_excel(os.path.join(os.path.dirname(os.path.realpath(__file__)), "inputs",
                                                  "sr15_mapping.xlsx"), header=0)
        self.regression_model = pd.read_excel(os.path.join(os.path.dirname(os.path.realpath(__file__)), "inputs",
                                                           "regression_model_summary.xlsx"), header=0)

        # This defines which column contain company specific, instead of target specific data
        self.company_columns = ["industry", "regression_param", "regression_intercept", "s1s2_emissions",
                                "s3_emissions", "market_cap", "investment_value", "portfolio_weight",
                                "company_enterprise_value", "company_ev_plus_cash", "company_total_assets"]
        self.slope_map = {
            "short": "slope5",
            "mid": "slope15",
            "long": "slope30",
        }

    def get_target_mapping(self, target: pd.Series) -> Optional[str]:
        """
        Map the target onto an SR15 target (None if not available).

        :param target: The target as a row of a dataframe
        :return:
        """
        industry = target["industry"] if target["industry"] in self.mapping["industry"] else "Others"
        target_type = "Intensity" \
            if type(target["target_reference_number"]) == str and \
               target["target_reference_number"].strip().startswith("Int") \
            else "Absolute"

        mappings = self.mapping[(self.mapping["industry"] == industry) &
                                (self.mapping["target_type"] == target_type) &
                                (self.mapping["scope"] == target["scope_category"])]
        if len(mappings) == 0:
            return None
        elif len(mappings) > 1:
            # There should never be more than one potential mapping
            raise ValueError("There is more than one potential mapping to a SR15 goal.")
        else:
            return mappings.iloc[0]["SR15"]

    def get_annual_reduction_rate(self, target: pd.Series) -> Optional[float]:
        """
        Get the annual reduction rate (or None if not available).

        :param target: The target as a row of a dataframe
        :return:
        """
        if np.isnan(target["reduction_from_base_year"]):
            return None

        return target["reduction_from_base_year"] / float(target["target_year"] - target["start_year"])

    def get_regression(self, target: pd.Series) -> Tuple[Optional[float], Optional[float]]:
        """
        Get the regression parameter and intercept from the model's output.

        :param target: The target as a row of a dataframe
        :return:
        """
        if target["SR15"] is None:
            return None, None

        regression = self.regression_model[(self.regression_model["variable"] == target["SR15"]) &
                                           (self.regression_model["slope"] == self.slope_map[target["time_frame"]]) &
                                           (self.regression_model["model"] == self.model)]
        if len(regression) == 0:
            return None, None
        elif len(regression) > 1:
            # There should never be more than one potential mapping
            raise ValueError("There is more than one potential regression parameter for this SR15 goal.")
        else:
            return regression.iloc[0]["param"], regression.iloc[0]["intercept"]

    def get_score(self, target) -> float:
        """
        Get the temperature score for a certain target based on the annual reduction rate and the regression parameters.

        :param target: The target as a row of a dataframe
        :return:
        """
        if np.isnan(target["regression_param"]) or np.isnan(target["regression_intercept"]) or \
                np.isnan(target["annual_reduction_rate"]):
            return self.fallback_score
        return target["regression_param"] * target["annual_reduction_rate"] + target["regression_intercept"]

    def process_score(self, target: pd.Series) -> float:
        """
        Process the temperature score, such that it's relative to the emissions in the scope.

        :param target: The target as a row of a dataframe
        :return:
        """
        if self.boundary_coverage_option == BoundaryCoverageOption.DEFAULT:
            if np.isnan(target["emissions_in_scope"]) or np.isnan(target["temperature_score"]):
                return self.fallback_score
            else:
                return target["emissions_in_scope"] / 100 * target["temperature_score"] + \
                       (1 - (target["emissions_in_scope"] / 100)) * self.fallback_score
        else:
            return target["temperature_score"]

    def get_ghc_temperature_score(self, data: pd.DataFrame, company: str, time_frame: str):
        """
        Get the aggregated temperature score for a certain company based on the emissions of company.

        :param data:
        :param company: The company name
        :param time_frame: The time_frame (short, mid, long)
        :return:
        """
        filtered_data = data[(data["company_name"] == company) & (data["time_frame"] == time_frame)]
        s1s2 = filtered_data[filtered_data["scope_category"] == "s1s2"]
        s3 = filtered_data[filtered_data["scope_category"] == "s3"]
        return (s1s2["temperature_score"].mean() * s1s2["s1s2_emissions"].mean() +
                s3["temperature_score"].mean() * s3["s3_emissions"].mean()) / \
               (s1s2["s1s2_emissions"].mean() + s3["s3_emissions"].mean())

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
            it will be converted to "Others"
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
        :return:
        """
        data["SR15"] = data.apply(lambda row: self.get_target_mapping(row), axis=1)
        data["annual_reduction_rate"] = data.apply(lambda row: self.get_annual_reduction_rate(row), axis=1)
        data["regression_param"], data["regression_intercept"] = zip(
            *data.apply(lambda row: self.get_regression(row), axis=1)
        )
        data["temperature_score"] = data.apply(lambda row: self.get_score(row), axis=1)
        data["temperature_score"] = data.apply(lambda row: self.process_score(row), axis=1)

        combined_data = []
        company_columns = [column for column in self.company_columns if column in data.columns]
        for company in data["company_name"].unique():
            for time_frame in ["short", "mid", "long"]:
                # We always include all company specific data
                company_data = {column: data[data["company_name"] == company][column].mode().iloc[0]
                                for column in company_columns}
                company_data["company_name"] = company
                company_data["scope"] = "scope 1+2+3"
                company_data["scope_category"] = "s1s2s3"
                company_data["time_frame"] = time_frame
                company_data["temperature_score"] = self.get_ghc_temperature_score(data, company, time_frame)
                combined_data.append(company_data)

        return pd.concat([data, pd.DataFrame(combined_data)])

    def aggregate_scores(self, data: pd.DataFrame, portfolio_aggregation_method: PortfolioAggregationMethod):
        """
        Aggregate scores to create a portfolio score per time_frame (short, mid, long).

        :param data: The results of the calculate method
        :type portfolio_aggregation_method: PortfolioAggregationMethod: The aggregation method to use
        :return:
        """
        portfolio_scores = {}
        for time_frame in ["short", "mid", "long"]:
            # Weighted average temperature score (WATS)
            filtered_data = data[(data["time_frame"] == time_frame) & (data["scope_category"] == "s1s2s3")].copy()
            if portfolio_aggregation_method == PortfolioAggregationMethod.WATS:
                filtered_data["weighted_temperature_score"] = filtered_data.apply(
                    lambda row: row["portfolio_weight"] * row["temperature_score"],
                    axis=1
                )

                # We're dividing by the portfolio weight. This is not done in the methodology, but we need it to account
                # for rounding errors.
                portfolio_scores[time_frame] = filtered_data["weighted_temperature_score"].sum() / \
                                               filtered_data["portfolio_weight"].sum()
            # Total emissions weighted temperature score (TETS)
            elif portfolio_aggregation_method == PortfolioAggregationMethod.TETS:
                # Calculate the total emissions of all companies
                emissions = filtered_data["s1s2_emissions"].sum() + filtered_data["s3_emissions"].sum()
                filtered_data["weighted_temperature_score"] = filtered_data.apply(
                    lambda row: (row["s1s2_emissions"] + row["s3_emissions"]) / emissions * row["temperature_score"],
                    axis=1
                )
                portfolio_scores[time_frame] = filtered_data["weighted_temperature_score"].sum()
            # Market Owned emissions weighted temperature score (MOTS)
            # Enterprise Owned emissions weighted temperature score (EOTS)
            # Enterprise Value + Cash emissions weighted temperature score (ECOTS)
            # Total Assets emissions weighted temperature score (AOTS)
            elif portfolio_aggregation_method == PortfolioAggregationMethod.MOTS or \
                    portfolio_aggregation_method == PortfolioAggregationMethod.EOTS or \
                    portfolio_aggregation_method == PortfolioAggregationMethod.ECOTS or \
                    portfolio_aggregation_method == PortfolioAggregationMethod.AOTS:
                # These four methods only differ in the way the company is valued.
                value_column = "market_cap"
                if portfolio_aggregation_method == PortfolioAggregationMethod.EOTS:
                    value_column = "company_enterprise_value"
                elif portfolio_aggregation_method == PortfolioAggregationMethod.ECOTS:
                    value_column = "company_ev_plus_cash"
                elif portfolio_aggregation_method == PortfolioAggregationMethod.AOTS:
                    value_column = "company_total_assets"

                # Calculate the total owned emissions of all companies
                filtered_data["owned_emissions"] = filtered_data.apply(
                    lambda row: ((row["investment_value"] / row[value_column]) * (
                            row["s1s2_emissions"] + row["s3_emissions"])),
                    axis=1
                )
                owned_emissions = filtered_data["owned_emissions"].sum()

                # Calculate the MOTS value per company
                filtered_data["weighted_temperature_score"] = filtered_data.apply(
                    lambda row: (row["owned_emissions"] / owned_emissions) * row["temperature_score"],
                    axis=1
                )

                portfolio_scores[time_frame] = filtered_data["weighted_temperature_score"].sum()
            else:
                raise ValueError("The specified portfolio aggregation method is invalid")
        return portfolio_scores

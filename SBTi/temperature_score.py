from enum import Enum
from typing import Optional, Tuple, Type, List

import pandas as pd
import numpy as np
import datetime

from .interfaces import (
    ScenarioInterface,
    EScope,
    ETimeFrames,
    Aggregation,
    AggregationContribution,
    ScoreAggregation,
    ScoreAggregationScopes,
    ScoreAggregations,
    PortfolioCompany,
)
from .portfolio_aggregation import PortfolioAggregation, PortfolioAggregationMethod
from .configs import TemperatureScoreConfig
from . import data, utils


class ScenarioType(Enum):
    """
    A scenario defines which scenario should be run.
    """

    TARGETS = 1
    APPROVED_TARGETS = 2
    HIGHEST_CONTRIBUTORS = 3
    HIGHEST_CONTRIBUTORS_APPROVED = 4

    @staticmethod
    def from_int(value) -> Optional["ScenarioType"]:
        value_map = {
            1: ScenarioType.TARGETS,
            2: ScenarioType.APPROVED_TARGETS,
            3: ScenarioType.HIGHEST_CONTRIBUTORS,
            4: ScenarioType.HIGHEST_CONTRIBUTORS_APPROVED,
        }
        return value_map.get(value, None)


class EngagementType(Enum):
    """
    An engagement type defines how the companies will be engaged.
    """

    SET_TARGETS = 1
    SET_SBTI_TARGETS = 2

    @staticmethod
    def from_int(value) -> "EngagementType":
        """
        Convert an integer to an engagement type.

        :param value: The value to convert
        :return:
        """
        value_map = {
            0: EngagementType.SET_TARGETS,
            1: EngagementType.SET_SBTI_TARGETS,
        }
        return value_map.get(value, EngagementType.SET_TARGETS)

    @staticmethod
    def from_string(value: Optional[str]) -> "EngagementType":
        """
        Convert a string to an engagement type.

        :param value: The value to convert
        :return:
        """
        if value is None:
            return EngagementType.SET_TARGETS

        value_map = {
            "SET_TARGETS": EngagementType.SET_TARGETS,
            "SET_SBTI_TARGETS": EngagementType.SET_SBTI_TARGETS,
        }
        return value_map.get(value.upper(), EngagementType.SET_TARGETS)


class Scenario:
    """
    A scenario defines the action the portfolio holder will take to improve its temperature score.
    """

    scenario_type: Optional[ScenarioType]
    engagement_type: EngagementType

    def get_score_cap(self) -> float:
        if self.engagement_type == EngagementType.SET_TARGETS:
            return 2.0
        elif (
            self.scenario_type == ScenarioType.APPROVED_TARGETS
            or self.engagement_type == EngagementType.SET_SBTI_TARGETS
        ):
            return 1.75
        else:
            return np.NaN

    def get_fallback_score(self, fallback_score: float) -> float:
        if self.scenario_type == ScenarioType.TARGETS:
            return 2.0
        else:
            return fallback_score

    @staticmethod
    def from_dict(scenario_values: dict) -> Optional["Scenario"]:
        """
        Convert a dictionary to a scenario. The dictionary should have the following keys:

        * number: The scenario type as an integer
        * engagement_type: The engagement type as a string

        :param scenario_values: The dictionary to convert
        :return: A scenario object matching the input values or None, if no scenario could be matched
        """
        scenario = Scenario()
        scenario.scenario_type = ScenarioType.from_int(
            scenario_values.get("number", -1)
        )
        scenario.engagement_type = EngagementType.from_string(
            scenario_values.get("engagement_type", "")
        )

        if scenario.scenario_type is not None:
            return scenario
        else:
            return None

    @staticmethod
    def from_interface(
        scenario_values: Optional[ScenarioInterface],
    ) -> Optional["Scenario"]:
        """
        Convert a scenario interface to a scenario.

        :param scenario_values: The interface model instance to convert
        :return: A scenario object matching the input values or None, if no scenario could be matched
        """
        if scenario_values is None:
            return None

        scenario = Scenario()
        scenario.scenario_type = ScenarioType.from_int(scenario_values.number)
        scenario.engagement_type = EngagementType.from_string(
            scenario_values.engagement_type
        )

        if scenario.scenario_type is not None:
            return scenario
        else:
            return None


class TemperatureScore(PortfolioAggregation):
    """
    This class provides a temperature score based on the climate goals.

    :param fallback_score: The temp score if a company is not found
    :param model: The regression model to use
    :param config: A class defining the constants that are used throughout this class. This parameter is only required
                    if you'd like to overwrite a constant. This can be done by extending the TemperatureScoreConfig
                    class and overwriting one of the parameters.
    """

    def __init__(
        self,
        time_frames: List[ETimeFrames],
        scopes: List[EScope],
        fallback_score: float = 3.2,
        model: int = 4,
        scenario: Optional[Scenario] = None,
        aggregation_method: PortfolioAggregationMethod = PortfolioAggregationMethod.WATS,
        grouping: Optional[List] = None,
        config: Type[TemperatureScoreConfig] = TemperatureScoreConfig,
    ):
        super().__init__(config)
        self.model = model
        self.c: Type[TemperatureScoreConfig] = config
        self.scenario: Optional[Scenario] = scenario
        self.fallback_score = fallback_score

        self.time_frames = time_frames
        self.scopes = scopes

        if self.scenario is not None:
            self.fallback_score = self.scenario.get_fallback_score(self.fallback_score)

        self.aggregation_method: PortfolioAggregationMethod = aggregation_method
        self.grouping: list = []
        if grouping is not None:
            self.grouping = grouping

        # Load the mappings from industry to SR15 goal
        self.mapping = pd.read_excel(self.c.FILE_SR15_MAPPING, header=0)
        self.regression_model = pd.read_excel(
            self.c.FILE_REGRESSION_MODEL_SUMMARY, header=0
        )
        self.regression_model = self.regression_model[
            self.regression_model[self.c.COLS.MODEL] == self.model
        ]

    def get_target_mapping(self, target: pd.Series) -> Optional[str]:
        """
        Map the target onto an SR15 target (None if not available).

        :param target: The target as a row of a dataframe
        :return: The mapped SR15 target
        """
        if (
            target[self.c.COLS.TARGET_REFERENCE_NUMBER]
            .strip()
            .lower()
            .startswith(self.c.VALUE_TARGET_REFERENCE_INTENSITY_BASE)
        ):
            return self.c.INTENSITY_MAPPINGS.get(
                (target[self.c.COLS.INTENSITY_METRIC], target[self.c.COLS.SCOPE]), None
            )
        else:
            # Only first 3 characters of ISIC code are relevant for the absolute mappings
            return self.c.ABSOLUTE_MAPPINGS.get(
                (target[self.c.COLS.COMPANY_ISIC][:3], target[self.c.COLS.SCOPE]),
                self.c.ABSOLUTE_MAPPINGS.get(("other", target[self.c.COLS.SCOPE])),
            )

    def get_annual_reduction_rate(self, target: pd.Series) -> Optional[float]:
        """
        Get the annual reduction rate (or None if not available).

        :param target: The target as a row of a dataframe
        :return: The annual reduction
        """

        # 2022-09-01 Bloomberg pointed out need for additional checks in input
        # Here is the original code:
        # if pd.isnull(target[self.c.COLS.REDUCTION_AMBITION]):
        #     return None

        # try:
        #     return target[self.c.COLS.REDUCTION_AMBITION] / float(
        #         target[self.c.COLS.END_YEAR] - target[self.c.COLS.BASE_YEAR]
        #     )
        # except ZeroDivisionError:
        #     raise ValueError(
        #         "Couldn't calculate the annual reduction rate because the start and target year are the "
        #         "same"
        #     )

        # Bloombergs proposal - changed 2022-09-01
        check = pd.isnull(target[self.c.COLS.REDUCTION_AMBITION])
        check = check or pd.isnull(target[self.c.COLS.END_YEAR])
        check = check or pd.isnull(target[self.c.COLS.BASE_YEAR])
        check = check or (target[self.c.COLS.END_YEAR] <= target[self.c.COLS.BASE_YEAR])
        # add check that target is not too old - moved to target_validation Nov22
        # check = check or (target[self.c.COLS.END_YEAR] < datetime.datetime.now().year)
        if check:
            return None
        return target[self.c.COLS.REDUCTION_AMBITION] / float(
            target[self.c.COLS.END_YEAR] - target[self.c.COLS.BASE_YEAR]
        )
        # End of BBGs code

    def get_regression(
        self, target: pd.Series
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Get the regression parameter and intercept from the model's output.

        :param target: The target as a row of a dataframe
        :return: The regression parameter and intercept
        """
        if pd.isnull(target[self.c.COLS.SR15]):
            return None, None

        regression = self.regression_model[
            (self.regression_model[self.c.COLS.VARIABLE] == target[self.c.COLS.SR15])
            & (
                self.regression_model[self.c.COLS.SLOPE]
                == self.c.SLOPE_MAP[target[self.c.COLS.TIME_FRAME]]
            )
        ]
        if len(regression) == 0:
            return None, None
        elif len(regression) > 1:
            # There should never be more than one potential mapping
            raise ValueError(
                "There is more than one potential regression parameter for this SR15 goal."
            )
        else:
            return (
                regression.iloc[0][self.c.COLS.PARAM],
                regression.iloc[0][self.c.COLS.INTERCEPT],
            )

    def _merge_regression(self, data: pd.DataFrame):
        """
        Merge the data with the regression parameters from the SBTi model.

        :param data: The data to merge
        :return: The data set, amended with the regression parameters
        """
        data[self.c.COLS.SLOPE] = data.apply(
            lambda row: self.c.SLOPE_MAP.get(row[self.c.COLS.TIME_FRAME], None), axis=1
        )
        return pd.merge(
            left=data,
            right=self.regression_model,
            left_on=[self.c.COLS.SLOPE, self.c.COLS.SR15],
            right_on=[self.c.COLS.SLOPE, self.c.COLS.VARIABLE],
            how="left",
        )

    def get_score(self, target: pd.Series) -> Tuple[float, float]:
        """
        Get the temperature score for a certain target based on the annual reduction rate and the regression parameters.

        :param target: The target as a row of a data frame
        :return: The temperature score
        """
        if (
            pd.isnull(target[self.c.COLS.REGRESSION_PARAM])
            or pd.isnull(target[self.c.COLS.REGRESSION_INTERCEPT])
            or pd.isnull(target[self.c.COLS.ANNUAL_REDUCTION_RATE])
        ):
            return self.fallback_score, 1

        ts = max(
            target[self.c.COLS.REGRESSION_PARAM]
            * target[self.c.COLS.ANNUAL_REDUCTION_RATE]
            * 100
            + target[self.c.COLS.REGRESSION_INTERCEPT],
            self.c.TEMPERATURE_FLOOR,
        )
        if target[self.c.COLS.SBTI_VALIDATED]:
            return ts, 0
        else:
            return (
                ts * self.c.SBTI_FACTOR
                + self.fallback_score * (1 - self.c.SBTI_FACTOR),
                0,
            )

    def get_ghc_temperature_score(
        self, row: pd.Series, company_data: pd.DataFrame
    ) -> Tuple[float, float, list]:
        """
        Get the aggregated temperature score and a temperature result, which indicates how much of the score is based on
        the default score for a certain company based on the emissions of company.

        :param company_data: The original data, grouped by company, time frame and scope category
        :param row: The row to calculate the temperature score for (if the scope of the row isn't s1s2s3, it will return
        the original score
        :return: The aggregated temperature score for a company and any target_ids associated
        """
        if row[self.c.COLS.SCOPE] != EScope.S1S2S3:
            return (
                row[self.c.COLS.TEMPERATURE_SCORE],
                row[self.c.TEMPERATURE_RESULTS],
                row[self.c.COLS.TARGET_IDS],
            )
        s1s2 = company_data.loc[
            (row[self.c.COLS.COMPANY_ID], row[self.c.COLS.TIME_FRAME], EScope.S1S2)
        ]
        s3 = company_data.loc[
            (row[self.c.COLS.COMPANY_ID], row[self.c.COLS.TIME_FRAME], EScope.S3)
        ]

        # returning different sets of target_ids depending on how GHG temperature score is determined
        s1s2_targets = s1s2[self.c.COLS.TARGET_IDS]
        combined_targets = ((s1s2_targets or []) + (s3[self.c.COLS.TARGET_IDS] or [])) or None

        # Bloomberg proposal to return original score (changed 2022-09-01) if ghg scope12 or 3 is empty
        if pd.isnull(s1s2[self.c.COLS.GHG_SCOPE12]) or pd.isnull(s3[self.c.COLS.GHG_SCOPE3]):
            return (
                row[self.c.COLS.TEMPERATURE_SCORE],
                row[self.c.TEMPERATURE_RESULTS],
                row[self.c.COLS.TARGET_IDS],
            )

        try:
            # If the s3 emissions are less than 40 percent, we'll ignore them altogether, if not, we'll weigh them
            if (
                s3[self.c.COLS.GHG_SCOPE3]
                / (s1s2[self.c.COLS.GHG_SCOPE12] + s3[self.c.COLS.GHG_SCOPE3])
                < 0.4
            ):
                return (
                    s1s2[self.c.COLS.TEMPERATURE_SCORE],
                    s1s2[self.c.TEMPERATURE_RESULTS],
                    s1s2_targets,
                )
            else:
                company_emissions = (
                    s1s2[self.c.COLS.GHG_SCOPE12] + s3[self.c.COLS.GHG_SCOPE3]
                )
                return (
                    (
                        s1s2[self.c.COLS.TEMPERATURE_SCORE]
                        * s1s2[self.c.COLS.GHG_SCOPE12]
                        + s3[self.c.COLS.TEMPERATURE_SCORE] * s3[self.c.COLS.GHG_SCOPE3]
                    )
                    / company_emissions,
                    (
                        s1s2[self.c.TEMPERATURE_RESULTS] * s1s2[self.c.COLS.GHG_SCOPE12]
                        + s3[self.c.TEMPERATURE_RESULTS] * s3[self.c.COLS.GHG_SCOPE3]
                    )
                    / company_emissions,
                    combined_targets,
                )

        # TODO - this doesn't get triggered if denom is np.float64, instead returns an (inf, inf),
        #  which 'ruins' the default score return and end up with NULL values where should have defaults
        except ZeroDivisionError:
            raise ValueError("The mean of the S1+S2 plus the S3 emissions is zero")

    def get_default_score(self, target: pd.Series) -> int:
        """
        Get the temperature score for a certain target based on the annual reduction rate and the regression parameters.

        :param target: The target as a row of a dataframe
        :return: The temperature score
        """
        if (
            pd.isnull(target[self.c.COLS.REGRESSION_PARAM])
            or pd.isnull(target[self.c.COLS.REGRESSION_INTERCEPT])
            or pd.isnull(target[self.c.COLS.ANNUAL_REDUCTION_RATE])
        ):
            return 1
        return 0

    def _prepare_data(self, data: pd.DataFrame):
        """
        Prepare the data such that it can be used to calculate the temperature score.

        :param data: The original data set as a pandas data frame
        :return: The extended data frame
        """
        # IDataProvider provides this optional field as an empty list by default
        # but if call TemperatureScore class with DataFrame directly then it may not be present
        if self.c.COLS.TARGET_IDS not in data.columns:
            data[self.c.COLS.TARGET_IDS] = [[] for _ in range(len(data))]

        # If scope S1S2S3 is in the list of scopes to calculate, we need to calculate the other two as well
        scopes = self.scopes.copy()
        if EScope.S1S2S3 in self.scopes and EScope.S1S2 not in self.scopes:
            scopes.append(EScope.S1S2)
        if EScope.S1S2S3 in scopes and EScope.S3 not in scopes:
            scopes.append(EScope.S3)

        data = data[
            data[self.c.COLS.SCOPE].isin(scopes)
            & data[self.c.COLS.TIME_FRAME].isin(self.time_frames)
        ].copy()

        data[self.c.COLS.TARGET_REFERENCE_NUMBER] = data[
            self.c.COLS.TARGET_REFERENCE_NUMBER
        ].replace({np.nan: self.c.VALUE_TARGET_REFERENCE_ABSOLUTE})
        data[self.c.COLS.SR15] = data.apply(
            lambda row: self.get_target_mapping(row), axis=1
        )
        data[self.c.COLS.ANNUAL_REDUCTION_RATE] = data.apply(
            lambda row: self.get_annual_reduction_rate(row), axis=1
        )
        data = self._merge_regression(data)

        # TODO: Move temperature result to cols
        data[self.c.COLS.TEMPERATURE_SCORE], data[self.c.TEMPERATURE_RESULTS] = zip(
            *data.apply(lambda row: self.get_score(row), axis=1)
        )

        data = self.cap_scores(data)
        return data

    def _calculate_company_score(self, data):
        """
        Calculate the combined s1s2s3 scores for all companies.

        :param data: The original data set as a pandas data frame
        :return: The data frame, with an updated s1s2s3 temperature score
        """
        # Calculate the GHC
        company_data = (
            data[
                [
                    self.c.COLS.COMPANY_ID,
                    self.c.COLS.TIME_FRAME,
                    self.c.COLS.SCOPE,
                    self.c.COLS.GHG_SCOPE12,
                    self.c.COLS.GHG_SCOPE3,
                    self.c.COLS.TEMPERATURE_SCORE,
                    self.c.COLS.TARGET_IDS,
                    self.c.TEMPERATURE_RESULTS,
                ]
            ]
            .groupby(
                [self.c.COLS.COMPANY_ID, self.c.COLS.TIME_FRAME, self.c.COLS.SCOPE]
            )
            .agg(
                # take the mean of numeric columns, list-append self.c.COLS.TARGET_IDS
                {
                    self.c.COLS.GHG_SCOPE12: "mean",
                    self.c.COLS.GHG_SCOPE3: "mean",
                    self.c.COLS.TEMPERATURE_SCORE: "mean",
                    self.c.TEMPERATURE_RESULTS: "mean",
                    self.c.COLS.TARGET_IDS: "sum",
                }
            )
        )

        # sum pandas aggregator returns 0 where all input targets were None
        company_data.loc[
            company_data[self.c.COLS.TARGET_IDS] == 0, self.c.COLS.TARGET_IDS
        ] = None

        (
            data[self.c.COLS.TEMPERATURE_SCORE],
            data[self.c.TEMPERATURE_RESULTS],
            data[self.c.COLS.TARGET_IDS],
        ) = zip(
            *data.apply(
                lambda row: self.get_ghc_temperature_score(row, company_data), axis=1
            )
        )
        return data

    def calculate(
        self,
        data: Optional[pd.DataFrame] = None,
        data_providers: Optional[List[data.DataProvider]] = None,
        portfolio: Optional[List[PortfolioCompany]] = None,
    ):
        """
        Calculate the temperature for a dataframe of company data. The columns in the data frame should be a combination
        of IDataProviderTarget and IDataProviderCompany.

        :param data: The data set (or None if the data should be retrieved)
        :param data_providers: A list of DataProvider instances. Optional, only required if data is empty.
        :param portfolio: A list of PortfolioCompany models. Optional, only required if data is empty.
        :return: A data frame containing all relevant information for the targets and companies
        """
        if data is None:
            if data_providers is not None and portfolio is not None:
                data = utils.get_data(data_providers, portfolio)
            else:
                raise ValueError(
                    "You need to pass and either a data set or a list of data providers and companies"
                )

        data = self._prepare_data(data)

        if EScope.S1S2S3 in self.scopes:
            # self._check_column(data, self.c.COLS.GHG_SCOPE12)
            # self._check_column(data, self.c.COLS.GHG_SCOPE3)
            data = self._calculate_company_score(data)

        # We need to filter the scopes again, because we might have had to add a scope in the preparation step
        data = data[data[self.c.COLS.SCOPE].isin(self.scopes)]
        data[self.c.COLS.TEMPERATURE_SCORE] = data[self.c.COLS.TEMPERATURE_SCORE].round(
            2
        )
        return data

    def _get_aggregations(
        self, data: pd.DataFrame, total_companies: int
    ) -> Tuple[Aggregation, pd.Series, pd.Series]:
        """
        Get the aggregated score over a certain data set. Also calculate the (relative) contribution of each company

        :param data: A data set, containing one row per company
        :return: An aggregated score and the relative and absolute contribution of each company
        """
        data = data.copy()
        weighted_scores = self._calculate_aggregate_score(
            data, self.c.COLS.TEMPERATURE_SCORE, self.aggregation_method
        )
        data[self.c.COLS.CONTRIBUTION_RELATIVE] = weighted_scores / (
            weighted_scores.sum() / 100
        )
        data[self.c.COLS.CONTRIBUTION] = weighted_scores
        contributions = (
            data.sort_values(self.c.COLS.CONTRIBUTION_RELATIVE, ascending=False)
            .where(pd.notnull(data), None)
            .to_dict(orient="records")
        )
        return (
            Aggregation(
                score=weighted_scores.sum(),
                proportion=len(weighted_scores) / (total_companies / 100.0),
                contributions=[
                    AggregationContribution.parse_obj(contribution)
                    for contribution in contributions
                ],
            ),
            data[self.c.COLS.CONTRIBUTION_RELATIVE],
            data[self.c.COLS.CONTRIBUTION],
        )

    def _get_score_aggregation(
        self, data: pd.DataFrame, time_frame: ETimeFrames, scope: EScope
    ) -> Optional[ScoreAggregation]:
        """
        Get a score aggregation for a certain time frame and scope, for the data set as a whole and for the different
        groupings.

        :param data: The whole data set
        :param time_frame: A time frame
        :param scope: A scope
        :return: A score aggregation, containing the aggregations for the whole data set and each individual group
        """
        filtered_data = data[
            (data[self.c.COLS.TIME_FRAME] == time_frame)
            & (data[self.c.COLS.SCOPE] == scope)
        ].copy()
        filtered_data[self.grouping] = filtered_data[self.grouping].fillna("unknown")
        total_companies = len(filtered_data)
        if not filtered_data.empty:
            (
                score_aggregation_all,
                filtered_data[self.c.COLS.CONTRIBUTION_RELATIVE],
                filtered_data[self.c.COLS.CONTRIBUTION],
            ) = self._get_aggregations(filtered_data, total_companies)
            score_aggregation = ScoreAggregation(
                grouped={},
                all=score_aggregation_all,
                influence_percentage=self._calculate_aggregate_score(
                    filtered_data, self.c.TEMPERATURE_RESULTS, self.aggregation_method
                ).sum()
                * 100,
            )

            # If there are grouping column(s) we'll group in pandas and pass the results to the aggregation
            if len(self.grouping) > 0:
                grouped_data = filtered_data.groupby(self.grouping)
                for group_names, group in grouped_data:
                    group_name_joined = (
                        group_names
                        if type(group_names) == str
                        else "-".join([str(group_name) for group_name in group_names])
                    )
                    (
                        score_aggregation.grouped[group_name_joined],
                        _,
                        _,
                    ) = self._get_aggregations(group.copy(), total_companies)
            return score_aggregation
        else:
            return None

    def aggregate_scores(self, data: pd.DataFrame) -> ScoreAggregations:
        """
        Aggregate scores to create a portfolio score per time_frame (short, mid, long).

        :param data: The results of the calculate method
        :return: A weighted temperature score for the portfolio
        """

        score_aggregations = ScoreAggregations()
        for time_frame in self.time_frames:
            score_aggregation_scopes = ScoreAggregationScopes()
            for scope in self.scopes:
                score_aggregation_scopes.__setattr__(
                    scope.name, self._get_score_aggregation(data, time_frame, scope)
                )
            score_aggregations.__setattr__(time_frame.value, score_aggregation_scopes)

        return score_aggregations

    def cap_scores(self, scores: pd.DataFrame) -> pd.DataFrame:
        """
        Cap the temperature scores in the input data frame to a certain value, based on the scenario that's being used.
        This can either be for the whole data set, or only for the top X contributors.

        :param scores: The data set with the temperature scores
        :return: The input data frame, with capped scores
        """
        if self.scenario is None:
            return scores
        if self.scenario.scenario_type == ScenarioType.APPROVED_TARGETS:
            score_based_on_target = ~pd.isnull(
                scores[self.c.COLS.TARGET_REFERENCE_NUMBER]
            )
            scores.loc[
                score_based_on_target, self.c.COLS.TEMPERATURE_SCORE
            ] = scores.loc[score_based_on_target, self.c.COLS.TEMPERATURE_SCORE].apply(
                lambda x: min(x, self.scenario.get_score_cap())
            )
        elif self.scenario.scenario_type == ScenarioType.HIGHEST_CONTRIBUTORS:
            # Cap scores of 10 highest contributors per time frame-scope combination
            # TODO: Should this actually be per time-frame/scope combi? Aren't you engaging the company as a whole?
            aggregations = self.aggregate_scores(scores)
            for time_frame in self.time_frames:
                for scope in self.scopes:
                    number_top_contributors = min(
                        10,
                        len(
                            aggregations[time_frame.value][scope.name].all.contributions
                        ),
                    )
                    for contributor in range(number_top_contributors):
                        company_name = aggregations[time_frame.value][
                            scope.name
                        ].all.contributions[contributor][self.c.COLS.COMPANY_NAME]
                        company_mask = (
                            (scores[self.c.COLS.COMPANY_NAME] == company_name)
                            & (scores[self.c.COLS.SCOPE] == scope)
                            & (scores[self.c.COLS.TIME_FRAME] == time_frame)
                        )
                        scores.loc[
                            company_mask, self.c.COLS.TEMPERATURE_SCORE
                        ] = scores.loc[
                            company_mask, self.c.COLS.TEMPERATURE_SCORE
                        ].apply(
                            lambda x: min(x, self.scenario.get_score_cap())
                        )
        elif self.scenario.scenario_type == ScenarioType.HIGHEST_CONTRIBUTORS_APPROVED:
            score_based_on_target = scores[self.c.COLS.ENGAGEMENT_TARGET]
            scores.loc[
                score_based_on_target, self.c.COLS.TEMPERATURE_SCORE
            ] = scores.loc[score_based_on_target, self.c.COLS.TEMPERATURE_SCORE].apply(
                lambda x: min(x, self.scenario.get_score_cap())
            )
        return scores

    def anonymize_data_dump(self, scores: pd.DataFrame) -> pd.DataFrame:
        """
        Anonymize the scores by deleting the company IDs, ISIN and renaming the companies.

        :param scores: The data set with the temperature scores
        :return: The input data frame, anonymized
        """
        scores.drop(
            columns=[self.c.COLS.COMPANY_ID, self.c.COLS.COMPANY_ISIN], inplace=True
        )
        for index, company_name in enumerate(scores[self.c.COLS.COMPANY_NAME].unique()):
            scores.loc[
                scores[self.c.COLS.COMPANY_NAME] == company_name,
                self.c.COLS.COMPANY_NAME,
            ] = "Company" + str(index + 1)
        return scores

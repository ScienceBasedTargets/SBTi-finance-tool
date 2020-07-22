import itertools
from typing import Optional, Tuple, Type, Dict

import pandas as pd

from SBTi.portfolio_aggregation import PortfolioAggregation, PortfolioAggregationMethod
from .configs import TemperatureScoreConfig


class TemperatureScore(PortfolioAggregation):
    """
    This class is provides a temperature score based on the climate goals.

    :param fallback_score: The temp score if a company is not found
    :param model: The regression model to use
    :param config: A class defining the constants that are used throughout this class. This parameter is only required
                    if you'd like to overwrite a constant. This can be done by extending the TemperatureScoreConfig
                    class and overwriting one of the parameters.
    """

    def __init__(self, fallback_score: float = 3.2, model: int = 4,
                 config: Type[TemperatureScoreConfig] = TemperatureScoreConfig):
        super().__init__(config)
        self.fallback_score = fallback_score
        self.model = model
        self.c: Type[TemperatureScoreConfig] = config
        self.scenario = dict(number=0)
        self.score_cap = None

        # Load the mappings from industry to SR15 goal
        self.mapping = pd.read_excel(self.c.FILE_SR15_MAPPING, header=0)
        self.regression_model = pd.read_excel(self.c.FILE_REGRESSION_MODEL_SUMMARY, header=0)

    def get_target_mapping(self, target: pd.Series) -> Optional[str]:
        """
        Map the target onto an SR15 target (None if not available).

        :param target: The target as a row of a dataframe
        :return: The mapped SR15 target
        """

        # Todo: For beta test, we are using a different SR15 Mapping excel. We are mapping based on Target Type and Intensity Metric
        # Check if the industry exists, if not use a default
        # industry = target[self.c.COLS.INDUSTRY] \
        #     if target[self.c.COLS.INDUSTRY] in self.mapping[self.c.COLS.INDUSTRY] \
        #     else self.c.DEFAULT_INDUSTRY

        # mappings = self.mapping[(self.mapping[self.c.COLS.INDUSTRY] == industry) &
        #                         (self.mapping[self.c.COLS.TARGET_TYPE] == target_type) &
        #                         (self.mapping[self.c.COLS.SCOPE] == target[self.c.COLS.SCOPE_CATEGORY])]


        # Todo: Talk with Daan, after Beta testing, to see how to address this. I do believe this is only for the testing
        target_type = self.c.VALUE_TARGET_REFERENCE_INTENSITY \
            if type(target[self.c.COLS.TARGET_REFERENCE_NUMBER]) == str and \
               target[self.c.COLS.TARGET_REFERENCE_NUMBER].strip().startswith(
                   self.c.VALUE_TARGET_REFERENCE_INTENSITY_BASE) \
            else self.c.VALUE_TARGET_REFERENCE_ABSOLUTE

        if target_type== self.c.VALUE_TARGET_REFERENCE_ABSOLUTE:
            mappings = self.mapping[(self.mapping[self.c.COLS.TARGET_TYPE_SR15] == target_type)]

        elif target_type== self.c.VALUE_TARGET_REFERENCE_INTENSITY:
            mappings = self.mapping[(self.mapping[self.c.COLS.TARGET_TYPE_SR15] == target_type) &
                                    (self.mapping[self.c.COLS.INTENSITY_METRIC_SR15] == target[self.c.COLS.INTENSITY_METRIC])]

        if len(mappings) == 0:
            return None
        elif len(mappings) > 1:
            # There should never be more than one potential mapping
            raise ValueError("There is more than one potential mapping to a SR15 goal.")
        else:
            return mappings.iloc[0][self.c.COLS.REGRESSION_MODEL]

    def get_annual_reduction_rate(self, target: pd.Series) -> Optional[float]:
        """
        Get the annual reduction rate (or None if not available).

        :param target: The target as a row of a dataframe
        :return: The annual reduction
        """
        if pd.isnull(target[self.c.COLS.REDUCTION_AMBITION]):
            return None

        try:
            return target[self.c.COLS.REDUCTION_AMBITION] / float(target[self.c.COLS.END_YEAR] -
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
        if pd.isnull(target[self.c.COLS.REGRESSION_PARAM]) or pd.isnull(target[self.c.COLS.REGRESSION_INTERCEPT]) \
                or pd.isnull(target[self.c.COLS.ANNUAL_REDUCTION_RATE]):
            return self.fallback_score
        return target[self.c.COLS.REGRESSION_PARAM] * target[self.c.COLS.ANNUAL_REDUCTION_RATE] + target[
            self.c.COLS.REGRESSION_INTERCEPT]

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
            return (s1s2[self.c.COLS.TEMPERATURE_SCORE].mean() * s1s2[self.c.COLS.GHG_SCOPE12].mean() +
                    s3[self.c.COLS.TEMPERATURE_SCORE].mean() * s3[self.c.COLS.GHG_SCOPE3].mean()) / \
                   (s1s2[self.c.COLS.GHG_SCOPE12].mean() + s3[self.c.COLS.GHG_SCOPE3].mean())
        except ZeroDivisionError:
            raise ValueError("The mean of the S1+S2 plus the S3 emissions is zero")

    def get_default_score(self, target: pd.Series) -> str:
        """
        Get the temperature score for a certain target based on the annual reduction rate and the regression parameters.

        :param target: The target as a row of a dataframe
        :return: The temperature score
        """
        if pd.isnull(target[self.c.COLS.REGRESSION_PARAM]) or pd.isnull(target[self.c.COLS.REGRESSION_INTERCEPT]) \
                or pd.isnull(target[self.c.COLS.ANNUAL_REDUCTION_RATE]):
            return 'default'
        return 'target'

    def calculate(self, data: pd.DataFrame, extra_columns: Optional[list] = None):
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
        * company_revenue: The revenue of the company. Only required to use the ROTS portfolio aggregation.

        :param extra_columns: A list of user defined extra, company related, columns
        :param data:
        :return: A data frame containing all relevant information for the targets and companies
        """
        if extra_columns is None:
            extra_columns = []

        data[self.c.COLS.SR15] = data.apply(lambda row: self.get_target_mapping(row), axis=1)
        data[self.c.COLS.ANNUAL_REDUCTION_RATE] = data.apply(lambda row: self.get_annual_reduction_rate(row), axis=1)
        data[self.c.COLS.REGRESSION_PARAM], data[self.c.COLS.REGRESSION_INTERCEPT] = zip(
            *data.apply(lambda row: self.get_regression(row), axis=1)
        )
        data[self.c.COLS.TEMPERATURE_SCORE] = data.apply(lambda row: self.get_score(row), axis=1)
        if (self.scenario['number'] == 2) or (self.scenario['number'] == 3):
            data = self.cap_scores(data)
        combined_data = []
        # company_columns = [column for column in self.c.COLS.COMPANY_COLUMNS + extra_columns if column in data.columns]
        company_columns = extra_columns + list(data.columns)
        for company in data[self.c.COLS.COMPANY_NAME].unique():
            for time_frame in self.c.VALUE_TIME_FRAMES:
                # We always include all company specific data
                company_values = data[data[self.c.COLS.COMPANY_NAME] == company]
                company_data = {
                    column: company_values[column].mode().iloc[0] if len(company_values[column].mode()) > 0 else None
                    for column in company_columns}
                company_data[self.c.COLS.COMPANY_NAME] = company
                company_data[self.c.COLS.SCOPE] = self.c.VALUE_SCOPE_S1S2S3
                company_data[self.c.COLS.SCOPE_CATEGORY] = self.c.VALUE_SCOPE_CATEGORY_S1S2S3
                company_data[self.c.COLS.TIME_FRAME] = time_frame
                company_data[self.c.COLS.TEMPERATURE_SCORE] = self.get_ghc_temperature_score(data, company, time_frame)
                combined_data.append(company_data)

        data_score = pd.concat([data, pd.DataFrame(combined_data)])
        data_score.reset_index(inplace=True, drop=True)
        for time_frame in data_score[self.c.COLS.TIME_FRAME].unique():
            for company in data_score[self.c.COLS.COMPANY_NAME].unique():
                company_data = data_score[(data_score[self.c.COLS.COMPANY_NAME] == company)
                                          & (data_score[self.c.COLS.TIME_FRAME] == time_frame)]
                scope_3_emissions = company_data[self.c.COLS.GHG_SCOPE3].iloc[0]
                scope_12_emissions = company_data[self.c.COLS.GHG_SCOPE12].iloc[0]
                scope_123_emissions = scope_12_emissions + scope_3_emissions
                if not pd.isnull(scope_3_emissions) & pd.isnull(scope_123_emissions):
                    s1s2_temp_score = \
                        company_data[company_data[self.c.COLS.SCOPE_CATEGORY] == 's1s2'][self.c.COLS.TEMPERATURE_SCORE].values[0]
                    s3_temp_score = company_data[company_data[self.c.COLS.SCOPE_CATEGORY] == 's3'][self.c.COLS.TEMPERATURE_SCORE].values[0]
                    index = \
                        data_score[(data_score[self.c.COLS.COMPANY_NAME] == company) & (data_score[self.c.COLS.TIME_FRAME] == time_frame) &
                                   (data_score[self.c.COLS.SCOPE_CATEGORY] == 's1s2s3')].index[0]
                    if (scope_3_emissions / scope_123_emissions) < 0.4:
                        data_score.at[index, self.c.COLS.TEMPERATURE_SCORE] = s1s2_temp_score

                    else:
                        data_score.at[index, self.c.COLS.TEMPERATURE_SCORE] = ((s1s2_temp_score * scope_12_emissions) +
                                                                     (s3_temp_score * scope_3_emissions)) / (
                                                                        scope_123_emissions)
        return data_score

    def aggregate_scores(self, data: pd.DataFrame, portfolio_aggregation_method: Type[PortfolioAggregationMethod],
                         grouping: Optional[list] = None):
        """
        Aggregate scores to create a portfolio score per time_frame (short, mid, long).

        :param data: The results of the calculate method
        :param portfolio_aggregation_method: PortfolioAggregationMethod: The aggregation method to use
        :param grouping: The grouping to use
        :return: A weighted temperature score for the portfolio
        """
        portfolio_scores:Dict = {
            time_frame: {scope: {} for scope in data[self.c.COLS.SCOPE_CATEGORY].unique()}
            for time_frame in data[self.c.COLS.TIME_FRAME].unique()}

        for time_frame, scope in itertools.product(data[self.c.COLS.TIME_FRAME].unique(),
                                                   data[self.c.COLS.SCOPE_CATEGORY].unique()):
            filtered_data = data[(data[self.c.COLS.TIME_FRAME] == time_frame) & (
                    data[self.c.COLS.SCOPE_CATEGORY] == scope)].copy()

            if not filtered_data.empty:
                # portfolio_scores[time_frame] = {}
                weighted_scores = self._calculate_aggregate_score(filtered_data, self.c.COLS.TEMPERATURE_SCORE,
                                                                  self.c.COLS.WEIGHTED_TEMPERATURE_SCORE,
                                                                  portfolio_aggregation_method)
                portfolio_scores[time_frame][scope]["all"] = {}
                portfolio_scores[time_frame][scope]["all"]["score"] = round(weighted_scores.sum(),4)
                filtered_data[self.c.COLS.CONTRIBUTION_RELATIVE] = weighted_scores / (weighted_scores.sum() / 100)
                filtered_data[self.c.COLS.CONTRIBUTION] = weighted_scores
                portfolio_scores[time_frame][scope]["all"]["contributions"] = filtered_data \
                    .sort_values(self.c.COLS.CONTRIBUTION_RELATIVE, ascending=False)[
                    self.c.CONTRIBUTION_COLUMNS].to_dict(orient="records")

                # If there are grouping column(s) we'll group in pandas and pass the results to the aggregation
                if grouping is not None and len(grouping) > 0:
                    grouped_data = filtered_data.groupby(grouping)
                    for group_name, group in grouped_data:
                        group_data = group.copy()
                        weighted_scores = self._calculate_aggregate_score(group_data, self.c.COLS.TEMPERATURE_SCORE,
                                                                          self.c.COLS.WEIGHTED_TEMPERATURE_SCORE,
                                                                          portfolio_aggregation_method)
                        group_name_joined = group_name if type(group_name) == str else "-".join(group_name)
                        group_data[self.c.COLS.CONTRIBUTION_RELATIVE] = weighted_scores / (weighted_scores.sum() / 100)
                        group_data[self.c.COLS.CONTRIBUTION] = weighted_scores
                        portfolio_scores[time_frame][scope][group_name_joined] = {}
                        portfolio_scores[time_frame][scope][group_name_joined]["score"] = weighted_scores.sum()
                        portfolio_scores[time_frame][scope][group_name_joined]["contributions"] = \
                            group_data.sort_values(self.c.COLS.CONTRIBUTION_RELATIVE, ascending=False)[
                                self.c.CONTRIBUTION_COLUMNS].to_dict(orient="records")
            else:
                portfolio_scores[time_frame][scope] = None

        return portfolio_scores

    def temperature_score_influence_percentage(self, data, aggregation_method):
        """
        Determines the percentage of the temperature score is covered by target and default score

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
            ECOTS, AOTS and ROTS portfolio aggregation.
        * company_enterprise_value: The enterprise value of the company. Only required to use the EOTS portfolio
            aggregation.
        * company_ev_plus_cash: The enterprise value of the company plus cash. Only required to use the ECOTS portfolio
            aggregation.
        * company_total_assets: The total assets of the company. Only required to use the AOTS portfolio aggregation.

        :param data: output from the target_valuation_protocol

        :return: A dataframe containing the percentage contributed by the default and target score for all three timeframes
        """
        data[self.c.COLS.SR15] = data.apply(lambda row: self.get_target_mapping(row), axis=1)
        data[self.c.COLS.ANNUAL_REDUCTION_RATE] = data.apply(lambda row: self.get_annual_reduction_rate(row), axis=1)
        data[self.c.COLS.REGRESSION_PARAM], data[self.c.COLS.REGRESSION_INTERCEPT] = zip(
            *data.apply(lambda row: self.get_regression(row), axis=1))

        data[self.c.TEMPERATURE_RESULTS] = data.apply(lambda row: self.get_default_score(row), axis=1)

        if aggregation_method == "MOTS" or \
                aggregation_method == "EOTS" or \
                aggregation_method == "ECOTS" or \
                aggregation_method == "AOTS" or \
                aggregation_method == "ROTS":
            # These four methods only differ in the way the company is valued.
            value_column = self.c.COLS.MARKET_CAP
            if aggregation_method == "EOTS":
                value_column = self.c.COLS.COMPANY_ENTERPRISE_VALUE
            elif aggregation_method == "ECOTS":
                value_column = self.c.COLS.COMPANY_EV_PLUS_CASH
                data[self.c.COLS.COMPANY_EV_PLUS_CASH] = data[self.c.COLS.COMPANY_ENTERPRISE_VALUE] + data[
                    self.c.COLS.CASH_EQUIVALENTS]
            elif aggregation_method == "AOTS":
                value_column = self.c.COLS.COMPANY_TOTAL_ASSETS
            elif aggregation_method == "ROTS":
                value_column = self.c.COLS.COMPANY_REVENUE

            # Calculate the total owned emissions of all companies
            try:
                data[self.c.COLS.OWNED_EMISSIONS] = data.apply(
                    lambda row: ((row[self.c.COLS.INVESTMENT_VALUE] / row[value_column]) * (
                            row[self.c.COLS.GHG_SCOPE12] + row[self.c.COLS.GHG_SCOPE3])),
                    axis=1
                )
            except ZeroDivisionError:
                raise ValueError("To calculate the aggregation, the {} column may not be zero".format(value_column))
            owned_emissions = data[self.c.COLS.OWNED_EMISSIONS].sum()

        company_temp_contribution = {
            self.c.TIME_FRAME_SHORT: {
                scope: {company: 0 for company in data[self.c.COLS.COMPANY_NAME].unique()} for scope in self.c.VALUE_SCOPE_CATEGORIES
            },
            self.c.TIME_FRAME_MID: {
                scope: {company: 0 for company in data[self.c.COLS.COMPANY_NAME].unique()} for scope in self.c.VALUE_SCOPE_CATEGORIES
            },
            self.c.TIME_FRAME_LONG: {
                scope: {company: 0 for company in data[self.c.COLS.COMPANY_NAME].unique()} for scope in self.c.VALUE_SCOPE_CATEGORIES
            }
        }

        time_frame_dictionary = {time_frame: {} for time_frame in data[self.c.COLS.TIME_FRAME].unique()}
        for time_frame in data[self.c.COLS.TIME_FRAME].unique():
            for scope in self.c.VALUE_SCOPE_CATEGORIES:
                for company in data[self.c.COLS.COMPANY_NAME].unique():
                    company_data = data[(data[self.c.COLS.COMPANY_NAME] == company) & (data[self.c.COLS.TIME_FRAME] == time_frame)]
                    if company_data[company_data[self.c.COLS.SCOPE_CATEGORY] == self.c.VALUE_SCOPE_CATEGORY_S1S2][self.c.TEMPERATURE_RESULTS].unique()[0] == 'default':
                        ds_s1s2 = 1
                    else:
                        ds_s1s2 = 0
                    if company_data[company_data[self.c.COLS.SCOPE_CATEGORY] == self.c.VALUE_SCOPE_CATEGORY_S3][self.c.TEMPERATURE_RESULTS].unique()[0] == 'default':
                        ds_s3 = 1
                    else:
                        ds_s3 = 0
                    s1s2_emissions = company_data.iloc[1][self.c.COLS.GHG_SCOPE12]
                    s3_emissions = company_data.iloc[1][self.c.COLS.GHG_SCOPE3]

                    if scope == self.c.VALUE_SCOPE_CATEGORY_S1S2:
                        scope_weight = ds_s1s2
                    elif scope == self.c.VALUE_SCOPE_CATEGORY_S1S2S3:
                        scope_weight = (ds_s1s2 * (s1s2_emissions / (s1s2_emissions + s3_emissions)) +
                                        ds_s3 * (s3_emissions / (s1s2_emissions + s3_emissions)))
                    elif scope == self.c.VALUE_SCOPE_CATEGORY_S3:
                        scope_weight = ds_s3

                    if aggregation_method == 'WATS':
                        portfolio_weight_storage = []
                        for company in data[self.c.COLS.COMPANY_NAME].unique():
                            portfolio_weight_storage.append(
                                data[data[self.c.COLS.COMPANY_NAME] == company].iloc[1][self.c.PORTFOLIO_WEIGHT])
                        portfolio_weight_total = sum(portfolio_weight_storage)
                        data[self.c.PORTFOLIO_WEIGHT] = data[self.c.PORTFOLIO_WEIGHT] / portfolio_weight_total

                        portfolio_weight = company_data.iloc[1][self.c.PORTFOLIO_WEIGHT]
                        value = portfolio_weight * scope_weight

                    elif aggregation_method == 'TETS':
                        company_emissions = company_data[self.c.COLS.GHG_SCOPE12].iloc[0] + \
                                            company_data[self.c.COLS.GHG_SCOPE3].iloc[0] # per company
                        portfolio_emissions = data[self.c.COLS.GHG_SCOPE12].sum() + data[
                            self.c.COLS.GHG_SCOPE3].sum()
                        value = company_emissions/portfolio_emissions * scope_weight

                    elif aggregation_method == 'MOTS':
                        company_emissions = company_data[self.c.COLS.GHG_SCOPE12].iloc[0] + \
                                            company_data[self.c.COLS.GHG_SCOPE3].iloc[0]  # per company
                        investment_value = company_data[self.c.COLS.INVESTMENT_VALUE].iloc[0]
                        market_cap = company_data[self.c.COLS.MARKET_CAP].iloc[0]
                        value = (((investment_value/market_cap)*company_emissions)/owned_emissions) * scope_weight

                    elif aggregation_method == 'EOTS':
                        company_emissions = company_data[self.c.COLS.GHG_SCOPE12].iloc[0] + \
                                            company_data[self.c.COLS.GHG_SCOPE3].iloc[0]
                        investment_value = company_data[self.c.COLS.INVESTMENT_VALUE].iloc[0]
                        enterprise_value = company_data[self.c.COLS.COMPANY_ENTERPRISE_VALUE].iloc[0]
                        value = (((investment_value/enterprise_value)*company_emissions)/owned_emissions) * scope_weight

                    elif aggregation_method == 'ECOTS':
                        investment_value = company_data[self.c.COLS.INVESTMENT_VALUE].iloc[0]
                        company_emissions = company_data[self.c.COLS.GHG_SCOPE12].iloc[0] + \
                                            company_data[self.c.COLS.GHG_SCOPE3].iloc[0]
                        company_ev_cash = company_data[self.c.COLS.CASH_EQUIVALENTS].iloc[0]
                        value = ((((investment_value/company_ev_cash)*company_emissions))/owned_emissions) * scope_weight

                    elif aggregation_method == 'AOTS':
                        investment_value = company_data[self.c.COLS.INVESTMENT_VALUE].iloc[0]
                        company_emissions = company_data[self.c.COLS.GHG_SCOPE12].iloc[0] + \
                                            company_data[self.c.COLS.GHG_SCOPE3].iloc[0]
                        company_total_assets = company_data[self.c.COLS.COMPANY_TOTAL_ASSETS].iloc[0]
                        value = (((investment_value/company_total_assets)*company_emissions)/owned_emissions) * scope_weight

                    elif aggregation_method == 'ROTS':
                        investment_value = company_data[self.c.COLS.INVESTMENT_VALUE].iloc[0]
                        company_emissions = company_data[self.c.COLS.GHG_SCOPE12].iloc[0] + \
                                            company_data[self.c.COLS.GHG_SCOPE3].iloc[0]
                        company_revenue = company_data[self.c.COLS.COMPANY_REVENUE].iloc[0]
                        value = (((investment_value/company_revenue)*company_emissions)/owned_emissions) * scope_weight

                    company_temp_contribution[time_frame][scope][company] = value
                time_frame_dictionary[time_frame][scope] = round(sum(company_temp_contribution[time_frame][scope].values()), 3)
        dictionary = {
            'target': {
                time_frame: {scope: round(1 - time_frame_dictionary[time_frame][scope], 3) for scope in self.c.VALUE_SCOPE_CATEGORIES} for time_frame in data[self.c.COLS.TIME_FRAME].unique()
            },
            'default': {
                time_frame: {scope: time_frame_dictionary[time_frame][scope] for scope in self.c.VALUE_SCOPE_CATEGORIES} for time_frame in data[self.c.COLS.TIME_FRAME].unique()
            }
        }

        return dictionary

    def columns_percentage_distribution(self, data, columns):
        '''
        Percentage distribution of specific column or columns

        :param data: output from the target_valuation_protocol
        :param columns: specified column names the client would like to have a percentage distribution
        :return: percentage distribution of specified columns
        '''

        data = data[columns].fillna('<EMPTY>')
        if columns==None:
            return None
        elif len(columns) == 1:
            percentage_distribution = (data.groupby(columns[0]).size() / data[columns[0]].count()) * 100
            return percentage_distribution.to_dict()
        elif len(columns) > 1:
            percentage_distribution = (data.groupby(columns).size() / data[columns[0]].count()) * 100
            return percentage_distribution.to_dict()

    def set_scenario(self, scenario: Dict):
        self.scenario = scenario
        # Scenario 1: Engage companies to set targets
        if self.scenario['number'] == 1:
            self.fallback_score = 2.0
        # Scenario 2: Engage companies to validate targets by SBTi
        if self.scenario['number'] == 2:
            self.score_cap = 1.75
        # Scenario 3: Engaging the highest contributors (top 10) to set (better) targets
        if self.scenario['number'] == 3:
            if self.scenario['engagement_type'] == 'set_targets':
                self.score_cap = 2.0
            elif self.scenario['engagement_type'] == 'set_SBTi_targets':
                self.score_cap = 1.75

    def cap_scores(self, scores: pd.DataFrame):
        if self.scenario['number'] == 2:
            score_based_on_target = ~pd.isnull(scores[self.c.COLS.TARGET_REFERENCE_NUMBER])
            scores.loc[score_based_on_target, self.c.COLS.TEMPERATURE_SCORE] = self.score_cap
        elif self.scenario['number'] == 3:
            # Cap scores of 10 highest contributors per time frame-scope combination
            aggregations = self.aggregate_scores(scores, self.scenario['aggregation_method'], self.scenario['grouping'])
            for time_frame in self.c.VALUE_TIME_FRAMES:
                for scope in scores[self.c.COLS.SCOPE_CATEGORY].unique():
                    number_top_contributors = min(10, len(aggregations[time_frame][scope]['all']['contributions']))
                    for contributor in range(number_top_contributors):
                        company_name = aggregations[time_frame][scope]['all']['contributions'][contributor][self.c.COLS.COMPANY_NAME]
                        scores.loc[((scores[self.c.COLS.COMPANY_NAME] == company_name) &
                                   (scores[self.c.COLS.SCOPE_CATEGORY] == scope) &
                                   (scores[self.c.COLS.TIME_FRAME] == time_frame)), self.c.COLS.TEMPERATURE_SCORE] = self.score_cap
        return scores
    
    def anonymize_data_dump(self, scores):
        '''
        Anonymizes scores for raw data output
        '''
        scores.drop(columns=[self.c.COLS.COMPANY_ISIC, self.c.COLS.COMPANY_ID], inplace=True)
        for index, company_name in enumerate(scores[self.c.COLS.COMPANY_NAME].unique()):
            scores.loc[scores[self.c.COLS.COMPANY_NAME] == company_name, self.c.COLS.COMPANY_NAME] = 'Company' + str(index + 1)
        return scores

    def merge_percentage_coverage_to_aggregations(self, aggregations: Dict, temperature_percentage_coverage: Dict):
        """Iterates over two dictionaries and ads keys from second dictionary to the first.
        :param temperature_percentage_coverage: first 'main' dictionary where keys should be added
        :type temperature_percentage_coverage: dict
        :param aggregations: second dictionary wherefrom key-value pairs are added to first dictionary
        :type aggregations: dict
        :rtype: aggregations, dict
        :return: aggregations
        """
        for time_frame in [self.c.TIME_FRAME_SHORT, self.c.TIME_FRAME_MID, self.c.TIME_FRAME_LONG]:
            for scope in self.c.VALUE_SCOPE_CATEGORIES:
                if aggregations.get(time_frame) and aggregations[time_frame].get(scope):
                    aggregations[time_frame][scope]['influence_percentage'] = {
                        'default': temperature_percentage_coverage['default'][time_frame][scope]*100,
                        'target': temperature_percentage_coverage['target'][time_frame][scope]*100
                    }
        return aggregations



'''
company_total_assets are "NaN", which is causing "NaN" for "owned_emissions", 
which returns "NaN" for "weighted_scores" and that is causing the "NaN" AOTS 
in temperature score. What is causing company_total_asset to be NaN is temperature_score.calculate
'''
# from SBTi.portfolio_aggregation import PortfolioAggregationMethod
# scores = pd.read_excel('C:/Projects/SBTi/scores.xlsx')
# temperature_score = TemperatureScore(fallback_score=3.2)
# aggregations = temperature_score.aggregate_scores(scores[(scores['scope_category']=='s1s2s3') &
#                                                          (scores['time_frame']=='short')], PortfolioAggregationMethod.AOTS, None)
#

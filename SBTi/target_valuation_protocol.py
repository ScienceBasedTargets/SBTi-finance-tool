import datetime
import itertools

import pandas as pd
from typing import Type
from SBTi.configs import PortfolioAggregationConfig


class TargetValuationProtocol:

    def __init__(self, data: pd.DataFrame, company_data: pd.DataFrame, config: Type[PortfolioAggregationConfig] = PortfolioAggregationConfig):
        self.data = data
        self.c = config
        self.company_data = company_data

    def target_valuation_protocol(self):
        '''
        Runs the target valuation protcol by calling on the four required steps

        :rtype: list
        :return: a list of six columns containing dataframes in each one
        '''
        self.test_target_type()
        self.data[self.c.COLS.SCOPE] = self.data[self.c.COLS.SCOPE].str.lower()
        self.data[self.c.COLS.SCOPE_CATEGORY] = self.data.apply(
            lambda row: self.c.SCOPE_MAP[row[self.c.COLS.SCOPE]], axis=1)
        self.test_boundary_coverage()
        self.test_target_process()
        self.test_end_year()
        self.time_frame()
        self.group_targets()
        self.combining_records()
        self.creating_records_scope_timeframe()
        return self.data


    def test_end_year(self):
        '''
        Records that have a valid end_year will be returned. A valid end_year is defined as a year that is greater then
        the start_year.
        :return: a dataframe containing records that have correct end_year feature.
        '''
        index_list = []
        for index, record in self.data.iterrows():
            if record[self.c.COLS.END_YEAR] > record[self.c.COLS.START_YEAR]:
                index_list.append(index)
        self.data = self.data.loc[index_list]


    def test_target_type(self):
        """
        Test on target type and only allow only GHG emission reduction targets (absolute or intensity based).

        Target validation step 1: target type #64
        If target type is Absolute => continue
        If target type is Intensity =>
        -- If Intensity_metric is Other (or none is specified) => Invalid target
        -- For all other intensity_metrics => continue
        If target type is Other (or none is specified) => Invalid target
        """
        index_list = []
        self.data[self.c.COLS.TARGET_REFERENCE_NUMBER] = self.data[self.c.COLS.TARGET_REFERENCE_NUMBER].str.lower()
        self.data[self.c.COLS.INTENSITY_METRIC] = self.data[self.c.COLS.INTENSITY_METRIC].str.lower()
        for index, record in self.data.iterrows():
            if not pd.isna(record[self.c.COLS.TARGET_REFERENCE_NUMBER]):
                if 'abs' in record[self.c.COLS.TARGET_REFERENCE_NUMBER]:
                    index_list.append(index)
                elif 'int' in record[self.c.COLS.TARGET_REFERENCE_NUMBER]:
                    if (not pd.isna(record[self.c.COLS.INTENSITY_METRIC])):
                        if ('other' not in record[self.c.COLS.INTENSITY_METRIC]):
                            index_list.append(index)
        self.data = self.data.loc[index_list]


    def test_boundary_coverage(self):
        '''
        Test on boundary coverage:

        Option 1: minimal coverage threshold
        For S1+S2 targets: coverage% must be above 95%, for S3 targets coverage must be above 67%

        Option 2: weighted coverage
        Thresholds are still 95% and 67%, target is always valid. Below threshold ambition is scaled.*
        New target ambition = input target ambition * coverage
        *either here or in tem score module

        Option 3: default coverage
        Target is always valid, % uncovered is given default score in temperature score module.
        '''
        index = []
        for record in self.data.iterrows():
            if not pd.isna(record[1][self.c.COLS.SCOPE_CATEGORY]):
                if 's1s2' in record[1][self.c.COLS.SCOPE_CATEGORY]:
                    if record[1][self.c.COLS.COVERAGE_S1] > 95:
                        index.append(record[0])
                    else:
                        index.append(record[0])
                        self.data.at[record[0], self.c.COLS.REDUCTION_AMBITION] = \
                            self.data[self.c.COLS.REDUCTION_AMBITION].loc[record[0]] * \
                            (self.data[self.c.COLS.COVERAGE_S1].loc[record[0]])
                elif 's3' in record[1][self.c.COLS.SCOPE_CATEGORY]:
                    if record[1][self.c.COLS.COVERAGE_S3] > 67:
                        index.append(record[0])
                    else:
                        index.append(record[0])
                        self.data.at[record[0], self.c.COLS.REDUCTION_AMBITION] = \
                            self.data[self.c.COLS.REDUCTION_AMBITION].loc[record[0]] * \
                            (self.data[self.c.COLS.COVERAGE_S3].loc[record[0]])
        self.data = self.data.loc[index]



    def test_target_process(self):
        '''
        Test on target process
        If target process is 100%, the target is invalid (only forward looking targets allowed)
        Output: a list of valid targets per company

        Target progress: the percentage of the target already achieved
        '''
        if self.c.COLS.ACHIEVED_EMISSIONS in self.data.columns:
            index = []
            for record in self.data.iterrows():
                if not pd.isna(record[1][self.c.COLS.ACHIEVED_EMISSIONS]):
                    if record[1][self.c.COLS.ACHIEVED_EMISSIONS] != 100:
                        index.append(record[0])
            self.data = self.data.loc[index]

    def time_frame(self):
        '''
        Time frame is forward looking: target year - current year. Less than 5y = short, between 5 and 15 is mid, 15 to 30 is long
        '''
        now = datetime.datetime.now()
        time_frame_list = []
        for index, record in self.data.iterrows():
            if not pd.isna(record[self.c.COLS.END_YEAR]):
                time_frame = record[self.c.COLS.END_YEAR] - now.year
                if (time_frame <= 15) & (time_frame > 5):
                    time_frame_list.append('mid')
                elif (time_frame <= 30) & (time_frame > 15):
                    time_frame_list.append('long')
                elif time_frame <= 5:
                    time_frame_list.append('short')
                else:
                    time_frame_list.append(None)
            else:
                time_frame_list.append(None)
        self.data[self.c.COLS.TIME_FRAME] = time_frame_list

    def _find_target(self, row: pd.Series)-> pd.DataFrame:
        """
        Find the target that corresponds to a given row. If there are multiple targets available, filter them.

        :return: returns records from the input data, which contains company and target information, that meet specific
        criteria. For example, record of greatest emissions_in_scope
        """

        # Find all targets that correspond to the given row
        target_data = self.data[(self.data[self.c.COLS.COMPANY_NAME] == row[self.c.COLS.COMPANY_NAME]) &
                                (self.data[self.c.COLS.TIME_FRAME] == row[self.c.COLS.TIME_FRAME]) &
                                (self.data[self.c.COLS.SCOPE_CATEGORY] == row[self.c.COLS.SCOPE_CATEGORY])].copy()
        if len(target_data) == 0:
            # If there are no targets, we'll return the original row
            return row
        elif len(target_data) == 1:
            # If there's exactly one target, we'll return that target
            return target_data.iloc[0]
        else:
            # We prefer targets with higher emissions in scope
            if target_data.iloc[0][self.c.COLS.SCOPE_CATEGORY] == self.c.VALUE_SCOPE_CATEGORY_S1S2:
                target_data = target_data[
                    target_data[self.c.COLS.GHG_SCOPE12] == target_data[
                        self.c.COLS.GHG_SCOPE12].max()].copy()
            elif target_data.iloc[0][self.c.COLS.SCOPE_CATEGORY] == self.c.VALUE_SCOPE_CATEGORY_S3:
                target_data = target_data[
                    target_data[self.c.COLS.GHG_SCOPE3] == target_data[
                        self.c.COLS.GHG_SCOPE3].max()].copy()
            if len(target_data) == 1:
                return target_data.iloc[0]

            # We prefer targets with higher base years
            target_data = target_data[
                target_data[self.c.COLS.BASE_YEAR] == target_data[self.c.COLS.BASE_YEAR].max()].copy()
            if len(target_data) == 1:
                return target_data.iloc[0]

            # We pick abs over int
            if len(target_data[target_data[self.c.COLS.TARGET_REFERENCE_NUMBER].str.lower().str.startswith("abs")]) > 0:
                target_data = target_data[
                    target_data[self.c.COLS.TARGET_REFERENCE_NUMBER].str.lower().str.startswith("abs")].copy()
            if len(target_data) == 1:
                return target_data.iloc[0]

            # There are more than 1 targets, so we'll average them out
            target_data[self.c.COLS.REDUCTION_AMBITION] = target_data[self.c.COLS.REDUCTION_AMBITION].mean()
            return target_data.iloc[0]

    def group_targets(self):
        """
        Group the targets and create the 6 field grid (short, mid, long * s1s2, s3).
        Group valid targets by category & filter multiple targets#
        Input: a list of valid targets for each company:
        For each company:

        Group all valid targets based on scope (S1+S2 / S3) and time frame (short / mid / long-term) into 6 categories.

        For each category: if more than 1 target is available, filter based on the following criteria
        -- Highest boundary coverage
        -- Latest base year
        -- Target type: Absolute over intensity
        -- If all else is equal: average the ambition of targets
        """
        grid_columns = [self.c.COLS.COMPANY_NAME, self.c.COLS.TIME_FRAME, self.c.COLS.SCOPE_CATEGORY]
        companies = self.data[self.c.COLS.COMPANY_NAME].unique()
        scopes = [self.c.VALUE_SCOPE_CATEGORY_S1S2, self.c.VALUE_SCOPE_CATEGORY_S3]
        empty_columns = [column for column in self.data.columns if column not in grid_columns]
        extended_data = pd.DataFrame(
            list(itertools.product(*[companies, self.c.VALUE_TIME_FRAMES, scopes] + [[None]] * len(empty_columns))),
            columns=grid_columns + empty_columns)
        # We always include all company specific data
        company_columns = [column for column in self.c.COLS.COMPANY_COLUMNS if column in extended_data.columns]
        for company in companies:
            for column in company_columns:
                extended_data.loc[extended_data[self.c.COLS.COMPANY_NAME] == company, column] = \
                    self.data[self.data[self.c.COLS.COMPANY_NAME] == company][column].mode() # removed ".iloc[0]" kept receiving an index error
        extended_data = extended_data.apply(lambda row: self._find_target(row), axis=1)
        self.data = extended_data


    def creating_records_scope_timeframe(self):
        '''
        Create S1+S2 and S3 scopes for records that have an empty scope
        '''
        scopeless_data_s1s2 = self.data[pd.isna(self.data[self.c.COLS.SCOPE_CATEGORY])].copy()
        scopeless_data_3 = self.data[pd.isna(self.data[self.c.COLS.SCOPE_CATEGORY])].copy()

        index_to_drop = self.data[pd.isna(self.data[self.c.COLS.SCOPE_CATEGORY])].index
        self.data.drop(index_to_drop, inplace=True)

        scopeless_data_s1s2[self.c.COLS.SCOPE_CATEGORY] = 's1s2'
        scopeless_data_3[self.c.COLS.SCOPE_CATEGORY] = 's3'
        self.data = pd.concat([self.data, scopeless_data_s1s2, scopeless_data_3])


        timeframe_data_short = self.data[pd.isna(self.data[self.c.COLS.TIME_FRAME])].copy()
        timeframe_data_mid = self.data[pd.isna(self.data[self.c.COLS.TIME_FRAME])].copy()
        timeframe_data_long = self.data[pd.isna(self.data[self.c.COLS.TIME_FRAME])].copy()

        index_to_drop = self.data[pd.isna(self.data[self.c.COLS.TIME_FRAME])].index
        self.data.drop(index_to_drop, inplace=True)

        timeframe_data_short[self.c.COLS.TIME_FRAME] = 'short'
        timeframe_data_mid[self.c.COLS.TIME_FRAME] = 'mid'
        timeframe_data_long[self.c.COLS.TIME_FRAME] = 'long'



        self.data = pd.concat([self.data, scopeless_data_s1s2, scopeless_data_3,timeframe_data_short,timeframe_data_mid,
                               timeframe_data_long])

        self.data.reset_index(drop=True, inplace=True)
        self.data.drop(self.data[pd.isna(self.data[self.c.COLS.TIME_FRAME])].index, inplace=True)



    def combining_records(self):
        '''
        Combines both dataframes together. The company_data and the portfolio data that filtered out companies.
        :return:
        '''
        for company_remove in self.data['company_name'].unique():
            self.company_data.drop(self.company_data[self.company_data['company_name'] == company_remove].index.values, inplace=True)
        # self.data = pd.merge(left=self.company_data, right=self.data, how='outer', on=['company_name'])
        self.data = pd.concat([self.company_data, self.data], ignore_index=True, sort=False)

# Testing
# data = pd.read_excel('C:/Projects/SBTi/testing.xlsx')
# company_data = pd.read_excel('C:/Projects/SBTi/company_data.xlsx')
# data.drop(columns='Unnamed: 0',inplace=True)
# company_data.drop(columns='Unnamed: 0',inplace=True)
# x = TargetValuationProtocol(data,company_data)
# x.test_target_type()
# x.data[c.COLS.SCOPE] = x.data[c.COLS.SCOPE].str.lower()
# x.data[c.COLS.SCOPE_CATEGORY] = x.data.apply(
#     lambda row: c.SCOPE_MAP[row[c.COLS.SCOPE]], axis=1)#
# x.test_boundary_coverage()
# x.test_target_process()
# x.test_end_year()
# x.time_frame()
# x.group_targets()
# x.combining_records()
# x.creating_records_scope_timeframe()








import datetime
import itertools
import pandas as pd
from typing import Type, List
from SBTi.configs import PortfolioAggregationConfig
import logging


class TargetValuationProtocol:

    def __init__(self, data: pd.DataFrame, company_data: pd.DataFrame,
                 config: Type[PortfolioAggregationConfig] = PortfolioAggregationConfig):
        self.data = data
        self.data_backup = data.copy()
        self.c = config
        self.company_data = company_data
        self.logger = logging.getLogger(__name__)

    def target_valuation_protocol(self) -> pd.DataFrame:
        '''
        Runs the target valuation protcol by calling on the four required steps

        :rtype: list
        :return: a list of six columns containing dataframes in each one
        '''
        self.test_target_type()
        self.test_missing_fields(self.data, self.c.COLS.REQUIRED_TARGETS)
        self.test_missing_fields(self.company_data, self.c.COLS.REQUIRED_COMPANY)
        self.data[self.c.COLS.SCOPE] = self.data[self.c.COLS.SCOPE].str.lower()
        self.data[self.c.COLS.SCOPE_CATEGORY] = self.data.apply(
            lambda row: self.c.SCOPE_MAP[row[self.c.COLS.SCOPE]], axis=1)
        self.split_s1s2s3()
        self.convert_s1_s2_into_s1s2()
        self.test_boundary_coverage()
        self.test_target_process()
        self.test_end_year()
        self.time_frame()
        self.group_targets()
        self.data = self.combine_records()
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

    def test_missing_fields(self, data_set, required_columns):
        """
        When a required field is missing (that we need to do calculations later on), we'll delete the whole target.
        :return:
        """
        for column in required_columns:
            len_old = len(data_set)
            data_set = data_set[data_set[column].notna()]
            if len_old != len(data_set):
                self.logger.warning("One or more targets have been deleted due to null values in column: {}".format(
                    column))

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

        self.data[self.c.COLS.TARGET_REFERENCE_NUMBER] = self.data[self.c.COLS.TARGET_REFERENCE_NUMBER].astype(str)
        self.data[self.c.COLS.INTENSITY_METRIC] = self.data[self.c.COLS.INTENSITY_METRIC].astype(str)
        self.data[self.c.COLS.TARGET_REFERENCE_NUMBER] = self.data[self.c.COLS.TARGET_REFERENCE_NUMBER].str.lower()
        self.data[self.c.COLS.INTENSITY_METRIC] = self.data[self.c.COLS.INTENSITY_METRIC].str.lower()
        for index, record in self.data.iterrows():
            if not pd.isna(record[self.c.COLS.TARGET_REFERENCE_NUMBER]):
                if 'abs' in record[self.c.COLS.TARGET_REFERENCE_NUMBER]:
                    index_list.append(index)
                elif 'int' in record[self.c.COLS.TARGET_REFERENCE_NUMBER]:
                    if not pd.isna(record[self.c.COLS.INTENSITY_METRIC]):
                        if 'other' not in record[self.c.COLS.INTENSITY_METRIC]:
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
                    if record[1][self.c.COLS.COVERAGE_S1] > 0.95:
                        index.append(record[0])
                    else:
                        index.append(record[0])
                        self.data.at[record[0], self.c.COLS.REDUCTION_AMBITION] = \
                            self.data[self.c.COLS.REDUCTION_AMBITION].loc[record[0]] * \
                            (self.data[self.c.COLS.COVERAGE_S1].loc[record[0]])
                elif 's3' in record[1][self.c.COLS.SCOPE_CATEGORY]:
                    if record[1][self.c.COLS.COVERAGE_S3] > 0.67:
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

    def convert_s1_s2_into_s1s2(self):
        s1_mask = self.data[self.c.COLS.SCOPE] == 's1'
        s1 = self.data[s1_mask]
        s1_delete_mask = (s1_mask & (
                self.data[self.c.COLS.COVERAGE_S1].isna() | self.data[self.c.COLS.BASEYEAR_GHG_S1].isna() |
                self.data[self.c.COLS.BASEYEAR_GHG_S2].isna()))
        coverage_percentage = s1[self.c.COLS.COVERAGE_S1] * s1[self.c.COLS.BASEYEAR_GHG_S1] / (
                s1[self.c.COLS.BASEYEAR_GHG_S1] + s1[self.c.COLS.BASEYEAR_GHG_S2])
        self.data.loc[s1_mask, [self.c.COLS.COVERAGE_S1, self.c.COLS.COVERAGE_S2]] = coverage_percentage
        self.data = self.data[~s1_delete_mask]

        s2_mask = self.data[self.c.COLS.SCOPE] == 's2'
        s2 = self.data[s2_mask]
        s2_delete_mask = (s2_mask & (
                self.data[self.c.COLS.COVERAGE_S2].isna() | self.data[self.c.COLS.BASEYEAR_GHG_S1].isna() |
                self.data[self.c.COLS.BASEYEAR_GHG_S2].isna()))
        coverage_percentage = s2[self.c.COLS.COVERAGE_S2] * s2[self.c.COLS.BASEYEAR_GHG_S2] / (
                s2[self.c.COLS.BASEYEAR_GHG_S1] + s2[self.c.COLS.BASEYEAR_GHG_S2])
        self.data.loc[s2_mask, [self.c.COLS.COVERAGE_S1, self.c.COLS.COVERAGE_S2]] = coverage_percentage
        self.data = self.data[~s2_delete_mask]

    def split_s1s2s3(self):
        '''
        If there is a s1s2s3 scope, split it into two targets with s1s2 and s3
        '''
        s1s2s3_mask = self.data[self.c.COLS.SCOPE_CATEGORY] == self.c.VALUE_SCOPE_CATEGORY_S1S2S3
        s1s2s3 = self.data[s1s2s3_mask]
        self.data = self.data[~s1s2s3_mask]
        for _, row in s1s2s3.iterrows():
            if (pd.isnull(row[self.c.COLS.BASEYEAR_GHG_S1]) or pd.isnull(row[self.c.COLS.BASEYEAR_GHG_S2])) and \
                    (row[self.c.COLS.COVERAGE_S1] != row[self.c.COLS.COVERAGE_S2]):
                pass
            else:
                s1s2 = row.copy()
                s1s2[self.c.COLS.SCOPE_CATEGORY] = self.c.VALUE_SCOPE_CATEGORY_S1S2
                if pd.isnull(s1s2[self.c.COLS.BASEYEAR_GHG_S1]) or pd.isnull(s1s2[self.c.COLS.BASEYEAR_GHG_S2]) or \
                    s1s2[self.c.COLS.BASEYEAR_GHG_S1] + s1s2[self.c.COLS.BASEYEAR_GHG_S2] == 0:
                    pass
                else:
                    coverage_percentage = (s1s2[self.c.COLS.COVERAGE_S1] * s1s2[self.c.COLS.BASEYEAR_GHG_S1] +
                                           s1s2[self.c.COLS.COVERAGE_S2] * s1s2[self.c.COLS.BASEYEAR_GHG_S2]) / \
                                          (s1s2[self.c.COLS.BASEYEAR_GHG_S1] + s1s2[self.c.COLS.BASEYEAR_GHG_S2])
                    s1s2[self.c.COLS.COVERAGE_S1] = coverage_percentage
                    s1s2[self.c.COLS.COVERAGE_S2] = coverage_percentage
                if not pd.isnull(coverage_percentage):
                    self.data = self.data.append(s1s2).reset_index(drop=True)
            if pd.isnull(row[self.c.COLS.COVERAGE_S3]):
                pass
            else:
                s3 = row.copy()
                s3[self.c.COLS.SCOPE_CATEGORY] = self.c.VALUE_SCOPE_CATEGORY_S3
                self.data = self.data.append(s3).reset_index(drop=True)

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

    def _find_target(self, row: pd.Series, target_columns: List[str]) -> pd.Series:
        """
        Find the target that corresponds to a given row. If there are multiple targets available, filter them.

        :return: returns records from the input data, which contains company and target information, that meet specific
        criteria. For example, record of greatest emissions_in_scope
        """

        # Find all targets that correspond to the given row
        target_data = self.data[(self.data[self.c.COLS.COMPANY_ID] == row[self.c.COLS.COMPANY_ID]) &
                                (self.data[self.c.COLS.TIME_FRAME] == row[self.c.COLS.TIME_FRAME]) &
                                (self.data[self.c.COLS.SCOPE_CATEGORY] == row[self.c.COLS.SCOPE_CATEGORY])].copy()
        if len(target_data) == 0:
            # If there are no targets, we'll return the original row
            return row
        elif len(target_data) == 1:
            # If there's exactly one target, we'll return that target
            return target_data[target_columns].iloc[0]
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
                return target_data[target_columns].iloc[0]

            # We prefer targets with higher base years
            target_data = target_data[
                target_data[self.c.COLS.BASE_YEAR] == target_data[self.c.COLS.BASE_YEAR].max()].copy()
            if len(target_data) == 1:
                return target_data[target_columns].iloc[0]

            # We pick abs over int
            if len(target_data[target_data[self.c.COLS.TARGET_REFERENCE_NUMBER].str.lower().str.startswith("abs")]) > 0:
                target_data = target_data[
                    target_data[self.c.COLS.TARGET_REFERENCE_NUMBER].str.lower().str.startswith("abs")].copy()
            if len(target_data) == 1:
                return target_data[target_columns].iloc[0]

            # There are more than 1 targets, so we'll average them out
            target_data[self.c.COLS.REDUCTION_AMBITION] = target_data[self.c.COLS.REDUCTION_AMBITION].mean()
            return target_data[target_columns].iloc[0]

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
        grid_columns = [self.c.COLS.COMPANY_ID, self.c.COLS.TIME_FRAME, self.c.COLS.SCOPE_CATEGORY]
        # These are columns that do apear in the target data, but should be exclusive to the company data
        # TODO: Check if we can remove this earlier on/make sure it's never in there
        company_columns = [self.c.COLS.COMPANY_NAME]
        companies = self.company_data[self.c.COLS.COMPANY_ID].unique()
        scopes = [self.c.VALUE_SCOPE_CATEGORY_S1S2, self.c.VALUE_SCOPE_CATEGORY_S3, self.c.VALUE_SCOPE_CATEGORY_S1S2S3]
        empty_columns = [column for column in self.data.columns if column not in grid_columns + company_columns]
        extended_data = pd.DataFrame(
            list(itertools.product(*[companies, self.c.VALUE_TIME_FRAMES, scopes] + [[None]] * len(empty_columns))),
            columns=grid_columns + empty_columns)

        target_columns = extended_data.columns
        self.data = self.combine_records()
        self.data = extended_data.apply(lambda row: self._find_target(row, target_columns), axis=1)

    def combine_records(self):
        '''
        Combines both dataframes together. The company_data and the portfolio data that filtered out companies.
        :return:
        '''
        return pd.merge(left=self.company_data, right=self.data, how='outer', on=['company_id'])

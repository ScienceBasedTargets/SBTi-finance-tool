import pandas as pd
from typing import List
from SBTi.configs import ColumnsConfig


class TargetValuationProtocol:

    def __init__(self, data: pd.DataFrame, config: ColumnsConfig = ColumnsConfig):
        self.data = data
        self.c = config

    def target_valuation_protocol(self):
        '''
        Runs the target valuation protcol by calling on the four required steps

        :rtype: list, dataframe
        :return: a list of six columns containing dataframes in each one
        '''

        self.test_target_type()
        self.test_boundary_coverage()
        self.test_target_process()
        return self.group_valid_target()

    def test_target_type(self):
        """
        Test on target type and only allow only GHG emission reduction targets (absolute or intensity based).

        :param:
        :type:

        :rtype:
        :return:
        """
        index = []
        for record in self.data.iterrows():
            if not pd.isna(record[1][self.c.TARGET_REFERENCE_NUMBER]):
                if 'int' in record[1][self.c.TARGET_REFERENCE_NUMBER].lower():
                    index.append(record[0])
                elif 'abs' in record[1][self.c.TARGET_REFERENCE_NUMBER].lower():
                    index.append(record[0])
        self.data = self.data.loc[index]

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


        :param :
        :type :

        :rtype:
        :return:
        '''

        # Option 1
        index = []
        # data.reset_index(inplace=True, drop=True)
        for record in self.data.iterrows():
            if not pd.isna(record[1][self.c.SCOPE]):
                if 'Scope 1+2' in record[1][self.c.SCOPE]:
                    if record[1][self.c.EMISSIONS_IN_SCOPE] > 95:
                        index.append(record[0])
                elif 'Scope 3' in record[1][self.c.SCOPE]:
                    if record[1][self.c.EMISSIONS_IN_SCOPE] > 67:
                        index.append(record[0])
        self.data = self.data.loc[index]

    def test_target_process(self):
        '''
        Test on target process
        If target process is 100%, the target is invalid (only forward looking targets allowed)
        Output: a list of valid targets per company

        Target progress: the percentage of the target already achieved


        :param:
        :type:

        :rtype:
        :return:
        '''

        index = []
        for record in self.data.iterrows():
            if not pd.isna(record[1][self.c.ACHIEVED_EMISSIONS]):
                if record[1][self.c.ACHIEVED_EMISSIONS] != 100:
                    index.append(record[0])
        self.data = self.data.loc[index]

    def time_frame(self):
        '''
        Time frame is forward looking: target year - current year. Less than 5y = short, between 5 and 15 is mid, 15 to 30 is long

        :param:
        :type:

        :rtype:
        :return:
        '''
        # Hard coded year
        current_year = 2020
        time_frame_list = []
        for index, record in self.data.iterrows():
            if not pd.isna(record[self.c.TARGET_YEAR]):
                time_frame = record[self.c.TARGET_YEAR] - current_year
                if (time_frame < 15) & (time_frame > 5):
                    time_frame_list.append('mid')
                elif (time_frame < 30) & (time_frame > 15):
                    time_frame_list.append('long')
                elif time_frame < 5:
                    time_frame_list.append('short')
                else:
                    time_frame_list.append(None)
            else:
                time_frame_list.append(None)
        self.data[self.c.TIME_FRAME] = time_frame_list

    def group_valid_target(self) -> List[pd.DataFrame]:
        '''
        Group valid targets by category & filter multiple targets#
        Input: a list of valid targets for each company:
        For each company:

        Group all valid targets based on scope (S1+S2 / S3) and time frame (short / mid / long-term) into 6 categories.

        For each category: if more than 1 target is available, filter based on the following criteria
        -- Highest boundary coverage
        -- Latest base year
        -- Target type: Absolute over intensity
        -- If all else is equal: average the ambition of targets

        :param:
        :type:

        :rtype: list, dataframe
        :return: a list of six categories, each one containing a dataframe.
        '''

        # Creates time frame
        self.time_frame()

        index_s1s2, index_s3 = [], []
        for index, record in self.data.iterrows():
            # Hard coded 1, hard coded scope name
            if not pd.isna(record[self.c.SCOPE]):
                if 'Scope 1+2' in record[self.c.SCOPE]:
                    index_s1s2.append(index)
                elif 'Scope 3' in record[self.c.SCOPE]:
                    index_s3.append(index)
        data_s1s2 = self.data.loc[index_s1s2].copy()
        data_s3 = self.data.loc[index_s3].copy()

        # # Creates 6 categories and filters each category if more then 1 target per company.
        data_s1s2_short = self.multiple_target_filter(data_s1s2[data_s1s2[self.c.TIME_FRAME] == 'short'])
        data_s1s2_mid = self.multiple_target_filter(data_s1s2[data_s1s2[self.c.TIME_FRAME] == 'mid'])
        data_s1s2_long = self.multiple_target_filter(data_s1s2[data_s1s2[self.c.TIME_FRAME] == 'long'])
        data_s3_short = self.multiple_target_filter(data_s3[data_s3[self.c.TIME_FRAME] == 'short'])
        data_s3_mid = self.multiple_target_filter(data_s3[data_s3[self.c.TIME_FRAME] == 'mid'])
        data_s3_long = self.multiple_target_filter(data_s3[data_s3[self.c.TIME_FRAME] == 'long'])

        data_s1s2_short_final = self.add_company_placeholder(data_s1s2_short)
        data_s1s2_mid_final = self.add_company_placeholder(data_s1s2_mid)
        data_s1s2_long_final = self.add_company_placeholder(data_s1s2_long)
        data_s3_short_final = self.add_company_placeholder(data_s3_short)
        data_s3_mid_final = self.add_company_placeholder(data_s3_mid)
        data_s3_long_final = self.add_company_placeholder(data_s3_long)

        return [data_s1s2_short_final, data_s1s2_mid_final, data_s1s2_long_final,
                data_s3_short_final, data_s3_mid_final, data_s3_long_final]

    def add_company_placeholder(self, data_category: pd.DataFrame) -> pd.DataFrame:
        '''
        Adds the additional companies, that did not meet the criteria to the list of
        categories but with the features as "NaN" values

        :param data_category: companies that made the criteria
        :type dataframe:

        :rtype: list, dataframe
        :return: a list of six categories, each one containing a dataframe.

        '''

        if data_category is not None:
            empty_company_name = self.data.drop(data_category.index)[self.c.COMPANY_NAME].values
            dictionary = {k: {
                self.c.COMPANY_NAME: empty_company_name[k]
            } for k in range(0, len(empty_company_name))}

            for key in dictionary.keys():
                for column in self.data.columns.drop(self.c.COMPANY_NAME):
                    dictionary[key][column] = None
            data_company_placeholder = pd.DataFrame.from_dict(dictionary, orient='index')
            frames = [data_category, data_company_placeholder]
            return pd.concat(frames)
        else:
            return data_category

    def multiple_target_filter(self, data: pd.DataFrame) -> pd.DataFrame:
        '''
        For each category: if more than 1 target is available, filter based on the following criteria
        -- Highest boundary coverage
        -- Latest base year
        -- Target type: Absolute over intensity
        -- If all else is equal: average the ambition of targets

        :param data: 1/6 predefined category
        :type data: dataframe

        :rtype: dataframe, dataframe
        :return: companies filtered based on criterias mentioned above
        '''

        if not len(data) == 0:

            # Checks last criteria "If all else is equal: average the ambition of targets"
            if not max(data.groupby([self.c.COMPANY_NAME, self.c.EMISSIONS_IN_SCOPE, self.c.BASE_YEAR,
                                     self.c.TARGET_REFERENCE_NUMBER]).size().values) == 1:
                groupby_value = data.groupby(
                    [self.c.COMPANY_NAME, self.c.EMISSIONS_IN_SCOPE, self.c.BASE_YEAR,
                     self.c.TARGET_REFERENCE_NUMBER]).size().values
                index_all_category_equal = [i for i, x in enumerate(groupby_value) if x != 1]
                company_all_category_equal = data.iloc[index_all_category_equal][self.c.COMPANY_NAME].values
                for company in company_all_category_equal:
                    data_company_all_category = data[data[self.c.COMPANY_NAME] == company]
                    average_ambition_of_target = round(
                        data_company_all_category[self.c.REDUCTION_FROM_BASE_YEAR].mean(), 2)
                    index_to_change = data[data[self.c.COMPANY_NAME] == company].index
                    for index in index_to_change:
                        data.at[index - 1, self.c.REDUCTION_FROM_BASE_YEAR] = average_ambition_of_target

            # Multiple Targets. Need to filter by: Highest boundary coverage, Latest base year, Target type: Absolute over intensity
            elif not max(data.groupby([self.c.COMPANY_NAME]).size().values) == 1:
                multiple_targets = data[self.c.COMPANY_NAME].value_counts()
                company_list = multiple_targets.index[:list(multiple_targets.values).index(1)]
                for company in company_list:
                    df = data[data[self.c.COMPANY_NAME] == company]
                    df_boundary_coverage = df[
                        df[self.c.EMISSIONS_IN_SCOPE] == max(df[self.c.EMISSIONS_IN_SCOPE])]

                    # Highest Boundary Coverage
                    if len(df_boundary_coverage) == 1:
                        data.drop(list(df.index), inplace=True)  # Drop Multiple Targets
                        data = data.append(df_boundary_coverage)  # Adds target with highest boundary coverage
                    else:
                        df_base_year = df[df[self.c.BASE_YEAR] == max(df[self.c.BASE_YEAR])]

                        # Latest Base Year
                        if len(df_base_year) == 1:
                            data.drop(list(df.index), inplace=True)  # Drop Multiple Targets
                            data = data.append(df_base_year)  # Adds target with highest boundary coverage
                        else:

                            # Target type: Absolute over intensity
                            index_to_keep = []
                            for record in df.iterrows():
                                if "abs" in record[1][self.c.TARGET_REFERENCE_NUMBER].lower():
                                    index_to_keep.append(record[0])

                            # Add record to data
                            if len(index_to_keep) == 1:
                                data.drop(list(df.index), inplace=True)  # Drop Multiple Targets
                                data = data.append(df.loc[index_to_keep])  # Adds target with Absolute

                            else:
                                '''
                                    Rare Exception to enter here:
                                    Example: Company A(Abs), Company A(Abs), Company A(Int)
                                    All Criteria Same: False
                                    Boundary Condition: True
                                    Base Year: True
                                    Target Reference: False ( Abs, Abs, Int)
                                    Can only happen if targets have multiple "Abs" with a "Int"
                                '''

                                # One record is chosen and "average the ambition of targets" is applied and remaining duplicate targets are dropped
                                targets_rare_exception = df[df.index.isin(index_to_keep)]
                                average_ambition_of_target = round(
                                    targets_rare_exception[self.c.REDUCTION_FROM_BASE_YEAR].mean(), 2)
                                data.drop(list(df.index[1:]), inplace=True)  # Drop Multiple Targets
                                data.at[targets_rare_exception.index[
                                            0], self.c.REDUCTION_FROM_BASE_YEAR] = average_ambition_of_target

            data = data.sort_values(by=[self.c.COMPANY_NAME, self.c.EMISSIONS_IN_SCOPE, self.c.BASE_YEAR,
                                        self.c.TARGET_REFERENCE_NUMBER],
                                    ascending=False)

            return data

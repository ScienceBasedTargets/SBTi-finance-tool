import pandas as pd


def input_data():
    """
    Reads in an excel file as input data

    :rtype: dataframe, dataframe
    :return: excel file as input data
    """

    return pd.read_excel("C:/Projects/SBTi/protocol/input_data/SBTi_FI_tool_data_sample v2.xlsx",
                       sheet_name ='Data Inputs',skiprows = 1)


def test_target_type(data):
    """
    Test on target type and only allow only GHG emission reduction targets (absolute or intensity based).

    :param data: input data
    :type data: dataframe

    :rtype: dataframe, dataframe
    :return: excel file as input data
    """

    return data[(data['Target reference number']==' Int 1') | (data['Target reference number']==' Abs 1')]


def test_boundary_coverage(data):
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


    :param data: input data
    :type data: dataframe

    :rtype: dataframe, dataframe
    :return: excel file as input data
    '''

    # Option 1
    index = []
    #data.reset_index(inplace=True, drop=True)
    for record in data.iterrows():
        if not pd.isna(record[1]['Scope']):
            if 'Scope 1 +2' in record[1]['Scope']:
                if record[1]['% emissions in Scope']>95:
                    index.append(record[0])
            elif 'Scope 1+2' in record[1]['Scope']:
                if record[1]['% emissions in Scope']>95:
                    index.append(record[0])
            elif 'Scope 3' in record[1]['Scope']:
                if record[1]['% emissions in Scope']>67:
                    index.append(record[0])
    return data.loc[index]


def test_target_process(data):
    '''
    Test on target process
    If target process is 100%, the target is invalid (only forward looking targets allowed)
    Output: a list of valid targets per company

    Target progress: the percentage of the target already achieved


    :param data: input data
    :type data: dataframe

    :rtype: dataframe, dataframe
    :return: excel file as input data
    '''

    index = []
    for record in data.iterrows():
        if not pd.isna(record[1]['% achieved (emissions)']):
            if record[1]['% achieved (emissions)']!=100:
                index.append(record[0])
    return data.loc[index]


def time_frame(data):
    '''
    Time frame is forward looking: target year - current year. Less than 5y = short, between 5 and 15 is mid, 15 to 30 is long

    :param data: input data
    :type data: dataframe

    :rtype: dataframe, dataframe
    :return: excel file as input data
    '''

    current_year = 2020; time_frame_list = [];
    for record in data.iterrows():
        if not pd.isna(record[1]['Target year']):
            time_frame = record[1]['Target year'] - current_year
            if (time_frame<15) & (time_frame>5):
                time_frame_list.append('mid')
            elif (time_frame<30) & (time_frame>15):
                time_frame_list.append('long')
            elif time_frame<5:
                time_frame_list.append('short')
            else:
                time_frame_list.append(None)
        else:
            time_frame_list.append(None)
     data['Time frame'] = time_frame_list
    return data


def group_valid_target(data):
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
    
    Output:
    A matrix of the six categories, with each max 1 target per company

    :param data: input data
    :type data: dataframe

    :rtype: list, list
    :return: a list of all 6 categories.
    '''

    # Creates time frame
    data = time_frame(data)

    index_s1s2 = []; index_s3 = [];
    for record in data.iterrows():
        if not pd.isna(record[1]['Scope']):
            if 'Scope 1 +2' in record[1]['Scope']:
                index_s1s2.append(record[0])
            elif 'Scope 1+2' in record[1]['Scope']:
                index_s1s2.append(record[0])
            elif 'Scope 3' in record[1]['Scope']:
                index_s3.append(record[0])
    data_s1s2 = data.loc[index_s1s2]
    data_s3 = data.loc[index_s3]

    # Creates 6 categories and filters each category if more then 1 target per company.
    data_s1s2_short = multiple_target_filter(data_s1s2[data_s1s2['Time frame']=='short'])
    data_s1s2_mid = multiple_target_filter(data_s1s2[data_s1s2['Time frame'] == 'mid'])
    data_s1s2_long = multiple_target_filter(data_s1s2[data_s1s2['Time frame'] == 'long'])
    data_s3_short = multiple_target_filter(data_s3[data_s3['Time frame']=='short'])
    data_s3_mid = multiple_target_filter(data_s3[data_s3['Time frame'] == 'mid'])
    data_s3_long = multiple_target_filter(data_s3[data_s3['Time frame'] == 'long'])

    return [data_s1s2_short,data_s1s2_mid,data_s1s2_long,data_s3_short,data_s3_mid,data_s3_long]


def multiple_target_filter(data):
    '''
    For each category: if more than 1 target is available, filter based on the following criteria
    -- Highest boundary coverage
    -- Latest base year
    -- Target type: Absolute over intensity
    -- If all else is equal: average the ambition of targets

    :param data: input data
    :type data: dataframe

    :rtype: dataframe, dataframe
    :return: excel file as input data
    '''

    if len(data)==0:
        return data
    else:
        data = data.sort_values(by=['company_name', '% emissions in Scope','Base year','Target reference number'], ascending=False)
        if max(data.groupby(['company_name', '% emissions in Scope', 'Base year', 'Target reference number']).size().values) == 1:
            return data
        else:
            groupby_value = data.groupby(['company_name', '% emissions in Scope','Base year','Target reference number']).size().values
            index_all_category_equal = [i for i, x in enumerate(groupby_value) if x != 1]
            company_all_category_equal = data.iloc[index_all_category_equal]['company_name'].values

            for company in company_all_category_equal:
                data_company_all_category = data[data['company_name'] == company]
                average_ambition_of_target = round(data_company_all_category['% reduction from base year'].mean(), 2)
                index_to_change = data[data['company_name'] == company].index
                for index in index_to_change:
                    data.at[index - 1, '% reduction from base year'] = average_ambition_of_target
            return data


def main():
    input_data = input_data()

    data = test_target_type(input_data)

    data = test_boundary_coverage(data)

    data = test_target_process(data)

    data = group_valid_target(data)
import pandas as pd
from pandas.api.types import is_string_dtype



class DataProvider:

    def __init__(self, input=None, path=None):
        self.input = input
        self.path = path

    def data_provider(self):
        '''
        Excel file will act as a temporary "data provider".

        :return: Dataframe
        '''

        return pd.read_excel("C:/Projects/SBTi/connector/InputFormat.xlsx", sheet_name=None, skiprows=1)


    def company_data(self):
        '''
        Records for the companies the client provided will be extracted from the data provider and returned

        A request is send to the data provider to return the following data for each company in the portfolio, based on company name/ company_ID

        Required: CDP_ACS_industry (industry classification, see also SR15 variable mapping"), GHG_scope12, GHG_scope3,
        Revenue, Market_cap, Enterprise_value, Total_assets, Cash_equivalents, country, industry, sector

        It should be easy to expand on this list at a later stage.

        :return: Data Frame
        '''

        data = self.data_provider()
        data = data['Company data']

        required_columns = ['company_name', 'company_ID', 'CDP_ACS_industry', 'country', 'industry', 'sector','GHG_scope12',
                            'GHG_scope3', 'Revenu', 'market_cap', 'enterprise_value', 'total_assets', 'cash_equivalents']

        data_frame = pd.DataFrame(columns=required_columns)

        for record in input_data.iterrows():
            data_frame = data_frame.append(data[(data['company_name'] == record[1]['Company_name']) &
                                                (data['company_ID'] == record[1]['Company_ID'])][required_columns],
                                           ignore_index=True)

        return data_frame


    def target_data(self):
        '''
        Input: portfolio (list of companies + company_ID)

        -A request is send to the data provider to return the following data for all available targets for each company in the portfolio, based on company name/ company_ID

        For each target the following data is requested:

        Required: Target classification, Scope, Coverage, Ambition, Base_year, end_year, Optional: start_year

        The format in which the data should be returned is clear in the documentation (examples).
        '''

        data = self.data_provider()
        data = data['Target data']

        required_columns = ['company_name', 'company_ID', 'Target_classification', 'Scope', 'coverage',
                            'reduction_ambition', 'base_year', 'end_year', 'start_year']

        data_frame = pd.DataFrame(columns=required_columns)

        for record in input_data.iterrows():
            data_frame = data_frame.append(data[(data['company_name'] == record[1]['Company_name']) &
                                                (data['company_ID'] == record[1]['Company_ID'])][required_columns],
                                           ignore_index=True)
        return data_frame





    def excel_connector(self):
        """
        Reads in an excel file as input data

        :rtype: dataframe, dataframe
        :return: excel file as input data
        """
        data = pd.read_excel(self.path, None, skiprows = 1)

        if self.validate_excel_file(data):
            return data
        else:
            print('Error: Incorrect Format')

    def validate_excel_file(self, data):
        """
        Validates the excel file is in the correct format

        :rtype: dataframe, dataframe
        :return: excel file as input data
        """
        if not self.validate_sheets(data):
            return False
        elif not self.validate_columns(data):
            return False
        else:
            return True


    def validate_sheets(self, data):
        """
        Validates the excel file sheets contains the Company and Target data

        :rtype: bolean value, <TRUE | FALSE>
        :return: excel file as input data
        """
        if ('company' in str(list(data.keys())).lower()) & ('target' in str(list(data.keys())).lower()):
            return True
        else:
            return False


    def validate_columns(self, data):
        """
        Validates the excel file columns and data type

        :rtype: bolean value, <TRUE | FALSE>
        :return: excel file as input data
        """

        sheets = ['Company data','Target data']

        for sheet in sheets:
            if sheet =='Company data':
                # True: string, False: integer
                required_columns = {'company_name': True, 'company_ID': True, 'CDP_ACS_industry': True, 'country': True,
                                    'industry': True,
                                    'sector': True, 'GHG_scope12': False, 'GHG_scope3': False, 'Revenu': False,
                                    'market_cap': False,
                                    'enterprise_value': False, 'total_assets': False, 'cash_equivalents': False}
            else:
                # True: string, False: integer
                required_columns = {'company_name' : True, 'company_ID' : True, 'Target_classification' : True, 'Scope' : True,
                                    'coverage' : False, 'reduction_ambition' : False, 'base_year': False, 'end_year':False,
                                    'start_year': False, 'SBTi_status':False}

            for column in required_columns.keys():
                if column not in data[sheet].columns:
                    print("Error: \n Column: {} \t Error Message: Missing".format(column))
                    return False
                else:
                    if not is_string_dtype(data['Company data'][column]) == required_columns[column]:
                        print("Error: \n Column: {} \t Error Message: Incorrect Data Type".format(column))
                        return False
        return True





# Testing
input_data = pd.read_excel("C:/Projects/SBTi/connector/InputFormat.xlsx", sheet_name='User input')[['Company_name','Company_ID']]
x = DataProvider(input_data)
x.company_data()
x.target_data()

# Testing Excel Connector
x = DataProvider(path = "C:/Projects/SBTi/connector/InputFormat.xlsx")
x.excel_connector()


import pandas as pd
from pandas.api.types import is_string_dtype
from SBTi.configs import ColumnsConfig


class DataProvider:

    def __init__(self, input=None, path=None, config: ColumnsConfig = ColumnsConfig):
        self.input_data = input
        self.path = path
        self.c = config


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


        required_columns = [self.c.COMPANY_NAME, self.c.COMPANY_ID, self.c.CDP_ACS_INDUSTRY, self.c.COUNTRY,
                            self.c.INDUSTRY, self.c.SECTOR, self.c.GHG_SCOPE12, self.c.GHG_SCOPE3, self.c.REVENU,
                            self.c.MARKET_CAP, self.c.ENTERPRISE_VALUE, self.c.TOTAL_ASSETS, self.c.CASH_EQUIVALENTS]

        data_frame = pd.DataFrame(columns=required_columns)

        for record in self.input_data.iterrows():
            data_frame = data_frame.append(data[(data[self.c.COMPANY_NAME] == record[1]['Company_name']) &
                                                (data[self.c.COMPANY_ID] == record[1]['Company_ID'])][required_columns],
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

        required_columns = [self.c.COMPANY_NAME, self.c.COMPANY_ID, self.c.TARGET_CLASSIFICATION, self.c.SCOPE,
                            self.c.COVERAGE, self.c.REDUCTION_AMBITION, self.c.BASE_YEAR, self.c.END_YEAR,
                            self.c.START_YEAR]

        data_frame = pd.DataFrame(columns=required_columns)

        for record in self.input_data.iterrows():
            data_frame = data_frame.append(data[(data[self.c.COMPANY_NAME] == record[1]['Company_name']) &
                                                (data[self.c.COMPANY_ID] == record[1]['Company_ID'])][required_columns],
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

        return self.validate_sheets(data) and self.validate_columns(data)




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
                required_columns = {self.c.COMPANY_NAME: True, self.c.COMPANY_ID: True, self.c.CDP_ACS_INDUSTRY: True,
                                    self.c.COUNTRY: True, self.c.INDUSTRY: True, self.c.SECTOR: True, self.c.GHG_SCOPE12: False, self.c.GHG_SCOPE3: False,
                                    self.c.REVENU: False, self.c.MARKET_CAP: False, self.c.ENTERPRISE_VALUE: False, self.c.TOTAL_ASSETS: False,
                                    self.c.CASH_EQUIVALENTS: False}
            else:
                # True: string, False: integer
                required_columns = {self.c.COMPANY_NAME: True, self.c.COMPANY_ID: True, self.c.TARGET_CLASSIFICATION : True,
                                    self.c.SCOPE : True, self.c.COVERAGE : False, self.c.REDUCTION_AMBITION : False, self.c.BASE_YEAR: False,
                                    self.c.END_YEAR : False, self.c.START_YEAR: False, self.c.SBTI_STATUS: False}
            for column in required_columns.keys():
                if column not in data[sheet].columns:
                    print("Error: \n Column: {} \t Error Message: Missing".format(column))
                    return False
                else:
                    if not is_string_dtype(data['Company data'][column]) == required_columns[column]:
                        print("Error: \n Column: {} \t Error Message: Incorrect Data Type".format(column))
                        return False
        return True


# # Testing
# input_data = pd.read_excel("C:/Projects/SBTi/connector/InputFormat.xlsx", sheet_name='User input')[['Company_name','Company_ID']]
# x = DataProvider(input_data)
# x.company_data()
# x.target_data()
#
# # Testing Excel Connector
# x = DataProvider(path = "C:/Projects/SBTi/connector/InputFormat.xlsx")
# x.excel_connector()





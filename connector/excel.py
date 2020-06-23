import pandas as pd
from pandas.api.types import is_string_dtype


class ExcelConnector:

    def __init__(self, path):
        self.path = path


    def input_data(self):
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


# Test
# x = ExcelConnector("C:/Projects/SBTi/connector/InputFormat.xlsx")
# df = x.input_data()

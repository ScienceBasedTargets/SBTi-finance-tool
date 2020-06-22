import pandas as pd


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


# Test
# x = ExcelConnector("C:/Projects/SBTi/connector/InputFormat.xlsx")
# df = x.input_data()

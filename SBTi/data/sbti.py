from typing import List, Type
import requests
import pandas as pd
import warnings


from SBTi.configs import PortfolioCoverageTVPConfig
from SBTi.interfaces import IDataProviderCompany


class SBTi:
    """
    Data provider skeleton for SBTi. This class only provides the sbti_validated field for existing companies.
    """

    def __init__(
        self, config: Type[PortfolioCoverageTVPConfig] = PortfolioCoverageTVPConfig
    ):
        self.c = config
        # Fetch CTA file from SBTi website
        resp = requests.get(self.c.CTA_FILE_URL)
        # Write CTA file to disk
        with open(self.c.FILE_TARGETS, 'wb') as output:
            output.write(resp.content)
            print(f'Status code from fetching the CTA file: {resp.status_code}, 200 = OK')
        # Read CTA file into pandas dataframe
        # Suppress warning about openpyxl - check if this is still needed in the released version.
        warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
        self.targets = pd.read_excel(self.c.FILE_TARGETS)
        
    
    def filter_cta_file(self, targets):
        """
        Filter the CTA file to create a datafram that has on row per company with the columns "Action" and "Target"
        If Action = Target then only keep the rows where Target = Near-term.
        Validate ISIN and LEI.
        """
        # Regex patterns for ISIN and LEI
        isin_regex = r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$'
        lei_regex = r'^[0-9A-Z]{18}[0-9]{2}$'

        # Create a new dataframe with only the columns "Action" and "Target"
        targets = targets[[self.c.COL_COMPANY_NAME, self.c.COL_COMPANY_ISIN, self.c.COL_COMPANY_LEI, self.c.COL_ACTION, self.c.COL_TARGET]]
        #
        # Keep rows where Action = Target and Target = Near-term or Action = Committed
        df = targets[(targets[self.c.COL_ACTION] != self.c.VALUE_ACTION_TARGET) | (targets[self.c.COL_TARGET] == self.c.VALUE_TARGET_SET)]
        # Drop duplicates in the dataframe by waterfall. Do company name last due to risk of misspelled names
        df = pd.concat([df[~df[self.c.COL_COMPANY_LEI].isnull()].drop_duplicates(subset=self.c.COL_COMPANY_LEI, keep='first'), df[df[self.c.COL_COMPANY_LEI].isnull()]])
        df = pd.concat([df[~df[self.c.COL_COMPANY_ISIN].isnull()].drop_duplicates(subset=self.c.COL_COMPANY_ISIN, keep='first'), df[df[self.c.COL_COMPANY_ISIN].isnull()]])
        df.drop_duplicates(subset=self.c.COL_COMPANY_NAME, inplace=True)

        #validate ISIN
        ISIN_check = df[self.c.COL_COMPANY_ISIN].str.match(isin_regex)
        ISIN_check = ISIN_check.fillna(True)
        invalid_ISIN = df.loc[~ISIN_check, self.c.COL_COMPANY_NAME]
        for co in invalid_ISIN:
            print('invalid ISIN in CTA file: ', co)

        #validate LEI
        LEI_check =  df[self.c.COL_COMPANY_LEI].str.match(lei_regex)
        LEI_check = LEI_check.fillna(True)
        invalid_LEI = df.loc[~LEI_check, self.c.COL_COMPANY_NAME]
        for co in invalid_LEI:
            print('invalid LEI in CTA file: ', co)
            # Filter based on "Target" column
  
        return df
    
    def get_sbti_targets(
        self, companies: List[IDataProviderCompany], id_map: dict
    ) -> List[IDataProviderCompany]:
        """
        Check for each company if they have an SBTi validated target, first using the company LEI, 
        if available, and then using the ISIN.
        
        :param companies: A list of IDataProviderCompany instances
        :param id_map: A map from company id to a tuple of (ISIN, LEI)
        :return: A list of IDataProviderCompany instances, supplemented with the SBTi information
        """
        # Filter out information about targets
        self.targets = self.filter_cta_file(self.targets)

        for company in companies:
            isin, lei = id_map.get(company.company_id)
            # Check lei and length of lei to avoid zeros 
            if not lei.lower() == 'nan' and len(lei) > 3:
                targets = self.targets[
                    self.targets[self.c.COL_COMPANY_LEI] == lei
                ]
            elif not isin.lower() == 'nan':
                targets = self.targets[
                    self.targets[self.c.COL_COMPANY_ISIN] == isin
                ]
            else:
                continue
            if len(targets) > 0:
                company.sbti_validated = (
                    self.c.VALUE_TARGET_SET in targets[self.c.COL_TARGET].values
                )
        return companies

   
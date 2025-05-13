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

        fallback_err_log_statement = 'Will read older file from this package version'
        try:
            # Fetch CTA file from SBTi website
            resp = requests.get(self.c.CTA_FILE_URL)

            # If status code == 200 then write CTA file to disk
            if resp.ok:
                with open(self.c.FILE_TARGETS, 'wb') as output:
                    output.write(resp.content)
                    print(f'Status code from fetching the CTA file: {resp.status_code}, 200 = OK')
            else:
                print(f'Non-200 status code when fetching the CTA file from the SBTi website: {resp.status_code}')
                print(fallback_err_log_statement)

        except requests.exceptions.RequestException as e:
            print(f'Exception when fetching the CTA file from the SBTi website: {e}')
            print(fallback_err_log_statement)

        # Read CTA file into pandas dataframe
        warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
        self.targets = pd.read_excel(self.c.FILE_TARGETS)
        
        # Store processed targets for efficient lookups
        self.processed_targets = None

    def filter_cta_file(self, targets):
        """
        Process the CTA file to create a comprehensive mapping of companies
        with their target status, allowing for identification by any available
        identifier (ISIN, LEI, or company name) with priority: ISIN > LEI > company name.
       
        Uses the new CTA file structure from SBTi (2025) where column names are:
        - company_name: The name of the company
        - isin: The ISIN identifier
        - lei: The LEI identifier
        - near_term_status: The status of near-term targets
        - net_zero_status: The status of net-zero targets
       
        Valid target statuses are "Targets Set" and "Committed".
        "Commitment Expired" and other statuses are treated as "No target".
        
        Returns a filtered dataframe containing only companies with valid targets.
        """
        targets_copy = targets.copy()
       
        filtered_df = targets_copy[
            [
                'company_name',  
                'isin',          
                'lei',           
                'near_term_status',
                'net_zero_status'
            ]
        ]
       
        valid_statuses = ['Targets Set', 'Committed']
       
        # Create target status flags based on the near_term_status
        filtered_df.loc[:, 'has_target'] = filtered_df['near_term_status'].isin(valid_statuses)
        filtered_df.loc[:, 'target_status'] = filtered_df['near_term_status']
        filtered_df.loc[~filtered_df['has_target'], 'target_status'] = 'No target'
        filtered_df.loc[:, 'company_name_lower'] = filtered_df['company_name'].str.lower()
        
        # Companies identified by ISIN (highest priority)
        isin_df = filtered_df[~filtered_df['isin'].isnull()].copy()
        isin_df['identifier_type'] = 'ISIN'
        isin_df['identifier'] = isin_df['isin']
       
        # Companies identified by LEI (second priority)
        lei_df = filtered_df[~filtered_df['lei'].isnull()].copy()
        lei_df['identifier_type'] = 'LEI'
        lei_df['identifier'] = lei_df['lei']
       
        # Companies identified by name (lowest priority)
        name_df = filtered_df.copy()
        name_df['identifier_type'] = 'NAME'
        name_df['identifier'] = name_df['company_name_lower']
       
        # Combine all lookup dataframes
        all_lookups = pd.concat([isin_df, lei_df, name_df])
       
        # Set priority based on the order: ISIN > LEI > company name
        priority_order = {'ISIN': 0, 'LEI': 1, 'NAME': 2}
        all_lookups['priority'] = all_lookups['identifier_type'].map(priority_order)
       
        # Sort by priority and keep the highest priority record for each company
        all_lookups = all_lookups.sort_values('priority')
        all_lookups = all_lookups.drop_duplicates(subset=['company_name'], keep='first')
       
        # Store the processed targets
        self.processed_targets = all_lookups[['company_name', 'isin', 'lei', 'target_status', 'has_target', 'company_name_lower']]
        
        # Filter to only include companies with valid targets
        df_nt_targets = self.processed_targets[self.processed_targets['has_target']].copy()
        
        # Select only the necessary columns for downstream compatibility
        df_nt_targets = df_nt_targets[['company_name', 'isin', 'lei']]
        
        return df_nt_targets
    
    def get_sbti_targets(
        self, companies: List[IDataProviderCompany], id_map: dict
    ) -> List[IDataProviderCompany]:
        """
        Check for each company if they have an SBTi validated target using ISIN, LEI, or company name.
        Prioritization order: ISIN > LEI > company name.
        """
        # Process the targets if not already done
        if self.processed_targets is None:
            self.filter_cta_file(self.targets)
        
        # Extract validated targets for lookup
        validated_targets = self.processed_targets[self.processed_targets['has_target']]
        
        # Create sets for efficient lookups
        validated_isins = set(validated_targets[~validated_targets['isin'].isnull()]['isin'])
        validated_leis = set(validated_targets[~validated_targets['lei'].isnull()]['lei'])
        validated_names = set(validated_targets['company_name_lower'])
        
        # Check each company for target validation
        for company in companies:
            # Default to not validated
            company.sbti_validated = False
            
            # Get company identifiers
            isin, lei = id_map.get(company.company_id, ('nan', 'nan'))
            
            # Check if company has a valid target using any identifier
            # Priority: ISIN > LEI > company name
            
            # Check ISIN (highest priority)
            if not pd.isnull(isin) and str(isin).lower() != 'nan':
                if isin in validated_isins:
                    company.sbti_validated = True
            
            # If not validated by ISIN, check LEI
            if not company.sbti_validated and not pd.isnull(lei) and str(lei).lower() != 'nan' and len(str(lei)) > 3:
                if lei in validated_leis:
                    company.sbti_validated = True
            
            # If still not validated, check company name
            if not company.sbti_validated and hasattr(company, 'company_name') and company.company_name:
                company_name_lower = str(company.company_name).lower()
                if company_name_lower in validated_names:
                    company.sbti_validated = True
        
        return companies
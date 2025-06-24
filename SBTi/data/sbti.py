from typing import List, Type, Dict, Tuple, Optional
import requests
import pandas as pd
import warnings
import datetime
import re

from SBTi.configs import PortfolioCoverageTVPConfig
from SBTi.interfaces import IDataProviderCompany, IDataProviderTarget, EScope, ETimeFrames


class SBTi:
    """
    Data provider skeleton for SBTi. This class only provides the sbti_validated field for existing companies.
    Updated to DEFAULT to per-company format for TR Testing consistency.
    Enhanced to extract detailed target information when available.
    """

    def __init__(
        self, config: Type[PortfolioCoverageTVPConfig] = PortfolioCoverageTVPConfig
    ):
        self.c = config
        
        # DEFAULT TO PER-COMPANY FORMAT for consistency with TR Testing baseline
        # Override the config to ensure per-company format is used
        original_url = self.c.CTA_FILE_URL
        self.c.CTA_FILE_URL = "https://files.sciencebasedtargets.org/production/files/companies-excel.xlsx"
        

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
        # Suppress warning about openpyxl
        warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
        self.targets = pd.read_excel(self.c.FILE_TARGETS)
        
        # Detect and convert column format if needed
        self.targets = self._ensure_compatible_format(self.targets)
        
        print(f"CTA format: {getattr(self, 'format_type', 'unknown')} | Companies: {len(self.targets)}")

    def _detect_format(self, df):
        """
        Detect the format of the CTA file:
        - 'old': Original format with Title Case columns
        - 'new_company': New per-company format (one row per company) - PREFERRED
        - 'new_target': New per-target format (multiple rows per company)
        """
        # Check for key columns to determine format
        if 'Company Name' in df.columns:
            return 'old'
        elif 'company_name' in df.columns:
            # Distinguish between per-company and per-target formats
            if 'near_term_status' in df.columns:
                return 'new_company'  # PREFERRED FORMAT
            elif 'target_wording' in df.columns or 'row_entry_id' in df.columns:
                return 'new_target'
            else:
                # Default to per-company if we can't determine
                return 'new_company'
        else:
            raise ValueError("Unrecognized CTA file format")
    
    def _ensure_compatible_format(self, df):
        """
        Convert CTA file to the format expected by the configs
        OPTIMIZED FOR PER-COMPANY FORMAT
        """
        format_type = self._detect_format(df)
        
        if format_type in ['new_target', 'new_company']:
            # Map new format columns to old format for backward compatibility
            column_mapping = {
                'company_name': self.c.COL_COMPANY_NAME,
                'isin': self.c.COL_COMPANY_ISIN,
                'lei': self.c.COL_COMPANY_LEI,
                'action': self.c.COL_ACTION,
                'target': self.c.COL_TARGET,
                'date_published': self.c.COL_DATE_PUBLISHED
            }
            
            # Handle different format types
            if format_type == 'new_company':
                # Map near_term_status to create synthetic Action and Target columns
                if 'near_term_status' in df.columns:
                    df['action'] = df['near_term_status'].apply(
                        lambda x: 'Target' if x == 'Targets set' else 'Commitment'
                    )
                    df['target'] = df['near_term_status'].apply(
                        lambda x: 'Near-term' if x == 'Targets set' else None
                    )
            
            # Only rename columns that exist
            rename_dict = {}
            for new_col, old_col in column_mapping.items():
                if new_col in df.columns:
                    rename_dict[new_col] = old_col
            
            df = df.rename(columns=rename_dict)
            
            # Store format type for later use
            self.format_type = format_type
            
            # Keep additional columns for potential future use
            if 'sbti_id' in df.columns:
                df['SBTI_ID'] = df['sbti_id']
            if 'target_classification_short' in df.columns:
                df['Target Classification'] = df['target_classification_short']
            if 'scope' in df.columns:
                df['Scope'] = df['scope']
            if 'base_year' in df.columns:
                df['Base Year'] = df['base_year']
            if 'target_year' in df.columns:
                df['Target Year'] = df['target_year']
        else:
            self.format_type = 'old'
        
        return df

    def filter_cta_file(self, targets):
        """
        Filter the CTA file to create a dataframe that has one row per company
        with the columns "Action" and "Target".
        If Action = Target then only keep the rows where Target = Near-term.
        
        Handles all three formats: old, new per-company, and new per-target.
        """

        # Create a new dataframe with only the columns "Action" and "Target"
        # and the columns that are needed for identifying the company
        required_cols = [
            self.c.COL_COMPANY_NAME, 
            self.c.COL_COMPANY_ISIN, 
            self.c.COL_COMPANY_LEI, 
            self.c.COL_ACTION, 
            self.c.COL_TARGET
        ]
        
        # Only select columns that exist
        existing_cols = [col for col in required_cols if col in targets.columns]
        targets_filtered = targets[existing_cols].copy()
        
        # Keep rows where Action = Target and Target = Near-term 
        df_nt_targets = targets_filtered[
            (targets_filtered[self.c.COL_ACTION] == self.c.VALUE_ACTION_TARGET) & 
            (targets_filtered[self.c.COL_TARGET] == self.c.VALUE_TARGET_SET)]
        
        # For per-target format, we need to deduplicate at company level
        # since there can be multiple target rows per company
        if hasattr(self, 'format_type') and self.format_type == 'new_target':
            print("Processing per-target format - deduplicating companies...")
        
        # Drop duplicates in the dataframe by waterfall approach
        # LEI first, then ISIN, then company name
        identifier_cols = [self.c.COL_COMPANY_LEI, self.c.COL_COMPANY_ISIN, self.c.COL_COMPANY_NAME]
        
        for identifier_col in identifier_cols:
            if identifier_col in df_nt_targets.columns:
                # Drop duplicates based on this identifier, keeping first occurrence
                before_count = len(df_nt_targets)
                df_nt_targets = df_nt_targets.drop_duplicates(subset=[identifier_col], keep='first')
                after_count = len(df_nt_targets)
                if before_count != after_count and hasattr(self, 'format_type') and self.format_type == 'new_target':
                    print(f"   Deduplicated {before_count - after_count} entries using {identifier_col}")
        
        return df_nt_targets

    def get_company_targets(self, company_name: str = None, isin: str = None, lei: str = None):
        """
        Get all targets for a specific company.
        Only works with per-target format.
        
        :param company_name: Company name to search for
        :param isin: ISIN to search for
        :param lei: LEI to search for
        :return: DataFrame with all targets for the company
        """
        if hasattr(self, 'format_type') and self.format_type == 'new_target':
            if lei:
                return self.targets[self.targets['lei'] == lei]
            elif isin:
                return self.targets[self.targets['isin'] == isin]
            elif company_name:
                return self.targets[self.targets[self.c.COL_COMPANY_NAME] == company_name]
        return pd.DataFrame()  # Empty dataframe if not per-target format

    def get_companies(
        self, companies: List[IDataProviderCompany], id_map: Dict[str, Tuple[str, str]]
    ) -> List[IDataProviderCompany]:
        """
        Get company data from SBTi database and add sbti_validated field.
        
        :param companies: A list of IDataProviderCompany instances
        :param id_map: A map from company id to a tuple of (ISIN, LEI)
        :return: A list of IDataProviderCompany instances, supplemented with the SBTi information
        """
        # Filter targets for validation check
        filtered_targets = self.filter_cta_file(self.targets)
        
        # Track matching statistics for debugging
        matched_lei = matched_isin = matched_name = 0

        for company in companies:
            isin, lei = id_map.get(company.company_id, (None, None))
            
            # Skip if no identifiers
            if not isin and not lei and not company.company_name:
                continue
                
            # Check lei and length of lei to avoid zeros 
            if lei and not lei.lower() == 'nan' and len(str(lei)) > 3:
                targets = filtered_targets[
                    filtered_targets[self.c.COL_COMPANY_LEI] == lei
                ]
                if len(targets) > 0:
                    company.sbti_validated = True
                    matched_lei += 1
                    continue
                    
            if isin and not isin.lower() == 'nan':
                targets = filtered_targets[
                    filtered_targets[self.c.COL_COMPANY_ISIN] == isin
                ]
                if len(targets) > 0:
                    company.sbti_validated = True
                    matched_isin += 1
                    continue
                    
            # Try company name matching as fallback
            if company.company_name:
                targets = filtered_targets[
                    filtered_targets[self.c.COL_COMPANY_NAME].str.lower() == company.company_name.lower()
                ]
                if len(targets) > 0:
                    company.sbti_validated = True
                    matched_name += 1
                    continue
            
            # No match found
            company.sbti_validated = False

        total_matched = matched_lei + matched_isin + matched_name
        print(f"SBTi matches: {total_matched}/{len(companies)} (LEI: {matched_lei}, ISIN: {matched_isin}, Name: {matched_name})")
        
        return companies

    def get_sbti_targets(
        self, companies: List[IDataProviderCompany], id_map: Dict[str, Tuple[str, str]]
    ) -> Tuple[List[IDataProviderCompany], Dict[str, List[IDataProviderTarget]]]:
        """
        Enhanced version that returns both validation status AND target details when available.
        
        :param companies: A list of IDataProviderCompany instances
        :param id_map: A map from company id to a tuple of (ISIN, LEI)
        :return: A tuple of:
            - List of IDataProviderCompany instances, supplemented with the SBTi information
            - Dictionary mapping company_id to list of IDataProviderTarget instances
        """
        # Store original unfiltered targets for detailed extraction
        original_targets = self.targets.copy()
        
        # Filter out information about targets for validation check
        self.targets = self.filter_cta_file(self.targets)
        
        # Dictionary to store detailed target data
        sbti_target_data = {}

        for company in companies:
            isin, lei = id_map.get(company.company_id, (None, None))
            
            # Skip if no identifiers
            if not isin and not lei:
                continue
                
            # Check lei and length of lei to avoid zeros 
            if lei and not lei.lower() == 'nan' and len(str(lei)) > 3:
                targets = self.targets[
                    self.targets[self.c.COL_COMPANY_LEI] == lei
                ]
                # Get all targets for detailed extraction
                if hasattr(self, 'format_type') and self.format_type == 'new_target':
                    all_company_targets = original_targets[
                        original_targets[self.c.COL_COMPANY_LEI if self.c.COL_COMPANY_LEI in original_targets.columns else 'lei'] == lei
                    ]
            elif isin and not isin.lower() == 'nan':
                targets = self.targets[
                    self.targets[self.c.COL_COMPANY_ISIN] == isin
                ]
                # Get all targets for detailed extraction
                if hasattr(self, 'format_type') and self.format_type == 'new_target':
                    all_company_targets = original_targets[
                        original_targets[self.c.COL_COMPANY_ISIN if self.c.COL_COMPANY_ISIN in original_targets.columns else 'isin'] == isin
                    ]
            else:
                continue
                
            if len(targets) > 0:
                company.sbti_validated = True
                
                # Extract detailed target information if available
                if hasattr(self, 'format_type') and self.format_type == 'new_target' and len(all_company_targets) > 0:
                    targets_list = []
                    for _, target_row in all_company_targets.iterrows():
                        target_data = {
                            'company_id': company.company_id,
                            'target_type': target_row.get('target_classification_short', 'Unknown'),
                            'scope': target_row.get('scope', 'Unknown'),
                            'base_year': target_row.get('base_year'),
                            'target_year': target_row.get('target_year'),
                        }
                        targets_list.append(target_data)
                    sbti_target_data[company.company_id] = targets_list
            else:
                company.sbti_validated = False

        return companies, sbti_target_data

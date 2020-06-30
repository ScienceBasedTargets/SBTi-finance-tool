"""
This module contains classes that create connections to data providers.
"""
from typing import Type

import pandas as pd

from SBTi.configs import ColumnsConfig


def get_company_data(data_providers: list, companies: list, config: Type[ColumnsConfig] = ColumnsConfig) -> pd.DataFrame:
    """
    Get the company data in a waterfall method, given a list of companies and a list of data providers. This will go
    through the list of data providers and retrieve the required info until either there are no companies left or there
    are no data providers left.

    :param data_providers: A list of data providers instances
    :param companies: A list of companies. Each company should be a dict and contain a company_name and company_id field
    :param config: A config containing the column names
    :return: A data frame containing the company data
    """
    company_data = pd.DataFrame()
    for data_provider in data_providers:
        company_data = pd.concat([company_data, data_provider.get_company_data(companies)])
        companies = [company for company in companies
                     if company[config.COMPANY_ID] not in company_data[config.COMPANY_ID].unique() and
                        company[config.COMPANY_NAME] not in company_data[config.COMPANY_NAME].unique()]
        if len(companies) == 0:
            break

    return company_data


def get_targets(data_providers: list, companies: list, config: Type[ColumnsConfig] = ColumnsConfig) -> pd.DataFrame:
    """
    Get the targets in a waterfall method, given a list of companies and a list of data providers. This will go through
    the list of data providers and retrieve the required info until either there are no companies left or there are no
    data providers left.

    :param data_providers: A list of data providers instances
    :param companies: A list of companies. Each company should be a dict and contain a company_name and company_id field
    :param config: A config containing the column names
    :return: A data frame containing the targets
    """
    company_data = pd.DataFrame()
    for data_provider in data_providers:
        company_data = pd.concat([company_data, data_provider.get_targets(companies)])
        companies = [company for company in companies
                     if company[config.COMPANY_ID] not in company_data[config.COMPANY_ID].unique() and
                        company[config.COMPANY_NAME] not in company_data[config.COMPANY_NAME].unique()]
        if len(companies) == 0:
            break

    return company_data


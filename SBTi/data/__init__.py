"""
This module contains classes that create connections to data providers.
"""
import logging
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
    company_data = pd.DataFrame(columns=config.REQUIRED_COLUMNS_COMPANY)
    logger = logging.getLogger(__name__)
    for data_provider in data_providers:
        try:
            company_data_provider = data_provider.get_company_data(companies)
            missing_columns = [column
                               for column in config.REQUIRED_COLUMNS_COMPANY
                               if column not in company_data_provider.columns]
            if len(missing_columns) > 0:
                logger.error("The following columns were missing in the data set: {}".format(", ".join(missing_columns)))
            else:
                company_data = pd.concat([company_data, company_data_provider])
                companies = [company for company in companies
                             if company not in company_data[config.COMPANY_ID].unique()]
            if len(companies) == 0:
                break
        except NotImplementedError:
            logger.warning("{} is not available yet".format(type(data_provider).__name__))

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
    company_data = pd.DataFrame(columns=config.REQUIRED_COLUMNS_TARGETS)
    logger = logging.getLogger(__name__)
    for data_provider in data_providers:
        try:
            targets_data_provider = data_provider.get_targets(companies)
            missing_columns = [column
                               for column in config.REQUIRED_COLUMNS_TARGETS
                               if column not in targets_data_provider.columns]
            if len(missing_columns) > 0:
                logger.error("The following columns were missing in the data set: {}".format(", ".join(missing_columns)))
            else:
                company_data = pd.concat([company_data, targets_data_provider])
                companies = [company for company in companies
                             if company not in company_data[config.COMPANY_ID].unique()]
            if len(companies) == 0:
                break
        except NotImplementedError:
            logger.warning("{} is not available yet".format(type(data_provider).__name__))

    return company_data


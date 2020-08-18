"""
This module contains classes that create connections to data providers.
"""
import logging
from typing import Type, List, Dict

from SBTi.interfaces import IDataProviderTarget, IDataProviderCompany

from .data_provider import DataProvider
from .csv import CSVProvider
from .excel import ExcelProvider
from .bloomberg import Bloomberg
from .cdp import CDP
from .iss import ISS
from .trucost import Trucost
from .urgentem import Urgentem


DATA_PROVIDER_MAP: Dict[str, Type[DataProvider]] = {
    "excel": ExcelProvider,
    "csv": CSVProvider,
    "bloomberg": Bloomberg,
    "cdp": CDP,
    "iss": ISS,
    "trucost": Trucost,
    "urgentem": Urgentem,
}


def get_data_providers(data_providers_config: List[dict], data_providers_input: List[str]) -> List[DataProvider]:
    """
    Determines which data provider and in which order should be used.

    :param data_providers_config: A list of data provider configurations
    :param data_providers_input: A list of data provider names
    :return: a list of data providers in order.
    """
    data_providers = []
    for data_provider_config in data_providers_config:
        data_provider_config["class"] = DATA_PROVIDER_MAP[data_provider_config["type"]](**data_provider_config["parameters"])
        data_providers.append(data_provider_config)

    selected_data_providers = []
    for data_provider_name in data_providers_input:
        for data_provider_config in data_providers:
            if data_provider_config["name"] == data_provider_name:
                selected_data_providers.append(data_provider_config["class"])
                break

    # TODO: When the user did give us data providers, but we can't match them this fails silently, maybe we should
    # fail louder
    if len(selected_data_providers) == 0:
        selected_data_providers = [data_provider_config["class"] for data_provider_config in data_providers]
    return selected_data_providers


def get_company_data(data_providers: list, company_ids: List[str]) -> List[IDataProviderCompany]:
    """
    Get the company data in a waterfall method, given a list of companies and a list of data providers. This will go
    through the list of data providers and retrieve the required info until either there are no companies left or there
    are no data providers left.

    :param data_providers: A list of data providers instances
    :param company_ids: A list of company ids (ISINs)
    :return: A data frame containing the company data
    """
    company_data = []
    logger = logging.getLogger(__name__)
    for dp in data_providers:
        try:
            company_data_provider = dp.get_company_data(company_ids)
            company_data += company_data_provider
            company_ids = [company for company in company_ids
                           if company not in [c.company_id for c in company_data_provider]]
            if len(company_ids) == 0:
                break
        except NotImplementedError:
            logger.warning("{} is not available yet".format(type(dp).__name__))

    return company_data


def get_targets(data_providers: list, companies: list) -> List[IDataProviderTarget]:
    """
    Get the targets in a waterfall method, given a list of companies and a list of data providers. This will go through
    the list of data providers and retrieve the required info until either there are no companies left or there are no
    data providers left.

    :param data_providers: A list of data providers instances
    :param companies: A list of companies. Each company should be a dict and contain a company_name and company_id field
    :return: A data frame containing the targets
    """
    target_data = []
    logger = logging.getLogger(__name__)
    for dp in data_providers:
        try:
            targets_data_provider = dp.get_targets(companies)
            target_data += targets_data_provider
            companies = [company for company in companies
                         if company not in [t.company_id for t in targets_data_provider]]
            if len(companies) == 0:
                break
        except NotImplementedError:
            logger.warning("{} is not available yet".format(type(dp).__name__))

    return target_data


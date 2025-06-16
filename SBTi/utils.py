import logging
import pandas as pd
from typing import List, Optional, Tuple, Type, Dict

from SBTi.configs import ColumnsConfig
from SBTi.data.sbti import SBTi
from SBTi.interfaces import IDataProviderTarget, IDataProviderCompany


from .interfaces import PortfolioCompany, EScope, ETimeFrames, ScoreAggregations
from .target_validation import TargetProtocol

from .temperature_score import Scenario, TemperatureScore
from .portfolio_aggregation import PortfolioAggregationMethod

from . import data


DATA_PROVIDER_MAP: Dict[str, Type[data.DataProvider]] = {
    "excel": data.ExcelProvider,
    "csv": data.CSVProvider,
    "bloomberg": data.Bloomberg,
    "cdp": data.CDP,
    "iss": data.ISS,
    "trucost": data.Trucost,
    "urgentem": data.Urgentem,
}


def get_data_providers(
    data_providers_configs: List[dict], data_providers_input: List[str]
) -> List[data.DataProvider]:
    """
    Determines which data provider and in which order should be used.

    :param data_providers_configs: A list of data provider configurations
    :param data_providers_input: A list of data provider names
    :return: a list of data providers in order.
    """
    logger = logging.getLogger(__name__)
    data_providers = []
    for data_provider_config in data_providers_configs:
        data_provider_config["class"] = DATA_PROVIDER_MAP[data_provider_config["type"]](
            **data_provider_config["parameters"]
        )
        data_providers.append(data_provider_config)

    selected_data_providers = []
    for data_provider_name in data_providers_input:
        found = False
        for data_provider_config in data_providers:
            if data_provider_config["name"] == data_provider_name:
                selected_data_providers.append(data_provider_config["class"])
                found = True
                break
        if not found:
            logger.warning(
                "The following data provider could not be found: {}".format(
                    data_provider_name
                )
            )

    if len(selected_data_providers) == 0:
        raise ValueError(
            "None of the selected data providers are available. The following data providers are valid "
            "options: "
            + ", ".join(
                data_provider["name"] for data_provider in data_providers_configs
            )
        )
    return selected_data_providers


def get_company_data(
    data_providers: list, company_ids: List[str]
) -> List[IDataProviderCompany]:
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
            company_ids = [
                company
                for company in company_ids
                if company not in [c.company_id for c in company_data_provider]
            ]
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
            companies = [
                company
                for company in companies
                if company not in [t.company_id for t in targets_data_provider]
            ]
            if len(companies) == 0:
                break
        except NotImplementedError:
            logger.warning("{} is not available yet".format(type(dp).__name__))

    return target_data


def _flatten_user_fields(record: PortfolioCompany):
    """
    Flatten the user fields in a portfolio company and return it as a dictionary.

    :param record: The record to flatten
    :return:
    """
    record_dict = record.dict(exclude_none=True)
    if record.user_fields is not None:
        for key, value in record_dict["user_fields"].items():
            record_dict[key] = value
        del record_dict["user_fields"]

    return record_dict

def _make_id_map(df_portfolio: pd.DataFrame) -> dict:
    """
    Create a mapping from company_id to ISIN and LEI (required for the SBTi matching).

    :param df_portfolio: The complete portfolio
    :return: A mapping from company_id to (ISIN, LEI) tuple
    """
    return {
        company_id: (company[ColumnsConfig.COMPANY_ISIN], company[ColumnsConfig.COMPANY_LEI])
        for company_id, company in df_portfolio[
            [ColumnsConfig.COMPANY_ID, ColumnsConfig.COMPANY_ISIN, ColumnsConfig.COMPANY_LEI]
        ]
        .set_index(ColumnsConfig.COMPANY_ID)
        .to_dict(orient="index")
        .items()
    }


def dataframe_to_portfolio(df_portfolio: pd.DataFrame) -> List[PortfolioCompany]:
    """
    Convert a data frame to a list of portfolio company objects.

    :param df_portfolio: The data frame to parse. The column names should align with the attribute names of the
    PortfolioCompany model.
    :return: A list of portfolio companies
    """
    df_portfolio[ColumnsConfig.ENGAGEMENT_TARGET] = (
        df_portfolio[ColumnsConfig.ENGAGEMENT_TARGET].fillna(False).astype("bool")
    )
    return [
        PortfolioCompany.parse_obj(company)
        for company in df_portfolio.to_dict(orient="records")
    ]


def merge_target_data(
    provider_targets: List[IDataProviderTarget], 
    sbti_targets: Dict[str, List[IDataProviderTarget]]
) -> List[IDataProviderTarget]:
    """
    Merge targets from data providers with SBTi targets, preferring SBTi data for validated companies.
    
    :param provider_targets: List of targets from data providers
    :param sbti_targets: Dictionary mapping company_id to list of SBTi targets
    :return: Merged list of targets
    """
    # Create lookup of provider targets by company
    provider_by_company = {}
    for target in provider_targets:
        if target.company_id not in provider_by_company:
            provider_by_company[target.company_id] = []
        provider_by_company[target.company_id].append(target)
    
    # Replace with SBTi targets where available
    for company_id, sbti_company_targets in sbti_targets.items():
        if sbti_company_targets:  # Only replace if we have valid SBTi targets
            provider_by_company[company_id] = sbti_company_targets
            logging.getLogger(__name__).info(
                f"Using {len(sbti_company_targets)} SBTi targets for company {company_id}"
            )
    
    # Flatten back to list
    merged_targets = []
    for company_targets in provider_by_company.values():
        merged_targets.extend(company_targets)
    
    return merged_targets


def get_data(
    data_providers: List[data.DataProvider], portfolio: List[PortfolioCompany]
) -> pd.DataFrame:
    """
    Get the required data from the data provider(s), validate the targets and return a 9-box grid for each company.
    Enhanced to use SBTi authoritative target data when available.

    :param data_providers: A list of DataProvider instances
    :param portfolio: A list of PortfolioCompany models
    :return: A data frame containing the relevant company-target data
    """
    logger = logging.getLogger(__name__)
    
    df_portfolio = pd.DataFrame.from_records(
        [_flatten_user_fields(c) for c in portfolio]
    )
    company_data = get_company_data(data_providers, df_portfolio["company_id"].tolist())
    target_data = get_targets(data_providers, df_portfolio["company_id"].tolist())

    # Supplement the company data with the SBTi target status and get detailed targets
    sbti = SBTi()
    company_data, sbti_targets = sbti.get_sbti_targets(company_data, _make_id_map(df_portfolio))
    
    # Log information about SBTi targets found
    if sbti_targets:
        logger.info(f"Found SBTi targets for {len(sbti_targets)} companies")
        for company_id, targets in sbti_targets.items():
            logger.info(f"Company {company_id}: {len(targets)} SBTi targets")
    
    # Merge SBTi targets with provider targets
    if sbti_targets:
        target_data = merge_target_data(target_data, sbti_targets)
        logger.info(f"Total targets after merging: {len(target_data)}")
    
    if len(target_data) == 0:
        raise ValueError("No targets found")

    # Prepare the data
    portfolio_data = TargetProtocol().process(target_data, company_data)
    portfolio_data = pd.merge(
        left=portfolio_data,
        right=df_portfolio.drop("company_name", axis=1),
        how="left",
        on=["company_id"],
    )

    if len(company_data) == 0:
        raise ValueError(
            "None of the companies in your portfolio could be found by the data providers"
        )

    return portfolio_data


def calculate(
    portfolio_data: pd.DataFrame,
    fallback_score: float,
    aggregation_method: PortfolioAggregationMethod,
    grouping: Optional[List[str]],
    scenario: Optional[Scenario],
    time_frames: List[ETimeFrames],
    scopes: List[EScope],
    anonymize: bool,
    aggregate: bool = True,
) -> Tuple[pd.DataFrame, Optional[ScoreAggregations]]:
    """
    Calculate the different parts of the temperature score (actual scores, aggregations, column distribution).

    :param portfolio_data: The portfolio data, already processed by the target validation module
    :param fallback_score: The fallback score to use while calculating the temperature score
    :param aggregation_method: The aggregation method to use
    :param time_frames: The time frames that the temperature scores should be calculated for  (None to calculate all)
    :param scopes: The scopes that the temperature scores should be calculated for (None to calculate all)
    :param grouping: The names of the columns to group on
    :param scenario: The scenario to play
    :param anonymize: Whether to anonymize the resulting data set or not
    :param aggregate: Whether to aggregate the scores or not
    :return: The scores, the aggregations and the column distribution (if a
    """
    ts = TemperatureScore(
        time_frames=time_frames,
        scopes=scopes,
        fallback_score=fallback_score,
        scenario=scenario,
        grouping=grouping,
        aggregation_method=aggregation_method,
    )

    scores = ts.calculate(portfolio_data)
    aggregations = None
    if aggregate:
        aggregations = ts.aggregate_scores(scores)

    if anonymize:
        scores = ts.anonymize_data_dump(scores)

    return scores, aggregations
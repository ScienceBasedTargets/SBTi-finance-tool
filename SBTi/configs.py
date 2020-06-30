"""
This file defines the constants used throughout the different classes. In order to redefine these settings whilst using
the module, extend the respective config class and pass it to the class as the "constants" parameter.
"""
import os


class ColumnsConfig:
    # Define a constant for each column used in the
    INDUSTRY = "industry"
    REGRESSION_PARAM = "regression_param"
    REGRESSION_INTERCEPT = "regression_intercept"
    S1S2_EMISSIONS = "s1s2_emissions"
    S3_EMISSIONS = "s3_emissions"
    MARKET_CAP = "market_cap"
    INVESTMENT_VALUE = "investment_value"
    PORTFOLIO_WEIGHT = "portfolio_weight"
    COMPANY_ENTERPRISE_VALUE = "company_enterprise_value"
    COMPANY_EV_PLUS_CASH = "company_ev_plus_cash"
    COMPANY_TOTAL_ASSETS = "company_total_assets"
    TARGET_REFERENCE_NUMBER = "target_reference_number"
    TARGET_TYPE = "target_type"
    SCOPE = "Scope"
    SCOPE_CATEGORY = "scope_category"
    SR15 = "SR15"
    REDUCTION_FROM_BASE_YEAR = "reduction_from_base_year"
    TARGET_YEAR = "target_year"
    START_YEAR = "start_year"
    VARIABLE = "variable"
    SLOPE = "slope"
    TIME_FRAME = "time_frame"
    MODEL = "model"
    ANNUAL_REDUCTION_RATE = "annual_reduction_rate"
    EMISSIONS_IN_SCOPE = "emissions_in_scope"
    TEMPERATURE_SCORE = "temperature_score"
    COMPANY_NAME = "company_name"
    OWNED_EMISSIONS = "owned_emissions"
    COMPANY_ID = 'company_ID'
    CDP_ACS_INDUSTRY = 'CDP_ACS_industry'
    COUNTRY = 'country'
    SECTOR = 'sector'
    GHG_SCOPE12 = 'GHG_scope12'
    GHG_SCOPE3 = 'GHG_scope3'
    REVENU = 'Revenu'
    ENTERPRISE_VALUE = 'enterprise_value'
    TOTAL_ASSETS = 'total_assets'
    CASH_EQUIVALENTS = 'cash_equivalents'
    TARGET_CLASSIFICATION = 'Target_classification'
    COVERAGE = 'coverage'
    REDUCTION_AMBITION = 'reduction_ambition'
    BASE_YEAR = 'base_year'
    END_YEAR = 'end_year'
    SBTI_STATUS = 'SBTi_status'

    # SR15 mapping columns
    PARAM = "param"
    INTERCEPT = "intercept"

    # Output columns
    WEIGHTED_TEMPERATURE_SCORE = "weighted_temperature_score"

    # This defines which column contain company specific, instead of target specific data
    COMPANY_COLUMNS = [INDUSTRY, REGRESSION_PARAM, REGRESSION_INTERCEPT,
                       S1S2_EMISSIONS,
                       S3_EMISSIONS, MARKET_CAP, INVESTMENT_VALUE, PORTFOLIO_WEIGHT,
                       COMPANY_ENTERPRISE_VALUE, COMPANY_EV_PLUS_CASH,
                       COMPANY_TOTAL_ASSETS]


class TemperatureScoreConfig:
    FILE_SR15_MAPPING = os.path.join(os.path.dirname(os.path.realpath(__file__)), "inputs",
                                     "sr15_mapping.xlsx")
    FILE_REGRESSION_MODEL_SUMMARY = os.path.join(os.path.dirname(os.path.realpath(__file__)), "inputs",
                                                 "regression_model_summary.xlsx")

    COLS = ColumnsConfig

    DEFAULT_INDUSTRY = "Others"

    VALUE_TARGET_REFERENCE_ABSOLUTE = "Absolute"
    VALUE_TARGET_REFERENCE_INTENSITY = "Intensity"
    VALUE_TARGET_REFERENCE_INTENSITY_BASE = "Int"

    VALUE_TIME_FRAMES = ["short", "mid", "long"]

    VALUE_SCOPE_S1S2 = "scope 1+2"
    VALUE_SCOPE_S3 = "scope 3"
    VALUE_SCOPE_S1S2S3 = "scope 1+2+3"

    VALUE_SCOPE_CATEGORY_S1S2 = "s1s2"
    VALUE_SCOPE_CATEGORY_S3 = "s3"
    VALUE_SCOPE_CATEGORY_S1S2S3 = "s1s2s3"

    SLOPE_MAP = {
        "short": "slope5",
        "mid": "slope15",
        "long": "slope30",
    }
import json
import os

from typing import List, Dict

import pandas as pd
import numpy as np
from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api
from flask_swagger_ui import get_swaggerui_blueprint

import mimetypes

mimetypes.init()

import SBTi
from SBTi.data.csv import CSVProvider
from SBTi.data.excel import ExcelProvider
from SBTi.portfolio_aggregation import PortfolioAggregationMethod
from SBTi.portfolio_coverage_tvp import PortfolioCoverageTVP
from SBTi.temperature_score import TemperatureScore, Scenario
from SBTi.target_valuation_protocol import TargetValuationProtocol

UPLOAD_FOLDER = 'data'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
api = Api(app)

DATA_PROVIDER_MAP = {
    "excel": ExcelProvider,
    "csv": CSVProvider,
}


def get_config():
    # TODO: Make this path relative to the current directory, instead of the working directory
    with open('config.json') as f_config:
        return json.load(f_config)


class BaseEndpoint(Resource):
    """
    This class instantiates the data provider classes and loads in the config file. Further classes with inherit the
     methods from this class.

    :rtype:
    :return:
    """

    def __init__(self):
        self.config = get_config()

        self.data_providers = []
        for data_provider in self.config["data_providers"]:
            data_provider["class"] = DATA_PROVIDER_MAP[data_provider["type"]](**data_provider["parameters"])
            self.data_providers.append(data_provider)

        self.aggregation_map = {
            "WATS": PortfolioAggregationMethod.WATS,
            "TETS": PortfolioAggregationMethod.TETS,
            "MOTS": PortfolioAggregationMethod.MOTS,
            "EOTS": PortfolioAggregationMethod.EOTS,
            "ECOTS": PortfolioAggregationMethod.ECOTS,
            "AOTS": PortfolioAggregationMethod.AOTS,
            "ROTS": PortfolioAggregationMethod.ROTS
        }

    def _get_data_providers(self, json_data: Dict):
        '''
        Determines which data provider and in which order should be used.
        :param json_data:

        :rtype: List
        :return: a list of data providers in order.
        '''
        # TODO: Why is there a hard-coded Excel connector here?
        data_providers = []
        if "data_providers" in json_data:
            for path in json_data["data_providers"]:
                data_provider = DATA_PROVIDER_MAP['excel'](path)
                data_providers.append(data_provider)

        # TODO: When the user did give us data providers, but we can't match them this fails silently, maybe we should
        # fail louder
        if len(data_providers) == 0:
            data_providers = [data_provider["class"] for data_provider in self.data_providers]
        return data_providers


class TemperatureScoreEndpoint(BaseEndpoint):
    '''
    Generates the temperature aggregation scoring for the companies provided.

    :rtype: Dictionary
    :return: aggregation scoring per companies.
    '''

    def __init__(self):
        super().__init__()

    def post(self):

        json_data = request.get_json(force=True)

        data_providers = self._get_data_providers(json_data)

        default_score = json_data.get("default_score", self.config["default_score"])
        temperature_score = TemperatureScore(fallback_score=default_score)

        company_data = SBTi.data.get_company_data(data_providers, json_data["companies"])
        targets = SBTi.data.get_targets(data_providers, json_data["companies"])

        portfolio_data = pd.merge(left=company_data, right=targets, how='outer', on=['company_name', 'company_id'])

        aggregation_method = self.aggregation_map[self.config["aggregation_method"]]
        # TODO: Write this as a shorthand and throw an exception if the user defined a non existing aggregation
        if "aggregation_method" in json_data and json_data["aggregation_method"] in self.aggregation_map:
            aggregation_method = self.aggregation_map[json_data["aggregation_method"]]

        # Group aggregates by certain column names
        grouping = json_data.get("grouping_columns", None)

        scenario = json_data.get('scenario', None)
        if scenario is not None:
            scenario['aggregation_method'] = aggregation_method
            scenario['grouping'] = grouping
            scenario = Scenario.from_dict(scenario)
            temperature_score.set_scenario(scenario)

        if len(portfolio_data) == 0:
            return {
                       "success": False,
                       "message": "None of the companies in your portfolio could be found by the data provider"
                   }, 400

        # Target_Valuation_Protocol
        target_valuation_protocol = TargetValuationProtocol(portfolio_data, company_data)

        portfolio_data = target_valuation_protocol.target_valuation_protocol()

        # Add the user-defined columns to the data set for grouping later on
        extra_columns = []
        for company in json_data["companies"]:
            for key, value in company.items():
                if key not in ["company_name", "company_id"]:
                    portfolio_data.loc[portfolio_data['company_name'] == company["company_name"], key] = value
                    extra_columns.append(key)

        scores = temperature_score.calculate(portfolio_data, extra_columns)

        # After calculation we'll re-add the extra columns from the input
        for company in json_data["companies"]:
            for key, value in company.items():
                if key not in ["company_name", "company_id"]:
                    portfolio_data.loc[portfolio_data['company_name'] == company["company_name"], key] = value

        # Filter scope (s1s2, s3 or s1s2s3)
        if len(json_data.get("filter_scope_category", [])) > 0:
            scores = scores[scores["scope_category"].isin(json_data["filter_scope_category"])]

        # Filter timeframe (short, mid, long)
        if len(json_data.get("filter_time_frame", [])) > 0:
            scores = scores[scores["time_frame"].isin(json_data["filter_time_frame"])]

        scores = scores.copy()
        # TODO: Why are the scores rounded here, even though there are still calculation left to do?
        scores = scores.round(2)

        aggregations = temperature_score.aggregate_scores(scores, aggregation_method, grouping)

        # Include columns
        include_columns = ["company_name", "scope_category", "time_frame", "temperature_score"] + \
                          [column for column in json_data.get("include_columns", []) if column in scores.columns]

        portfolio_coverage_tvp = PortfolioCoverageTVP()
        coverage = portfolio_coverage_tvp.get_portfolio_coverage(portfolio_data, aggregation_method)

        # Temperature score percentage breakdown by default score and target score
        temperature_percentage_coverage = temperature_score.temperature_score_influence_percentage(portfolio_data,
                                                                                                   json_data[
                                                                                                       'aggregation_method'])

        if grouping:
            column_distribution = temperature_score.columns_percentage_distribution(portfolio_data,
                                                                                    json_data['grouping_columns'])
        else:
            column_distribution = None

        temperature_percentage_coverage = pd.DataFrame.from_dict(temperature_percentage_coverage).replace(
            {np.nan: None}).to_dict()
        aggregations = temperature_score.merge_percentage_coverage_to_aggregations(aggregations,
                                                                                   temperature_percentage_coverage)

        # Dump raw data to compute the scores
        anonymize_data_dump = json_data.get("anonymize_data_dump", False)
        if anonymize_data_dump:
            scores = temperature_score.anonymize_data_dump(scores)

        return_dic = {
            "aggregated_scores": aggregations,
            # TODO: The scores are included twice now, once with all columns, and once with only a subset of the columns
            "scores": scores.replace({np.nan: None}).to_dict(orient="records"),
            "coverage": coverage,
            "companies": scores[include_columns].replace({np.nan: None}).to_dict(
                orient="records"),
            "feature_distribution": column_distribution
        }

        return_dic = convert_nan_to_none(return_dic)

        return return_dic


def convert_nan_to_none(nested_dictionary):
    """Convert NaN values to None in a list in a nested dictionary.
    TODO: Temporary fix for front-end not supporting nan, will be deleted after Beta testing
    TODO: Refactor this such that the NaNs are replaced in a data frame, instead of a dictionary

    :param nested_dictionary: dictionary to return that possible contains NaN values
    :type nested_dictionary: dict

    :rtype: dict
    :return: cleaned dictionary where all NaN values are converted to None
    """
    for parent, dictionary in nested_dictionary.items():
        if isinstance(dictionary, list):
            clean_list = []
            for element in dictionary:
                clean_element = element
                if isinstance(element, dict):
                    for x, y in element.items():
                        if str(y) == 'nan':
                            clean_element[x] = None
                clean_list.append(clean_element)
            nested_dictionary[parent] = clean_list

        elif isinstance(dictionary, dict):
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    for time_frame, values in value.items():
                        if isinstance(values, dict):
                            for scope, scores_el in values.items():
                                for k, v in scores_el.items():
                                    if isinstance(v, list):
                                        clean_v = []
                                        for company in v:
                                            clean_company = company
                                            if isinstance(company, dict):
                                                for identifier, number in company.items():
                                                    if str(number) == 'nan':
                                                        clean_company[identifier] = None
                                                clean_v.append(clean_company)
                                                scores_el[k] = clean_v

                                    if str(v) == 'nan':
                                        scores_el[k] = None
                        if str(values) == 'nan':
                            value[time_frame] = None

    return nested_dictionary


class DataProvidersEndpoint(BaseEndpoint):
    """
    This class provides the user with a list of the available data providers.
    """

    def __init__(self):
        super().__init__()

    def get(self):
        """
        Get a list of available data providers on this server.

        :rtype: List
        :return: a list of data providers.
        """
        return [{"name": data_provider["name"], "type": data_provider["type"]}
                for data_provider in self.config["data_providers"]]


class DocumentationEndpoint(Resource):
    '''
    Supports flask_swagger documentation endpoint
    '''

    def get(self, path):
        return send_from_directory('static', path)


class ParsePortfolioEndpoint(Resource):
    """
    This class allows the client to user to parse his Excel portfolio and transform it into a JSON object.
    Note: This endpoint is only meant to be used by the UI!
    """

    def post(self):
        skiprows = request.form.get("skiprows", 0)
        df = pd.read_excel(request.files.get('file'), skiprows=int(skiprows))

        return {'portfolio': df.replace(r'^\s*$', np.nan, regex=True).dropna(how='all').replace({np.nan: None}).to_dict(
            orient="records")}


class ImportDataProviderEndpoint(Resource):
    """
    Allows the user to replace the "inputFormat" with a new "data provider".
    """

    def post(self):
        file = request.files['file']
        file_name = file.filename
        file_type = file_name.split('.')[-1]
        if (int(file.tell()) < 10000000) & (file_type == 'xlsx'):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'InputFormat.xlsx'))
            return {'POST Request': {'Response': {'Status Code': 200, 'Message': 'Data Provider Imported'}}}
        else:
            return {'POST Request': {'Response': {'Status Code': 400, 'Message': 'Error. File did not save.'}}}


SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'SBTi-API'
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

api.add_resource(TemperatureScoreEndpoint, '/temperature_score/')
api.add_resource(DataProvidersEndpoint, '/data_providers/')
api.add_resource(DocumentationEndpoint, '/static/<path:path>')
api.add_resource(ParsePortfolioEndpoint, '/parse_portfolio/')
api.add_resource(ImportDataProviderEndpoint, '/import_data_provider/')

if __name__ == '__main__':
    app.run(debug=True)  # important to mention debug=True

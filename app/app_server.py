import itertools
import json
import os
import mimetypes

from typing import List, Dict

import pandas as pd
import numpy as np
from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api
from flask_swagger_ui import get_swaggerui_blueprint
from flask_uploads import UploadSet, ALL, configure_uploads

import mimetypes
mimetypes.init()

import SBTi
from SBTi.data.csv import CSVProvider
from SBTi.data.excel import ExcelProvider
from SBTi.portfolio_aggregation import PortfolioAggregationMethod
from SBTi.portfolio_coverage_tvp import PortfolioCoverageTVP
from SBTi.temperature_score import TemperatureScore
from SBTi.target_valuation_protocol import TargetValuationProtocol

PATH = "uploads"
app = Flask(__name__)
files = UploadSet('files', ALL)
app.config['UPLOADS_DEFAULT_DEST'] = PATH
configure_uploads(app, files)
api = Api(app)

DATA_PROVIDER_MAP = {
    "excel": ExcelProvider,
    "csv": CSVProvider,
}


def get_config():
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
            "AOTS": PortfolioAggregationMethod.AOTS
        }

    def _get_data_providers(self, json_data: Dict):
        '''
        Determines which data provider and in which order should be used.
        :param json_data:

        :rtype: List
        :return: a list of data providers in order.
        '''
        data_providers = []
        if "data_providers" in json_data:
            for data_provider_name in json_data["data_providers"]:
                for data_provider in self.data_providers:
                    if data_provider["name"] == data_provider_name:
                        data_providers.append(data_provider["class"])
                        break

        # TODO: When the user did give us data providers, but we can't match them this fails silently, maybe we should
        # fail louder
        if len(data_providers) == 0:
            data_providers = [data_provider["class"] for data_provider in self.data_providers]
        return data_providers



class temp_score(BaseEndpoint):
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

        default_score = self.config["default_score"]
        if "default_score" in json_data:
            default_score = json_data["default_score"]
        temperature_score = TemperatureScore(fallback_score=default_score)

        scenario = json_data.get('scenario', None)
        if scenario is not None:
            temperature_score.set_scenario(scenario)

        company_data = SBTi.data.get_company_data(data_providers, json_data["companies"])
        targets = SBTi.data.get_targets(data_providers, json_data["companies"])
        portfolio_data = pd.merge(left=company_data, right=targets, left_on='company_name', right_on='company_name')

        # Target_Valuation_Protocol
        target_valuation_protocol = TargetValuationProtocol(portfolio_data)
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
        if "filter_scope_category" in json_data and len(json_data["filter_scope_category"]) > 0:
            scores = scores[scores["scope_category"].isin(json_data["filter_scope_category"])]

        # Filter timeframe (short, mid, long)
        if "filter_time_frame" in json_data and len(json_data["filter_time_frame"]) > 0:
            scores = scores[scores["time_frame"].isin(json_data["filter_time_frame"])]

        # Group by certain column names
        grouping = json_data.get("grouping_columns", None)

        scores = scores.copy()

        aggregation_method = self.aggregation_map[self.config["aggregation_method"]]
        if "aggregation_method" in json_data and json_data["aggregation_method"] in self.aggregation_map:
            aggregation_method = self.aggregation_map[json_data["aggregation_method"]]
        aggregations = temperature_score.aggregate_scores(scores, aggregation_method, grouping)

        # Include columns
        include_columns = ["company_name", "scope_category", "time_frame", "temperature_score"]
        if "include_columns" in json_data and len(json_data["include_columns"]) > 0:
            include_columns += [column for column in json_data["include_columns"] if column in scores.columns]

        portfolio_coverage_tvp = PortfolioCoverageTVP()
        coverage = portfolio_coverage_tvp.get_portfolio_coverage(portfolio_data, aggregation_method)

        # Temperature score percentage breakdown by default score and target score
        temperature_percentage_coverage = temperature_score.temperature_score_influence_percentage(portfolio_data, json_data['aggregation_method'])

        # Distribution of columns
        column_distribution = temperature_score.columns_percentage_distribution(portfolio_data,json_data['feature_distribution'])

        return {
            "aggregated_scores": aggregations,
            "coverage": coverage,
            "companies": scores[include_columns].replace({np.nan: None}).to_dict(
                orient="records"),
            "temp_score_percent_coverage": temperature_percentage_coverage,
            "feature_distribution": str(column_distribution)
        }

class DataProviders(BaseEndpoint):
    """
    This class provides the user with a list of the available data providers.

    :param BaseEndpoint: inherites from a different class

    :rtype: List
    :return: a list of data providers.
    """

    def __init__(self):
        super().__init__()

    def get(self):
        return [{"name": data_provider["name"], "type": data_provider["type"]}
                for data_provider in self.config["data_providers"]]


class portfolio_coverage(BaseEndpoint):
    """
    This class provides the user with the portfolio coverage of the specified companies.

    :param BaseEndpoint: inherites from a different class

    :rtype: Dictionary
    :return: Coverage scoring.
    """

    def __init__(self):
        super().__init__()
        self.portfolio_coverage_tvp = PortfolioCoverageTVP()

    def post(self):
        json_data = request.get_json(force=True)
        data_providers = self._get_data_providers(json_data)
        company_data = SBTi.data.get_company_data(data_providers, json_data["companies"])
        targets = SBTi.data.get_targets(data_providers, json_data["companies"])
        portfolio_data = pd.merge(left=company_data, right=targets, left_on='company_name', right_on='company_name')

        for company in json_data["companies"]:
            portfolio_data.loc[portfolio_data['company_name'] == company["company_name"], "portfolio_weight"] = company[
                "portfolio_weight"]
            portfolio_data.loc[portfolio_data['company_name'] == company["company_name"], "investment_value"] = company[
                "investment_value"]

        coverage = self.portfolio_coverage_tvp.get_portfolio_coverage(portfolio_data,
                                                                      self.aggregation_map[
                                                                          json_data["aggregation_method"]])
        return {
            "coverage": coverage,
        }


class data(BaseEndpoint):
    """
    Acquires company and target data per specified company.

    :param BaseEndpoint: inherites from a different class

    :rtype: Dictionary
    :return: Company and target data.
    """

    def __init__(self):
        super().__init__()
        self.portfolio_coverage_tvp = PortfolioCoverageTVP()

    def post(self):
        json_data = request.get_json(force=True)
        data_providers = self._get_data_providers(json_data)
        company_data = SBTi.data.get_company_data(data_providers, json_data["companies"])
        targets = SBTi.data.get_targets(data_providers, json_data["companies"])
        data = pd.merge(left=company_data, right=targets, left_on='company_name', right_on='company_name')

        return {
            "data": data.to_dict(orient="records"),
        }


class report(Resource):
    '''
    To be determined...
    '''

    def get(self):
        return {'GET Request': 'Hello World'}

    def post(self):
        return {'POST Request': 'Hello World'}


class documentation_endpoint(Resource):
    '''
    Supports flask_swagger documentation endpoint
    '''
    def get(self, path):
        return send_from_directory('static', path)


class Frontend(Resource):
    def get(self, path="index.html"):
        mimetypes.add_type('application/javascript', '.js')
        mimetypes.add_type('text/css', '.css')
        config = get_config()
        return send_from_directory(config["frontend_path"], path)


class ParsePortfolio(Resource):
    """
    This class allows the client to user to parse his Excel portfolio and transform it into a JSON object.
    Note: This endpoint is only meant to be used by the UI!
    """

    def post(self):
        skiprows = request.form.get("skiprows")
        if skiprows is None:
            skiprows = 0

        df = pd.read_excel(request.files.get('file'), skiprows=int(skiprows))

        return {'portfolio': df.replace({np.nan: None}).to_dict(orient="records")}


class import_portfolio(Resource):
    """
    This class allows the client to import and replace portfolios. Multiple HTTP Protocols are available for
    this resource.

    :param BaseEndpoint: inherites from a different class

    :rtype: Dictionary
    :return: HTTP Request Information.
    """

    def get(self):
        return {'GET Request': 'Hello World'}

    def post(self):
        doc_type = request.args.get('document_type')
        if doc_type=='excel':
            file = request.files['file']
            if test_file(file,'excel'):
                files.save(request.files['file'])
                return {'POST Request': {'Response': {'Status Code': 200, 'Message': 'File Saved', 'File': file.filename}}}
            else:
                return {'POST Request': {'Response': {'Status Code': 400, 'Message': 'Error. File did not save.'}}}

        elif doc_type=='json':
            json_data = request.get_json(force=True)
            df = pd.DataFrame(data=json_data['companies'], index=[0])
            # Todo: Name of document needs to be adjusted.
            df.to_excel('json_example.xlsx')

            # Todo: Modify the return response.
            return {'POST Request': {'Response': {'Status Code': 200, 'Message': 'File Saved', 'File':''}}}

    def put(self):
        doc_type = request.args.get('document_type')
        remove_doc = request.args.get('document_replace')
        for root, dirs, file in os.walk(PATH):
            for f in file:
                if remove_doc == f.split('.')[0]:
                    if doc_type=='excel':
                        os.remove(os.path.join(root, f))
                        files.save(request.files['file'])
                    elif doc_type=='json':
                        os.remove(os.path.join(root, f))
                        json_data = request.get_json(force=True)
                        df = pd.DataFrame(data=json_data['companies'], index=[0])

                        # Todo: Name of document needs to be adjusted.
                        df.to_excel('json_example.xlsx')
                    return {'PUT Request': {
                        'Response': {'Status Code': 200, 'Message': 'File Replaced', 'Replaced File': remove_doc}}}
        return {'PUT Request': {'Response': {'Status Code': 400, 'Error Message': 'File Not Found', 'File': remove_doc}}}



class data_provider(BaseEndpoint):
    """
    This class allows the client to receive information from the data provider.

    :param BaseEndpoint: inherites from a different class

    :rtype: Dictionary
    :return: HTTP Request.

    """

    def __init__(self):
        super().__init__()

    def get(self):
        return {'GET Request': 'Hello World'}

    def post(self):
        json_data = request.get_json(force=True)
        data_providers = self._get_data_providers(json_data)
        company_data = SBTi.data.get_company_data(data_providers, json_data["companies"])
        targets = SBTi.data.get_targets(data_providers, json_data["companies"])
        portfolio_data = pd.merge(left=company_data, right=targets, left_on='company_name', right_on='company_name')

        return {
            "POST Request": {
                'Status': 200,
                'Data': portfolio_data.to_json(orient='records')
            }
        }


def test_file(file,target_type):
    """
    This supporting function determines if the file size is not above a predetermine threshold, and if the target type
    matchs the file that is being imported.

    :param file: file that is being imported through HTTP Protocol
    :param target_type: <excel|json>

    :rtype: Boolean
    :return: <True|False>
    """
    file.seek(0, 2)
    file_name = file.filename
    file_type = file_name.split('.')[-1]
    file_dictionary = {'excel':'xlsx'}
    if (int(file.tell())<10000000) & (file_type==file_dictionary[target_type]):
        return True
    else:
        return False


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

api.add_resource(temp_score, '/temperature_score/')
api.add_resource(portfolio_coverage, '/portfolio_coverage/')
api.add_resource(DataProviders, '/data_providers/')
api.add_resource(data, '/data/')
api.add_resource(report, '/report/')
api.add_resource(documentation_endpoint, '/static/<path:path>')
api.add_resource(import_portfolio, '/import_portfolio/')
api.add_resource(ParsePortfolio, '/parse_portfolio/')
api.add_resource(data_provider, '/data_provider')
api.add_resource(Frontend, '/<path:path>', '/')

if __name__ == '__main__':
    app.run(debug=True)  # important to mention debug=True

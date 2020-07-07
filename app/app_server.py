import itertools
import json
import os

from typing import List, Set, Dict, Tuple, Optional, Type

import pandas as pd
from pathlib import Path
from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api
from flask_swagger_ui import get_swaggerui_blueprint
from flask_uploads import UploadSet, ALL

import SBTi
from SBTi.data.csv import CSVProvider
from SBTi.data.excel import ExcelProvider
from SBTi.portfolio_aggregation import PortfolioAggregationMethod
from SBTi.portfolio_coverage_tvp import PortfolioCoverageTVP
from SBTi.temperature_score import TemperatureScore
from protocol.target_valuation_protocol import TargetValuationProtocol

PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "uploads")
app = Flask(__name__)
files = UploadSet('files', ALL)
app.config['UPLOADS_DEFAULT_DEST'] = PATH
api = Api(app)

DATA_PROVIDER_MAP = {
    "excel": ExcelProvider,
    "csv": CSVProvider,
}


class BaseEndpoint(Resource):
    """
    This class instantiates the data provider classes and loads in the config file. Further classes with inherit the
     methods from this class.

    :rtype:
    :return:
    """
    def __init__(self):
        with open('config.json') as f_config:
            self.config = json.load(f_config)

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

        company_data = SBTi.data.get_company_data(data_providers, json_data["companies"])
        targets = SBTi.data.get_targets(data_providers, json_data["companies"])
        portfolio_data = pd.merge(left=company_data, right=targets, left_on='company_name', right_on='company_name')

        # Target_Valuation_Protocol
        target_valuation_protocol = TargetValuationProtocol(portfolio_data)
        portfolio_data = target_valuation_protocol.target_valuation_protocol()

        for company in json_data["companies"]:
            portfolio_data.loc[portfolio_data['company_name'] == company["company_name"], "portfolio_weight"] = company[
                "portfolio_weight"]
            portfolio_data.loc[portfolio_data['company_name'] == company["company_name"], "investment_value"] = company[
                "investment_value"]

        scores = temperature_score.calculate(portfolio_data)

        # Filter scope (s1s2, s3 or s1s2s3)
        if "filter_scope_category" in json_data:
            scores = scores[scores["scope_category"].isin(json_data["filter_scope_category"])]

        # Filter timeframe (short, mid, long)
        if "filter_time_frame" in json_data:
            scores = scores[scores["time_frame"].isin(json_data["filter_time_frame"])]

        # Group by certain column names
        if len(json_data.get("grouping_column", [])) > 0:
            groupings = []
            for column in json_data["grouping_column"]:
                if column in scores.columns:
                    groupings.append([(column, value) for value in scores[column].unique()])

            all_groupings = list(itertools.product(*groupings))
            print(all_groupings)
            # scores = scores[scores["time_frame"].isin(json_data["filter_time_frame"])]

        scores = scores.copy()
        aggregations = temperature_score.aggregate_scores(scores,
                                                          self.aggregation_map[json_data["aggregation_method"]])

        # Include columns
        include_columns = ["company_name", "scope_category", "time_frame", "temperature_score"]
        if "include_columns" in json_data:
            include_columns += [column for column in json_data["include_columns"] if column in scores.columns]

        return {
            "aggregated_scores": aggregations,
            "companies": scores[include_columns].to_dict(
                orient="records")
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
    def get(path):
        return send_from_directory('static', path)


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
        if 'file' in request.files:
            files.save(request.files['file'])
            path = str(sorted(Path(PATH + '/files/').iterdir(), key=os.path.getmtime, reverse=True)[0])
            file_name = path.split("""\\""")[-1]
            return {'POST Request': {'Response': {'Status Code': 200, 'Message': 'File Saved', 'File': file_name}}}
        else:
            json_data = request.get_json(force=True)
            df = pd.DataFrame(data=json_data['companies'], index=[0])
            # Todo: Name of document needs to be adjusted.
            df.to_excel('dict1.xlsx')
            return {'POST Request': {'Response': {'Status Code': 200, 'Message': 'File Saved', 'File':''}}}

    def put(self):
        remove_doc = request.args.get('document_replace')
        if 'file' in request.files:
            for root, dirs, file in os.walk(PATH):
                for f in file:
                    if remove_doc == f.split('.')[0]:
                        if 'file' in request.files:
                            os.remove(os.path.join(root, f))
                            files.save(request.files['file'])
                        else:
                            os.remove(os.path.join(root, f))
                            json_data = request.get_json(force=True)
                            df = pd.DataFrame(data=json_data['companies'], index=[0])
                            # Todo: Name of document needs to be adjusted.
                            df.to_excel('dict1.xlsx')
                        return {'PUT Request': {
                            'Response': {'Status Code': 200, 'Message': 'File Replaced', 'Replaced File': remove_doc}}}


        return {
            'PUT Request': {'Response': {'Status Code': 404, 'Error Message': 'File Not Found', 'File': remove_doc}}}

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
        return {'GET Request':'Hello World'}

    def post(self):
        json_data = request.get_json(force=True)
        data_providers = self._get_data_providers(json_data)
        company_data = SBTi.data.get_company_data(data_providers, json_data["companies"])
        targets = SBTi.data.get_targets(data_providers, json_data["companies"])
        portfolio_data = pd.merge(left=company_data, right=targets, left_on='company_name', right_on='company_name')

        return {
            "POST Request": {
                'Status':200,
                'Data':portfolio_data.to_json(orient='records')
            }
        }


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
api.add_resource(import_portfolio, '/import_portfolio')
api.add_resource(data_provider, '/data_provider')

if __name__ == '__main__':
    app.run(debug=True)  # important to mention debug=True

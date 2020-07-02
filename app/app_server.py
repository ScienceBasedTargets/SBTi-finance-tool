import json
import os

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

    def _get_data_providers(self, json_data):
        # Check which data providers, in which order, should be used
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

        json_data = request.get_json(force=True)
        data_providers = self._get_data_providers(json_data)

        default_score = self.config["default_score"]
        if "default_score" in json_data:
            default_score = json_data["default_score"]
        temperature_score = TemperatureScore(fallback_score=default_score)

        company_data = SBTi.data.get_company_data(data_providers, json_data["companies"])
        targets = SBTi.data.get_targets(data_providers, json_data["companies"])
        portfolio_data = pd.merge(left=company_data, right=targets, left_on='company_name', right_on='company_name')

        for company in json_data["companies"]:
            portfolio_data.loc[portfolio_data['company_name'] == company["company_name"], "portfolio_weight"] = company["portfolio_weight"]
            portfolio_data.loc[portfolio_data['company_name'] == company["company_name"], "investment_value"] = company["investment_value"]

        scores = temperature_score.calculate(portfolio_data)

        # Filter scope (s1s2, s3 or s1s2s3)
        if "filter_scope_category" in json_data:
            scores = scores[scores["scope_category"].isin(json_data["filter_scope_category"])]

        # Filter timeframe (short, mid, long)
        if "filter_time_frame" in json_data:
            scores = scores[scores["time_frame"].isin(json_data["filter_time_frame"])]

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
    """

    def __init__(self):
        super().__init__()

    def get(self):
        return {'data_providers': [{"name": data_provider["name"], "type": data_provider["type"]}
                                   for data_provider in self.config["data_providers"]]}


class portfolio_coverage(BaseEndpoint):
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

    def get(self):
        return {'GET Request': 'Hello World'}

    def post(self):
        return {'POST Request': 'Hello World'}


class documentation_endpoint(Resource):
    def get(path):
        return send_from_directory('static', path)


class import_portfolio(Resource):
    """
    This class allows the client to import and replace portfolios. Multiple HTTP Protocols are available for
    this resource.
    """

    def get(self):
        return {'GET Request': 'Hello World'}

    def post(self):
        files.save(request.files['file'])
        path = str(sorted(Path(PATH + '/files/').iterdir(), key=os.path.getmtime, reverse=True)[0])
        file_name = path.split("""\\""")[-1]

        return {'POST Request': {'Response': {'Status Code': 200, 'Message': 'File Saved', 'File': file_name}}}

    def put(self):
        remove_doc = request.args.get('document_replace')
        for root, dirs, file in os.walk(PATH):
            for f in file:
                if remove_doc == f.split('.')[0]:
                    os.remove(os.path.join(root, f))
                    files.save(request.files['file'])
                    return {'PUT Request': {
                        'Response': {'Status Code': 200, 'Message': 'File Replaced', 'Replaced File': remove_doc}}}
        return {
            'PUT Request': {'Response': {'Status Code': 404, 'Error Message': 'File Not Found', 'File': remove_doc}}}

class data_provider(Resource):
    """
    This class allows the client to receive information from the data provider. Multiple HTTP Protocols are available for
    this resource.
    """

    def get(self):
        return {'GET Request':'Hello World'}

    def post(self):
        data = request.get_json()

        # 0: data_provider_input
        data_provider = DataProvider(pd.DataFrame.from_dict(data, orient='index'))
        combined_data = pd.merge(data_provider.company_data(),data_provider.target_data(),how='inner',on='company_name')

        return {'POST Request':str(combined_data)}



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

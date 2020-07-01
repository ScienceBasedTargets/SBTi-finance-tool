import os

import pandas as pd
from pathlib import Path
from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api, reqparse
from flask_swagger_ui import get_swaggerui_blueprint
from flask_uploads import UploadSet, configure_uploads, ALL


import SBTi
from SBTi.data.csv import CSVProvider
from SBTi.portfolio_aggregation import PortfolioAggregationMethod
from SBTi.portfolio_coverage_tvp import PortfolioCoverageTVP
from SBTi.temperature_score import TemperatureScore

PATH = 'C:/Projects/SBTi/documents'
app = Flask(__name__)
files = UploadSet('files',ALL)
app.config['UPLOADS_DEFAULT_DEST'] = PATH
api = Api(app)



class temp_score(Resource):

    def __init__(self):
        self.temperature_score = TemperatureScore()
        self.data_providers = [

            # One of these replaced with excel connector
            CSVProvider({
                "path": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                     "data_test_waterfall_a.csv"),
                "path_targets": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                             "data_test_temperature_score_targets.csv")
            }),
            CSVProvider({
                "path": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                     "data_test_waterfall_b.csv"),
                "path_targets": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                             "data_test_temperature_score_targets.csv")
            }),
            CSVProvider({
                "path": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                     "data_test_waterfall_c.csv"),
                "path_targets": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                             "data_test_temperature_score_targets.csv")
            }),
        ]
        self.aggregation_map = {
            "WATS": PortfolioAggregationMethod.WATS,
            "TETS": PortfolioAggregationMethod.TETS,
            "MOTS": PortfolioAggregationMethod.MOTS,
            "EOTS": PortfolioAggregationMethod.EOTS,
            "ECOTS": PortfolioAggregationMethod.ECOTS,
            "AOTS": PortfolioAggregationMethod.AOTS
        }

    def get(self):
        return {'GET Request': 'Hello World'}

    def post(self):




        json_data = request.get_json(force=True)
        company_data = SBTi.data.get_company_data(self.data_providers, json_data["companies"])
        targets = SBTi.data.get_targets(self.data_providers, json_data["companies"])
        data = pd.merge(left=company_data, right=targets, left_on='company_name', right_on='company_name')

        for company in json_data["companies"]:
            data.loc[data['company_name'] == company["company_name"], "portfolio_weight"] = company["portfolio_weight"]
            data.loc[data['company_name'] == company["company_name"], "investment_value"] = company["investment_value"]

        scores = self.temperature_score.calculate(data)
        aggregations = self.temperature_score.aggregate_scores(scores,
                                                               self.aggregation_map[json_data["aggregation_method"]])
        return {
            "aggregated_scores": aggregations,
            "companies": scores[["company_name", "scope_category", "time_frame", "temperature_score"]].to_dict(
                orient="records")
        }


class portfolio_coverage(Resource):
    def __init__(self):
        self.portfolio_coverage_tvp = PortfolioCoverageTVP()
        self.data_providers = [
            CSVProvider({
                "path": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                     "data_test_waterfall_a.csv"),
                "path_targets": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                             "data_test_temperature_score_targets.csv")
            }),
            CSVProvider({
                "path": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                     "data_test_waterfall_b.csv"),
                "path_targets": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                             "data_test_temperature_score_targets.csv")
            }),
            CSVProvider({
                "path": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                     "data_test_waterfall_c.csv"),
                "path_targets": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                             "data_test_temperature_score_targets.csv")
            }),
        ]
        self.aggregation_map = {
            "WATS": PortfolioAggregationMethod.WATS,
            "TETS": PortfolioAggregationMethod.TETS,
            "MOTS": PortfolioAggregationMethod.MOTS,
            "EOTS": PortfolioAggregationMethod.EOTS,
            "ECOTS": PortfolioAggregationMethod.ECOTS,
            "AOTS": PortfolioAggregationMethod.AOTS
        }

    def get(self):
        return {'GET Request': 'Hello World'}

    def post(self):
        json_data = request.get_json(force=True)
        company_data = SBTi.data.get_company_data(self.data_providers, json_data["companies"])
        targets = SBTi.data.get_targets(self.data_providers, json_data["companies"])
        data = pd.merge(left=company_data, right=targets, left_on='company_name', right_on='company_name')

        for company in json_data["companies"]:
            data.loc[data['company_name'] == company["company_name"], "portfolio_weight"] = company["portfolio_weight"]
            data.loc[data['company_name'] == company["company_name"], "investment_value"] = company["investment_value"]

        coverage = self.portfolio_coverage_tvp.get_portfolio_coverage(data,
                                                                      self.aggregation_map[
                                                                          json_data["aggregation_method"]])
        return {
            "coverage": coverage,
        }


class data(Resource):
    def __init__(self):
        self.portfolio_coverage_tvp = PortfolioCoverageTVP()
        self.data_providers = [
            CSVProvider({
                "path": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                     "data_test_waterfall_a.csv"),
                "path_targets": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                             "data_test_temperature_score_targets.csv")
            }),
            CSVProvider({
                "path": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                     "data_test_waterfall_b.csv"),
                "path_targets": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                             "data_test_temperature_score_targets.csv")
            }),
            CSVProvider({
                "path": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                     "data_test_waterfall_c.csv"),
                "path_targets": os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "test", "inputs",
                                             "data_test_temperature_score_targets.csv")
            }),
        ]
        self.aggregation_map = {
            "WATS": PortfolioAggregationMethod.WATS,
            "TETS": PortfolioAggregationMethod.TETS,
            "MOTS": PortfolioAggregationMethod.MOTS,
            "EOTS": PortfolioAggregationMethod.EOTS,
            "ECOTS": PortfolioAggregationMethod.ECOTS,
            "AOTS": PortfolioAggregationMethod.AOTS
        }

    def get(self):
        return {'GET Request': 'Hello World'}

    def post(self):
        json_data = request.get_json(force=True)
        company_data = SBTi.data.get_company_data(self.data_providers, json_data["companies"])
        targets = SBTi.data.get_targets(self.data_providers, json_data["companies"])
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
        return {'GET Request':'Hello World'}

    def post(self):
        files.save(request.files['file'])
        path = str(sorted(Path(PATH + '/files/').iterdir(), key=os.path.getmtime,reverse=True)[0])
        file_name = path.split("""\\""")[-1]

        return{'POST Request': {'Response':{'Status Code':200,'Message':'File Saved','File':file_name}}}

    def put(self):
        remove_doc = request.args.get('document_replace')
        for root, dirs, file in os.walk(PATH):
            for f in file:
                if remove_doc == f.split('.')[0]:
                    os.remove(os.path.join(root, f))
                    files.save(request.files['file'])
                    return {'PUT Request': {'Response': {'Status Code': 200, 'Message': 'File Replaced', 'Replaced File': remove_doc}}}
        return {'PUT Request': {'Response':{'Status Code':404,'Error Message': 'File Not Found','File':remove_doc}}}



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
api.add_resource(data, '/data/')
api.add_resource(report, '/report/')
api.add_resource(documentation_endpoint, '/static/<path:path>')
api.add_resource(import_portfolio, '/import_portfolio')


if __name__ == '__main__':
    app.run(debug=True)  # important to mention debug=True

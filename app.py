from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api, reqparse
from flask_swagger_ui import get_swaggerui_blueprint
import os
import pandas as pd
from flask_uploads import UploadSet, configure_uploads, ALL
from pathlib import Path
from SBTi.temperature_score import TemperatureScore
from protocol.target_valuation_protocol import TargetValuationProtocol
from data_provider.data_provider_input import DataProvider


PATH = 'C:/Projects/SBTi/documents'
app = Flask(__name__)
files = UploadSet('files',ALL)
# app.config['PROPAGATE_EXCEPTIONS'] = True # To allow flask propagating exception even if debug is set to false on app
app.config['UPLOADS_DEFAULT_DEST'] = PATH
configure_uploads(app,files)
api = Api(app)


class temp_score(Resource):
    """
    This class acts as a resource for the API to handle Temperature Score. Multiple HTTP Protocols are available for
    this resource.
    """


    def get(self):
        return {'GET Request':'Hello World'}

    def post(self):
        data = request.get_json()

        # 0: data_provider_input
        data_provider = DataProvider(pd.DataFrame.from_dict(data, orient='index'))
        combined_data = pd.merge(data_provider.company_data(),data_provider.target_data(),how='inner',on='company_name')

        # 1: TargetValuationProtocol
        target_valuation_protocol = TargetValuationProtocol(combined_data)
        target_valuation_protocol.target_valuation_protocol()

        # 2: TemperatureScore

        return {'POST Request':str(target_valuation_protocol.data)}


class portfolio_coverage(Resource):
    """
    This class acts as a resource for the API to handle Portfolio Coverage. Multiple HTTP Protocols are available for
    this resource.
    """

    parser = reqparse.RequestParser()
    parser.add_argument('aggregation_method', type=float, required=True, help="This field cannot be left blank!")


    def get(self):
        return {'GET Request':'Hello World'}

    def post(self):
        data = portfolio_coverage.parser.parse_args()
        aggregation_method = data['aggregation_method']
        temperature_default = data['temperature_default']
        return{'POST Request': 'File Save'}




class report(Resource):
    """
    This class acts as a resource for the API to handle Reporting functionality. Multiple HTTP Protocols are available for
    this resource.
    """

    def get(self):
        return {'GET Request':'Hello World'}

    def post(self):
        return {'POST Request':'Hello World'}


class documentation_endpoint(Resource):
    """
    This class acts creates a documentation endpoint using Swagger.
    """

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


SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name':'SBTi-API'
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
api.add_resource(temp_score, '/temperature_score')
api.add_resource(portfolio_coverage, '/portfolio_coverage')
api.add_resource(report, '/report')
api.add_resource(documentation_endpoint, '/static/<path:path>')
api.add_resource(import_portfolio, '/import_portfolio')

if __name__ == '__main__':
    app.run(debug=True)  # important to mention debug=True



# TESTING
# x  = {
# 	"0":{
# 		"company_name":"A",
# 		"company_id":1123
# 	},
# 	"1":{
# 		"company_name":"B",
# 		"company_id":4231
# 	},
# 	"2":{
# 		"company_name":"C",
# 		"company_id":"15AB43"
# 	},
# 	"3":{
# 		"company_name":"D",
# 		"company_id":"da51"
# 	}
# }
#
# input_data = pd.DataFrame.from_dict(x, orient='index')
#

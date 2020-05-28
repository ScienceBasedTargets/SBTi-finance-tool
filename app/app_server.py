from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api, reqparse
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True  # To allow flask propagating exception even if debug is set to false on app
api = Api(app)


class temp_score(Resource):

    def get(self):
        return {'GET Request': 'Hello World'}

    def post(self):
        return {'POST Request': 'Hello World'}


class portfolio_coverage(Resource):

    def get(self):
        return {'GET Request': 'Hello World'}

    def post(self):
        return {'POST Request': 'Hello World'}


class report(Resource):

    def get(self):
        return {'GET Request': 'Hello World'}

    def post(self):
        return {'POST Request': 'Hello World'}


class documentation_endpoint(Resource):
    def get(path):
        return send_from_directory('static', path)


SWAGGER_URL = '/swagger'
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
api.add_resource(report, '/report/')
api.add_resource(documentation_endpoint, '/static/<path:path>')

if __name__ == '__main__':
    app.run(debug=True)  # important to mention debug=True

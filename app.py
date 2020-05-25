from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required, current_identity

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True # To allow flask propagating exception even if debug is set to false on app
api = Api(app)

class temp_score(Resource):

    # parameters
    # parser = reqparse.RequestParser()
    # parser.add_argument('price',
    #     type=float,
    #     required=True,
    #     help="This field cannot be left blank!"
    # )

    def get(self):
        return {'GET Request':'Hello World'}

    def post(self):
        return {'POST Request':'Hello World'}


class portfolio_coverage(Resource):

    def get(self):
        return {'GET Request':'Hello World'}

    def post(self):
        return {'POST Request':'Hello World'}


class report(Resource):

    def get(self):
        return {'GET Request':'Hello World'}

    def post(self):
        return {'POST Request':'Hello World'}


api.add_resource(temp_score, '/temperature_score/')
api.add_resource(portfolio_coverage, '/portfolio_coverage/')
api.add_resource(report, '/report/')

if __name__ == '__main__':
    app.run(debug=True)  # important to mention debug=True
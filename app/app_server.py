# -*- coding: utf-8 -*-
"""
Define flask application instance.
"""
from flask import Flask, jsonify
from SBTi.reporting import Reporting

app = Flask(__name__)  # setup app


@app.route("/", methods=["GET"])
def hello_world():
    reporting = Reporting()
    return jsonify({"message": "I'm a teapot"}), 418

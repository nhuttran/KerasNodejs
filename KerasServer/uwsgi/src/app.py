import os
import logging
from flask_api import status
from flask import Flask, make_response, jsonify, Blueprint, render_template, request, Response, abort
#from flask_cors import CORS, cross_origin
import json
from commons import Utils
from controllers.AuthController import authApp
from controllers.FaceController import faceApp
from controllers.WorkerController import workerApp

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')
app = Flask(__name__)

app.register_blueprint(authApp, url_prefix='/')
app.register_blueprint(faceApp, url_prefix='/')
app.register_blueprint(workerApp, url_prefix='/')

@app.route("/")
def index():
    html = "<h3>Welcome CSM System!</h3>"
    return html.format()

@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
def error_handler(error):
    logging.info("error_handler %d" % error.code)
    resp = jsonify({"statusCode": error.code, "errorJson": error.description, "errorText": ""})
    return resp, 200

if __name__ == '__main__':
    app.run()

import sys
import json
sys.path.append('../')
import logging
from flask_api import status
from flask import Flask, send_from_directory, make_response, jsonify, Blueprint, render_template, request, Response, abort
from commons import EnvConfig, Utils
from services.FacesService import Faces

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')
faceApp = Blueprint("faceApp", __name__)

@faceApp.route("/searchFaceStatus", methods=["POST"])
@Utils.content_type("application/json")
def search_face_status():
    # Faceステータス一覧を取得する
    face_status_list = Faces().get_face_status_list(request.get_json())
    # 処理結果の返却（JSON形式）
    return make_response(jsonify({"faceStatusList": face_status_list}))

@faceApp.route("/searchFaceIds", methods=["POST"])
@Utils.content_type("application/json")
def search_face_ids():
    # Face ID一覧を取得する
    face_id_list = Faces().get_face_ids(request.get_json())
    # 処理結果の返却（JSON形式）
    return make_response(jsonify({"faceIdList": face_id_list}))

@faceApp.route("/searchDetectFaceList", methods=["POST"])
@Utils.content_type("application/json")
def search_detect_face_list():
    # ログインIDにより、Face情報一覧を取得する
    detect_face_list = Faces().get_detect_face_list(request.get_json())
    # 処理結果の返却（JSON形式）
    return make_response(jsonify({"detectFaceList": detect_face_list}))

@faceApp.route("/uploadFace", methods=["POST"])
@Utils.content_type('application/json')
def upload_face():
    result = Faces().regist_detect_face(request.get_json())
    # 処理結果の返却（JSON形式）
    return make_response(jsonify({"status": result}))

@faceApp.route("/startTrain", methods=["POST"])
@Utils.content_type('application/json')
def start_train():
    # ワーカーへ学習依頼を送信する
    train_count = Faces().start_train_face(request.get_json())
    # 処理結果の返却（JSON形式）
    return make_response(jsonify({"trainCount": train_count}))

@faceApp.route("/getTrainStatus", methods=["GET", "POST"])
def get_train_status():
    train_status_list = Faces().get_train_status(request.get_json())
    # 処理結果の返却（JSON形式）
    return make_response(jsonify({"trainStatusList": train_status_list}))

@faceApp.route("/stopTrain/<loginId>", methods=["POST"])
def stop_train(login_id):
    result_dto = Faces().train_face(login_id)
    # 処理結果の返却（JSON形式）
    return Response(response=json.dumps(result_dto.__dict__), status=status.HTTP_200_OK)

@faceApp.route("/downloadModel", methods=["POST"])
def download_model():
    try:
        model_path, model_file = Faces().download_ml_model(request.get_json())
        response = make_response()
        response.data = open("{}/{}".format(model_path, model_file), "rb").read()
        response.headers['Content-Disposition'] = "attachment; filename='{}'".format(model_file)
        #response.headers["x-suggested-filename"] = model_file
        response.headers["x-filename"] = model_file
        response.headers["Access-Control-Expose-Headers"] = "x-filename"
        return response
    except FileNotFoundError:
        abort(404)

import sys
sys.path.append('../')
import os
from flask import Flask, Blueprint, request, make_response, jsonify, redirect, abort
import logging
from commons import Utils
from services.WorkerService import Worker

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')
workerApp = Blueprint("workerApp", __name__)

@workerApp.route("/worker/getTrainFaceInfo", methods=["POST"])
@Utils.content_type("application/json")
def get_train_face_info():
    # 学習情報を取得する
    encrypt_train_face_info = Worker().get_train_face_info(request.get_json())
    # 処理結果の返却（JSON形式）
    return make_response(jsonify({"encryptTrainFaceInfo": encrypt_train_face_info}))

@workerApp.route("/worker/sendDownloadStatus", methods=["POST"])
@Utils.content_type("application/json")
def send_download_status():
    # 学習情報を取得する
    result = Worker().send_download_status(request.get_json())
    # 処理結果の返却（JSON形式）
    return make_response(jsonify({"status": result}))

@workerApp.route("/worker/sendTrainStatus", methods=["POST"])
@Utils.content_type("application/json")
def send_train_status():
    # 学習情報を取得する
    result = Worker().send_train_status(request.get_json())
    # 処理結果の返却（JSON形式）
    return make_response(jsonify({"status": result}))

@workerApp.route("/worker/sendStatusError", methods=["POST"])
@Utils.content_type("application/json")
def send_status_error():
    # 学習情報を取得する
    result = Worker().send_status_error(request.get_json())
    # 処理結果の返却（JSON形式）
    return make_response(jsonify({"status": result}))

@workerApp.route("/worker/sendTrainFinish", methods=["POST"])
@Utils.content_type("application/json")
def send_train_finish():
    # 学習情報を取得する
    result = Worker().send_train_finish(request.get_json())
    # 処理結果の返却（JSON形式）
    return make_response(jsonify({"status": result}))

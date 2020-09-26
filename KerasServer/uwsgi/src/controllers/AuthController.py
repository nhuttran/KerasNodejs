import sys
sys.path.append('../')
import os
from flask import Flask, Blueprint, request, make_response, jsonify, redirect, abort
import json
import logging
import datetime
from commons import Utils
from services.AuthService import LoginAuth

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')
authApp = Blueprint("authApp", __name__)

@authApp.route('/auth/login', methods=["POST"])
@Utils.content_type("application/json")
def login():
    data_json = request.get_json()
    login_id = data_json.get("loginId")
    password = data_json.get("password")
    worker_flg = data_json.get("workerFlg")
    if worker_flg is None:
        worker_flg = 0
    # ログイン確認
    is_success, encode_cookie_str, same_time_train_num = LoginAuth().login(login_id, password, worker_flg)
    response = make_response(jsonify({"loginStatus": is_success, "sameTimeTrainNum": same_time_train_num}))
    # 成功にログインした場合、ログイン情報をクッキーに保存する
    if is_success:
        response.set_cookie(os.environ["COOKIE_NAME"], encode_cookie_str, path='/',
                            domain=None, secure=None, httponly=False)
    return response

@authApp.route('/auth/logout', methods=["GET"])
def logout():
    response = make_response(jsonify({}))
    response.set_cookie(os.environ["COOKIE_NAME"], "", expires=0)  # Delete cookie
    return response

@authApp.route('/auth/is_login', methods=["GET", "POST"])
def is_login():
    # Cookieからログイン情報を取得する
    cookie_info = request.cookies.get(os.environ["COOKIE_NAME"])
    # Cookie情報の認証を行う
    login_id = LoginAuth().check_cookie(cookie_info)
    return login_id, 200
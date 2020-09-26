import os
import pickle
import logging
import json
import requests
from ..Utils.ManageAES import AESCipher
from ..Dto.RequestWorker import AuthTrainDto, RequestWorkerDto

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')

def login(worker_id, password):
    # ログインAPIをコールする
    url = os.environ["LOGIN_API"]
    url = url.replace("{BASE_URL}", os.environ["BASE_URL"])
    headers = {"Content-Type": "application/json"}
    params = {"loginId": worker_id, "password": password, "workerFlg": 1}
    response = requests.post(url=url, headers=headers, data=json.dumps(params))
    if response.status_code != 200:
        logging.info("サーバへログインできません。[worker id: %s]" % worker_id)
        return None
    login_info = response.json()
    # エンコードされたCookie情報、同時の学習許可回数を返す
    return response.cookies.get(os.environ["COOKIE_NAME"]), login_info.get("sameTimeTrainNum")

def get_train_face_info(worker_id, encode_cookie):
    # 学習情報取得APIをコールする
    url = os.environ["GET_TRAIN_FACE_INFO_API"]
    url = url.replace("{BASE_URL}", os.environ["BASE_URL"])
    headers = {"Content-Type": "application/json"}
    params = {"loginId": worker_id}
    cookies = {os.environ["COOKIE_NAME"]: encode_cookie}
    response = requests.post(url=url, headers=headers, data=json.dumps(params), cookies=cookies)
    train_face_info = response.json()
    if train_face_info.get("statusCode") is not None:
        logging.info("学習情報が取得できません。[worker id: %s]" % worker_id)
        return None

    encrypt_train_face_info = train_face_info.get("encryptTrainFaceInfo")
    if encrypt_train_face_info is None:
        logging.info("学習情報がありません。[worker id: %s]" % worker_id)
        return None

    # JSON情報をデコードする
    decrypt_train_face_str = AESCipher().decrypt(os.environ["AES_PSK"], encrypt_train_face_info)
    return AuthTrainDto.from_json_str(decrypt_train_face_str)

def send_download_status(worker_id, encode_cookie, user_id, train_kbn, download_status):
    """
    サーバへダウンロード状況通知を送信する
    """
    # ダウンロード状況通知APIをコールする
    url = os.environ["SEND_DOWNLOAD_STATUS_API"]
    url = url.replace("{BASE_URL}", os.environ["BASE_URL"])
    headers = {"Content-Type": "application/json"}
    params = {"loginId": worker_id, "userId": user_id, "trainKbn": train_kbn, "downloadStatus": download_status}
    cookies = {os.environ["COOKIE_NAME"]: encode_cookie}
    response = requests.post(url=url, headers=headers, data=json.dumps(params), cookies=cookies)
    train_face_info = response.json()
    if train_face_info.get("statusCode") is not None:
        logging.info("ダウンロード結果が送信できません。[worker id: %s]" % worker_id)
        return False
    return True

def send_train_status(worker_id, encode_cookie, user_id, train_kbn, current_epoch):
    """
    サーバへ学習状況通知を送信する
    """
    # 学習状況通知APIをコールする
    url = os.environ["SEND_TRAIN_STATUS_API"]
    url = url.replace("{BASE_URL}", os.environ["BASE_URL"])
    headers = {"Content-Type": "application/json"}
    params = {"loginId": worker_id, "userId": user_id, "trainKbn": train_kbn, "currentEpoch": current_epoch}
    cookies = {os.environ["COOKIE_NAME"]: encode_cookie}
    response = requests.post(url=url, headers=headers, data=json.dumps(params), cookies=cookies)
    train_face_info = response.json()
    if train_face_info.get("statusCode") is not None:
        logging.info("学習状況が送信できません。[worker id: %s]" % worker_id)
        return False
    return True

def send_status_error(worker_id, encode_cookie, user_id, train_kbn):
    """
    サーバへエラー通知を送信する
    """
    # エラー通知APIをコールする
    url = os.environ["SEND_STATUS_ERROR_API"]
    url = url.replace("{BASE_URL}", os.environ["BASE_URL"])
    headers = {"Content-Type": "application/json"}
    params = {"loginId": worker_id, "userId": user_id, "trainKbn": train_kbn}
    cookies = {os.environ["COOKIE_NAME"]: encode_cookie}
    response = requests.post(url=url, headers=headers, data=json.dumps(params), cookies=cookies)
    train_face_info = response.json()
    if train_face_info.get("statusCode") is not None:
        logging.info("エラー状況が送信できません。[worker id: %s]" % worker_id)
        return False
    return True

def send_train_finish(worker_id, encode_cookie, user_id, train_kbn, train_result_dto):
    """
    サーバへ学習完了通知を送信する
    """
    # 学習完了通知APIをコールする
    url = os.environ["SEND_TRAIN_FINISH_API"]
    url = url.replace("{BASE_URL}", os.environ["BASE_URL"])
    headers = {"Content-Type": "application/json"}
    params = {"loginId": worker_id, "userId": user_id, "trainKbn": train_kbn, "trainResultInfo": train_result_dto.to_json_str()}
    cookies = {os.environ["COOKIE_NAME"]: encode_cookie}
    response = requests.post(url=url, headers=headers, data=json.dumps(params), cookies=cookies)
    train_face_info = response.json()
    if train_face_info.get("statusCode") is not None:
        logging.info("学習状況結果が送信できません。[worker id: %s]" % worker_id)
        return False
    return True

if __name__ == "__main__":
    pass
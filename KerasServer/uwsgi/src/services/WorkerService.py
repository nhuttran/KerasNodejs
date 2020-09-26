import sys
sys.path.append('../')
import os
import json
import uuid
import logging
from flask import request, abort
from contextlib import contextmanager
from .CodeUtils import DELETE_SIGN, TRAIN_KBN, TRAIN_STATUS
from .AuthService import LoginAuth
from .Dao.TrainStatus import TrainStatusDao
from .Dao.RequestWorker import RequestWorkerDao
from .Dto.RequestWorker import AuthTrainDto
from .Dto.TrainResultInfo import TrainResultDto

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')

class Worker(LoginAuth):
    def __init__(self):
        super().__init__()

    def get_train_face_info(self, data_json):
        """
        学習情報を取得する
        :param data_json: JSONデータ
        :return: 学習情報
        """
        login_id = self.check_auth(data_json)
        encrypt_train_face_info = None
        # トランザクション開始
        self.trans_begin()
        train_status_dao = TrainStatusDao()
        request_worker_dao = RequestWorkerDao()
        train_status = train_status_dao.select_train_status(status=[TRAIN_STATUS.SENDED, TRAIN_STATUS.RESENDED])
        if train_status:
            # FTP接続情報を取得する
            ftp_host = os.environ["FTP_HOST"]
            ftp_port = os.environ["FTP_PORT"]
            ftp_user_id = os.environ["FTP_USER_ID"]
            ftp_password = os.environ["FTP_PASSWORD"]
            # ワーカーへ送信する学習情報を取得する
            request_worker_data = request_worker_dao.select(uuid_key=train_status.uuid_key)
            download_path_file = request_worker_data.download_path_file
            upload_path = request_worker_data.upload_path
            auth_train_dto = AuthTrainDto(ftp_host, ftp_port, ftp_user_id,
                                          ftp_password, download_path_file, upload_path)
            # 学習情報を暗号化する
            encrypt_train_face_info = self.encrypt(auth_train_dto.to_json_str())
            # 学習ステータス管理テーブルの更新
            train_status.status = TRAIN_STATUS.READY
            train_status_dao.update(train_status)
            # ワーカーリクエストテーブルの更新
            request_worker_data.worker_id = login_id
            request_worker_dao.update(request_worker_data)

        # トランザクション終了(コミット)
        self.trans_commit()
        return encrypt_train_face_info

    def send_download_status(self, data_json):
        """
        学習ステータスを更新する
        :param data_json: JSONデータ
        :return: True/False(エラーなし/エラーなし)
        """
        self.check_auth(data_json)
        user_id = data_json.get("userId")
        train_kbn = data_json.get("trainKbn")
        return self.update_train_status(user_id, train_kbn, TRAIN_STATUS.READY, TRAIN_STATUS.RUNNING)

    def send_train_status(self, data_json):
        """
        現在の学習回数を更新する
        :param data_json: JSONデータ
        :return: True/False(エラーなし/エラーなし)
        """
        self.check_auth(data_json)
        user_id = data_json.get("userId")
        train_kbn = data_json.get("trainKbn")
        current_epoch = data_json.get("currentEpoch")
        return self.update_train_status(user_id, train_kbn, TRAIN_STATUS.RUNNING, TRAIN_STATUS.RUNNING, current_epoch)

    def send_status_error(self, data_json):
        """
        エラーステータスを更新する
        :param data_json: JSONデータ
        :return: True/False(エラーなし/エラーなし)
        """
        self.check_auth(data_json)
        user_id = data_json.get("userId")
        train_kbn = data_json.get("trainKbn")
        return self.update_train_status(user_id, train_kbn, TRAIN_STATUS.RUNNING, TRAIN_STATUS.ERROR)

    def send_train_finish(self, data_json):
        """
        学習ステータスを更新する
        :param data_json: JSONデータ
        :return: True/False(エラーなし/エラーなし)
        """
        self.check_auth(data_json)
        user_id = data_json.get("userId")
        train_kbn = data_json.get("trainKbn")
        train_result_json_str = data_json.get("trainResultInfo")
        train_result_dto = TrainResultDto.from_json_str(train_result_json_str)
        return self.update_train_finish(user_id, train_kbn, train_result_dto)

    def update_train_status(self, user_id, train_kbn, before_status, after_status, current_epoch=None):
        """
        学習ステータスを更新する
        :param user_id: 学習のユーザーID
        :param train_kbn: 学習種類
        :param before_status: 更新前学習ステータス
        :param after_status: 更新後学習ステータス
        :param epoch: 現在の学習回数
        :return: True/False(エラーなし/エラーあり)
        """
        # トランザクション開始
        self.trans_begin()
        train_status_dao = TrainStatusDao()
        train_status = train_status_dao.select_one(user_id, train_kbn, before_status)
        if not train_status:
            return False
        # 学習ステータス管理テーブルの更新
        train_status.status = after_status
        if after_status == TRAIN_STATUS.FINISHED:
            train_status.current_epoch = train_status.epochs
        elif current_epoch is not None:
            train_status.current_epoch = current_epoch
        train_status_dao.update(train_status)
        # トランザクション終了(コミット)
        self.trans_commit()
        return True

    def update_train_finish(self, user_id, train_kbn, train_result_dto):
        """
        学習ステータスを更新する
        :param user_id: 学習のユーザーID
        :param train_kbn: 学習種類
        :param before_status: 更新前学習ステータス
        :param after_status: 更新後学習ステータス
        :param epoch: 現在の学習回数
        :return: True/False(エラーなし/エラーあり)
        """
        # トランザクション開始
        self.trans_begin()
        train_status_dao = TrainStatusDao()
        train_status = train_status_dao.select_one(user_id, train_kbn, TRAIN_STATUS.RUNNING)
        if not train_status:
            return False
        # 学習ステータス管理テーブルの更新
        train_status.status = TRAIN_STATUS.FINISHED
        train_status.current_epoch = train_status.epochs
        train_status_dao.update(train_status)
        # リクエストワーカーテーブルの更新
        # ワーカーへ送信する学習情報を取得する
        request_worker_dao = RequestWorkerDao()
        request_worker_data = request_worker_dao.select(uuid_key=train_status.uuid_key)
        request_worker_data.train_result = train_result_dto.to_json_str()
        request_worker_dao.update(request_worker_data)
        # トランザクション終了(コミット)
        self.trans_commit()
        return True
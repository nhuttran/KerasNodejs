import os
import pickle
import logging
import json
import requests
import ftplib
from ftplib import FTP
from contextlib import closing
from .utils import ManageCookie
from .dto.RequestWorker import AuthTrainDto, RequestWorkerDto

class ServerControl:
    user_id = None
    password = None

    def __init(self):
        pass

    def read_access_file(self):
        # 接続設定ファイルの読み込み
        connect_info = {}
        try:
            with open(os.environ["ACCESS_INFO_FILE"], "rb") as f:
                og_labels = pickle.load(f)
                connect_info = {k: v for k, v in og_labels.items()}
        except:
            logging.info("接続情報取得に失敗しました。")
            return False

        if len(connect_info) == 0:
            logging.info("接続情報がありません。")
            return False

        self.user_id = connect_info["user_id"]
        self.password = connect_info["password"]
        return True

    def get_auth_train_face(self):
        # サーバーへの接続情報を取得する
        result = self.read_access_file()
        if not result:
            return None

        # 学習ファイル情報取得APIをコールする
        url = os.environ["GET_TRAIN_FACE_API"]
        url = url.replace("{BASE_URL}", os.environ["BASE_URL"])
        headers = {'Content-Type': 'application/json'}
        params = {'loginId': self.user_id, 'password': self.password}
        response = requests.post(url=url, headers=headers, data=json.dumps(params))
        if response.status_code != 200:
            logging.info("FTPへの接続情報が取得できません。[user name: %s]" % self.user_id)
            return None

       train_face_info = response.json()
        if train_face_info is None:
            return None
        # JSON情報をデコードする
        decode_train_face_str = ManageCookie.decode_cookie(train_face_info["trainFaceInfo"])
        return AuthTrainDto.from_json(decode_train_face_str)

    def send_download_result(self, status):
        # サーバーへの接続情報を取得する
        result = self.read_access_file()
        if not result:
            return None

        # ダウンロード結果送信APIをコールする
        url = os.environ["SEND_DOWNLOAD_STATUS_API"]
        headers = {'Content-Type': 'application/json'}
        params = {'login_id': self.user_id, 'password': self.password}
        response = requests.post(url=url, headers=headers, data=json.dumps(params))
        if response.status_code != 200:
            logging.info("ダウンロード結果送信に失敗しました。[user name: %s]" % self.user_id)
            return False

    def download_file_from_ftp(self, save_path_file, auth_train_dto=AuthTrainDto()):
        logging.info("download_file_from_ftp START")

        try:
            with closing(ftplib.FTP()) as ftp:
                ftp.set_debuglevel(1)
                ftp.connect(auth_train_dto.ftpHost, int(auth_train_dto.ftpPort), int(60*2))
                ftp.login(auth_train_dto.ftpUserId, auth_train_dto.ftpPassword)
                train_path = os.path.dirname(auth_train_dto.downloadPathFile)
                train_file = os.path.basename(auth_train_dto.downloadPathFile)

                ftp.cwd(train_path)
                ftp.set_pasv(True)
                with open(save_path_file, 'wb') as file:
                    res = ftp.retrbinary(f'RETR %s' % train_file, file.write)

                    if not res.startswith('226 Transfer complete'):
                        logging.info("ファイルのダウンロードが終了できません. [%s]" % auth_train_dto.downloadPathFile)
                        os.remove(save_path_file)

                ftp.quit()
        except Exception as e:
            logging.info("例外エラーが発生しました。 {}".format(e))
            return False
        return True

    def upload_file_to_ftp(self, upload_path_file, ftp_info=FtpInfo()):
        with closing(ftplib.FTP()) as ftp:
            try:
                ftp.connect(ftp_info.host, ftp_info.port, ftp_info.timeout)
                ftp.login(ftp_info.user_id, ftp_info.password)
                ftp.set_pasv(True)
                with open(upload_path_file, 'rb') as file:
                    file_name = os.path.basename(upload_path_file)
                    save_path_file = "{}/{}".format(ftp_info.save_model_path, file_name)
                    # アップロード実行
                    ftp.storbinary(f'STOR {save_path_file}', file)
            except:
                logging.info("FTPにファイルがアップロードできません. [%s]" % upload_path_file)
                return False
        return True

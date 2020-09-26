import sys
sys.path.append('../')
import os
import uuid
from flask import request, abort
from contextlib import contextmanager
from commons import EnvConfig, Utils, ManageCookie, ManageAES
from .Entities.Database import db_session
from .Dto.LoginAuth import LoginAuthDto

class Initial(object):
    ENV = EnvConfig
    db_session = db_session
    ftp_host = os.environ["FTP_HOST"]
    ftp_port = os.environ["FTP_PORT"]
    ftp_user_id = os.environ["FTP_USER_ID"]
    ftp_password = os.environ["FTP_PASSWORD"]

    def __init__(self):
        super().__init__()

    """
    トランザクション開始
    """
    @contextmanager
    def trans_begin(self):
        # self.db_session.begin()
        yield

    """
    トランザクション終了(コミット)
    """
    @contextmanager
    def trans_commit(self):
        try:
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    """
    TimeZone時間を取得する
    """
    def get_time_zone(self, utc_time=None, format=None):
        return Utils.get_time_zone(utc_time, format)

    """
    uuid生成
    """
    def create_uuid_key(self) -> str:
        return str(uuid.uuid4())

    """
    JSON文字列をエンコードする
    """
    def encode_json(self, json_data_str) -> str:
        return ManageCookie.encode_cookie(os.environ["COOKIE_SSK"], json_data_str)

    """
    JSON文字列をデコードする
    """
    def decode_json(self, encode_json_str):
        decode_json_str = ManageCookie.decode_cookie(os.environ["COOKIE_SSK"], encode_json_str)
        return decode_json_str

    """
    暗号化
    """
    def encrypt(self, password):
        return ManageAES.AESCipher().encrypt(os.environ["AES_PSK"], password)

    """
    複合化
    """
    def decrypt(self, encrypt_password):
        return ManageAES.AESCipher().decrypt(os.environ["AES_PSK"], encrypt_password)

    """
    Cookieからログイン情報を取得する
    ※ ログイン情報が認証されたため、再認証が不要になる
    """
    def get_login_id(self) -> str:
        cookie_info = request.cookies.get(os.environ["COOKIE_NAME"])
        # ログイン認証情報をデコードする
        decode_cookie_str = self.decode_json(cookie_info)
        auth_login_dto = LoginAuthDto.from_json_str(decode_cookie_str)
        return auth_login_dto.loginId

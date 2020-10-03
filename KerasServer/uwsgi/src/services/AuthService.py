import os
import uuid
import logging
from flask import request, abort
from . import Initial
from .Dao.Account import AccountDao
from .Dao.Worker import WorkerDao
from .Dto.LoginAuth import LoginAuthDto

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')

class LoginAuth(Initial):

    def __init__(self):
        super().__init__()

    """
    ログイン認証
    """
    def login(self, login_id, password, worker_flg=None):
        if login_id is None:
            abort(400, {"message": "ログインIDを入力してください。"})

        same_time_train_num = None
        if worker_flg:
            # WorkerテーブルにユーザIDをパスワードを検索する
            login_data = WorkerDao().select(login_id, self.encrypt(password))
            if login_data:
                same_time_train_num = login_data.same_time_train_num
        else:
            # AccountテーブルにユーザIDをパスワードを検索する
            login_data = AccountDao().select(login_id, self.encrypt(password))
        is_success = (login_data is not None)
        encode_cookie_str = None
        if is_success:
            auth_cookie_dto = LoginAuthDto(os.environ["SYS_SSK"], login_id, self.get_time_zone())
            # ログイン認証情報をエンコードする
            encode_cookie_str = self.encode_json(auth_cookie_dto.to_json_str())
        return is_success, encode_cookie_str, same_time_train_num

    """
    リクエストから取得したJSON情報にログインIDが存在するかどうか確認する
    """
    def check_auth(self, data_json) -> str:
        login_id = data_json.get("loginId")
        if login_id is None:
            abort(405)
        return login_id

    """
    Cookie情報を認証する
    ※DB側にユーザIDが存在するかどうか判定しない
    """
    def check_cookie(self, cookie_info) -> bool:
        if not cookie_info:
            # 401 Unauthorizedを返す
            abort(401, {"message": "Authorization Failed. Please check if the credentials are correct"})

        try:
            # ログイン認証情報をデコードする
            decode_cookie_str = self.decode_json(cookie_info)
            auth_login_dto = LoginAuthDto.from_json_str(decode_cookie_str)
            # 認証キーが一致しない場合、
            if auth_login_dto.authKey != os.environ["SYS_SSK"]:
                # 401 Unauthorizedを返す
                abort(401, {"message": "Authorization Failed. Please check if the credentials are correct"})
            # 30分を超過した場合、再ログインを依頼する
            # TODO
        except Exception as e:
            # 401 Unauthorizedを返す
            abort(401, {"message": "Authorization Failed. Please check if the credentials are correct"})
        return auth_login_dto.loginId


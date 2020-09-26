import os
import psycopg2
from sqlalchemy.sql import text
from sqlalchemy import desc
from sqlalchemy.sql import func
from .. import Initial
from ..CodeUtils import DELETE_SIGN
from ..Entities.Database import db_session
from ..Entities.RequestWorker import RequestWorkerEntity

class RequestWorkerDao(Initial):
    def __init__(self):
        super().__init__()
        self.entity = RequestWorkerEntity

    def select(self, uuid_key):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.uuid_key == ("%s" % uuid_key))
        query = query.filter(self.entity.delete_sign == ("%s" % DELETE_SIGN.OFF))
        return query.one()

    def insert(self, entity):
        entity.delete_sign = DELETE_SIGN.OFF
        entity.delete_date = ""
        entity.insert_user_id = self.get_login_id()
        entity.insert_date = self.get_time_zone()
        entity.update_user_id = self.get_login_id()
        entity.update_date = self.get_time_zone()
        db_session.add(entity)

    def update(self, entity):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.uuid_key == ("%s" % entity.uuid_key))
        # 主キー以外の項目に値を設定する
        update_data = {}
        if entity.download_path_file is not None:
            update_data.update({self.entity.download_path_file: entity.download_path_file})
        if entity.upload_path is not None:
            update_data.update({self.entity.upload_path: entity.upload_path})
        if entity.worker_id is not None:
            update_data.update({self.entity.worker_id: entity.worker_id})
        if entity.train_result is not None:
            update_data.update({self.entity.train_result: entity.train_result})
        update_data.update({self.entity.update_user_id: self.get_login_id()})
        update_data.update({self.entity.update_date: self.get_time_zone()})
        query.update(update_data)

    def delete_logical(self, uuid_key):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.uuid_key == ("%s" % uuid_key))
        # 削除項目を更新する
        update_data = {}
        update_data.update({self.entity.delete_sign: DELETE_SIGN.ON})
        update_data.update({self.entity.delete_date: self.get_time_zone(format=self.ENV.FORMAT_YYYYMMDD)})
        update_data.update({self.entity.update_user_id: self.get_login_id()})
        update_data.update({self.entity.update_date: self.get_time_zone()})
        query.update(update_data)

    def delete(self, uuid_key):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.uuid_key == ("%s" % uuid_key))
        query.delete()

if __name__ == "__main__":
    pass
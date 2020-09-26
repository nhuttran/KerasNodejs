import os
import psycopg2
from sqlalchemy.sql import func
from .. import Initial
from ..CodeUtils import DELETE_SIGN
from ..Entities.Database import db_session
from ..Entities.Worker import WorkerEntity

class WorkerDao(Initial):
    def __init__(self):
        self.entity = WorkerEntity

    def select(self, worker_id, password):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.worker_id == ("%s" % worker_id))
        query = query.filter(self.entity.password == password)
        return query.first()

    def insert(self, entity=WorkerEntity()):
        entity.delete_sign = DELETE_SIGN.OFF
        entity.delete_date = ""
        entity.insert_user_id = self.get_login_id()
        entity.insert_date = self.get_time_zone()
        entity.update_user_id = self.get_login_id()
        entity.update_date = self.get_time_zone()
        db_session.add(entity)

    def update(self, entity=WorkerEntity()):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.worker_id == ("%s" % entity.worker_id))
        # 主キー以外の項目に値を設定する
        update_data = {}
        if entity.worker_name is not None:
            update_data.update({self.entity.worker_name: entity.worker_name})
        if entity.ip_address is not None:
            update_data.update({self.entity.ip_address: entity.ip_address})
        if entity.password is not None:
            update_data.update({self.entity.password: entity.password})
        if entity.same_time_train_num is not None:
            update_data.update({self.entity.same_time_train_num: entity.same_time_train_num})
        update_data.update({self.entity.update_user_id: self.get_login_id()})
        update_data.update({self.entity.update_date: self.get_time_zone()})
        query.update(update_data)

    def delete_logical(self, worker_id):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.worker_id == ("%s" % worker_id))
        # 削除項目を更新する
        update_data = {}
        update_data.update({self.entity.delete_sign: DELETE_SIGN.ON})
        update_data.update({self.entity.delete_date: self.get_time_zone(format=self.ENV.FORMAT_YYYYMMDD)})
        update_data.update({self.entity.update_user_id: self.get_login_id()})
        update_data.update({self.entity.update_date: self.get_time_zone()})
        query.update(update_data)

    def delete(self, worker_id):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.worker_id == ("%s" % worker_id))
        query.delete()

if __name__ == "__main__":
    pass
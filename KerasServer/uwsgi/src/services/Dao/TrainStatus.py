import os
import psycopg2
from sqlalchemy import asc, desc
from sqlalchemy.sql import func
from .. import Initial
from ..CodeUtils import DELETE_SIGN
from ..Entities.Database import db_session
from ..Entities.TrainStatus import TrainStatusEntity

class TrainStatusDao(Initial):
    def __init__(self):
        super().__init__()
        self.entity = TrainStatusEntity

    def select_all(self, user_id, train_kbn=None):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.user_id == ("%s" % user_id))
        if train_kbn is not None:
            query = query.filter(self.entity.train_kbn == ("%s" % train_kbn))
        query = query.filter(self.entity.delete_sign == ("%s" % DELETE_SIGN.OFF))
        return query.all()

    def select_one(self, user_id, train_kbn, status):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.user_id == ("%s" % user_id))
        query = query.filter(self.entity.train_kbn == ("%s" % train_kbn))
        query = query.filter(self.entity.status == ("%s" % status))
        return query.first()

    def select_train_status(self, status=[]):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.status.in_(status))
        query = query.filter(self.entity.delete_sign == ("%s" % DELETE_SIGN.OFF))
        query = query.order_by(asc(self.entity.seq))
        return query.first()

    def select_train_status_user(self, user_id, seq=None):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.user_id == ("%s" % user_id))
        if seq is not None:
            query = query.filter(self.entity.seq == ("%d" % seq))
        query = query.filter(self.entity.delete_sign == ("%s" % DELETE_SIGN.OFF))
        # SEQが設定ありの場合、1レコードのみ返す
        if seq is not None:
            return query.one()
        # 複数件をデフォルトとし返す
        return query.all()

    def get_max_seq(self, user_id):
        query = db_session.query(func.max(self.entity.seq).label("seq_max"))
        query = query.filter(self.entity.user_id == ("%s" % user_id))
        result = query.one()
        seq_max = 0
        if result.seq_max is not None:
            seq_max = result.seq_max
        return seq_max
    
    def insert(self, entity=TrainStatusEntity()):
        entity.delete_sign = DELETE_SIGN.OFF
        entity.delete_date = ""
        entity.insert_user_id = self.get_login_id()
        entity.insert_date = self.get_time_zone()
        entity.update_user_id = self.get_login_id()
        entity.update_date = self.get_time_zone()
        db_session.add(entity)

    def update(self, entity=TrainStatusEntity()):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.user_id == ("%s" % entity.user_id))
        query = query.filter(self.entity.seq == ("%d" % entity.seq))
        # 主キー以外の項目に値を設定する
        update_data = {}
        if entity.status is not None:
            update_data.update({self.entity.status: entity.status})
        if entity.learn_count is not None:
            update_data.update({self.entity.learn_count: entity.learn_count})
        if entity.epochs is not None:
            update_data.update({self.entity.epochs: entity.epochs})
        if entity.current_epoch is not None:
            update_data.update({self.entity.current_epoch: entity.current_epoch})
        if entity.uuid_key is not None:
            update_data.update({self.entity.uuid_key: entity.uuid_key})
        update_data.update({self.entity.update_user_id: self.get_login_id()})
        update_data.update({self.entity.update_date: self.get_time_zone()})
        query.update(update_data)

    def delete_logical(self, user_id, seq):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.user_id == ("%s" % user_id))
        query = query.filter(self.entity.seq == ("%d" % seq))
        # 削除項目を更新する
        update_data = {}
        update_data.update({self.entity.delete_sign: DELETE_SIGN.ON})
        update_data.update({self.entity.delete_date: self.get_time_zone(format=self.ENV.FORMAT_YYYYMMDD)})
        update_data.update({self.entity.update_user_id: self.get_login_id()})
        update_data.update({self.entity.update_date: self.get_time_zone()})
        query.update(update_data)

    def delete(self, user_id, seq=None):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.user_id == ("%s" % user_id))
        if seq is not None:
            query = query.filter(self.entity.seq == ("%d" % seq))
        query.delete()

if __name__ == "__main__":
    pass
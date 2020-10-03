import os
import psycopg2
from sqlalchemy.sql import text
from sqlalchemy import asc, desc
from sqlalchemy.sql import func
from .. import Initial
from ..CodeUtils import DELETE_SIGN
from ..Entities.Database import db_session
from ..Entities.DetectFace import DetectFaceEntity

class DetectFaceDao(Initial):
    def __init__(self):
        self.entity = DetectFaceEntity

    def select(self, user_id=None, face_id=None):
        sql = ""
        sql = sql + "SELECT "
        sql = sql + "   user_id,"
        sql = sql + "   face_id,"
        sql = sql + "   seq,"
        sql = sql + "   face_status_kbn,"
        sql = sql + "   encode(face_binary, 'base64') face_binary,"
        sql = sql + "   delete_sign,"
        sql = sql + "   delete_date "
        sql = sql + "FROM detect_face "
        sql = sql + "WHERE 1=1 "
        sql_where = {}
        if user_id is not None:
            sql = sql + " AND user_id = :user_id"
            sql_where.update({"user_id": user_id})
        if face_id is not None:
            sql = sql + " AND face_id = :face_id"
            sql_where.update({"face_id": face_id})
        return db_session.execute(text(sql), sql_where)

    def get_train_class(self, user_id=None):
        query = db_session.query(self.entity)
        if user_id is not None:
            query = query.filter(self.entity.user_id == ("%s" % user_id))
        # 削除サインを追加する
        query = query.filter(self.entity.delete_sign == "0")
        # ソート順
        query = query.order_by(asc(self.entity.face_id), asc(self.entity.face_status_kbn))
        return query.all()

    def get_max_seq(self, user_id, face_id):
        query = db_session.query(func.max(self.entity.seq).label("max_seq"))
        query = query.filter(self.entity.user_id == ("%s" % user_id), self.entity.face_id == ("%s" % face_id))
        result = query.one()
        seq_max = 0
        if result.max_age is not None:
            seq_max = result.max_age
        return seq_max

    def insert(self, entity=DetectFaceEntity()):
        entity.delete_sign = DELETE_SIGN.OFF
        entity.delete_date = ""
        entity.insert_user_id = self.get_login_id()
        entity.insert_date = self.get_time_zone()
        entity.update_user_id = self.get_login_id()
        entity.update_date = self.get_time_zone()
        db_session.add(entity)

    def update(self, entity=DetectFaceEntity()):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.user_id == ("%s" % entity.user_id))
        query = query.filter(self.entity.face_id == ("%s" % entity.face_id))
        query = query.filter(self.entity.seq == ("%s" % entity.seq))
        # 主キー以外の項目に値を設定する
        update_data = {}
        if entity.face_status_kbn is not None:
            update_data.update({self.entity.face_status_kbn: entity.face_status_kbn})
        update_data.update({self.entity.update_user_id: self.get_login_id()})
        update_data.update({self.entity.update_date: self.get_time_zone()})
        query.update(update_data)

    def delete_logical(self, user_id, face_id, seq):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.user_id == ("%s" % user_id))
        query = query.filter(self.entity.face_id == ("%s" % face_id))
        query = query.filter(self.entity.seq == ("%s" % seq))
        # 削除項目を更新する
        update_data = {}
        update_data.update({self.entity.delete_sign: DELETE_SIGN.ON})
        update_data.update({self.entity.delete_date: self.get_time_zone(format=self.ENV.FORMAT_YYYYMMDD)})
        update_data.update({self.entity.update_user_id: self.get_login_id()})
        update_data.update({self.entity.update_date: self.get_time_zone()})
        query.update(update_data)

    def delete(self, user_id, face_id, seq):
        query = db_session.query(self.entity)
        query = query.filter(self.entity.user_id == ("%s" % user_id))
        query = query.filter(self.entity.face_id == ("%s" % face_id))
        query = query.filter(self.entity.seq == ("%s" % seq))
        query.delete()

if __name__ == "__main__":
    pass
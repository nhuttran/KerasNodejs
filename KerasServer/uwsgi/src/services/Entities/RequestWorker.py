import sqlalchemy
from sqlalchemy import Column
from .Database import Base, db_engine

class RequestWorkerEntity(Base):
    """
    worker_listenテーブル
    """
    __tablename__ = "request_worker"
    uuid_key = Column(sqlalchemy.VARCHAR(36), primary_key=True)
    download_path_file = Column(sqlalchemy.VARCHAR(100), nullable=False)
    upload_path = Column(sqlalchemy.VARCHAR(100), nullable=False)
    worker_id = Column(sqlalchemy.CHAR(15), nullable=False)
    train_result = Column(sqlalchemy.VARCHAR(500), nullable=False)
    delete_sign = Column(sqlalchemy.CHAR(1), nullable=False)
    delete_date = Column(sqlalchemy.CHAR(8), nullable=False)
    insert_user_id = Column(sqlalchemy.CHAR(15))
    insert_date = Column(sqlalchemy.TIMESTAMP(timezone=True))
    update_user_id = Column(sqlalchemy.CHAR(15))
    update_date = Column(sqlalchemy.TIMESTAMP(timezone=True))

if __name__ == "__main__":
    Base.metadata.create_all(bind=db_engine)
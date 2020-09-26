import os
import json
import logging
import redis

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')

class RedisDB(object):
    db_redis = None
    queue_name = None
    train_name = None

    def __init__(self):
        try:
            # Redisサーバーに接続する
            self.db_redis = redis.StrictRedis(host=os.environ["REDIS_HOST"],
                                        port=os.environ["REDIS_PORT"],
                                        db=os.environ["REDIS_DB"],
                                        max_connections=4)
            # キュー名
            self.queue_name = "keras_queue"
            # フィールド名
            self.train_name = "train_file"
        except Exception:
            logging.info("Cannot get setting information.")
    
    def is_train_allowed(self, same_time_train_num):
        if self.db_redis is None:
            logging.info("Redisストアデータベースが起動されていません。")
            return False

        # redisストアデータベースから、現在の学習ステータスを取得する
        item_list = self.db_redis.lrange(self.queue_name, 0, -1)

        # PCごとの処理速度が異なるため、同時に学習回数が多すぎる場合、メモリオーバーが発生する。
        # そのため、PCの同時に学習許可回数を制御する必要がある。
        if len(item_list) >= same_time_train_num:
            # 同時に学習許可回数を超えた場合、現在処理をスキップする。
            logging.info("同時に学習許可回数を超えたため、処理終了します。")
            return False
        return True
    
    def insert_queue(self, file_name):
        # ダウンロード済み学習ファイル名をRedisストアデータベースへプッシュする
        self.db_redis.rpush(self.queue_name, json.dumps({self.train_name: str(file_name)}))
    
    def delete_queue(self, file_name):
        # redisストアデータベースから、現在の学習ステータスを取得する
        item_list = self.db_redis.lrange(self.queue_name, 0, -1)

        elements = []
        for item in item_list:
            data_json = json.loads(item.decode("utf-8"))
            fname = data_json.get(self.train_name)
            if file_name != fname:
                elements.append(fname)

        self.db_redis.ltrim(self.queue_name, len(item_list), -1)
        for fname in elements:
            self.db_redis.rpush(self.queue_name, json.dumps({"fname": str(fname)}))
        
        return True
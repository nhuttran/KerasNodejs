import os
import json
import numpy
import logging
from celery import Celery
from celery.schedules import crontab
from celery.task import periodic_task
from datetime import timedelta, datetime
from . import celery as tasks
from .CeleryController.RedisController import RedisDB
from .CeleryController.TrainController import TrainAuth
from .CeleryController.KerasModels.VGG16 import Vgg16Model
from .CeleryController.KerasModels.VGG19 import Vgg19Model
from .CeleryController.KerasModels.VGGFace import VggFaceModel
from .CeleryController.KerasModels.TrainModel import Trainer
from .CeleryController.Utils import CodeUtils, FormatUtils, Commons
import tensorflow as tf

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')

redis_db = RedisDB()
appcelery = Celery(os.environ["CELERY_PROJECT"])
appcelery.config_from_object(os.environ["CELERY_CONFIG"], namespace="CELERY")


@periodic_task(
    run_every=timedelta(seconds=30),  # 毎30秒実行
    name="auto_run_train",            # タスク名
    ignore_result=True                # 返却結果を無視する
)
def auto_run_train():
    train_auth = TrainAuth()
    login_status = train_auth.login()
    if not login_status:
        return
    
    same_time_train_num = train_auth.get_same_time_train_num()
    if not redis_db.is_train_allowed(same_time_train_num):
        return

    # 学習ファイルをダウンロードする
    download_status, auth_train_dto = train_auth.download_train_file()
    if not download_status:
        return

    # ダウンロードした学習ファイルを学習フォルダーへ移動する
    decrypt_status, train_kbn, train_path_file = train_auth.decrypt_train_file()
    if not decrypt_status:
        return

    # 学習ファイルダウンロード状況通知
    send_status = train_auth.send_download_status(download_status)
    if not send_status:
        return
    
    # 学習スタクを起動する
    if train_kbn in [CodeUtils.TRAIN_KBN.VGG16, CodeUtils.TRAIN_KBN.VGG19, CodeUtils.TRAIN_KBN.VGGFACE]:
        tasks.train_vgg.delay(train_kbn, train_path_file, auth_train_dto.to_json_str())
        #
        file_name = os.path.basename(train_path_file)
        redis_db.insert_queue(file_name)

@periodic_task(
    run_every=crontab(minute="0", hour="0"),  # 毎日深夜0:00に実行
    name="auto_send_to_server",               # タスク名
    ignore_result=True                        # 返却結果を無視する
)
def auto_send_to_server():
    pass

@appcelery.task
def train_vgg(train_kbn, train_path_file, auth_train_json_str):
    logging.info("VGG Start {}".format(train_path_file))

    # 開始日時を保持する
    start_time = Commons.get_time_zone(format=FormatUtils.FORMAT_TIME_ZONE)

    train_auth = TrainAuth()
    login_status = train_auth.login()
    if not login_status:
        return False

    # 学習データ取込
    load_status, epochs, class_labels, train_faces, labels = train_auth.load_train_data(train_path_file)
    if not load_status:
        return False

    # モデルファイル名を取得する
    json_path_file, h5_path_file = train_auth.get_h5_path_file(train_path_file)
    # H5形式のファイルによりMLModel形式のファイルを作成する
    ml_model_path_file = train_auth.get_mlmodel_path_file(train_path_file)
    x_data = numpy.array(train_faces)
    y_data = numpy.array(labels)
    x_data = x_data.astype('float32')
    if train_kbn == CodeUtils.TRAIN_KBN.VGG16:
        vgg_model = Vgg16Model(func_callback=train_auth.send_train_status)
    elif train_kbn == CodeUtils.TRAIN_KBN.VGG19:
        vgg_model = Vgg19Model(func_callback=train_auth.send_train_status)
    elif train_kbn == CodeUtils.TRAIN_KBN.VGGFACE:
        vgg_model = VggFaceModel(func_callback=train_auth.send_train_status)
    error_rate, accuracy_rate = vgg_model.train(class_labels, epochs, x_data, y_data,
                                                json_path_file, h5_path_file, ml_model_path_file)
    # 学習済み各ファイルをアップロードする
    upload_path_file_list = [json_path_file, h5_path_file, ml_model_path_file]
    upload_status = train_auth.upload_train_file(auth_train_json_str, upload_path_file_list)
    if not upload_status:
        train_auth.send_status_error()
        return False

    # 終了日時を保持する
    end_time = Commons.get_time_zone(format=FormatUtils.FORMAT_TIME_ZONE)
    # 合計時間
    start_time_convert = datetime.strptime(start_time, FormatUtils.FORMAT_TIME_ZONE)
    end_time_convert = datetime.strptime(end_time, FormatUtils.FORMAT_TIME_ZONE)
    total_time = end_time_convert - start_time_convert

    # 学習完了通知
    json_file= os.path.basename(json_path_file)
    h5_file = os.path.basename(h5_path_file)
    ml_file = os.path.basename(ml_model_path_file)
    train_auth.send_train_finish(json_file, h5_file, ml_file, start_time, end_time, total_time, error_rate, accuracy_rate)
    # 完了フォルダーへ学習データファイルを移動する
    train_auth.move_train_file(train_path_file)
    # redisストアデータベースからレコードを削除する
    file_name = os.path.basename(train_path_file)
    redis_db.delete_queue(file_name)
    logging.info("VGG Start {}".format(train_path_file))
    return True

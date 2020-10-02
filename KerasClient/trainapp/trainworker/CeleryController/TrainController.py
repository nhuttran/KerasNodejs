import os
import logging
import cv2
import base64
import numpy
import io
from PIL import Image
import pickle
import shutil
from .TrainModels import ApiModel, FTPModel
from .Dto.RequestWorker import AuthTrainDto, RequestWorkerDto
from .Dto.TrainResultInfo import TrainResultDto
from .Utils.ManageAES import AESCipher
from .Utils import CodeUtils
from .KerasModels.VGG16 import Vgg16Model

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')

class TrainAuth(object):
    worker_id = None
    password = None
    encode_cookie = None
    same_time_train_num = None

    user_id = None
    train_kbn = None
    train_file = None
    begin_path = None
    running_path = None
    finish_path = None

    def __init__(self):
        self.begin_path = os.environ["TRAIN_BEGIN_FOLDER"]
        self.running_path = os.environ["TRAIN_RUNNING_FOLDER"]
        self.finish_path = os.environ["TRAIN_FINISH_FOLDER"]
        self.load_access_api_info()

    def load_access_api_info(self):
        """
        接続設定ファイルの読み込み
        """
        # connect_info = {}
        # try:
        #     with open(os.environ["ACCESS_INFO_FILE"], "rb") as f:
        #         og_labels = pickle.load(f)
        #         connect_info = {k: v for k, v in og_labels.items()}
        # except:
        #     logging.info("接続情報取得に失敗しました。")
        #     return False

        # if len(connect_info) == 0:
        #     logging.info("接続情報がありません。")
        #     return False

        # worker_id = connect_info["worker_id"]
        # password = connect_info["password"]
        # AESクラスを生成する
        #aes_cipher = ManageAES.AESCipher(os.environ["SYS_SSK"])
        self.worker_id = "WK10000001"
        self.password = "demo"
    
    def login(self):
        # サーバへログインする
        self.encode_cookie, self.same_time_train_num = ApiModel.login(self.worker_id, self.password)
        if self.encode_cookie is None:
            logging.info("サーバへログインできません。[worker id: %s]" % self.worker_id)
            return False
        return True
    
    def get_same_time_train_num(self):
        """
        同時の学習許可回数を取得する
        """
        return self.same_time_train_num

    def download_train_file(self):
        """
        FTPから学習データファイルをダウンロードする
        """
        # 学習情報を取得する
        auth_train_dto = ApiModel.get_train_face_info(self.worker_id, self.encode_cookie)
        if auth_train_dto is None:
            return False, None

        self.train_file = os.path.basename(auth_train_dto.downloadPathFile)
        local_path_file = "{}/{}".format(self.begin_path, self.train_file)

        # FTPから学習ファイルをダウンロードする
        download_status = FTPModel.download_file(local_path_file, auth_train_dto)
        if not download_status:
            logging.info("ファイルがダウンロードできません。[worker id: %s]" % self.worker_id)
            return False, None

        return download_status, auth_train_dto
    
    def upload_train_file(self, auth_train_json_str, upload_path_file_list):
        """
        FTPへ学習済み各ファイルをアップロードする
        """
        download_status = FTPModel.upload_file(auth_train_json_str, upload_path_file_list)
        if not download_status:
            logging.info("ファイルがダウンロードできません。[worker id: %s]" % self.worker_id)
            return False

        return True

    def send_download_status(self, download_status):
        """
        学習ファイルダウンロード状況通知
        :param download_status: ダウンロードステータス
        """
        return ApiModel.send_download_status(self.worker_id, self.encode_cookie, self.user_id, self.train_kbn, download_status)

    def send_train_status(self, epoch):
        logging.info("\n user_id={}, train_kbn={}, epoch={}".format(self.user_id, self.train_kbn, epoch))
        return ApiModel.send_train_status(self.worker_id, self.encode_cookie, self.user_id, self.train_kbn, epoch)

    def send_status_error(self):
        return ApiModel.send_status_error(self.worker_id, self.encode_cookie, self.user_id, self.train_kbn)

    def send_train_finish(self, json_file, h5_file, ml_file, start_time, end_time, total_time, error_rate, accuracy_rate):
        """
        学習完了通知
        """
        train_result_dto = TrainResultDto(json_file, h5_file, ml_file, start_time, end_time, str(total_time), str(error_rate), str(accuracy_rate))
        return ApiModel.send_train_finish(self.worker_id, self.encode_cookie, self.user_id, self.train_kbn, train_result_dto)

    def decrypt_train_file(self):
        """
        AESで学習データファイルを複合化する
        """
        local_path_file = "{}/{}".format(self.begin_path, self.train_file)
        # 学習データファイルを読み込む
        with open(local_path_file, "rb") as file:
            encrypt_data = pickle.load(file)

        # AESで学習データを複合化する
        decrypt_json_str = AESCipher().decrypt(os.environ["AES_PSK"], encrypt_data)
        # JSON文字列をRequestWorkerDtoに変換する
        request_worker_dto = RequestWorkerDto.from_json_str(decrypt_json_str)

        # 学習するユーザーIDと学習種類を保持する
        self.user_id = request_worker_dto.userId
        self.train_kbn = request_worker_dto.trainKbn

        try:
            running_path_file = "{}/{}".format(self.running_path, self.train_file)
            # 複合化した学習データをファイルにpickle形式で保存する
            with open(running_path_file, mode='wb') as file:
                pickle.dump(request_worker_dto.to_json_str(), file)
            # ダウンロードした学習データファイルを削除する
            os.remove(local_path_file)
        except Exception:
            logging.info("学習フォルダーへファイルが移動できません. [%s]" % local_path_file)
            return False
        return True, self.train_kbn, running_path_file

    def get_h5_path_file(self, train_path_file):
        """
        H5ファイル名を取得する
        """
        file_name = os.path.basename(train_path_file)
        fname, _ = os.path.splitext(file_name)
        json_path_file = "{}/{}.{}".format(self.finish_path, fname, CodeUtils.MODEL_TYPE.JSON)
        h5_path_file = "{}/{}.{}".format(self.finish_path, fname, CodeUtils.MODEL_TYPE.H5)
        
        return json_path_file, h5_path_file

    def get_mlmodel_path_file(self, train_path_file):
        """
        MLModelファイル名を取得する
        """
        file_name = os.path.basename(train_path_file)
        fname, _ = os.path.splitext(file_name)
        model_path_file = "{}/{}.{}".format(self.finish_path, fname, CodeUtils.MODEL_TYPE.ML_MODEL)
        return model_path_file

    def load_train_data(self, train_path_file):
        """
        :param train_path_file: 学習データファイル
        """
        # 学習データファイルを読み込む
        with open(train_path_file, "rb") as file:
            train_json_str = pickle.load(file)
        
        # JSON文字列をRequestWorkerDtoに変換する
        request_worker_dto = RequestWorkerDto.from_json_str(train_json_str)

        # 学習するユーザーIDと学習種類を保持する
        self.user_id = request_worker_dto.userId
        self.train_kbn = request_worker_dto.trainKbn

        epochs = request_worker_dto.epochs
        class_labels = request_worker_dto.classLabels
        encode_base64_train_faces = request_worker_dto.trainFaces
        labels = request_worker_dto.labels

        # 画像がエンコードされたため、デコードする必要がある
        train_faces = []
        for idx, base64_encoded_data in enumerate(encode_base64_train_faces):
            #バイナリデータ <- base64でエンコードされたデータ
            img_binary = base64.b64decode(base64_encoded_data)
            #バイナリーストリーム <- バリナリデータ
            img_binarystream = io.BytesIO(img_binary)
            #PILイメージ <- バイナリーストリーム
            img_pil = Image.open(img_binarystream)
            #numpy配列(RGBA) <- PILイメージ
            img_numpy = numpy.asarray(img_pil)
            #numpy配列(BGR) <- numpy配列(RGBA)
            img_numpy_bgr = cv2.cvtColor(img_numpy, cv2.COLOR_RGBA2BGR)
            #画像を保存する場合
            # image_file = "{}/face_{}.jpg".format(self.running_path, idx)
            # cv2.imwrite(image_file, img_numpy_bgr)
            train_faces.append(img_numpy_bgr)
        
        return True, epochs, class_labels, train_faces, labels

    def move_train_file(self, train_path_file):
        try:
            os.remove(train_path_file)
        except Exception as e:
            logging.info("完了フォルダーへファイルが移動できません. [%s]" % train_path_file)

if __name__ == "__main__":
    os.environ["TRAIN_BEGIN_FOLDER"] = ""
    os.environ["TRAIN_RUNNING_FOLDER"] = ""
    os.environ["TRAIN_FINISH_FOLDER"] = ""
    train_auth = TrainAuth()
    train_path_file = "C:\\ProjectAI\\KerasNodeJs\\KerasClient\\traindata\\running\\VuonSaoBang99_2.pickle"
    load_status, epochs, class_labels, train_faces, labels = train_auth.load_train_data(train_path_file)
    x_data = numpy.array(train_faces)
    y_data = numpy.array(labels)
    x_data = x_data.astype('float32')

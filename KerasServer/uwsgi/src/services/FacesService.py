import sys
sys.path.append('../')
import os
import numpy
import cv2
import logging
import base64
import pickle
from flask import abort
from .AuthService import LoginAuth
from .CodeUtils import TRAIN_STATUS
from .Entities.DetectFace import DetectFaceEntity
from .Entities.TrainStatus import TrainStatusEntity
from .Entities.RequestWorker import RequestWorkerEntity
from .Dao.TrainKind import TrainKindDao
from .Dao.FaceStatus import FaceStatusDao
from .Dao.TrainStatus import TrainStatusDao
from .Dao.DetectFace import DetectFaceDao
from .Dao.FaceInfo import FaceInfoDao
from .Dao.RequestWorker import RequestWorkerDao
from .Dto.FaceInfo import FaceInfoDto
from .Dto.DetectFace import DetectFaceDto
from .Dto.FaceStatus import FaceStatusDto
from .Dto.RequestWorker import RequestWorkerDto
from .Dto.UploadFace import UploadFaceDto
from .Dto.TrainStatus import TrainStatusDto
from .Dto.TrainResultInfo import TrainResultDto

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')

class Faces(LoginAuth):
    def __init__(self):
        super().__init__()

    def get_face_status_list(self, data_json):
        """
        Faceステータス一覧を取得する
        :param data_json: JSONデータ
        :return: Faceステータス一覧
        """
        self.check_auth(data_json)
        face_status_list = []
        face_status_data = FaceStatusDao().select()
        for face_status in face_status_data:
            face_status_dto = FaceStatusDto(face_status.face_status_kbn, face_status.language,
                                            face_status.face_status_name)
            face_status_list.append(face_status_dto.to_json())
        return face_status_list

    def get_face_ids(self, data_json):
        """
        Face ID一覧を取得する
        :param data_json: JSONデータ
        :return: Face ID一覧
        """
        login_id = self.check_auth(data_json)
        face_id_list = []
        face_info_data = FaceInfoDao().select(user_id=login_id)
        for row in face_info_data:
            face_info_dto = FaceInfoDto(row.face_id, row.face_name)
            face_id_list.append(face_info_dto.to_json())
        return face_id_list

    def get_detect_face_list(self, data_json):
        """
        指定のFace IDに対する学習用フェイス情報一覧を取得する
        :param data_json: JSONデータ
        :return: 学習用フェイス情報一覧
        """
        login_id = self.check_auth(data_json)
        face_id = data_json.get("faceId")
        detect_face_list = []
        if int(face_id) < 0:
            face_id = None
        face_info_data = FaceInfoDao().select(user_id=login_id, face_id=face_id)
        for face_info in face_info_data:
            detect_face_data = DetectFaceDao().select(user_id=login_id, face_id=face_info.face_id)
            for detect_face in detect_face_data:
                #data_encode_bytes = base64.b64encode(detect_face.face_binary)
                #data_encode_str = data_encode_bytes.decode('utf-8')
                data_encode_str = detect_face.face_binary
                seq = detect_face.seq
                face_status_kbn = detect_face.face_status_kbn
                detect_face_dto = DetectFaceDto(face_info.face_id, face_info.face_name,
                                                seq, face_status_kbn, data_encode_str)
                detect_face_list.append(detect_face_dto.to_json())
        return detect_face_list

    def regist_detect_face(self, json_data) -> bool:
        """
        Face情報を登録する
        :param json_data: JSONデータ
        :return: True/False : エラーなし/エラーあり
        """
        login_id = self.check_auth(data_json)
        # トランザクション開始
        self.trans_begin()
        upload_face_dto = UploadFaceDto.from_json_str(json_data)
        img_binary = base64.b64decode(upload_face_dto.jpegData.img_base64)
        # jpg = numpy.frombuffer(img_binary, dtype= numpy.uint8)
        # img = cv2.imdecode(jpg, cv2.IMREAD_UNCHANGED)
        # (h, w) = img.shape[:2]

        detect_face_dao = DetectFaceDao()
        seq_id = detect_face_dao.get_max_seq(login_id, upload_face_dto.faceId)

        detect_face_entity = DetectFaceEntity()
        detect_face_entity.user_id(login_id)
        detect_face_entity.face_id(upload_face_dto.faceId)
        detect_face_entity.seq(seq_id + 1)
        detect_face_entity.face_status_kbn(upload_face_dto.faceStatus)
        detect_face_entity.face_binary(img_binary)
        # データ登録
        detect_face_dao.insert(detect_face_entity)

        # トランザクション終了(コミット)
        self.trans_commit()
        return True

    def start_train_face(self, data_json):
        """
        指定のログインIDに従ってワーカーへ学習依頼送信を行う
        :param data_json: JSONデータ
        :return: 学習種類カウンター
        """
        train_count_result = 0
        # トランザクション開始
        self.trans_begin()
        login_id = self.check_auth(data_json)
        train_kind_dao = TrainKindDao()
        train_status_dao = TrainStatusDao()
        request_worker_dao = RequestWorkerDao()
        # ワーカー側の学習ステータスを確認する
        train_status_data = train_status_dao.select_all(user_id=login_id)
        if len(train_status_data) > 0:
            for train_status in train_status_data:
                status = train_status.status
                train_kbn = train_status.train_kbn
                learn_count = train_status.learn_count + 1
                # 学習ステータスが1:依頼済、2:学習準備、3:学習中、4:学習済、5:再依頼済のいずれかを満たす場合、次のレコードへ進む
                if status in [TRAIN_STATUS.SENDED, TRAIN_STATUS.READY, TRAIN_STATUS.RUNNING,
                              TRAIN_STATUS.FINISHED, TRAIN_STATUS.RESENDED]:
                    continue
                train_count_result = train_count_result + 1
                # 未学習の場合
                if status == TRAIN_STATUS.NONE:
                    # ワーカーリクエストテーブルの登録
                    uuid_key = self.insert_request_worker(request_worker_dao, login_id, train_kbn)
                    # 学習ステータス管理テーブルの更新
                    train_status.learn_count = learn_count
                    train_status.status = TRAIN_STATUS.SENDED
                    train_status.uuid_key = uuid_key
                    train_status_dao.update(train_status)
                    # 次のレコードへ進む
                    continue
                # 6:キャンセル、9:エラーの場合
                # 論理削除を行う
                train_status_dao.delete_logical(train_status.user_id, train_status.seq)
                # UUIDキーが設定されている場合、ワーカーリクエストテーブルも論理削除する
                if train_status.uuid_key != "":
                    request_worker_dao.delete_logical(train_status.uuid_key)
                # 学習モデル種類取得
                train_kind_data = train_kind_dao.select(train_kbn=train_kbn)
                epochs = train_kind_data[0].epochs
                # 学習ステータスの設定
                if status in [TRAIN_STATUS.CANCELED, TRAIN_STATUS.ERROR]:
                    # キャンセルまたはエラーの場合、6:再依頼済とする
                    status = TRAIN_STATUS.RESENDED
                else:
                    # それ以外の場合、1:依頼済とする
                    status = TRAIN_STATUS.SENDED
                self.insert_train_status(train_status_dao, request_worker_dao, login_id, train_kbn, epochs, status, learn_count)
        else:
            # 学習モデル種類取得
            train_kind_data = train_kind_dao.select()
            for train_kind_info in train_kind_data:
                train_count_result = train_count_result + 1
                train_kbn = train_kind_info.train_kbn
                epochs = train_kind_info.epochs
                status = TRAIN_STATUS.SENDED
                self.insert_train_status(train_status_dao, request_worker_dao, login_id, train_kbn, epochs, status, 1)

        # トランザクション終了(コミット)
        self.trans_commit()
        return train_count_result

    def get_train_status(self, data_json):
        """
        学習ステータスを取得する
        :param data_json: JSONデータ
        :return: 学習ステータス
        """
        login_id = self.check_auth(data_json)
        train_kbn = data_json.get("trainKbn")
        train_status_dao = TrainStatusDao()
        train_status_data = train_status_dao.select_all(user_id=login_id, train_kbn=train_kbn)
        train_status_list = []
        if train_status_data:
            for train_status in train_status_data:
                train_kbn = train_status.train_kbn
                status = train_status.status
                epochs = train_status.epochs
                current_epoch = train_status.current_epoch
                train_status_dto = TrainStatusDto(train_kbn, status, epochs, current_epoch)
                train_status_list.append(train_status_dto.to_json())
        return train_status_list

    def download_ml_model(self, data_json):
        login_id = self.check_auth(data_json)
        user_id = data_json.get("userId")
        train_kbn = data_json.get("trainKbn")
        train_status_dao = TrainStatusDao()
        train_status_data = train_status_dao.select_one(user_id=user_id, train_kbn=train_kbn, status=TRAIN_STATUS.FINISHED)
        if not train_status_data:
            return None, None
        request_worker_dao = RequestWorkerDao()
        request_worker_data = request_worker_dao.select(uuid_key=train_status_data.uuid_key)
        train_result_dto = TrainResultDto.from_json_str(request_worker_data.train_result)
        return request_worker_data.upload_path, train_result_dto.mlFile

    def insert_request_worker(self, request_worker_dao, login_id, train_kbn, epochs):
        """
        ワーカーリクエスト情報を登録する
        :param request_worker_dao: リクエストワーカーDAO
        :param login_id: ログインID
        :param train_kbn: 学習種類
        :param epochs:
        :return: UUID文字列
        """
        # UUID生成
        uuid_key = self.create_uuid_key()
        # 学習用データを作成する
        request_worker_dto = self.get_data_train_status(login_id, train_kbn, epochs)
        # ワーカーへ送信する学習用ファイルを作成する
        download_path_file, upload_path = self.create_train_file(uuid_key, request_worker_dto)
        # ワーカーリクエストテーブルの登録
        request_worker_entity = RequestWorkerEntity()
        request_worker_entity.uuid_key = uuid_key
        request_worker_entity.download_path_file = download_path_file
        request_worker_entity.upload_path = upload_path
        request_worker_entity.worker_id = ""
        request_worker_entity.train_result = ""
        request_worker_dao.insert(request_worker_entity)
        # UUID文字列を返す
        return uuid_key

    def insert_train_status(self, train_status_dao, request_worker_dao, login_id, train_kbn, epochs, status, learn_count):
        """
        ワーカーへ送信する学習情報を登録する
        :param train_status_dao: 学習ステータスDAO
        :param request_worker_dao: リクエストワーカーDAO
        :param login_id: ログインID
        :param train_kbn: 学習種類
        :param epochs: 学習回数
        :param status: ステータス
        :param learn_count: 過去の学習回数
        :return: ワーカーへ送信する学習情報
        """
        # ワーカーリクエストテーブルの登録
        uuid_key = self.insert_request_worker(request_worker_dao, login_id, train_kbn, epochs)
        # 学習ステータス管理テーブルから最大SEQを取得する
        seq_id = train_status_dao.get_max_seq(user_id=login_id)
        # 学習ステータス管理テーブルの登録
        train_status_entity = TrainStatusEntity()
        train_status_entity.user_id = login_id
        train_status_entity.seq = seq_id + 1
        train_status_entity.train_kbn = train_kbn
        train_status_entity.status = status
        train_status_entity.learn_count = learn_count
        train_status_entity.epochs = epochs
        train_status_entity.current_epoch = 0
        train_status_entity.uuid_key = uuid_key
        train_status_dao.insert(train_status_entity)

    def convert_binary_to_image(self, image_binary):
        jpegData = numpy.frombuffer(image_binary, dtype=numpy.uint8)
        image = cv2.imdecode(jpegData, cv2.IMREAD_UNCHANGED)
        return image

    def get_data_train_status(self, login_id, train_kbn, epochs):
        """
        学習データを取得する
        :param login_id: ログインID
        :param train_kbn: 学習種類
        :return: 学習データ
        """
        detect_face_dao = DetectFaceDao()
        face_info_dao = FaceInfoDao()

        train_faces_unknown = []
        face_unknown_data = detect_face_dao.select(user_id=self.ENV.UNKNOWN_ID)
        labels_unknown = []
        index = 0
        for face_unknown in face_unknown_data:
            #binary_to_image = self.convert_binary_to_image(face_unknown.face_binary)
            #train_faces_unknown.append(binary_to_image)
            #train_face_b64encode_str = base64.b64encode(face_unknown.face_binary).decode()
            train_face_b64encode_str = face_unknown.face_binary
            train_faces_unknown.append(train_face_b64encode_str)
            labels_unknown.append(index)

        face_info_data = face_info_dao.select(user_id=login_id)
        detect_face_data = detect_face_dao.select(user_id=login_id)
        class_labels = set()
        class_labels.add(self.ENV.UNKNOWN_NAME)
        train_faces = []
        train_faces[0:0] = train_faces_unknown
        labels = []
        labels[0:0] = labels_unknown

        index = index + 1
        for detect_face in detect_face_data:
            face_id = detect_face.face_id
            face_status_kbn = detect_face.face_status_kbn
            #binary_to_image = self.convert_binary_to_image(detect_face.face_binary)
            #train_faces_unknown.append(binary_to_image)
            #train_face_b64encode_str = base64.b64encode(detect_face.face_binary).decode()
            train_face_b64encode_str = detect_face.face_binary
            face_name = None
            # FaceIDに従ってファイズ名を取得する
            for face_info in face_info_data:
                if face_id in face_info.face_id:
                    face_name = face_info.face_name
                    break
            class_labels.add("%s_%s" % (face_name, face_status_kbn))
            train_faces.append(train_face_b64encode_str)
            labels.append(index)

        class_label_array = []
        for class_label in class_labels:
            class_label_array.append(class_label)
        # ワーカーへ送信する学習データを返す
        return RequestWorkerDto(login_id, train_kbn, class_label_array, epochs, train_faces, labels)

    def create_train_file(self, uuid_key, request_worker_dto):
        """
        学習データファイルを作成する
        :param uuid_key: UUIDキー
        :param request_worker_dto: リクエストワーカーDTO
        :return: 作成された学習データファイル情報
        """
        download_path = ("%s/%s" % (os.environ["BRIDGE_TRAIN_FOLDER"], request_worker_dto.userId))
        upload_path = ("%s/%s" % (os.environ["BRIDGE_MODEL_FOLDER"], request_worker_dto.userId))
        try:
            if not os.path.exists(download_path):
                # 学習用フォルダーが存在しない場合、新規作成する
                os.mkdir(download_path)
            if not os.path.exists(upload_path):
                # モデルフォルダーが存在しない場合、新規作成する
                os.mkdir(upload_path)
        except Exception:
            abort(400, {"message": ("学習・モデルフォルダーが作成できません。システム管理者に連絡してください。(ユーザーID:%s)" % request_worker_dto.userId)})

        try:
            download_path_file = ("%s/%s_%s.pickle" % (download_path,
                                                       request_worker_dto.userId, request_worker_dto.trainKbn))
            # ファイルが存在する場合、ファイルを削除する
            if os.path.isfile(download_path_file):
                os.remove(download_path_file)
            # AESで学習データを暗号化する
            encrypt_json_str = self.encrypt(request_worker_dto.to_json_str())
            # pickle形式でファイルに保存する
            with open(download_path_file, mode='wb') as file:
                pickle.dump(encrypt_json_str, file)
        except Exception:
            abort(400, {"message": ("学習ファイルが作成できません。システム管理者に連絡してください。(ユーザーID:%s)" % request_worker_dto.userId)})
        return download_path_file, upload_path

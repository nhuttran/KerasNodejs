import os
import logging
import tensorflow.compat.v1 as tf
from keras.utils import np_utils
from keras.models import Sequential, Model
from keras.applications.vgg19 import VGG19
from keras.layers import Dense, Input, Flatten, Dropout, Activation
from keras import optimizers
from keras.callbacks import Callback
from sklearn.model_selection import train_test_split
from . import Callback, VGGModel

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')

class Vgg19Model(object):
    func_callback = None
    session = None
    config = None
    graph = None
    out_model = None
    input_tensor = None
    input_model = None
    model = None

    def __init__(self, func_callback):
        os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        self.func_callback = func_callback
        self.graph = tf.Graph()
        self.config = tf.ConfigProto(allow_soft_placement=True, intra_op_parallelism_threads=1, inter_op_parallelism_threads=1)
        # 最小限のGPUメモリのみ確保
        self.config.gpu_options.visible_device_list = "0"
        self.config.gpu_options.allow_growth = True
        # 合計GPUメモリの割合指定で確保
        self.config.gpu_options.per_process_gpu_memory_fraction = 0.5

    def train(self, class_labels, epochs, x_data, y_data, json_path_file, h5_path_file, ml_model_path_file):
        """
        学習実行
        :param class_labels: 学習クラス数
        :param epochs: 学習回数
        :param x_data: 学習データ
        :param y_data: 認識IDデータ
        :param json_path_file: JSON形式ファイル
        :param h5_path_file: H5形式ファイル
        :param ml_model_path_file: MLModel形式ファイル
        :return: 誤差率、精度率
        """
        nb_classes = len(class_labels)
        error_rate = None
        accuracy_rate = None
        y_data = np_utils.to_categorical(y_data, nb_classes)
        x_train, x_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.3)

        old_session = tf.keras.backend.get_session()
        with self.graph.as_default():
            self.session = tf.Session(config=self.config, graph=self.graph)
            tf.keras.backend.set_session(self.session)
            tf.keras.backend.set_learning_phase(1)
            self.session.run(tf.global_variables_initializer())
            # VGG19のINPUT情報を設定する
            self.input_tensor = Input(shape=(224, 224, 3))
            self.input_model = VGG19(include_top=False, weights="imagenet", input_tensor=self.input_tensor)
            # FC層の作成
            self.out_model = Sequential()
            self.out_model.add(Flatten(input_shape=self.input_model.output_shape[1:]))
            self.out_model.add(Dense(256, activation="relu"))
            self.out_model.add(Dropout(0.2))
            self.out_model.add(Dense(nb_classes, activation="softmax"))
            # VGG19とFC層を結合してモデルを作成
            self.model = Model(inputs=self.input_model.input, outputs=self.out_model(self.input_model.output))
            # 最後のconv層の直前までの層をfreeze
            # trainingするlayerを指定　VGG19では16,11,7,1など 21で全層固定
            for layer in self.model.layers[:11]:
                layer.trainable = False
            # 多クラス分類を指定
            self.model.compile(loss="categorical_crossentropy", optimizer=optimizers.SGD(lr=1e-4, momentum=0.9), metrics=["accuracy"])
            # 学習実施
            self.model.fit(x_train, y_train, epochs=epochs, verbose=0,
                           callbacks=[Callback.VggCallback(self.func_callback)])
            # テストデータで評価
            eval_result = self.model.evaluate(x_test, y_test, verbose=0)
            error_rate = eval_result[0]
            accuracy_rate = eval_result[1]
            # H5モデルとMLModelモデルを作成する
            VGGModel.create_h5_model(self.model, json_path_file, h5_path_file)
            VGGModel.create_ml_model(self.model, class_labels, ml_model_path_file)

        tf.keras.backend.set_session(old_session)
        return error_rate, accuracy_rate

if __name__ == "__main__":
    pass
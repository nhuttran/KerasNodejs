#import tensorflow.compat.v1 as tf
import keras.callbacks
import logging

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-10s) %(message)s')


class VggCallback(keras.callbacks.Callback):
    func_callback = None

    def __init__(self, func_callback):
        self.func_callback = func_callback

    def on_epoch_begin(self, epoch, logs={}):
        self.func_callback(epoch)

import os
import tensorflow as tf
from tensorflow import keras
import argparse
import sys

from data_manager import DataManager
from transformer import Transformer
from model import create_model
from callback import ModelCheckpoint, IPC

from types import SimpleNamespace
import yaml
from socket import *
import logging


def init_server(port):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(('', port))
    sock.listen(5)
    input_conn, addr = sock.accept()
    output_conn, addr = sock.accept()
    log_conn, addr = sock.accept()
    log = log_conn.makefile('w')

    input_conn.setblocking(False)
    output_conn.setblocking(False)
    log_conn.setblocking(False)

    sys.stdout = log
    sys.stderr = log
    return sock, input_conn, output_conn, log_conn

def train(config):
    dict_config = yaml.load(open(config, encoding='utf8'))
    config = SimpleNamespace(**dict_config)

    sock, input_conn, output_conn, log_conn = init_server(config.port)

    stop = IPC(input_conn, output_conn)

    transformer = Transformer(**dict_config)

    data_manager = DataManager(config.train_data, config.valid_data, config.class_info, config.project_dir, config.batch_size,
                                config.width, config.height, transformer)

    model = create_model(config.height, config.width, data_manager.class_num, config.network, config.loss, config.lr, config.transfer, config.train_all)

    if config.weights:
        saved_model = tf.keras.models.load_model(config.weights)
        for weight_in, weight_out in zip(model.variables[:-2], saved_model.variables[:-2]):
            weight_in.assign(weight_out)
        try:
            for weight_in, weight_out in zip(model.variables[-2:], saved_model.variables[-2:]):
                weight_in.assign(weight_out)
        except:
            print('restore base_model weights.')
        else:
            print('restore all weights.')

    checkpoint_dir = os.path.join(config.project_dir, 'checkpoint')
    if not os.path.exists(checkpoint_dir):
        os.mkdir(checkpoint_dir)

    reduce_lr = keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1)
    checkpoint = keras.callbacks.ModelCheckpoint(os.path.join(checkpoint_dir, config.network + '-' + 'ep{epoch:03d}-loss{loss:.3f}-val_loss{val_loss:.3f}.ckpt'))
    
    model.fit(
            data_manager.train_sequence(), 
            validation_data=data_manager.valid_sequence(),
            epochs=config.epochs, 
            shuffle = True,
            class_weight = data_manager.class_weight(),
            callbacks=[checkpoint, reduce_lr, stop],
            max_queue_size=10,
            workers=config.workers,
            use_multiprocessing=False
            )

    input_conn.close()
    output_conn.close()
    log_conn.close()
    sock.close()
    
            
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='训练命令行工具')
    parser.add_argument('--config', default=r'C:\Users\jiangwei\Desktop\新建文件夹\train_config.yaml')
    args = parser.parse_args()

    train(args.config)



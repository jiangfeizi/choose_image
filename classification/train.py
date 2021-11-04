
import os
import tensorflow as tf
from tensorflow import keras
import argparse
import sys

from data_manager import DataManager
from transformer import Transformer
from model import create_model
from callback import ModelCheckpoint, IPC
from utils import redirect_out, Config


def train(config):
    config = Config(config)

    if config.port:
        sys.stderr = open('error.txt', 'w', encoding='utf8')
        _, loss_sock = redirect_out(config.port, 'localhost')
        stop = IPC(loss_sock)

    transformer = Transformer(**config._config)

    data_manager = DataManager(config.train_data, config.valid_data, config.class_info, config.project_dir, config.batch_size,
                                config.width, config.height, transformer)

    model = create_model(config.height, config.width, data_manager.class_num, config.network, config.loss, config.lr, config.transfer, config.train_all)

    try:
        checkpoint = tf.train.Checkpoint(base_model=model.base_model, fc=model.fc)
        if config.weights:
            checkpoint.restore(config.weights)
            print('restore all weights.')
    except:
        checkpoint = tf.train.Checkpoint(base_model=model.base_model)
        if config.weights:
            checkpoint.restore(config.weights)
            print('restore base_model weights.')
    
    checkpoint_dir = os.path.join(config.project_dir, 'checkpoint')
    if not os.path.exists(checkpoint_dir):
        os.mkdir(checkpoint_dir)

    checkpoint = ModelCheckpoint(os.path.join(checkpoint_dir, config.network + '-' + 'ep{epoch:03d}-loss{loss:.3f}-val_loss{val_loss:.3f}.ckpt'))
    reduce_lr = keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1)
    
    model.fit(
            data_manager.train_sequence(), 
            validation_data=data_manager.valid_sequence(),
            epochs=config.epochs, 
            shuffle = True,
            class_weight = data_manager.class_weight(),
            callbacks=[checkpoint, reduce_lr, stop] if config.port else [checkpoint, reduce_lr],
            max_queue_size=10,
            workers=config.workers,
            use_multiprocessing=False
            )
            
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='训练命令行工具')
    parser.add_argument('--config', default=r'C:\Users\jiangwei\Desktop\新建文件夹\train_config.yaml')
    args = parser.parse_args()

    train(args.config)


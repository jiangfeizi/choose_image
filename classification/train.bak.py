
import imp
import os
from six import with_metaclass
from tensorflow import keras
import tensorflow as tf
from common import LossHistory, BinaryCrossentropy, NewOptimizer, CategoricalCrossentropy
import argparse
from data_manager import DataManager
from transformer import Transformer
from model import create_model


def train(args):

    transformer = Transformer(scale=args.scale, translate_percent_x=args.translate_percent_x, translate_percent_y=args.translate_percent_y,
                                    rotate=args.rotate, shear=args.shear, flip_lr=args.flip_lr, flip_ud=args.flip_ud, crop=args.crop, multiply=args.multiply,
                                    gaussian_noise=args.gaussian_noise, gaussian_blur=args.gaussian_blur, linear_contrast=args.linear_contrast)

    data_manager = DataManager(args.train_data, args.valid_data, args.class_info, args.project_dir, args.batch_size,
                                args.width, args.height, args.reset_mean_and_std, transformer)


    model = create_model(args.height, args.width, len(data_manager.class_list), args.network, args.transfer, args.train_all)

    if args.weights:
        model.load_weights(args.weights, by_name=True, skip_mismatch=True)
    

    # if args['multi_label']:
    #     loss = BinaryCrossentropy(focal_loss=args['focal_loss'], alpha=args['alpha'], gamma=args['gamma'])
    #     accuracy = keras.metrics.BinaryAccuracy(threshold=0)
    # else:
    #     loss = CategoricalCrossentropy(focal_loss=args['focal_loss'], alpha=args['alpha'], gamma=args['gamma'])
    #     accuracy = keras.metrics.CategoricalAccuracy()

    checkpoint = keras.callbacks.ModelCheckpoint(os.path.join(args['log_dir'], args['network'] + '-' + 'ep{epoch:03d}-loss{loss:.3f}-val_loss{val_loss:.3f}.h5'),  
        monitor='val_loss', save_weights_only=True, save_best_only=False, period=1)
    reduce_lr = keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1)
    loss_history = LossHistory(args['log_dir'])

    optimizer = NewOptimizer(args['learning_rate_base'])
    model.compile(optimizer=optimizer, 
                    loss=loss,
                    metrics=[accuracy])

    model.fit(
            train_data_sequence, 
            validation_data=val_data_sequence,
            epochs=args['epochs'],
            shuffle = True,
            class_weight = train_data_sequence.get_class_weight(),
            callbacks=[checkpoint, reduce_lr, loss_history],
            max_queue_size = 10,
            workers = 2,
            use_multiprocessing = True
            )
            
    optimizer.apply_ema_weights() 
    model.save_weights(os.path.join(args['log_dir'], 'last.h5'))





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='训练命令行工具')
    parser.add_argument('--train_data', default=r'D:\Project\PYTHON\classification\data\valid.txt')
    parser.add_argument('--valid_data', default=r'D:\Project\PYTHON\classification\data\valid.txt')
    parser.add_argument('--class_info', default=r'D:\Project\PYTHON\classification\data\class.txt')
    parser.add_argument('--project_dir', default=r'D:\Project\PYTHON\classification\log')

    parser.add_argument('--network', default=r'mobilenetv2')
    parser.add_argument('--weights', default=r'D:\Project\PYTHON\classification\pretrain_model\D:\Project\PYTHON\classification\pretrain_model\resnet50v2_weights_tf_dim_ordering_tf_kernels_notop.h5')
    parser.add_argument('--reset_mean_and_std', default=False)
    parser.add_argument('--transfer', default=False)
    parser.add_argument('--train_all', default=False)
    parser.add_argument('--epochs', default=100)
    parser.add_argument('--height', default=224)
    parser.add_argument('--width', default=224)
    parser.add_argument('--lr', default=10e-4)
    parser.add_argument('--batch_size', default=4)

    parser.add_argument('--scale', nargs=2, default=None)
    parser.add_argument('--translate_percent_x', nargs=2, type=float, default=[-0.05, 0.05])
    parser.add_argument('--translate_percent_y', nargs=2, type=float, default=[-0.01, 0.01])
    parser.add_argument('--rotate', nargs=2, type=int, default=[-10, 10])
    parser.add_argument('--shear', default=None)
    parser.add_argument('--flip_lr', type=float, default=0.5)
    parser.add_argument('--flip_ud', type=float, default=0.5)
    parser.add_argument('--crop', default=None)
    parser.add_argument('--multiply', nargs=2, default=[0.8, 1.2])
    parser.add_argument('--gaussian_noise', nargs=2, default=[0, 2.55])
    parser.add_argument('--gaussian_blur', nargs=2, default=[0, 1.0])
    parser.add_argument('--linear_contrast', default=None)

    args = parser.parse_args()

    train(args)
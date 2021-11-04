import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import backend as K
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy.signal
import numpy as np
import cv2
import yaml
import math
import shutil
from imgaug import augmenters as iaa
from tqdm import trange

# 内置参数
root_path = os.path.dirname(__file__)
resnet50_weight_path = os.path.join(root_path, r'pretrain_model/resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5')
mobilenetv2_weight_path = os.path.join(root_path, r'pretrain_model/mobilenet_v2_weights_tf_dim_ordering_tf_kernels_1.0_224_no_top.h5')


def is_image(image_name):
    return image_name.endswith('.png') or image_name.endswith('.jpeg') or image_name.endswith('.bmp') or image_name.endswith('.jpg') or image_name.endswith('.tiff')



class DataSequence(keras.utils.Sequence):
    def __init__(self, data_path, classes, batch_size, resize_size, mean=0, std=255., transformer=None, save_dir=None):
        self.data_path = data_path
        self.classes = classes
        self.batch_size = batch_size
        self.resize_size = resize_size
        self.mean = mean
        self.std = std

        self.transformer = transformer
        self.save_dir = save_dir
        if self.save_dir:
            shutil.rmtree(self.save_dir)
            os.mkdir(self.save_dir)

        self.dataset = []
        self.class_num_list = len(classes) * [0]
        self.init()

    def __len__(self):
        return math.ceil(len(self.dataset) / self.batch_size)

    def __getitem__(self, idx):
        batch_data = self.dataset[idx*self.batch_size : (idx+1)*self.batch_size]
        batch_image = []
        batch_label = []
        for image_path, label in batch_data:
            image = cv2.imdecode(np.fromfile(image_path,np.uint8),flags=-1)
            if self.transformer:
                image = self.transformer(image)
            image = cv2.resize(image, self.resize_size, interpolation=cv2.INTER_LINEAR)
            hot_label = np.zeros(len(self.classes), dtype=np.float32)
            hot_label[label] = 1.

            if self.save_dir:
                class_save_dir = os.path.join(self.save_dir, self.classes[label])
                if not os.path.exists(class_save_dir):
                    os.mkdir(class_save_dir)
                save_name = os.path.splitext(os.path.split(image_path)[1])[0] + '.jpg'
                cv2.imencode('.jpg',image)[1].tofile(os.path.join(class_save_dir, save_name))

            batch_image.append(image)
            batch_label.append(hot_label)

        batch_image = np.array(batch_image, dtype=np.float32)
        batch_image = (batch_image - self.mean) / self.std

        return np.array(batch_image, np.float32), np.array(batch_label, np.float32)

    def init(self):        
        self.dataset = []
        for line in open(self.data_path, encoding='utf8'):
            image_path, class_name = line.strip().split('\t')
            index = self.classes.index(class_name)
            self.class_num_list[index] += 1
            self.dataset.append((image_path, index))
        np.random.shuffle(self.dataset)

    def get_class_weight(self):
        n_samples = sum(self.class_num_list)
        n_classes = len(self.class_num_list)
        return {index : n_samples/(item*n_classes) for index, item in enumerate(self.class_num_list)}


def init_env():
    args = yaml.load(open(os.path.join(root_path,'config.yaml'), encoding='utf8'))

    os.environ['CUDA_VISIBLE_DEVICES'] = args['gpu']

    args['log_dir'] = os.path.join(root_path, args['log_dir'])
    args['train_augdata_dir'] = os.path.join(root_path, args['train_augdata_dir']) if args['train_augdata_dir'] else None
    args['val_augdata_dir'] = os.path.join(root_path, args['val_augdata_dir']) if args['val_augdata_dir'] else None
    args['test_result_dir'] = os.path.join(root_path, args['test_result_dir'])

    print(args['classes'])
    args['num_class'] = len(args['classes'])

    if args['reset']:
        args['mean'], args['std'] = mean_and_std(args['train_data_path'], args['img_height'], args['img_width'])

    args['mean'] = np.array(args['mean'])
    args['std'] = np.array(args['std'])

    args['alpha'] = np.array(args['alpha'])
    args['gamma'] = np.array(args['gamma'])

    gpus = tf.config.experimental.list_physical_devices('GPU')
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)

    return args


class BinaryCrossentropy(tf.keras.losses.Loss):
    def __init__(self, focal_loss=False, alpha=0.5, gamma=2.0, name='binary_crossentropy'):
        super(BinaryCrossentropy, self).__init__(name=name)
        self.focal_loss = focal_loss
        self.alpha = alpha
        self.gamma = gamma

    def call(self, y_true, y_pred):
        loss = tf.nn.sigmoid_cross_entropy_with_logits(labels=y_true, logits=y_pred)

        if self.focal_loss:
            focal_mask = (self.alpha * y_true + (1 - self.alpha) * (1 - y_true)) * tf.pow(tf.abs(y_true - tf.sigmoid(y_pred)), self.gamma)
            loss = loss * focal_mask

        return tf.reduce_sum(loss, axis=-1)


class CategoricalCrossentropy(tf.keras.losses.Loss):
    def __init__(self, focal_loss=False, alpha=0.5, gamma=2.0, name='categorical_crossentropy'):
        super(CategoricalCrossentropy, self).__init__(name=name)
        self.focal_loss = focal_loss
        self.alpha = alpha
        self.gamma = gamma

    def call(self, y_true, y_pred):
        if self.focal_loss:
            loss = -tf.math.log(tf.nn.softmax(y_pred)) * y_true
            focal_mask = self.alpha * tf.pow(1 - tf.nn.softmax(y_pred), self.gamma)
            loss = loss * focal_mask
            loss = tf.reduce_sum(loss, axis=-1)
        else:
            loss = tf.nn.softmax_cross_entropy_with_logits(labels=y_true, logits=y_pred)

        return loss




class LossHistory(keras.callbacks.Callback):
    def __init__(self, log_dir):
        import datetime
        curr_time = datetime.datetime.now()
        time_str = datetime.datetime.strftime(curr_time,'%Y_%m_%d_%H_%M_%S')
        self.log_dir    = log_dir
        self.time_str   = time_str
        self.save_path  = os.path.join(self.log_dir, "loss_" + str(self.time_str))  
        self.losses     = []
        self.val_loss   = []
        
        os.makedirs(self.save_path)

    def on_epoch_end(self, epoch, logs={}):
        self.losses.append(logs.get('loss'))
        self.val_loss.append(logs.get('val_loss'))
        with open(os.path.join(self.save_path, "epoch_loss_" + str(self.time_str) + ".txt"), 'a') as f:
            f.write('epoch : ' + str(epoch + 1) + '\n')
            f.write('loss : ' + str(logs.get('loss')) + '\n')
            f.write('acc : ' + str(logs.get('binary_accuracy')) + '\n')
            f.write('lr : ' + str(logs.get('lr')) + '\n')
            f.write('*' * 20 + '\n')
        with open(os.path.join(self.save_path, "epoch_val_loss_" + str(self.time_str) + ".txt"), 'a') as f:
            f.write('epoch : ' + str(epoch + 1) + '\n')
            f.write('val_loss : ' + str(logs.get('val_loss')) + '\n')
            f.write('val_acc : ' + str(logs.get('val_binary_accuracy')) + '\n')
            f.write('lr : ' + str(logs.get('lr')) + '\n')
            f.write('*' * 20 + '\n')
        self.loss_plot()

    def loss_plot(self):
        iters = range(len(self.losses))

        plt.figure()
        plt.plot(iters, self.losses, 'red', linewidth = 2, label='train loss')
        plt.plot(iters, self.val_loss, 'coral', linewidth = 2, label='val loss')
        try:
            if len(self.losses) < 25:
                num = 5
            else:
                num = 15
            
            plt.plot(iters, scipy.signal.savgol_filter(self.losses, num, 3), 'green', linestyle = '--', linewidth = 2, label='smooth train loss')
            plt.plot(iters, scipy.signal.savgol_filter(self.val_loss, num, 3), '#8B4513', linestyle = '--', linewidth = 2, label='smooth val loss')
        except:
            pass

        plt.grid(True)
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('A Loss Curve')
        plt.legend(loc="upper right")

        plt.savefig(os.path.join(self.save_path, "epoch_loss_" + str(self.time_str) + ".png"))

        plt.cla()
        plt.close("all")

Unknown = 'Un'
def finetune(result, classes, threshold=0):
    index = np.argmax(result)
    score = result[index]
    if score > threshold:
        return classes[index]
    else:
        return Unknown

# def finetune(result, classes, threshold=0):
#     index = np.argmax(result)
#     score = result[index]
#     if score > threshold:
#         if classes[index] in ['C1F', 'C2F'] and score < 0.9:
#             return Unknown
#         else:
#             return classes[index]
#     else:
#         return Unknown

def sigmoid(z):
    return 1/(1 + np.exp(-z))

class TestEr:
    def __init__(self, args):
        self.args = args

        if args['mode'] == 'pb':
            graph_def=tf.GraphDef()
            with open(args['test_pb_path'],"rb") as fp:
                graph_def.ParseFromString(fp.read()[3:])
            tf.import_graph_def(graph_def,name='')
            tensor_name_list = [tensor.name for tensor in tf.get_default_graph().as_graph_def().node]
            self.inputs=tf.get_default_graph().get_tensor_by_name("Detection_input:0")
            self.outputs=tf.get_default_graph().get_tensor_by_name("Detection_output:0")
            config = tf.ConfigProto()  
            config.gpu_options.allow_growth=True   #不全部占满显存, 按需分配
            self.sess = tf.Session(config=config)
            self.sess.run(self.outputs,feed_dict={self.inputs : np.zeros((1,args['img_height'], args['img_width'], 3), dtype=np.uint8)})

        elif args['mode'] == 'weights':
            self.model = create_model(args)
            self.model.load_weights(args['test_weights_path'])
            self.model.predict(np.zeros((1, args['img_height'], args['img_width'], 3)))

    def infer(self, image):
        if self.args['mode'] == 'pb':
            result=self.sess.run(self.outputs,feed_dict={self.inputs : image[np.newaxis,:,:,:]})
            result = result[0,:,1]
        elif self.args['mode'] == 'weights':
            images = []
            image = cv2.resize(image, (self.args['img_width'], self.args['img_height']), interpolation=cv2.INTER_LINEAR)
            images.append(image)
            images = np.array(images, dtype=np.float32)
            images = (images - self.args['mean']) / self.args['std']
            result = self.model.predict(images)
            result = sigmoid(result)[0]
        return result


class NewOptimizer(keras.optimizers.Adam):
    def __init__(self, *args, **kwargs):
        super(NewOptimizer, self).__init__(*args, **kwargs)
        self.ema_momentum = 0.999

    def get_updates(self, loss, params):
        # 调用父类 get_updates 就更新了权重 m v
        updates = super(NewOptimizer, self).get_updates(loss, params)
        self.model_weights = params  # 用于更新和reset
        self.ema_weights = [K.zeros(K.shape(w)) for w in params]  # ema 初始化
        self.old_weights = K.batch_get_value(params)
        # 滑动平均不是这样的，是否权重初始化后后续只能K.update
        K.batch_set_value(zip(self.ema_weights, self.old_weights))

        ema_updates, ema_momentum = [], self.ema_momentum
        # 控制依赖，后续执行需要在updates执行后，执行后params就做了更新
        with tf.control_dependencies(updates):
            for w1, w2 in zip(self.ema_weights, params):
                new_w = ema_momentum * w1 + (1 - ema_momentum) * w2
                ema_updates.append(K.update(w1, new_w))

        return ema_updates

    def get_config(self):
        config = {'ema_momentum': self.ema_momentum,
                    }
        base_config = super(NewOptimizer, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))

    def apply_ema_weights(self):
        """备份原模型权重，然后将平均权重应用到模型上去。
        """
        self.old_weights = K.batch_get_value(self.model_weights)
        ema_weights = K.batch_get_value(self.ema_weights)
        K.batch_set_value(zip(self.model_weights, ema_weights))

    def reset_old_weights(self):
        """恢复模型到旧权重。
        """
        K.batch_set_value(zip(self.model_weights, self.old_weights))


def mean_and_std(data_path, img_height, img_width):
    dataset = open(data_path, encoding='utf8').readlines()
    image_num = len(dataset)
    pix_num = image_num * img_width * img_height

    B_channel = 0
    G_channel = 0
    R_channel = 0

    print('computing mean...')
    for index in trange(image_num):
        line = dataset[index]
        image_path, _ = line.strip().split('\t')
        image = cv2.imdecode(np.fromfile(image_path,np.uint8),flags=-1)
        image = cv2.resize(image, (img_width, img_height), interpolation=cv2.INTER_LINEAR)

        B_channel = B_channel + np.sum(image[:, :, 0])
        G_channel = G_channel + np.sum(image[:, :, 1])
        R_channel = R_channel + np.sum(image[:, :, 2])

    B_mean = B_channel / pix_num
    G_mean = G_channel / pix_num
    R_mean = R_channel / pix_num
    print('mean: ','[{:.3f}, {:.3f}, {:.3f}]'.format(B_mean, G_mean, R_mean))

    B_channel = 0
    G_channel = 0
    R_channel = 0

    print('computing std...')
    for index in trange(image_num):
        line = dataset[index]
        image_path, _ = line.strip().split('\t')
        image = cv2.imdecode(np.fromfile(image_path,np.uint8),flags=-1)
        image = cv2.resize(image, (img_width, img_height), interpolation=cv2.INTER_LINEAR)

        B_channel = B_channel + np.sum((image[:, :, 0] - B_mean) ** 2)
        G_channel = G_channel + np.sum((image[:, :, 1] - G_mean) ** 2)
        R_channel = R_channel + np.sum((image[:, :, 2] - R_mean) ** 2)

    B_var = np.sqrt(B_channel / pix_num)
    G_var = np.sqrt(G_channel / pix_num)
    R_var = np.sqrt(R_channel / pix_num)

    print('std: ','[{:.3f}, {:.3f}, {:.3f}]'.format(B_var, G_var, R_var))
    return eval('[{:.3f}, {:.3f}, {:.3f}]'.format(B_mean, G_mean, R_mean)), eval('[{:.3f}, {:.3f}, {:.3f}]'.format(B_var, G_var, R_var))


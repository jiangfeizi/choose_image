from tensorflow import keras
from tensorflow.keras import backend as K
import tensorflow as tf


class NewOptimizer(keras.optimizers.Adam):
    def __init__(self, ema_momentum=0.999, *args, **kwargs):
        super(NewOptimizer, self).__init__(*args, **kwargs)
        self.ema_momentum = ema_momentum

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


def create_model(img_height, img_width, num_class, network, loss, lr, transfer, train_all):
    if network == r'resnet50':
        base_model = keras.applications.ResNet50(weights=None, include_top=False, pooling='avg')
    elif network == r'mobilenetv2':
        base_model = keras.applications.MobileNetV2(weights=None, include_top=False, pooling='avg')
    else:
        raise NotImplementedError('Not support the network!')

    inputs = keras.layers.Input(shape=(img_height, img_width, 3))

    if transfer:
        x = base_model(inputs, training=False)
    else:
        x = base_model(inputs)

    if loss == 'binary_crossentropy':
        fc = keras.layers.Dense(num_class, activation='sigmoid')
        x = fc(x)
        loss = keras.losses.BinaryCrossentropy()
        accuracy = keras.metrics.BinaryAccuracy()
    elif loss == 'categorical_crossentropy':
        fc = keras.layers.Dense(num_class, activation='softmax')
        x = fc(x)
        loss = keras.losses.CategoricalCrossentropy()
        accuracy = keras.metrics.CategoricalAccuracy()
    model = keras.models.Model(inputs, x)
    model.summary()

    model.base_model = base_model
    model.fc = fc

    if train_all:
        base_model.trainable = True
    else:
        base_model.trainable = False

    optimizer = keras.optimizers.Adam(lr)

    model.compile(optimizer=optimizer, 
                    loss=loss,
                    metrics=[accuracy])

    return model



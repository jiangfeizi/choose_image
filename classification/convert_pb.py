from six import with_metaclass
import tensorflow as tf
from tensorflow import keras
from common import create_model, init_env
from tensorflow.python.framework import graph_util
from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2


def func(inputs):
    x = tf.identity(inputs, name='Detection_input')
    x = tf.image.resize(x, [args['img_height'], args['img_width']])
    x = (x - args['mean']) / args['std']
    x = model(x)
    x = tf.sigmoid(x)
    labels = tf.expand_dims(tf.range(1,args['num_class']+1), axis=0)
    labels = tf.expand_dims(labels, axis=2)
    labels = tf.cast(labels, tf.float32)
    scores = tf.expand_dims(x, axis=2)
    constant = tf.zeros([1, args['num_class'], 4], tf.float32)
    x = tf.concat([labels, scores, constant], axis=2)
    x = tf.identity(x, name='Detection_output')
    return x

args = init_env()

# keras.backend.set_learning_phase(0)

model = create_model(args['img_height'], args['img_width'], args['channels'], args['num_class'], args['network'])
model.load_weights(args['convert_weights_path'])

tf_model_graph = tf.function(lambda x: func(x))

# get concrete function
tf_model_graph = tf_model_graph.get_concrete_function(
    tf.TensorSpec(model.inputs[0].shape, model.inputs[0].dtype))

# obtain frozen concrete function
frozen_tf_func = convert_variables_to_constants_v2(tf_model_graph)
# get frozen graph
graph_def = frozen_tf_func.graph.as_graph_def()

layers = [op.name for op in frozen_tf_func.graph.get_operations()]

with open('test.pb', 'wb') as fp:
    fp.write(b'sci')
    fp.write(graph_def.SerializeToString())



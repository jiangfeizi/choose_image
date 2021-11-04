import os

import cv2
import numpy as np
import tensorflow as tf


def get_tf_model_proto(tf_model):
    # define the directory for .pb model
    pb_model_path = "models"

    # define the name of .pb model
    pb_model_name = "mobilenet.pb"

    # create directory for further converted model
    os.makedirs(pb_model_path, exist_ok=True)

    # get model TF graph
    tf_model_graph = tf.function(lambda x: tf_model(x))

    # get concrete function
    tf_model_graph = tf_model_graph.get_concrete_function(
        tf.TensorSpec(tf_model.inputs[0].shape, tf_model.inputs[0].dtype))

    # obtain frozen concrete function
    frozen_tf_func = convert_variables_to_constants_v2(tf_model_graph)
    # get frozen graph
    frozen_tf_func.graph.as_graph_def()

    # save full tf model
    tf.io.write_graph(graph_or_graph_def=frozen_tf_func.graph,
                      logdir=pb_model_path,
                      name=pb_model_name,
                      as_text=False)

    return os.path.join(pb_model_path, pb_model_name)


def get_preprocessed_img(img_path):
    # read the image
    input_img = cv2.imread(img_path, cv2.IMREAD_COLOR)
    input_img = input_img.astype(np.float32)

    # define preprocess parameters
    mean = np.array([1.0, 1.0, 1.0]) * 127.5
    scale = 1 / 127.5

    # prepare input blob to fit the model input:
    # 1. subtract mean
    # 2. scale to set pixel values from 0 to 1
    input_blob = cv2.dnn.blobFromImage(
        image=input_img,
        scalefactor=scale,
        size=(1152, 384),  # img target size
        mean=mean,
        swapRB=True,  # BGR -> RGB
        crop=True  # center crop
    )
    print("Input blob shape: {}\n".format(input_blob.shape))

    return input_blob


def get_imagenet_labels(labels_path):
    with open(labels_path) as f:
        imagenet_labels = [line.strip() for line in f.readlines()]
    return imagenet_labels


def get_opencv_dnn_prediction(opencv_net, preproc_img):
    # set OpenCV DNN input
    opencv_net.setInput(preproc_img)
    import time
    # OpenCV DNN inference
    out = opencv_net.forward()

    start = time.time()
    for _ in range(10):
        out = opencv_net.forward()
    end = time.time()
    print(end-start)
    print("OpenCV DNN prediction: \n")
    print("* shape: ", out.shape)

    # get the predicted class ID
    imagenet_class_id = np.argmax(out)

    # get confidence
    confidence = out[0][imagenet_class_id]


def main():
    full_pb_path = r'test\test.pb'

    # get TF frozen graph path
    # pb_data = open('0927-tobacco.scidl','rb').read()[3:]
    # open(full_pb_path,'wb').write(pb_data)

    # read frozen graph with OpenCV API
    opencv_net = cv2.dnn.readNetFromTensorflow(full_pb_path)
    print("OpenCV model was successfully read. Model layers: \n", opencv_net.getLayerNames())

    # get preprocessed image
    input_img = get_preprocessed_img(r"C:\Users\jiangwei\Desktop\18_12_25-2021_8_26.bmp")

    # obtain OpenCV DNN predictions
    get_opencv_dnn_prediction(opencv_net, input_img)



if __name__ == "__main__":
    main()

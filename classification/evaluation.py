import pickle
import tensorflow as tf
import argparse
import cv2
import numpy as np
from socket import *

def load_class_list(class_info):
    lines = open(class_info, encoding='utf8').readlines()
    return [line.strip() for line in lines]

def evaluation(args):
    class_list = load_class_list(args.class_info)
    saved_model = tf.keras.models.load_model(args.model_path)
    saved_model(np.zeros((8, 224, 224, 3), np.float32))

    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(('', args.port))
    sock.listen(5)
    conn, addr = sock.accept() 
    
    while True:
        bytes = conn.recv(4096)
        obj = pickle.loads(bytes)
        images = []
        for path in obj:
            image = cv2.imdecode(np.fromfile(path,np.uint8),flags=cv2.IMREAD_COLOR)
            image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_LINEAR)
            images.append(image)
        images = np.array(images, np.float32)
        result = saved_model(images).numpy()
        indexes = np.argmax(result, axis=-1).tolist()
        scores = np.max(result, axis=-1).tolist()
        classes = [class_list[i] for i in indexes]
        obj = list(zip(classes, scores))
        conn.send(pickle.dumps(obj))



if __name__=='__main__':
    parser = argparse.ArgumentParser(description='model serving')
    parser.add_argument('--model_path', default=r'C:\Users\jiangwei\Desktop\新建文件夹\checkpoint\resnet50-ep006-loss0.014-val_loss0.344.ckpt')
    parser.add_argument('--class_info', default=r'C:\Users\jiangwei\Desktop\新建文件夹\class.txt')
    parser.add_argument('--port', type=int, default=50008)
    args = parser.parse_args()

    evaluation(args)
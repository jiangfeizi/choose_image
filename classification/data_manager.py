import cv2
import numpy as np
from tensorflow import keras
import math


class DataSequence(keras.utils.Sequence):
    def __init__(self, dataset, class_num, batch_size, resize_size, transformer=None):
        self.dataset = dataset
        self.class_num = class_num
        self.batch_size = batch_size
        self.resize_size = resize_size

        self.transformer = transformer

    def __len__(self):
        return math.ceil(len(self.dataset) / self.batch_size)

    def __getitem__(self, idx):
        batch_data = self.dataset[idx*self.batch_size : (idx+1)*self.batch_size]
        batch_image = []
        batch_label = []
        for image_path, label in batch_data:
            image = cv2.imdecode(np.fromfile(image_path,np.uint8),flags=cv2.IMREAD_COLOR)
            if self.transformer:
                image = self.transformer(image)
            image = cv2.resize(image, self.resize_size, interpolation=cv2.INTER_LINEAR)
            hot_label = np.zeros(self.class_num, dtype=np.float32)
            hot_label[label] = 1.

            batch_image.append(image)
            batch_label.append(hot_label)

        return np.array(batch_image, np.float32), np.array(batch_label, np.float32)


class DataManager:
    def __init__(self, train_data, valid_data, class_info, project_dir, batch_size, 
                image_width, image_height, transformer):
        self.train_data = train_data
        self.valid_data = valid_data
        self.class_info = class_info
        self.project_dir = project_dir
        self.batch_size = batch_size
        self.image_width = image_width
        self.image_height = image_height
        self.transformer = transformer

        self.class_list = self.load_class_list()
        self.class_num = len(self.class_list)
        self.train_dataset, self.train_num_list = self.load_dataset(self.train_data, True)
        self.valid_dataset, _ = self.load_dataset(self.valid_data)

    def load_dataset(self, data, shuffle=False):
        dataset = []
        num_list = len(self.class_list) * [0]

        for line in open(data, encoding='utf8'):
            image_path, class_name = line.strip().split('\t')
            index = self.class_list.index(class_name)
            dataset.append((image_path, index))
            num_list[index] += 1

        if shuffle:
            np.random.shuffle(dataset)

        return dataset, num_list

    def class_weight(self):
        n_samples = sum(self.train_num_list)
        n_classes = len(self.train_num_list)
        return {index : n_samples/((item*n_classes)+np.finfo(np.float64).eps) for index, item in enumerate(self.train_num_list)}

    def train_sequence(self):
        return DataSequence(self.train_dataset, len(self.class_list), self.batch_size, (self.image_width, self.image_height), self.transformer)

    def valid_sequence(self):
        return DataSequence(self.valid_dataset, len(self.class_list), self.batch_size, (self.image_width, self.image_height))

    def load_class_list(self):
        lines = open(self.class_info, encoding='utf8').readlines()
        return [line.strip() for line in lines]
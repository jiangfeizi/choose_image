from socket import *
import sys
import yaml


def is_image(image_name):
    return image_name.endswith('.png') or image_name.endswith('.jpeg') or image_name.endswith('.bmp') or image_name.endswith('.jpg') or image_name.endswith('.tiff')


def redirect_out(port, host):
    loss_sock = socket(AF_INET, SOCK_STREAM)
    loss_sock.connect((host, port))
    loss_sock.setblocking(False)

    log_sock = socket(AF_INET, SOCK_STREAM)
    log_sock.connect((host, port))
    file = log_sock.makefile('w')
    sys.stdout = file
    return log_sock, loss_sock

class Config:
    def __init__(self, file):
        self._file = file
        self._config = yaml.load(open(self._file, encoding='utf8'))
        for key, value in self._config.items():
            exec('self.{} = value'.format(key))




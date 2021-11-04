import os
import sys
from socket import *


def is_image(image_name):
    return image_name.endswith('.png') or image_name.endswith('.jpg') or image_name.endswith('.bmp') or image_name.endswith('.jpeg') or image_name.endswith('.tiff')

def resource_path(relative_path):
    if getattr(sys, 'frozen', False): 
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def initListenerSocket(port):
    """
    initialize connected socket for callers that listen in server mode
    """
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(('', port))                     # listen on this port number
    sock.listen(5)                            # set pending queue length
    sock.setblocking(False) 
    return sock                               # return connected socket


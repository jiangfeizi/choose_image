import yaml
import os
from tkinter import *

root = os.path.dirname(__file__)


class Setting:
    def __init__(self, file):
        self._file = file
        self._setting = yaml.load(open(os.path.join(root, self._file), encoding='utf8'))
        for key, value in self._setting.items():
            exec('self.{} = value'.format(key))
        self.language = Language(self.language)

    def save_setting(self):
        with open(os.path.join(root, self._file), encoding='utf8', mode='w') as fp:
            setting = yaml.dump(self._setting)
            fp.write(setting)


class Language:
    def __init__(self, file):
        self._file = file
        self._language = yaml.load(open(os.path.join(root, 'language', self._file), encoding='utf8'))

        for key, value in self._language.items():
            exec('self.{} = value'.format(key))



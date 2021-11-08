# from threading import Thread
# import queue
# import logging


# def track_error(func):
#     global gui
#     def func_track_error(*args, **kwargs):
#         try:
#             func(*args, **kwargs)
#         except:
#             gui.label_statusbar.config(text='{}:{}'.format(gui.setting.language.gui_error, func.__name__))
#             raise
#     return func_track_error


import tkinter as tk
import tkinter.ttk as ttk
import yaml

from utils import resource_path
from setting import Setting
from label_frame import LabelFrame
from train_frame import TrainFrame
from eval_frame import EvalFrame

class Gui(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        self.setting_path = resource_path('setting\gui_setting.yaml')
        self.setting = yaml.load(open(self.setting_path, encoding='utf8'))
        
        self.notebook = self.make_notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.title(self.setting['title'])
        self.iconbitmap(resource_path(self.setting['icon']))
        self.geometry('{}'.format(self.setting['geometry']))

        self.protocol('WM_DELETE_WINDOW', self.exit)

    def make_notebook(self, master):
        self.notebook = ttk.Notebook(master)
        
        self.label_frame = LabelFrame(self.notebook, self.setting['language'])
        # self.train_frame = TrainFrame(self.notebook)
        # self.eval_frame = EvalFrame(self.notebook)

        self.label_frame.pack(fill=tk.BOTH, expand=True)
        # self.train_frame.pack(fill=tk.BOTH, expand=True)
        # self.eval_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook.add(self.label_frame, text=self.setting[self.setting['language']]['notebook_label'])
        # self.notebook.add(self.train_frame, text=self.setting[self.setting['language']]['notebook_train'])
        # self.notebook.add(self.eval_frame, text=self.setting[self.setting['language']]['notebook_eval'])

        return self.notebook       

    def save_setting(self):
        geometry = self.geometry()
        self.setting.update({'geometry': geometry})
        yaml.dump(self.setting, open(resource_path('setting\gui_setting.yaml'), 'w', encoding='utf8'))

    def exit(self):
        self.save_setting()
        self.label_frame.save_setting()

        self.quit()


if __name__=='__main__':
    gui = Gui()
    gui.mainloop()

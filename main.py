from setting import Setting
from label_frame import LabelFrame
from train_frame import TrainFrame

import tkinter as tk
import tkinter.ttk as ttk
from utils import resource_path

from threading import Thread
import queue


def track_error(func):
    global gui
    def func_track_error(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            gui.label_statusbar.config(text='{}:{}'.format(gui.setting.language.gui_error, func.__name__))
            raise
    return func_track_error


class Gui(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.setting = Setting(resource_path('setting.yaml'))
        self.thread_queue = queue.Queue(maxsize=0)

        self.check_event()

        # 内置参数

        self.notebook = self.make_notebook(self)
 
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.title(self.setting.gui_title)
        self.iconbitmap(resource_path(self.setting.gui_icon))
        self.geometry('{}'.format(self.setting.geometry))

        self.protocol('WM_DELETE_WINDOW', self.save_setting)

    def make_notebook(self, master):
        self.notebook = ttk.Notebook(master)
        
        self.label_frame = LabelFrame(self.notebook, self.setting, self.thread_queue)
        self.train_frame = TrainFrame(self.notebook, self.setting, self.thread_queue)
        self.eval_frame = ttk.Frame(self.notebook)

        self.label_frame.pack(fill=tk.BOTH, expand=True)
        self.train_frame.pack(fill=tk.BOTH, expand=True)
        self.eval_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook.add(self.label_frame, text=self.setting.language.notebook_label)
        self.notebook.add(self.train_frame, text=self.setting.language.notebook_train)
        self.notebook.add(self.eval_frame, text=self.setting.language.notebook_eval)

        return self.notebook

    def check_event(self):
        for i in range(100):                                # pass to set speed
            try:                                                
                callback, args = self.thread_queue.get(block=False)  # run <= N callbacks
            except queue.Empty:
                break                                            # anything ready?
            else:
                callback(*args)                                  # run callback here

        self.after(100, self.check_event)                               


    def save_setting(self):
        geometry = self.geometry()
        self.setting._setting.update({'geometry': geometry})
        self.setting.save_setting()
        self.quit()
        


if __name__=='__main__':
    gui = Gui()
    gui.mainloop()

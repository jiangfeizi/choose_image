# from utils import *
from PIL import ImageTk, Image
from config import Setting
from label_frame import LabelFrame

import tkinter as tk
import tkinter.ttk as ttk


class Gui(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry('1200x800')
        
        self.setting = Setting('config.yaml')

        self.notebook = ttk.Notebook(self)

        self.label_frame = LabelFrame(self.notebook, self.setting)
        self.train_frame = LabelFrame(self.notebook, self.setting)
        self.evalution_fram = LabelFrame(self.notebook, self.setting)

        self.notebook.add(self.label_frame, text=self.setting.language.notebook_label)
        self.notebook.add(self.train_frame, text=self.setting.language.notebook_train)
        self.notebook.add(self.evalution_fram, text=self.setting.language.notebook_evaluation)
 
        self.notebook.pack(fill=tk.BOTH, expand=True)





one = Gui()

one.mainloop()

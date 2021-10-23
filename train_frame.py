from tkinter import *
from utils import *
from tkinter.filedialog import askdirectory, askopenfilename
from PIL import Image, ImageTk
import numpy as np
import os
import shutil
from tkinter.messagebox import *
import pickle

import tkinter as tk
import tkinter.ttk as ttk


class BasicSetting(Frame):
    def __init__(self, master, textvariable):
        Frame.__init__(self, master)
        self.label = Label(self, textvariable=textvariable)
        self.entry = Entry(self,)
        




class HyperParameters(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)


tk = Tk()
a = IntVar()
one = LabelAndSpinbox(tk, 'aa', 2, 5, a)
one.pack()
tk.mainloop()
print(a.get())
print(type(a.get()))



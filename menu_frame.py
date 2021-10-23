




import os
import tkinter
from tkinter.ttk import *
import sys
from tkinter import *

from tkinter import ttk

ttk.LabeledScale

class MenuFrame(Frame):
    def __init__(self, master, setting):
        Frame.__init__(self, master)

        self.setting = setting

        self.label_button = Button(self, textvariable=self.setting.language.menu_label)
        self.train_button = Button(self, textvariable=self.setting.language.menu_train)
        self.evaluation_button = Button(self, textvariable=self.setting.language.menu_evaluation)

        self.label_button.pack(side=LEFT)
        self.train_button.pack(side=LEFT)
        self.evaluation_button.pack(side=LEFT)

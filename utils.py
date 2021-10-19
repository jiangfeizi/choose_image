from tkinter import *
import sys
import os

class LabelAndEntry(Frame):
    def __init__(self, master, label, textvariable):
        Frame.__init__(self, master)
        self.label = Label(self, text=label)
        self.entry = Entry(self, textvariable=textvariable)

        self.label.pack(side=LEFT)
        self.entry.pack(side=RIGHT)

class LabelAndEntryAndButton(Frame):
    def __init__(self, master, label, textvariable, button):
        Frame.__init__(self, master)
        self.label_and_entry = LabelAndEntry(self, label, textvariable)
        self.button = Button(self, text=button)

        self.label_and_entry.pack(side=LEFT)
        self.button.pack(side=RIGHT)

def is_image(image_name):
    return image_name.endswith('.png') or image_name.endswith('.jpg') or image_name.endswith('.bmp') or image_name.endswith('.jpeg') or image_name.endswith('.tiff')

def resource_path(relative_path):
    if getattr(sys, 'frozen', False): 
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
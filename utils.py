
from tkinter import *
import os
from tkinter import ttk
import sys





def is_image(image_name):
    return image_name.endswith('.png') or image_name.endswith('.jpg') or image_name.endswith('.bmp') or image_name.endswith('.jpeg') or image_name.endswith('.tiff')

def resource_path(relative_path):
    if getattr(sys, 'frozen', False): 
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# class LabelAndEntry(Frame):
#     def __init__(self, master, label_var, entry_var):
#         Frame.__init__(self, master)
#         self.label = Label(self, textvariable=label_var)
#         self.entry = Entry(self, textvariable=entry_var)

#         self.label.pack(side=LEFT)
#         self.entry.pack(side=RIGHT)


# class LabelAndEntryAndButton(Frame):
#     def __init__(self, master, label_var, entry_var, button_var):
#         Frame.__init__(self, master)
#         self.label_and_entry = LabelAndEntry(self, label_var, entry_var)
#         self.button = Button(self, textvariable=button_var)

#         self.label_and_entry.pack(side=LEFT)
#         self.button.pack(side=RIGHT)


# class LabelAndCombobox(Frame):
#     def __init__(self, master, label_var, default, values, textvariable):
#         Frame.__init__(self, master)
#         self.label = Label(self, text=label_var)
#         self.combobox = ttk.Combobox(self, values=values, textvariable=textvariable)
#         self.combobox.current(values.index(default))

#         self.label.pack(side=LEFT)
#         self.combobox.pack(side=RIGHT)


# class LabelAndSpinbox(Frame):
#     def __init__(self, master, label, min, max, textvariable):
#         Frame.__init__(self, master)
#         self.label = Label(self, text=label)
#         self.spinbox = Spinbox(self, from_=min, to=max, textvariable=textvariable)

#         self.label.pack(side=LEFT)
#         self.spinbox.pack(side=RIGHT)




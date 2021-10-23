
import tkinter as tk
from tkinter.constants import TOP
import tkinter.ttk as ttk
from PIL import ImageTk, Image
import numpy as np
from tkinter.filedialog import askdirectory
import os
from tkinter.simpledialog import askstring

from utils import is_image



class ButtonSet(ttk.Frame):
    def __init__(self, master, setting):
        ttk.Frame.__init__(self, master)

        self.setting = setting

        self.buttons = []
        self.ret_button = ttk.Button(self, text=self.vertical_str(self.setting.language.label_ret_button))
        self.ret_button.config(width=2)
        self.ret_button.pack(side=tk.TOP)

    def vertical_str(self, str):
        return '\n'.join(list(str))

    def add(self, item):
        button = ttk.Button(self, text=self.vertical_str(item))
        button.config(width=2)
        button.pack(side=tk.TOP)
        self.buttons.append(button)
        return button

    def reset(self):
        for button in self.buttons:
            button.destroy()
        self.buttons = []


class LabelLeftUp(ttk.Frame):
    def __init__(self, master, setting):
        ttk.Frame.__init__(self, master)

        self.setting = setting

        self.input_button = ttk.Button(self, text=self.setting.language.label_input_button_text)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.treeview = ttk.Treeview(self, columns=(1,), show='headings')
        self.treeview.column(1)
        self.button_set = ButtonSet(self, self.setting)

        self.scrollbar.config(command=self.treeview.yview)                    
        self.treeview.config(yscrollcommand=self.scrollbar.set)  
        self.treeview.heading(1, text='文件名')

        self.input_button.pack(side=tk.TOP, anchor=tk.W)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)   
        self.button_set.pack(side=tk.LEFT, fill=tk.Y)          
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


class LabelLeftDownButtonSet(ttk.Frame):
    def __init__(self, master, setting):
        ttk.Frame.__init__(self, master)

        self.setting = setting

        self.output_button = ttk.Button(self, text=self.setting.language.label_output_button_text)
        self.add_button = ttk.Button(self, text=self.setting.language.label_add_button_text)

        self.output_button.pack(side=tk.LEFT)
        self.add_button.pack(side=tk.LEFT)



class ThreeLabel(ttk.Frame):
    def __init__(self, master, first, second, third):
        ttk.Frame.__init__(self, master)

        self.first = ttk.Label(self, text=first, relief=tk.RIDGE, anchor=tk.CENTER)
        self.second = ttk.Label(self, text=second, relief=tk.RIDGE, anchor=tk.CENTER)
        self.third = ttk.Label(self, text=third, relief=tk.RIDGE, anchor=tk.CENTER)

        self.first.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.second.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.third.pack(side=tk.LEFT, fill=tk.X, expand=True)


class ThreeLabelSet(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.three_label_list = []

    def add(self, first_var, second_var, third_var):
        three_label = ThreeLabel(self, first_var, second_var, third_var)
        self.three_label_list.append(three_label)
        return three_label

    def reset(self):
        for three_label in self.three_label_list:
            three_label.destroy()
        self.three_label_list = []


class LabelLeftDownTable(ttk.Frame):
    def __init__(self, master, setting):
        ttk.Frame.__init__(self, master)

        self.setting = setting

        self.header = ThreeLabel(self, self.setting.language.label_table_class, 
                                        self.setting.language.label_table_num, self.setting.language.label_table_key)
        self.class_list = []
        self.num_list = []
        self.key_list = []
        self.tabel = []

        self.header.pack(side=tk.TOP, fill=tk.X)

        for _ in range(9):
            class_var = ''
            num_var = ''
            key_var = ''

            self.class_list.append(class_var)
            self.num_list.append(num_var)
            self.key_list.append(key_var)

            three_label = ThreeLabel(self, class_var, num_var, key_var)
            three_label.pack(side=tk.TOP, fill=tk.X)
            self.tabel.append(three_label)


class LabelLeftDown(ttk.Frame):
    def __init__(self, master, setting):
        ttk.Frame.__init__(self, master)

        self.setting = setting

        self.button_set = LabelLeftDownButtonSet(self, self.setting)
        self.treeview = ttk.Treeview(self, columns=(1, 2, 3), show='headings')
        self.treeview.column(1, width=80, anchor=tk.CENTER)
        self.treeview.column(2, width=80, anchor=tk.CENTER)
        self.treeview.column(3, width=80, anchor=tk.CENTER)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)


        self.scrollbar.config(command=self.treeview.yview)                    
        self.treeview.config(yscrollcommand=self.scrollbar.set)  


        self.button_set.pack(side=tk.TOP, anchor=tk.W)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.treeview.heading(1, text=self.setting.language.label_table_class)
        self.treeview.heading(2, text=self.setting.language.label_table_num)
        self.treeview.heading(3, text=self.setting.language.label_table_key)



class LabelLeft(ttk.Frame):
    def __init__(self, master, setting):
        ttk.Frame.__init__(self, master)

        self.setting = setting

        self.up = LabelLeftUp(self, self.setting)
        self.down = LabelLeftDown(self, self.setting)

        self.down.pack(side=tk.BOTTOM, fill=tk.X)
        self.up.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class LabelCore(ttk.Frame):
    def __init__(self, master, setting):
        ttk.Frame.__init__(self, master)

        self.setting = setting

        self.panedwindow = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.panedwindow.pack(fill=tk.BOTH, expand=tk.YES)

        self.left = LabelLeft(self, self.setting)
        # self.init_image = ImageTk.PhotoImage(Image.fromarray(np.ones((500,500), dtype=np.uint8) * 255))
        self.window = ttk.Label(self)

        self.left.pack(side=tk.LEFT, fill=tk.Y)
        self.window.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH)

        self.panedwindow.add(self.left)
        self.panedwindow.add(self.window)

        

class LabelFrame(ttk.Frame):
    def __init__(self, master, setting):
        ttk.Frame.__init__(self, master)

        self.setting = setting

        self.label_core = LabelCore(self, self.setting)
        self.statusbar = ttk.Label(self)
        self.right_menu = tk.Menu(self, tearoff=tk.OFF)


        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.label_core.pack(side=tk.TOP, expand=True, fill=tk.BOTH)


        self.label_core.left.up.input_button.config(command=self.set_input)
        self.label_core.left.up.treeview.bind('<<TreeviewSelect>>', lambda event : self.select())
        self.label_core.window.bind('<Configure>', lambda event : self.show())

        self.label_core.left.up.button_set.ret_button.config(command=lambda item=self.setting.language.label_ret_button:self.press_button(item))

        self.label_core.left.down.button_set.output_button.config(command=self.set_output)
        self.label_core.left.down.button_set.add_button.config(command=self.add_class)

        self.input_dir = None
        self.output_dir = None
        self.class_list = []

        self.current = None
        self.image = None
        self.resize_image = None


    def add_class(self):
        if self.output_dir:
            if len(self.class_list) < 9:
                item = askstring('{}'.format(self.setting.language.info_output_tip), '{}'.format(self.setting.language.info_output_tip)).strip()
                if item:
                    if not item in self.class_list:
                        self.class_list.append(item)
                        item_path = os.path.join(self.output_dir, item)
                        if not os.path.exists(item_path):
                            os.mkdir(item_path)

                        key = len(self.label_core.left.down.treeview.get_children())+1
                        self.label_core.left.up.treeview.bind('', lambda event : self.select())
                        
                        images = [image for image in os.listdir(item_path) if is_image(image)]
                        self.label_core.left.down.treeview.insert('', tk.END, values = (item, len(images), key))
                        
                        button = self.label_core.left.up.button_set.add(item)
                        button.config(command=lambda item=item:self.press_button(item))
                    else:
                        self.statusbar.config(text='{}'.format(self.setting.language.error_multi_create))
            else:
                self.statusbar.config(text='{}'.format(self.setting.language.error_class_limit))
        else:
            self.statusbar.config(text='{}'.format(self.setting.language.error_no_output_dir))

    def press_button(self, item):
        if item == self.setting.language.label_ret_button:
            self.current = 'input'
            self.switch_dir(self.input_dir)
        else:
            self.current = item
            self.switch_dir(os.path.join(self.output_dir, item))


    def switch_dir(self, dir_path):
        for i in self.label_core.left.up.treeview.get_children():
            self.label_core.left.up.treeview.delete(i)
        items = [item for item in os.listdir(dir_path) if is_image(item)]
        if items:
            for item in items:
                self.label_core.left.up.treeview.insert('', tk.END, item, values=(item,))
            self.label_core.left.up.treeview.focus_set()
            self.label_core.left.up.treeview.selection_set(items[0])
            self.label_core.left.up.treeview.focus(items[0])
            self.select()
        else:
            self.label_core.window.config(image='')
            self.statusbar.config(text='')


    def set_input(self):
        dir_path = askdirectory()
        if dir_path:
            self.input_dir = dir_path
            self.current = 'input'
            self.switch_dir(self.input_dir)


    def set_output(self):
        dir_path = askdirectory()
        for item in os.listdir(dir_path):
            if not os.path.isdir(os.path.join(dir_path, item)):
                break
        else:
            self.output_dir = dir_path
            self.statusbar.config(text='{}:{}'.format(self.setting.language.info_set_output, self.output_dir))

    def select(self):
        self.input_item = self.label_core.left.up.treeview.focus()
        item_path = os.path.join(self.input_dir, self.input_item) if self.current == 'input' else os.path.join(self.output_dir, self.current, self.input_item)
        try:
            self.image = ImageTk.PhotoImage(Image.open(item_path))
        except:
            self.statusbar.config(text='{}'.format(self.setting.language.error_open_image))
        else:
            self.show()

    def show(self):
        win_width = self.label_core.window.winfo_width()
        win_height = self.label_core.window.winfo_height()
        if self.image:
            image = ImageTk.getimage(self.image)
            ratio = min(win_width/image.width, win_height/image.height)
            image = image.resize((int(ratio * image.width), int(ratio * image.height)), Image.LINEAR)
            self.resize_image = ImageTk.PhotoImage(image)
            self.label_core.window.config(image=self.resize_image)
            self.statusbar.config(text='进度：{}/{}'.format(self.label_core.left.up.treeview.index(self.input_item) + 1, 
                                len(self.label_core.left.up.treeview.get_children())))




        

         


                            


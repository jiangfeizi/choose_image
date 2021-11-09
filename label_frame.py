import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory
from tkinter.simpledialog import askstring
import yaml
import os
import shutil
from PIL import Image, ImageTk

from utils import resource_path, is_image


class LabelFrame(ttk.Frame):
    def __init__(self, master, language):
        ttk.Frame.__init__(self, master)
        self.language = language

        self.setting_path = resource_path('setting\label_frame_setting.yaml')
        self.setting = yaml.load(open(self.setting_path, encoding='utf8'))
        
        # 内置参数
        self.current = None
        self.input_dir = None
        self.output_dir = None
        self.class_list = []
        self.class_key = [0]
        self.class_button = []
        self.image = None
        self.resize_image = None
        
        self.panedwindow = self.make_panedwindow(self)
        self.statusbar = ttk.Label(self)

        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.panedwindow.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.after(50, self.load_sashpos)

    def make_panedwindow(self, master):
        self.panedwindow = ttk.PanedWindow(master, orient=tk.HORIZONTAL)

        self.left = self.make_left(self.panedwindow)
        self.window = tk.Label(self.panedwindow)

        self.left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.window.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.panedwindow.add(self.left) #必须先pack然后add
        self.panedwindow.add(self.window)

        self.window.bind('<Configure>', lambda event : self.resize_window())

        return self.panedwindow


    def make_left(self, master):
        self.left = ttk.Frame(master)

        self.left_up = self.make_left_up(self.left)
        self.left_mid = self.make_left_mid(self.left)
        self.left_down = self.make_left_down(self.left)

        self.left_down.pack(side=tk.BOTTOM, fill=tk.X)
        self.left_mid.pack(side=tk.BOTTOM, anchor=tk.W)
        self.left_up.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        return self.left

    def make_left_up(self, master):
        self.left_up = ttk.Frame(master)

        self.input_button = ttk.Button(self.left_up, text=self.setting[self.language]['input_button'], command=self.set_input)
        self.input_treeview = ttk.Treeview(self.left_up)
        self.input_scrollbar = ttk.Scrollbar(self.left_up)
        self.button_set = self.make_button_set(self.left_up)
        self.input_menu = tk.Menu(self.left_up, tearoff=tk.OFF)

        self.input_scrollbar.config(command=self.input_treeview.yview)                    
        self.input_treeview.config(yscrollcommand=self.input_scrollbar.set)

        self.input_treeview.config(columns=(1,), show='headings')
        self.input_treeview.heading(1, text=self.setting[self.language]['input_treeview_heading'])

        self.button_set.pack(side=tk.LEFT, fill=tk.Y)
        self.input_button.pack(side=tk.TOP, anchor=tk.W) 
        self.input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.input_treeview.bind('<<TreeviewSelect>>', lambda event : self.select_item())
        self.input_treeview.bind('<Double-Button-1>', lambda event : self.post_input_menu(event))
        self.input_menu.add_command(label=self.setting[self.language]['menu_delete'], command=self.delete_item_and_remove_file)

        return self.left_up

    def make_button_set(self, master):
        self.button_set = ttk.Frame(master)

        self.ret_button = ttk.Button(self.button_set, text=self.vertical_str(self.setting[self.language]['return_button']), width=2, command=self.tip_no_input_dir)

        self.ret_button.pack(side=tk.TOP)

        return self.button_set

    def make_left_mid(self, master):
        self.left_mid = ttk.Frame(master)

        self.output_button = ttk.Button(self.left_mid, text=self.setting[self.language]['output_button'], command=self.set_output)
        self.add_button = ttk.Button(self.left_mid, text=self.setting[self.language]['add_button'], command=self.add_class)

        self.output_button.pack(side=tk.LEFT)
        self.add_button.pack(side=tk.LEFT)

        return self.left_mid

    def make_left_down(self, master):
        self.left_down = ttk.Frame(master)

        self.class_treeview = ttk.Treeview(self.left_down)
        self.class_scrollbar = ttk.Scrollbar(self.left_down)
        self.class_menu = tk.Menu(self.left_down, tearoff=tk.OFF)

        self.class_scrollbar.config(command=self.class_treeview.yview)                    
        self.class_treeview.config(yscrollcommand=self.class_scrollbar.set)  

        self.class_treeview.config(columns=(1, 2, 3), show='headings')
        self.class_treeview.column(1, width=80, anchor=tk.CENTER)
        self.class_treeview.column(2, width=80, anchor=tk.CENTER)
        self.class_treeview.column(3, width=80, anchor=tk.CENTER)
        self.class_treeview.heading(1, text=self.setting[self.language]['class_treeview_heading'][0])
        self.class_treeview.heading(2, text=self.setting[self.language]['class_treeview_heading'][1])
        self.class_treeview.heading(3, text=self.setting[self.language]['class_treeview_heading'][2])

        self.class_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.class_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
        self.class_treeview.bind('<Double-Button-1>', lambda event : self.post_class_menu(event))
        self.class_menu.add_command(label=self.setting[self.language]['menu_delete'], command=self.delete_class)
        self.class_menu.add_command(label=self.setting[self.language]['menu_change_key'], command=self.change_key)

        return self.left_down

    def load_sashpos(self):
        self.panedwindow.sashpos(0, self.setting['sashpos'])

    def change_key(self):
        ask_key = tk.Toplevel()
        buttons = []
        for i in range(1, 10):
            if not i in self.class_key:
                button = ttk.Button(ask_key, text=i, command=lambda toplevel=ask_key, i=i: self.bind_key(toplevel, i))
                button.pack()
                buttons.append(button)

        ask_key.geometry('+{}+{}'.format(self.curse_x, self.curse_y))

        ask_key.grab_set()
        ask_key.focus_set()
        ask_key.wait_window()

    def bind_key(self, toplevel, key):
        dir_path = self.class_treeview.focus()
        self.input_treeview.bind('<Control-Key-{}>'.format(key), lambda event, dir_path=dir_path:self.switch_dir(dir_path))
        self.input_treeview.bind('<Key-{}>'.format(key), lambda event, dir_path=dir_path:self.move_to_dir(dir_path))
        self.class_treeview.set(dir_path, column=3, value=key)
        self.class_key[self.class_list.index(self.class_treeview.set(dir_path, column=1)) + 1] = key
        toplevel.destroy()
        self.input_treeview.focus_set()

    def move_to_dir(self, dir_path):
        image_item = self.input_treeview.focus()
        if image_item:
            image_path = os.path.join(self.current, image_item)
            if self.current != dir_path:
                shutil.move(image_path, os.path.join(dir_path, image_item))
                self.delete_item()
                if dir_path != self.input_dir:
                    num = self.class_treeview.set(dir_path, column=2)
                    self.class_treeview.set(dir_path, column=2, value=int(num)+1)


    def resize_window(self):
        win_width = self.window.winfo_width()
        win_height = self.window.winfo_height()
        if self.image:
            ratio = min(win_width/self.image.width, win_height/self.image.height)
            image = self.image.resize((int(ratio * self.image.width), int(ratio * self.image.height)), Image.LINEAR)
            self.resize_image = ImageTk.PhotoImage(image)
            self.window.config(image=self.resize_image)

    def delete_item(self):
        item = self.input_treeview.focus()
        index = self.input_treeview.index(item)
        all_item = self.input_treeview.get_children()
        length = len(all_item)

        if index == length-1:
            if index != 0:
                self.input_treeview.selection_set(all_item[index-1])
                self.input_treeview.focus(all_item[index-1])
                self.select_item()
            else:
                self.clear_image()
                self.clear_statusbar()
        else:
            self.input_treeview.selection_set(all_item[index+1])
            self.input_treeview.focus(all_item[index+1])
            self.select_item()

        self.input_treeview.delete(item)

        if self.current != self.input_dir:
            num = self.class_treeview.set(self.current, column=2)
            self.class_treeview.set(self.current, column=2, value=int(num)-1)

        return item

    def delete_item_and_remove_file(self):
        item = self.delete_item()

        item_path = os.path.join(self.current, item)
        os.remove(item_path)

    def delete_class(self):
        item = self.class_treeview.focus()
        self.input_treeview.unbind('<Control-Key-{}>'.format(self.class_treeview.set(item, column=3)))
        self.input_treeview.unbind('<Key-{}>'.format(self.class_treeview.set(item, column=3)))
        
        index = self.class_list.index(self.class_treeview.set(item, column=1))
        self.class_treeview.delete(item)

        self.class_list.pop(index)
        self.class_key.pop(index+1)

        self.class_button[index].destroy()
        self.class_button.pop(index)

        if self.current == item:
            self.switch_dir(self.input_dir)


    def switch_dir(self, dir_path):
        self.current = dir_path

        for i in self.input_treeview.get_children():
            self.input_treeview.delete(i)
        items = [item for item in os.listdir(dir_path) if is_image(item)]

        if items:
            for item in items:
                self.input_treeview.insert('', tk.END, item, values=(item,))
            self.input_treeview.focus_set()
            self.input_treeview.selection_set(items[0])
            self.input_treeview.focus(items[0])
            self.select_item()
        else:
            self.clear_image()
            self.clear_statusbar()

    def clear_image(self):
        self.image = None
        self.window.config(image='')

    def clear_statusbar(self):
        self.statusbar.config(text='')

    def tip_no_input_dir(self):
        self.statusbar.config(text='{}'.format(self.setting[self.language]['info_no_input_dir']))


    def select_item(self):
        item = self.input_treeview.focus()
        item_path = os.path.join(self.current, item)

        try:
            self.image = Image.open(item_path)
        except:
            self.clear_image()
            self.statusbar.config(text='{}'.format(self.setting[self.language]['info_open_image']))
        else:
            self.resize_window()
            self.statusbar.config(text='{}：{}/{}'.format(self.setting[self.language]['progress'], self.input_treeview.index(item) + 1, 
                                len(self.input_treeview.get_children())))


    def vertical_str(self, str):
        return '\n'.join(list(str))

    def post_input_menu(self, event):
        if self.input_treeview.focus():
            self.input_menu.post(event.x_root, event.y_root)

    def post_class_menu(self, event):
        if self.class_treeview.focus():
            self.class_menu.post(event.x_root, event.y_root)

            self.curse_x = event.x_root
            self.curse_y = event.y_root

    def add_class(self):
        if self.output_dir:
            if len(self.class_list) < 9:
                item = askstring('{}'.format(self.setting[self.language]['info_add_class']), '{}'.format(self.setting[self.language]['info_add_class']))
                if item:
                    item = item.strip()
                    if not item in self.class_list:
                        self.class_list.append(item)
                        dir_path = os.path.join(self.output_dir, item)
                        if not os.path.exists(dir_path):
                            os.mkdir(dir_path)

                        for key in range(1, 10):
                            if not key in self.class_key:
                                break
                        self.class_key.append(key)
                        
                        images = [image for image in os.listdir(dir_path) if is_image(image)]
                        self.class_treeview.insert('', tk.END, dir_path, values = (item, len(images), key))
                        
                        button = ttk.Button(self.button_set, text=self.vertical_str(item), width=2)
                        button.pack(side=tk.TOP)
                        button.config(command=lambda item=dir_path:self.switch_dir(item))
                        self.input_treeview.bind('<Control-Key-{}>'.format(key), lambda event, dir_path=dir_path:self.switch_dir(dir_path))
                        self.input_treeview.bind('<Key-{}>'.format(key), lambda event, dir_path=dir_path:self.move_to_dir(dir_path))
                        self.class_button.append(button)
                        self.input_treeview.focus_set()
                    else:
                        self.statusbar.config(text='{}'.format(self.setting[self.language]['info_repeat_create']))
            else:
                self.statusbar.config(text='{}'.format(self.setting[self.language]['info_class_limit']))
        else:
            self.statusbar.config(text='{}'.format(self.setting[self.language]['info_no_output_dir']))


    def set_output(self):
        dir_path = askdirectory()
        if dir_path:
            if self.current != self.input_dir:
                self.switch_dir(self.input_dir)

            for i in self.class_treeview.get_children():
                self.class_treeview.focus(i)
                self.delete_class()

            self.output_dir = dir_path
            self.statusbar.config(text='{}:{}'.format(self.setting[self.language]['info_set_output'], self.output_dir))

    def set_input(self):
        dir_path = askdirectory()
        if dir_path:
            self.input_dir = dir_path 
            self.switch_dir(self.input_dir)

            self.ret_button.config(command=lambda dir_path=self.input_dir : self.switch_dir(dir_path))
            self.input_treeview.bind('<Control-s>', lambda event, dir_path=self.input_dir:self.switch_dir(dir_path))
            self.input_treeview.bind('<s>', lambda event, dir_path=self.input_dir:self.move_to_dir(dir_path))

    def save_setting(self):
        sashpos = self.panedwindow.sashpos(0)
        self.panedwindow.sashpos(0)
        self.setting.update({'sashpos': sashpos})
        yaml.dump(self.setting, open(self.setting_path, 'w', encoding='utf8'))
        

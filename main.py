# from utils import *
from tkinter.constants import TOP
from PIL import ImageTk, Image
from setting import Setting
import os
import shutil

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory
from tkinter.simpledialog import askstring
from utils import is_image



class Gui(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        self.setting = Setting('setting.yaml')

        # 内置参数
        ## label
        self.label_input_dir = None
        self.label_output_dir = None
        self.label_class_list = []
        self.label_class_key = [0]
        self.label_class_button = []

        self.label_current = None
        self.label_image = None
        self.label_resize_image = None

        self.notebook = ttk.Notebook(self)
        # 三个框架
        self.label_frame = ttk.Frame(self.notebook)
        self.train_frame = ttk.Frame(self.notebook)
        self.eval_frame = ttk.Frame(self.notebook)

        self.label_frame.pack(fill=tk.BOTH, expand=True)
        self.train_frame.pack(fill=tk.BOTH, expand=True)
        self.eval_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook.add(self.label_frame, text=self.setting.language.notebook_label)
        self.notebook.add(self.train_frame, text=self.setting.language.notebook_train)
        self.notebook.add(self.eval_frame, text=self.setting.language.notebook_eval)
 
        self.notebook.pack(fill=tk.BOTH, expand=True)


        # 界面
        ## label界面
        self.label_input_right_menu = tk.Menu(self.label_frame, tearoff=tk.OFF)
        self.label_output_right_menu = tk.Menu(self.label_frame, tearoff=tk.OFF)

        self.label_panedwindow = ttk.PanedWindow(self.label_frame, orient=tk.HORIZONTAL)
        self.label_statusbar = ttk.Label(self.label_frame)

        self.label_left = ttk.Frame(self.label_panedwindow)
        self.label_window = tk.Label(self.label_panedwindow)

        self.label_left_up = ttk.Frame(self.label_left)
        self.label_left_mid = ttk.Frame(self.label_left)
        self.label_left_down = ttk.Frame(self.label_left)

        self.label_input_button = ttk.Button(self.label_left_up)
        self.label_input_treeview = ttk.Treeview(self.label_left_up)
        self.label_input_scrollbar = ttk.Scrollbar(self.label_left_up)
        self.label_button_set = ttk.Frame(self.label_left_up)

        self.label_ret_button = ttk.Button(self.label_button_set)

        self.label_output_button = ttk.Button(self.label_left_mid)
        self.label_add_button = ttk.Button(self.label_left_mid)

        self.label_output_treeview = ttk.Treeview(self.label_left_down)
        self.label_output_scrollbar = ttk.Scrollbar(self.label_left_down)


        # 配置
        self.geometry('{}'.format(self.setting.geometry))

        ## label界面配置
        self.label_input_button.config(text=self.setting.language.label_input_button)
        self.label_ret_button.config(text=self.vertical_str(self.setting.language.label_ret_button), width=2)
        self.label_output_button.config(text=self.setting.language.label_output_button)
        self.label_add_button.config(text=self.setting.language.label_add_button)

        self.label_input_treeview.config(columns=(1,), show='headings')
        self.label_input_treeview.heading(1, text=self.setting.language.label_filename)
        self.label_output_treeview.config(columns=(1, 2, 3), show='headings')
        self.label_output_treeview.column(1, width=80, anchor=tk.CENTER)
        self.label_output_treeview.column(2, width=80, anchor=tk.CENTER)
        self.label_output_treeview.column(3, width=80, anchor=tk.CENTER)

        self.label_output_treeview.heading(1, text=self.setting.language.label_table_class)
        self.label_output_treeview.heading(2, text=self.setting.language.label_table_num)
        self.label_output_treeview.heading(3, text=self.setting.language.label_table_key)



        # 布局
        self.label_statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.label_panedwindow.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.label_left.pack(side=tk.LEFT, fill=tk.Y)
        self.label_window.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.label_panedwindow.add(self.label_left) #必须先pack然后add
        self.label_panedwindow.add(self.label_window)

        self.label_left_down.pack(side=tk.BOTTOM, fill=tk.X)
        self.label_left_mid.pack(side=tk.BOTTOM, anchor=tk.W)
        self.label_left_up.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


        self.label_button_set.pack(side=tk.LEFT, fill=tk.Y)
        self.label_input_button.pack(side=tk.TOP, anchor=tk.W) 
        self.label_input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.label_input_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.label_ret_button.pack(side=tk.TOP)

        self.label_output_button.pack(side=tk.LEFT)
        self.label_add_button.pack(side=tk.LEFT)

        self.label_output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.label_output_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


        #事件绑定
        self.protocol('WM_DELETE_WINDOW', self.save_setting)

        ## label
        self.label_input_right_menu.add_command(label=self.setting.language.label_menu_delete, command=self.label_delete_item_and_remove_file)
        self.label_output_right_menu.add_command(label=self.setting.language.label_menu_delete, command=self.label_delete_class)
        self.label_output_right_menu.add_command(label=self.setting.language.label_menu_change_key, command=self.label_change_key)

        self.label_input_scrollbar.config(command=self.label_input_treeview.yview)                    
        self.label_input_treeview.config(yscrollcommand=self.label_input_scrollbar)  

        self.label_output_scrollbar.config(command=self.label_output_treeview.yview)                    
        self.label_output_treeview.config(yscrollcommand=self.label_output_scrollbar.set)  

        self.label_input_button.config(command=self.label_set_input)
        self.label_output_button.config(command=self.label_set_output)
        self.label_add_button.config(command=self.label_add_class)
        self.label_ret_button.config(command=lambda item=None : self.label_switch_item(item))

        self.label_input_treeview.bind('<Control-s>', lambda event, item=None:self.label_switch_item(item))
        self.label_input_treeview.bind('<s>', lambda event, item=None:self.label_move_to_item(item))
        self.label_input_treeview.bind('<<TreeviewSelect>>', lambda event : self.label_select_item())
        self.label_input_treeview.bind('<Double-Button-1>', lambda event : self.label_post_input_right_menu(event))
        self.label_output_treeview.bind('<Double-Button-1>', lambda event : self.label_post_output_right_menu(event))


        self.label_window.bind('<Configure>', lambda event : self.label_resize_window())

    def label_change_key(self):
        label_askstring = tk.Toplevel()
        buttons = []
        for i in range(1, 10):
            if not i in self.label_class_key:
                button = ttk.Button(label_askstring, text=i, command=lambda toplevel=label_askstring, i=i: self.label_bind_key(toplevel, i))
                button.pack()
                buttons.append(button)

        label_askstring.geometry('+{}+{}'.format(self.label_curse_x, self.label_curse_y))



    def label_bind_key(self, toplevel, key):
        item = self.label_output_treeview.focus()
        self.label_input_treeview.bind('<Control-Key-{}>'.format(key), lambda event, item=item:self.label_switch_item(item))
        self.label_input_treeview.bind('<Key-{}>'.format(key), lambda event, item=item:self.label_move_to_item(item))
        self.label_output_treeview.set(item, column=3, value=key)
        toplevel.destroy()


    def label_move_to_item(self, item):
        image_item = self.label_input_treeview.focus()
        if image_item:
            image_path = os.path.join(self.label_output_dir, self.label_current, image_item) if self.label_current else os.path.join(self.label_input_dir, image_item)
            if self.label_current != item:
                if item:
                    shutil.move(image_path, os.path.join(self.label_output_dir, item, image_item))
                    self.label_delete_item()
                    num = self.label_output_treeview.set(item, column=2)
                    self.label_output_treeview.set(item, column=2, value=int(num)+1)
                else:
                    if self.label_input_dir:
                        shutil.move(image_path, os.path.join(self.label_input_dir, image_item))
                        self.label_delete_item()
                    else:
                        self.label_statusbar.config(text='{}'.format(self.setting.language.label_error_no_input_dir))


    def label_resize_window(self):
        win_width = self.label_window.winfo_width()
        win_height = self.label_window.winfo_height()

        if self.label_image:
            ratio = min(win_width/self.label_image.width, win_height/self.label_image.height)
            image = self.label_image.resize((int(ratio * self.label_image.width), int(ratio * self.label_image.height)), Image.LINEAR)
            self.resize_image = ImageTk.PhotoImage(image)
            self.label_window.config(image=self.resize_image)


    def label_delete_item(self):
        item = self.label_input_treeview.focus()
        index = self.label_input_treeview.index(item)
        all_item = self.label_input_treeview.get_children()
        length = len(all_item)

        if index == length-1:
            if index != 0:
                self.label_input_treeview.selection_set(all_item[index-1])
                self.label_input_treeview.focus(all_item[index-1])
        else:
            self.label_input_treeview.selection_set(all_item[index+1])
            self.label_input_treeview.focus(all_item[index+1])

        self.label_input_treeview.delete(item)

        if self.label_current:
            num = self.label_output_treeview.set(self.label_current, column=2)
            self.label_output_treeview.set(self.label_current, column=2, value=int(num)-1)

        self.label_select_all()
        return item

    def label_delete_item_and_remove_file(self):
        item = self.label_delete_item()

        item_path = os.path.join(self.label_output_dir, self.label_current, item) if self.label_current else os.path.join(self.label_input_dir, item)
        os.remove(item_path)

    def label_delete_class(self):
        item = self.label_output_treeview.focus()
        self.label_input_treeview.unbind('<Control-Key-{}>'.format(self.label_output_treeview.set(item, column=3)))
        self.label_input_treeview.unbind('<Key-{}>'.format(self.label_output_treeview.set(item, column=3)))


        self.label_output_treeview.delete(item)
        index = self.label_class_list.index(item)

        self.label_class_list.pop(index)
        self.label_class_key.pop(index+1)

        self.label_class_button[index].destroy()
        self.label_class_button.pop(index)


        if self.label_current == item:
            self.label_switch_item(None)

    def label_select_all(self):
        item = self.label_input_treeview.focus()
        if item:
            self.label_select_item()
        else:
            self.label_select_no()


    def label_switch_item(self, item):
        self.label_current = item
        if item:
            dir_path = os.path.join(self.label_output_dir, item)
        else:
            dir_path = self.label_input_dir

        for i in self.label_input_treeview.get_children():
            self.label_input_treeview.delete(i)
        items = [item for item in os.listdir(dir_path) if is_image(item)]

        if items:
            for item in items:
                self.label_input_treeview.insert('', tk.END, item, values=(item,))
            self.label_input_treeview.focus_set()
            self.label_input_treeview.selection_set(items[0])
            self.label_input_treeview.focus(items[0])
            self.label_select_item()
        else:
            self.label_select_no()

    def label_select_no(self):
        self.label_image = None
        self.label_window.config(image='')
        self.label_statusbar.config(text='')

    def label_select_item(self):
        item = self.label_input_treeview.focus()
        item_path = os.path.join(self.label_output_dir, self.label_current,  item) if self.label_current else os.path.join(self.label_input_dir, item)

        try:
            self.label_image = Image.open(item_path)
        except:
            self.label_window.config(image='')
            self.label_statusbar.config(text='{}'.format(self.setting.language.label_error_open_image))
        else:
            self.label_resize_window()
            self.label_statusbar.config(text='{}：{}/{}'.format(self.setting.language.label_progress, self.label_input_treeview.index(item) + 1, 
                                len(self.label_input_treeview.get_children())))


    def vertical_str(self, str):
        return '\n'.join(list(str))

    def label_post_input_right_menu(self, event):
        if self.label_input_treeview.focus():
            self.label_input_right_menu.post(event.x_root, event.y_root)

    def label_post_output_right_menu(self, event):
        if self.label_output_treeview.focus():
            self.label_output_right_menu.post(event.x_root, event.y_root)

            self.label_curse_x = event.x_root
            self.label_curse_y = event.y_root

        
    def label_add_class(self):
        if self.label_output_dir:
            if len(self.label_class_list) < 9:
                item = askstring('{}'.format(self.setting.language.label_info_output_tip), '{}'.format(self.setting.language.label_info_output_tip))
                if item:
                    item = item.strip()
                    if not item in self.label_class_list:
                        self.label_class_list.append(item)
                        item_path = os.path.join(self.label_output_dir, item)
                        if not os.path.exists(item_path):
                            os.mkdir(item_path)

                        key = max(self.label_class_key)+1
                        self.label_class_key.append(key)
                        
                        images = [image for image in os.listdir(item_path) if is_image(image)]
                        self.label_output_treeview.insert('', tk.END, item, values = (item, len(images), key))
                        
                        button = ttk.Button(self.label_button_set, text=item, width=2)
                        button.pack(side=TOP)
                        button.config(command=lambda item=item:self.label_switch_item(item))
                        self.label_input_treeview.bind('<Control-Key-{}>'.format(key), lambda event, item=item:self.label_switch_item(item))
                        self.label_input_treeview.bind('<Key-{}>'.format(key), lambda event, item=item:self.label_move_to_item(item))
                        self.label_class_button.append(button)

                        self.label_input_treeview.focus_set()

                    else:
                        self.label_statusbar.config(text='{}'.format(self.setting.language.label_error_multi_create))
            else:
                self.label_statusbar.config(text='{}'.format(self.setting.language.label_error_class_limit))
        else:
            self.label_statusbar.config(text='{}'.format(self.setting.language.label_error_no_output_dir))


    def label_set_output(self):
        dir_path = askdirectory()
        if dir_path:
            if self.label_current:
                self.label_switch_item(None)
            self.label_class_list = []
            self.label_class_key = [0]
            for button in self.label_class_button:
                button.destroy()
            self.label_class_button = []

            for i in self.label_output_treeview.get_children():
                self.label_output_treeview.delete(i)
            self.label_output_dir = dir_path
            self.label_statusbar.config(text='{}:{}'.format(self.setting.language.label_info_set_output, self.label_output_dir))


    def label_set_input(self):
        dir_path = askdirectory()
        if dir_path:
            self.label_input_dir = dir_path
            self.label_switch_item(None)



    def save_setting(self):
        geometry = self.geometry()
        self.setting._setting.update({'geometry': geometry})
        self.setting.save_setting()
        self.quit()
        



one = Gui()

one.mainloop()

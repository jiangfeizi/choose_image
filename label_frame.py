# from utils import *
from PIL import ImageTk, Image
from setting import Setting
import os
import shutil

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory
from tkinter.simpledialog import askstring
from utils import is_image, resource_path



class LabelFrame(ttk.Frame):
    def __init__(self, master, setting, thread_queue):
        ttk.Frame.__init__(self, master)
        self.setting = setting
        self.thread_queue = thread_queue

        self.input_dir = None
        self.output_dir = None
        self.class_list = []
        self.class_key = [0]
        self.class_button = []

        self.current = None
        self.image = None
        self.resize_image = None

        # 界面
        self.panedwindow = self.make_panedwindow(self)
        self.statusbar = ttk.Label(self)

        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.panedwindow.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


    def make_panedwindow(self, master):
        self.panedwindow = ttk.PanedWindow(master, orient=tk.HORIZONTAL)

        self.left = self.make_left(self.panedwindow)
        self.window = tk.Label(self.panedwindow)

        self.left.pack(side=tk.LEFT, fill=tk.Y)
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

        self.input_button = ttk.Button(self.left_up, text=self.setting.language.label_input_button, command=self.set_input)
        self.input_treeview = ttk.Treeview(self.left_up)
        self.input_scrollbar = ttk.Scrollbar(self.left_up)
        self.button_set = self.make_button_set(self.left_up)
        self.input_right_menu = tk.Menu(self.left_up, tearoff=tk.OFF)

        self.input_scrollbar.config(command=self.input_treeview.yview)                    
        self.input_treeview.config(yscrollcommand=self.input_scrollbar)  
        self.input_treeview.config(columns=(1,), show='headings')
        self.input_treeview.heading(1, text=self.setting.language.label_filename)

        self.button_set.pack(side=tk.LEFT, fill=tk.Y)
        self.input_button.pack(side=tk.TOP, anchor=tk.W) 
        self.input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.input_treeview.bind('<Control-s>', lambda event, item=None:self.switch_item(item))
        self.input_treeview.bind('<s>', lambda event, item=None:self.move_to_item(item))
        self.input_treeview.bind('<<TreeviewSelect>>', lambda event : self.select_item())
        self.input_treeview.bind('<Double-Button-1>', lambda event : self.post_input_right_menu(event))
        self.input_right_menu.add_command(label=self.setting.language.label_menu_delete, command=self.delete_item_and_remove_file)

        return self.left_up

    def make_button_set(self, master):
        self.button_set = ttk.Frame(master)

        self.ret_button = ttk.Button(self.button_set, text=self.vertical_str(self.setting.language.label_ret_button),
                                    width=2, command=lambda item=None : self.switch_item(item))

        self.ret_button.pack(side=tk.TOP)

        return self.button_set

    def make_left_mid(self, master):
        self.left_mid = ttk.Frame(master)

        self.output_button = ttk.Button(self.left_mid, text=self.setting.language.label_output_button, command=self.set_output)
        self.add_button = ttk.Button(self.left_mid, text=self.setting.language.label_add_button, command=self.add_class)

        self.output_button.pack(side=tk.LEFT)
        self.add_button.pack(side=tk.LEFT)

        return self.left_mid

    def make_left_down(self, master):
        self.left_down = ttk.Frame(master)

        self.output_treeview = ttk.Treeview(self.left_down)
        self.output_scrollbar = ttk.Scrollbar(self.left_down)
        self.output_right_menu = tk.Menu(self.left_down, tearoff=tk.OFF)

        self.output_scrollbar.config(command=self.output_treeview.yview)                    
        self.output_treeview.config(yscrollcommand=self.output_scrollbar.set)  
        self.output_treeview.config(columns=(1, 2, 3), show='headings')
        self.output_treeview.column(1, width=80, anchor=tk.CENTER)
        self.output_treeview.column(2, width=80, anchor=tk.CENTER)
        self.output_treeview.column(3, width=80, anchor=tk.CENTER)
        self.output_treeview.heading(1, text=self.setting.language.label_table_class)
        self.output_treeview.heading(2, text=self.setting.language.label_table_num)
        self.output_treeview.heading(3, text=self.setting.language.label_table_key)


        self.output_treeview.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.output_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
    
        self.output_treeview.bind('<Double-Button-1>', lambda event : self.post_output_right_menu(event))
        self.output_right_menu.add_command(label=self.setting.language.label_menu_delete, command=self.delete_class)
        self.output_right_menu.add_command(label=self.setting.language.label_menu_change_key, command=self.change_key)

        return self.left_down

    def change_key(self):
        askstring = tk.Toplevel()
        buttons = []
        for i in range(1, 10):
            if not i in self.class_key:
                button = ttk.Button(askstring, text=i, command=lambda toplevel=askstring, i=i: self.bind_key(toplevel, i))
                button.pack()
                buttons.append(button)

        askstring.geometry('+{}+{}'.format(self.curse_x, self.curse_y))



    def bind_key(self, toplevel, key):
        item = self.output_treeview.focus()
        self.input_treeview.bind('<Control-Key-{}>'.format(key), lambda event, item=item:self.switch_item(item))
        self.input_treeview.bind('<Key-{}>'.format(key), lambda event, item=item:self.move_to_item(item))
        self.output_treeview.set(item, column=3, value=key)
        toplevel.destroy()


    def move_to_item(self, item):
        image_item = self.input_treeview.focus()
        if image_item:
            image_path = os.path.join(self.output_dir, self.current, image_item) if self.current else os.path.join(self.input_dir, image_item)
            if self.current != item:
                if item:
                    shutil.move(image_path, os.path.join(self.output_dir, item, image_item))
                    self.delete_item()
                    num = self.output_treeview.set(item, column=2)
                    self.output_treeview.set(item, column=2, value=int(num)+1)
                else:
                    if self.input_dir:
                        shutil.move(image_path, os.path.join(self.input_dir, image_item))
                        self.delete_item()
                    else:
                        self.statusbar.config(text='{}'.format(self.setting.language.label_error_no_input_dir))

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
        else:
            self.input_treeview.selection_set(all_item[index+1])
            self.input_treeview.focus(all_item[index+1])

        self.input_treeview.delete(item)

        if self.current:
            num = self.output_treeview.set(self.current, column=2)
            self.output_treeview.set(self.current, column=2, value=int(num)-1)

        self.select_all()
        return item

    def delete_item_and_remove_file(self):
        item = self.delete_item()

        item_path = os.path.join(self.output_dir, self.current, item) if self.current else os.path.join(self.input_dir, item)
        os.remove(item_path)

    def delete_class(self):
        item = self.output_treeview.focus()
        self.input_treeview.unbind('<Control-Key-{}>'.format(self.output_treeview.set(item, column=3)))
        self.input_treeview.unbind('<Key-{}>'.format(self.output_treeview.set(item, column=3)))


        self.output_treeview.delete(item)
        index = self.class_list.index(item)

        self.class_list.pop(index)
        self.class_key.pop(index+1)

        self.class_button[index].destroy()
        self.class_button.pop(index)


        if self.current == item:
            self.switch_item(None)

    def select_all(self):
        item = self.input_treeview.focus()
        if item:
            self.select_item()
        else:
            self.select_no()


    def switch_item(self, item):
        self.current = item
        if item:
            dir_path = os.path.join(self.output_dir, item)
        else:
            dir_path = self.input_dir

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
            self.select_no()

    def select_no(self):
        self.image = None
        self.window.config(image='')
        self.statusbar.config(text='')

    def select_item(self):
        item = self.input_treeview.focus()
        item_path = os.path.join(self.output_dir, self.current,  item) if self.current else os.path.join(self.input_dir, item)

        try:
            self.image = Image.open(item_path)
        except:
            self.window.config(image='')
            self.statusbar.config(text='{}'.format(self.setting.language.label_error_open_image))
        else:
            self.resize_window()
            self.statusbar.config(text='{}：{}/{}'.format(self.setting.language.label_progress, self.input_treeview.index(item) + 1, 
                                len(self.input_treeview.get_children())))


    def vertical_str(self, str):
        return '\n'.join(list(str))

    def post_input_right_menu(self, event):
        if self.input_treeview.focus():
            self.input_right_menu.post(event.x_root, event.y_root)

    def post_output_right_menu(self, event):
        if self.output_treeview.focus():
            self.output_right_menu.post(event.x_root, event.y_root)

            self.curse_x = event.x_root
            self.curse_y = event.y_root

        
    def add_class(self):
        if self.output_dir:
            if len(self.class_list) < 9:
                item = askstring('{}'.format(self.setting.language.label_info_output_tip), '{}'.format(self.setting.language.label_info_output_tip))
                if item:
                    item = item.strip()
                    if not item in self.class_list:
                        self.class_list.append(item)
                        item_path = os.path.join(self.output_dir, item)
                        if not os.path.exists(item_path):
                            os.mkdir(item_path)

                        key = max(self.class_key)+1
                        self.class_key.append(key)
                        
                        images = [image for image in os.listdir(item_path) if is_image(image)]
                        self.output_treeview.insert('', tk.END, item, values = (item, len(images), key))
                        
                        button = ttk.Button(self.button_set, text=self.vertical_str(item), width=2)
                        button.pack(side=tk.TOP)
                        button.config(command=lambda item=item:self.switch_item(item))
                        self.input_treeview.bind('<Control-Key-{}>'.format(key), lambda event, item=item:self.switch_item(item))
                        self.input_treeview.bind('<Key-{}>'.format(key), lambda event, item=item:self.move_to_item(item))
                        self.class_button.append(button)

                        self.input_treeview.focus_set()

                    else:
                        self.statusbar.config(text='{}'.format(self.setting.language.label_error_multi_create))
            else:
                self.statusbar.config(text='{}'.format(self.setting.language.label_error_class_limit))
        else:
            self.statusbar.config(text='{}'.format(self.setting.language.label_error_no_output_dir))


    def set_output(self):
        dir_path = askdirectory()
        if dir_path:
            if self.current:
                self.switch_item(None)
            self.class_list = []
            self.class_key = [0]
            for button in self.class_button:
                button.destroy()
            self.class_button = []

            for i in self.output_treeview.get_children():
                self.input_treeview.unbind('<Control-Key-{}>'.format(self.output_treeview.set(i, column=3)))
                self.input_treeview.unbind('<Key-{}>'.format(self.output_treeview.set(i, column=3)))
                self.output_treeview.delete(i)
            self.output_dir = dir_path
            self.statusbar.config(text='{}:{}'.format(self.setting.language.label_info_set_output, self.output_dir))


    def set_input(self):
        dir_path = askdirectory()
        if dir_path:
            self.input_dir = dir_path
            self.switch_item(None)



    def save_setting(self):
        geometry = self.geometry()
        self.setting._setting.update({'geometry': geometry})
        self.setting.save_setting()
        self.quit()
        


if __name__=='__main__':
    a = tk.Tk()
    gui = LabelFrame(a, Setting('setting.yaml'))
    gui.mainloop()

from tkinter.filedialog import askdirectory, askopenfilename
from PIL import Image, ImageTk
import numpy as np
import os
import shutil
from tkinter.messagebox import *
import pickle
from tkinter.scrolledtext import ScrolledText
from utils import is_image, resource_path

import tkinter as tk
import tkinter.ttk as ttk
import random
from threading import Thread
from classification.transformer import Transformer
import cv2
import socket
from utils import initListenerSocket
import yaml
import pickle
import io
from PIL import Image
import matplotlib.pyplot as plt
import queue


class TrainFrame(ttk.Frame):
    def __init__(self, master, language):
        ttk.Frame.__init__(self, master)
        self.language = language

        self.setting_path = resource_path('setting\train_frame_setting.yaml')
        self.setting = yaml.load(open(self.setting_path, encoding='utf8'))

        self.thread_queue = queue.Queue(maxsize=0)

        self.port = 50007
        self.sock = initListenerSocket(self.port)
        self.loss_conn = None
        self.log_conn = None
        self.train_log = None

        self.losses = []
        self.val_loss = []

        self.augmentation_add_image = ImageTk.PhotoImage(Image.open(resource_path('res/add-icon.png')))
        self.augmentation_delete_image = ImageTk.PhotoImage(Image.open(resource_path('res/Remove-icon.png')))
        self.dir_image = ImageTk.PhotoImage(Image.open(resource_path('res/Folder-Open-icon_24.png')))
        self.file_image = ImageTk.PhotoImage(Image.open(resource_path('res/File-icon.png')))
        self.start_image = ImageTk.PhotoImage(Image.open(resource_path('res/Start-2-icon.png')))
        self.stop_image = ImageTk.PhotoImage(Image.open(resource_path('res/End-icon.png')))
        self.load_image = ImageTk.PhotoImage(Image.open(resource_path('res/Folder-Open-icon.png')))

        self.augmentation_list = []
        self.augmentation_items = []

        self.left_right_panedwindow = self.make_left_right_panedwindow(self)
        self.left_right_panedwindow.pack(fill=tk.BOTH, expand=True)

        self.check_connect()
        self.check_event()


    def make_left_right_panedwindow(self, master):
        self.left_right_panedwindow = ttk.PanedWindow(master, orient=tk.HORIZONTAL)

        self.left_frame = self.make_left_frame(self.left_right_panedwindow)
        self.right_frame = self.make_right_frame(self.left_right_panedwindow)
        
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.left_right_panedwindow.add(self.left_frame)
        self.left_right_panedwindow.add(self.right_frame)

        return self.left_right_panedwindow


    def make_left_frame(self, master):
        self.left_frame = ttk.Frame(master)

        self.notebook = self.make_notebook(self.left_frame)
        self.label_info = self.make_label_info(self.left_frame)

        self.notebook.pack(side=tk.TOP, fill=tk.X)
        self.label_info.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        return self.left_frame

    def make_right_frame(self, master):
        self.right_frame = ttk.Frame(master)

        self.buttons = self.make_buttons(self.right_frame)
        self.main_window = self.make_main_window(self.right_frame)

        self.buttons.pack(side=tk.TOP)
        self.main_window.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        return self.right_frame

    def make_main_window(self, master):
        self.main_window = ttk.Panedwindow(master)

        self.window = tk.Label(self.main_window, height=30)
        self.text = ScrolledText(self.main_window)
        self.window_image = None
        self.window_image_resize = None

        self.window.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.text.pack(side=tk.BOTTOM, fill=tk.X)
        self.main_window.add(self.window)
        self.main_window.add(self.text)

        self.window.bind('<Configure>', lambda event : self.resize_window())

        return self.main_window

    def make_notebook(self, master):
        self.notebook = ttk.Notebook(master)

        self.hyperparameter_frame = self.make_hyperparameter_frame(self.notebook)
        self.augmentation_frame = self.make_augmentation_frame(self.notebook)

        self.hyperparameter_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.augmentation_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.notebook.add(self.hyperparameter, text=self.setting.language.train_hyperparameter)
        self.notebook.add(self.augmentation, text=self.setting.language.train_augmentation)

        return self.notebook

    def make_augmentation_frame(self, master):
        self.augmentation = ttk.Frame(master)

        self.augmentation_choose_frame = self.make_augmentation_choose_frame(self.augmentation)
        self.augmentation_buttons = self.make_augmentation_buttons(self.augmentation)

        self.augmentation_choose_frame.pack(side=tk.TOP, fill=tk.X)
        self.augmentation_buttons.pack(side=tk.BOTTOM, fill=tk.X)

        return self.augmentation



    def make_augmentation_choose_frame(self, master):
        self.augmentation_choose_frame = ttk.Frame(master)
        self.augmentation_choose_frame.columnconfigure(1, weight=1)
        

        self.augmentation_combobox_var = tk.StringVar()

        self.augmentation_choose_label = tk.Label(self.augmentation_choose_frame, anchor=tk.W, text=self.setting.language.train_aug_choose)
        self.augmentation_combobox = ttk.Combobox(self.augmentation_choose_frame, values=self.setting.language.train_aug_list, textvariable=self.augmentation_combobox_var)
        self.augmentation_add_button = ttk.Button(self.augmentation_choose_frame, image=self.augmentation_add_image, command=self.add_augmentation_item)

        self.augmentation_choose_label.grid(row=20, column=0, sticky=tk.NSEW, ipadx=5)
        self.augmentation_combobox.grid(row=20, column=1, sticky=tk.NSEW)
        self.augmentation_add_button.grid(row=20, column=2, sticky=tk.NSEW)
        
        return self.augmentation_choose_frame

    def make_augmentation_buttons(self, master):
        self.augmentation_buttons = ttk.Frame(master)

        self.augmentation_preview_button = ttk.Button(self.augmentation_buttons, text=self.setting.language.train_aug_preview)
        self.augmentation_reset_button = ttk.Button(self.augmentation_buttons, text=self.setting.language.train_aug_reset)

        self.augmentation_preview_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.augmentation_reset_button.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.augmentation_preview_button.config(command=self.preview_augmentation)
        self.augmentation_reset_button.config(command=self.reset_augmentation)

        return self.augmentation_buttons

    def make_hyperparameter_frame(self, master):
        self.hyperparameter = ttk.Frame(master)

        self.params_some = self.make_params_some(self.hyperparameter)
        self.params_checkbuttons = self.make_params_checkbuttons(self.hyperparameter)

        self.params_some.pack(side=tk.TOP, fill=tk.X)
        self.params_checkbuttons.pack(side=tk.TOP, fill=tk.X, ipady=10)

        return self.hyperparameter

    def make_params_some(self, master):
        self.params_some = ttk.Frame(master)

        self.params_some.rowconfigure(tuple(range(10)), weight=1, minsize=42)
        self.params_some.columnconfigure((1, ), weight=1)

        self.work_dir_var = tk.StringVar()
        self.weights_dir_var = tk.StringVar()
        self.network_var = tk.StringVar(value=self.setting.train_network_values[0])
        self.loss_var = tk.StringVar(value=self.setting.train_losses[0])
        self.epochs_var = tk.IntVar(value=100)
        self.height_var = tk.IntVar(value=224)
        self.width_var = tk.IntVar(value=224)
        self.batchsize_var = tk.IntVar(value=8)
        self.lr_var = tk.DoubleVar(value=0.0001)
        self.workers_var = tk.IntVar(value=2)

        self.work_dir_label = tk.Label(self.params_some, text=self.setting.language.train_work_dir, anchor=tk.W)
        self.work_dir_entry = ttk.Entry(self.params_some, textvariable=self.work_dir_var)
        self.work_dir_button = ttk.Button(self.params_some, image=self.dir_image)
        self.network_label = tk.Label(self.params_some, text=self.setting.language.train_network, anchor=tk.W)
        self.network_combobox = ttk.Combobox(self.params_some, values=self.setting.train_network_values, textvariable=self.network_var)
        self.loss_label = tk.Label(self.params_some, text=self.setting.language.train_loss, anchor=tk.W)
        self.loss_combobox = ttk.Combobox(self.params_some, values=self.setting.train_losses, textvariable=self.loss_var)
        self.network_weights_label = tk.Label(self.params_some, text=self.setting.language.train_network_weights, anchor=tk.W)
        self.network_weights_entry = ttk.Entry(self.params_some, textvariable=self.weights_dir_var)
        self.network_weights_button = ttk.Button(self.params_some, image=self.dir_image)
        self.network_epochs_label = tk.Label(self.params_some, text=self.setting.language.train_epochs, anchor=tk.W)
        self.network_epochs_spinbox = ttk.Spinbox(self.params_some, from_=1, to=10000, textvariable=self.epochs_var)
        self.network_height_label = tk.Label(self.params_some, text=self.setting.language.train_network_height, anchor=tk.W)
        self.network_height_spinbox = ttk.Spinbox(self.params_some, from_=32, to=1024, increment=32, textvariable=self.height_var)
        self.network_width_label = tk.Label(self.params_some, text=self.setting.language.train_network_width, anchor=tk.W)
        self.network_width_spinbox = ttk.Spinbox(self.params_some, from_=32, to=1024, increment=32, textvariable=self.width_var)
        self.network_batchsize_label = tk.Label(self.params_some, text=self.setting.language.train_batch_size, anchor=tk.W)
        self.network_batchsize_spinbox = ttk.Spinbox(self.params_some, from_=1, to=256, textvariable=self.batchsize_var)
        self.network_lr_label = tk.Label(self.params_some, text=self.setting.language.train_lr, anchor=tk.W)
        self.network_lr_spinbox = ttk.Spinbox(self.params_some, from_=0, to=0.1, increment=0.000001, format='%.6f', textvariable=self.lr_var)
        self.workers_label = tk.Label(self.params_some, text=self.setting.language.train_works, anchor=tk.W)
        self.workers_spinbox = ttk.Spinbox(self.params_some, from_=0, to=8, textvariable=self.workers_var)

        self.work_dir_label.grid(row=0, column=0, sticky=tk.NSEW, ipadx=5)
        self.work_dir_entry.grid(row=0, column=1, sticky=tk.NSEW, pady=1)
        self.work_dir_button.grid(row=0, column=2, sticky=tk.NSEW, pady=1)
        self.network_label.grid(row=1, column=0, sticky=tk.NSEW)
        self.network_combobox.grid(row=1, column=1, sticky=tk.NSEW, pady=1)
        self.loss_label.grid(row=2, column=0, sticky=tk.NSEW)
        self.loss_combobox.grid(row=2, column=1, sticky=tk.NSEW, pady=1)
        self.network_weights_label.grid(row=3, column=0, sticky=tk.NSEW)
        self.network_weights_entry.grid(row=3, column=1, sticky=tk.NSEW, pady=1)
        self.network_weights_button.grid(row=3, column=2, sticky=tk.NSEW, pady=1)
        self.network_epochs_label.grid(row=4, column=0, sticky=tk.NSEW)
        self.network_epochs_spinbox.grid(row=4, column=1, sticky=tk.NSEW, pady=1)
        self.network_height_label.grid(row=5, column=0, sticky=tk.NSEW)
        self.network_height_spinbox.grid(row=5, column=1, sticky=tk.NSEW, pady=1)
        self.network_width_label.grid(row=6, column=0, sticky=tk.NSEW)
        self.network_width_spinbox.grid(row=6, column=1, sticky=tk.NSEW, pady=1)
        self.network_batchsize_label.grid(row=7, column=0, sticky=tk.NSEW)
        self.network_batchsize_spinbox.grid(row=7, column=1, sticky=tk.NSEW, pady=1)
        self.network_lr_label.grid(row=8, column=0, sticky=tk.NSEW)
        self.network_lr_spinbox.grid(row=8, column=1, sticky=tk.NSEW, pady=1)
        self.workers_label.grid(row=9, column=0, sticky=tk.NSEW)
        self.workers_spinbox.grid(row=9, column=1, sticky=tk.NSEW, pady=1)

        self.work_dir_button.config(command=lambda data_var=self.work_dir_var : self.set_data(data_var))
        self.network_weights_button.config(command=lambda data_var=self.weights_dir_var : self.set_data(data_var))


        return self.params_some


    def make_params_checkbuttons(self, master):
        self.params_checkbuttons = ttk.Frame(master)

        self.transfer_var = tk.IntVar(value=0)
        self.train_all_var = tk.IntVar(value=1)

        self.transfer = ttk.Checkbutton(self.params_checkbuttons, variable=self.transfer_var, text=self.setting.language.train_transfer)
        self.train_all = ttk.Checkbutton(self.params_checkbuttons, variable=self.train_all_var, text=self.setting.language.train_network_all)

        self.transfer.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.train_all.pack(side=tk.LEFT, fill=tk.X, expand=True)

        return self.params_checkbuttons

    def make_buttons(self, master):
        self.buttons = ttk.Frame(master)

        self.start_button = ttk.Button(self.buttons, text=self.setting.language.train_start_button, image=self.start_image, command=self.start_train)
        self.stop_button = ttk.Button(self.buttons, text=self.setting.language.train_stop_button, image=self.stop_image, command=self.stop_train)
        self.load_button = ttk.Button(self.buttons, text=self.setting.language.train_load_button, image=self.load_image)

        self.start_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.stop_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.load_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


        return self.buttons

    def make_label_info(self, master):
        self.label_info = ttk.Frame(master)

        self.label_info_input = self.make_label_info_input(self.label_info)
        self.label_info_window = self.make_label_info_window(self.label_info)

        self.label_info_input.pack(side=tk.TOP, fill=tk.X)
        self.label_info_window.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        return self.label_info


    def make_label_info_input(self, master):
        self.label_info_input = ttk.Frame(master)
        self.label_info_input.rowconfigure((0, 1, 2), weight=1)
        self.label_info_input.columnconfigure((0, 1, 2), weight=1)

        self.data_var = tk.StringVar()
        self.train_ratio_var = tk.DoubleVar(value=0.9)
        self.valid_ratio_var = tk.DoubleVar(value=0.1)

        self.data_label = tk.Label(self.label_info_input, text=self.setting.language.data_label)
        self.data_entry = ttk.Entry(self.label_info_input, textvariable=self.data_var)
        self.data_button = ttk.Button(self.label_info_input, text=self.setting.language.data_entry)
        self.train_ratio_label = tk.Label(self.label_info_input, text=self.setting.language.train_ratio)
        self.train_ratio_spinbox = ttk.Spinbox(self.label_info_input, from_=0, to=1, textvariable=self.train_ratio_var, format='%.1f',increment=0.1)
        self.valid_ratio_label = tk.Label(self.label_info_input, text=self.setting.language.valid_ratio)
        self.valid_ratio_spinbox = ttk.Spinbox(self.label_info_input, from_=0, to=1, textvariable=self.valid_ratio_var, format='%.1f',increment=0.1)
        self.register_data_button = ttk.Button(self.label_info_input, text=self.setting.language.train_register_button)


        self.data_label.grid(row=0, column=0, sticky=tk.EW)
        self.data_entry.grid(row=0, column=1, sticky=tk.EW)
        self.data_button.grid(row=0, column=2, sticky=tk.EW)
        self.train_ratio_label.grid(row=1, column=0, sticky=tk.EW)
        self.train_ratio_spinbox.grid(row=1, column=1, sticky=tk.EW)
        self.valid_ratio_label.grid(row=2, column=0, sticky=tk.EW, pady=1)
        self.valid_ratio_spinbox.grid(row=2, column=1, sticky=tk.EW, pady=1)
        self.register_data_button.grid(row=1, column=2, rowspan=2, sticky=tk.NSEW, pady=1)

        self.data_button.config(command=lambda data_var=self.data_var : self.set_data(data_var))
        self.register_data_button.config(command=self.register_data)

        return self.label_info_input



    def make_label_info_window(self, master):
        self.label_info_window = ttk.Frame(master)

        self.treeview = ttk.Treeview(self.label_info_window, columns=(1, 2, 3), show='headings')
        self.scrollbar = ttk.Scrollbar(self.label_info_window)

        self.scrollbar.config(command=self.treeview.yview)                    
        self.treeview.config(yscrollcommand=self.scrollbar.set)  

        self.treeview.column(1, width=80, anchor=tk.CENTER)
        self.treeview.column(2, width=80, anchor=tk.CENTER)
        self.treeview.column(3, width=80, anchor=tk.CENTER)

        self.treeview.heading(1, text=self.setting.language.train_treeview_class)
        self.treeview.heading(2, text=self.setting.language.train_treeview_train)
        self.treeview.heading(3, text=self.setting.language.train_treeview_valid)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.treeview.yview)                    
        self.treeview.config(yscrollcommand=self.scrollbar.set)  

        return self.label_info_window

    def check_event(self):
        for i in range(100):                                # pass to set speed
            try:                                                
                callback, args = self.thread_queue.get(block=False)  # run <= N callbacks
            except queue.Empty:
                break                                            # anything ready?
            else:
                callback(*args)                                  # run callback here

        self.after(100, self.check_event)    

    def check_connect(self):
        try:
            if self.loss_conn is None:
                self.loss_conn, addr = self.sock.accept()
                self.loss_conn.setblocking(False)   
            else:
                self.log_conn, addr = self.sock.accept()
                self.log_conn.setblocking(False)           
                self.train_log = self.log_conn.makefile('r')
        except:
            pass

        if (not self.loss_conn is None) and (not self.log_conn is None):
            self.check_log()
            self.check_loss()
            return

        self.after(100, self.check_connect)

    def check_log(self):
        if not self.train_log is None:
            try:
                log = self.train_log.read()
                self.thread_queue.put((self.insert_text, (log,)))
            except:
                pass
        else:
            return

        self.after(100, self.check_log)

    def check_loss(self):
        if not self.loss_conn is None:
            try:
                bytes = self.loss_conn.recv(4092)
                loss = pickle.loads(bytes)
                self.losses.append(loss['loss'])
                self.val_loss.append(loss['val_loss'])
                self.show_loss()
            except:
                pass
        else:
            return

        self.after(100, self.check_loss)

    def show_loss(self):
        img_buf = io.BytesIO()

        iters = range(len(self.losses))
        plt.figure()
        plt.plot(iters, self.losses, 'red', linewidth = 2, label='train loss')
        plt.plot(iters, self.val_loss, 'coral', linewidth = 2, label='val loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('A Loss Curve')
        plt.legend(loc="upper right")

        plt.savefig(img_buf, format='png')

        self.window_image = Image.open(img_buf)
        #img_buf.close()
        self.resize_window()

    def add_augmentation_item(self):
        item = self.augmentation_combobox_var.get()
        if item:
            if not item in self.augmentation_list:
                augmentation_item_label = tk.Label(self.augmentation_choose_frame, anchor=tk.W, text=item)
                augmentation_item_entry = ttk.Entry(self.augmentation_choose_frame)
                augmentation_item_delete_button = ttk.Button(self.augmentation_choose_frame, image=self.augmentation_delete_image)

                augmentation_item_label.grid(row=len(self.augmentation_list), column=0, sticky=tk.NSEW, ipadx=5)
                augmentation_item_entry.grid(row=len(self.augmentation_list), column=1, sticky=tk.NSEW, pady=1)
                augmentation_item_delete_button.grid(row=len(self.augmentation_list), column=2, sticky=tk.NSEW)

                augmentation_item_delete_button.config(command=lambda index=len(self.augmentation_list), label=augmentation_item_label, entry=augmentation_item_entry,
                                                        button=augmentation_item_delete_button : self.remove_augmentation_item(index, label, entry, button))

                self.augmentation_list.append(item)
                self.augmentation_items.append((augmentation_item_label, augmentation_item_entry, augmentation_item_delete_button))

                self.augmentation_combobox_var.set('')
            else:
                self.insert_text(self.setting.language.train_error_repeat_add+'\n')

    def stop_train(self):
        self.loss_conn.send(b'stop')
        self.loss_conn.close()
        self.log_conn.close()
        self.loss_conn = None
        self.log_conn = None
        self.train_log = None
        self.losses=[]
        self.val_loss=[]
        self.check_connect()


    def start_train(self):
        def call_train():
            os.system('start D:/Program/Anaconda3/envs/tf2/python.exe {} --config {}'.format(r'classification\train.py', os.path.join(project_dir, 'train_config.yaml')))
        
        config = {}

        project_dir = self.work_dir_var.get()
        train_data = os.path.join(project_dir, 'train.txt')
        valid_data = os.path.join(project_dir, 'valid.txt')
        class_info = os.path.join(project_dir, 'class.txt')

        shutil.copy(os.path.join(os.path.dirname(__file__), 'tmp', 'train.txt'), train_data)
        shutil.copy(os.path.join(os.path.dirname(__file__), 'tmp', 'valid.txt'), valid_data)
        shutil.copy(os.path.join(os.path.dirname(__file__), 'tmp', 'class.txt'), class_info)

        config['train_data'] = train_data
        config['valid_data'] = valid_data
        config['class_info'] = class_info
        config['project_dir'] = project_dir

        config['network'] = self.network_var.get()
        config['weights'] = self.weights_dir_var.get()
        config['loss'] = self.loss_var.get()
        config['transfer'] = self.transfer_var.get()
        config['train_all'] = self.train_all_var.get()
        config['epochs'] = self.epochs_var.get()
        config['height'] = self.height_var.get()
        config['width'] = self.width_var.get()
        config['lr'] = self.lr_var.get()
        config['batch_size'] = self.batchsize_var.get()
        config['workers'] = self.workers_var.get()
        config['port'] = self.port
        aug_params = self.get_aug_params()
        config.update(aug_params)

        with open(os.path.join(project_dir, 'train_config.yaml'), encoding='utf8', mode='w') as fp:
            setting = yaml.dump(config)
            fp.write(setting)

        self.insert_text('starting.')
        thread = Thread(target=call_train)
        thread.start()

    def remove_augmentation_item(self, index, label, entry, button):
        label.destroy()
        entry.destroy()
        button.destroy()

        self.augmentation_list.pop(index)
        self.augmentation_items.pop(index)

    def reset_augmentation(self):
        for label, entry, button in self.augmentation_items:
            label.destroy()
            entry.destroy()
            button.destroy()

        self.augmentation_items = []
        self.augmentation_list = []

        self.window_image = None
        self.resize_window()

    def resize_window(self):
        win_width = self.window.winfo_width()
        win_height = self.window.winfo_height()
        if self.window_image:
            ratio = min(win_width/self.window_image.width, win_height/self.window_image.height)
            image = self.window_image.resize((int(ratio * self.window_image.width), int(ratio * self.window_image.height)), Image.LINEAR)
            self.window_image_resize = ImageTk.PhotoImage(image)
            self.window.config(image=self.window_image_resize)
        else:
            self.window.config(image='')

    def get_aug_params(self):
        kwargs = {}
        for index, item in enumerate(self.augmentation_list):
            if item == self.setting.language.train_aug_scale:
                kwargs['scale'] = [float(item) for item in self.augmentation_items[index][1].get().split()]
            if item == self.setting.language.train_aug_translate_x:
                kwargs['translate_percent_x'] = [float(item) for item in self.augmentation_items[index][1].get().split()]
            if item == self.setting.language.train_aug_translate_y:
                kwargs['translate_percent_y'] = [float(item) for item in self.augmentation_items[index][1].get().split()]
            if item == self.setting.language.train_aug_rotate:
                kwargs['rotate'] = [float(item) for item in self.augmentation_items[index][1].get().split()]
            if item == self.setting.language.train_aug_shear:
                kwargs['shear'] = [float(item) for item in self.augmentation_items[index][1].get().split()]
            if item == self.setting.language.train_aug_flip_lr:
                kwargs['flip_lr'] = float(self.augmentation_items[index][1].get())
            if item == self.setting.language.train_aug_flip_ud:
                kwargs['flip_ud'] = float(self.augmentation_items[index][1].get())
            if item == self.setting.language.train_aug_crop:
                kwargs['crop'] = [float(item) for item in self.augmentation_items[index][1].get().split()]
            if item == self.setting.language.train_aug_multiply:
                kwargs['multiply'] = [float(item) for item in self.augmentation_items[index][1].get().split()]
            if item == self.setting.language.train_aug_gaussian_noise:
                kwargs['gaussian_noise'] = [float(item) for item in self.augmentation_items[index][1].get().split()]
            if item == self.setting.language.train_aug_gaussian_blur:
                kwargs['gaussian_blur'] = [float(item) for item in self.augmentation_items[index][1].get().split()]
            if item == self.setting.language.train_aug_linear_contrast:
                kwargs['linear_contrast'] = [float(item) for item in self.augmentation_items[index][1].get().split()]

        return kwargs


    def preview_augmentation(self):
        aug_params = self.get_aug_params()
        self.augmentation_transformer = Transformer(**aug_params)

        dir_path = self.data_var.get()
        if dir_path:
            try:
                random_class = random.choice(os.listdir(dir_path))
                image_name = random.choice(os.listdir(os.path.join(dir_path, random_class)))
                image = cv2.imdecode(np.fromfile(os.path.join(dir_path, random_class, image_name), np.uint8), 1)
                image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
                image = self.augmentation_transformer(image)
                self.window_image = Image.fromarray(image)
                self.resize_window()
            except:
                self.insert_text(self.setting.language.train_error_check_dir+'\n')
        else:
            self.insert_text(self.setting.language.train_error_no_data+'\n')

    def set_data(self, data_var):
        dir_path = askdirectory()
        if dir_path:
            data_var.set(dir_path)

    def insert_text(self, msg):
        fully_scrolled_down = self.text.yview()[1] == 1.0
        self.text.insert(tk.END, msg)
        if fully_scrolled_down:
            self.text.see(tk.END)

    def insert_treeview(self, item, values):
        self.treeview.insert('', tk.END, item, values=values)

    def register_data(self):
        def register_data_thread(data_dir, train_ratio, valid_ratio):
            train_txt = os.path.join(os.path.dirname(__file__), 'tmp', 'train.txt')
            valid_txt = os.path.join(os.path.dirname(__file__), 'tmp', 'valid.txt')
            class_txt = os.path.join(os.path.dirname(__file__), 'tmp', 'class.txt')
            classes = os.listdir(data_dir)

            with open(class_txt, 'w', encoding='utf8') as fp:
                for item in classes:
                    fp.write(item+'\n')

            with open(train_txt, 'w', encoding='utf8') as fp1, open(valid_txt, 'w', encoding='utf8') as fp2:
                for index, item in enumerate(classes):
                    images = [item for item in os.listdir(os.path.join(data_dir, item)) if is_image(item)]
                    np.random.seed(1)
                    np.random.shuffle(images)
                    image_num = len(images)

                    train_num = int(train_ratio * image_num)
                    valid_num = int((train_ratio+valid_ratio)*image_num) - train_num

                    train_images = images[:train_num]
                    valid_images = images[train_num:train_num+valid_num]
                    for image in train_images:
                        fp1.write(os.path.join(data_dir, item, image)+'\t'+item+'\n')
                    for image in valid_images:
                        fp2.write(os.path.join(data_dir, item, image)+'\t'+item+'\n')

                    self.thread_queue.put((self.insert_treeview, (item, (item, train_num, valid_num))))
                    self.thread_queue.put((self.insert_text, (self.setting.language.train_register_button+':{}/{}\n'.format(index+1,len(classes)),)))


            self.thread_queue.put((self.insert_text, (self.setting.language.train_register_finish+'\n',)))


        data_dir = self.data_var.get()
        train_ratio = self.train_ratio_var.get()
        valid_ratio = self.valid_ratio_var.get()

        if os.path.isdir(data_dir) and os.path.exists(data_dir):
            for i in self.treeview.get_children():
                self.treeview.delete(i) 

            thread = Thread(target=register_data_thread, args=(data_dir, train_ratio, valid_ratio))
            thread.start()
        else:
            self.insert_text(self.setting.language.train_error_check_dir+'\n')

        

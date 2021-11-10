from logging import disable
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter.scrolledtext import ScrolledText
import pickle
import yaml
import subprocess
import os
import matplotlib.pyplot as plt
import queue
from threading import Thread
from socket import *
from PIL import ImageTk, Image
import io
import numpy as np

from utils import resource_path, is_image


class EvalFrame(ttk.Frame):
    def __init__(self, master, language):
        ttk.Frame.__init__(self, master)
        self.language = language

        self.setting_path = resource_path('setting/eval_frame_setting.yaml')
        self.setting = yaml.load(open(self.setting_path, encoding='utf8'))

        self.image = None
        self.resize_image = None
        self.eval_image = None
        self.server_running = False
        self.stop_eval = False
        self.eval_running = False
        self.thread_queue = queue.Queue(maxsize=0)
        self.servering_port = 50008
        self.folder_icon = ImageTk.PhotoImage(Image.open(resource_path(self.setting['folder_icon'])))
        self.file_icon = ImageTk.PhotoImage(Image.open(resource_path(self.setting['file_icon'])))

        self.panedwindow = ttk.PanedWindow(self, orient=tk.HORIZONTAL)

        self.left_frame = self.make_notebook(self.panedwindow)
        self.right_frame = self.make_right_frame(self.panedwindow)

        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.panedwindow.add(self.left_frame)
        self.panedwindow.add(self.right_frame)
        self.panedwindow.pack(fill=tk.BOTH, expand=True)

        self.check_event()
        self.load_sashpos()

    def make_right_frame(self, master):
        self.right_frame = ttk.PanedWindow(master, orient=tk.VERTICAL)

        self.control_frame = self.make_control_frame(self.right_frame)
        self.text = ScrolledText(self.right_frame)

        self.text.pack(side=tk.BOTTOM, fill=tk.X)
        self.control_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.right_frame.add(self.control_frame)
        self.right_frame.add(self.text)

        return self.right_frame

    def make_control_frame(self, master):
        self.control_frame = ttk.Frame(master)

        self.tool_buttons = self.make_tool_buttons(self.control_frame)
        self.window = tk.Label(self.control_frame, height=25)

        self.tool_buttons.pack(side=tk.TOP)
        self.window.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.window.bind('<Configure>', lambda event : self.resize_window())

        return self.control_frame

    def make_notebook(self, master):
        self.notebook = ttk.Notebook(master)

        self.notebook_1 = self.make_notebook_1(self.notebook)
        self.output_treeview_frame = self.make_output_treeview_frame(self.notebook)

        self.notebook_1.pack(fill=tk.BOTH, expand=True)
        self.output_treeview_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook.add(self.notebook_1, text=self.setting[self.language]['notebook_heading'][0])
        self.notebook.add(self.output_treeview_frame, text=self.setting[self.language]['notebook_heading'][1])

        return self.notebook

    def make_notebook_1(self, master):
        self.notebook_1 = ttk.Frame(master)

        self.input_frame = self.make_input_frame(self.notebook_1)
        self.input_treeview_frame = self.make_input_treeview_frame(self.notebook_1)

        self.input_frame.pack(side=tk.TOP, fill=tk.X)
        self.input_treeview_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        return self.notebook_1

    def make_input_treeview_frame(self, master):
        self.input_treeview_frame = ttk.Frame(master)

        self.input_treeview = ttk.Treeview(self.input_treeview_frame, show="tree")
        self.input_scrollbar = ttk.Scrollbar(self.input_treeview_frame)

        self.input_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.input_scrollbar.config(command=self.input_treeview.yview)                    
        self.input_treeview.config(yscrollcommand=self.input_scrollbar.set)  

        self.input_treeview.bind('<<TreeviewSelect>>', lambda event : self.select_input_item())

        return self.input_treeview_frame

    def make_output_treeview_frame(self, master):
        self.output_treeview_frame = ttk.Frame(master)

        self.output_treeview = ttk.Treeview(self.output_treeview_frame, show="tree")
        self.output_scrollbar = ttk.Scrollbar(self.output_treeview_frame)

        self.output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.output_scrollbar.config(command=self.output_treeview.yview)                    
        self.output_treeview.config(yscrollcommand=self.output_scrollbar.set)  

        self.output_treeview.bind('<<TreeviewSelect>>', lambda event : self.select_output_item())
        self.output_treeview.bind('<Double-Button-1>', lambda event : self.show_eval_image())

        return self.output_treeview_frame

    def make_input_frame(self, master):
        self.input_frame = ttk.Frame(master)
        self.input_frame.columnconfigure((1, ), weight=1)

        self.input_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.class_var = tk.StringVar()

        self.input_label = tk.Label(self.input_frame, text=self.setting[self.language]['input_label'])
        self.input_entry = ttk.Entry(self.input_frame, textvariable=self.input_var)
        self.input_button = ttk.Button(self.input_frame, image=self.folder_icon, command=self.set_input_dir)
        self.model_label = tk.Label(self.input_frame, text=self.setting[self.language]['model_label'])
        self.model_entry = ttk.Entry(self.input_frame, textvariable=self.model_var)
        self.model_button = ttk.Button(self.input_frame, image=self.folder_icon, command=lambda var=self.model_var : self.set_dir(var))
        self.class_label = tk.Label(self.input_frame, text=self.setting[self.language]['class_label'])
        self.class_entry = ttk.Entry(self.input_frame, textvariable=self.class_var)
        self.class_button = ttk.Button(self.input_frame, image=self.file_icon, command=lambda var=self.class_var : self.set_file(var))

        self.model_label.grid(row=0, column=0)
        self.model_entry.grid(row=0, column=1, sticky=tk.NSEW, pady=1)
        self.model_button.grid(row=0, column=2)
        self.class_label.grid(row=1, column=0)
        self.class_entry.grid(row=1, column=1, sticky=tk.NSEW, pady=1)
        self.class_button.grid(row=1, column=2)
        self.input_label.grid(row=2, column=0)
        self.input_entry.grid(row=2, column=1, sticky=tk.NSEW, pady=1)
        self.input_button.grid(row=2, column=2)

        return self.input_frame


    def make_tool_buttons(self, master):
        self.tool_buttons = ttk.Frame(master)

        self.init_button = ttk.Button(self.tool_buttons, text=self.setting[self.language]['init_button'], command=self.init_serve)
        self.eval_button = ttk.Button(self.tool_buttons, text=self.setting[self.language]['eval_button'], command=self.eval)
        self.stop_button = ttk.Button(self.tool_buttons, text=self.setting[self.language]['stop_button'], command=self.stop)

        self.init_button.pack(side=tk.LEFT)
        self.eval_button.pack(side=tk.LEFT)
        self.stop_button.pack(side=tk.LEFT)

        return self.tool_buttons

    def insert_text(self, msg):
        fully_scrolled_down = self.text.yview()[1] == 1.0
        self.text.insert(tk.END, msg)
        if fully_scrolled_down:
            self.text.see(tk.END)

    def load_sashpos(self):
        if self.setting['lr_sashpos'] != self.panedwindow.sashpos(0) or self.setting['tb_sashpos'] != self.right_frame.sashpos(0):
            self.panedwindow.sashpos(0, self.setting['lr_sashpos'])
            self.right_frame.sashpos(0, self.setting['tb_sashpos'])
            self.after(100, self.load_sashpos)

    def check_event(self):
        for i in range(100):                                # pass to set speed
            try:                                                
                callback, args = self.thread_queue.get(block=False)  # run <= N callbacks
            except queue.Empty:
                break                                            # anything ready?
            else:
                callback(*args)                                  # run callback here

        self.after(100, self.check_event)  

    def select_item(self, image_path):
        if os.path.isfile(image_path):
            self.image = Image.open(image_path)
            self.resize_window()
            if self.server_running:
                result = self.predict([image_path])
                self.insert_text('{}:{:.3f}\n'.format(result[0][0], result[0][1]))

    def select_input_item(self):
        image_path = self.input_treeview.focus()
        self.select_item(image_path)

    def select_output_item(self):
        image_path = self.output_treeview.focus()
        self.select_item(image_path)

    def resize_window(self):
        win_width = self.window.winfo_width()
        win_height = self.window.winfo_height()
        if self.image:
            ratio = min(win_width/self.image.width, win_height/self.image.height)
            image = self.image.resize((int(ratio * self.image.width), int(ratio * self.image.height)), Image.LINEAR)
            self.resize_image = ImageTk.PhotoImage(image)
            self.window.config(image=self.resize_image)
        else:
            self.window.config(image='')

    def predict(self, batch_image):
        bytes = pickle.dumps(batch_image)
        self.sock.send(bytes)
        bytes = self.sock.recv(4096)
        obj = pickle.loads(bytes)
        return obj

    def init_serve(self):
        def call_serve(model_path, class_info, port):
            subprocess.Popen('D:/Program/Anaconda3/envs/tf2/python.exe classification/evaluation.py --model_path {} --class_info {} --port {}'.format(model_path, class_info, port))
            
            self.sock = socket(AF_INET, SOCK_STREAM)
            while True:
                try:
                    self.sock.connect(('localhost', self.servering_port))
                    self.thread_queue.put((self.insert_text, (self.setting[self.language]['info_server_running']+'\n', )))
                    self.server_running = True
                except Exception as e:
                    print(e)
                else:
                    break

        model_path = self.model_var.get()
        class_info = self.class_var.get()
        if model_path and class_info:
            self.init_button.config(state=tk.DISABLED)
            self.insert_text(self.setting[self.language]['info_wait_server']+'\n')

            thread = Thread(target=call_serve, args=(model_path, class_info, self.servering_port))
            thread.start()
        else:
            self.insert_text(self.setting[self.language]['info_no_model']+'\n')

    def output_treeview_insert(self, parent, index, iid, text):
        self.output_treeview.insert(parent, index, iid, text=text)


    def stop(self):
        if self.eval_running:
            self.stop_eval = True
        else:
            self.insert_text(self.setting[self.language]['info_no_eval']+'\n')

    def load_class_list(self, class_info):
        lines = open(class_info, encoding='utf8').readlines()
        return [line.strip() for line in lines]

    def show_eval_image(self):
        self.image = self.eval_image
        self.resize_window()

    def eval(self):
        def plot_table(total_dir, class_list, array):
            img_buf = io.BytesIO()
            plt.figure(figsize=(20,8))
            tab = plt.table(cellText=array, 
                        colLabels=class_list, 
                        rowLabels=total_dir,
                        loc='center', 
                        cellLoc='center',
                        rowLoc='center')
            tab.scale(1,2) 
            plt.axis('off')
            plt.savefig(img_buf, format='png')
            self.eval_image = Image.open(img_buf).copy()
            
            self.image = self.eval_image
            img_buf.close()
            self.resize_window()

        def thread_eval(input_dir, class_info):
            self.eval_running = True
            total_num = len(os.listdir(input_dir))
            total_dir = os.listdir(input_dir)
            class_list = self.load_class_list(class_info)
            result_array = np.zeros((len(total_dir), len(class_list)), dtype=np.int32)

            for progress_index, dir_item in enumerate(total_dir):
                dir_path = os.path.join(input_dir, dir_item)
                self.thread_queue.put((self.output_treeview_insert, ('', tk.END, dir_path, dir_item)))
                image_names = [item for item in os.listdir(dir_path) if is_image(item)]
                image_paths = [os.path.join(dir_path, item) for item in image_names]

                result = []
                tmp_image_paths = image_paths[:]
                while tmp_image_paths:       
                    if self.stop_eval:
                        self.eval_running = False
                        self.stop_eval = False
                        return
                    batch_image_paths, tmp_image_paths = tmp_image_paths[:8], tmp_image_paths[8:]   
                    batch_result = self.predict(batch_image_paths)
                    result.extend(batch_result)

                    for item in batch_result:
                        result_array[progress_index][class_list.index(item[0])] += 1

                out_dir = sorted(set([item[0] for item in result]))
                for item in out_dir:
                    self.thread_queue.put((self.output_treeview_insert, (dir_path, tk.END, dir_path+'##'+item, item)))
                for index, item in enumerate(result):
                    self.thread_queue.put((self.output_treeview_insert, (dir_path+'##'+item[0], tk.END, image_paths[index], image_names[index])))

                self.thread_queue.put((self.insert_text, ('{}:{}/{}\n'.format(self.setting[self.language]['info_progress'], progress_index+1, total_num), )))
            self.thread_queue.put((self.insert_text, (self.setting[self.language]['info_eval_finish']+'\n', )))

            plot_table(total_dir, class_list, result_array)

        if self.server_running:
            self.eval_image = None
            input_dir = self.input_var.get()
            class_info = self.class_var.get()
            if input_dir:
                for i in self.output_treeview.get_children():
                    self.output_treeview.delete(i)

                thread = Thread(target=thread_eval, args=(input_dir, class_info))
                thread.start()
            else:
                self.insert_text(self.setting[self.language]['info_no_input']+'\n')
        else:
            self.insert_text(self.setting[self.language]['info_no_server']+'\n')

        

    def set_dir(self, var):
        dir_path = askdirectory()
        if dir_path:
            var.set(dir_path)

    def set_file(self, var):
        file_path = askopenfilename()
        if file_path:
            var.set(file_path)

    def set_input_dir(self):
        input_dir = askdirectory()
        if input_dir:
            for i in self.input_treeview.get_children():
                self.input_treeview.delete(i)
            self.input_var.set(input_dir)
            for dir_item in os.listdir(input_dir):
                dir_path = os.path.join(input_dir, dir_item)
                self.input_treeview.insert('', tk.END, dir_path, text=dir_item)
                for image_item in os.listdir(dir_path):
                    if is_image(image_item):
                        image_path = os.path.join(dir_path, image_item)
                        self.input_treeview.insert(dir_path, tk.END, image_path, text=image_item)

    def save_setting(self):
        lr_sashpos = self.panedwindow.sashpos(0)
        tb_sashpos = self.right_frame.sashpos(0)
        self.setting.update({'lr_sashpos': lr_sashpos})
        self.setting.update({'tb_sashpos': tb_sashpos})
        yaml.dump(self.setting, open(self.setting_path, 'w', encoding='utf8'))


if __name__=='__main__':
    a = tk.Tk()
    gui = EvalFrame(a, None)
    gui.pack(fill=tk.BOTH, expand=True)
    gui.mainloop()

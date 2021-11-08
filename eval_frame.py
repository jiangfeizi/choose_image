import pickle
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from PIL import ImageTk, Image
from utils import is_image, resource_path, initListenerSocket
import queue
from tkinter.filedialog import askdirectory, askopenfilename
import os
from threading import Thread
from socket import *


class EvalFrame(ttk.Frame):
    def __init__(self, master, setting):
        ttk.Frame.__init__(self, master)
        self.setting = setting

        self.setting = setting   
        self.thread_queue = queue.Queue(maxsize=0)

        self.servering_port = 50008

        self.image = None

        self.dir_image = ImageTk.PhotoImage(Image.open(resource_path('res/Folder-Open-icon_24.png')))
        self.file_image = ImageTk.PhotoImage(Image.open(resource_path('res/File-icon.png')))

        self.panedwindow = ttk.PanedWindow(self, orient=tk.HORIZONTAL)

        self.left_frame = self.make_notebook(self.panedwindow)
        self.right_frame = self.make_right_frame(self.panedwindow)

        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.panedwindow.add(self.left_frame)
        self.panedwindow.add(self.right_frame)
        self.panedwindow.pack(fill=tk.BOTH, expand=True)

        self.check_event()

    def insert_text(self, msg):
        fully_scrolled_down = self.text.yview()[1] == 1.0
        self.text.insert(tk.END, msg)
        if fully_scrolled_down:
            self.text.see(tk.END)

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

        self.notebook.add(self.notebook_1, text='输入')
        self.notebook.add(self.output_treeview_frame, text='结果')

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

        return self.output_treeview_frame

    def make_input_frame(self, master):
        self.input_frame = ttk.Frame(master)
        self.input_frame.columnconfigure((1, ), weight=1)

        self.input_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.class_var = tk.StringVar()

        self.input_label = tk.Label(self.input_frame, text='输入路径')
        self.input_entry = ttk.Entry(self.input_frame, textvariable=self.input_var)
        self.input_button = ttk.Button(self.input_frame, image=self.dir_image, command=self.set_input_dir)
        self.model_label = tk.Label(self.input_frame, text='模型路径')
        self.model_entry = ttk.Entry(self.input_frame, textvariable=self.model_var)
        self.model_button = ttk.Button(self.input_frame, image=self.dir_image, command=lambda var=self.model_var : self.set_dir(var))
        self.class_label = tk.Label(self.input_frame, text='类别信息')
        self.class_entry = ttk.Entry(self.input_frame, textvariable=self.class_var)
        self.class_button = ttk.Button(self.input_frame, image=self.file_image, command=lambda var=self.class_var : self.set_file(var))

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

        self.init_button = ttk.Button(self.tool_buttons, text='开启', command=self.init_serve)
        self.eval_button = ttk.Button(self.tool_buttons, text='评估', command=self.eval)
        self.stop_button = ttk.Button(self.tool_buttons, text='停止')

        self.init_button.pack(side=tk.LEFT)
        self.eval_button.pack(side=tk.LEFT)
        self.stop_button.pack(side=tk.LEFT)

        return self.tool_buttons

    def select_input_item(self):
        item = self.input_treeview.focus()
        if is_image(item):
            self.image = Image.open(item)
            self.resize_window()
            result = self.predict([item])
            self.insert_text(result[0])

    def select_output_item(self):
        item = self.output_treeview.focus()
        if is_image(item):
            self.image = Image.open(item)
            self.resize_window()
            result = self.predict([item])
            self.insert_text(result[0])

    def resize_window(self):
        win_width = self.window.winfo_width()
        win_height = self.window.winfo_height()
        if self.image:
            ratio = min(win_width/self.image.width, win_height/self.image.height)
            image = self.image.resize((int(ratio * self.image.width), int(ratio * self.image.height)), Image.LINEAR)
            self.image_resize = ImageTk.PhotoImage(image)
            self.window.config(image=self.image_resize)
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
            os.system('start D:/Program/Anaconda3/envs/tf2/python.exe classification/evaluation.py --model_path {} --class_info {} --port {}'.format(model_path, class_info, port))
            
            self.sock = socket(AF_INET, SOCK_STREAM)
            while True:
                try:
                    self.sock.connect(('localhost', self.servering_port))
                    self.thread_queue.put((self.insert_text, ('server is running.\n', )))
                except Exception as e:
                    print(e)
                else:
                    break

        self.insert_text('please wait.\n')
        model_path = self.model_var.get()
        class_info = self.class_var.get()

        thread = Thread(target=call_serve, args=(model_path, class_info, self.servering_port))
        thread.start()

    def eval(self):
        dir_path = self.input_var.get()
        for dir_item in os.listdir(dir_path):
            id_dir = os.path.join(dir_path, dir_item)
            self.output_treeview.insert('', tk.END, id_dir, text=dir_item)
            image_names = [item for item in os.listdir(id_dir) if is_image(item)]
            images = [os.path.join(id_dir, item) for item in image_names]
            tmp_images = images[:]
            result = []
            while tmp_images:       
                batch_image, tmp_images = tmp_images[:8], tmp_images[8:]   
                batch_result = self.predict(batch_image)
                result.extend(batch_result)
            out_dir = sorted(set(result))
            for i in out_dir:
                self.output_treeview.insert(id_dir, tk.END, id_dir+'##'+i, text=i)
            for index, i in enumerate(result):
                self.output_treeview.insert(id_dir+'##'+i, tk.END, images[index], text=image_names[index])




    def check_event(self):
        for i in range(100):                                # pass to set speed
            try:                                                
                callback, args = self.thread_queue.get(block=False)  # run <= N callbacks
            except queue.Empty:
                break                                            # anything ready?
            else:
                callback(*args)                                  # run callback here

        self.after(100, self.check_event)  

    def set_dir(self, var):
        dir_path = askdirectory()
        if dir_path:
            var.set(dir_path)

    def set_file(self, var):
        file_path = askopenfilename()
        if file_path:
            var.set(file_path)

    def set_input_dir(self):
        dir_path = askdirectory()
        if dir_path:
            self.input_var.set(dir_path)
            for dir_item in os.listdir(dir_path):
                id_dir = os.path.join(dir_path, dir_item)
                self.input_treeview.insert('', tk.END, id_dir, text=dir_item)
                for image_item in os.listdir(id_dir):
                    if is_image(image_item):
                        id_image = os.path.join(id_dir, image_item)
                        self.input_treeview.insert(id_dir, tk.END, id_image, text=image_item)


if __name__=='__main__':
    a = tk.Tk()
    gui = EvalFrame(a, None)
    gui.pack(fill=tk.BOTH, expand=True)
    gui.mainloop()

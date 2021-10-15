from tkinter import *
from tkinter.filedialog import askdirectory, askopenfilename
from PIL import Image, ImageTk
import numpy as np
import os
import shutil
from tkinter.messagebox import *
import pickle

class Setting(Toplevel):
    def __init__(self, parent, input_var, output_var, class_var, statu_var):
        Toplevel.__init__(self, parent)
        self.resizable(0, 0)
        self.input_var = input_var
        self.output_var = output_var
        self.class_var = class_var
        self.statu_var = statu_var

        self.make_table()

    def make_table(self):
        labels = ['输入路径', '输出路径', '类别']
        vars = [self.input_var, self.output_var, self.class_var]
        commands = [self.choose_path, self.choose_path, self.ok]
        buttons = ['路径选择', '路径选择', '   确定   ']
        for r in range(3):
            label = Label(self, text=labels[r])
            entry = Entry(self, textvariable=vars[r])
            input_button = Button(self, text=buttons[r], command=lambda r=r, entry=entry: commands[r](entry))

            label.grid(row=r, column=0)
            entry.grid(row=r, column=1)
            input_button.grid(row=r, column=2)

        self.grab_set()
        self.focus_set()
        self.wait_window()

    def choose_path(self, entry):
        dir_path = askdirectory()
        if dir_path:
            entry.delete(0, END)
            entry.insert(END, dir_path)

    def ok(self, *args):
        self.statu_var.set(1)
        self.destroy()


class Save(Toplevel):
    def __init__(self, parent, dir_var, file_var, statu_var):
        Toplevel.__init__(self, parent)
        self.resizable(0, 0)
        self.dir_var = dir_var
        self.file_var = file_var
        self.statu_var = statu_var

        self.make_table()

    def make_table(self):
        labels = ['输出路径', '文件名']
        vars = [self.dir_var, self.file_var]
        commands = [self.choose_path, self.ok]
        buttons = ['路径选择', '   确定   ']
        for r in range(2):
            label = Label(self, text=labels[r])
            entry = Entry(self, textvariable=vars[r])
            input_button = Button(self, text=buttons[r], command=lambda r=r, entry=entry: commands[r](entry))

            label.grid(row=r, column=0)
            entry.grid(row=r, column=1)
            input_button.grid(row=r, column=2)

        self.grab_set()
        self.focus_set()
        self.wait_window()

    def choose_path(self, entry):
        dir_path = askdirectory()
        if dir_path:
            entry.delete(0, END)
            entry.insert(END, dir_path)

    def ok(self, *args):
        self.statu_var.set(1)
        self.destroy()


class ButtonSet(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.buttons = []

    def add(self, item):
        button = Button(self, text=item)
        self.buttons.append(button)
        return button

    def reset(self):
        for button in self.buttons:
            button.destroy()
        self.buttons = []

class Core(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        
        self.left_frame = Frame(self)
        self.scrollbar = Scrollbar(self.left_frame)
        self.listbox = Listbox(self.left_frame, relief=SUNKEN)
        self.button_set = ButtonSet(self.left_frame)
        self.statusbar = Label(self.left_frame, anchor='w')

        self.scrollbar.config(command=self.listbox.yview)                    
        self.listbox.config(yscrollcommand=self.scrollbar.set)  

        self.statusbar.pack(side=BOTTOM, fill=X)
        self.scrollbar.pack(side=RIGHT, fill=Y)   
        self.button_set.pack(side=LEFT, fill=Y)          
        self.listbox.pack(side=LEFT, expand=YES, fill=BOTH)

        self.window = Label(self)

        self.left_frame.pack(side=LEFT, fill=BOTH)
        self.window.pack(side=RIGHT, expand=YES, fill=BOTH)
        self.width = None
        self.height = None

        self.init_image()
        self.show_window()

    def init_image(self):
        self.image_tmp = ImageTk.PhotoImage(Image.fromarray(np.ones((500,500), dtype=np.uint8) * 255))

    def set_image(self, image_name):
        if self.current == 'current':
            image_path = os.path.join(self.input_path, image_name)
        else:
            image_path = os.path.join(self.output_path, self.current, image_name)
        
        self.image_tmp = ImageTk.PhotoImage(Image.open(image_path))

    def init(self, input_path, output_path, class_list, images_dict):
        self.current = 'current'
        self.input_path = input_path
        self.output_path = output_path
        self.class_list = class_list
        self.images_dict = images_dict

        self.init_listbox(self.images_dict[self.current])

        self.button_set.reset()
        for idx, item in enumerate(self.class_list):
            button = self.button_set.add(self.vertical_str(item))
            button.pack(side=TOP)
            button.bind('<Button-1>', lambda event, item=item:self.toggle(item))
            self.listbox.bind('<Control-Key-{}>'.format(idx+1), lambda event, item=item:self.toggle(item))

        button = self.button_set.add(self.vertical_str('返回'))
        button.bind('<Button-1>', lambda event, item='current':self.toggle(item))
        button.pack(side=BOTTOM)
        self.listbox.bind('<Control-s>', lambda event, item='current':self.toggle(item))
        self.update()

        self.listbox.bind('<<ListboxSelect>>', lambda event:self.update())
        self.listbox.bind('<KeyPress>', lambda event: self.event(event))

    def set_size(self):
        self.width = self.window.winfo_width() - 4
        self.height = self.window.winfo_height() - 4
        self.update()

    def reset_size(self):
        self.width = None
        self.height = None
        self.update()

    def show_window(self):
        image = ImageTk.getimage(self.image_tmp)
        if self.width and self.height:
            image = image.resize((self.width, self.height), Image.ANTIALIAS)
        self.image_tmp = ImageTk.PhotoImage(image)
        self.window.config(image=self.image_tmp)

    def toggle(self, current):
        try:
            self.current = current
            self.init_listbox(self.images_dict[self.current])
            self.update()
        except:
            self.statusbar.config(text='error!!!')
            raise


    def vertical_str(self, str):
        return '\n'.join(list(str))

    def update(self):
        try:
            index = self.listbox.curselection()
            self.images_dict[self.current][1] = index
            if index:
                self.statusbar.config(text='进度：{}/{}'.format(index[0] + 1, len(self.images_dict[self.current][0])))
                image_name = self.listbox.get(index)
                self.set_image(image_name)
            else:
                self.statusbar.config(text='进度：')
                self.init_image()
            self.show_window()
        except:
            self.statusbar.config(text='error!!!')
            raise

    def init_listbox(self, value):
        self.listbox.delete(0, END)
        for item in value[0]:
            self.listbox.insert(END, item)

        if value[1]:
            self.set_focus(value[1])
        self.listbox.focus_set()

    def set_focus(self, index):
            self.listbox.select_set(index)
            self.listbox.activate(index)

    def event(self, event):
        try:
            retval = event.char
            index = self.listbox.curselection()
            if index:
                index = index[0]
                if retval == 'a':
                    if index-1>= 0:
                        self.listbox.select_clear(0, END)
                        self.set_focus(index-1)
                if retval == 's':
                    if self.current != 'current':
                        self.move_to(index, 'current')

                if retval == 'd':
                    if index+1< len(self.images_dict[self.current][0]):
                        self.listbox.select_clear(0, END)
                        self.set_focus(index+1)
                for idx, cl in enumerate(self.class_list):
                    if retval == str(idx+1):
                        if self.current != self.class_list[idx]:
                            self.move_to(index, cl)
                
                self.listbox.event_generate('<<ListboxSelect>>')
        except:
            self.statusbar.config(text='error!!!')
            raise

    def move_to(self, idx, cl):
        item = self.listbox.get(idx)
        if idx+1 == len(self.images_dict[self.current][0]):
            if idx == 0:
                self.images_dict[self.current][1] = tuple()
            else:
                self.images_dict[self.current][1] = (self.images_dict[self.current][1][0]-1,)
        self.images_dict[self.current][0].pop(idx)
        self.listbox.delete(idx)          
        if self.images_dict[self.current][1]:  
            self.set_focus(self.images_dict[self.current][1][0])  
        self.images_dict[cl][0].insert(0, item)
        if self.images_dict[cl][1]:
            self.images_dict[cl][1] = (self.images_dict[cl][1][0]+1,)
        else:
            self.images_dict[cl][1] = (0,)
        if self.current == 'current':
            ori_path = os.path.join(self.input_path, item)
        else:
            ori_path = os.path.join(self.output_path, self.current, item)

        if cl == 'current':
            dest_path = os.path.join(self.input_path, item)
        else:
            dest_path = os.path.join(self.output_path, cl, item)
        shutil.move(ori_path, dest_path)
        
        

class Gui(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title('images')
        self.iconbitmap('favicon.ico')

        menubar = Menu(self)
        self.core = Core(self)
        self.config(menu=menubar)

        file = Menu(menubar, tearoff=False)
        file.add_command(label='设置路径', command=self.init_from_setting)
        file.add_command(label='载入存档', command=self.init_from_file)
        file.add_command(label='保存档案', command=self.save)
        menubar.add_cascade(label='文件', menu=file)

        setting = Menu(menubar, tearoff=False)
        setting.add_command(label='适应窗口', command=self.core.set_size)
        setting.add_command(label='适应图片', command=self.core.reset_size)
        menubar.add_cascade(label='设置', menu=setting)

        menubar.add_command(label='帮助', command=self.help)

        self.core.pack(expand=YES, fill=BOTH)

        self.input_var = StringVar()
        self.output_var = StringVar()
        self.class_var = StringVar()

    def help(self):
         
        msg =   '''
                上一张 ：a
                下一张 ：d
                移动到输入文件夹 ：s
                移动到输出文件夹 ：数字键
                切换视图 ：Ctrl+数字键
                '''
                
        showinfo('help', msg)

    def init_from_file(self):
        try:
            file_path = askopenfilename()
            if file_path:
                with open(file_path,'rb') as fp:
                    obj = pickle.load(fp)

                self.input_path = obj['input_path']
                self.output_path = obj['output_path']
                self.classes_str = obj['classes_str']
                self.images_dict = obj['images_dict']

                self.input_var.set(self.input_path)
                self.output_var.set(self.output_path)
                self.class_var.set(self.classes_str)

                self.class_list = self.classes_str.split()

                self.core.init(self.input_path, self.output_path, self.class_list, self.images_dict)
        except:
            self.core.statusbar.config(text='error!!!')
            raise

    def init_from_setting(self):
        try:
            statu_var = IntVar(0)
            Setting(self, self.input_var, self.output_var, self.class_var, statu_var)

            if statu_var.get():
                self.input_path = self.input_var.get()
                self.output_path = self.output_var.get()
                self.classes_str = self.class_var.get()

                self.class_list = self.classes_str.split()

                for item in self.class_list:
                    os.mkdir(os.path.join(self.output_path, item))


                self.images_dict = {item : [[], tuple()] for item in self.class_list}
                image_names = os.listdir(self.input_path)
                self.images_dict.update({'current':[image_names, (0,) if image_names else tuple()]})

                self.core.init(self.input_path, self.output_path, self.class_list, self.images_dict)
        except:
            self.core.statusbar.config(text='error!!!')
            raise


    def save(self):
        try:
            self.dir_var = StringVar()
            self.file_var = StringVar()
            statu_var = IntVar(0)

            Save(self, self.dir_var, self.file_var, statu_var)
            if statu_var.get():
                obj = {
                        'input_path':self.input_path,
                        'output_path':self.output_path,
                        'classes_str':self.classes_str,
                        'images_dict':self.images_dict
                        }
                
                dir_path = self.dir_var.get()
                file_name = self.file_var.get()
                with open(os.path.join(dir_path, file_name),'wb') as fp:
                    pickle.dump(obj, fp)
        except:
            self.core.statusbar.config(text='error!!!')
            raise

if __name__ == '__main__':
    one = Gui()
    one.mainloop()

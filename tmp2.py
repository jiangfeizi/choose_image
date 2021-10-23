import tkinter as tk
from tkinter import ttk
 
window = tk.Tk()
# 设置窗口大小
winWidth = 600
winHeight = 400
# 获取屏幕分辨率
screenWidth = window.winfo_screenwidth()
screenHeight = window.winfo_screenheight()
 
x = int((screenWidth - winWidth) / 2)
y = int((screenHeight - winHeight) / 2)
 
# 设置主窗口标题
window.title("TreeView参数说明")
# 设置窗口初始位置在屏幕居中
window.geometry("%sx%s+%s+%s" % (winWidth, winHeight, x, y))
# 设置窗口图标
#window.iconbitmap("./image/icon.ico")
# 设置窗口宽高固定
window.resizable(0, 0)
 
# 定义列的名称
tree = ttk.Treeview(window, show = "tree")
 
myid=tree.insert("",0,"中国",text="中国China",values=("1"))  # ""表示父节点是根
myidx1=tree.insert(myid,0,"广东",text="中国广东",values=("2"))  # text表示显示出的文本，values是隐藏的值
myidx2=tree.insert(myid,1,"江苏",text="中国江苏",values=("3"))
myidy=tree.insert("",1,"美国",text="美国USA",values=("4"))   
myidy1=tree.insert(myidy,0,"加州",text="美国加州",values=("5"))
 
# 鼠标选中一行回调
def selectTree(event):
    for item in tree.selection():
        item_text = tree.item(item, "values")
        print(item_text)
     
# 选中行
tree.bind('<<TreeviewSelect>>', selectTree)
 
tree.pack(expand = True, fill = tk.BOTH)
 
window.mainloop()
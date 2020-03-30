#!/usr/bin/python3
# encoding: utf-8

"""
@author: chsh
@file:  customDialog.py
@time:  2020/3/19 14:59
@title:
@content:
"""
from tkinter import *
# 导入ttk
from tkinter import ttk
from tkinter import messagebox
from ChinaChess.settings import Settings
from ChinaChess.common import Commmon

# 自定义对话框类，继承Toplevel
class MyDialog(Toplevel):
    # 定义构造方法
    def __init__(self, parent, title=None, modal=True, img=None):
        self.setting = Settings()
        self.common = Commmon()
        self.img = img
        self.width = 360
        self.height = 450
        self.frame_x = 350
        self.frame_y = 100

        Toplevel.__init__(self, parent)
        self.transient(parent)
        # 设置标题
        if title: self.title(title)
        self.parent = parent
        self.result = None
        # 创建对话框的主体内容
        frame = Frame(self)
        # 调用init_widgets方法来初始化对话框界面
        self.initial_focus = self.init_widgets(frame)
        frame.pack()
        # 根据modal选项设置是否为模式对话框
        if modal: self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        # 为"WM_DELETE_WINDOW"协议使用self.cancel_click事件处理方法
        self.protocol("WM_DELETE_WINDOW", self.cancel_click)
        # 根据父窗口来设置对话框的位置
        self.geometry(f"{self.width}x{self.height}+{parent.winfo_rootx()+self.frame_x}+{parent.winfo_rooty()+self.frame_y}")
        # 固定窗口大小
        self.resizable(width=False, height=False)
        # 让对话框获取焦点
        self.initial_focus.focus_set()
        self.wait_window(self)

    # 通过该方法来创建自定义对话框的内容
    def init_widgets(self, master):
        # 创建画布，获得焦点
        cv = Canvas(master, bg=self.setting.bg_color, width=self.width, height=self.height)
        cv.pack(fill=BOTH, expand=YES)
        cv.focus_set()
        # 添加一个图片
        cv.create_image(78, 55, image=self.img)
        # 添加一行文字
        text_show_font = (self.setting.font_style, 25)
        text_show_text = self.setting.game_title + self.setting.version
        cv.create_text(216, 52, text=text_show_text, font=text_show_font)
        # 添加一个文本域，只读模式，显示版本更新信息
        text_area_font = ('华文新魏', 14)
        text_area = Text(cv, font=text_area_font, background=self.setting.bg_color)
        text_area.place(x=10, y=90, width=self.width-20, height=self.height-145)
        # 读取版本更新文件内容，加载到文本域中
        text_area_value = self.common.read_file(self.setting.version_file)
        text_area.insert(0.0, text_area_value)
        # 为文本域设置垂直滚动条
        # scroll = Scrollbar(text_area, command=text_area.yview)
        # scroll.pack(side=RIGHT, fill=Y)
        # # 文本域设置只读
        # text_area.configure(state='disabled', yscrollcommand=scroll.set)
        text_area.configure(state='disabled')
        # 添加一个关闭按钮
        close_btn = ttk.Button(cv, text='关 闭')
        close_btn.place(x=140, y=410)
        close_btn.bind('<ButtonRelease-1>', self.cancel_click)

    def cancel_click(self, event=None):
        # 将焦点返回给父窗口
        self.parent.focus_set()
        # 销毁自己
        self.destroy()

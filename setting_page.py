import ttkbootstrap as ttk
import tkinter.filedialog as file_box
import tkinter.messagebox as msg_box
import json
import highlight
import os
from ttkbootstrap import font
from ttkbootstrap.constants import *
from const import *


class SettingPage:
    def __init__(self, master, fonts, fonts_size):
        self.master = master
        self.fonts = fonts
        self.fonts_size = fonts_size
        self.master.Style.configure("Treeview", background=self.master.theme["SecondColor"])
        self.setting_box = ttk.Treeview(self.master, show=TREE)
        self.frame = ttk.Frame(self.master)
        self.tools = ttk.Frame(self.master)
        self.ide = self.setting_box.insert("", END, text="编辑器")
        self.run = self.setting_box.insert("", END, text="运行")
        self.theme = self.setting_box.insert("", END, text="主题")
        self.cancel = ttk.Button(self.tools, text="返回", command=self.back)
        self.setting_components = [self.setting_box, self.frame, self.tools, self.cancel]
        self.show_components = []
        self.hash_page = {
            self.ide: SettingPageIde(self, self.master.keybind),
            self.run: SettingPageRun(self),
            self.theme: SettingPageTheme(self)
        }
        self.style = self.master.theme["name"]
        self.setting_box.bind("<<TreeviewSelect>>", lambda e: self.goto_page())

    def goto_page(self):
        page = self.hash_page[self.setting_box.selection()[0]]
        page.build()
        self.show_components = page.components

    def build(self):
        for i in self.master.components:
            i.pack_forget()
        self.setting_box.pack(side=LEFT, fill=Y)
        self.tools.pack(side=BOTTOM, fill=X)
        self.cancel.pack(side=RIGHT, padx=10, pady=10)
        self.frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.setting_box.selection_clear()
        self.setting_box.selection_add(self.ide)

    def back(self):
        for i in self.show_components + self.setting_components:
            i.pack_forget()
        self.master.build()


class SettingPageIde:
    def __init__(self, master, keybind):
        self.master = master
        self.keybind_data = keybind
        self.last_component = []
        self.title = ttk.Label(self.master.frame, text="编辑器设置", font=("等线 bold", 30))
        self.keybind_title = ttk.Label(self.master.frame, text="快捷键：")
        self.keybind = ttk.Treeview(self.master.frame, show=HEADINGS)
        self.keybind["columns"] = ("功能", "快捷键")
        self.keybind.heading("功能", text="功能")
        self.keybind.heading("快捷键", text="快捷键")
        self.components = [self.title, self.keybind_title, self.keybind]

    def update_keybind(self):
        self.keybind.delete(*self.keybind.get_children())
        self.keybind_data = self.master.master.keybind
        ide_keybind = self.keybind_data["ide_keybind"]
        page_keybind = self.keybind_data["page_keybind"]
        for i in ide_keybind:
            self.keybind.insert("", END, values=(ide_keybind[i][0], ide_keybind[i][1]))
        for i in page_keybind:
            self.keybind.insert("", END, values=(page_keybind[i][0], page_keybind[i][1]))
        self.keybind.selection_set(self.keybind.get_children()[0])

    def build(self):
        self.last_component = self.master.show_components
        for i in self.last_component:
            i.pack_forget()
        self.title.pack(side=TOP, fill=X, pady=10, padx=10)
        self.keybind_title.pack(side=TOP, fill=X, pady=10, padx=10)
        self.keybind.pack(side=TOP, fill=BOTH, expand=True, pady=10, padx=10)
        self.update_keybind()


class SettingPageRun:
    def __init__(self, master):
        self.master = master
        self.last_component = []
        self.title = ttk.Label(self.master.frame, text="运行设置", font=("等线 bold", 30))
        self.mingw_frame = ttk.Frame(self.master.frame)
        self.mingw_path = ttk.Label(self.mingw_frame, text="MinGW根目录: ")
        self.mingw = ttk.Entry(self.mingw_frame, state=READONLY)
        self.mingw_open = ttk.Button(self.mingw_frame, text="打开", command=self.open_mingw)
        self.components = [self.title, self.mingw_frame, self.mingw_path,
                           self.mingw, self.mingw_open]

    def insert_mingw(self):
        with open("./src/run/cpp.json", "r") as f:
            config = json.load(f)
            self.mingw.configure(state=NORMAL)
            self.mingw.delete(0, END)
            if os.path.exists(config["Mingw"]):
                self.mingw.insert(0, config["Mingw"])
            else:
                self.mingw.insert(0, "暂未设置")
            self.mingw.configure(state=READONLY)

    def open_mingw(self):
        msg_box.showinfo("提示", "请选择MinGW的根目录（含有bin文件夹）")
        file_path = file_box.askdirectory(title="选择MinGW根目录")
        if file_path:
            with open("./src/run/cpp.json", "r") as f:
                config = json.load(f)
                config["Mingw"] = file_path
                with open("./src/run/cpp.json", "w") as p:
                    json.dump(config, p, indent=4)
            self.insert_mingw()
        msg_box.showinfo("提示", "MinGW根目录设置成功")

    def build(self):
        self.last_component = self.master.show_components
        for i in self.last_component:
            i.pack_forget()
        self.title.pack(side=TOP, fill=X, pady=10, padx=10)
        self.mingw_frame.pack(side=TOP, fill=X)
        self.mingw_path.pack(side=LEFT, pady=10, padx=10)
        self.mingw.pack(side=LEFT, pady=10, padx=10)
        self.mingw_open.pack(side=LEFT, pady=10, padx=10)
        self.insert_mingw()


class SettingPageTheme:
    def __init__(self, master):
        self.master = master
        self.last_component = []
        self.title = ttk.Label(self.master.frame, text="主题设置", font=("等线 bold", 30))
        self.theme_frame = ttk.Frame(self.master.frame)
        self.now_theme = ttk.Label(self.theme_frame, text="当前主题: ")
        self.theme = ttk.Combobox(self.theme_frame, values=themes, state=READONLY)
        self.theme_use = ttk.Button(self.theme_frame, text="应用", command=self.use_theme)
        self.font_frame = ttk.Frame(self.master.frame)
        self.now_font = ttk.Label(self.font_frame, text="当前字体: ")
        self.font_use = ttk.Button(self.font_frame, text="应用", command=self.use_font)
        self.font = ttk.Combobox(self.font_frame, values=font.families(), state=READONLY)
        self.size_frame = ttk.Frame(self.master.frame)
        self.now_size = ttk.Label(self.size_frame, text="当前字号: ")
        self.size = ttk.Spinbox(self.size_frame, from_=1, to=30, state=READONLY, command=self.view_config)
        self.size_use = ttk.Button(self.size_frame, text="应用", command=self.use_size)
        self.view = ttk.Text(self.master.frame)
        self.hl = highlight.Highlight(self.view, self.master.master.theme["HighlightColor"])
        self.view_text = '关键字：import\n函数：print()\n字符串："string"\n数字：123456\n括号：()[]{}\n注释：# 注释\n方法：tk.TK()'
        self.components = [self.title, self.theme_frame, self.now_theme, self.theme,
                           self.theme_use, self.font_frame, self.now_font, self.font,
                           self.font_use, self.size_frame, self.now_size, self.size,
                           self.size_use, self.view]
        self.theme.bind("<<ComboboxSelected>>", lambda e: self.view_config())
        self.font.bind("<<ComboboxSelected>>", lambda e: self.view_config())
        self.view.insert(END, self.view_text)

    def view_config(self):
        fonts = (self.font.get(), int(self.size.get()))
        try:
            with open(f"./src/styles/{self.theme.get()}.json", "r") as f:
                style = json.load(f)
        except Exception:
            raise Exception
        self.view.configure(font=fonts, bg=style["SecondColor"], fg=style["TextColor"])
        self.hl.set_style(style["HighlightColor"])
        self.hl.highlight("Python")
        self.view.configure(state=DISABLED)

    def build(self):
        self.last_component = self.master.show_components
        for i in self.last_component:
            i.pack_forget()
        self.title.pack(side=TOP, fill=X, pady=10, padx=10)
        self.theme_frame.pack(side=TOP, fill=X)
        self.now_theme.pack(side=LEFT, pady=10, padx=10)
        self.theme.pack(side=LEFT, pady=10, padx=10)
        self.theme_use.pack(side=LEFT, pady=10, padx=10)
        self.font_frame.pack(side=TOP, fill=X)
        self.now_font.pack(side=LEFT, pady=10, padx=10)
        self.font.pack(side=LEFT, pady=10, padx=10)
        self.font_use.pack(side=LEFT, pady=10, padx=10)
        self.size_frame.pack(side=TOP, fill=X)
        self.now_size.pack(side=LEFT, pady=10, padx=10)
        self.size.pack(side=LEFT, pady=10, padx=10)
        self.size_use.pack(side=LEFT, pady=10, padx=10)
        self.theme.current(themes.index(self.master.style))
        self.font.current(font.families().index(self.master.fonts))
        self.view.pack(side=TOP, fill=BOTH, expand=True)
        self.size.set(self.master.fonts_size)
        self.view_config()

    def use_theme(self):
        if self.theme.get() == self.master.style:
            return
        with open("./data/user_data.json", "r") as f:
            config = json.load(f)
            config["style"] = self.theme.get()
            self.master.style = self.theme.get()
            with open("./data/user_data.json", "w") as p:
                json.dump(config, p, indent=4)
        msg_box.showinfo("提示", "主题已应用，重启软件后生效。")

    def use_font(self):
        if self.font.get() == self.master.fonts:
            return
        with open("./data/user_data.json", "r") as f:
            config = json.load(f)
            config["font"] = self.font.get()
            self.master.fonts = self.font.get()
            with open("./data/user_data.json", "w") as p:
                json.dump(config, p, indent=4)
        msg_box.showinfo("提示", "字体已应用，重启软件后生效。")

    def use_size(self):
        if self.size.get() == self.master.fonts_size:
            return
        with open("./data/user_data.json", "r") as f:
            config = json.load(f)
            config["font_size"] = self.size.get()
            with open("./data/user_data.json", "w") as p:
                json.dump(config, p, indent=4)
            self.master.fonts_size = int(self.size.get())
        msg_box.showinfo("提示", "字号已应用，重启软件后生效。")

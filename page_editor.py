import ttkbootstrap as ttk
import tkinter.filedialog as file_box
import tkinter.simpledialog as input_box
import tkinter.messagebox as msg_box
import tkinter.font as font
import highlight
import setting_page
import icon
import json
import os
from const import *
from ttkbootstrap.constants import *


def error():
    msg_box.showerror("错误", "文件已被损坏，请到github上重新下载该项目。")
    exit()


class Editor(ttk.Window):
    def __init__(self, style, data, keybind):
        super().__init__()
        self.title("Light Editor")
        self.geometry("1000x600")
        self.iconbitmap("./src/LE.ico")
        if "Consolas" not in font.families() or "等线" not in font.families():
            msg_box.showerror("错误", "未安装字体，请到fonts文件夹下安装字体。")
            exit()
        self.theme = style
        self.data = data
        self.keybind = keybind
        self.can_undo = False
        self.language = "Python"
        self.save = False
        self.Style = ttk.Style(style["default"])
        self.Style.configure("TFrame", background=style["SecondColor"])
        self.Style.configure("TLabel", background=style["SecondColor"])
        self.tools = ttk.Frame(self)
        self.new_button = ttk.Button(self.tools, text="新建文件", command=self.new_file)
        self.open_button = ttk.Button(self.tools, text="打开文件", command=self.open_file)
        self.save_button = ttk.Button(self.tools, text="保存文件", command=self.save_file)
        self.cmd_button = ttk.Button(self.tools, text="启动终端", command=self.open_cmd)
        self.run_button = ttk.Button(self.tools, text="运行程序", command=self.build_code)
        self.setting_button = ttk.Button(self.tools, text=" 设    置 ", command=self.setting_page)
        self.set_lang_text = ttk.Label(self.tools, text="编程语言:")
        self.set_lang = ttk.Combobox(self.tools, values=Languages, state=READONLY)
        self.set_lang.bind("<<ComboboxSelected>>", lambda e: self.language_change())
        self.ide = ttk.Text(self, font=(data["font"], data["font_size"]), undo=True)
        self.x_scrollbar = ttk.Scrollbar(self, orient=HORIZONTAL, command=self.ide.xview)
        self.y_scrollbar = ttk.Scrollbar(self, orient=VERTICAL, command=self.ide.yview)
        self.y_scrollbar.config(command=self.ide.yview)
        self.x_scrollbar.config(command=self.ide.xview)
        self.ide.bind("<Tab>", lambda e: self.ide_tab())
        self.ide.bind("<<Modified>>", self.key_press)
        self.ide.bind("<ButtonRelease>", lambda e: self.info_update())
        self.ide.bind("<<Undo>>", lambda e: self.undo())
        self.ide.bind("<<Redo>>", lambda e: self.highlight.highlight(self.language))
        self.info = ttk.Frame(self)
        self.info_span = ttk.Label(self.info)
        self.info_lang = ttk.Label(self.info)
        self.info_file = ttk.Label(self.info)
        self.infos = [self.info_span, self.info_file, self.info_lang]
        self.components = [self.tools, self.ide, self.x_scrollbar, self.y_scrollbar,
                           self.info, self.info_span, self.info_file, self.info_lang,
                           self.new_button, self.open_button, self.save_button,
                           self.cmd_button, self.run_button, self.setting_button,
                           self.set_lang_text, self.set_lang]
        self.setting = setting_page.SettingPage(self, data["font"], data["font_size"])
        try:
            self.highlight = highlight.Highlight(self.ide, style["HighlightColor"])
        except Exception:
            error()
        self.tools_button = [self.new_button, self.open_button, self.save_button,
                             self.cmd_button,  self.run_button, self.setting_button,
                             self.set_lang_text, self.set_lang]
        self.this_file = (None, None, None)
        self.map_keybind = {
            "New": self.new_file,
            "Open": self.open_file,
            "Save": self.save_file,
            "Cmd": self.open_cmd,
            "Build": self.build_code,
            "Setting": self.setting_page
        }
        self.build()

    def undo(self):
        if self.can_undo:
            self.ide.edit_undo()
            self.can_undo = False
            self.ide.edit_modified(False)
            self.info_update()
            self.highlight.highlight(self.language)
        return "break"

    def key_press(self, event=None):
        if event.widget.edit_modified():
            self.highlight.highlight(self.language)
            self.info_update()
            event.widget.edit_modified(False)
            self.can_undo = True

    def key_bind(self):
        can_edit = self.keybind["page_keybind"]
        for i in can_edit:
            self.bind(can_edit[i][1], self.map_keybind[i])

    def ide_tab(self):
        self.ide.insert(INSERT, "    ")
        return "break"

    def insert_file(self, file, coding):
        with open(file, "r", encoding=coding) as f:
            self.ide.delete(1.0, END)
            self.ide.insert(1.0, f.read())
            self.ide.edit_modified(False)
            self.can_undo = False

    def open_file(self, *args, **kwargs):
        file = file_box.askopenfilename(title="打开文件")
        filename = file.split("/")[-1]
        directory = file.split("/")[:-1]
        directory = "/".join(directory)
        if file:
            try:
                self.insert_file(file, "utf-8")
            except UnicodeDecodeError:
                try:
                    self.insert_file(file, "gbk")
                except UnicodeDecodeError:
                    msg_box.showerror("错误", "无法打开该文件，请检查编码格式。")
                    return
            self.language = icon.get_type(filename)
            self.set_lang.current(Languages.index(self.language))
            self.highlight.highlight(self.language)
            self.this_file = (filename, file, directory)
            self.info_update()
            self.save = True
        return args, kwargs

    def save_file(self, *args, **kwargs):
        if self.this_file[0] is None:
            filetypes = [("All Files", "*.*")]
            file = file_box.asksaveasfilename(title="保存文件", filetypes=filetypes)
            if not file:
                return
            directory = file.split("/")[:-1]
            directory = "/".join(directory)
        else:
            file = self.this_file[1]
            directory = self.this_file[2]
        if file:
            with open(file, "w", encoding="utf-8") as f:
                f.write(self.ide.get(1.0, END))
            self.this_file = (file.split("/")[-1], file, directory)
        self.save = True
        self.info_update()
        return args, kwargs

    def new_file(self, *args, **kwargs):
        ipt = input_box.askstring("新建文件", "请输入文件名")
        if ipt:
            directory = file_box.askdirectory(title="另存为")
            file = f"{directory}/{ipt}"
            with open(file, "w", encoding="utf-8") as f:
                f.write("")
            self.this_file = (ipt, file, directory)
            self.info_update()
            with open(file, "w", encoding="utf-8") as f:
                f.write(self.ide.get(1.0, END))
            self.language = icon.get_type(ipt)
            self.info_update()
            self.save = True
        return args, kwargs

    @staticmethod
    def open_cmd(*args, **kwargs):
        os.system("start cmd")
        return args, kwargs

    def build_code(self, *args, **kwargs):
        if not self.save:
            if msg_box.showinfo("运行程序", "当前文件未另存，请先另存文件再运行。"):
                self.save_file()
                if not self.save:
                    return
        else:
            self.save_file()
        try:
            with open(f"./src/run/{self.language.lower()}.json", "r") as f:
                build_command = json.load(f)
                commands = build_command["build"]
        except Exception:
            error()
        if self.language == "Cpp":
            if not os.path.isfile(f"{build_command['Mingw']}/bin/g++.exe"):
                msg_box.showwarning("运行程序", "未配置MinGW，请先配置MinGW。")
                msg_box.showinfo("运行程序", "请去到设置页面，找到运行，点击进去修改mingw路径")
                return
        for cmd in range(len(commands)):
            commands[cmd] = commands[cmd].replace("{file}", self.this_file[1])
            commands[cmd] = commands[cmd].replace("{dir}", self.this_file[2])
            if self.language == "Cpp":
                commands[cmd] = commands[cmd].replace("{Mingw}", build_command["Mingw"])
            commands[cmd] = '"' + commands[cmd] + '"'
        os.system(f'start Run {" ".join(commands)}')
        return args, kwargs

    def info_update(self):
        line = None
        col = None
        if self.ide.index(INSERT):
            line = self.ide.index(INSERT).split(".")[0]
            col = int(self.ide.index(INSERT).split(".")[1]) + 1
        self.info_span.configure(text=f"行: {line}, 列: {col}")
        self.info_file.configure(text=f"文件名：{self.this_file[0]}")
        self.info_lang.configure(text=f"编程语言：{self.language}")

    def language_change(self):
        self.language = self.set_lang.get()
        self.highlight.highlight(self.language)
        self.info_update()

    def setting_page(self, *args, **kwargs):
        self.setting.build()
        return args, kwargs

    def build(self):
        self.tools.pack(side=TOP, fill=X)
        self.info.pack(side=BOTTOM, fill=X)
        self.x_scrollbar.pack(side=BOTTOM, fill=X)
        for button in self.tools_button:
            button.pack(side=LEFT, padx=10, pady=10)
        for info in self.infos:
            info.pack(side=LEFT, padx=10, pady=10)
        self.y_scrollbar.pack(side=RIGHT, fill=Y)
        self.ide.pack(side=LEFT, fill=BOTH, expand=True)
        self.info_update()
        self.set_lang.current(0)
        self.ide.configure(background=self.theme["MainColor"],
                           xscrollcommand=self.x_scrollbar.set,
                           yscrollcommand=self.y_scrollbar.set)
        self.key_bind()

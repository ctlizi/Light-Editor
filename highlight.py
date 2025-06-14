import re
import json

import ttkbootstrap
from ttkbootstrap.constants import *


class PythonHighlight:
    def __init__(self):
        try:
            with open("./src/words/python.json", 'r') as f:
                self.words = json.load(f)
        except Exception:
            raise Exception
        self.kw_words = re.compile(r"\b" + r"\b|\b".join(self.words["keywords"]) + r"\b")
        self.functions = r""
        for func in self.words["functions"]:
            self.functions += fr"{func}\(" + "|"
        self.functions = self.functions[:-1]
        self.functions = re.compile(self.functions)
        self.func_user = re.compile(r"\bdef\s+(?P<name>.*?)\((?P<args>.*?)\):\b")
        self.numbers = re.compile(r"\b\d+\b")
        self.baskets = re.compile(r"[(){}\[\]]")
        self.string = []
        self.flag_string = [(False, None) for _ in range(len(self.string))]
        self.comments = re.compile(r"#.*")
        self.dot = re.compile(r"\.[a-zA-Z_][a-zA-Z0-9_]*\(")
        self.turns = [self.func_user, self.kw_words, self.functions,
                      self.baskets, self.numbers, self.dot, self.comments, self.string]
        self.infos = ["user_functions", "keywords", "functions", "baskets",
                      "numbers", "dot", "comments", "string"]

    def highlight(self, text):
        get = {
            "functions": [],
            "keywords": [],
            "numbers": [],
            "dot": [],
            "baskets": [],
            "comments": [],
            "string": [],
            "user_functions": []
        }
        text = " " + text
        index = 0
        stack = []
        flag = False
        for i in range(len(self.turns)):
            if i == 7:
                for j in range(len(text)):
                    if text[j] == '"' or text[j] == "'":
                        self.string.append(j)
                tag = self.string
                self.flag_string = [[False, "'" if text[s] == "'" else '"', s] for s in tag]
            else:
                tag = self.turns[i].finditer(text)
            for match in list(tag):
                if i == 7:
                    if index == 0:
                        stack.append(self.flag_string[index])
                        index += 1
                        continue
                    if not stack:
                        stack.append(self.flag_string[index])
                        index += 1
                        continue
                    for j in stack:
                        if not j[0] and j[1] == self.flag_string[index][1]:
                            get["string"].append((j[2] - 1, self.flag_string[index][2]))
                            for k in stack[stack.index(j):]:
                                stack.remove(k)
                            index += 1
                            flag = True
                            break
                    if flag:
                        flag = False
                        continue
                    stack.append(self.flag_string[index])
                    index += 1
                    continue
                start, end = match.span()
                if i == 0:
                    user_func = match.group("name")
                    user_func = re.compile(fr"{user_func}\(")
                    for j in user_func.finditer(text):
                        start, end = j.span()
                        end -= 1
                        get[self.infos[i]].append((start - 1, end - 1))
                    continue
                if i == 2:
                    end -= 1
                if i == 5:
                    end -= 1
                    start += 1
                get[self.infos[i]].append((start - 1, end - 1))
        self.string.clear()
        self.flag_string.clear()
        return get


class CppHighlight:
    def __init__(self):
        try:
            with open("./src/words/cpp.json", 'r') as f:
                self.words = json.load(f)
        except Exception:
            raise Exception
        self.kw_words = re.compile(r"\b" + r"\b|\b".join(self.words["keywords"]) + r"\b")
        self.numbers = re.compile(r"\b\d+\b")
        self.baskets = re.compile(r"[(){}\[\]]")
        self.preprocessor = re.compile(r"#" + r"|#".join(self.words["preprocessor"]))
        self.string = []
        self.flag_string = [(False, None) for _ in range(len(self.string))]
        self.comments = re.compile(r"\b//.*")
        self.dot = re.compile(r"\.[a-zA-Z_][a-zA-Z0-9_]*\(")
        self.turns = [self.kw_words, self.preprocessor, self.baskets, self.numbers,
                      self.dot, self.comments, self.string]
        self.infos = ["keywords", "preprocessor", "baskets", "numbers", "dot", "comments", "string"]

    def highlight(self, text):
        get = {
            "keywords": [],
            "preprocessor": [],
            "numbers": [],
            "dot": [],
            "baskets": [],
            "comments": [],
            "string": []
        }
        text = " " + text
        index = 0
        stack = []
        flag = False
        for i in range(len(self.turns)):
            if i == 6:
                for j in range(len(text)):
                    if text[j] == '"':
                        self.string.append(j)
                tag = self.string
                self.flag_string = [[False, s] for s in tag]
            else:
                tag = self.turns[i].finditer(text)
            for match in list(tag):
                if i == 6:
                    if index == 0:
                        stack.append(self.flag_string[index])
                        index += 1
                        continue
                    if not stack:
                        stack.append(self.flag_string[index])
                        index += 1
                        continue
                    for j in stack:
                        if not j[0]:
                            get["string"].append((j[1] - 1, self.flag_string[index][1]))
                            for k in stack[stack.index(j):]:
                                stack.remove(k)
                            index += 1
                            flag = True
                            break
                    if flag:
                        flag = False
                        continue
                    stack.append(self.flag_string[index])
                    index += 1
                    continue
                start, end = match.span()
                get[self.infos[i]].append((start - 1, end - 1))
        self.string.clear()
        self.flag_string.clear()
        return get


class Highlight:
    def __init__(self, master: ttkbootstrap.Text, style):
        self.master = master
        self.style = style
        self.highlight_object = None
        self.highlight_turns = None
        self.tags = ["numbers", "baskets", "keywords", "functions", "comments", "string",
                     "user_functions", "dot", "preprocessor"]
        self.set_style(style)

    def set_style(self, style):
        self.style = style
        for tag in self.tags:
            if tag == "dot":
                self.master.tag_configure(tag, foreground=self.style["user_functions"])
            elif tag == "preprocessor":
                self.master.tag_configure(tag, foreground=self.style["keywords"])
            else:
                self.master.tag_configure(tag, foreground=self.style[tag])
        self.master.tag_configure("default", foreground=self.style["default"])

    def clear(self):
        for i in self.tags:
            self.master.tag_remove(i, "1.0", END)

    def highlight(self, words):
        if words == "Python":
            try:
                self.highlight_object = PythonHighlight()
            except Exception:
                raise Exception
            self.highlight_turns = self.highlight_object.infos
        if words == "Cpp":
            try:
                self.highlight_object = CppHighlight()
            except Exception:
                raise Exception
            self.highlight_turns = self.highlight_object.infos
        highlight_words = self.highlight_object.highlight(self.master.get(1.0, END))
        self.clear()
        for i in self.highlight_turns:
            for j in highlight_words[i]:
                start, end = j
                self.master.tag_remove("default", f"1.0+{start}c", f"1.0+{end}c")
                self.master.tag_add(i, f"1.0+{start}c", f"1.0+{end}c")

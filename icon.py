from const import *


types = ["Python", "Cpp", "File"]


def get_type(file_name):
    ext = "." + file_name.split(".")[-1]
    for i in all_files.items():
        print(i)
        if ext in i[1]:
            return i[0]
    return "File"

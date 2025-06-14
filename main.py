import json
import page_editor


def main():
    try:
        with open("./data/user_data.json", "r") as f:
            dat = json.load(f)
        with open("./data/key_bind.json", "r", encoding="utf-8") as f:
            keybind = json.load(f)
        with open(f"./src/styles/{dat['style']}.json", "r") as f:
            style = json.load(f)
    except Exception:
        page_editor.msg_box.showerror("错误", "文件已被损坏，请到github上重新下载该项目。")
        exit()
    app = page_editor.Editor(style=style, data=dat, keybind=keybind)
    app.mainloop()


if __name__ == "__main__":
    main()


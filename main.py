import tkinter as tk
from planner_ui import PlannerApp

if __name__ == "__main__":
    root = tk.Tk()
    # 设置主题风格
    try:
        from tkinter import ttk

        style = ttk.Style()
        style.theme_use('clam')  # 使用较现代的样式
    except:
        pass

    app = PlannerApp(root)
    root.mainloop()
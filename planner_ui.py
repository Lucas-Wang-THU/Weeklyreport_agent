import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from data_model import PlanManager
from report_generator import WordGenerator
from ai_agent import ReportAgent
from config import USER_NAME, FULL_REPORT_PATH
import threading
import os
import PyPDF2  # 引入PDF库


class PlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Visual Planner Pro - {USER_NAME}")
        self.root.geometry("1150x800")  # 稍微加大一点窗口

        self.manager = PlanManager()
        self.agent = ReportAgent()

        self.current_item_id = None

        self._init_ui()
        self._load_ui_data()

    def _init_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: 看板
        self.tab_plan = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_plan, text='任务看板与成果')
        self._build_dashboard()

        # Tab 2: 深度思考 (主要修改区域)
        self.tab_thought = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_thought, text='深度思考与规划')
        self._build_thought_tab()

        # 底部
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill='x', padx=10, pady=10)
        ttk.Button(btn_frame, text="保存所有进度", command=self.save_all).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="生成 Word 周报 (AI)", command=self.generate_report).pack(side='right', padx=5)

    def _build_dashboard(self):
        # ... (保持原有的 dashboard 代码不变，为节省篇幅省略，请直接复用上一版代码) ...
        # 如果需要完整代码请看上一条回复，这里只展示 _build_thought_tab 的变化
        # --- start dashboard copy ---
        left_pane = ttk.LabelFrame(self.tab_plan, text="上周计划清单 (双击状态栏切换完成度)", width=400)
        left_pane.pack(side='left', fill='y', expand=False, padx=5, pady=5)
        left_pane.pack_propagate(False)

        cols = ('status', 'title')
        self.tree = ttk.Treeview(left_pane, columns=cols, show='headings', selectmode='browse')
        self.tree.heading('status', text='状态', anchor='center')
        self.tree.heading('title', text='任务内容')
        self.tree.column('status', width=60, anchor='center')
        self.tree.column('title', width=300)
        self.tree.pack(fill='both', expand=True)

        self.tree.bind('<<TreeviewSelect>>', self.on_select_item)
        self.tree.bind('<Double-1>', self.on_double_click)

        input_frame = ttk.Frame(left_pane)
        input_frame.pack(fill='x', pady=5)
        self.entry_new = ttk.Entry(input_frame)
        self.entry_new.pack(side='left', fill='x', expand=True)
        ttk.Button(input_frame, text="+", width=3, command=self.add_task).pack(side='left')
        ttk.Button(input_frame, text="-", width=3, command=self.del_task).pack(side='left')

        right_pane = ttk.LabelFrame(self.tab_plan, text="任务执行详情")
        right_pane.pack(side='right', fill='both', expand=True, padx=5, pady=5)

        ttk.Label(right_pane, text="执行情况描述:").pack(anchor='w')
        self.text_result = scrolledtext.ScrolledText(right_pane, height=12)
        self.text_result.pack(fill='x', padx=5, pady=5)

        img_frame = ttk.LabelFrame(right_pane, text="成果截图/图片证据")
        img_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.list_images = tk.Listbox(img_frame, height=5)
        self.list_images.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        btn_img_box = ttk.Frame(img_frame)
        btn_img_box.pack(side='right', fill='y', padx=5, pady=5)
        ttk.Button(btn_img_box, text="添加图片", command=self.add_image).pack(pady=2)
        ttk.Button(btn_img_box, text="移除选中", command=self.del_image).pack(pady=2)
        # --- end dashboard copy ---

    def _build_thought_tab(self):
        """ 重构后的思考 Tab，包含新的功能按钮 """
        # 使用 Canvas + Scrollbar 防止屏幕太小显示不全
        canvas = tk.Canvas(self.tab_thought)
        scrollbar = ttk.Scrollbar(self.tab_thought, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 定义各个板块
        self.thought_texts = {}

        # 1. 下周计划 (特殊处理：增加迁移按钮)
        frame_next = ttk.LabelFrame(scrollable_frame, text="本周(下周)工作计划")
        frame_next.pack(fill='x', expand=True, padx=10, pady=5)

        self.text_next = scrolledtext.ScrolledText(frame_next, height=5)
        self.text_next.pack(fill='x', padx=5, pady=5)
        self.thought_texts["next_week_plan"] = self.text_next

        # 按钮：将下周计划转为待办
        ttk.Button(frame_next, text="⬇ 将上述计划添加至左侧待办清单",
                   command=self.migrate_next_plan_to_todo).pack(anchor='e', padx=5, pady=5)

        # 2. 文献阅读 (特殊处理：增加PDF上传)
        frame_lit = ttk.LabelFrame(scrollable_frame, text="文献阅读情况")
        frame_lit.pack(fill='x', expand=True, padx=10, pady=5)

        self.text_lit = scrolledtext.ScrolledText(frame_lit, height=5)
        self.text_lit.pack(fill='x', padx=5, pady=5)
        self.thought_texts["literature"] = self.text_lit

        # 按钮：上传PDF
        btn_frame_lit = ttk.Frame(frame_lit)
        btn_frame_lit.pack(fill='x', padx=5, pady=2)
        ttk.Button(btn_frame_lit, text="📄 上传PDF并由AI生成阅读摘要",
                   command=self.upload_and_summarize_pdf).pack(side='right')

        # 3. 其他常规板块
        other_labels = {
            "近期总工作目标": "long_term_goals",
            "工作意义": "significance",
            "其他未尽问题": "others"
        }

        for label, key in other_labels.items():
            lf = ttk.LabelFrame(scrollable_frame, text=label)
            lf.pack(fill='x', expand=True, padx=10, pady=5)
            t = scrolledtext.ScrolledText(lf, height=4)
            t.pack(fill='x', padx=5, pady=5)
            self.thought_texts[key] = t

    def _load_ui_data(self):
        d = self.manager.data
        # Load List
        for idx, item in enumerate(d.get('weekly_items', [])):
            stat_icon = "✅" if item.get('status') == 'done' else "⬜"
            self.tree.insert('', 'end', iid=str(idx), values=(stat_icon, item.get('title', '')))

        # Load Texts
        mappings = {
            "next_week_plan": self.text_next,
            "long_term_goals": self.thought_texts["long_term_goals"],
            "significance": self.thought_texts["significance"],
            "literature": self.text_lit,
            "others": self.thought_texts["others"]
        }

        for key, widget in mappings.items():
            content = d.get(key, "")
            if isinstance(content, list): content = "\n".join(content)
            widget.delete('1.0', 'end')
            widget.insert('1.0', content)

    # --- 新增功能逻辑 ---

    def migrate_next_plan_to_todo(self):
        """将下周计划文本框的内容，逐行解析并添加到左侧待办列表"""
        content = self.text_next.get("1.0", "end-1c")
        if not content.strip():
            messagebox.showwarning("提示", "下周计划为空，无法迁移。")
            return

        lines = content.split('\n')
        count = 0
        for line in lines:
            clean_line = line.strip()
            # 去除可能存在的编号 (如 "1. ", "(1)")
            if not clean_line: continue

            # 简单的正则清理或者直接添加
            import re
            clean_line = re.sub(r'^[\d\uff10-\uff19]+\.?\s*', '', clean_line)  # 去除数字开头
            clean_line = re.sub(r'^[（(][\d\uff10-\uff19]+[)）]\s*', '', clean_line)  # 去除(1)开头

            if clean_line:
                # 添加到数据模型
                new_item = {"title": clean_line, "status": "todo", "result": "", "images": []}
                self.manager.data.setdefault('weekly_items', []).append(new_item)

                # 添加到 UI
                idx = len(self.manager.data['weekly_items']) - 1
                self.tree.insert('', 'end', iid=str(idx), values=("⬜", clean_line))
                count += 1

        if count > 0:
            messagebox.showinfo("成功", f"已将 {count} 条计划移入左侧待办清单！")
            # 可选：清空原文本框
            # self.text_next.delete("1.0", "end")
        else:
            messagebox.showwarning("提示", "未识别到有效内容")

    def upload_and_summarize_pdf(self):
        """选择PDF -> 提取文本 -> AI总结 -> 填入文本框"""
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            return

        def task():
            try:
                # 1. 读取PDF
                text_content = ""
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    # 只读取前3页，通常包含摘要和引言
                    pages_to_read = min(3, len(reader.pages))
                    for i in range(pages_to_read):
                        text_content += reader.pages[i].extract_text()

                if len(text_content) < 50:
                    messagebox.showerror("错误", "PDF内容过少或无法提取文本（可能是扫描件）")
                    return

                # 2. 调用 AI
                messagebox.showinfo("AI Agent", "正在读取论文并生成摘要，请稍候...")
                summary = self.agent.summarize_paper(text_content)

                # 3. 更新 UI (需在主线程)
                self.root.after(0, lambda: self._append_lit_review(summary))

            except Exception as e:
                messagebox.showerror("错误", f"处理失败: {str(e)}")

        threading.Thread(target=task).start()

    def _append_lit_review(self, text):
        """将AI生成的摘要追加到文本框中"""
        current_text = self.text_lit.get("1.0", "end-1c")
        if current_text.strip():
            new_text = current_text + "\n\n" + text
        else:
            new_text = text

        self.text_lit.delete("1.0", "end")
        self.text_lit.insert("1.0", new_text)
        messagebox.showinfo("完成", "文献摘要已生成并填入！")

    # --- 保持原有的其他方法 ---
    # save_all, generate_report, add_task, del_task, ...
    # 请确保将之前 planner_ui.py 中的其他 helper function (save_all, on_select_item等) 复制过来

    # ... (以下为必须保留的方法，为完整性请确保代码中包含) ...
    def save_current_details(self):
        if self.current_item_id is not None:
            items = self.manager.data.get('weekly_items', [])
            idx = int(self.current_item_id)
            if idx < len(items):
                items[idx]['result'] = self.text_result.get("1.0", "end-1c")
                items[idx]['images'] = list(self.list_images.get(0, 'end'))

    def on_select_item(self, event):
        self.save_current_details()
        sel = self.tree.selection()
        if not sel: return
        self.current_item_id = sel[0]
        idx = int(self.current_item_id)
        items = self.manager.data.get('weekly_items', [])
        if idx < len(items):
            item = items[idx]
            self.text_result.delete("1.0", "end")
            self.text_result.insert("1.0", item.get('result', ''))
            self.list_images.delete(0, 'end')
            for img in item.get('images', []):
                self.list_images.insert('end', img)

    def on_double_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            col = self.tree.identify_column(event.x)
            if col == '#1':
                sel = self.tree.selection()
                if not sel: return
                idx = int(sel[0])
                items = self.manager.data.get('weekly_items', [])
                current_status = items[idx].get('status', 'todo')
                new_status = 'done' if current_status == 'todo' else 'todo'
                items[idx]['status'] = new_status
                icon = "✅" if new_status == 'done' else "⬜"
                self.tree.set(sel[0], column='status', value=icon)

    def add_task(self):
        val = self.entry_new.get()
        if val:
            new_item = {"title": val, "status": "todo", "result": "", "images": []}
            self.manager.data.setdefault('weekly_items', []).append(new_item)
            idx = len(self.manager.data['weekly_items']) - 1
            self.tree.insert('', 'end', iid=str(idx), values=("⬜", val))
            self.entry_new.delete(0, 'end')

    def del_task(self):
        sel = self.tree.selection()
        if sel:
            idx = int(sel[0])
            del self.manager.data['weekly_items'][idx]
            for item in self.tree.get_children(): self.tree.delete(item)
            self._load_ui_data()

    def add_image(self):
        if self.current_item_id is None:
            messagebox.showwarning("提示", "请先选择左侧的一个任务")
            return
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
        if path:
            self.list_images.insert('end', path)
            self.save_current_details()

    def del_image(self):
        sel = self.list_images.curselection()
        if sel:
            self.list_images.delete(sel)
            self.save_current_details()

    def save_all(self):
        self.save_current_details()
        d = self.manager.data

        # 保存 Text 组件内容
        d["next_week_plan"] = self.thought_texts["next_week_plan"].get("1.0", "end-1c").split('\n')
        d["long_term_goals"] = self.thought_texts["long_term_goals"].get("1.0", "end-1c")
        d["significance"] = self.thought_texts["significance"].get("1.0", "end-1c")
        d["literature"] = self.thought_texts["literature"].get("1.0", "end-1c")
        d["others"] = self.thought_texts["others"].get("1.0", "end-1c")

        self.manager.save_data(d)
        messagebox.showinfo("保存", "数据已保存")

    def generate_report(self):
        self.save_all()
        threading.Thread(target=self._run_agent).start()

    def _run_agent(self):
        try:
            raw_data = self.manager.data
            polished = self.agent.polish_content(raw_data)
            gen = WordGenerator(FULL_REPORT_PATH)
            path = gen.generate(raw_data, polished)
            messagebox.showinfo("成功", f"文件已生成:\n{path}")
        except Exception as e:
            print(e)
            messagebox.showerror("错误", f"生成失败: {e}")

---

# 🤖 AI-Powered Academic Weekly Planner (智能学术周报生成助手)

**一个集成了可视化计划管理、成果追踪与 AI 自动化写作的桌面端效能工具。**

本项目专为科研人员、研究生及开发者设计，旨在解决周报撰写过程中“记录碎片化”、“格式调整繁琐”、“文献总结耗时”的痛点。通过直观的 GUI 界面管理本周任务，利用 LLM (OpenRouter/GPT) 将碎片化的执行记录润色为学术严谨的汇报语言，并自动排版生成符合标准格式的 Word 文档。

---

## ✨ 核心功能 (Key Features)

### 1. 📅 可视化任务看板 (Visual Dashboard)
- **待办/完成状态切换**：通过双击任务图标（⬜ / ✅）快速标记完成状态。
- **图文成果录入**：支持为每一项任务添加详细的文字描述及多张图片证据（如仿真云图、代码运行截图），图片将自动插入 Word 对应段落中。

### 2. 🧠 AI 智能写作与润色 (AI-Driven Polishing)
- **学术化重写**：内置专业的 Prompt Engineering，通过 OpenRouter API 调用 LLM，将口语化的工作记录（如“跑通了代码”）自动润色为专业学术表达（如“完成了相关算法模块的构建与验证”）。
- **严格中文输出**：强制 AI 输出简体中文，保留必要的英文术语（如 Midas, Python），确保周报语言规范。

### 3. 📄 自动化文档生成 (Auto-Documentation)
- **标准格式输出**：基于 `python-docx`，严格遵循学术周报排版规范：
  - **字体混排**：中文强制使用 **宋体**，西文/数字使用 **Times New Roman**。
  - **段落布局**：自动处理 1.5 倍行距、首行缩进、各级标题加粗。
  - **自动命名**：文件按 `姓名-（日期）周报.docx` 格式自动保存至指定目录。

### 4. 📚 文献辅助与闭环管理 (Smart Workflow)
- **PDF 智能摘要**：集成 `PyPDF2`，支持直接上传 PDF 论文，AI 自动读取摘要并生成“标题+问题+结论”格式的精炼阅读报告。
- **计划自动迁移**：支持一键将“下周计划”迁移至左侧“待办列表”，实现周与周之间的无缝衔接。

---

## 🛠️ 技术栈 (Tech Stack)

- **语言**: Python 3.8+
- **GUI 框架**: Tkinter (ttk)
- **大模型接口**: OpenAI API Standard (via OpenRouter)
- **文档处理**: `python-docx` (Word), `PyPDF2` (PDF)
- **图像处理**: Pillow (PIL)
- **数据存储**: JSON (本地持久化)

---

## 📂 项目结构 (Project Structure)

```text
AI-Weekly-Planner/
├── main.py              # 程序入口
├── planner_ui.py        # 桌面 GUI 界面逻辑 (Tkinter)
├── ai_agent.py          # AI 智能体 (调用 LLM API)
├── report_generator.py  # Word 文档生成器 (处理排版与样式)
├── data_model.py        # 数据持久化与状态管理
├── config.py            # 配置文件 (API Key, 路径设置)
├── requirements.txt     # 依赖库列表
└── plan_data.json       # (自动生成) 本地存储的任务数据
```

---

## 🚀 快速开始 (Quick Start)

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/AI-Weekly-Planner.git
   cd AI-Weekly-Planner
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置 API**
   打开 `config.py`，填入你的 OpenRouter API Key：
   ```python
   OPENROUTER_API_KEY = "sk-or-your-api-key-here"
   USER_NAME = "你的名字"
   ```

4. **运行程序**
   ```bash
   python main.py
   ```

---

## 📸 使用截图 (Screenshots)

*(此处可放置程序运行截图)*
1. **任务看板**：左侧管理任务，右侧录入图文成果。
2. **深度思考页**：上传 PDF 生成摘要，规划下周工作。
3. **成果文档**：自动生成的 Word 周报，排版精美，包含图片。

---

## 📝 License

This project is licensed under the MIT License.

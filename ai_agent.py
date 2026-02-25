import openai
import json
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME


class ReportAgent:
    def __init__(self):
        self.client = openai.OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )

    def polish_content(self, raw_data):
        """
        读取结构化数据，使用LLM润色成中文学术周报风格
        """
        # 1. 预处理数据：将 list 转换为字符串以便 AI 理解
        items = raw_data.get('weekly_items', [])
        # 提取 "任务标题 + 执行结果"
        results_context = "\n".join([
            f"- 任务{i + 1}: {item['title']} (执行情况: {item.get('result', '已完成')})"
            for i, item in enumerate(items)
        ])

        # 2. 构建提示词 (Prompt Engineering)
        # 核心修改：明确要求 "Simplified Chinese" 和 "Academic Tone"
        system_instruction = (
            "你是一名资深的科研学术助理。你的任务是将用户的碎片化工作记录，润色为一份专业、严谨、逻辑通顺的**中文**学术周报。"
            "所有输出必须严格使用**简体中文**。"
            "遇到专有名词（如 Midas, Python, Transformer）可以保留英文，但其余描述性文字必须是中文。"
        )

        user_prompt = f"""
        请根据以下原始输入数据，生成对应的周报内容。

        【原始数据】
        1. 本周工作计划及完成情况:
        {results_context}

        2. 近期总目标: {raw_data.get('long_term_goals', '暂无')}
        3. 工作意义: {raw_data.get('significance', '暂无')}
        4. 文献阅读: {raw_data.get('literature', '暂无')}

        【生成要求】
        1. **返回格式**：必须是标准的 JSON 格式，不要包含 Markdown 标记（如 ```json）。
        2. **内容要求**：
           - "summary_list": (数组) 针对上面的每一项任务，生成一段学术风格的总结。例如将“做完了”润色为“完成了...的构建与验证”。**数量必须与任务数量一致**。
           - "long_term_goals": (字符串) 润色近期目标，使其听起来更有规划性。
           - "significance": (字符串) 润色工作意义，强调研究价值。
           - "literature": (字符串) 润色文献阅读情况。

        【JSON结构示例】
        {{
            "summary_list": ["完成了XXX模块的代码重构...", "针对YYY问题进行了仿真实验..."],
            "long_term_goals": "推进...",
            "significance": "本周工作验证了...",
            "literature": "阅读了..."
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                # 强制 JSON 模式 (如果模型支持)
                response_format={"type": "json_object"},
                temperature=0.7
            )

            content = response.choices[0].message.content
            # 解析 JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # 如果模型偶尔返回了 ```json 包裹，尝试清洗
                clean_content = content.replace("```json", "").replace("```", "").strip()
                return json.loads(clean_content)

        except Exception as e:
            print(f"AI Agent Error: {e}")
            # 降级处理：如果 AI 挂了，返回原始数据，保证程序不崩
            return {
                "summary_list": [item.get('result', '') for item in items],
                "long_term_goals": raw_data.get('long_term_goals', ""),
                "significance": raw_data.get('significance', ""),
                "literature": raw_data.get('literature', "")
            }

    def summarize_paper(self, paper_text):
        """
        专门用于读取论文片段，生成周报格式的文献阅读记录
        """
        prompt = f"""
        请阅读以下论文的开头部分（包含标题、摘要和引言片段），请提取核心信息。

        要求：
        1. 输出格式严格为：**《论文中文标题（若原为英文请直译）》：简要概括该研究解决了什么问题，用了什么方法，得出了什么结论。（约100字）**
        2. 必须使用**简体中文**。
        3. 语气要在学术周报中显得自然。

        论文内容片段：
        {paper_text[:2500]} 
        """
        # 限制字符数防止token溢出

        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "你是一个学术科研助手，擅长快速总结文献。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Paper Summary Error: {e}")
            return "（AI读取文献失败，请手动输入）"
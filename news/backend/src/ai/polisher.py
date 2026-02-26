"""AI润色模块。

使用阿里云通义千问API实现文章润色功能。
负责将中文文章润色为适合今日头条发布的风格。
"""
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class Polisher:
    """文章润色器，使用通义千问API将中文文章润色为适合今日头条发布的风格。"""

    def __init__(self):
        """初始化润色器。"""
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = "qwen3-max"

    def polish(self, text: str) -> str:
        """润色中文文章。

        Args:
            text: 待润色的中文文章。

        Returns:
            str: 润色后的中文文章。
        """
        if not text:
            return ""

        prompt = f"""你是一名资深国际政治评论员，现需撰写一篇适合在今日头条发布的原创时事评论文章。请严格遵循以下要求：

1. **内容来源处理**：
   - 基于用户提供的外媒报道（如BBC、CNN等）中的**公开事实信息**（如民调数据、政策事件、时间、人物言论等）进行整合；
   - **不得直接翻译、复制或改写原文句子**，所有表达必须为原创；
   - 不得声称"据XX报道"作为主语，而是将外媒信息视为背景素材。

2. **文章定位**：
   - 类型：**原创评论/分析**，非新闻报道；
   - 语气：客观冷静，略带洞察力，避免情绪化或煽动性语言；
   - 视角：以"作者观察"为主，可引用专家观点或历史对比，但需明确是分析而非转述。

3. **风格与格式（今日头条适配）**：
   - 标题：简洁有力，含冲突、悬念或数字（如"跌破40%""最后8个月"）；
   - 正文：700–850字；
   - 段落：每段2–4行，逻辑递进，重点突出；
   - 开头：首段直击核心矛盾或转折点；
   - 结尾：留有思考空间或指向未来事件（如选举、政策后果）。

4. **法律与合规要求**：
   - 文末必须添加声明段落，格式如下：
     > 本文所涉[事件/数据]综合自BBC、CNN等国际媒体[年份][月份]公开报道，仅用于事实背景参考。  
     > 文中分析、观点及表述均为作者独立撰写，不代表任何外媒立场，亦非对原始报道的翻译或转载。  
     > 本文为原创时事评论，转载请注明出处；如有版权疑义，请联系删除。

5. **禁止行为**：
   - 不得虚构未提及的事实；
   - 不得使用"编译""据XX报道""XX称"作为段落主干；
   - 不得照搬原文结构或修辞模式。

请根据以上准则，将以下原文润色为符合今日头条调性的原创评论文章：

原文如下：
{text}

请直接输出润色后的文章内容，不要包含任何解释或前缀。"""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            return completion.choices[0].message.content or ""
        except Exception as e:
            print(f"润色失败: {e}")
            return ""


def polish_text(text: str) -> str:
    """润色文本（供命令行或外部调用）。"""
    polisher = Polisher()
    return polisher.polish(text)


if __name__ == "__main__":
    import sys
    text = sys.argv[1] if len(sys.argv) > 1 else "这是一个测试文章。"
    result = polish_text(text)
    print(result)

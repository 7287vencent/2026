"""翻译模块。

使用阿里云通义千问API实现英译中功能。
只负责翻译，不涉及数据库操作。
"""
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class Translator:
    """翻译器，使用通义千问API将英文翻译成中文。"""

    def __init__(self):
        """初始化翻译器。"""
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model = "qwen-mt-plus"

    def translate(self, text: str) -> str:
        """将英文翻译成中文。

        Args:
            text: 待翻译的英文文本。

        Returns:
            str: 翻译后的中文文本。
        """
        if not text:
            return ""

        messages = [
            {
                "role": "user",
                "content": f"请将以下英文文章翻译成中文。只输出翻译后的中文内容，不要输出任何英文。\n\n{text}"
            }
        ]

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
            )
            return completion.choices[0].message.content or ""
        except Exception as e:
            print(f"翻译失败: {e}")
            return ""


def translate_text(text: str) -> str:
    """翻译文本（供命令行或外部调用）。"""
    translator = Translator()
    return translator.translate(text)


if __name__ == "__main__":
    import sys
    text = sys.argv[1] if len(sys.argv) > 1 else "Hello, this is a test."
    result = translate_text(text)
    print(result)

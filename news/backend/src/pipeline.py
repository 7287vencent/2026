"""任务编排模块。

整合爬虫、内容获取、翻译等功能，提供统一的调用入口。
支持单独调用或组合调用各个功能模块。
"""
import asyncio
from typing import List, Dict, Optional

from models.database import db

from src.crawler import BBCCrawler, run as run_crawler
from src.article_fetcher import ArticleFetcher, fetch_article
from src.ai.translator import Translator


class NewsPipeline:
    """新闻处理流水线，整合爬虫、获取、翻译等各个环节。"""

    @staticmethod
    async def crawl_and_save() -> int:
        """步骤1: 爬取新闻列表并保存到数据库。

        Returns:
            int: 新增文章数量。
        """
        print("=" * 50)
        print("步骤1: 爬取BBC Most Read新闻")
        print("=" * 50)

        articles = await run_crawler()
        if not articles:
            print("未获取到任何新闻")
            return 0

        count = db.add_articles_batch(articles)
        print(f"新增 {count} 篇文章")
        return count

    @staticmethod
    def fetch_article_content(article_id: int) -> bool:
        """步骤2: 获取单篇文章的详细内容。

        Args:
            article_id: 文章ID。

        Returns:
            bool: 成功返回True，失败返回False。
        """
        print("=" * 50)
        print(f"步骤2: 获取文章内容 (ID: {article_id})")
        print("=" * 50)

        article = db.get_article_by_id(article_id)
        if not article:
            print(f"文章不存在: {article_id}")
            return False

        result = asyncio.run(fetch_article(article["url"]))
        if not result:
            print("获取内容失败")
            return False

        db.update_article(article_id, result)
        print("文章内容已更新")
        return True

    @staticmethod
    def translate_article(article_id: int) -> bool:
        """步骤3: 翻译文章到中文。

        Args:
            article_id: 文章ID。

        Returns:
            bool: 成功返回True，失败返回False。
        """
        print("=" * 50)
        print(f"步骤3: 翻译文章 (ID: {article_id})")
        print("=" * 50)

        article = db.get_article_by_id(article_id)
        if not article:
            print(f"文章不存在: {article_id}")
            return False

        translator = Translator()

        title_zh = translator.translate(article["title_en"])
        print(f"标题翻译完成: {title_zh[:30]}...")

        content_zh = ""
        if article.get("content_en"):
            content_zh = translator.translate(article["content_en"])
            print(f"正文翻译完成: {len(content_zh)} 字符")

        db.update_article(article_id, {
            "title_zh": title_zh,
            "content_zh": content_zh,
            "status": "translated"
        })
        print("翻译结果已保存")
        return True

    @staticmethod
    def run_full_pipeline(article_id: Optional[int] = None) -> bool:
        """运行完整流水线。

        如果不指定article_id，则执行爬虫+最新文章的处理。

        Args:
            article_id: 文章ID，None则自动处理最新文章。

        Returns:
            bool: 成功返回True，失败返回False。
        """
        print("\n" + "=" * 50)
        print("开始运行完整流水线")
        print("=" * 50 + "\n")

        NewsPipeline.crawl_and_save()

        if article_id is None:
            articles = db.get_all_articles()
            if articles:
                article_id = articles[0]["id"]

        if article_id:
            NewsPipeline.fetch_article_content(article_id)
            NewsPipeline.translate_article(article_id)

        print("\n" + "=" * 50)
        print("流水线执行完成")
        print("=" * 50)
        return True


def main():
    """命令行入口。"""
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python -m src.pipeline crawl          # 爬取新闻")
        print("  python -m src.pipeline fetch <id>    # 获取文章内容")
        print("  python -m src.pipeline translate <id> # 翻译文章")
        print("  python -m src.pipeline run            # 运行完整流水线")
        return

    action = sys.argv[1]
    pipeline = NewsPipeline()

    if action == "crawl":
        asyncio.run(pipeline.crawl_and_save())
    elif action == "fetch":
        article_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        pipeline.fetch_article_content(article_id)
    elif action == "translate":
        article_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        pipeline.translate_article(article_id)
    elif action == "run":
        pipeline.run_full_pipeline()
    else:
        print(f"未知操作: {action}")


if __name__ == "__main__":
    main()

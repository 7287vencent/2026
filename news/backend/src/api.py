"""Flask API 后端服务。

提供新闻列表、搜索、爬取、翻译等API接口。
"""
import asyncio
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
from src.crawler import BBCCrawler
from src.article_fetcher import ArticleFetcher
from src.ai.translator import Translator
from src.ai.polisher import Polisher

app = Flask(__name__)
CORS(app)


@app.route("/api/articles", methods=["GET"])
def get_articles():
    """获取新闻列表，支持搜索"""
    keyword = request.args.get("keyword", "")
    status = request.args.get("status", "")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))

    if keyword:
        articles = db.search_articles(keyword)
    else:
        articles = db.get_all_articles(status=status if status else None)

    start = (page - 1) * page_size
    end = start + page_size
    total = len(articles)

    return jsonify({
        "code": 0,
        "data": {
            "list": articles[start:end],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    })


@app.route("/api/articles/<int:article_id>", methods=["GET"])
def get_article(article_id):
    """获取单篇文章详情"""
    article = db.get_article_by_id(article_id)
    if not article:
        return jsonify({"code": 1, "message": "文章不存在"}), 404
    return jsonify({"code": 0, "data": article})


@app.route("/api/crawl", methods=["POST"])
def crawl_news():
    """爬取最新新闻（自动翻译标题）"""
    async def _crawl():
        crawler = BBCCrawler()
        articles = await crawler.fetch_most_read()
        return articles

    articles = asyncio.run(_crawl())
    
    # 翻译标题
    translator = Translator()
    for article in articles:
        title_zh = translator.translate(article["title_en"])
        article["title_zh"] = title_zh
    
    # 保存到数据库
    count = db.add_articles_batch(articles)
    
    return jsonify({
        "code": 0,
        "message": f"成功爬取 {count} 条新闻",
        "data": {"count": count}
    })


@app.route("/api/articles/<int:article_id>/fetch", methods=["POST"])
def fetch_article_content(article_id):
    """获取文章内容"""
    article = db.get_article_by_id(article_id)
    if not article:
        return jsonify({"code": 1, "message": "文章不存在"}), 404

    async def _fetch():
        fetcher = ArticleFetcher()
        return await fetcher.fetch_content(article["url"])

    result = asyncio.run(_fetch())
    if result:
        db.update_article(article_id, result)
        updated_article = db.get_article_by_id(article_id)
        return jsonify({"code": 0, "message": "获取成功", "data": updated_article})
    return jsonify({"code": 1, "message": "获取失败"}), 500


@app.route("/api/articles/<int:article_id>/translate", methods=["POST"])
def translate_article(article_id):
    """翻译文章"""
    article = db.get_article_by_id(article_id)
    if not article:
        return jsonify({"code": 1, "message": "文章不存在"}), 404

    translator = Translator()

    title_zh = translator.translate(article["title_en"])
    content_zh = ""
    if article.get("content_en"):
        content_zh = translator.translate(article["content_en"])

    db.update_article(article_id, {
        "title_zh": title_zh,
        "content_zh": content_zh,
        "status": "translated",
        "translated_at": datetime.now().isoformat()
    })

    updated_article = db.get_article_by_id(article_id)
    return jsonify({"code": 0, "message": "翻译成功", "data": updated_article})


@app.route("/api/articles/<int:article_id>/fetch-and-translate", methods=["POST"])
def fetch_and_translate(article_id):
    """获取原文并翻译（或仅翻译已获取的内容）"""
    article = db.get_article_by_id(article_id)
    if not article:
        return jsonify({"code": 1, "message": "文章不存在"}), 404

    result = None
    
    # 如果没有英文内容，先获取
    if not article.get("content_en"):
        async def _fetch():
            fetcher = ArticleFetcher()
            return await fetcher.fetch_content(article["url"])

        result = asyncio.run(_fetch())
        if not result:
            return jsonify({"code": 1, "message": "获取内容失败"}), 500

        db.update_article(article_id, result)
    else:
        result = {"content_en": article.get("content_en")}

    # 翻译标题和内容
    translator = Translator()
    title_zh = translator.translate(article["title_en"])
    content_zh = ""
    if result.get("content_en"):
        content_zh = translator.translate(result["content_en"])

    db.update_article(article_id, {
        "title_zh": title_zh,
        "content_zh": content_zh,
        "status": "translated",
        "translated_at": datetime.now().isoformat()
    })

    updated_article = db.get_article_by_id(article_id)
    return jsonify({"code": 0, "message": "处理成功", "data": updated_article})


@app.route("/api/articles/<int:article_id>/polish", methods=["POST"])
def polish_article(article_id):
    """AI润色文章"""
    article = db.get_article_by_id(article_id)
    if not article:
        return jsonify({"code": 1, "message": "文章不存在"}), 404

    if not article.get("content_zh"):
        return jsonify({"code": 1, "message": "请先翻译文章内容"}), 400

    print(f"开始润色文章 {article_id}，内容长度: {len(article['content_zh'])}")
    
    polisher = Polisher()
    content_polished = polisher.polish(article["content_zh"])
    
    print(f"润色完成，结果长度: {len(content_polished) if content_polished else 0}")

    if not content_polished:
        return jsonify({"code": 1, "message": "润色失败"}), 500

    db.update_article(article_id, {
        "content_polished": content_polished,
        "polished_at": datetime.now().isoformat(),
        "status": "polished"
    })
    print(f"已保存到数据库")

    # 返回更新后的完整文章数据
    updated_article = db.get_article_by_id(article_id)
    print(f"读取返回数据，content_polished 长度: {len(updated_article.get('content_polished', '')) if updated_article else 0}")
    
    return jsonify({"code": 0, "message": "润色成功", "data": updated_article})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

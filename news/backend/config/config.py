"""配置模块。

集中管理项目配置，包括数据库、爬虫、日志等配置项。
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据库配置
DATABASE_CONFIG = {
    "path": BASE_DIR / "db" / "news.db"
}

# 爬虫配置
CRAWLER_CONFIG = {
    "bbc_url": "https://www.bbc.com/news",
    "headers": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    },
    "timeout": 30,
    "retry_times": 3,
    "retry_delay": 2,
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": BASE_DIR / "logs" / "app.log"
}

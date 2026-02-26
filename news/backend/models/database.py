"""数据库模块。

负责SQLite数据库的初始化和CRUD操作，支持文章的增删改查。
"""
import sqlite3
from datetime import datetime
from typing import List, Optional
from contextlib import contextmanager

from config.config import DATABASE_CONFIG


class Database:
    """数据库操作类，提供文章数据的持久化能力。"""

    def __init__(self, db_path: Optional[str] = None):
        """初始化数据库连接并创建表结构。

        Args:
            db_path: 数据库文件路径，默认为config中配置的路径。
        """
        self.db_path = db_path or DATABASE_CONFIG["path"]
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接。

        Returns:
            sqlite3.Connection: 数据库连接对象。
        """
        return sqlite3.connect(self.db_path)

    @contextmanager
    def _cursor(self):
        """获取数据库游标的上下文管理器。

        自动处理事务提交和异常回滚，确保数据一致性。
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            yield cursor
            conn.commit()  # 提交事务
        except Exception as e:
            conn.rollback()  # 发生异常时回滚
            raise e
        finally:
            conn.close()

    def _init_db(self) -> None:
        """初始化数据库，创建文章表和索引。"""
        with self._cursor() as cursor:
            # 创建文章表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title_en TEXT NOT NULL,        -- 英文标题
                    title_zh TEXT,                 -- 中文标题
                    summary_en TEXT,                -- 英文摘要
                    summary_zh TEXT,                -- 中文摘要
                    content_en TEXT,                -- 英文正文
                    content_zh TEXT,                -- 中文正文
                    content_polished TEXT,          -- AI润色后的中文正文
                    url TEXT NOT NULL UNIQUE,       -- 文章链接（唯一）
                    image_url TEXT,                 -- 图片链接
                    published_at TEXT,              -- 发布时间
                    crawled_at TEXT NOT NULL,       -- 爬取时间
                    translated_at TEXT,            -- 翻译时间
                    polished_at TEXT,               -- AI润色时间
                    status TEXT DEFAULT 'crawled',   -- 状态：crawled/translated/polished
                    created_at TEXT NOT NULL,       -- 创建时间
                    updated_at TEXT NOT NULL        -- 更新时间
                )
            """)
            
            # 为已存在的数据库添加新字段（迁移）
            try:
                cursor.execute("ALTER TABLE articles ADD COLUMN content_polished TEXT")
            except sqlite3.OperationalError:
                pass  # 字段已存在
                
            try:
                cursor.execute("ALTER TABLE articles ADD COLUMN translated_at TEXT")
            except sqlite3.OperationalError:
                pass  # 字段已存在
                
            try:
                cursor.execute("ALTER TABLE articles ADD COLUMN polished_at TEXT")
            except sqlite3.OperationalError:
                pass  # 字段已存在
                
            # URL索引，加速去重查询
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)
            """)
            # 状态索引，加速状态筛选
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status)
            """)

    def article_exists(self, url: str) -> bool:
        """检查文章是否已存在（根据URL去重）。

        Args:
            url: 文章链接。

        Returns:
            bool: 存在返回True，否则返回False。
        """
        with self._cursor() as cursor:
            cursor.execute("SELECT 1 FROM articles WHERE url = ?", (url,))
            return cursor.fetchone() is not None

    def add_article(self, article: dict) -> int:
        """添加单篇文章到数据库。

        Args:
            article: 包含文章数据的字典，必须包含title_en和url字段。

        Returns:
            int: 新插入记录的ID。
        """
        now = datetime.now().isoformat()
        with self._cursor() as cursor:
            cursor.execute("""
                INSERT INTO articles (
                    title_en, url, image_url, published_at, crawled_at,
                    status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article["title_en"],
                article["url"],
                article.get("image_url"),
                article.get("published_at"),
                article.get("crawled_at", now),
                "crawled",
                now,
                now
            ))
            return cursor.lastrowid

    def add_articles_batch(self, articles: List[dict]) -> int:
        """批量添加文章（自动去重）。

        Args:
            articles: 文章列表，每条包含title_en和url等字段。

        Returns:
            int: 实际新增的文章数量（去重后）。
        """
        count = 0
        now = datetime.now().isoformat()
        with self._cursor() as cursor:
            for article in articles:
                if not self.article_exists(article["url"]):
                    cursor.execute("""
                        INSERT INTO articles (
                            title_en, title_zh, url, image_url, published_at, crawled_at,
                            status, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        article["title_en"],
                        article.get("title_zh", ""),
                        article["url"],
                        article.get("image_url"),
                        article.get("published_at"),
                        article.get("crawled_at", now),
                        "crawled",
                        now,
                        now
                    ))
                    count += 1
        return count

    def get_all_articles(
        self,
        status: Optional[str] = None
    ) -> List[dict]:
        """获取所有文章。

        Args:
            status: 可选，按状态筛选（如'crawled'、'translated'）。

        Returns:
            List[dict]: 文章列表，按爬取时间倒序排列。
        """
        with self._cursor() as cursor:
            if status:
                cursor.execute(
                    "SELECT * FROM articles WHERE status = ? ORDER BY crawled_at DESC",
                    (status,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM articles ORDER BY crawled_at DESC"
                )
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def search_articles(self, keyword: str) -> List[dict]:
        """搜索文章（按标题）。

        Args:
            keyword: 搜索关键词。

        Returns:
            List[dict]: 匹配的文章列表。
        """
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT * FROM articles WHERE title_en LIKE ? OR title_zh LIKE ? ORDER BY crawled_at DESC",
                (f"%{keyword}%", f"%{keyword}%")
            )
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_article_by_id(self, article_id: int) -> Optional[dict]:
        """根据ID获取单篇文章。

        Args:
            article_id: 文章ID。

        Returns:
            Optional[dict]: 文章数据，不存在返回None。
        """
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT * FROM articles WHERE id = ?",
                (article_id,)
            )
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None

    def update_article(self, article_id: int, data: dict) -> bool:
        """更新文章内容。

        Args:
            article_id: 文章ID。
            data: 要更新的字段和值。

        Returns:
            bool: 更新成功返回True，否则返回False。
        """
        data["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        values = list(data.values()) + [article_id]
        with self._cursor() as cursor:
            cursor.execute(
                f"UPDATE articles SET {set_clause} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0

    def delete_article(self, article_id: int) -> bool:
        """删除文章。

        Args:
            article_id: 文章ID。

        Returns:
            bool: 删除成功返回True，否则返回False。
        """
        with self._cursor() as cursor:
            cursor.execute(
                "DELETE FROM articles WHERE id = ?",
                (article_id,)
            )
            return cursor.rowcount > 0

    def get_articles_count(self, status: Optional[str] = None) -> int:
        """获取文章总数。

        Args:
            status: 可选，按状态筛选。

        Returns:
            int: 文章总数。
        """
        with self._cursor() as cursor:
            if status:
                cursor.execute(
                    "SELECT COUNT(*) FROM articles WHERE status = ?",
                    (status,)
                )
            else:
                cursor.execute("SELECT COUNT(*) FROM articles")
            return cursor.fetchone()[0]


# 创建全局数据库实例
db = Database()

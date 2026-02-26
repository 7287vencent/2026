"""BBC新闻爬虫模块。

使用Playwright爬取BBC新闻首页的Most Read区域。
只负责数据爬取，不涉及数据库操作。
"""
import asyncio
from datetime import datetime
from typing import List, Dict

from playwright.async_api import async_playwright


class BBCCrawler:
    """BBC新闻爬虫类，负责爬取BBC首页的Most Read新闻。"""

    URL = "https://www.bbc.com/news"

    async def fetch_most_read(self) -> List[Dict]:
        """获取BBC首页Most Read区域的新闻列表。

        使用Playwright模拟浏览器访问BBC新闻首页，解析HTML获取热门新闻数据。

        Returns:
            List[Dict]: 新闻列表，每条包含title_en(英文标题)、url(链接)、crawled_at(爬取时间)。
        """
        articles: List[Dict] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(
                self.URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            await page.wait_for_timeout(5000)

            most_read_section = None
            selectors = [
                'section[data-testid="illinois-section-outer-10"]',
                'section[data-analytics_group_name="Most read"]',
                '[data-analytics_group_name="Most read"]',
            ]

            for selector in selectors:
                section = await page.query_selector(selector)
                if section:
                    most_read_section = section
                    print(f"找到 Most Read 区域: {selector}")
                    break

            if not most_read_section:
                print("未找到 Most Read 区域")
                await browser.close()
                return []

            article_links = await most_read_section.query_selector_all('a')

            for link in article_links:
                href = await link.get_attribute("href")
                if not href or "/news/" not in href:
                    continue

                full_url = "https://www.bbc.com" + href if href.startswith("/") else href

                h2_elem = await link.query_selector("h2")
                title = await h2_elem.inner_text() if h2_elem else ""

                if title and full_url:
                    articles.append({
                        "title_en": title,
                        "url": full_url,
                        "crawled_at": datetime.now().isoformat()
                    })

            await browser.close()

        return articles


async def run() -> List[Dict]:
    """运行爬虫，返回爬取的新闻列表。"""
    crawler = BBCCrawler()
    articles = await crawler.fetch_most_read()
    print(f"获取到 {len(articles)} 条新闻")
    return articles


if __name__ == "__main__":
    asyncio.run(run())

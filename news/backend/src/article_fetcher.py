"""文章内容获取模块。

通过Playwright访问BBC文章链接，获取完整的文章内容。
只负责数据爬取，不涉及数据库操作。
"""
import asyncio
from datetime import datetime
from typing import Dict, Optional, List

from playwright.async_api import async_playwright


class ArticleFetcher:
    """文章内容获取器，负责获取单篇文章的详细内容。"""

    async def fetch_content(self, url: str) -> Optional[Dict]:
        """获取单篇文章的详细内容。

        使用Playwright访问文章URL，解析HTML获取文章标题、正文、图片等。

        Args:
            url: 文章链接。

        Returns:
            Optional[Dict]: 包含文章内容的字典，失败返回None。
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(3000)

                content_parts: List[str] = []
                image_url = ""

                content_blocks = await page.query_selector_all(
                    '[data-component="text-block"], [data-component="image-block"]'
                )

                published_at = ""
                time_elem = await page.query_selector('[data-component="byline-block"] time')
                if time_elem:
                    published_at = await time_elem.get_attribute('datetime') or ""

                for block in content_blocks:
                    if await block.get_attribute('data-component') == 'text-block':
                        text = await block.inner_text()
                        if text:
                            content_parts.append(text)
                        continue

                    if await block.get_attribute('data-component') == 'image-block':
                        img_elem = await block.query_selector('img')
                        if img_elem and not image_url:
                            image_url = await img_elem.get_attribute("src") or ""

                content = "\n\n".join(content_parts)

                await browser.close()

                return {
                    "content_en": content,
                    "image_url": image_url,
                    "published_at": published_at,
                }

            except Exception as e:
                print(f"获取文章内容失败: {e}")
                await browser.close()
                return None


async def fetch_article(url: str) -> Optional[Dict]:
    """获取单篇文章的内容（供命令行调用）。"""
    fetcher = ArticleFetcher()
    result = await fetcher.fetch_content(url)
    if result:
        print(f"获取成功，正文长度: {len(result['content_en'])} 字符")
    else:
        print("获取失败")
    return result


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.bbc.com/news/articles/cx2lp7xwql4o"
    asyncio.run(fetch_article(url))

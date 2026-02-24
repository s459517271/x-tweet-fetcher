#!/usr/bin/env python3
"""
Sogou WeChat Search - Search WeChat articles via Sogou.
Part of x-tweet-fetcher.

Usage:
  python3 sogou_wechat.py --keyword "AI" --limit 5
  python3 sogou_wechat.py --keyword "人工智能" --json
"""

import requests
from urllib.parse import quote
import re
import json
import argparse
import sys
import html as html_lib


def sogou_wechat_search(keyword, max_results=10):
    """搜索搜狗微信公众号文章"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    url = f'https://weixin.sogou.com/weixin?type=2&query={quote(keyword)}'
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        text = response.text
        
        results = []
        
        # 找到所有 txt-box 块
        blocks = re.findall(r'<div class="txt-box">(.*?)</div>\s*</div>', text, re.DOTALL)
        
        for block in blocks[:max_results]:
            # 标题和链接
            title_match = re.search(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', block, re.DOTALL)
            if not title_match:
                continue
            
            article_url = title_match.group(1).replace('&amp;', '&')
            # 清理标题中的 HTML 标签
            raw_title = title_match.group(2)
            title = re.sub(r'<[^>]+>', '', raw_title).strip()
            title = html_lib.unescape(title)
            
            # 作者/公众号
            author_match = re.search(r'<a[^>]*class="account"[^>]*>(.*?)</a>', block, re.DOTALL)
            author = re.sub(r'<[^>]+>', '', author_match.group(1)).strip() if author_match else ''
            
            # 摘要
            snippet_match = re.search(r'<p class="txt-info">(.*?)</p>', block, re.DOTALL)
            snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip() if snippet_match else ''
            snippet = html_lib.unescape(snippet)
            
            # 日期 (timestamp)
            date_match = re.search(r"document\.write\(timeConvert\('(\d+)'\)\)", block)
            if date_match:
                from datetime import datetime
                ts = int(date_match.group(1))
                date = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            else:
                date = ''
            
            # 完整链接
            if article_url.startswith('/link'):
                article_url = 'https://weixin.sogou.com' + article_url
            
            results.append({
                'title': title,
                'url': article_url,
                'author': author,
                'snippet': snippet,
                'date': date
            })
            
        return results
        
    except Exception as e:
        print(f"搜索失败: {e}", file=sys.stderr)
        return []


def main():
    parser = argparse.ArgumentParser(description="Search WeChat articles via Sogou")
    parser.add_argument("--keyword", "-k", required=True, help="Search keyword")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON")
    args = parser.parse_args()

    results = sogou_wechat_search(args.keyword, args.limit)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print("未找到结果")
        for i, article in enumerate(results, 1):
            print(f"{i}. {article['title']}")
            if article['author']:
                print(f"   公众号: {article['author']}")
            if article['date']:
                print(f"   日期: {article['date']}")
            if article['snippet']:
                print(f"   摘要: {article['snippet'][:80]}...")
            print(f"   链接: {article['url'][:80]}...")
            print()

    sys.exit(0 if results else 1)


if __name__ == "__main__":
    main()

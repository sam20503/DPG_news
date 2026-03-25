#!/usr/bin/env python3
"""
動物新聞搜尋器 - Animal News Finder
搜尋關於動物、動物福利、動物研究的新聞，以中文輸出結果。
"""

import argparse
import json
import sys
import urllib.parse
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

# 搜尋關鍵字（中英文）
KEYWORD_CATEGORIES = {
    "動物一般": [
        "動物新聞", "野生動物", "寵物", "瀕危物種",
        "animal news", "wildlife", "endangered species",
    ],
    "動物福利": [
        "動物福利", "動物保護", "動物權益", "動物收容所", "流浪動物",
        "animal welfare", "animal rights", "animal rescue",
    ],
    "動物研究": [
        "動物研究", "動物行為", "動物科學", "生態研究", "動物醫學",
        "animal research", "animal science", "zoology",
    ],
}


def search_google_news(query, num_results=5):
    """透過 Google News RSS 搜尋新聞"""
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item", limit=num_results)

        results = []
        for item in items:
            title = item.title.text if item.title else "無標題"
            link = item.link.text if item.link else ""
            pub_date = item.pubDate.text if item.pubDate else "未知日期"
            source = item.source.text if item.source else "未知來源"

            results.append({
                "標題": title,
                "來源": source,
                "發布日期": pub_date,
                "連結": link,
            })
        return results
    except requests.RequestException as e:
        print(f"  ⚠ 搜尋 '{query}' 時發生錯誤: {e}")
        return []


def search_bing_news(query, num_results=5):
    """透過 Bing News RSS 搜尋新聞（備用來源）"""
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.bing.com/news/search?q={encoded_query}&format=rss&mkt=zh-TW"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item", limit=num_results)

        results = []
        for item in items:
            title = item.title.text if item.title else "無標題"
            link = item.link.text if item.link else ""
            pub_date = item.pubDate.text if item.pubDate else "未知日期"
            description_tag = item.description
            description = description_tag.text if description_tag else ""

            results.append({
                "標題": title,
                "來源": "Bing News",
                "發布日期": pub_date,
                "連結": link,
                "摘要": description[:150] + "..." if len(description) > 150 else description,
            })
        return results
    except requests.RequestException as e:
        print(f"  ⚠ 搜尋 '{query}' 時發生錯誤: {e}")
        return []


def deduplicate_results(results):
    """移除重複的新聞結果"""
    seen_titles = set()
    unique = []
    for item in results:
        title = item["標題"]
        if title not in seen_titles:
            seen_titles.add(title)
            unique.append(item)
    return unique


def display_results(category, results):
    """以中文格式顯示搜尋結果"""
    print(f"\n{'='*60}")
    print(f"📂 分類：{category}")
    print(f"{'='*60}")

    if not results:
        print("  找不到相關新聞。")
        return

    for i, item in enumerate(results, 1):
        print(f"\n  📰 [{i}] {item['標題']}")
        print(f"     來源：{item['來源']}")
        print(f"     日期：{item['發布日期']}")
        if item.get("摘要"):
            print(f"     摘要：{item['摘要']}")
        print(f"     🔗 {item['連結']}")


def save_results_json(all_results, filename="animal_news_results.json"):
    """將結果儲存為 JSON 檔案"""
    output = {
        "搜尋時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "結果": all_results,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n💾 結果已儲存至：{filename}")


def run_search(categories=None, num_results=5, save=False):
    """執行新聞搜尋"""
    if categories is None:
        categories = list(KEYWORD_CATEGORIES.keys())

    print("🔍 動物新聞搜尋器")
    print(f"📅 搜尋時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 搜尋分類：{', '.join(categories)}")

    all_results = {}

    for category in categories:
        if category not in KEYWORD_CATEGORIES:
            print(f"\n⚠ 未知分類：{category}，跳過。")
            continue

        keywords = KEYWORD_CATEGORIES[category]
        category_results = []

        for keyword in keywords:
            print(f"\n  🔎 正在搜尋：{keyword} ...")
            results = search_google_news(keyword, num_results=3)
            if not results:
                results = search_bing_news(keyword, num_results=3)
            category_results.extend(results)

        category_results = deduplicate_results(category_results)
        category_results = category_results[:num_results]
        all_results[category] = category_results
        display_results(category, category_results)

    if save:
        save_results_json(all_results)

    # 統計摘要
    total = sum(len(v) for v in all_results.values())
    print(f"\n{'='*60}")
    print(f"📊 搜尋完成！共找到 {total} 則不重複新聞。")
    print(f"{'='*60}")

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="動物新聞搜尋器 - 搜尋動物、動物福利、動物研究相關新聞"
    )
    parser.add_argument(
        "-c", "--category",
        nargs="+",
        choices=list(KEYWORD_CATEGORIES.keys()),
        default=None,
        help="選擇搜尋分類（預設：全部）",
    )
    parser.add_argument(
        "-n", "--num-results",
        type=int,
        default=10,
        help="每個分類顯示的新聞數量（預設：10）",
    )
    parser.add_argument(
        "-s", "--save",
        action="store_true",
        help="將結果儲存為 JSON 檔案",
    )
    parser.add_argument(
        "-k", "--keyword",
        type=str,
        default=None,
        help="自訂搜尋關鍵字",
    )

    args = parser.parse_args()

    if args.keyword:
        print(f"\n🔍 自訂搜尋：{args.keyword}")
        results = search_google_news(args.keyword, num_results=args.num_results)
        if not results:
            results = search_bing_news(args.keyword, num_results=args.num_results)
        display_results("自訂搜尋", results)
        if args.save:
            save_results_json({"自訂搜尋": results})
    else:
        run_search(
            categories=args.category,
            num_results=args.num_results,
            save=args.save,
        )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
動物新聞監測器 - Animal News Monitor
專為動保團體設計，監測五大動物類別的新聞：
伴侶動物、農場動物、實驗動物、展演動物、經濟動物

支援語言：英文（預設）、日文、韓文、中文
"""

import argparse
import json
import math
import sys
import urllib.parse
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# ============================================================
# 設定
# ============================================================
PAGE_SIZE = 10  # 每頁顯示筆數
DEFAULT_TOTAL = 50  # 預設每分類搜尋總筆數

# ============================================================
# 語言設定
# ============================================================
LANGUAGES = {
    "en": {
        "name": "English（英文）",
        "google_params": "hl=en&gl=US&ceid=US:en",
        "bing_params": "mkt=en-US",
    },
    "ja": {
        "name": "日本語（日文）",
        "google_params": "hl=ja&gl=JP&ceid=JP:ja",
        "bing_params": "mkt=ja-JP",
    },
    "ko": {
        "name": "한국어（韓文）",
        "google_params": "hl=ko&gl=KR&ceid=KR:ko",
        "bing_params": "mkt=ko-KR",
    },
    "zh": {
        "name": "中文（繁體）",
        "google_params": "hl=zh-TW&gl=TW&ceid=TW:zh-Hant",
        "bing_params": "mkt=zh-TW",
    },
}

# ============================================================
# 五大動物類別關鍵字（依語言分組）
# ============================================================
KEYWORD_CATEGORIES = {
    "伴侶動物": {
        "en": [
            "companion animal news",
            "pet welfare legislation",
            "stray dog cat rescue",
            "animal shelter adoption",
            "pet abuse cruelty case",
            "dog cat abandonment news",
            "TNR stray animal policy",
        ],
        "ja": [
            "ペット ニュース 動物愛護",
            "犬猫 殺処分 保護",
            "コンパニオンアニマル 福祉",
            "野良猫 TNR 地域猫",
            "ペット 虐待 事件",
            "動物愛護法 改正",
        ],
        "ko": [
            "반려동물 뉴스",
            "유기동물 보호",
            "동물학대 사건",
            "반려동물 복지 정책",
            "길고양이 TNR",
            "동물보호법",
        ],
        "zh": [
            "伴侶動物 新聞",
            "流浪動物 收容 救援",
            "寵物 虐待 案件",
            "動物保護法 修法",
            "TNR 流浪貓狗",
            "動物收容所 領養",
        ],
    },
    "農場動物": {
        "en": [
            "farm animal welfare news",
            "factory farming cruelty",
            "cage-free eggs legislation",
            "pig gestation crate ban",
            "poultry chicken welfare",
            "livestock slaughter regulations",
            "dairy cow welfare standards",
            "farm animal abuse investigation",
        ],
        "ja": [
            "畜産動物 アニマルウェルフェア",
            "養鶏 バタリーケージ 廃止",
            "豚 妊娠ストール 禁止",
            "畜産 動物福祉 基準",
            "と畜 動物虐待",
            "アニマルウェルフェア 畜産 ニュース",
        ],
        "ko": [
            "농장동물 복지 뉴스",
            "공장식 축산 동물학대",
            "산란계 케이지프리",
            "축산 동물복지 인증",
            "가축 도축 규정",
            "동물복지 축산농장",
        ],
        "zh": [
            "農場動物 福利 新聞",
            "格子籠 蛋雞 廢除",
            "母豬 狹欄 禁止",
            "畜牧 動物福利 標準",
            "屠宰 人道 規範",
            "工廠化農場 虐待",
        ],
    },
    "實驗動物": {
        "en": [
            "animal testing news",
            "laboratory animal welfare",
            "animal experiment alternatives",
            "3Rs replacement reduction refinement",
            "cosmetic animal testing ban",
            "primate research controversy",
            "FDA animal testing policy",
            "lab animal rescue release",
        ],
        "ja": [
            "動物実験 ニュース",
            "実験動物 代替法",
            "動物実験 廃止 3R",
            "化粧品 動物実験 禁止",
            "霊長類 実験 批判",
            "実験動物 福祉",
        ],
        "ko": [
            "동물실험 뉴스",
            "실험동물 대체법",
            "동물실험 금지 화장품",
            "실험동물 복지",
            "동물실험 3R 원칙",
            "실험동물 해방",
        ],
        "zh": [
            "動物實驗 新聞",
            "實驗動物 替代方案",
            "化妝品 動物實驗 禁止",
            "3R原則 實驗動物",
            "靈長類 實驗 爭議",
            "實驗動物 福利",
        ],
    },
    "展演動物": {
        "en": [
            "zoo animal welfare news",
            "aquarium dolphin captivity",
            "circus animal ban",
            "marine park orca whale welfare",
            "animal performance entertainment ban",
            "captive wildlife welfare",
            "zoo accreditation animal abuse",
            "elephant ride tourism ban",
        ],
        "ja": [
            "動物園 動物福祉 ニュース",
            "水族館 イルカ 飼育 問題",
            "サーカス 動物 禁止",
            "動物ショー 廃止",
            "展示動物 福祉 基準",
            "象 ライド 観光 禁止",
        ],
        "ko": [
            "동물원 동물복지 뉴스",
            "수족관 돌고래 사육",
            "서커스 동물 금지",
            "동물 공연 전시 폐지",
            "전시동물 복지",
            "동물원 학대 논란",
        ],
        "zh": [
            "動物園 動物福利 新聞",
            "水族館 海豚 圈養",
            "馬戲團 動物 禁令",
            "動物展演 表演 廢除",
            "展演動物 福利 標準",
            "騎象 觀光 禁止",
        ],
    },
    "經濟動物": {
        "en": [
            "fur farming ban news",
            "wildlife trade illegal trafficking",
            "ivory trade ban enforcement",
            "shark fin trade ban",
            "bear bile farming ban",
            "animal skin leather industry welfare",
            "fishing bycatch marine animal",
            "bushmeat wildlife poaching",
            "foie gras ban news",
        ],
        "ja": [
            "毛皮 ファーファーミング 禁止",
            "野生動物 取引 密売",
            "象牙 取引 禁止",
            "フカヒレ 取引 規制",
            "熊胆 養殖 廃止",
            "フォアグラ 禁止 ニュース",
            "混獲 海洋動物 保護",
        ],
        "ko": [
            "모피 농장 금지 뉴스",
            "야생동물 거래 밀매",
            "상아 거래 금지",
            "상어 지느러미 규제",
            "곰 담즙 농장 폐지",
            "푸아그라 금지",
            "혼획 해양동물 보호",
        ],
        "zh": [
            "皮草 養殖 禁令 新聞",
            "野生動物 貿易 走私",
            "象牙 交易 禁令",
            "魚翅 交易 禁止",
            "熊膽 養殖 廢除",
            "鵝肝醬 禁令",
            "混獲 海洋動物 保護",
        ],
    },
}

def _set_page_size(size):
    global PAGE_SIZE
    PAGE_SIZE = size


CATEGORY_DESCRIPTIONS = {
    "伴侶動物": "Companion Animals — 寵物、流浪動物、收容所、TNR、虐待案件",
    "農場動物": "Farm Animals — 畜牧業、格子籠、狹欄、屠宰、動物福利認證",
    "實驗動物": "Laboratory Animals — 動物實驗、替代方案、3R原則、實驗禁令",
    "展演動物": "Performing/Exhibition Animals — 動物園、水族館、馬戲團、動物表演",
    "經濟動物": "Economic Animals — 皮草、野生動物貿易、象牙、魚翅、熊膽",
}


def prompt_language_selection():
    """互動式語言選擇"""
    print("\n" + "=" * 60)
    print("🌐 動物新聞監測器 — Animal News Monitor")
    print("   專為動保團體設計的新聞監測工具")
    print("=" * 60)
    print("\n請選擇要搜尋的新聞語言 / Select news language:\n")
    print("  [1] 🇺🇸 English（英文）        ← 預設 / Default")
    print("  [2] 🇯🇵 日本語（日文）")
    print("  [3] 🇰🇷 한국어（韓文）")
    print("  [4] 🇹🇼 中文（繁體中文）")
    print("  [5] 🌍 全部語言（All languages）")
    print()

    choice = input("請輸入選項 (1-5) [預設: 1]: ").strip()

    lang_map = {
        "1": ["en"],
        "2": ["ja"],
        "3": ["ko"],
        "4": ["zh"],
        "5": ["en", "ja", "ko", "zh"],
        "": ["en"],
    }

    selected = lang_map.get(choice, ["en"])
    names = [LANGUAGES[lang]["name"] for lang in selected]
    print(f"\n✅ 已選擇：{', '.join(names)}\n")
    return selected


def prompt_category_selection():
    """互動式類別選擇"""
    print("請選擇要監測的動物類別 / Select animal categories:\n")
    categories = list(KEYWORD_CATEGORIES.keys())
    for i, cat in enumerate(categories, 1):
        print(f"  [{i}] {cat} — {CATEGORY_DESCRIPTIONS[cat]}")
    print(f"  [6] 🔍 全部類別（All categories）")
    print()

    choice = input("請輸入選項，可多選以逗號分隔 (例: 1,2,4) [預設: 6]: ").strip()

    if not choice or choice == "6":
        return categories

    selected = []
    for c in choice.split(","):
        c = c.strip()
        if c.isdigit() and 1 <= int(c) <= 5:
            selected.append(categories[int(c) - 1])

    if not selected:
        return categories

    print(f"\n✅ 已選擇：{', '.join(selected)}\n")
    return selected


def search_google_news(query, lang="en", num_results=10):
    """透過 Google News RSS 搜尋新聞"""
    encoded_query = urllib.parse.quote(query)
    params = LANGUAGES[lang]["google_params"]
    url = f"https://news.google.com/rss/search?q={encoded_query}&{params}"

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
                "語言": LANGUAGES[lang]["name"],
            })
        return results
    except requests.RequestException as e:
        print(f"  ⚠ 搜尋 '{query}' 時發生錯誤: {e}")
        return []


def search_bing_news(query, lang="en", num_results=10):
    """透過 Bing News RSS 搜尋新聞（備用來源）"""
    encoded_query = urllib.parse.quote(query)
    params = LANGUAGES[lang]["bing_params"]
    url = f"https://www.bing.com/news/search?q={encoded_query}&format=rss&{params}"

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
                "語言": LANGUAGES[lang]["name"],
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


def display_page(items, page, total_pages, category=""):
    """顯示單頁結果"""
    start = (page - 1) * PAGE_SIZE
    end = min(start + PAGE_SIZE, len(items))
    page_items = items[start:end]

    if category:
        print(f"\n{'='*70}")
        print(f"📂 分類：{category}")
        print(f"   {CATEGORY_DESCRIPTIONS.get(category, '')}")
        print(f"   共 {len(items)} 則新聞  |  第 {page}/{total_pages} 頁（每頁 {PAGE_SIZE} 則）")
        print(f"{'='*70}")

    if not page_items:
        print("  找不到相關新聞。")
        return

    for i, item in enumerate(page_items, start + 1):
        print(f"\n  📰 [{i}] {item['標題']}")
        print(f"     來源：{item['來源']}  |  語言：{item['語言']}")
        print(f"     日期：{item['發布日期']}")
        if item.get("摘要"):
            print(f"     摘要：{item['摘要']}")
        print(f"     🔗 {item['連結']}")


def paginate_results(items, category=""):
    """互動式分頁瀏覽"""
    if not items:
        print(f"\n{'='*70}")
        print(f"📂 分類：{category}")
        print(f"   {CATEGORY_DESCRIPTIONS.get(category, '')}")
        print(f"{'='*70}")
        print("  找不到相關新聞。")
        return

    total_pages = math.ceil(len(items) / PAGE_SIZE)
    current_page = 1

    while True:
        display_page(items, current_page, total_pages, category)

        # 顯示導覽選項
        print(f"\n{'─'*70}")
        nav_options = []
        if current_page > 1:
            nav_options.append("P: 上一頁")
        if current_page < total_pages:
            nav_options.append("N: 下一頁")
        nav_options.append(f"1-{total_pages}: 跳至指定頁")
        nav_options.append("Q: 離開此分類")
        print(f"  📄 第 {current_page}/{total_pages} 頁  |  {' | '.join(nav_options)}")

        if current_page >= total_pages and total_pages == 1:
            # 只有一頁，不需要分頁操作
            break

        try:
            choice = input("\n  請輸入選項: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if choice == "n" and current_page < total_pages:
            current_page += 1
        elif choice == "p" and current_page > 1:
            current_page -= 1
        elif choice == "q" or choice == "":
            break
        elif choice.isdigit():
            target = int(choice)
            if 1 <= target <= total_pages:
                current_page = target
            else:
                print(f"  ⚠ 頁碼需在 1-{total_pages} 之間")
        else:
            print("  ⚠ 無效選項，請重新輸入")


def save_results_json(all_results, languages, filename=None):
    """將結果儲存為 JSON 檔案"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"animal_news_{timestamp}.json"

    output = {
        "搜尋時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "搜尋語言": [LANGUAGES[lang]["name"] for lang in languages],
        "結果": all_results,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n💾 結果已儲存至：{filename}")
    return filename


def run_search(categories=None, languages=None, num_results=50, save=False):
    """執行新聞搜尋"""
    if categories is None:
        categories = list(KEYWORD_CATEGORIES.keys())
    if languages is None:
        languages = ["en"]

    # 計算每個關鍵字應抓取的數量（確保總數足夠）
    max_keywords = max(
        len(KEYWORD_CATEGORIES[cat].get(lang, []))
        for cat in categories if cat in KEYWORD_CATEGORIES
        for lang in languages
    ) or 1
    first_cat = categories[0] if categories else None
    total_keywords_per_cat = sum(
        len(KEYWORD_CATEGORIES[first_cat].get(lang, []))
        for lang in languages
    ) if first_cat and first_cat in KEYWORD_CATEGORIES else 1
    per_keyword = max(5, math.ceil(num_results / max(total_keywords_per_cat, 1)))

    print("\n" + "=" * 70)
    print("🔍 動物新聞監測器 — Animal News Monitor")
    print(f"📅 搜尋時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 搜尋語言：{', '.join(LANGUAGES[l]['name'] for l in languages)}")
    print(f"📋 搜尋類別：{', '.join(categories)}")
    print(f"📊 每分類目標：{num_results} 則（每頁 {PAGE_SIZE} 則）")
    print("=" * 70)

    all_results = {}

    for category in categories:
        if category not in KEYWORD_CATEGORIES:
            print(f"\n⚠ 未知分類：{category}，跳過。")
            continue

        category_results = []

        for lang in languages:
            keywords = KEYWORD_CATEGORIES[category].get(lang, [])
            for keyword in keywords:
                print(f"  🔎 [{LANGUAGES[lang]['name'][:2]}] 正在搜尋：{keyword} ...")
                results = search_google_news(keyword, lang=lang, num_results=per_keyword)
                if not results:
                    results = search_bing_news(keyword, lang=lang, num_results=per_keyword)
                category_results.extend(results)

        category_results = deduplicate_results(category_results)
        category_results = category_results[:num_results]
        all_results[category] = category_results

        # 使用分頁顯示
        paginate_results(category_results, category)

    if save:
        save_results_json(all_results, languages)

    # 統計摘要
    total = sum(len(v) for v in all_results.values())
    print(f"\n{'='*70}")
    print(f"📊 搜尋完成！共找到 {total} 則不重複新聞。")
    by_cat = "  ".join(f"{k}: {len(v)}則" for k, v in all_results.items())
    print(f"   {by_cat}")
    print(f"{'='*70}")

    # 搜尋後總覽操作
    if total > 0:
        post_search_menu(all_results, languages)

    return all_results


def post_search_menu(all_results, languages):
    """搜尋完成後的總覽選單"""
    categories = list(all_results.keys())

    while True:
        print(f"\n{'─'*70}")
        print("📋 操作選單：")
        for i, cat in enumerate(categories, 1):
            count = len(all_results[cat])
            print(f"  [{i}] 重新瀏覽 {cat}（{count} 則）")
        print(f"  [S] 儲存全部結果為 JSON")
        print(f"  [Q] 結束程式")

        try:
            choice = input("\n  請輸入選項: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if choice == "q" or choice == "":
            break
        elif choice == "s":
            save_results_json(all_results, languages)
        elif choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(categories):
                cat = categories[idx - 1]
                paginate_results(all_results[cat], cat)
            else:
                print(f"  ⚠ 請輸入 1-{len(categories)} 之間的數字")
        else:
            print("  ⚠ 無效選項")


def main():
    parser = argparse.ArgumentParser(
        description="動物新聞監測器 — 專為動保團體設計，監測五大動物類別新聞"
    )
    parser.add_argument(
        "-c", "--category",
        nargs="+",
        choices=list(KEYWORD_CATEGORIES.keys()),
        default=None,
        help="選擇搜尋分類（預設：全部）",
    )
    parser.add_argument(
        "-l", "--language",
        nargs="+",
        choices=list(LANGUAGES.keys()),
        default=None,
        help="選擇搜尋語言：en, ja, ko, zh（預設：互動選擇）",
    )
    parser.add_argument(
        "-n", "--num-results",
        type=int,
        default=DEFAULT_TOTAL,
        help=f"每個分類搜尋的新聞數量（預設：{DEFAULT_TOTAL}）",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=PAGE_SIZE,
        help=f"每頁顯示筆數（預設：{PAGE_SIZE}）",
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
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="略過互動式選單，使用預設值或命令列參數",
    )

    args = parser.parse_args()

    # 設定每頁筆數
    page_size = args.page_size
    _set_page_size(page_size)

    # 決定語言
    if args.language:
        languages = args.language
    elif args.no_interactive or args.keyword:
        languages = ["en"]
    else:
        languages = prompt_language_selection()

    # 自訂關鍵字搜尋
    if args.keyword:
        print(f"\n🔍 自訂搜尋：{args.keyword}")
        all_lang_results = []
        for lang in languages:
            results = search_google_news(args.keyword, lang=lang, num_results=args.num_results)
            if not results:
                results = search_bing_news(args.keyword, lang=lang, num_results=args.num_results)
            all_lang_results.extend(results)
        all_lang_results = deduplicate_results(all_lang_results)
        paginate_results(all_lang_results, "自訂搜尋")
        if args.save:
            save_results_json({"自訂搜尋": all_lang_results}, languages)
        return

    # 決定類別
    if args.category:
        categories = args.category
    elif args.no_interactive:
        categories = list(KEYWORD_CATEGORIES.keys())
    else:
        categories = prompt_category_selection()

    run_search(
        categories=categories,
        languages=languages,
        num_results=args.num_results,
        save=args.save,
    )


if __name__ == "__main__":
    main()

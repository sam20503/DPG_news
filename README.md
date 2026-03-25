# 動物新聞監測器 Animal News Monitor

專為**動保團體**設計的新聞監測工具，涵蓋五大動物類別，支援多語言搜尋。

## 五大動物類別

| 類別 | 說明 | 關鍵字範例 |
|------|------|-----------|
| 伴侶動物 | Companion Animals | 寵物福利、流浪動物、收容所、TNR、虐待案件 |
| 農場動物 | Farm Animals | 格子籠、母豬狹欄、屠宰規範、畜牧業福利 |
| 實驗動物 | Laboratory Animals | 動物實驗、替代方案、3R原則、實驗禁令 |
| 展演動物 | Performing/Exhibition Animals | 動物園、水族館、馬戲團、動物表演 |
| 經濟動物 | Economic Animals | 皮草、野生動物貿易、象牙、魚翅、熊膽 |

## 支援語言

| 優先順序 | 語言 | 說明 |
|---------|------|------|
| 1（預設）| 🇺🇸 English | 國際動保新聞主要來源 |
| 2 | 🇯🇵 日本語 | 亞洲動保政策參考 |
| 2 | 🇰🇷 한국어 | 亞洲動保政策參考 |
| 3 | 🇹🇼 中文 | 台灣及華語地區新聞 |

## 安裝

```bash
pip install -r requirements.txt
```

## 使用方式

```bash
# 互動模式（會詢問語言和類別）
python animal_news_finder.py

# 指定語言搜尋
python animal_news_finder.py -l en ja        # 英文 + 日文
python animal_news_finder.py -l ko           # 僅韓文
python animal_news_finder.py -l en ja ko zh  # 全部語言

# 指定類別
python animal_news_finder.py -c 農場動物 實驗動物

# 自訂關鍵字
python animal_news_finder.py -k "cage-free eggs"

# 儲存結果為 JSON
python animal_news_finder.py -s

# 非互動模式（使用預設值，適合排程）
python animal_news_finder.py --no-interactive -s

# 指定每分類顯示數量
python animal_news_finder.py -n 15
```

# 動物新聞搜尋器 Animal News Finder

搜尋關於**動物**、**動物福利**、**動物研究**的最新新聞，以中文輸出結果。

## 安裝

```bash
pip install -r requirements.txt
```

## 使用方式

```bash
# 搜尋所有分類
python animal_news_finder.py

# 只搜尋動物福利相關新聞
python animal_news_finder.py -c 動物福利

# 自訂關鍵字搜尋
python animal_news_finder.py -k "台灣黑熊保育"

# 儲存結果為 JSON
python animal_news_finder.py -s

# 指定每分類顯示數量
python animal_news_finder.py -n 15
```

## 搜尋分類

| 分類 | 關鍵字範例 |
|------|-----------|
| 動物一般 | 動物新聞、野生動物、寵物、瀕危物種 |
| 動物福利 | 動物福利、動物保護、動物權益、流浪動物 |
| 動物研究 | 動物研究、動物行為、生態研究、動物醫學 |

# 📈 股市技術分析完整教學

互動式技術分析教材，**台股 / 美股顏色習慣可一鍵切換**（紅漲綠跌 ↔ 綠漲紅跌），全部採用真實歷史資料，可輸出 PNG / PDF 分享。

## 特色

- **9 大模組**：K 線基礎 → 趨勢/支撐壓力 → 反轉與整理型態 → 均線系統 → 動能指標（MACD/RSI/KD/威廉）→ 通道乖離（布林/BIAS）→ 量能（Volume/OBV）→ **籌碼面（三大法人/融資券/外資持股）** → 多指標綜合看盤
- **真實資料**：台積電 2330、加權指數 ^TWII、NVIDIA、Apple（Yahoo Finance）＋ 台股籌碼（FinMind）
- **互動演練**：均線天數、MACD/RSI/KD/布林 參數可拖曳即時重算；重要指標可切換台股 / 美股對照
- **誠實標註**：指標訊號為程式實際計算；型態示意圖為理想化繪製，另附真實案例對照
- **離線可用**：函式庫已內含，雙擊 `index.html` 即可開啟，無需網路或安裝

## 更新資料

```bash
python3 fetch_cases.py   # 重抓最新股價與籌碼，產生 cases.js
```

## 技術

純靜態 HTML + [ECharts](https://echarts.apache.org/) + [html2canvas](https://html2canvas.hertzen.com/)。無後端、無追蹤。

---
教學用途，非投資建議。

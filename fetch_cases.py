#!/opt/homebrew/bin/python3.13
"""抓取真實個股/指數日線 OHLC（Yahoo Finance）並烘焙成 cases.js 供技術分析教學網頁離線使用。一次性建置工具，非排程。"""
import json, sys, time, urllib.request, urllib.error

# (key, yahoo_symbol, display_name, market, range)
TICKERS = [
    ("2330", "2330.TW", "台積電 2330", "tw", "5y"),
    ("TWII", "^TWII",   "加權指數 ^TWII", "tw", "10y"),
    ("NVDA", "NVDA",    "NVIDIA (NVDA)", "us", "5y"),
    ("AAPL", "AAPL",    "Apple (AAPL)",  "us", "5y"),
]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"

def fetch(symbol, rng):
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/"
           f"{urllib.parse.quote(symbol)}?interval=1d&range={rng}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    res = d["chart"]["result"][0]
    ts = res["timestamp"]
    q = res["indicators"]["quote"][0]
    meta = res["meta"]
    dates, o, h, l, c, v = [], [], [], [], [], []
    for i, t in enumerate(ts):
        if None in (q["open"][i], q["high"][i], q["low"][i], q["close"][i]):
            continue
        dates.append(time.strftime("%Y-%m-%d", time.gmtime(t)))
        o.append(round(q["open"][i], 2));  h.append(round(q["high"][i], 2))
        l.append(round(q["low"][i], 2));   c.append(round(q["close"][i], 2))
        v.append(int(q["volume"][i] or 0))
    return {"name": meta.get("symbol"), "currency": meta.get("currency"),
            "dates": dates, "o": o, "h": h, "l": l, "c": c, "v": v}

# ── 台股籌碼面（FinMind，一次取整段時序；單位轉「張」= 股//1000）──
FINMIND = "https://api.finmindtrade.com/api/v4/data"
CHIP_ID, CHIP_START, CHIP_END = "2330", "2024-01-01", "2026-06-18"

def finmind(dataset, data_id, d1, d2):
    url = (f"{FINMIND}?dataset={dataset}&data_id={data_id}"
           f"&start_date={d1}&end_date={d2}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        d = json.load(r)
    if d.get("status") != 200:
        raise RuntimeError(f"FinMind {dataset}: {d.get('msg')}")
    return d.get("data", [])

def build_chips():
    rec = {}  # date -> dict
    def slot(dt):
        return rec.setdefault(dt, {"foreign": 0, "trust": 0, "dealer": 0,
                                   "marginBal": None, "shortBal": None,
                                   "fratio": None, "close": None})
    # 三大法人買賣超（買-賣，股→張）
    for row in finmind("TaiwanStockInstitutionalInvestorsBuySell", CHIP_ID, CHIP_START, CHIP_END):
        s = slot(row["date"]); net = (row["buy"] - row["sell"]) // 1000
        n = row["name"]
        if n in ("Foreign_Investor", "Foreign_Dealer_Self"): s["foreign"] += net
        elif n == "Investment_Trust": s["trust"] += net
        elif n in ("Dealer_self", "Dealer_Hedging"): s["dealer"] += net
    # 融資融券餘額（張）
    for row in finmind("TaiwanStockMarginPurchaseShortSale", CHIP_ID, CHIP_START, CHIP_END):
        s = slot(row["date"])
        s["marginBal"] = row.get("MarginPurchaseTodayBalance")
        s["shortBal"] = row.get("ShortSaleTodayBalance")
    # 外資持股比率（%）
    for row in finmind("TaiwanStockShareholding", CHIP_ID, CHIP_START, CHIP_END):
        s = slot(row["date"]); s["fratio"] = row.get("ForeignInvestmentSharesRatio")
    # 收盤價（對齊同日，元）
    for row in finmind("TaiwanStockPrice", CHIP_ID, CHIP_START, CHIP_END):
        if row["date"] in rec: rec[row["date"]]["close"] = row.get("close")
    dates = sorted(d for d, v in rec.items() if v["foreign"] or v["trust"] or v["dealer"] or v["close"])
    g = lambda k: [rec[d][k] for d in dates]
    return {"name": "台積電 2330", "dates": dates,
            "foreign": g("foreign"), "trust": g("trust"), "dealer": g("dealer"),
            "marginBal": g("marginBal"), "shortBal": g("shortBal"),
            "fratio": g("fratio"), "close": g("close")}

def main():
    out = {"_generated": time.strftime("%Y-%m-%d %H:%M"), "series": {}, "chips": {}}
    for key, sym, name, market, rng in TICKERS:
        try:
            s = fetch(sym, rng)
            s["name"], s["market"] = name, market
            out["series"][key] = s
            print(f"  ✓ {key:6} {sym:8} {len(s['dates'])} rows  "
                  f"{s['dates'][0]}~{s['dates'][-1]}  {s['currency']}")
        except Exception as e:
            print(f"  ✗ {key} {sym}: {e}", file=sys.stderr)
            sys.exit(1)
        time.sleep(0.6)
    try:
        c = build_chips()
        out["chips"]["2330"] = c
        print(f"  ✓ chips 2330  {len(c['dates'])} rows  {c['dates'][0]}~{c['dates'][-1]}")
    except Exception as e:
        print(f"  ✗ chips: {e}", file=sys.stderr)
        sys.exit(1)
    payload = "window.CASES = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n"
    with open("cases.js", "w", encoding="utf-8") as f:
        f.write(payload)
    print(f"  → cases.js  {len(payload)/1024:.0f} KB")

if __name__ == "__main__":
    main()

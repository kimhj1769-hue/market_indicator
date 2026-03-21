"""utils.py — 공통 데이터 수집 함수"""

import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta


# ── 캐시 (같은 실행 중 중복 API 호출 방지) ──────────────────────────────
_cache: dict = {}


def _get_cached(key: str, ttl: int = 60):
    """TTL(초) 이내 캐시 반환."""
    if key in _cache:
        val, ts = _cache[key]
        if (datetime.now() - ts).seconds < ttl:
            return val
    return None


def _set_cache(key: str, val):
    _cache[key] = (val, datetime.now())


# ── 주요 지수 현재가 ─────────────────────────────────────────────────────

def get_market_overview() -> dict:
    """BTC, VIX, 나스닥, S&P500 현재가 + 등락률 반환."""
    key = "market_overview"
    cached = _get_cached(key, ttl=60)
    if cached:
        return cached

    symbols = {
        "BTC":    "BTC-USD",
        "나스닥": "^IXIC",
        "S&P500": "^GSPC",
        "VIX":    "^VIX",
        "DOW":    "^DJI",
    }

    result = {}
    for name, sym in symbols.items():
        try:
            ticker = yf.Ticker(sym)
            hist   = ticker.history(period="2d", interval="1d")
            if len(hist) < 2:
                hist = ticker.history(period="5d", interval="1d").tail(2)
            if len(hist) >= 2:
                prev  = float(hist["Close"].iloc[-2])
                cur   = float(hist["Close"].iloc[-1])
                chg   = cur - prev
                pct   = chg / prev * 100
            elif len(hist) == 1:
                cur  = float(hist["Close"].iloc[-1])
                chg  = 0.0
                pct  = 0.0
            else:
                continue

            result[name] = {
                "price":   cur,
                "change":  chg,
                "pct":     pct,
                "symbol":  sym,
            }
        except Exception:
            pass

    _set_cache(key, result)
    return result


# ── Fear & Greed Index ────────────────────────────────────────────────────

def get_fear_greed() -> dict:
    """CNN Fear & Greed Index (alternative.me API)."""
    key = "fear_greed"
    cached = _get_cached(key, ttl=300)
    if cached:
        return cached

    try:
        r = requests.get(
            "https://api.alternative.me/fng/?limit=30&format=json",
            timeout=10,
        )
        data = r.json()["data"]
        latest = data[0]
        history = [
            {
                "date":  datetime.fromtimestamp(int(d["timestamp"])),
                "value": int(d["value"]),
                "label": d["value_classification"],
            }
            for d in data
        ]
        result = {
            "value":   int(latest["value"]),
            "label":   latest["value_classification"],
            "history": history,
        }
        _set_cache(key, result)
        return result
    except Exception:
        return {"value": 50, "label": "Neutral", "history": []}


# ── S&P500 섹터 히트맵 데이터 ─────────────────────────────────────────────

# S&P500 대표 종목 (섹터별)
SP500_UNIVERSE = {
    "Technology":    ["AAPL","MSFT","NVDA","AVGO","AMD","ORCL","QCOM","TXN","AMAT","MU"],
    "Communication": ["META","GOOGL","NFLX","TMUS","DIS","VZ","T","CMCSA","EA","TTWO"],
    "Consumer Disc": ["AMZN","TSLA","HD","MCD","NKE","SBUX","BKNG","TJX","EBAY","F"],
    "Financials":    ["BRK-B","JPM","V","MA","BAC","WFC","GS","MS","BLK","AXP"],
    "Healthcare":    ["LLY","UNH","JNJ","MRK","ABBV","TMO","ABT","DHR","BMY","ISRG"],
    "Industrials":   ["RTX","HON","UPS","CAT","DE","LMT","GE","BA","MMM","EMR"],
    "Energy":        ["XOM","CVX","COP","SLB","EOG","PXD","MPC","PSX","VLO","OXY"],
    "Consumer Stpl": ["WMT","PG","KO","PEP","COST","PM","MO","CL","GIS","KHC"],
    "Real Estate":   ["PLD","AMT","EQIX","CCI","SPG","PSA","WELL","DLR","AVB","EQR"],
    "Utilities":     ["NEE","DUK","SO","D","AEP","EXC","SRE","XEL","WEC","ES"],
    "Materials":     ["LIN","APD","SHW","FCX","NEM","NUE","VMC","MLM","CF","MOS"],
}


def get_heatmap_data() -> pd.DataFrame:
    """섹터별 종목 수익률 + 시가총액 반환 (히트맵용)."""
    key = "heatmap"
    cached = _get_cached(key, ttl=120)
    if cached is not None:
        return cached

    rows = []
    all_tickers = [t for tickers in SP500_UNIVERSE.values() for t in tickers]

    try:
        raw = yf.download(
            all_tickers,
            period="2d",
            interval="1d",
            auto_adjust=True,
            group_by="ticker",
            progress=False,
        )

        for sector, tickers in SP500_UNIVERSE.items():
            for ticker in tickers:
                try:
                    if len(all_tickers) == 1:
                        hist = raw
                    else:
                        hist = raw[ticker]
                    hist = hist.dropna(how="all")
                    if len(hist) < 2:
                        continue
                    prev = float(hist["Close"].iloc[-2])
                    cur  = float(hist["Close"].iloc[-1])
                    pct  = (cur - prev) / prev * 100

                    # 시가총액 (간략 근사: 현재가 × 임의 가중치)
                    info   = yf.Ticker(ticker).fast_info
                    mktcap = getattr(info, "market_cap", 10_000_000_000) or 10_000_000_000

                    rows.append({
                        "sector": sector,
                        "ticker": ticker,
                        "pct":    round(pct, 2),
                        "mktcap": mktcap,
                        "price":  round(cur, 2),
                    })
                except Exception:
                    rows.append({
                        "sector": sector,
                        "ticker": ticker,
                        "pct":    0.0,
                        "mktcap": 10_000_000_000,
                        "price":  0.0,
                    })
    except Exception:
        pass

    df = pd.DataFrame(rows)
    _set_cache(key, df)
    return df


# ── 개별 차트 데이터 ─────────────────────────────────────────────────────

def get_chart_data(symbol: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame:
    """OHLCV 차트 데이터 반환."""
    key = f"chart_{symbol}_{period}_{interval}"
    cached = _get_cached(key, ttl=120)
    if cached is not None:
        return cached
    try:
        df = yf.download(symbol, period=period, interval=interval,
                         auto_adjust=True, progress=False)
        df.columns = [c.lower() for c in df.columns]
        _set_cache(key, df)
        return df
    except Exception:
        return pd.DataFrame()


# ── VIX 히스토리 ─────────────────────────────────────────────────────────

def get_vix_history(period: str = "3mo") -> pd.DataFrame:
    return get_chart_data("^VIX", period=period)


# ── VIX 상세 정보 (investing.com 스타일) ──────────────────────────────────

def get_vix_detail() -> dict:
    """VIX 현재가 + 시가/고저/52주 등 상세 정보."""
    key = "vix_detail"
    cached = _get_cached(key, ttl=60)
    if cached:
        return cached

    result = {
        "price": 0.0, "prev_close": 0.0, "change": 0.0, "pct": 0.0,
        "open": 0.0, "high": 0.0, "low": 0.0,
        "week52_high": 0.0, "week52_low": 0.0, "avg3m": 0.0,
    }
    try:
        t    = yf.Ticker("^VIX")
        d1   = t.history(period="2d",  interval="1d")
        y1   = t.history(period="1y",  interval="1d")
        m3   = t.history(period="3mo", interval="1d")

        if len(d1) >= 2:
            result["prev_close"] = float(d1["Close"].iloc[-2])
            result["price"]      = float(d1["Close"].iloc[-1])
            result["open"]       = float(d1["Open"].iloc[-1])
            result["high"]       = float(d1["High"].iloc[-1])
            result["low"]        = float(d1["Low"].iloc[-1])
            result["change"]     = result["price"] - result["prev_close"]
            result["pct"]        = result["change"] / result["prev_close"] * 100

        if not y1.empty:
            result["week52_high"] = float(y1["High"].max())
            result["week52_low"]  = float(y1["Low"].min())

        if not m3.empty:
            result["avg3m"] = float(m3["Close"].mean())

    except Exception:
        pass

    _set_cache(key, result)
    return result


# ── Put/Call Ratio ────────────────────────────────────────────────────────

def get_put_call_ratio() -> dict:
    """SPY/QQQ 옵션 기반 Put/Call 비율 반환."""
    key = "put_call_ratio"
    cached = _get_cached(key, ttl=300)
    if cached:
        return cached

    result = {
        "ratio": None,
        "put_vol": 0,
        "call_vol": 0,
        "label": "N/A",
        "signal": "neutral",
        "history": [],
    }

    try:
        # SPY + QQQ 합산
        total_puts = 0
        total_calls = 0
        for sym in ["SPY", "QQQ"]:
            t = yf.Ticker(sym)
            exps = t.options
            if not exps:
                continue
            # 가장 가까운 만기 2개만 사용
            for exp in exps[:2]:
                try:
                    chain = t.option_chain(exp)
                    total_puts  += int(chain.puts["volume"].fillna(0).sum())
                    total_calls += int(chain.calls["volume"].fillna(0).sum())
                except Exception:
                    pass

        if total_calls > 0:
            ratio = round(total_puts / total_calls, 3)
            result["ratio"]    = ratio
            result["put_vol"]  = total_puts
            result["call_vol"] = total_calls

            if ratio < 0.7:
                result["label"]  = "Extreme Greed"
                result["signal"] = "greed"
            elif ratio < 0.9:
                result["label"]  = "Greed"
                result["signal"] = "greed"
            elif ratio < 1.1:
                result["label"]  = "Neutral"
                result["signal"] = "neutral"
            elif ratio < 1.3:
                result["label"]  = "Fear"
                result["signal"] = "fear"
            else:
                result["label"]  = "Extreme Fear"
                result["signal"] = "fear"

        # 히스토리: CBOE total P/C ratio 대리 지표 (VIX 5일 변화율)
        vix_hist = get_chart_data("^VIX", period="1mo", interval="1d")
        if not vix_hist.empty:
            hist_rows = []
            for dt, row in vix_hist.iterrows():
                hist_rows.append({"date": dt, "vix": round(float(row["close"]), 2)})
            result["history"] = hist_rows[-30:]

    except Exception:
        pass

    _set_cache(key, result)
    return result

"""utils.py — 공통 데이터 수집 함수"""

import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed


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


def clear_cache():
    """커스텀 캐시 전체 초기화 (Refresh 버튼용)."""
    _cache.clear()


# ── 색상 유틸리티 ────────────────────────────────────────────────────────────

def get_fg_color_and_emoji(value: float) -> tuple:
    """Fear & Greed 값 → (색상코드, 이모지텍스트)"""
    if value <= 25:   return "#ff5252", "😱 Extreme Fear"
    elif value <= 45: return "#ff9100", "😨 Fear"
    elif value <= 55: return "#ffd600", "😐 Neutral"
    elif value <= 75: return "#00e676", "😊 Greed"
    else:             return "#00e5ff", "🤑 Extreme Greed"


def get_vix_color_and_status(value: float) -> tuple:
    """VIX 값 → (색상코드, 상태텍스트)"""
    if value < 15:   return "#00e676", "안정"
    elif value < 20: return "#69f0ae", "낮음"
    elif value < 25: return "#ffd600", "보통"
    elif value < 30: return "#ff9100", "주의"
    elif value < 40: return "#ff5252", "공포"
    else:            return "#ff1744", "극도의 공포"


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """Hex → rgba() 문자열 (매번 파싱 대신 함수 호출)"""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ── 주요 지수 현재가 ─────────────────────────────────────────────────────

def _fetch_single_ticker(name: str, sym: str) -> tuple:
    """단일 지수 fetch (병렬 실행용)."""
    try:
        ticker = yf.Ticker(sym)
        hist = ticker.history(period="2d", interval="1d")
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
            return None

        return (name, {
            "price":   cur,
            "change":  chg,
            "pct":     pct,
            "symbol":  sym,
        })
    except Exception:
        return None


def get_market_overview() -> dict:
    """BTC, VIX, 나스닥, S&P500 현재가 + 등락률 반환 (병렬 fetch)."""
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
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_fetch_single_ticker, name, sym): name
                   for name, sym in symbols.items()}
        for future in as_completed(futures):
            res = future.result()
            if res:
                name, data = res
                result[name] = data

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

# S&P500 대표 종목 (섹터별, 섹터당 20종목)
SP500_UNIVERSE = {
    "Technology":    ["AAPL","MSFT","NVDA","AVGO","AMD","ORCL","QCOM","TXN","AMAT","MU",
                      "INTC","NOW","ADBE","CRM","KLAC","LRCX","SNPS","CDNS","MRVL","HPQ"],
    "Communication": ["META","GOOGL","NFLX","TMUS","DIS","VZ","T","CMCSA","EA","TTWO",
                      "GOOG","CHTR","MTCH","WBD","FOXA","OMC","NWSA","LYV","SIRI","ZM"],
    "Consumer Disc": ["AMZN","TSLA","HD","MCD","NKE","SBUX","BKNG","TJX","EBAY","F",
                      "GM","ABNB","CMG","ORLY","AZO","DHI","LEN","ROST","YUM","MAR"],
    "Financials":    ["BRK-B","JPM","V","MA","BAC","WFC","GS","MS","BLK","AXP",
                      "C","SCHW","CB","PGR","ICE","CME","AON","TRV","ALL","MET"],
    "Healthcare":    ["LLY","UNH","JNJ","MRK","ABBV","TMO","ABT","DHR","BMY","ISRG",
                      "CVS","AMGN","GILD","VRTX","REGN","ZTS","CI","HUM","BSX","MDT"],
    "Industrials":   ["RTX","HON","UPS","CAT","DE","LMT","GE","BA","MMM","EMR",
                      "ETN","ITW","PH","GD","NOC","FDX","NSC","CSX","WM","RSG"],
    "Energy":        ["XOM","CVX","COP","SLB","EOG","OXY","MPC","PSX","VLO","HAL",
                      "BKR","DVN","APA","CTRA","PR","SM","OVV","LNG","TRGP","WMB"],
    "Consumer Stpl": ["WMT","PG","KO","PEP","COST","PM","MO","CL","GIS","KHC",
                      "MDLZ","STZ","HSY","SJM","CPB","HRL","TSN","CAG","MKC","CHD"],
    "Real Estate":   ["PLD","AMT","EQIX","CCI","SPG","PSA","WELL","DLR","AVB","EQR",
                      "O","VICI","WY","IRM","ESS","MAA","UDR","CPT","BXP","KIM"],
    "Utilities":     ["NEE","DUK","SO","D","AEP","EXC","SRE","XEL","WEC","ES",
                      "ED","ETR","FE","PPL","CMS","AES","EIX","NI","PNW","LNT"],
    "Materials":     ["LIN","APD","SHW","FCX","NEM","NUE","VMC","MLM","CF","MOS",
                      "ECL","PPG","EMN","ALB","IFF","CE","SEE","PKG","IP","SON"],
}

# 나스닥100 대표 종목
NASDAQ100_UNIVERSE = {
    "Mega Cap Tech":   ["AAPL","MSFT","NVDA","GOOGL","GOOG","META","AMZN","TSLA","AVGO","ORCL"],
    "Software":        ["ADBE","CRM","NOW","PANW","SNPS","CDNS","TEAM","WDAY","ZS","DDOG"],
    "Semiconductors":  ["AMD","QCOM","TXN","MU","AMAT","KLAC","LRCX","MRVL","ON","MCHP"],
    "Internet/Media":  ["NFLX","TMUS","CMCSA","CSCO","INTC","PYPL","INTU","ADI","ASML","MELI"],
    "Biotech/Health":  ["AMGN","GILD","VRTX","REGN","MRNA","BIIB","DXCM","IDXX","ILMN","ALGN"],
    "Consumer Tech":   ["COST","SBUX","BKNG","ABNB","EBAY","DLTR","FAST","ODFL","CTAS","PAYX"],
}


# 시가총액 사전 정의 (단위: 억달러 × 1e9) — API 호출 없이 즉시 사용
# 실제 값과 약간 차이 있어도 히트맵 비율에는 충분
_MKTCAP_B = {
    # Technology
    "AAPL":3500,"MSFT":3100,"NVDA":2800,"AVGO":800,"AMD":300,"ORCL":450,
    "QCOM":200,"TXN":180,"AMAT":160,"MU":130,"INTC":90,"NOW":200,
    "ADBE":200,"CRM":260,"KLAC":100,"LRCX":90,"SNPS":90,"CDNS":75,
    "MRVL":70,"HPQ":30,
    # Communication
    "META":1400,"GOOGL":2100,"GOOG":2100,"NFLX":350,"TMUS":250,"DIS":200,
    "VZ":160,"T":150,"CMCSA":150,"EA":40,"TTWO":25,"CHTR":40,
    "MTCH":10,"WBD":20,"FOXA":25,"IPG":10,"OMC":20,"NWSA":15,"LYV":25,"PARA":5,
    # Consumer Disc
    "AMZN":2000,"TSLA":700,"HD":350,"MCD":200,"NKE":120,"SBUX":90,
    "BKNG":150,"TJX":130,"EBAY":30,"F":50,"GM":50,"ABNB":90,"CMG":75,
    "ORLY":60,"AZO":55,"DHI":50,"LEN":45,"ROST":50,"YUM":35,"MAR":60,
    # Financials
    "BRK-B":900,"JPM":700,"V":550,"MA":450,"BAC":350,"WFC":250,
    "GS":180,"MS":170,"BLK":150,"AXP":200,"C":120,"SCHW":130,
    "CB":90,"PGR":130,"MMC":90,"ICE":70,"CME":75,"AON":70,"TRV":55,"ALL":45,
    # Healthcare
    "LLY":700,"UNH":500,"JNJ":400,"MRK":300,"ABBV":330,"TMO":200,
    "ABT":180,"DHR":150,"BMY":130,"ISRG":180,"CVS":80,"AMGN":160,
    "GILD":90,"VRTX":120,"REGN":100,"ZTS":80,"CI":90,"HUM":60,"BSX":100,"MDT":90,
    # Industrials
    "RTX":200,"HON":130,"UPS":100,"CAT":190,"DE":130,"LMT":130,
    "GE":200,"BA":120,"MMM":60,"EMR":70,"ETN":120,"ITW":80,"PH":80,
    "GD":75,"NOC":70,"FDX":60,"NSC":60,"CSX":60,"WM":70,"RSG":60,
    # Energy
    "XOM":450,"CVX":300,"COP":150,"SLB":60,"EOG":70,"OXY":50,
    "HAL":30,"MPC":70,"PSX":60,"VLO":50,"BKR":35,"FANG":25,
    "DVN":20,"HES":40,"MRO":15,"APA":10,"CTRA":10,"PR":8,"SM":8,"OVV":10,
    # Consumer Staples
    "WMT":700,"PG":400,"KO":280,"PEP":230,"COST":350,"PM":150,
    "MO":80,"CL":60,"GIS":35,"KHC":35,"MDLZ":80,"STZ":50,"HSY":35,
    "SJM":15,"CPB":15,"HRL":20,"K":20,"TSN":20,"CAG":15,"MKC":20,
    # Real Estate
    "PLD":120,"AMT":100,"EQIX":80,"CCI":50,"SPG":70,"PSA":50,
    "WELL":60,"DLR":50,"AVB":30,"EQR":25,"O":55,"VICI":35,
    "WY":20,"IRM":25,"ESS":20,"MAA":18,"UDR":15,"CPT":15,"BXP":12,"KIM":10,
    # Utilities
    "NEE":120,"DUK":80,"SO":70,"D":50,"AEP":50,"EXC":40,
    "SRE":50,"XEL":35,"WEC":30,"ES":25,"ED":25,"ETR":20,
    "FE":20,"PPL":20,"CMS":18,"AES":15,"EIX":25,"NI":12,"PNW":10,"LNT":10,
    # Materials
    "LIN":220,"APD":70,"SHW":90,"FCX":55,"NEM":50,"NUE":35,
    "VMC":30,"MLM":30,"CF":20,"MOS":15,"ECL":60,"PPG":30,"EMN":12,
    "ALB":15,"IFF":20,"CE":10,"SEE":8,"PKG":15,"IP":12,"SON":8,
    # Nasdaq extra
    "CSCO":200,"PYPL":65,"INTU":180,"ADI":90,"ASML":300,"MELI":80,
    "PANW":120,"ANSS":25,"TEAM":45,"WDAY":55,"ZS":30,"MRNA":20,
    "BIIB":35,"DXCM":25,"IDXX":30,"ILMN":20,"ALGN":15,"DLTR":30,
    "FAST":40,"ODFL":40,"CTAS":60,"PAYX":50,"ON":30,"MCHP":40,
}

def _fetch_heatmap(universe: dict, cache_key: str) -> pd.DataFrame:
    """공통 히트맵 데이터 로더."""
    cached = _get_cached(cache_key, ttl=300)
    if cached is not None:
        return cached

    rows = []
    all_tickers = [t for tickers in universe.values() for t in tickers]
    try:
        raw = yf.download(all_tickers, period="2d", interval="1d",
                          auto_adjust=True, group_by="ticker", progress=False)
        for sector, tickers in universe.items():
            for ticker in tickers:
                try:
                    hist = raw[ticker] if len(all_tickers) > 1 else raw
                    hist = hist.dropna(how="all")
                    if len(hist) < 2:
                        continue
                    prev = float(hist["Close"].iloc[-2])
                    cur  = float(hist["Close"].iloc[-1])
                    pct  = (cur - prev) / prev * 100
                    mktcap = _MKTCAP_B.get(ticker, 10) * 1_000_000_000
                    rows.append({"sector": sector, "ticker": ticker,
                                 "pct": round(pct, 2), "mktcap": mktcap, "price": round(cur, 2)})
                except Exception:
                    rows.append({"sector": sector, "ticker": ticker,
                                 "pct": 0.0, "mktcap": _MKTCAP_B.get(ticker, 10)*1_000_000_000, "price": 0.0})
    except Exception:
        pass

    df = pd.DataFrame(rows)
    _set_cache(cache_key, df)
    return df


def get_heatmap_data() -> pd.DataFrame:
    """S&P500 섹터별 히트맵 데이터."""
    return _fetch_heatmap(SP500_UNIVERSE, "heatmap_sp500")


def get_nasdaq_heatmap_data() -> pd.DataFrame:
    """나스닥100 히트맵 데이터."""
    return _fetch_heatmap(NASDAQ100_UNIVERSE, "heatmap_nasdaq")


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
        # yfinance 버전에 따라 컬럼 구조가 다름 — 안전하게 평탄화
        _PRICE_NAMES = {"close", "open", "high", "low", "volume", "adj close"}
        if isinstance(df.columns, pd.MultiIndex):
            lvl0 = [str(c[0]).lower() for c in df.columns]
            lvl1 = [str(c[1]).lower() for c in df.columns]
            # 첫 번째 레벨이 가격명이면 그대로, 아니면 두 번째 레벨 사용
            if any(n in _PRICE_NAMES for n in lvl0):
                df.columns = lvl0
            else:
                df.columns = lvl1
        else:
            df.columns = [str(c).lower() for c in df.columns]
        # 중복 컬럼 제거 (같은 이름이 여러 개면 첫 번째만 유지)
        df = df.loc[:, ~df.columns.duplicated()]
        # 각 컬럼이 Series인지 확인 (혹시 남은 DataFrame 컬럼 squeeze)
        for _col in list(df.columns):
            if isinstance(df[_col], pd.DataFrame):
                df[_col] = df[_col].iloc[:, 0]
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

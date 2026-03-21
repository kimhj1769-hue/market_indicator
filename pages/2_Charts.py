"""pages/2_Charts.py — 캔들차트 + 볼린저밴드 + RSI + MACD"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from utils import get_chart_data, clear_cache

st.set_page_config(page_title="Charts", page_icon="📈", layout="wide")

if "rc_chart" not in st.session_state:
    st.session_state["rc_chart"] = 0

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
  * { font-family:'Inter',sans-serif; }
  [data-testid="stAppViewContainer"] { background:#0d0d1a; }
  [data-testid="stHeader"] { background:transparent !important; }
  .block-container { padding-top:3rem !important; max-width:1400px; }
  .stat-box { background:#111126; border:1px solid #1e1e3a; border-radius:12px; padding:14px; text-align:center; }
  .stat-val { font-size:20px; font-weight:800; color:#fff; }
  .stat-lbl { font-size:10px; color:#555; margin-top:5px; letter-spacing:0.8px; text-transform:uppercase; }
  div[data-testid="stButton"] button {
    background:#1a1a35 !important; border:1px solid #2a2a4a !important;
    border-radius:8px !important; color:#aaa !important;
    font-size:13px !important; font-weight:600 !important;
  }
  div[data-testid="stButton"] button:hover { border-color:#4f8ef7 !important; color:#fff !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 📈 시장 차트")

OPTIONS = ["나스닥 (^IXIC)","S&P500 (^GSPC)","BTC (BTC-USD)","VIX (^VIX)","DOW (^DJI)","NVDA","TSLA","AMD"]

# 히트맵에서 개별 종목으로 넘어온 경우
_custom = st.session_state.pop("chart_custom_ticker", None)
if _custom:
    st.session_state["chart_symbol"] = _custom
    if _custom not in OPTIONS:
        OPTIONS = [_custom] + OPTIONS

default_sym = st.session_state.get("chart_symbol", "나스닥 (^IXIC)")
default_idx = OPTIONS.index(default_sym) if default_sym in OPTIONS else 0

col_sym, col_per, col_btn = st.columns([2, 2, 1])
with col_sym:
    symbol_opt = st.selectbox("종목", OPTIONS, index=default_idx, label_visibility="collapsed")
with col_per:
    period_opt = st.select_slider("기간", options=["5d","1mo","3mo","6mo","1y","2y"], value="3mo", label_visibility="collapsed")
with col_btn:
    if st.button("⟳  Refresh", use_container_width=True):
        clear_cache()
        st.rerun()

sym_map = {
    "나스닥 (^IXIC)":"^IXIC","S&P500 (^GSPC)":"^GSPC","BTC (BTC-USD)":"BTC-USD",
    "VIX (^VIX)":"^VIX","DOW (^DJI)":"^DJI","NVDA":"NVDA","TSLA":"TSLA","AMD":"AMD",
}
interval_map = {"5d":"15m","1mo":"1h","3mo":"1d","6mo":"1d","1y":"1d","2y":"1wk"}
# 히트맵 등에서 넘어온 커스텀 티커는 sym_map에 없으면 그대로 사용
symbol   = sym_map.get(symbol_opt, symbol_opt)
interval = interval_map[period_opt]

with st.spinner(""):
    df = get_chart_data(symbol, period=period_opt, interval=interval)

if df.empty:
    st.error("데이터를 불러올 수 없습니다.")
    st.stop()

# ── 지표 계산 ─────────────────────────────────────────────────────────────
close = df["close"]

# 볼린저 밴드 (20, ±2σ)
bb_mid  = close.rolling(20).mean()
bb_std  = close.rolling(20).std()
bb_up   = bb_mid + 2 * bb_std
bb_dn   = bb_mid - 2 * bb_std

# RSI (14)
delta = close.diff()
gain  = delta.clip(lower=0).rolling(14).mean()
loss  = (-delta.clip(upper=0)).rolling(14).mean()
rs    = gain / loss.replace(0, float("nan"))
rsi   = 100 - (100 / (1 + rs))

# MACD (12, 26, 9)
ema12   = close.ewm(span=12, adjust=False).mean()
ema26   = close.ewm(span=26, adjust=False).mean()
macd    = ema12 - ema26
signal  = macd.ewm(span=9, adjust=False).mean()
hist_mc = macd - signal

pct_total = float((close.iloc[-1] / close.iloc[0] - 1) * 100)
pct_color = "#00e676" if pct_total >= 0 else "#ff5252"

# ── 서브플롯 구성 (캔들 / 거래량 / RSI / MACD) ───────────────────────────
fig = make_subplots(
    rows=4, cols=1, shared_xaxes=True,
    vertical_spacing=0.02,
    row_heights=[0.52, 0.12, 0.18, 0.18],
    subplot_titles=("", "", "RSI (14)", "MACD (12·26·9)"),
)

# ── Row 1: 캔들 ───────────────────────────────────────────────────────────
fig.add_trace(go.Candlestick(
    x=df.index, open=df["open"], high=df["high"], low=df["low"], close=close,
    increasing_line_color="#00e676", increasing_fillcolor="#00e676",
    decreasing_line_color="#ff5252", decreasing_fillcolor="#ff5252",
    name=symbol_opt, showlegend=True,
), row=1, col=1)

# MA 선
for ma, color in [(20,"#4f8ef7"),(60,"#ff9100"),(120,"#cc44ff")]:
    if len(df) >= ma:
        fig.add_trace(go.Scatter(
            x=df.index, y=close.rolling(ma).mean(),
            line=dict(color=color, width=1.2), name=f"MA{ma}", opacity=0.85,
        ), row=1, col=1)

# 볼린저 밴드
fig.add_trace(go.Scatter(
    x=df.index, y=bb_up,
    line=dict(color="rgba(180,140,255,0.7)", width=1, dash="dot"),
    name="BB Upper", showlegend=True,
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=df.index, y=bb_dn,
    line=dict(color="rgba(180,140,255,0.7)", width=1, dash="dot"),
    fill="tonexty", fillcolor="rgba(140,100,255,0.06)",
    name="BB Lower", showlegend=True,
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=df.index, y=bb_mid,
    line=dict(color="rgba(180,140,255,0.4)", width=1),
    name="BB Mid", showlegend=False,
), row=1, col=1)

# ── Row 2: 거래량 ─────────────────────────────────────────────────────────
if "volume" in df.columns:
    fig.add_trace(go.Bar(
        x=df.index, y=df["volume"],
        marker_color=["#00e676" if c >= o else "#ff5252" for c, o in zip(close, df["open"])],
        name="Volume", opacity=0.6, showlegend=False,
    ), row=2, col=1)

# ── Row 3: RSI ────────────────────────────────────────────────────────────
fig.add_trace(go.Scatter(
    x=df.index, y=rsi,
    line=dict(color="#ffd600", width=1.5),
    name="RSI", showlegend=False,
    hovertemplate="RSI: <b>%{y:.1f}</b><extra></extra>",
), row=3, col=1)

# 과매수/과매도 기준선
for y_val, color, lbl in [(70, "#ff5252", "과매수 70"), (30, "#00e676", "과매도 30"), (50, "#444", "")]:
    fig.add_hline(y=y_val, line_dash="dash", line_color=color, line_width=1,
                  opacity=0.6, row=3, col=1,
                  annotation_text=lbl, annotation_font_color=color,
                  annotation_position="right")

# RSI 과매수 구간 채움
fig.add_trace(go.Scatter(
    x=df.index, y=rsi.clip(upper=70),
    line=dict(width=0), showlegend=False, hoverinfo="skip",
), row=3, col=1)

# ── Row 4: MACD ───────────────────────────────────────────────────────────
hist_colors = ["#00e676" if v >= 0 else "#ff5252" for v in hist_mc.fillna(0)]
fig.add_trace(go.Bar(
    x=df.index, y=hist_mc,
    marker_color=hist_colors, opacity=0.7,
    name="MACD Hist", showlegend=False,
    hovertemplate="Hist: <b>%{y:.4f}</b><extra></extra>",
), row=4, col=1)
fig.add_trace(go.Scatter(
    x=df.index, y=macd,
    line=dict(color="#4f8ef7", width=1.5),
    name="MACD", showlegend=False,
    hovertemplate="MACD: <b>%{y:.4f}</b><extra></extra>",
), row=4, col=1)
fig.add_trace(go.Scatter(
    x=df.index, y=signal,
    line=dict(color="#ff9100", width=1.5),
    name="Signal", showlegend=False,
    hovertemplate="Signal: <b>%{y:.4f}</b><extra></extra>",
), row=4, col=1)
fig.add_hline(y=0, line_dash="dot", line_color="#333", line_width=1, row=4, col=1)

# ── 레이아웃 ──────────────────────────────────────────────────────────────
fig.update_layout(
    paper_bgcolor="#111126", plot_bgcolor="#0e0e1e",
    height=900, margin=dict(t=44, b=10, l=8, r=80),
    font=dict(color="white", family="Inter"),
    legend=dict(bgcolor="#111126", bordercolor="#1e1e3a", borderwidth=1,
                font=dict(color="#aaa", size=11), x=1.01, y=1.0),
    xaxis_rangeslider_visible=False,
    title=dict(
        text=f"{symbol_opt}  <span style='font-size:14px;color:{pct_color}'>{'▲' if pct_total>=0 else '▼'} {abs(pct_total):.2f}%</span>",
        font=dict(color="white", size=17), x=0.01,
    ),
    hovermode="x unified",
)

# subplot 제목 색상
for ann in fig.layout.annotations:
    ann.font.color = "#555"
    ann.font.size  = 11

# rangebreaks
rb_intraday = [dict(bounds=["sat","mon"]), dict(bounds=[20, 13.5], pattern="hour")]
rb_daily    = [dict(bounds=["sat","mon"])]
rb = rb_intraday if interval in ("15m","1h") else rb_daily

fig.update_xaxes(showgrid=False, tickfont=dict(color="#444"), rangebreaks=rb)
fig.update_yaxes(showgrid=True, gridcolor="#1a1a2e", tickfont=dict(color="#444"), zeroline=False)

# RSI y축 고정
fig.update_yaxes(range=[0, 100], row=3, col=1)

st.plotly_chart(fig, use_container_width=True,
                key=f"main_chart_{st.session_state['rc_chart']}",
                config={"scrollZoom": True, "doubleClick": "reset+autosize", "displayModeBar": True})
col_rst, _ = st.columns([1, 5])
with col_rst:
    if st.button("↺  차트 초기화", key="btn_reset_chart", use_container_width=True):
        st.session_state["rc_chart"] += 1
        st.rerun()

# ── 하단 통계 카드 ────────────────────────────────────────────────────────
c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
rsi_now = float(rsi.dropna().iloc[-1]) if not rsi.dropna().empty else 0
rsi_col = "#ff5252" if rsi_now>=70 else "#00e676" if rsi_now<=30 else "#ffd600"
macd_now = float(macd.dropna().iloc[-1]) if not macd.dropna().empty else 0
sig_now  = float(signal.dropna().iloc[-1]) if not signal.dropna().empty else 0
macd_col = "#00e676" if macd_now > sig_now else "#ff5252"

stats = [
    ("현재가",     f"{close.iloc[-1]:,.2f}",                    "#fff"),
    ("기간 고점",  f"{df['high'].max():,.2f}",                  "#ff5252"),
    ("기간 저점",  f"{df['low'].min():,.2f}",                   "#00e676"),
    ("기간 수익률",f"{'▲' if pct_total>=0 else '▼'} {abs(pct_total):.2f}%", pct_color),
    ("RSI",        f"{rsi_now:.1f}",                            rsi_col),
    ("MACD",       f"{macd_now:+.3f}",                          macd_col),
    ("평균 거래량",f"{df['volume'].mean():,.0f}" if "volume" in df.columns else "N/A", "#888"),
]
for col,(lbl,val,vc) in zip([c1,c2,c3,c4,c5,c6,c7], stats):
    col.markdown(f'<div class="stat-box"><div class="stat-val" style="color:{vc}">{val}</div><div class="stat-lbl">{lbl}</div></div>', unsafe_allow_html=True)

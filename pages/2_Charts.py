"""
pages/2_Charts.py — 나스닥 / S&P500 / BTC / VIX 캔들차트
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import get_chart_data, get_vix_history

st.set_page_config(page_title="Charts", page_icon="📈", layout="wide")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #0d0d1a; }
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 📈 시장 차트")

# ── 설정 ──────────────────────────────────────────────────────────────────
col_sym, col_per, col_btn = st.columns([2, 2, 1])

with col_sym:
    symbol_opt = st.selectbox("종목 선택", [
        "나스닥 (^IXIC)", "S&P500 (^GSPC)", "BTC (BTC-USD)",
        "VIX (^VIX)", "DOW (^DJI)", "NVDA", "TSLA", "AMD",
    ])
with col_per:
    period_opt = st.select_slider(
        "기간",
        options=["5d","1mo","3mo","6mo","1y","2y"],
        value="3mo",
    )
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 새로고침", use_container_width=True):
        st.rerun()

# 심볼 변환
sym_map = {
    "나스닥 (^IXIC)": "^IXIC",
    "S&P500 (^GSPC)": "^GSPC",
    "BTC (BTC-USD)":  "BTC-USD",
    "VIX (^VIX)":     "^VIX",
    "DOW (^DJI)":     "^DJI",
    "NVDA": "NVDA", "TSLA": "TSLA", "AMD": "AMD",
}
symbol = sym_map[symbol_opt]

interval_map = {
    "5d": "15m", "1mo": "1h", "3mo": "1d",
    "6mo": "1d", "1y": "1d", "2y": "1wk",
}
interval = interval_map[period_opt]

with st.spinner("차트 데이터 로딩 중..."):
    df = get_chart_data(symbol, period=period_opt, interval=interval)

if df.empty:
    st.error("데이터를 불러올 수 없습니다.")
    st.stop()

# ── 캔들차트 + 거래량 ─────────────────────────────────────────────────────
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.75, 0.25],
)

# 캔들
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["open"], high=df["high"],
    low=df["low"],   close=df["close"],
    increasing_line_color="#00c851",
    decreasing_line_color="#ff4444",
    name=symbol_opt,
), row=1, col=1)

# 이동평균선
for ma, color in [(20, "#4f8ef7"), (60, "#ff9500"), (120, "#cc44ff")]:
    if len(df) >= ma:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["close"].rolling(ma).mean(),
            line=dict(color=color, width=1),
            name=f"MA{ma}",
            opacity=0.8,
        ), row=1, col=1)

# 거래량
if "volume" in df.columns:
    colors = ["#00c851" if c >= o else "#ff4444"
              for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(
        x=df.index,
        y=df["volume"],
        marker_color=colors,
        name="거래량",
        opacity=0.7,
    ), row=2, col=1)

fig.update_layout(
    paper_bgcolor="#0d0d1a",
    plot_bgcolor="#1e1e2e",
    height=600,
    margin=dict(t=20, b=20, l=10, r=10),
    font=dict(color="white"),
    legend=dict(bgcolor="#1e1e2e", font=dict(color="white")),
    xaxis_rangeslider_visible=False,
)
fig.update_xaxes(showgrid=False, tickfont=dict(color="gray"))
fig.update_yaxes(showgrid=True, gridcolor="#2a2a3e", tickfont=dict(color="gray"))

st.plotly_chart(fig, use_container_width=True)

# ── 통계 요약 ─────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
stats = [
    ("현재가", f"{df['close'].iloc[-1]:,.2f}"),
    ("기간 고점", f"{df['high'].max():,.2f}"),
    ("기간 저점", f"{df['low'].min():,.2f}"),
    ("기간 수익률", f"{(df['close'].iloc[-1]/df['close'].iloc[0]-1)*100:+.2f}%"),
    ("평균 거래량", f"{df['volume'].mean():,.0f}" if "volume" in df.columns else "N/A"),
]
for col, (label, val) in zip([c1,c2,c3,c4,c5], stats):
    col.metric(label, val)

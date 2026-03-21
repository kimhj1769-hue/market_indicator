"""pages/2_Charts.py — 캔들차트"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import get_chart_data

st.set_page_config(page_title="Charts", page_icon="📈", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
  * { font-family: 'Inter', sans-serif; }
  [data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #08081a 0%, #0d0d22 60%, #0a0a18 100%);
  }
  .block-container { padding-top: 1.2rem; max-width: 1400px; }
  .stat-box {
    background: #111126; border:1px solid #1e1e3a;
    border-radius: 12px; padding: 14px; text-align: center;
  }
  .stat-val { font-size: 22px; font-weight: 800; color: #fff; }
  .stat-lbl { font-size: 11px; color: #555; margin-top: 5px; letter-spacing: 0.8px; text-transform: uppercase; }
  div[data-testid="stButton"] button {
    background: linear-gradient(135deg,#1e1e40,#252550) !important;
    border:1px solid #333 !important; border-radius:8px !important;
    color:#aaa !important; font-size:13px !important; font-weight:600 !important;
  }
  div[data-testid="stButton"] button:hover { border-color:#4f8ef7 !important; color:#fff !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 📈 시장 차트")

col_sym, col_per, col_btn = st.columns([2, 2, 1])
with col_sym:
    symbol_opt = st.selectbox("종목", [
        "나스닥 (^IXIC)", "S&P500 (^GSPC)", "BTC (BTC-USD)",
        "VIX (^VIX)", "DOW (^DJI)", "NVDA", "TSLA", "AMD",
    ], label_visibility="collapsed")
with col_per:
    period_opt = st.select_slider("기간",
        options=["5d","1mo","3mo","6mo","1y","2y"], value="3mo",
        label_visibility="collapsed")
with col_btn:
    if st.button("⟳  Refresh", use_container_width=True):
        st.rerun()

sym_map = {
    "나스닥 (^IXIC)": "^IXIC", "S&P500 (^GSPC)": "^GSPC",
    "BTC (BTC-USD)":  "BTC-USD", "VIX (^VIX)": "^VIX",
    "DOW (^DJI)": "^DJI", "NVDA": "NVDA", "TSLA": "TSLA", "AMD": "AMD",
}
interval_map = {
    "5d":"15m","1mo":"1h","3mo":"1d","6mo":"1d","1y":"1d","2y":"1wk",
}
symbol   = sym_map[symbol_opt]
interval = interval_map[period_opt]

with st.spinner(""):
    df = get_chart_data(symbol, period=period_opt, interval=interval)

if df.empty:
    st.error("데이터를 불러올 수 없습니다.")
    st.stop()

pct_total = (df["close"].iloc[-1] / df["close"].iloc[0] - 1) * 100
pct_color = "#00e676" if pct_total >= 0 else "#ff5252"

fig = make_subplots(
    rows=2, cols=1, shared_xaxes=True,
    vertical_spacing=0.02, row_heights=[0.75, 0.25],
)

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["open"], high=df["high"], low=df["low"], close=df["close"],
    increasing_line_color="#00e676", increasing_fillcolor="#00e676",
    decreasing_line_color="#ff5252", decreasing_fillcolor="#ff5252",
    name=symbol_opt,
), row=1, col=1)

for ma, color in [(20,"#4f8ef7"),(60,"#ff9100"),(120,"#cc44ff")]:
    if len(df) >= ma:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["close"].rolling(ma).mean(),
            line=dict(color=color, width=1.2), name=f"MA{ma}", opacity=0.85,
        ), row=1, col=1)

if "volume" in df.columns:
    colors = ["#00e676" if c >= o else "#ff5252"
              for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(
        x=df.index, y=df["volume"],
        marker_color=colors, name="Volume", opacity=0.6,
    ), row=2, col=1)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0e0e20",
    height=580,
    margin=dict(t=16, b=10, l=8, r=8),
    font=dict(color="white", family="Inter"),
    legend=dict(bgcolor="#111126", bordercolor="#1e1e3a", borderwidth=1,
                font=dict(color="#aaa", size=11)),
    xaxis_rangeslider_visible=False,
    title=dict(
        text=f"{symbol_opt}  <span style='color:{pct_color};font-size:14px'>"
             f"{'▲' if pct_total>=0 else '▼'} {abs(pct_total):.2f}%</span>",
        font=dict(color="white", size=17), x=0.01,
    ),
)
fig.update_xaxes(showgrid=False, tickfont=dict(color="#444"), showline=False)
fig.update_yaxes(showgrid=True, gridcolor="#1a1a30", tickfont=dict(color="#444"),
                 showline=False)

st.plotly_chart(fig, use_container_width=True)

c1, c2, c3, c4, c5 = st.columns(5)
stats = [
    ("현재가",    f"{df['close'].iloc[-1]:,.2f}"),
    ("기간 고점", f"{df['high'].max():,.2f}"),
    ("기간 저점", f"{df['low'].min():,.2f}"),
    ("기간 수익률", f"{'▲' if pct_total>=0 else '▼'} {abs(pct_total):.2f}%"),
    ("평균 거래량", f"{df['volume'].mean():,.0f}" if "volume" in df.columns else "N/A"),
]
val_colors = ["#fff","#ff5252","#00e676", pct_color,"#888"]
for col, (label, val), vc in zip([c1,c2,c3,c4,c5], stats, val_colors):
    col.markdown(
        f'<div class="stat-box">'
        f'<div class="stat-val" style="color:{vc}">{val}</div>'
        f'<div class="stat-lbl">{label}</div></div>',
        unsafe_allow_html=True,
    )

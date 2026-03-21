"""Home.py — Market Dashboard 메인"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from utils import get_market_overview, get_fear_greed, get_chart_data, clear_cache

st.set_page_config(page_title="marketindicator", page_icon="📊",
                   layout="wide", initial_sidebar_state="collapsed")

# CSS
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
  * { font-family: 'Inter', sans-serif; }
  .js-plotly-plot, .plotly { touch-action: none !important; }
  [data-testid="stAppViewContainer"] { background: #0d0d1a; }
  [data-testid="stSidebar"] { background: #0d0d1e; }
  [data-testid="stHeader"] { background: transparent !important; }
  .block-container { padding-top: 3rem !important; max-width: 1400px; }
  .card {
    background: #111126; border: 1px solid #1e1e3a; border-radius: 14px;
    padding: 20px 16px; text-align: center; position: relative; overflow: hidden;
    cursor: pointer;
  }
  .card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    background: var(--accent, #4f8ef7); border-radius:14px 14px 0 0;
  }
  .card-label { font-size:11px; font-weight:600; color:#556; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px; }
  .card-value { font-size:28px; font-weight:800; color:#fff; letter-spacing:-0.5px; line-height:1; }
  .card-change { font-size:13px; font-weight:600; margin-top:8px; }
  .up { color:#00e676; } .down { color:#ff5252; } .neu { color:#666; }
  .sec-title {
    font-size:12px; font-weight:700; color:#4f8ef7; letter-spacing:2px;
    text-transform:uppercase; margin:28px 0 14px; display:flex; align-items:center; gap:8px;
  }
  .sec-title::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,#1e1e3a,transparent); }
  .live-dot {
    width:8px; height:8px; border-radius:50%; background:#00e676;
    box-shadow:0 0 8px #00e676; animation:pulse 2s infinite;
    display:inline-block; margin-right:6px; vertical-align:middle;
  }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
  /* 카드 안 버튼 스타일 제거 */
  div[data-testid="stButton"] button {
    background: #1a1a35 !important; border: 1px solid #2a2a4a !important;
    border-radius:8px !important; color:#888 !important;
    font-size:11px !important; padding:4px 8px !important;
    margin-top:8px !important; width:100% !important;
    letter-spacing:0.5px !important;
  }
  div[data-testid="stButton"] button:hover { border-color:#4f8ef7 !important; color:#fff !important; }
</style>
""", unsafe_allow_html=True)

# 날짜
_now = datetime.now()
_DAYS = ["월요일","화요일","수요일","목요일","금요일","토요일","일요일"]
_date_str = _now.strftime("%Y년 %m월 %d일") + f"  {_DAYS[_now.weekday()]}"
_time_str = _now.strftime("%H:%M")

# 헤더
col_h, col_btn = st.columns([6, 1])
with col_h:
    st.markdown(f"""
    <div style="padding-bottom:18px; border-bottom:1px solid #1e1e3a; margin-bottom:20px;">
      <div style="font-size:26px; font-weight:800; color:#fff; letter-spacing:-0.5px;">
        📊 Market Dashboard
      </div>
      <div style="font-size:13px; color:#555; margin-top:5px;">
        <span class="live-dot"></span>{_date_str} &nbsp;·&nbsp; {_time_str} 기준
      </div>
    </div>
    """, unsafe_allow_html=True)
with col_btn:
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("⟳  Refresh", use_container_width=True):
        clear_cache()
        st.rerun()

# 데이터
with st.spinner(""):
    market = get_market_overview()
    fg     = get_fear_greed()

# ── 주요 지수 카드 ──────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">주요 지수</div>', unsafe_allow_html=True)

CARD_META = [
    ("BTC",    "₿  Bitcoin",    "#f7931a", "BTC (BTC-USD)"),
    ("나스닥", "NASDAQ",         "#4f8ef7", "나스닥 (^IXIC)"),
    ("S&P500", "S&P 500",       "#00e676", "S&P500 (^GSPC)"),
    ("VIX",    "VIX 공포지수",   "#ff5252", "VIX (^VIX)"),
    ("DOW",    "DOW JONES",     "#cc44ff", "DOW (^DJI)"),
]

cols = st.columns(5)
for col, (key, label, accent, chart_sym) in zip(cols, CARD_META):
    d     = market.get(key, {})
    price = d.get("price", 0)
    pct   = d.get("pct",   0)
    price_str = f"${price:,.0f}" if key=="BTC" else f"{price:.2f}" if key=="VIX" else f"{price:,.1f}"
    sign  = "▲" if pct > 0 else "▼" if pct < 0 else "—"
    cls   = "up" if pct > 0 else "down" if pct < 0 else "neu"
    with col:
        st.markdown(f"""
        <div class="card" style="--accent:{accent}">
          <div class="card-label">{label}</div>
          <div class="card-value">{price_str}</div>
          <div class="card-change {cls}">{sign} {abs(pct):.2f}%</div>
        </div>""", unsafe_allow_html=True)
        # 차트 바로가기 버튼
        if st.button(f"📈 차트 보기", key=f"btn_{key}"):
            st.session_state["chart_symbol"] = chart_sym
            st.switch_page("pages/2_Charts.py")

st.markdown("<br>", unsafe_allow_html=True)

# ── Fear & Greed + VIX 게이지 ─────────────────────────────────────────────
st.markdown('<div class="sec-title">시장 심리 &amp; 변동성</div>', unsafe_allow_html=True)

col_fg, col_vix = st.columns(2)

# Fear & Greed
with col_fg:
    fg_val = fg["value"]
    fg_lbl = fg["label"]
    if fg_val <= 25:   fg_color, fg_emoji = "#ff5252", "😱 Extreme Fear"
    elif fg_val <= 45: fg_color, fg_emoji = "#ff9100", "😨 Fear"
    elif fg_val <= 55: fg_color, fg_emoji = "#ffd600", "😐 Neutral"
    elif fg_val <= 75: fg_color, fg_emoji = "#00e676", "😊 Greed"
    else:              fg_color, fg_emoji = "#00e5ff", "🤑 Extreme Greed"

    fig_fg = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fg_val,
        title={"text": f"Fear & Greed Index<br><span style='font-size:14px;color:{fg_color}'>{fg_emoji}</span>",
               "font": {"color": "#ccc", "size": 16}},
        number={"font": {"color": fg_color, "size": 56}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#333", "tickfont": {"color": "#555"}, "nticks": 6},
            "bar": {"color": fg_color, "thickness": 0.25},
            "bgcolor": "#0d0d1e", "borderwidth": 0,
            "steps": [
                {"range": [0,  25], "color": "#2a0007"},
                {"range": [25, 45], "color": "#2a1000"},
                {"range": [45, 55], "color": "#2a2500"},
                {"range": [55, 75], "color": "#002a0f"},
                {"range": [75,100], "color": "#002a2a"},
            ],
            "threshold": {"line": {"color": "#fff", "width": 2}, "thickness": 0.85, "value": fg_val},
        },
    ))
    fig_fg.update_layout(
        paper_bgcolor="#111126", plot_bgcolor="#111126",
        height=380, margin=dict(t=120, b=50, l=20, r=20),
        font={"color": "white"},
    )
    st.plotly_chart(fig_fg, use_container_width=True,
                    config={"scrollZoom": True, "doubleClick": "reset+autosize", "displayModeBar": True})

# VIX 게이지
with col_vix:
    vix_val = market.get("VIX", {}).get("price", 20)
    if vix_val < 15:   vix_color, vix_status = "#00e676", "안정"
    elif vix_val < 20: vix_color, vix_status = "#69f0ae", "낮음"
    elif vix_val < 25: vix_color, vix_status = "#ffd600", "보통"
    elif vix_val < 30: vix_color, vix_status = "#ff9100", "주의"
    elif vix_val < 40: vix_color, vix_status = "#ff5252", "공포"
    else:              vix_color, vix_status = "#ff1744", "극도의 공포"

    fig_vix = go.Figure(go.Indicator(
        mode="gauge+number",
        value=vix_val,
        title={"text": f"VIX 공포지수<br><span style='font-size:14px;color:{vix_color}'>{vix_status}</span>",
               "font": {"color": "#ccc", "size": 16}},
        number={"font": {"color": vix_color, "size": 56}},
        gauge={
            "axis": {"range": [0, 60], "tickcolor": "#333", "tickfont": {"color": "#555"}, "nticks": 7},
            "bar": {"color": vix_color, "thickness": 0.25},
            "bgcolor": "#0d0d1e", "borderwidth": 0,
            "steps": [
                {"range": [0,  15], "color": "#002a0f"},
                {"range": [15, 20], "color": "#0d1a00"},
                {"range": [20, 25], "color": "#2a2500"},
                {"range": [25, 30], "color": "#2a1500"},
                {"range": [30, 40], "color": "#2a0f00"},
                {"range": [40, 60], "color": "#2a0007"},
            ],
            "threshold": {"line": {"color": "#fff", "width": 2}, "thickness": 0.85, "value": vix_val},
        },
    ))
    fig_vix.update_layout(
        paper_bgcolor="#111126", plot_bgcolor="#111126",
        height=380, margin=dict(t=120, b=50, l=20, r=20),
        font={"color": "white"},
    )
    st.plotly_chart(fig_vix, use_container_width=True,
                    config={"scrollZoom": True, "doubleClick": "reset+autosize", "displayModeBar": True})

# ── BTC / 나스닥 / S&P 차트 ────────────────────────────────────────────────
st.markdown('<div class="sec-title">주요 차트 (1개월)</div>', unsafe_allow_html=True)

col_btc, col_nas, col_sp = st.columns(3)

for col, sym, label, color, fmt in [
    (col_btc, "BTC-USD", "₿  Bitcoin",       "#f7931a", "$,.0f"),
    (col_nas, "^IXIC",   "NASDAQ",            "#4f8ef7", ",.0f"),
    (col_sp,  "^GSPC",   "S&P 500",           "#00e676", ",.0f"),
]:
    with col:
        df = get_chart_data(sym, period="1mo", interval="1d")
        if not df.empty:
            pct  = float((df["close"].iloc[-1] / df["close"].iloc[0] - 1) * 100)
            lc   = color if pct >= 0 else "#ff5252"
            fill = f"rgba({','.join(str(int(color.lstrip('#')[i:i+2],16)) for i in (0,2,4))},0.08)"
            fig  = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index, y=df["close"], mode="lines",
                line=dict(color=lc, width=2), fill="tozeroy", fillcolor=fill,
            ))
            fig.update_layout(
                title=dict(
                    text=f"{label}  <span style='font-size:13px;color:{lc}'>{'▲' if pct>=0 else '▼'} {abs(pct):.2f}%</span>",
                    font=dict(color="white", size=14), x=0.02,
                ),
                paper_bgcolor="#111126", plot_bgcolor="#0e0e1e",
                height=300, margin=dict(t=44, b=10, l=8, r=8),
                xaxis=dict(showgrid=False, tickfont=dict(color="#444"), showline=False),
                yaxis=dict(showgrid=True, gridcolor="#1a1a30", tickformat=fmt,
                           tickfont=dict(color="#444"), showline=False),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True,
                            config={"scrollZoom": True, "doubleClick": "reset+autosize", "displayModeBar": True})
        else:
            st.markdown(f'<div style="height:220px;background:#111126;border-radius:10px;display:flex;align-items:center;justify-content:center;color:#444;font-size:13px">{label} 로딩 실패</div>', unsafe_allow_html=True)

# ── F&G 30일 히스토리 ─────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Fear &amp; Greed 30일 추이</div>', unsafe_allow_html=True)

if fg["history"]:
    hist_df = pd.DataFrame(fg["history"]).sort_values("date")
    fig_h = go.Figure()
    fig_h.add_trace(go.Bar(
        x=hist_df["date"], y=hist_df["value"],
        marker_color=["#ff5252" if v<=25 else "#ff9100" if v<=45 else "#ffd600" if v<=55 else "#00e676" if v<=75 else "#00e5ff" for v in hist_df["value"]],
        text=[str(v) for v in hist_df["value"]], textposition="outside",
        textfont=dict(color="#666", size=9),
    ))
    fig_h.add_hline(y=50, line_dash="dot", line_color="#333",
                    annotation_text="Neutral 50", annotation_font_color="#444",
                    annotation_position="right")
    fig_h.update_layout(
        paper_bgcolor="#111126", plot_bgcolor="#0e0e1e",
        height=250, margin=dict(t=10, b=10, l=8, r=70),
        xaxis=dict(showgrid=False, tickfont=dict(color="#444")),
        yaxis=dict(range=[0,115], showgrid=False, tickfont=dict(color="#444")),
    )
    st.plotly_chart(fig_h, use_container_width=True,
                    config={"scrollZoom": True, "doubleClick": "reset+autosize", "displayModeBar": True})

# 푸터
st.markdown("""
<div style="border-top:1px solid #1a1a30; margin-top:24px; padding-top:14px;
            text-align:center; color:#333; font-size:12px;">
  Data: Yahoo Finance · alternative.me
</div>
""", unsafe_allow_html=True)

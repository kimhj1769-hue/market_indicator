"""Home.py — Market Dashboard 메인"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from utils import get_market_overview, get_fear_greed, get_chart_data

st.set_page_config(
    page_title="Market Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

  * { font-family: 'Inter', sans-serif; }

  [data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #08081a 0%, #0d0d22 60%, #0a0a18 100%);
  }
  [data-testid="stSidebar"] { background: #0d0d1e; }
  .block-container { padding-top: 1.2rem; max-width: 1400px; }

  /* 헤더 */
  .dash-header {
    display: flex; align-items: center; gap: 12px;
    padding: 6px 0 18px 0; border-bottom: 1px solid #1e1e3a;
    margin-bottom: 24px;
  }
  .dash-title { font-size: 26px; font-weight: 800; color: #fff; letter-spacing: -0.5px; }
  .dash-sub   { font-size: 13px; color: #555; margin-top: 3px; }
  .live-dot   {
    width: 8px; height: 8px; border-radius: 50%;
    background: #00e676; box-shadow: 0 0 8px #00e676;
    animation: pulse 2s infinite;
    display: inline-block; margin-right: 6px; vertical-align: middle;
  }
  @keyframes pulse {
    0%,100% { opacity: 1; } 50% { opacity: 0.3; }
  }

  /* 섹션 타이틀 */
  .sec-title {
    font-size: 13px; font-weight: 700; color: #4f8ef7;
    letter-spacing: 1.5px; text-transform: uppercase;
    margin: 28px 0 14px 0; display: flex; align-items: center; gap: 8px;
  }
  .sec-title::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, #1e1e3a, transparent);
  }

  /* 지표 카드 */
  .card {
    background: linear-gradient(145deg, #141428, #111126);
    border: 1px solid #1e1e3a;
    border-radius: 14px;
    padding: 18px 16px;
    text-align: center;
    transition: border-color .3s;
    position: relative; overflow: hidden;
  }
  .card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: var(--accent, #4f8ef7);
    border-radius: 14px 14px 0 0;
  }
  .card-label { font-size: 11px; font-weight: 600; color: #556; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; }
  .card-value { font-size: 26px; font-weight: 800; color: #fff; letter-spacing: -0.5px; line-height: 1; }
  .card-change { font-size: 13px; font-weight: 600; margin-top: 7px; }
  .up   { color: #00e676; }
  .down { color: #ff5252; }
  .neu  { color: #666; }

  /* 작은 통계 */
  .mini-stat {
    background: #111126;
    border: 1px solid #1e1e3a;
    border-radius: 10px;
    padding: 12px 14px;
    text-align: center;
  }
  .mini-val { font-size: 22px; font-weight: 700; }
  .mini-lbl { font-size: 11px; color: #555; margin-top: 4px; letter-spacing: 0.5px; }

  /* 새로고침 버튼 */
  div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #1e1e40, #252550) !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
    color: #aaa !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
  }
  div[data-testid="stButton"] button:hover {
    border-color: #4f8ef7 !important;
    color: #fff !important;
  }
</style>
""", unsafe_allow_html=True)

# ── 날짜/요일 계산 ────────────────────────────────────────────────────────
_now = datetime.now()
_DAYS_KO = ["월요일","화요일","수요일","목요일","금요일","토요일","일요일"]
_date_str = _now.strftime("%Y년 %m월 %d일") + f"  {_DAYS_KO[_now.weekday()]}"
_time_str = _now.strftime("%H:%M")

# ── 헤더 ──────────────────────────────────────────────────────────────────
col_h, col_btn = st.columns([6, 1])
with col_h:
    st.markdown(f"""
    <div class="dash-header">
      <div>
        <div class="dash-title">📊 Market Dashboard</div>
        <div class="dash-sub">
          <span class="live-dot"></span>
          {_date_str} &nbsp;·&nbsp; 기준 {_time_str}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
with col_btn:
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("⟳  Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── 데이터 로드 ────────────────────────────────────────────────────────────
with st.spinner(""):
    market = get_market_overview()
    fg     = get_fear_greed()

# ── 주요 지표 카드 ──────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">주요 지수</div>', unsafe_allow_html=True)

CARD_META = [
    ("BTC",    "₿  Bitcoin",   "$",  "#f7931a"),
    ("나스닥", "NASDAQ",        "",   "#4f8ef7"),
    ("S&P500", "S&P 500",      "",   "#00e676"),
    ("VIX",    "VIX  공포지수", "",   "#ff5252"),
    ("DOW",    "DOW JONES",    "",   "#cc44ff"),
]

cols = st.columns(5)
for col, (key, label, prefix, accent) in zip(cols, CARD_META):
    d     = market.get(key, {})
    price = d.get("price", 0)
    pct   = d.get("pct",   0)
    chg   = d.get("change", 0)

    if key == "BTC":
        price_str = f"${price:,.0f}"
    elif key == "VIX":
        price_str = f"{price:.2f}"
    else:
        price_str = f"{price:,.1f}"

    sign  = "▲" if pct > 0 else "▼" if pct < 0 else "—"
    cls   = "up" if pct > 0 else "down" if pct < 0 else "neu"
    chg_str = f"{sign} {abs(pct):.2f}%"

    with col:
        st.markdown(f"""
        <div class="card" style="--accent:{accent}">
          <div class="card-label">{label}</div>
          <div class="card-value">{price_str}</div>
          <div class="card-change {cls}">{chg_str}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Fear & Greed + VIX 게이지 + BTC 차트 ─────────────────────────────────
st.markdown('<div class="sec-title">시장 심리 &amp; 변동성</div>', unsafe_allow_html=True)

col_fg, col_vix = st.columns(2)

# ── Fear & Greed ──
with col_fg:
    fg_val = fg["value"]
    fg_lbl = fg["label"]
    if fg_val <= 25:   fg_color, fg_emoji = "#ff5252", "😱"
    elif fg_val <= 45: fg_color, fg_emoji = "#ff9100", "😨"
    elif fg_val <= 55: fg_color, fg_emoji = "#ffd600", "😐"
    elif fg_val <= 75: fg_color, fg_emoji = "#00e676", "😊"
    else:              fg_color, fg_emoji = "#00e5ff", "🤑"

    fig_fg = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fg_val,
        title={
            "text": f"Fear & Greed<br><span style='font-size:13px;color:{fg_color}'>{fg_emoji} {fg_lbl}</span>",
            "font": {"color": "#ccc", "size": 15},
        },
        number={"font": {"color": fg_color, "size": 48}, "suffix": ""},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#333",
                     "tickfont": {"color": "#444"}, "nticks": 6},
            "bar":  {"color": fg_color, "thickness": 0.22},
            "bgcolor": "#0d0d1e",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  25], "color": "#1a0508"},
                {"range": [25, 45], "color": "#1a0b00"},
                {"range": [45, 55], "color": "#1a1800"},
                {"range": [55, 75], "color": "#001a0d"},
                {"range": [75, 100],"color": "#001a1a"},
            ],
            "threshold": {"line": {"color": "#fff", "width": 2},
                          "thickness": 0.8, "value": fg_val},
        },
    ))
    fig_fg.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=260,
        margin=dict(t=80, b=10, l=20, r=20),
        font={"color": "white"},
    )
    st.plotly_chart(fig_fg, use_container_width=True)

# ── VIX 게이지 ──
with col_vix:
    vix_val = market.get("VIX", {}).get("price", 20)
    if vix_val < 15:   vix_color, vix_status = "#00e676", "안정"
    elif vix_val < 20: vix_color, vix_status = "#69f0ae", "낮음"
    elif vix_val < 25: vix_color, vix_status = "#ffd600", "보통"
    elif vix_val < 30: vix_color, vix_status = "#ff9100", "주의"
    elif vix_val < 40: vix_color, vix_status = "#ff5252", "공포"
    else:              vix_color, vix_status = "#ff5252", "극도의 공포"

    fig_vix = go.Figure(go.Indicator(
        mode="gauge+number",
        value=vix_val,
        title={
            "text": f"VIX 공포지수<br><span style='font-size:13px;color:{vix_color}'>{vix_status}</span>",
            "font": {"color": "#ccc", "size": 15},
        },
        number={"font": {"color": vix_color, "size": 48}},
        gauge={
            "axis": {"range": [0, 60], "tickcolor": "#333",
                     "tickfont": {"color": "#444"}, "nticks": 7},
            "bar":  {"color": vix_color, "thickness": 0.22},
            "bgcolor": "#0d0d1e",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  15], "color": "#001a0d"},
                {"range": [15, 20], "color": "#0d1a00"},
                {"range": [20, 25], "color": "#1a1800"},
                {"range": [25, 30], "color": "#1a1000"},
                {"range": [30, 40], "color": "#1a0b00"},
                {"range": [40, 60], "color": "#1a0508"},
            ],
            "threshold": {"line": {"color": "#fff", "width": 2},
                          "thickness": 0.8, "value": vix_val},
        },
    ))
    fig_vix.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=260,
        margin=dict(t=80, b=10, l=20, r=20),
        font={"color": "white"},
    )
    st.plotly_chart(fig_vix, use_container_width=True)

# ── BTC + 나스닥 + S&P 차트 ───────────────────────────────────────────────
st.markdown('<div class="sec-title">주요 차트</div>', unsafe_allow_html=True)

col_btc, col_nas, col_sp = st.columns(3)

for col, sym, label, color, fill, fmt in [
    (col_btc, "BTC-USD", "₿  Bitcoin",        "#f7931a", "rgba(247,147,26,0.08)",  "$,.0f"),
    (col_nas, "^IXIC",   "NASDAQ Composite",  "#4f8ef7", "rgba(79,142,247,0.08)",  ",.0f"),
    (col_sp,  "^GSPC",   "S&P 500",           "#00e676", "rgba(0,230,118,0.08)",   ",.0f"),
]:
    with col:
        df = get_chart_data(sym, period="1mo", interval="1d")
        if not df.empty:
            pct = (df["close"].iloc[-1] / df["close"].iloc[0] - 1) * 100
            lc  = color if pct >= 0 else "#ff5252"
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index, y=df["close"],
                mode="lines",
                line=dict(color=lc, width=2),
                fill="tozeroy", fillcolor=fill,
            ))
            fig.update_layout(
                title=dict(
                    text=f"{label}  <span style='font-size:13px;color:{lc}'>"
                         f"{'▲' if pct>=0 else '▼'} {abs(pct):.2f}%</span>",
                    font=dict(color="white", size=14), x=0.02,
                ),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0e0e20",
                height=220, margin=dict(t=44, b=10, l=8, r=8),
                xaxis=dict(showgrid=False, tickfont=dict(color="#444"), showline=False),
                yaxis=dict(showgrid=True, gridcolor="#1a1a30",
                           tickformat=fmt, tickfont=dict(color="#444"), showline=False),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(
                f'<div style="height:220px;background:#0e0e20;border-radius:10px;'
                f'display:flex;align-items:center;justify-content:center;'
                f'color:#444;font-size:13px">{label} 데이터 로딩 실패</div>',
                unsafe_allow_html=True,
            )

# ── Fear & Greed 30일 히스토리 ─────────────────────────────────────────────
st.markdown('<div class="sec-title">Fear &amp; Greed  30일 추이</div>', unsafe_allow_html=True)

if fg["history"]:
    hist_df = pd.DataFrame(fg["history"]).sort_values("date")
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Bar(
        x=hist_df["date"], y=hist_df["value"],
        marker_color=[
            "#ff5252" if v <= 25 else
            "#ff9100" if v <= 45 else
            "#ffd600" if v <= 55 else
            "#00e676" if v <= 75 else "#00e5ff"
            for v in hist_df["value"]
        ],
        text=[str(v) for v in hist_df["value"]],
        textposition="outside",
        textfont=dict(color="#777", size=9),
    ))
    fig_hist.add_hline(y=50, line_dash="dot", line_color="#333",
                       annotation_text="Neutral", annotation_font_color="#444",
                       annotation_position="right")
    fig_hist.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0e0e20",
        height=180, margin=dict(t=10, b=10, l=8, r=60),
        xaxis=dict(showgrid=False, tickfont=dict(color="#444"), showline=False),
        yaxis=dict(range=[0, 115], showgrid=False, tickfont=dict(color="#444")),
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ── 푸터 ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="border-top:1px solid #1a1a30; margin-top:24px; padding-top:14px;
            text-align:center; color:#333; font-size:12px;">
  Data: Yahoo Finance · alternative.me &nbsp;|&nbsp; Auto-refresh every 60s
</div>
""", unsafe_allow_html=True)

st.markdown("""
<script>setTimeout(function(){window.location.reload();},60000);</script>
""", unsafe_allow_html=True)

"""
Home.py — 시장 동향 대시보드 메인 페이지

Overview:
  BTC / VIX / Fear&Greed / 나스닥 / S&P500 핵심 지표 한눈에
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils import get_market_overview, get_fear_greed, get_chart_data

# ── 페이지 설정 ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Market Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS 스타일 ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #333;
    }
    .metric-label { color: #888; font-size: 13px; margin-bottom: 4px; }
    .metric-value { color: #fff; font-size: 28px; font-weight: bold; }
    .metric-up   { color: #00c851; font-size: 16px; }
    .metric-down { color: #ff4444; font-size: 16px; }
    .metric-neu  { color: #aaa;    font-size: 16px; }
    .section-title { color: #ccc; font-size: 18px; font-weight: 600;
                     margin: 20px 0 10px 0; border-left: 3px solid #4f8ef7;
                     padding-left: 10px; }
    [data-testid="stAppViewContainer"] { background: #0d0d1a; }
    [data-testid="stSidebar"]          { background: #13131f; }
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)


# ── 헤더 ──────────────────────────────────────────────────────────────────
col_title, col_refresh = st.columns([5, 1])
with col_title:
    st.markdown("# 📊 Market Dashboard")
    st.caption("실시간 글로벌 시장 동향 | 60초 자동 새로고침")
with col_refresh:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.divider()

# ── 데이터 로드 ────────────────────────────────────────────────────────────
with st.spinner("데이터 불러오는 중..."):
    market   = get_market_overview()
    fg       = get_fear_greed()


# ── 1행: 주요 지표 카드 ────────────────────────────────────────────────────
st.markdown('<div class="section-title">📈 주요 지수</div>', unsafe_allow_html=True)

cols = st.columns(5)
items = [
    ("₿ BTC",    "BTC",    "$"),
    ("📊 나스닥", "나스닥", ""),
    ("📊 S&P500", "S&P500", ""),
    ("📉 VIX",   "VIX",    ""),
    ("📊 DOW",   "DOW",    ""),
]

for col, (label, key, prefix) in zip(cols, items):
    with col:
        d = market.get(key, {})
        price = d.get("price", 0)
        pct   = d.get("pct",   0)

        if pct > 0:
            arrow = "▲"
            cls   = "metric-up"
        elif pct < 0:
            arrow = "▼"
            cls   = "metric-down"
        else:
            arrow = "—"
            cls   = "metric-neu"

        if key == "BTC":
            price_str = f"${price:,.0f}"
        elif key == "VIX":
            price_str = f"{price:.2f}"
        else:
            price_str = f"{price:,.2f}"

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{price_str}</div>
            <div class="{cls}">{arrow} {abs(pct):.2f}%</div>
        </div>
        """, unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)

# ── 2행: Fear&Greed 게이지 + VIX 게이지 + BTC 미니차트 ──────────────────
st.markdown('<div class="section-title">🌡 시장 심리 & 변동성</div>', unsafe_allow_html=True)

col_fg, col_vix, col_btc = st.columns([1, 1, 2])

# Fear & Greed 게이지
with col_fg:
    fg_val = fg["value"]
    fg_lbl = fg["label"]

    # 색상
    if fg_val <= 25:
        fg_color = "#ff2d55"
        fg_emoji = "😱"
    elif fg_val <= 45:
        fg_color = "#ff9500"
        fg_emoji = "😨"
    elif fg_val <= 55:
        fg_color = "#ffcc00"
        fg_emoji = "😐"
    elif fg_val <= 75:
        fg_color = "#34c759"
        fg_emoji = "😊"
    else:
        fg_color = "#00c851"
        fg_emoji = "🤑"

    fig_fg = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fg_val,
        title={"text": f"{fg_emoji} Fear & Greed<br><span style='font-size:14px'>{fg_lbl}</span>",
               "font": {"color": "white", "size": 16}},
        number={"font": {"color": fg_color, "size": 40}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "gray",
                     "tickfont": {"color": "gray"}},
            "bar":  {"color": fg_color, "thickness": 0.3},
            "bgcolor": "#1e1e2e",
            "bordercolor": "#333",
            "steps": [
                {"range": [0,  25], "color": "#3d0010"},
                {"range": [25, 45], "color": "#3d1f00"},
                {"range": [45, 55], "color": "#2e2e00"},
                {"range": [55, 75], "color": "#003d1a"},
                {"range": [75, 100],"color": "#005c28"},
            ],
            "threshold": {"line": {"color": "white", "width": 3},
                          "value": fg_val},
        },
    ))
    fig_fg.update_layout(
        paper_bgcolor="#0d0d1a", plot_bgcolor="#0d0d1a",
        height=220, margin=dict(t=60, b=10, l=20, r=20),
        font={"color": "white"},
    )
    st.plotly_chart(fig_fg, use_container_width=True)

# VIX 게이지
with col_vix:
    vix_val = market.get("VIX", {}).get("price", 20)

    if vix_val < 15:
        vix_color = "#34c759"; vix_status = "낮음(안정)"
    elif vix_val < 25:
        vix_color = "#ffcc00"; vix_status = "보통"
    elif vix_val < 35:
        vix_color = "#ff9500"; vix_status = "높음(주의)"
    else:
        vix_color = "#ff2d55"; vix_status = "매우 높음(공포)"

    fig_vix = go.Figure(go.Indicator(
        mode="gauge+number",
        value=vix_val,
        title={"text": f"📉 VIX 공포지수<br><span style='font-size:14px'>{vix_status}</span>",
               "font": {"color": "white", "size": 16}},
        number={"font": {"color": vix_color, "size": 40}},
        gauge={
            "axis": {"range": [0, 80], "tickcolor": "gray",
                     "tickfont": {"color": "gray"}},
            "bar":  {"color": vix_color, "thickness": 0.3},
            "bgcolor": "#1e1e2e",
            "bordercolor": "#333",
            "steps": [
                {"range": [0,  15], "color": "#003d1a"},
                {"range": [15, 25], "color": "#2e2e00"},
                {"range": [25, 35], "color": "#3d1f00"},
                {"range": [35, 80], "color": "#3d0010"},
            ],
            "threshold": {"line": {"color": "white", "width": 3},
                          "value": vix_val},
        },
    ))
    fig_vix.update_layout(
        paper_bgcolor="#0d0d1a", plot_bgcolor="#0d0d1a",
        height=220, margin=dict(t=60, b=10, l=20, r=20),
        font={"color": "white"},
    )
    st.plotly_chart(fig_vix, use_container_width=True)

# BTC 7일 차트
with col_btc:
    btc_df = get_chart_data("BTC-USD", period="7d", interval="1h")
    if not btc_df.empty:
        btc_color = "#f7931a"
        fig_btc = go.Figure()
        fig_btc.add_trace(go.Scatter(
            x=btc_df.index,
            y=btc_df["close"],
            mode="lines",
            line=dict(color=btc_color, width=2),
            fill="tozeroy",
            fillcolor="rgba(247,147,26,0.1)",
            name="BTC",
        ))
        fig_btc.update_layout(
            title=dict(text="₿ BTC 7일 추이", font=dict(color="white", size=16)),
            paper_bgcolor="#0d0d1a", plot_bgcolor="#1e1e2e",
            height=220, margin=dict(t=40, b=10, l=10, r=10),
            xaxis=dict(showgrid=False, tickfont=dict(color="gray"), color="gray"),
            yaxis=dict(showgrid=True, gridcolor="#333",
                       tickformat="$,.0f", tickfont=dict(color="gray")),
            showlegend=False,
        )
        st.plotly_chart(fig_btc, use_container_width=True)


# ── 3행: 나스닥 + S&P500 미니차트 ────────────────────────────────────────
st.markdown('<div class="section-title">📈 지수 차트 (1개월)</div>', unsafe_allow_html=True)

col_nas, col_sp = st.columns(2)

for col, sym, label, color in [
    (col_nas, "^IXIC", "나스닥 (IXIC)", "#4f8ef7"),
    (col_sp,  "^GSPC", "S&P 500",       "#34c759"),
]:
    with col:
        df = get_chart_data(sym, period="1mo", interval="1d")
        if not df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index, y=df["close"],
                mode="lines",
                line=dict(color=color, width=2),
                fill="tozeroy",
                fillcolor=f"rgba{tuple(list(int(color.lstrip('#')[i:i+2], 16) for i in (0,2,4)) + [0])}".replace(
                    ", 0)", ", 0.1)"),
                name=label,
            ))
            fig.update_layout(
                title=dict(text=f"📊 {label}", font=dict(color="white", size=15)),
                paper_bgcolor="#0d0d1a", plot_bgcolor="#1e1e2e",
                height=220, margin=dict(t=40, b=10, l=10, r=10),
                xaxis=dict(showgrid=False, tickfont=dict(color="gray")),
                yaxis=dict(showgrid=True, gridcolor="#333",
                           tickformat=",.0f", tickfont=dict(color="gray")),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)


# ── Fear & Greed 30일 히스토리 ────────────────────────────────────────────
st.markdown('<div class="section-title">📅 Fear & Greed 30일 추이</div>', unsafe_allow_html=True)

if fg["history"]:
    hist_df = pd.DataFrame(fg["history"]).sort_values("date")
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Bar(
        x=hist_df["date"],
        y=hist_df["value"],
        marker_color=[
            "#ff2d55" if v <= 25 else
            "#ff9500" if v <= 45 else
            "#ffcc00" if v <= 55 else
            "#34c759" if v <= 75 else
            "#00c851"
            for v in hist_df["value"]
        ],
        name="Fear & Greed",
    ))
    fig_hist.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
    fig_hist.update_layout(
        paper_bgcolor="#0d0d1a", plot_bgcolor="#1e1e2e",
        height=200, margin=dict(t=10, b=30, l=10, r=10),
        xaxis=dict(showgrid=False, tickfont=dict(color="gray")),
        yaxis=dict(range=[0, 100], showgrid=True, gridcolor="#333",
                   tickfont=dict(color="gray")),
        showlegend=False,
    )
    st.plotly_chart(fig_hist, use_container_width=True)


# ── 자동 새로고침 ─────────────────────────────────────────────────────────
st.markdown("---")
st.caption("⏱ 데이터는 60초마다 자동 갱신됩니다. | 출처: Yahoo Finance · alternative.me")

# 60초 자동 새로고침
st.markdown("""
<script>
setTimeout(function() { window.location.reload(); }, 60000);
</script>
""", unsafe_allow_html=True)

"""
pages/1_Heatmap.py — Finviz 스타일 S&P500 섹터 히트맵
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import get_heatmap_data

st.set_page_config(page_title="Heatmap", page_icon="🗺️", layout="wide")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #0d0d1a; }
    .block-container { padding-top: 1rem; }
    .section-title { color: #ccc; font-size: 18px; font-weight: 600;
                     margin: 10px 0; border-left: 3px solid #4f8ef7;
                     padding-left: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🗺️ S&P500 섹터 히트맵")
st.caption("Finviz 스타일 | 크기: 시가총액 비례 | 색상: 당일 등락률")

col_btn, col_range = st.columns([1, 3])
with col_btn:
    if st.button("🔄 새로고침"):
        st.cache_data.clear()
        st.rerun()
with col_range:
    color_range = st.slider("색상 범위 (%)", 1, 10, 3, 1)

with st.spinner("히트맵 데이터 로딩 중... (약 10~20초)"):
    df = get_heatmap_data()

if df.empty:
    st.error("데이터를 불러올 수 없습니다.")
    st.stop()

# ── Treemap (Finviz 스타일) ────────────────────────────────────────────────
# 색상: 빨강(-) ↔ 검정(0) ↔ 초록(+)
df["label_text"] = df.apply(
    lambda r: f"{r['ticker']}<br>{r['pct']:+.2f}%", axis=1
)
df["color_clamped"] = df["pct"].clip(-color_range, color_range)

fig = go.Figure(go.Treemap(
    ids=df["ticker"],
    labels=df["ticker"],
    parents=df["sector"],
    values=df["mktcap"],
    customdata=df[["pct", "price", "sector"]],
    texttemplate="<b>%{label}</b><br>%{customdata[0]:+.2f}%",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "섹터: %{customdata[2]}<br>"
        "가격: $%{customdata[1]:.2f}<br>"
        "등락: %{customdata[0]:+.2f}%"
        "<extra></extra>"
    ),
    marker=dict(
        colors=df["color_clamped"],
        colorscale=[
            [0.0,  "#8b0000"],
            [0.2,  "#c0392b"],
            [0.4,  "#e74c3c"],
            [0.5,  "#1a1a2e"],
            [0.6,  "#27ae60"],
            [0.8,  "#1e8449"],
            [1.0,  "#145a32"],
        ],
        cmid=0,
        cmin=-color_range,
        cmax=color_range,
        showscale=True,
        colorbar=dict(
            title="등락률(%)",
            tickfont=dict(color="gray"),
            titlefont=dict(color="gray"),
            thickness=12,
            len=0.8,
        ),
    ),
    textfont=dict(color="white", size=12),
    tiling=dict(squarifyratio=1),
    pathbar=dict(visible=True),
    root=dict(color="#0d0d1a"),
))

fig.update_layout(
    paper_bgcolor="#0d0d1a",
    plot_bgcolor="#0d0d1a",
    height=680,
    margin=dict(t=10, b=10, l=10, r=10),
    font=dict(color="white"),
)

st.plotly_chart(fig, use_container_width=True)

# ── 섹터별 요약 표 ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📋 섹터별 평균 등락률</div>',
            unsafe_allow_html=True)

sector_summary = (
    df.groupby("sector")["pct"]
    .mean()
    .reset_index()
    .rename(columns={"sector": "섹터", "pct": "평균 등락률(%)"})
    .sort_values("평균 등락률(%)", ascending=False)
)

def color_pct(val):
    color = "#00c851" if val > 0 else "#ff4444" if val < 0 else "#aaa"
    return f"color: {color}; font-weight: bold"

st.dataframe(
    sector_summary.style
    .format({"평균 등락률(%)": "{:+.2f}%"})
    .applymap(color_pct, subset=["평균 등락률(%)"]),
    use_container_width=True,
    height=350,
)

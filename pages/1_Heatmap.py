"""pages/1_Heatmap.py — Finviz 스타일 S&P500 섹터 히트맵"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import get_heatmap_data

st.set_page_config(page_title="Heatmap", page_icon="🗺️", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
  * { font-family: 'Inter', sans-serif; }
  [data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #08081a 0%, #0d0d22 60%, #0a0a18 100%);
  }
  .block-container { padding-top: 1.2rem; max-width: 1400px; }
  .sec-title {
    font-size: 13px; font-weight: 700; color: #4f8ef7;
    letter-spacing: 1.5px; text-transform: uppercase;
    margin: 28px 0 14px 0; display: flex; align-items: center; gap: 8px;
  }
  .sec-title::after {
    content:''; flex:1; height:1px;
    background: linear-gradient(90deg,#1e1e3a,transparent);
  }
  div[data-testid="stButton"] button {
    background: linear-gradient(135deg,#1e1e40,#252550) !important;
    border:1px solid #333 !important; border-radius:8px !important;
    color:#aaa !important; font-size:13px !important; font-weight:600 !important;
  }
  div[data-testid="stButton"] button:hover { border-color:#4f8ef7 !important; color:#fff !important; }
  [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🗺️ S&P 500 섹터 히트맵")
st.caption("시가총액 비례 크기 · 색상: 당일 등락률 · Finviz 스타일")

col_btn, col_range = st.columns([1, 3])
with col_btn:
    if st.button("⟳  Refresh"):
        st.cache_data.clear()
        st.rerun()
with col_range:
    color_range = st.slider("색상 범위 (%)", 1, 10, 3, 1, label_visibility="collapsed")

with st.spinner("히트맵 데이터 로딩 중... (약 10~20초)"):
    df = get_heatmap_data()

if df.empty:
    st.error("데이터를 불러올 수 없습니다.")
    st.stop()

df["color_clamped"] = df["pct"].clip(-color_range, color_range)

# Finviz 스타일 색상 함수
def finviz_color(pct, cr=color_range):
    ratio = pct / cr  # -1 ~ +1
    if ratio >= 0:
        # 0 → 어두운초록  /  +1 → 밝은초록
        g = int(100 + 155 * ratio)
        return f"rgb(0,{g},0)"
    else:
        # 0 → 어두운빨강  /  -1 → 밝은빨강
        r = int(100 + 155 * abs(ratio))
        return f"rgb({r},0,0)"

df["tile_color"] = df["pct"].apply(lambda p: finviz_color(p, color_range))

fig = go.Figure(go.Treemap(
    ids=df["ticker"],
    labels=df["ticker"],
    parents=df["sector"],
    values=df["mktcap"],
    customdata=df[["pct","price","sector","tile_color"]],
    texttemplate="<b>%{label}</b><br><span style='font-size:11px'>%{customdata[0]:+.2f}%</span>",
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
            [0.0,  "#8b0000"],   # 강한 하락
            [0.35, "#c0392b"],
            [0.48, "#4a0000"],   # 약한 하락
            [0.5,  "#1a1a1a"],   # 중립
            [0.52, "#004a00"],   # 약한 상승
            [0.65, "#1e8449"],
            [1.0,  "#006400"],   # 강한 상승
        ],
        cmid=0, cmin=-color_range, cmax=color_range,
        showscale=True,
        colorbar=dict(
            tickvals=[-color_range, -color_range/2, 0, color_range/2, color_range],
            ticktext=[f"-{color_range}%", f"-{color_range//2}%", "0", f"+{color_range//2}%", f"+{color_range}%"],
            tickfont=dict(color="#777", size=10),
            thickness=8, len=0.6,
            bgcolor="rgba(0,0,0,0)", borderwidth=0,
            x=1.01,
        ),
    ),
    textfont=dict(color="white", size=13, family="Inter"),
    tiling=dict(squarifyratio=1, pad=2),
    pathbar=dict(
        visible=True,
        side="top",
        textfont=dict(color="#ccc", size=12, family="Inter"),
        thickness=24,
    ),
    root=dict(color="#0d0d0d"),
))

fig.update_layout(
    paper_bgcolor="#0d0d0d",
    plot_bgcolor="#0d0d0d",
    height=700,
    margin=dict(t=4, b=4, l=4, r=30),
    font=dict(color="white", family="Inter"),
)
st.plotly_chart(fig, use_container_width=True)

# 섹터 요약
st.markdown('<div class="sec-title">섹터별 평균 등락률</div>', unsafe_allow_html=True)

sector_summary = (
    df.groupby("sector")["pct"]
    .mean().reset_index()
    .rename(columns={"sector":"섹터","pct":"평균 등락률(%)"})
    .sort_values("평균 등락률(%)", ascending=False)
)

def color_pct(val):
    c = "#00e676" if val > 0 else "#ff5252" if val < 0 else "#888"
    return f"color:{c};font-weight:700"

st.dataframe(
    sector_summary.style
    .format({"평균 등락률(%)": "{:+.2f}%"})
    .applymap(color_pct, subset=["평균 등락률(%)"]),
    use_container_width=True,
    height=340,
)

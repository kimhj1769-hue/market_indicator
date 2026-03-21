"""pages/1_Heatmap.py — Finviz 스타일 S&P500 섹터 히트맵"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils import get_heatmap_data

st.set_page_config(page_title="Heatmap", page_icon="🗺️", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
  * { font-family:'Inter',sans-serif; }
  [data-testid="stAppViewContainer"] { background:#0d0d1a; }
  [data-testid="stHeader"] { background:transparent !important; }
  .block-container { padding-top:3rem !important; max-width:1400px; }
  .sec-title {
    font-size:12px; font-weight:700; color:#4f8ef7; letter-spacing:2px;
    text-transform:uppercase; margin:28px 0 14px; display:flex; align-items:center; gap:8px;
  }
  .sec-title::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,#1e1e3a,transparent); }
  div[data-testid="stButton"] button {
    background:#1a1a35 !important; border:1px solid #2a2a4a !important;
    border-radius:8px !important; color:#aaa !important; font-size:13px !important;
  }
  div[data-testid="stButton"] button:hover { border-color:#4f8ef7 !important; color:#fff !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🗺️ S&P 500 섹터 히트맵")
st.caption("크기: 시가총액 비례  ·  색상: 당일 등락률  ·  Finviz 스타일")

col_btn, col_range = st.columns([1, 3])
with col_btn:
    if st.button("⟳  Refresh"):
        st.cache_data.clear()
        st.rerun()
with col_range:
    color_range = st.slider("색상 범위 (%)", 1, 10, 3, 1, label_visibility="collapsed")

with st.spinner("데이터 로딩 중... (약 10~20초)"):
    df = get_heatmap_data()

if df.empty:
    st.error("데이터를 불러올 수 없습니다.")
    st.stop()

# ── 섹터 부모 노드 추가 (Treemap 계층 구성) ──────────────────────────────
sector_rows = []
for sec in df["sector"].unique():
    sec_df = df[df["sector"] == sec]
    sector_rows.append({
        "id":     sec,
        "label":  sec,
        "parent": "",
        "value":  sec_df["mktcap"].sum(),
        "pct":    sec_df["pct"].mean(),
        "price":  0.0,
        "color":  float(sec_df["pct"].mean()),
    })

sector_meta = pd.DataFrame(sector_rows)

# 티커 행
ticker_rows = df.rename(columns={"ticker":"id","sector":"parent"}).copy()
ticker_rows["label"] = ticker_rows["id"]
ticker_rows["value"] = ticker_rows["mktcap"]
ticker_rows["color"] = ticker_rows["pct"]

# 합치기
all_ids     = list(sector_meta["id"])    + list(ticker_rows["id"])
all_labels  = list(sector_meta["label"]) + list(ticker_rows["label"])
all_parents = list(sector_meta["parent"])+ list(ticker_rows["parent"])
all_values  = list(sector_meta["value"]) + list(ticker_rows["value"])
all_colors  = [float(c) for c in sector_meta["color"]] + [float(c) for c in ticker_rows["color"]]
all_prices  = [0.0] * len(sector_meta) + list(df["price"])
all_pcts    = list(sector_meta["pct"])  + list(df["pct"])

colors_clamped = [max(-color_range, min(color_range, c)) for c in all_colors]

fig = go.Figure(go.Treemap(
    ids=all_ids, labels=all_labels, parents=all_parents,
    values=all_values,
    customdata=list(zip(all_pcts, all_prices)),
    texttemplate="<b>%{label}</b><br><span style='font-size:11px'>%{customdata[0]:+.2f}%</span>",
    hovertemplate="<b>%{label}</b><br>등락: %{customdata[0]:+.2f}%<br>가격: $%{customdata[1]:.2f}<extra></extra>",
    marker=dict(
        colors=colors_clamped,
        colorscale=[
            [0.0,  "#8b0000"],
            [0.35, "#c0392b"],
            [0.48, "#3a0000"],
            [0.5,  "#111126"],
            [0.52, "#003a00"],
            [0.65, "#1e8449"],
            [1.0,  "#006400"],
        ],
        cmid=0, cmin=-color_range, cmax=color_range,
        showscale=True,
        colorbar=dict(
            tickvals=[-color_range, 0, color_range],
            ticktext=[f"-{color_range}%", "0", f"+{color_range}%"],
            tickfont=dict(color="#777", size=10),
            thickness=8, len=0.5, bgcolor="rgba(0,0,0,0)", borderwidth=0,
        ),
    ),
    textfont=dict(color="white", size=13, family="Inter"),
    tiling=dict(squarifyratio=1, pad=3),
    pathbar=dict(visible=True, textfont=dict(color="#ccc", size=12), thickness=26),
    root=dict(color="#0d0d1a"),
))

fig.update_layout(
    paper_bgcolor="#0d0d1a", plot_bgcolor="#0d0d1a",
    height=700, margin=dict(t=4, b=4, l=4, r=30),
    font=dict(color="white", family="Inter"),
)
st.plotly_chart(fig, use_container_width=True)

# 섹터 요약 표
st.markdown('<div class="sec-title">섹터별 평균 등락률</div>', unsafe_allow_html=True)
sector_summary = (
    df.groupby("sector")["pct"].mean().reset_index()
    .rename(columns={"sector":"섹터","pct":"평균 등락률(%)"})
    .sort_values("평균 등락률(%)", ascending=False)
)
def color_pct(val):
    c = "#00e676" if val > 0 else "#ff5252" if val < 0 else "#888"
    return f"color:{c};font-weight:700"

st.dataframe(
    sector_summary.style.format({"평균 등락률(%)":"{:+.2f}%"}).applymap(color_pct, subset=["평균 등락률(%)"]),
    use_container_width=True, height=340,
)

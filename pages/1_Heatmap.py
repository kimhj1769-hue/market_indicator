"""pages/1_Heatmap.py — Finviz 스타일 S&P500 섹터 히트맵"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from utils import get_heatmap_data, get_nasdaq_heatmap_data, get_chart_data, clear_cache

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
  .stat-box { background:#111126; border:1px solid #1e1e3a; border-radius:12px; padding:14px; text-align:center; }
  .stat-val { font-size:18px; font-weight:800; color:#fff; }
  .stat-lbl { font-size:10px; color:#555; margin-top:5px; letter-spacing:0.8px; text-transform:uppercase; }
  div[data-testid="stButton"] button {
    background:#1a1a35 !important; border:1px solid #2a2a4a !important;
    border-radius:8px !important; color:#aaa !important; font-size:13px !important;
  }
  div[data-testid="stButton"] button:hover { border-color:#4f8ef7 !important; color:#fff !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🗺️ 시장 히트맵")
st.caption("크기: 시가총액 비례  ·  색상: 당일 등락률  ·  종목 클릭 시 상세 정보")

col_tab, col_range, col_btn = st.columns([2, 2, 1])
with col_tab:
    market_tab = st.radio("시장", ["S&P 500", "NASDAQ 100"],
                           horizontal=True, label_visibility="collapsed")
with col_range:
    color_range = st.slider("색상 범위 (%)", 1, 10, 3, 1, label_visibility="collapsed")
with col_btn:
    if st.button("⟳  Refresh"):
        clear_cache()
        st.rerun()

with st.spinner("데이터 로딩 중... (5~10초)"):
    df = get_heatmap_data() if market_tab == "S&P 500" else get_nasdaq_heatmap_data()

if df.empty:
    st.error("데이터를 불러올 수 없습니다.")
    st.stop()

ticker_set = set(df["ticker"].tolist())

# ── 섹터 부모 노드 추가 ────────────────────────────────────────────────────
sector_rows = []
for sec in df["sector"].unique():
    sec_df = df[df["sector"] == sec]
    sector_rows.append({
        "id": sec, "label": sec, "parent": "",
        "value": sec_df["mktcap"].sum(), "pct": sec_df["pct"].mean(),
        "color": float(sec_df["pct"].mean()),
    })

sector_meta = pd.DataFrame(sector_rows)
ticker_rows = df.rename(columns={"ticker": "id", "sector": "parent"}).copy()
ticker_rows["label"] = ticker_rows["id"]
ticker_rows["value"] = ticker_rows["mktcap"]
ticker_rows["color"] = ticker_rows["pct"]

all_ids     = list(sector_meta["id"])     + list(ticker_rows["id"])
all_labels  = list(sector_meta["label"])  + list(ticker_rows["label"])
all_parents = list(sector_meta["parent"]) + list(ticker_rows["parent"])
all_values  = list(sector_meta["value"])  + list(ticker_rows["value"])
all_colors  = [float(c) for c in sector_meta["color"]] + [float(c) for c in ticker_rows["color"]]
all_prices  = [0.0] * len(sector_meta) + list(df["price"])
all_pcts    = list(sector_meta["pct"])   + list(df["pct"])

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
            [0.0,  "#8b0000"], [0.35, "#c0392b"], [0.48, "#3a0000"],
            [0.5,  "#111126"], [0.52, "#003a00"], [0.65, "#1e8449"],
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
    height=800, margin=dict(t=4, b=4, l=4, r=30),
    font=dict(color="white", family="Inter"),
)

# ── 클릭 이벤트 감지 ──────────────────────────────────────────────────────
event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="heatmap_treemap",
                        config={"scrollZoom": False, "doubleClick": "reset+autosize"})

# 클릭된 티커 추출
clicked_ticker = None
if event and hasattr(event, "selection") and event.selection.points:
    label = event.selection.points[0].get("label", "")
    if label in ticker_set:
        clicked_ticker = label
        st.session_state["heatmap_selected"] = label

# session_state 유지
if clicked_ticker is None:
    clicked_ticker = st.session_state.get("heatmap_selected")

# ── 종목 검색 + 상세 패널 ─────────────────────────────────────────────────
st.markdown('<div class="sec-title">종목 상세 보기</div>', unsafe_allow_html=True)

ticker_list = sorted(df["ticker"].tolist())
default_idx = (ticker_list.index(clicked_ticker) + 1) if clicked_ticker in ticker_list else 0

col_search, col_clear = st.columns([3, 1])
with col_search:
    sel = st.selectbox(
        "종목 선택 (히트맵 클릭 또는 직접 선택)",
        ["— 종목을 선택하세요 —"] + ticker_list,
        index=default_idx,
        label_visibility="collapsed",
    )
with col_clear:
    if st.button("✕ 닫기", use_container_width=True):
        st.session_state.pop("heatmap_selected", None)
        st.rerun()

selected_ticker = sel if sel != "— 종목을 선택하세요 —" else None

# ── 상세 패널 ──────────────────────────────────────────────────────────────
if selected_ticker:
    row = df[df["ticker"] == selected_ticker].iloc[0]
    price  = row["price"]
    pct    = row["pct"]
    sector = row["sector"] if "sector" in row else row.get("parent", "")
    p_color = "#00e676" if pct >= 0 else "#ff5252"
    p_sign  = "▲" if pct >= 0 else "▼"

    # 가격 카드
    st.markdown(f"""
    <div style="background:#111126; border:1px solid #1e1e3a; border-radius:16px;
                padding:20px 28px; margin:12px 0; border-top:3px solid {p_color};">
      <div style="display:flex; align-items:flex-end; gap:24px; flex-wrap:wrap;">
        <div>
          <div style="font-size:11px; color:#555; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:6px;">
            {sector}
          </div>
          <div style="font-size:48px; font-weight:800; color:#fff; line-height:1; letter-spacing:-1px;">
            {selected_ticker}
          </div>
        </div>
        <div style="padding-bottom:6px;">
          <div style="font-size:32px; font-weight:700; color:#fff;">${price:,.2f}</div>
          <div style="font-size:18px; font-weight:700; color:{p_color}; margin-top:4px;">
            {p_sign} {abs(pct):.2f}% 오늘
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 차트 로딩
    with st.spinner(f"{selected_ticker} 차트 로딩 중..."):
        chart_df = get_chart_data(selected_ticker, period="3mo", interval="1d")

    if not chart_df.empty:
        close = chart_df["close"]
        pct_3m = float((close.iloc[-1] / close.iloc[0] - 1) * 100)
        lc = "#00e676" if pct_3m >= 0 else "#ff5252"

        # ── 지표 계산 ─────────────────────────────────────────────────────
        # 볼린저 밴드 (20, ±2σ)
        bb_mid = close.rolling(20).mean()
        bb_std = close.rolling(20).std()
        bb_up  = bb_mid + 2 * bb_std
        bb_dn  = bb_mid - 2 * bb_std

        # RSI (14)
        delta = close.diff()
        gain  = delta.clip(lower=0).rolling(14).mean()
        loss  = (-delta.clip(upper=0)).rolling(14).mean()
        rsi   = 100 - (100 / (1 + gain / loss.replace(0, float("nan"))))

        # MACD (12, 26, 9)
        ema12   = close.ewm(span=12, adjust=False).mean()
        ema26   = close.ewm(span=26, adjust=False).mean()
        macd    = ema12 - ema26
        sig_line = macd.ewm(span=9, adjust=False).mean()
        hist_mc = macd - sig_line

        # ── 서브플롯 (캔들 / 거래량 / RSI / MACD) ─────────────────────
        fig_detail = make_subplots(
            rows=4, cols=1, shared_xaxes=True,
            vertical_spacing=0.02,
            row_heights=[0.50, 0.14, 0.18, 0.18],
            subplot_titles=("", "", "RSI (14)", "MACD (12·26·9)"),
        )

        # Row 1 — 캔들
        fig_detail.add_trace(go.Candlestick(
            x=chart_df.index,
            open=chart_df["open"], high=chart_df["high"],
            low=chart_df["low"],  close=close,
            increasing_line_color="#00e676", increasing_fillcolor="#00e676",
            decreasing_line_color="#ff5252", decreasing_fillcolor="#ff5252",
            name=selected_ticker, showlegend=False,
        ), row=1, col=1)

        # MA20
        fig_detail.add_trace(go.Scatter(
            x=chart_df.index, y=close.rolling(20).mean(),
            line=dict(color="#4f8ef7", width=1.2), name="MA20", opacity=0.85,
        ), row=1, col=1)

        # 볼린저 밴드
        fig_detail.add_trace(go.Scatter(
            x=chart_df.index, y=bb_up,
            line=dict(color="rgba(180,140,255,0.6)", width=1, dash="dot"),
            name="BB Upper", showlegend=True,
        ), row=1, col=1)
        fig_detail.add_trace(go.Scatter(
            x=chart_df.index, y=bb_dn,
            line=dict(color="rgba(180,140,255,0.6)", width=1, dash="dot"),
            fill="tonexty", fillcolor="rgba(140,100,255,0.05)",
            name="BB Lower", showlegend=False,
        ), row=1, col=1)

        # Row 2 — 거래량
        if "volume" in chart_df.columns:
            fig_detail.add_trace(go.Bar(
                x=chart_df.index, y=chart_df["volume"],
                marker_color=["#00e676" if c >= o else "#ff5252"
                              for c, o in zip(close, chart_df["open"])],
                name="Volume", opacity=0.6, showlegend=False,
                hovertemplate="Vol: <b>%{y:,.0f}</b><extra></extra>",
            ), row=2, col=1)

        # Row 3 — RSI
        fig_detail.add_trace(go.Scatter(
            x=chart_df.index, y=rsi,
            line=dict(color="#ffd600", width=1.5),
            name="RSI", showlegend=False,
            hovertemplate="RSI: <b>%{y:.1f}</b><extra></extra>",
        ), row=3, col=1)
        for y_val, color, lbl in [(70, "#ff5252", "과매수 70"), (30, "#00e676", "과매도 30"), (50, "#444", "")]:
            fig_detail.add_hline(y=y_val, line_dash="dash", line_color=color,
                                 line_width=1, opacity=0.6, row=3, col=1,
                                 annotation_text=lbl, annotation_font_color=color,
                                 annotation_position="right")

        # Row 4 — MACD
        hist_colors = ["#00e676" if v >= 0 else "#ff5252" for v in hist_mc.fillna(0)]
        fig_detail.add_trace(go.Bar(
            x=chart_df.index, y=hist_mc,
            marker_color=hist_colors, opacity=0.7,
            name="Hist", showlegend=False,
            hovertemplate="Hist: <b>%{y:.4f}</b><extra></extra>",
        ), row=4, col=1)
        fig_detail.add_trace(go.Scatter(
            x=chart_df.index, y=macd,
            line=dict(color="#4f8ef7", width=1.5),
            name="MACD", showlegend=False,
            hovertemplate="MACD: <b>%{y:.4f}</b><extra></extra>",
        ), row=4, col=1)
        fig_detail.add_trace(go.Scatter(
            x=chart_df.index, y=sig_line,
            line=dict(color="#ff9100", width=1.5),
            name="Signal", showlegend=False,
            hovertemplate="Signal: <b>%{y:.4f}</b><extra></extra>",
        ), row=4, col=1)
        fig_detail.add_hline(y=0, line_dash="dot", line_color="#333", line_width=1, row=4, col=1)

        # ── 레이아웃 ──────────────────────────────────────────────────
        fig_detail.update_layout(
            paper_bgcolor="#111126", plot_bgcolor="#0e0e1e",
            height=820, margin=dict(t=20, b=10, l=8, r=80),
            font=dict(color="white", family="Inter"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#888", size=11),
                        orientation="h", x=0, y=1.02),
            xaxis_rangeslider_visible=False,
            hovermode="x unified",
            title=dict(
                text=f"{selected_ticker} — 3개월  <span style='color:{lc};font-size:13px'>{'▲' if pct_3m>=0 else '▼'} {abs(pct_3m):.2f}%</span>",
                font=dict(color="#ccc", size=14), x=0.01,
            ),
        )
        for ann in fig_detail.layout.annotations:
            ann.font.color = "#555"
            ann.font.size  = 11

        fig_detail.update_xaxes(
            showgrid=False, tickfont=dict(color="#444"),
            rangebreaks=[dict(bounds=["sat", "mon"])],
        )
        fig_detail.update_yaxes(showgrid=True, gridcolor="#1a1a2e",
                                tickfont=dict(color="#444"), zeroline=False)
        fig_detail.update_yaxes(range=[0, 100], row=3, col=1)

        st.plotly_chart(fig_detail, use_container_width=True,
                        config={"scrollZoom": False, "doubleClick": "reset+autosize", "displayModeBar": False})

        # ── 통계 카드 ─────────────────────────────────────────────────
        rsi_now  = float(rsi.dropna().iloc[-1])  if not rsi.dropna().empty  else 0
        macd_now = float(macd.dropna().iloc[-1]) if not macd.dropna().empty else 0
        sig_now  = float(sig_line.dropna().iloc[-1]) if not sig_line.dropna().empty else 0
        rsi_col  = "#ff5252" if rsi_now >= 70 else "#00e676" if rsi_now <= 30 else "#ffd600"
        macd_col = "#00e676" if macd_now > sig_now else "#ff5252"
        high_3m  = float(chart_df["high"].max())
        low_3m   = float(chart_df["low"].min())
        avg_vol  = f"{chart_df['volume'].mean():,.0f}" if "volume" in chart_df.columns else "N/A"

        cols_s = st.columns(7)
        stats_s = [
            ("현재가",       f"${price:,.2f}",                              p_color),
            ("오늘 등락",    f"{p_sign} {abs(pct):.2f}%",                   p_color),
            ("3개월 수익률", f"{'▲' if pct_3m>=0 else '▼'} {abs(pct_3m):.2f}%", "#00e676" if pct_3m>=0 else "#ff5252"),
            ("3개월 고점",   f"${high_3m:,.2f}",                            "#ff5252"),
            ("3개월 저점",   f"${low_3m:,.2f}",                             "#00e676"),
            ("RSI (14)",     f"{rsi_now:.1f}",                              rsi_col),
            ("MACD",         f"{macd_now:+.3f}",                            macd_col),
        ]
        for c, (lbl, val, vc) in zip(cols_s, stats_s):
            c.markdown(
                f'<div class="stat-box"><div class="stat-val" style="color:{vc};font-size:16px">{val}</div>'
                f'<div class="stat-lbl">{lbl}</div></div>',
                unsafe_allow_html=True,
            )

        # Charts 페이지 이동 버튼
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"📈 {selected_ticker} 전체 차트 보기", use_container_width=False):
            st.session_state["chart_custom_ticker"] = selected_ticker
            st.switch_page("pages/2_Charts.py")
    else:
        st.warning(f"{selected_ticker} 차트 데이터를 불러올 수 없습니다.")

# ── 섹터 요약 표 ──────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">섹터별 평균 등락률</div>', unsafe_allow_html=True)
sector_summary = (
    df.groupby("sector")["pct"].mean().reset_index()
    .rename(columns={"sector": "섹터", "pct": "평균 등락률(%)"})
    .sort_values("평균 등락률(%)", ascending=False)
)

def color_pct(val):
    c = "#00e676" if val > 0 else "#ff5252" if val < 0 else "#888"
    return f"color:{c};font-weight:700"

st.dataframe(
    sector_summary.style.format({"평균 등락률(%)": "{:+.2f}%"}).applymap(color_pct, subset=["평균 등락률(%)"]),
    use_container_width=True, height=340,
)

"""pages/3_VIX_Fear.py — Fear/Greed + Put/Call + VIX (investing.com 스타일)"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from utils import get_fear_greed, get_vix_history, get_put_call_ratio, get_vix_detail, get_chart_data, clear_cache

st.set_page_config(page_title="VIX & Fear", page_icon="🌡️", layout="wide")

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
  .stat-val { font-size:18px; font-weight:800; }
  .stat-lbl { font-size:10px; color:#555; margin-top:5px; letter-spacing:0.8px; text-transform:uppercase; }
  .level-card { padding:10px 14px; margin:4px 0; background:#111126; border-radius:9px; }
  div[data-testid="stButton"] button {
    background:#1a1a35 !important; border:1px solid #2a2a4a !important;
    border-radius:8px !important; color:#aaa !important; font-size:13px !important;
  }
  div[data-testid="stButton"] button:hover { border-color:#4f8ef7 !important; color:#fff !important; }
</style>
""", unsafe_allow_html=True)

col_title, col_btn = st.columns([5, 1])
with col_title:
    st.markdown("## 🌡️ Fear & Greed · VIX · Put/Call")
with col_btn:
    if st.button("⟳  Refresh", use_container_width=True):
        clear_cache()
        st.rerun()

with st.spinner(""):
    fg    = get_fear_greed()
    pc    = get_put_call_ratio()
    vix_d = get_vix_detail()

# VIX period용 데이터는 탭 선택 후 로드
# ════════════════════════════════════════════════════════════════════
# 1. Fear & Greed — go.Indicator 게이지
# ════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">Fear &amp; Greed Index</div>', unsafe_allow_html=True)

fg_val = fg["value"]
fg_lbl = fg["label"]
if fg_val <= 25:   fg_color, fg_emoji = "#ff5252", "😱 Extreme Fear"
elif fg_val <= 45: fg_color, fg_emoji = "#ff9100", "😨 Fear"
elif fg_val <= 55: fg_color, fg_emoji = "#ffd600", "😐 Neutral"
elif fg_val <= 75: fg_color, fg_emoji = "#00e676", "😊 Greed"
else:              fg_color, fg_emoji = "#00e5ff", "🤑 Extreme Greed"

col_gauge, col_info = st.columns([1, 1])

with col_gauge:
    fig_fg = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fg_val,
        title={"text": f"Fear & Greed Index<br><span style='font-size:14px;color:{fg_color}'>{fg_emoji}</span>",
               "font": {"color": "#ccc", "size": 16}},
        number={"font": {"color": fg_color, "size": 64}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#333", "tickfont": {"color": "#555"}, "nticks": 6},
            "bar": {"color": fg_color, "thickness": 0.28},
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
        height=420, margin=dict(t=130, b=60, l=20, r=20),
        font={"color": "white"},
    )
    st.plotly_chart(fig_fg, use_container_width=True,
                    config={"scrollZoom": False, "doubleClick": "reset+autosize", "displayModeBar": False})

    if len(fg["history"]) > 1:
        delta = fg_val - fg["history"][1]["value"]
        d_col = "#00e676" if delta >= 0 else "#ff5252"
        st.markdown(f'<p style="text-align:center;color:{d_col};font-size:13px;margin-top:-16px">{"▲" if delta>=0 else "▼"} {abs(delta)}pt 전일 대비</p>', unsafe_allow_html=True)

with col_info:
    st.markdown("<br>", unsafe_allow_html=True)
    levels = [("0–24","Extreme Fear","#ff5252","😱"),("25–44","Fear","#ff9100","😨"),
              ("45–55","Neutral","#ffd600","😐"),("56–75","Greed","#00e676","😊"),("76–100","Extreme Greed","#00e5ff","🤑")]
    for rng, lbl, color, emoji in levels:
        is_cur = fg_lbl.lower().replace(" ","") in lbl.lower().replace(" ","")
        bg  = "#1a1a35" if is_cur else "#111126"
        bdr = f"border:1.5px solid {color}" if is_cur else f"border-left:3px solid {color}"
        mark = f' <span style="color:{color};font-weight:800">◀ 현재</span>' if is_cur else ""
        st.markdown(
            f'<div style="padding:10px 14px;margin:5px 0;background:{bg};{bdr};border-radius:9px;color:white;">'
            f'{emoji} <b style="color:{color}">{lbl}</b> <span style="color:#444;font-size:12px">({rng})</span>{mark}</div>',
            unsafe_allow_html=True,
        )

    # 7일 미니
    if len(fg["history"]) >= 7:
        st.markdown("<br>", unsafe_allow_html=True)
        mc_cols = st.columns(7)
        for i, mc in enumerate(mc_cols):
            h = fg["history"][6-i]
            v = h["value"]; d = h["date"].strftime("%m/%d")
            c = "#ff5252" if v<=25 else "#ff9100" if v<=45 else "#ffd600" if v<=55 else "#00e676" if v<=75 else "#00e5ff"
            mc.markdown(f'<div style="text-align:center;background:#111126;border-radius:7px;padding:7px 2px;border-top:2.5px solid {c};"><div style="font-size:16px;font-weight:800;color:{c}">{v}</div><div style="font-size:9px;color:#444">{d}</div></div>', unsafe_allow_html=True)

# 30일 히스토리 바차트
st.markdown('<div class="sec-title">30일 추이</div>', unsafe_allow_html=True)
if fg["history"]:
    hist_df = pd.DataFrame(fg["history"]).sort_values("date")
    fig_fh  = go.Figure()
    fig_fh.add_trace(go.Bar(
        x=hist_df["date"], y=hist_df["value"],
        marker_color=["#ff5252" if v<=25 else "#ff9100" if v<=45 else "#ffd600" if v<=55 else "#00e676" if v<=75 else "#00e5ff" for v in hist_df["value"]],
        text=[str(v) for v in hist_df["value"]], textposition="outside",
        textfont=dict(color="#666", size=9),
    ))
    fig_fh.add_hline(y=50, line_dash="dot", line_color="#333",
                     annotation_text="Neutral", annotation_font_color="#444", annotation_position="right")
    fig_fh.update_layout(
        paper_bgcolor="#111126", plot_bgcolor="#0e0e1e",
        height=280, margin=dict(t=10, b=10, l=8, r=60),
        xaxis=dict(showgrid=False, tickfont=dict(color="#444")),
        yaxis=dict(range=[0,115], showgrid=False, tickfont=dict(color="#444")),
    )
    st.plotly_chart(fig_fh, use_container_width=True,
                    config={"scrollZoom": False, "doubleClick": "reset+autosize", "displayModeBar": False})

# ════════════════════════════════════════════════════════════════════
# 2. Put/Call Ratio
# ════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">Put / Call Ratio (SPY + QQQ)</div>', unsafe_allow_html=True)

# 현재값 요약 카드
if pc["ratio"] is not None:
    r = pc["ratio"]
    pc_color = "#00e5ff" if r<0.7 else "#00e676" if r<0.9 else "#ffd600" if r<1.1 else "#ff9100" if r<1.3 else "#ff5252"
    chg_col_pc = "#ff5252" if r >= 1.0 else "#00e676"
else:
    r = 0.0
    pc_color = "#888"

col_pc_a, col_pc_b, col_pc_c, col_pc_d = st.columns([1, 1, 1, 2])
with col_pc_a:
    ratio_str = f"{r:.3f}" if pc["ratio"] is not None else "N/A"
    st.markdown(f'<div class="stat-box" style="border-top:3px solid {pc_color};"><div class="stat-val" style="color:{pc_color};font-size:28px;">{ratio_str}</div><div class="stat-lbl">P/C Ratio</div></div>', unsafe_allow_html=True)
with col_pc_b:
    st.markdown(f'<div class="stat-box" style="border-top:3px solid {pc_color};"><div class="stat-val" style="color:{pc_color};font-size:16px;">{pc["label"]}</div><div class="stat-lbl">심리</div></div>', unsafe_allow_html=True)
with col_pc_c:
    st.markdown(f'<div class="stat-box" style="border-left:3px solid #ff5252;margin-bottom:6px"><div class="stat-val" style="color:#ff5252;font-size:16px;">{pc["put_vol"]:,}</div><div class="stat-lbl">Put 거래량</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box" style="border-left:3px solid #00e676;"><div class="stat-val" style="color:#00e676;font-size:16px;">{pc["call_vol"]:,}</div><div class="stat-lbl">Call 거래량</div></div>', unsafe_allow_html=True)
with col_pc_d:
    guide = [
        ("< 0.7",  "Extreme Greed", "#00e5ff", "콜 매수 급증, 시장 과열"),
        ("0.7–0.9","Greed",         "#00e676", "낙관적 심리, 콜 우세"),
        ("0.9–1.1","Neutral",       "#ffd600", "균형 상태"),
        ("1.1–1.3","Fear",          "#ff9100", "풋 증가, 헤지 수요"),
        ("> 1.3",  "Extreme Fear",  "#ff5252", "강한 패닉 헤지"),
    ]
    cur_lbl = pc["label"] if pc["ratio"] else ""
    for rng, lbl, color, desc in guide:
        is_cur = (lbl == cur_lbl)
        bg  = "#1a1a35" if is_cur else "#111126"
        bdr = f"border:1.5px solid {color}" if is_cur else f"border-left:3px solid {color}"
        mark = f' <span style="color:{color};font-weight:800">◀</span>' if is_cur else ""
        st.markdown(
            f'<div style="padding:7px 12px;margin:3px 0;background:{bg};{bdr};border-radius:8px;">'
            f'<span style="color:{color};font-weight:700;font-size:13px;">{rng} — {lbl}</span>{mark}'
            f'<br><span style="color:#555;font-size:11px;">{desc}</span></div>',
            unsafe_allow_html=True,
        )

# P/C 선그래프 (VIX 대리 히스토리 + 현재값 강조)
if pc["history"]:
    hist_pc = pd.DataFrame(pc["history"])

    fig_pc = go.Figure()

    # VIX 선 (참고용, 연회색)
    fig_pc.add_trace(go.Scatter(
        x=hist_pc["date"], y=hist_pc["vix"],
        mode="lines",
        line=dict(color="rgba(150,150,200,0.35)", width=1.5, dash="dot"),
        name="VIX (참고)",
        yaxis="y2",
        hovertemplate="%{x|%Y-%m-%d}<br>VIX: <b>%{y:.2f}</b><extra></extra>",
    ))

    # 기준선
    for y_val, lbl, lc in [(0.7, "Greed 0.7", "#00e676"), (0.9, "0.9", "#69f0ae"),
                            (1.0, "중립 1.0", "#ffd600"), (1.3, "Fear 1.3", "#ff5252")]:
        fig_pc.add_hline(
            y=y_val, line_dash="dash", line_color=lc, line_width=1, opacity=0.5,
            annotation_text=lbl, annotation_font_color=lc,
            annotation_position="right",
        )

    # 현재 P/C ratio 수평선 (강조)
    if pc["ratio"] is not None:
        fig_pc.add_hline(
            y=pc["ratio"], line_dash="solid", line_color=pc_color, line_width=2, opacity=0.9,
            annotation_text=f"  현재 {pc['ratio']:.3f}",
            annotation_font_color=pc_color, annotation_font_size=13,
            annotation_position="right",
        )

    fig_pc.update_layout(
        paper_bgcolor="#111126", plot_bgcolor="#0e0e1e",
        height=400, margin=dict(t=16, b=30, l=8, r=100),
        font=dict(color="white", family="Inter"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#888", size=11),
                    orientation="h", x=0, y=1.06),
        hovermode="x unified",
        xaxis=dict(showgrid=False, tickfont=dict(color="#555")),
        yaxis=dict(
            title="P/C Ratio", range=[0, 2.2], showgrid=True, gridcolor="#1a1a2e",
            tickfont=dict(color="#555"), zeroline=False,
        ),
        yaxis2=dict(
            title="VIX", overlaying="y", side="left", showgrid=False,
            tickfont=dict(color="#333"), zeroline=False, showticklabels=False,
        ),
    )

    # 현재 P/C 값 레이블
    if pc["ratio"] is not None:
        fig_pc.add_annotation(
            x=hist_pc["date"].iloc[-1],
            y=pc["ratio"],
            text=f"  <b>{pc['ratio']:.3f}</b>",
            showarrow=False, xanchor="left",
            font=dict(color=pc_color, size=13),
            bgcolor="#111126", bordercolor=pc_color, borderwidth=1, borderpad=4,
        )

    st.plotly_chart(fig_pc, use_container_width=True,
                    config={"scrollZoom": False, "doubleClick": "reset+autosize", "displayModeBar": False})
    st.caption("※ P/C Ratio: 오늘 SPY+QQQ 옵션 체인 기준 · 히스토리는 VIX 참고선으로 표시")

# ════════════════════════════════════════════════════════════════════
# 3. VIX — investing.com 스타일
# ════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">VIX 공포지수 — CBOE Volatility Index</div>', unsafe_allow_html=True)

v_price = vix_d["price"]
v_chg   = vix_d["change"]
v_pct   = vix_d["pct"]

if v_price < 15:    v_status, v_color = "안정",       "#00e676"
elif v_price < 20:  v_status, v_color = "낮음",       "#69f0ae"
elif v_price < 25:  v_status, v_color = "보통",       "#ffd600"
elif v_price < 30:  v_status, v_color = "주의",       "#ff9100"
elif v_price < 40:  v_status, v_color = "공포",       "#ff5252"
else:               v_status, v_color = "극도의 공포", "#ff1744"

# VIX는 오를수록 나쁨 → 상승=빨강
chg_col = "#ff5252" if v_chg >= 0 else "#00e676"
chg_sym = "▲" if v_chg >= 0 else "▼"

st.markdown(f"""
<div style="background:#111126; border:1px solid #1e1e3a; border-radius:16px;
            padding:24px 28px; margin-bottom:16px;">
  <div style="display:flex; align-items:flex-end; gap:20px; flex-wrap:wrap;">
    <div>
      <div style="font-size:12px;color:#555;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">
        CBOE Volatility Index · VIX
      </div>
      <div style="font-size:60px;font-weight:800;color:{v_color};letter-spacing:-1px;line-height:1;">
        {v_price:.2f}
      </div>
    </div>
    <div style="padding-bottom:12px;">
      <div style="font-size:22px;font-weight:700;color:{chg_col};">
        {chg_sym} {abs(v_chg):.2f} &nbsp;({abs(v_pct):.2f}%)
      </div>
      <div style="font-size:14px;font-weight:700;color:{v_color};margin-top:6px;">
        ● {v_status}
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# 지표 바
stats_row = [
    ("시가",       f"{vix_d['open']:.2f}"),
    ("전일 종가",  f"{vix_d['prev_close']:.2f}"),
    ("일중 고가",  f"{vix_d['high']:.2f}"),
    ("일중 저가",  f"{vix_d['low']:.2f}"),
    ("52주 최고",  f"{vix_d['week52_high']:.2f}"),
    ("52주 최저",  f"{vix_d['week52_low']:.2f}"),
    ("3개월 평균", f"{vix_d['avg3m']:.2f}"),
]
s_cols = st.columns(len(stats_row))
for sc, (lbl, val) in zip(s_cols, stats_row):
    sc.markdown(
        f'<div class="stat-box"><div class="stat-val">{val}</div><div class="stat-lbl">{lbl}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# 기간 탭
period_opts = {"1개월": "1mo", "3개월": "3mo", "6개월": "6mo", "1년": "1y"}
sel_period = st.radio("기간", list(period_opts.keys()), index=1,
                       horizontal=True, label_visibility="collapsed")
vix_tab = get_chart_data("^VIX", period=period_opts[sel_period], interval="1d")

# ── investing.com 스타일 선그래프 ─────────────────────────────────────────
if not vix_tab.empty:
    cur_close = vix_tab["close"].iloc[-1]

    fig_v = go.Figure()

    # 면적 채움 선그래프 (연한 파란색 — investing.com 스타일)
    fig_v.add_trace(go.Scatter(
        x=vix_tab.index, y=vix_tab["close"],
        mode="lines",
        line=dict(color="#5b9cf6", width=2),
        fill="tozeroy",
        fillcolor="rgba(91,156,246,0.12)",
        name="VIX",
        hovertemplate="%{x|%Y-%m-%d}<br>VIX: <b>%{y:.2f}</b><extra></extra>",
    ))

    # MA20
    if len(vix_tab) >= 20:
        ma20 = vix_tab["close"].rolling(20).mean()
        fig_v.add_trace(go.Scatter(
            x=vix_tab.index, y=ma20,
            mode="lines", line=dict(color="#ff9100", width=1.5, dash="dot"),
            name="MA20", opacity=0.8,
            hovertemplate="MA20: %{y:.2f}<extra></extra>",
        ))

    # 기준선
    for y_val, lbl, lc in [(20, "주의 20", "#ffd600"), (30, "공포 30", "#ff5252")]:
        fig_v.add_hline(
            y=y_val, line_dash="dash", line_color=lc, line_width=1, opacity=0.6,
            annotation_text=lbl, annotation_font_color=lc,
            annotation_position="right",
        )

    # 현재값 레이블 (오른쪽 끝 강조)
    fig_v.add_annotation(
        x=vix_tab.index[-1], y=cur_close,
        text=f"  <b>{cur_close:.2f}</b>",
        showarrow=False, xanchor="left",
        font=dict(color=v_color, size=13, family="Inter"),
        bgcolor="#111126", bordercolor=v_color, borderwidth=1, borderpad=4,
    )

    fig_v.update_layout(
        paper_bgcolor="#111126", plot_bgcolor="#0e0e1e",
        height=500, margin=dict(t=10, b=30, l=8, r=90),
        font=dict(color="white", family="Inter"),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#888", size=11),
                    orientation="h", x=0, y=1.04),
        hovermode="x unified",
        xaxis=dict(showgrid=False, tickfont=dict(color="#555"), showline=False,
                   rangeslider=dict(visible=False)),
        yaxis=dict(showgrid=True, gridcolor="#1a1a2e", tickfont=dict(color="#555"),
                   showline=False, zeroline=False),
    )
    st.plotly_chart(fig_v, use_container_width=True,
                    config={"scrollZoom": False, "doubleClick": "reset+autosize", "displayModeBar": False})

    # 52주 레인지
    w52h = vix_d["week52_high"]
    w52l = vix_d["week52_low"]
    if w52h > w52l > 0:
        ratio_52 = min(100, max(0, (v_price - w52l) / (w52h - w52l) * 100))
        st.markdown(f"""
        <div style="background:#111126;border:1px solid #1e1e3a;border-radius:10px;
                    padding:14px 18px;margin-top:6px;">
          <div style="display:flex;justify-content:space-between;
                      font-size:11px;color:#555;margin-bottom:8px;letter-spacing:0.8px;">
            <span>52주 최저 &nbsp; {w52l:.2f}</span>
            <span style="color:{v_color};font-weight:700;">현재 {v_price:.2f} &nbsp; ({ratio_52:.0f}%)</span>
            <span>52주 최고 &nbsp; {w52h:.2f}</span>
          </div>
          <div style="background:#1a1a2e;border-radius:4px;height:8px;">
            <div style="background:{v_color};height:100%;border-radius:4px;width:{ratio_52:.1f}%;"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

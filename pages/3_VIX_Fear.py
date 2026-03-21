"""pages/3_VIX_Fear.py — Fear/Greed + Put/Call + VIX (investing.com 스타일)"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from utils import get_fear_greed, get_vix_history, get_put_call_ratio, get_vix_detail, get_chart_data

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
        st.cache_data.clear()
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
        height=320, margin=dict(t=130, b=60, l=20, r=20),
        font={"color": "white"},
    )
    st.plotly_chart(fig_fg, use_container_width=True)

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
        height=200, margin=dict(t=10, b=10, l=8, r=60),
        xaxis=dict(showgrid=False, tickfont=dict(color="#444")),
        yaxis=dict(range=[0,115], showgrid=False, tickfont=dict(color="#444")),
    )
    st.plotly_chart(fig_fh, use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# 2. Put/Call Ratio
# ════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">Put / Call Ratio (SPY + QQQ)</div>', unsafe_allow_html=True)

col_pc1, col_pc2, col_pc3 = st.columns([1, 1, 2])

with col_pc1:
    if pc["ratio"] is not None:
        r = pc["ratio"]
        pc_color = "#00e5ff" if r<0.7 else "#00e676" if r<0.9 else "#ffd600" if r<1.1 else "#ff9100" if r<1.3 else "#ff5252"
        fig_pc = go.Figure(go.Indicator(
            mode="gauge+number",
            value=r,
            number={"font": {"color": pc_color, "size": 52}, "valueformat": ".3f"},
            title={"text": f"Put/Call Ratio<br><span style='font-size:13px;color:{pc_color}'>{pc['label']}</span>",
                   "font": {"color": "#ccc", "size": 14}},
            gauge={
                "axis": {"range": [0, 2.0], "tickcolor": "#333", "tickfont": {"color": "#444"}, "dtick": 0.5},
                "bar": {"color": pc_color, "thickness": 0.25},
                "bgcolor": "#0d0d1e", "borderwidth": 0,
                "steps": [
                    {"range": [0.0, 0.7], "color": "#002a2a"},
                    {"range": [0.7, 0.9], "color": "#002a0f"},
                    {"range": [0.9, 1.1], "color": "#2a2500"},
                    {"range": [1.1, 1.3], "color": "#2a1000"},
                    {"range": [1.3, 2.0], "color": "#2a0007"},
                ],
                "threshold": {"line": {"color": "#fff", "width": 2}, "thickness": 0.85, "value": r},
            },
        ))
        fig_pc.update_layout(
            paper_bgcolor="#111126", plot_bgcolor="#111126",
            height=300, margin=dict(t=120, b=50, l=20, r=20),
            font={"color": "white"},
        )
        st.plotly_chart(fig_pc, use_container_width=True)
    else:
        st.info("장 외 시간이거나 데이터 로딩 중입니다.")

with col_pc2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box" style="border-left:3px solid #ff5252;margin-bottom:10px"><div class="stat-val" style="color:#ff5252">{pc["put_vol"]:,}</div><div class="stat-lbl">Put 거래량</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box" style="border-left:3px solid #00e676"><div class="stat-val" style="color:#00e676">{pc["call_vol"]:,}</div><div class="stat-lbl">Call 거래량</div></div>', unsafe_allow_html=True)

with col_pc3:
    st.markdown("<br>", unsafe_allow_html=True)
    guide = [
        ("< 0.7",  "Extreme Greed", "#00e5ff", "콜 매수 급증, 시장 과열 신호"),
        ("0.7–0.9","Greed",         "#00e676", "낙관적 심리, 콜 옵션 우세"),
        ("0.9–1.1","Neutral",       "#ffd600", "균형 상태, 방향성 불확실"),
        ("1.1–1.3","Fear",          "#ff9100", "풋 증가, 하락 헤지 수요 증가"),
        ("> 1.3",  "Extreme Fear",  "#ff5252", "강한 패닉 헤지, 반등 가능성"),
    ]
    cur_lbl = pc["label"] if pc["ratio"] else ""
    for rng, lbl, color, desc in guide:
        is_cur = (lbl == cur_lbl)
        bg  = "#1a1a35" if is_cur else "#111126"
        bdr = f"border:1.5px solid {color}" if is_cur else f"border-left:3px solid {color}"
        mark = f' <span style="color:{color};font-weight:800">◀</span>' if is_cur else ""
        st.markdown(
            f'<div style="padding:9px 14px;margin:5px 0;background:{bg};{bdr};border-radius:9px;">'
            f'<span style="color:{color};font-weight:700">{rng} — {lbl}</span>{mark}'
            f'<br><span style="color:#555;font-size:12px">{desc}</span></div>',
            unsafe_allow_html=True,
        )

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

# 캔들차트
if not vix_tab.empty:
    fig_v = make_subplots(rows=2, cols=1, shared_xaxes=True,
                          vertical_spacing=0.02, row_heights=[0.78, 0.22])

    fig_v.add_trace(go.Candlestick(
        x=vix_tab.index, open=vix_tab["open"], high=vix_tab["high"],
        low=vix_tab["low"], close=vix_tab["close"],
        increasing_line_color="#ff5252", increasing_fillcolor="#ff5252",
        decreasing_line_color="#00e676", decreasing_fillcolor="#00e676",
        name="VIX",
    ), row=1, col=1)

    if len(vix_tab) >= 20:
        ma20 = vix_tab["close"].rolling(20).mean()
        std  = vix_tab["close"].rolling(20).std()
        fig_v.add_trace(go.Scatter(x=vix_tab.index, y=ma20,
            line=dict(color="#4f8ef7", width=1.5), name="MA20", opacity=0.8), row=1, col=1)
        fig_v.add_trace(go.Scatter(x=vix_tab.index, y=ma20+2*std,
            line=dict(color="#cc44ff", width=1, dash="dot"), name="BB+2σ", opacity=0.5), row=1, col=1)
        fig_v.add_trace(go.Scatter(x=vix_tab.index, y=ma20-2*std,
            line=dict(color="#cc44ff", width=1, dash="dot"), name="BB-2σ",
            fill="tonexty", fillcolor="rgba(204,68,255,0.04)", opacity=0.5), row=1, col=1)

    for y_val, lbl, lc in [(20,"주의 20","#ffd600"),(30,"공포 30","#ff5252")]:
        fig_v.add_hline(y=y_val, line_dash="dot", line_color=lc, opacity=0.5,
                        annotation_text=lbl, annotation_font_color=lc,
                        annotation_position="right", row=1, col=1)

    v_changes = vix_tab["close"].pct_change() * 100
    fig_v.add_trace(go.Bar(
        x=vix_tab.index, y=v_changes.abs(),
        marker_color=["#ff5252" if c>=0 else "#00e676" for c in v_changes.fillna(0)],
        name="일변화%", opacity=0.7,
    ), row=2, col=1)

    fig_v.update_layout(
        paper_bgcolor="#111126", plot_bgcolor="#0e0e1e",
        height=480, margin=dict(t=10, b=10, l=8, r=80),
        font=dict(color="white", family="Inter"),
        legend=dict(bgcolor="#111126", bordercolor="#1e1e3a", borderwidth=1,
                    font=dict(color="#888", size=11), orientation="h", x=0, y=1.02),
        xaxis_rangeslider_visible=False,
    )
    fig_v.update_xaxes(showgrid=False, tickfont=dict(color="#444"))
    fig_v.update_yaxes(showgrid=True, gridcolor="#1a1a30", tickfont=dict(color="#444"))
    st.plotly_chart(fig_v, use_container_width=True)

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

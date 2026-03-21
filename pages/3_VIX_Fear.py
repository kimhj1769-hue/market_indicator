"""pages/3_VIX_Fear.py — CNN 스타일 Fear/Greed + Put/Call + VIX"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils import get_fear_greed, get_vix_history, get_put_call_ratio, get_vix_detail

st.set_page_config(page_title="VIX & Fear", page_icon="🌡️", layout="wide")

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
  .level-row {
    padding: 9px 14px; margin: 4px 0;
    background: #111126; border-radius: 9px;
    display: flex; justify-content: space-between; align-items: center;
  }
  .stat-box {
    background: #111126; border: 1px solid #1e1e3a;
    border-radius: 12px; padding: 18px; text-align: center;
  }
  .stat-val { font-size: 30px; font-weight: 800; }
  .stat-lbl { font-size: 11px; color: #555; margin-top: 6px; letter-spacing: 0.8px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# ── 헤더 ──────────────────────────────────────────────────────────────────
col_title, col_per, col_btn = st.columns([3, 2, 1])
with col_title:
    st.markdown("## 🌡️ Fear & Greed · VIX · Put/Call")
with col_per:
    period = st.select_slider("VIX 기간", options=["1mo","3mo","6mo","1y"], value="3mo",
                               label_visibility="collapsed")
with col_btn:
    if st.button("⟳  Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with st.spinner(""):
    fg     = get_fear_greed()
    vix    = get_vix_history(period=period)
    pc     = get_put_call_ratio()
    vix_d  = get_vix_detail()


# ════════════════════════════════════════════════════════════════════════════
# 1. CNN 스타일 Fear & Greed 게이지
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">Fear &amp; Greed Index</div>', unsafe_allow_html=True)

fg_val = fg["value"]
fg_lbl = fg["label"]
if fg_val <= 25:   fg_color = "#ff5252"
elif fg_val <= 45: fg_color = "#ff9100"
elif fg_val <= 55: fg_color = "#ffd600"
elif fg_val <= 75: fg_color = "#00e676"
else:              fg_color = "#00e5ff"


def make_cnn_gauge(value: int, color: str) -> go.Figure:
    fig = go.Figure()
    zones = [
        (0,  25,  "#2a0007", "#ff5252", "Extreme\nFear"),
        (25, 45,  "#2a1000", "#ff9100", "Fear"),
        (45, 55,  "#2a2500", "#ffd600", "Neutral"),
        (55, 75,  "#002a0f", "#00e676", "Greed"),
        (75, 100, "#002a2a", "#00e5ff", "Extreme\nGreed"),
    ]
    for z_min, z_max, z_bg, z_fg, z_lbl in zones:
        thetas = np.linspace(180 - z_min*1.8, 180 - z_max*1.8, 40)
        r_o, r_i = 1.0, 0.68
        xo = r_o * np.cos(np.radians(thetas))
        yo = r_o * np.sin(np.radians(thetas))
        xi = r_i * np.cos(np.radians(thetas[::-1]))
        yi = r_i * np.sin(np.radians(thetas[::-1]))
        fig.add_trace(go.Scatter(
            x=list(xo)+list(xi), y=list(yo)+list(yi),
            fill="toself", fillcolor=z_bg,
            line=dict(color="#0d0d1e", width=1.5),
            mode="lines", hoverinfo="skip", showlegend=False,
        ))
        mid = (180 - z_min*1.8 + 180 - z_max*1.8) / 2
        lx = 0.86 * np.cos(np.radians(mid))
        ly = 0.86 * np.sin(np.radians(mid))
        fig.add_annotation(
            x=lx, y=ly, text=z_lbl.replace("\n","<br>"),
            showarrow=False, font=dict(color=z_fg, size=9, family="Inter"),
            align="center",
        )

    # 바늘
    angle = 180 - value * 1.8
    nx = 0.60 * np.cos(np.radians(angle))
    ny = 0.60 * np.sin(np.radians(angle))
    fig.add_trace(go.Scatter(
        x=[0, nx], y=[0, ny], mode="lines",
        line=dict(color=color, width=3.5), hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode="markers",
        marker=dict(size=12, color=color, symbol="circle",
                    line=dict(color="#0d0d1e", width=2)),
        hoverinfo="skip", showlegend=False,
    ))

    # 중앙 숫자
    fig.add_annotation(x=0, y=-0.18, showarrow=False, xanchor="center",
        text=f'<span style="font-size:52px;font-weight:800;color:{color};font-family:Inter">{value}</span>')
    fig.add_annotation(x=0, y=-0.40, showarrow=False, xanchor="center",
        text=f'<span style="font-size:15px;color:{color};font-weight:700;font-family:Inter">{fg_lbl}</span>')

    # 눈금
    for v, lbl in [(0,"0"),(50,"50"),(100,"100")]:
        a = 180 - v * 1.8
        fig.add_annotation(
            x=1.14*np.cos(np.radians(a)), y=1.14*np.sin(np.radians(a)),
            text=lbl, showarrow=False,
            font=dict(color="#444", size=10, family="Inter"), xanchor="center",
        )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=330, margin=dict(t=10, b=70, l=10, r=10),
        xaxis=dict(range=[-1.3,1.3], visible=False),
        yaxis=dict(range=[-0.65,1.15], visible=False, scaleanchor="x"),
        showlegend=False,
    )
    return fig


col_gauge, col_info = st.columns([1, 1])

with col_gauge:
    st.plotly_chart(make_cnn_gauge(fg_val, fg_color), use_container_width=True)
    if len(fg["history"]) > 1:
        delta = fg_val - fg["history"][1]["value"]
        d_col = "#00e676" if delta >= 0 else "#ff5252"
        d_sym = "▲" if delta >= 0 else "▼"
        st.markdown(
            f'<p style="text-align:center;color:{d_col};font-size:13px;margin-top:-20px">'
            f'{d_sym} {abs(delta)}pt (전일 대비)</p>',
            unsafe_allow_html=True,
        )

with col_info:
    st.markdown("<br>", unsafe_allow_html=True)
    levels = [
        ("0–24",   "Extreme Fear", "#ff5252", "😱"),
        ("25–44",  "Fear",         "#ff9100", "😨"),
        ("45–55",  "Neutral",      "#ffd600", "😐"),
        ("56–75",  "Greed",        "#00e676", "😊"),
        ("76–100", "Extreme Greed","#00e5ff", "🤑"),
    ]
    for rng, lbl, color, emoji in levels:
        is_cur = fg_lbl.lower().replace(" ","") in lbl.lower().replace(" ","")
        bg   = "#1a1a35" if is_cur else "#111126"
        bdr  = f"border:1.5px solid {color}" if is_cur else f"border-left:3px solid {color}"
        mark = f'<span style="color:{color};font-weight:800;margin-left:6px">◀ 현재</span>' if is_cur else ""
        st.markdown(
            f'<div style="padding:10px 14px;margin:5px 0;background:{bg};'
            f'{bdr};border-radius:9px;color:white;">'
            f'{emoji} <b style="color:{color}">{lbl}</b>'
            f'<span style="color:#444;font-size:12px;margin-left:6px">({rng})</span>'
            f'{mark}</div>',
            unsafe_allow_html=True,
        )

    # 7일 미니 카드
    if len(fg["history"]) >= 7:
        st.markdown("<br>", unsafe_allow_html=True)
        mini_cols = st.columns(7)
        for i, mc in enumerate(mini_cols):
            h = fg["history"][6-i]
            v = h["value"]
            d = h["date"].strftime("%m/%d")
            c = "#ff5252" if v<=25 else "#ff9100" if v<=45 else "#ffd600" if v<=55 else "#00e676" if v<=75 else "#00e5ff"
            mc.markdown(
                f'<div style="text-align:center;background:#111126;border-radius:7px;'
                f'padding:7px 2px;border-top:2.5px solid {c};">'
                f'<div style="font-size:17px;font-weight:800;color:{c}">{v}</div>'
                f'<div style="font-size:9px;color:#444;margin-top:2px">{d}</div></div>',
                unsafe_allow_html=True,
            )


# ════════════════════════════════════════════════════════════════════════════
# 2. Fear & Greed 30일 히스토리
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">30일 추이</div>', unsafe_allow_html=True)

if fg["history"]:
    hist_df = pd.DataFrame(fg["history"]).sort_values("date")
    fig_fh  = go.Figure()
    fig_fh.add_trace(go.Bar(
        x=hist_df["date"], y=hist_df["value"],
        marker_color=[
            "#ff5252" if v<=25 else "#ff9100" if v<=45 else
            "#ffd600" if v<=55 else "#00e676" if v<=75 else "#00e5ff"
            for v in hist_df["value"]
        ],
        text=[str(v) for v in hist_df["value"]],
        textposition="outside", textfont=dict(color="#666", size=9),
    ))
    fig_fh.add_hline(y=50, line_dash="dot", line_color="#333",
                     annotation_text="Neutral", annotation_font_color="#444",
                     annotation_position="right")
    fig_fh.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0e0e20",
        height=200, margin=dict(t=10, b=10, l=8, r=60),
        xaxis=dict(showgrid=False, tickfont=dict(color="#444")),
        yaxis=dict(range=[0,115], showgrid=False, tickfont=dict(color="#444")),
    )
    st.plotly_chart(fig_fh, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# 3. Put/Call Ratio
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">Put / Call Ratio &nbsp;(SPY + QQQ 옵션)</div>',
            unsafe_allow_html=True)

col_pc1, col_pc2, col_pc3 = st.columns([1, 1, 2])

with col_pc1:
    if pc["ratio"] is not None:
        r = pc["ratio"]
        if r < 0.7:    pc_color = "#00e5ff"
        elif r < 0.9:  pc_color = "#00e676"
        elif r < 1.1:  pc_color = "#ffd600"
        elif r < 1.3:  pc_color = "#ff9100"
        else:          pc_color = "#ff5252"

        fig_pc = go.Figure(go.Indicator(
            mode="gauge+number",
            value=r,
            number={"font": {"color": pc_color, "size": 50, "family": "Inter"},
                    "valueformat": ".3f"},
            title={
                "text": f"Put/Call Ratio<br><span style='font-size:13px;color:{pc_color}'>{pc['label']}</span>",
                "font": {"color": "#ccc", "size": 14},
            },
            gauge={
                "axis": {"range": [0, 2.0], "tickcolor": "#333",
                         "tickfont": {"color": "#444"}, "dtick": 0.5},
                "bar": {"color": pc_color, "thickness": 0.22},
                "bgcolor": "#0d0d1e", "borderwidth": 0,
                "steps": [
                    {"range": [0.0, 0.7], "color": "#002a2a"},
                    {"range": [0.7, 0.9], "color": "#002a0f"},
                    {"range": [0.9, 1.1], "color": "#2a2500"},
                    {"range": [1.1, 1.3], "color": "#2a1000"},
                    {"range": [1.3, 2.0], "color": "#2a0007"},
                ],
                "threshold": {"line": {"color": "#fff", "width": 2},
                              "thickness": 0.8, "value": r},
            },
        ))
        fig_pc.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=260, margin=dict(t=80, b=10, l=20, r=20),
            font={"color": "white"},
        )
        st.plotly_chart(fig_pc, use_container_width=True)
    else:
        st.info("장 외 시간이거나 데이터 로딩 중입니다.")

with col_pc2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="stat-box" style="border-left:3px solid #ff5252;margin-bottom:10px">'
        f'<div class="stat-val" style="color:#ff5252">{pc["put_vol"]:,}</div>'
        f'<div class="stat-lbl">Put 거래량</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="stat-box" style="border-left:3px solid #00e676">'
        f'<div class="stat-val" style="color:#00e676">{pc["call_vol"]:,}</div>'
        f'<div class="stat-lbl">Call 거래량</div></div>',
        unsafe_allow_html=True,
    )

with col_pc3:
    st.markdown("<br>", unsafe_allow_html=True)
    guide = [
        ("< 0.7",  "Extreme Greed", "#00e5ff", "콜 매수 급증, 시장 과열 신호"),
        ("0.7–0.9","Greed",         "#00e676", "낙관적 심리, 콜 옵션 우세"),
        ("0.9–1.1","Neutral",       "#ffd600", "균형 상태, 방향성 불확실"),
        ("1.1–1.3","Fear",          "#ff9100", "풋 증가, 하락 헤지 수요 증가"),
        ("> 1.3",  "Extreme Fear",  "#ff5252", "강한 패닉 헤지, 반등 가능성"),
    ]
    is_cur_label = pc["label"] if pc["ratio"] else ""
    for rng, lbl, color, desc in guide:
        is_cur = (lbl == is_cur_label)
        bg  = "#1a1a35" if is_cur else "#111126"
        bdr = f"border:1.5px solid {color}" if is_cur else f"border-left:3px solid {color}"
        mark = f' <span style="color:{color};font-weight:800">◀</span>' if is_cur else ""
        st.markdown(
            f'<div style="padding:9px 14px;margin:5px 0;background:{bg};'
            f'{bdr};border-radius:9px;">'
            f'<span style="color:{color};font-weight:700">{rng} — {lbl}</span>{mark}'
            f'<br><span style="color:#555;font-size:12px">{desc}</span></div>',
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════════════════════
# 4. VIX — investing.com 스타일
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">VIX 공포지수 (CBOE Volatility Index)</div>',
            unsafe_allow_html=True)

# ── 현재가 헤더 ──────────────────────────────────────────────────────────
v_price = vix_d["price"]
v_chg   = vix_d["change"]
v_pct   = vix_d["pct"]

if v_price < 15:    v_status, v_color = "안정",        "#00e676"
elif v_price < 20:  v_status, v_color = "낮음",        "#69f0ae"
elif v_price < 25:  v_status, v_color = "보통",        "#ffd600"
elif v_price < 30:  v_status, v_color = "주의",        "#ff9100"
elif v_price < 40:  v_status, v_color = "공포",        "#ff5252"
else:               v_status, v_color = "극도의 공포",  "#ff1744"

chg_col = "#ff5252" if v_chg >= 0 else "#00e676"   # VIX 상승=나쁨=빨강
chg_sym = "▲" if v_chg >= 0 else "▼"

st.markdown(f"""
<div style="background:linear-gradient(135deg,#111126,#0e0e1e);
            border:1px solid #1e1e3a; border-radius:16px;
            padding:24px 28px; margin-bottom:16px;">
  <div style="display:flex; align-items:flex-end; gap:16px; flex-wrap:wrap;">
    <div>
      <div style="font-size:13px;color:#555;letter-spacing:1px;
                  text-transform:uppercase;margin-bottom:6px;">
        CBOE Volatility Index · VIX
      </div>
      <div style="font-size:56px;font-weight:800;color:{v_color};
                  letter-spacing:-1px;line-height:1;">
        {v_price:.2f}
      </div>
    </div>
    <div style="padding-bottom:10px;">
      <div style="font-size:22px;font-weight:700;color:{chg_col};">
        {chg_sym} {abs(v_chg):.2f} ({abs(v_pct):.2f}%)
      </div>
      <div style="font-size:13px;font-weight:700;color:{v_color};
                  margin-top:4px;letter-spacing:0.5px;">
        ● {v_status}
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── 주요 지표 바 ─────────────────────────────────────────────────────────
stats_items = [
    ("시가",        f"{vix_d['open']:.2f}"),
    ("전일 종가",   f"{vix_d['prev_close']:.2f}"),
    ("일중 고가",   f"{vix_d['high']:.2f}"),
    ("일중 저가",   f"{vix_d['low']:.2f}"),
    ("52주 최고",   f"{vix_d['week52_high']:.2f}"),
    ("52주 최저",   f"{vix_d['week52_low']:.2f}"),
    ("3개월 평균",  f"{vix_d['avg3m']:.2f}"),
]

cols_s = st.columns(len(stats_items))
for col, (lbl, val) in zip(cols_s, stats_items):
    col.markdown(
        f'<div style="background:#111126;border:1px solid #1e1e3a;'
        f'border-radius:10px;padding:12px 10px;text-align:center;">'
        f'<div style="font-size:16px;font-weight:800;color:#fff;">{val}</div>'
        f'<div style="font-size:10px;color:#555;margin-top:5px;'
        f'letter-spacing:0.8px;text-transform:uppercase;">{lbl}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── 기간 탭 선택 ─────────────────────────────────────────────────────────
period_map = {
    "1일": ("5d", "15m"),
    "1주": ("1mo", "1d"),
    "1개월": ("1mo", "1d"),
    "3개월": ("3mo", "1d"),
    "6개월": ("6mo", "1d"),
    "1년":   ("1y",  "1d"),
}
tab_labels = list(period_map.keys())
selected_tab = st.radio("기간", tab_labels, index=3,
                         horizontal=True, label_visibility="collapsed")
v_period, v_interval = period_map[selected_tab]
vix_tab = get_vix_history(period=v_period) if v_period != "5d" else \
          __import__("utils").get_chart_data("^VIX", period=v_period, interval=v_interval)

# ── 캔들 + 볼린저 차트 ───────────────────────────────────────────────────
if not vix_tab.empty:
    from plotly.subplots import make_subplots

    fig_v2 = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.02, row_heights=[0.78, 0.22],
    )

    # 캔들스틱
    fig_v2.add_trace(go.Candlestick(
        x=vix_tab.index,
        open=vix_tab["open"], high=vix_tab["high"],
        low=vix_tab["low"],   close=vix_tab["close"],
        increasing_line_color="#ff5252", increasing_fillcolor="#ff5252",
        decreasing_line_color="#00e676", decreasing_fillcolor="#00e676",
        name="VIX",
    ), row=1, col=1)

    # MA20
    if len(vix_tab) >= 20:
        ma20 = vix_tab["close"].rolling(20).mean()
        fig_v2.add_trace(go.Scatter(
            x=vix_tab.index, y=ma20,
            line=dict(color="#4f8ef7", width=1.5), name="MA20", opacity=0.8,
        ), row=1, col=1)

    # 볼린저밴드
    if len(vix_tab) >= 20:
        std = vix_tab["close"].rolling(20).std()
        fig_v2.add_trace(go.Scatter(
            x=vix_tab.index, y=ma20 + 2 * std,
            line=dict(color="#cc44ff", width=1, dash="dot"), name="BB+2σ", opacity=0.6,
        ), row=1, col=1)
        fig_v2.add_trace(go.Scatter(
            x=vix_tab.index, y=ma20 - 2 * std,
            line=dict(color="#cc44ff", width=1, dash="dot"), name="BB-2σ",
            fill="tonexty", fillcolor="rgba(204,68,255,0.04)", opacity=0.6,
        ), row=1, col=1)

    # 기준선
    for y_val, lbl, col_line in [
        (20, "주의 20", "#ffd600"),
        (30, "공포 30", "#ff5252"),
    ]:
        fig_v2.add_hline(y=y_val, line_dash="dot", line_color=col_line, opacity=0.5,
                         annotation_text=lbl, annotation_font_color=col_line,
                         annotation_position="right", row=1, col=1)

    # 거래량 대신 변동성 바 (VIX 전일대비 변화율)
    v_changes = vix_tab["close"].pct_change() * 100
    bar_colors = ["#ff5252" if c >= 0 else "#00e676" for c in v_changes.fillna(0)]
    fig_v2.add_trace(go.Bar(
        x=vix_tab.index, y=v_changes.abs(),
        marker_color=bar_colors, name="일변화(%)", opacity=0.7,
    ), row=2, col=1)

    fig_v2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0b0b1a",
        height=480,
        margin=dict(t=10, b=10, l=8, r=80),
        font=dict(color="white", family="Inter"),
        legend=dict(
            bgcolor="#111126", bordercolor="#1e1e3a", borderwidth=1,
            font=dict(color="#888", size=11),
            orientation="h", x=0, y=1.02,
        ),
        xaxis_rangeslider_visible=False,
        xaxis2=dict(showgrid=False, tickfont=dict(color="#444")),
        yaxis=dict(showgrid=True, gridcolor="#1a1a30",
                   tickfont=dict(color="#444"), zeroline=False),
        yaxis2=dict(showgrid=False, tickfont=dict(color="#444")),
    )
    fig_v2.update_xaxes(showgrid=False)

    st.plotly_chart(fig_v2, use_container_width=True)

    # ── 52주 레인지 바 ────────────────────────────────────────────────────
    w52h = vix_d["week52_high"]
    w52l = vix_d["week52_low"]
    if w52h > w52l:
        ratio_52 = (v_price - w52l) / (w52h - w52l) * 100
        st.markdown(f"""
        <div style="background:#111126;border:1px solid #1e1e3a;border-radius:10px;
                    padding:14px 18px;margin-top:4px;">
          <div style="display:flex;justify-content:space-between;
                      font-size:11px;color:#555;margin-bottom:6px;
                      letter-spacing:0.8px;text-transform:uppercase;">
            <span>52주 최저  {w52l:.2f}</span>
            <span style="color:{v_color};font-weight:700;">
              현재  {v_price:.2f}  ({ratio_52:.0f}%)
            </span>
            <span>52주 최고  {w52h:.2f}</span>
          </div>
          <div style="background:#1a1a2e;border-radius:4px;height:8px;position:relative;">
            <div style="background:{v_color};height:100%;border-radius:4px;
                        width:{ratio_52:.1f}%;"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

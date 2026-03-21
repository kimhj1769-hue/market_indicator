"""pages/3_VIX_Fear.py — CNN 스타일 Fear/Greed + Put/Call + VIX"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils import get_fear_greed, get_vix_history, get_put_call_ratio

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
    fg  = get_fear_greed()
    vix = get_vix_history(period=period)
    pc  = get_put_call_ratio()


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
# 4. VIX 차트
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-title">VIX 공포지수 추이</div>', unsafe_allow_html=True)

if not vix.empty:
    cur_vix = vix["close"].iloc[-1]
    if cur_vix < 20:   vc = "#00e676"
    elif cur_vix < 30: vc = "#ffd600"
    else:              vc = "#ff5252"

    fig_vix = go.Figure()
    # 공포 구간 배경
    fear_zone = vix[vix["close"] > 30]
    if not fear_zone.empty:
        fig_vix.add_vrect(
            x0=fear_zone.index[0], x1=fear_zone.index[-1],
            fillcolor="rgba(255,82,82,0.07)", line_width=0,
            annotation_text="공포구간", annotation_font_color="#ff5252",
            annotation_position="top left",
        )
    fig_vix.add_trace(go.Scatter(
        x=vix.index, y=vix["close"],
        mode="lines", line=dict(color=vc, width=2),
        fill="tozeroy", fillcolor=f"rgba{tuple(list(int(vc.lstrip('#')[i:i+2],16) for i in (0,2,4))+[0])}".replace(", 0)",", 0.08)"),
        name="VIX",
    ))
    fig_vix.add_hline(y=20, line_dash="dot", line_color="#ffd600", opacity=0.5,
                      annotation_text="주의 20", annotation_font_color="#ffd600",
                      annotation_position="right")
    fig_vix.add_hline(y=30, line_dash="dot", line_color="#ff5252", opacity=0.5,
                      annotation_text="공포 30", annotation_font_color="#ff5252",
                      annotation_position="right")
    fig_vix.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0e0e20",
        height=260, margin=dict(t=10, b=10, l=8, r=70),
        font=dict(color="white"),
        xaxis=dict(showgrid=False, tickfont=dict(color="#444")),
        yaxis=dict(showgrid=True, gridcolor="#1a1a30", tickfont=dict(color="#444")),
        showlegend=False,
    )
    st.plotly_chart(fig_vix, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val in [
        (c1, "현재 VIX",  f"{vix['close'].iloc[-1]:.2f}"),
        (c2, "기간 최고", f"{vix['high'].max():.2f}"),
        (c3, "기간 최저", f"{vix['low'].min():.2f}"),
        (c4, "평균",      f"{vix['close'].mean():.2f}"),
    ]:
        col.markdown(
            f'<div class="stat-box"><div class="stat-val" style="color:#ffd600">{val}</div>'
            f'<div class="stat-lbl">{label}</div></div>',
            unsafe_allow_html=True,
        )

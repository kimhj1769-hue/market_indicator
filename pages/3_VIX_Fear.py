"""
pages/3_VIX_Fear.py — CNN 스타일 Fear/Greed + Put/Call + VIX
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from utils import get_fear_greed, get_vix_history, get_put_call_ratio

st.set_page_config(page_title="VIX & Fear", page_icon="🌡️", layout="wide")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #0d0d1a; }
    .block-container { padding-top: 1rem; }
    .section-title {
        color: #ccc; font-size: 18px; font-weight: 600;
        margin: 24px 0 10px 0; border-left: 3px solid #4f8ef7;
        padding-left: 10px;
    }
    .cnn-label {
        text-align: center; font-size: 14px; color: #aaa; margin-top: -8px;
    }
    .stat-box {
        background: #1e1e2e; border-radius: 10px; padding: 14px 18px;
        text-align: center; border: 1px solid #2a2a3e;
    }
    .stat-val { font-size: 28px; font-weight: 700; }
    .stat-lbl { font-size: 12px; color: #888; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🌡️ Fear & Greed — CNN 스타일")

col_per, col_btn = st.columns([3, 1])
with col_per:
    period = st.select_slider("VIX 기간", options=["1mo","3mo","6mo","1y"], value="3mo")
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with st.spinner("데이터 로딩 중..."):
    fg  = get_fear_greed()
    vix = get_vix_history(period=period)
    pc  = get_put_call_ratio()


# ════════════════════════════════════════════════════════════════════════════
# 1. CNN 스타일 Fear & Greed 게이지
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">😱 Fear & Greed Index — CNN Style</div>',
            unsafe_allow_html=True)

fg_val = fg["value"]
fg_lbl = fg["label"]

# 색상 결정
if fg_val <= 25:   fg_color = "#d63031"
elif fg_val <= 45: fg_color = "#e17055"
elif fg_val <= 55: fg_color = "#fdcb6e"
elif fg_val <= 75: fg_color = "#00b894"
else:              fg_color = "#00cec9"

# CNN 스타일 게이지 (Plotly Indicator 커스텀)
def make_cnn_gauge(value: int, color: str) -> go.Figure:
    """CNN Fear & Greed 스타일 반원 게이지."""
    fig = go.Figure()

    # 배경 색상 구간
    zones = [
        (0,  25,  "#3d0010", "Extreme<br>Fear"),
        (25, 45,  "#3d1500", "Fear"),
        (45, 55,  "#2e2800", "Neutral"),
        (55, 75,  "#003d1a", "Greed"),
        (75, 100, "#00291a", "Extreme<br>Greed"),
    ]

    # 바깥 링 (색상 구간)
    for z_min, z_max, z_col, z_lbl in zones:
        theta_min = 180 - (z_min / 100) * 180
        theta_max = 180 - (z_max / 100) * 180
        thetas = np.linspace(theta_min, theta_max, 40)
        r_outer, r_inner = 1.0, 0.72

        xs_outer = r_outer * np.cos(np.radians(thetas))
        ys_outer = r_outer * np.sin(np.radians(thetas))
        xs_inner = r_inner * np.cos(np.radians(thetas[::-1]))
        ys_inner = r_inner * np.sin(np.radians(thetas[::-1]))

        fig.add_trace(go.Scatter(
            x=list(xs_outer) + list(xs_inner),
            y=list(ys_outer) + list(ys_inner),
            fill="toself",
            fillcolor=z_col,
            line=dict(color="#0d0d1a", width=1),
            mode="lines",
            hoverinfo="skip",
            showlegend=False,
        ))

        # 라벨 위치 (중간각도)
        mid_angle = (theta_min + theta_max) / 2
        lx = 0.88 * np.cos(np.radians(mid_angle))
        ly = 0.88 * np.sin(np.radians(mid_angle))
        fig.add_annotation(
            x=lx, y=ly,
            text=z_lbl,
            showarrow=False,
            font=dict(color="white", size=9),
            align="center",
        )

    # 바늘 (needle)
    needle_angle = 180 - (value / 100) * 180
    needle_len = 0.65
    nx = needle_len * np.cos(np.radians(needle_angle))
    ny = needle_len * np.sin(np.radians(needle_angle))

    fig.add_trace(go.Scatter(
        x=[0, nx], y=[0, ny],
        mode="lines",
        line=dict(color=color, width=4),
        hoverinfo="skip",
        showlegend=False,
    ))
    # 바늘 중심점
    fig.add_trace(go.Scatter(
        x=[0], y=[0],
        mode="markers",
        marker=dict(size=14, color=color, symbol="circle"),
        hoverinfo="skip",
        showlegend=False,
    ))

    # 가운데 숫자 & 레이블
    fig.add_annotation(
        x=0, y=-0.22,
        text=f'<span style="font-size:44px;font-weight:700;color:{color}">{value}</span>',
        showarrow=False, xanchor="center", yanchor="middle",
    )
    fig.add_annotation(
        x=0, y=-0.42,
        text=f'<span style="font-size:16px;color:{color};font-weight:600">{fg_lbl}</span>',
        showarrow=False, xanchor="center", yanchor="middle",
    )

    # 0 / 50 / 100 눈금
    for tick_val, tick_lbl in [(0,"0"), (50,"50"), (100,"100")]:
        ta = 180 - (tick_val / 100) * 180
        tx = 1.12 * np.cos(np.radians(ta))
        ty = 1.12 * np.sin(np.radians(ta))
        fig.add_annotation(
            x=tx, y=ty, text=tick_lbl,
            showarrow=False,
            font=dict(color="#888", size=10),
            xanchor="center",
        )

    fig.update_layout(
        paper_bgcolor="#0d0d1a",
        plot_bgcolor="#0d0d1a",
        height=320,
        margin=dict(t=20, b=60, l=20, r=20),
        xaxis=dict(range=[-1.3, 1.3], showgrid=False, zeroline=False,
                   showticklabels=False, visible=False),
        yaxis=dict(range=[-0.65, 1.15], showgrid=False, zeroline=False,
                   showticklabels=False, visible=False, scaleanchor="x"),
        showlegend=False,
    )
    return fig


col_gauge, col_info = st.columns([1, 1])

with col_gauge:
    fig_cnn = make_cnn_gauge(fg_val, fg_color)
    st.plotly_chart(fig_cnn, use_container_width=True)
    # 전일 대비
    if len(fg["history"]) > 1:
        prev_val = fg["history"][1]["value"]
        delta = fg_val - prev_val
        delta_str = f"{'▲' if delta >= 0 else '▼'} {abs(delta)}pt (전일 대비)"
        delta_color = "#00b894" if delta >= 0 else "#d63031"
        st.markdown(
            f'<p style="text-align:center;color:{delta_color};font-size:14px;">{delta_str}</p>',
            unsafe_allow_html=True,
        )

with col_info:
    st.markdown("<br>", unsafe_allow_html=True)
    levels = [
        ("0–24",  "Extreme Fear", "#d63031", "😱"),
        ("25–44", "Fear",         "#e17055", "😨"),
        ("45–55", "Neutral",      "#fdcb6e", "😐"),
        ("56–75", "Greed",        "#00b894", "😊"),
        ("76–100","Extreme Greed","#00cec9", "🤑"),
    ]
    for rng, lbl, color, emoji in levels:
        is_current = fg_lbl.lower().replace(" ", "") in lbl.lower().replace(" ", "")
        border = f"border: 2px solid {color}" if is_current else f"border-left: 4px solid {color}"
        marker = " ◀ 현재" if is_current else ""
        st.markdown(
            f'<div style="padding:8px 14px; margin:5px 0; background:#1e1e2e; '
            f'{border}; border-radius:8px; color:white;">'
            f'{emoji} <b>{lbl}</b> ({rng})'
            f'<span style="color:{color}; font-weight:700">{marker}</span></div>',
            unsafe_allow_html=True,
        )

    # 최근 7일 요약
    if len(fg["history"]) >= 7:
        st.markdown("<br>", unsafe_allow_html=True)
        cols7 = st.columns(7)
        for i, col in enumerate(cols7):
            h = fg["history"][6 - i]
            d = h["date"].strftime("%m/%d")
            v = h["value"]
            c = "#d63031" if v<=25 else "#e17055" if v<=45 else "#fdcb6e" if v<=55 else "#00b894" if v<=75 else "#00cec9"
            col.markdown(
                f'<div style="text-align:center;background:#1e1e2e;border-radius:6px;'
                f'padding:6px 2px;border-top:3px solid {c};">'
                f'<div style="font-size:18px;font-weight:700;color:{c}">{v}</div>'
                f'<div style="font-size:10px;color:#777">{d}</div></div>',
                unsafe_allow_html=True,
            )


# ════════════════════════════════════════════════════════════════════════════
# 2. Fear & Greed 30일 히스토리
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📅 Fear & Greed 30일 추이</div>',
            unsafe_allow_html=True)

if fg["history"]:
    hist_df = pd.DataFrame(fg["history"]).sort_values("date")
    fig_fh  = go.Figure()
    fig_fh.add_trace(go.Bar(
        x=hist_df["date"], y=hist_df["value"],
        marker_color=[
            "#d63031" if v <= 25 else
            "#e17055" if v <= 45 else
            "#fdcb6e" if v <= 55 else
            "#00b894" if v <= 75 else "#00cec9"
            for v in hist_df["value"]
        ],
        text=[f"{v}" for v in hist_df["value"]],
        textposition="outside",
        textfont=dict(color="white", size=10),
    ))
    fig_fh.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5,
                     annotation_text="Neutral 50", annotation_font_color="gray")
    fig_fh.update_layout(
        paper_bgcolor="#0d0d1a", plot_bgcolor="#1e1e2e",
        height=240, margin=dict(t=10, b=20, l=10, r=10),
        xaxis=dict(showgrid=False, tickfont=dict(color="gray")),
        yaxis=dict(range=[0, 115], showgrid=True, gridcolor="#333",
                   tickfont=dict(color="gray")),
    )
    st.plotly_chart(fig_fh, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# 3. Put/Call Ratio
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Put/Call Ratio (SPY+QQQ 옵션)</div>',
            unsafe_allow_html=True)

col_pc1, col_pc2, col_pc3 = st.columns([1, 1, 2])

with col_pc1:
    if pc["ratio"] is not None:
        r = pc["ratio"]
        if r < 0.7:    pc_color = "#00cec9"
        elif r < 0.9:  pc_color = "#00b894"
        elif r < 1.1:  pc_color = "#fdcb6e"
        elif r < 1.3:  pc_color = "#e17055"
        else:          pc_color = "#d63031"

        fig_pc = go.Figure(go.Indicator(
            mode="gauge+number",
            value=r,
            number={"font": {"color": pc_color, "size": 52}, "suffix": ""},
            title={"text": f"Put/Call Ratio<br><span style='font-size:14px;color:{pc_color}'>{pc['label']}</span>",
                   "font": {"color": "white", "size": 15}},
            gauge={
                "axis": {"range": [0, 2.0], "tickcolor": "gray",
                         "tickfont": {"color": "gray"}, "dtick": 0.5},
                "bar":  {"color": pc_color, "thickness": 0.25},
                "bgcolor": "#1e1e2e",
                "bordercolor": "#333",
                "steps": [
                    {"range": [0.0, 0.7], "color": "#00291a"},
                    {"range": [0.7, 0.9], "color": "#003d1a"},
                    {"range": [0.9, 1.1], "color": "#2e2800"},
                    {"range": [1.1, 1.3], "color": "#3d1500"},
                    {"range": [1.3, 2.0], "color": "#3d0010"},
                ],
                "threshold": {"line": {"color": "white", "width": 3},
                              "thickness": 0.75, "value": r},
            },
        ))
        fig_pc.update_layout(
            paper_bgcolor="#0d0d1a", height=260,
            margin=dict(t=60, b=10, l=20, r=20),
            font={"color": "white"},
        )
        st.plotly_chart(fig_pc, use_container_width=True)
    else:
        st.info("옵션 데이터를 불러오는 중이거나 장 외 시간입니다.")

with col_pc2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="stat-box">'
        f'<div class="stat-val" style="color:#e17055">{pc["put_vol"]:,}</div>'
        f'<div class="stat-lbl">Put 거래량</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="stat-box">'
        f'<div class="stat-val" style="color:#00b894">{pc["call_vol"]:,}</div>'
        f'<div class="stat-lbl">Call 거래량</div></div>',
        unsafe_allow_html=True,
    )

with col_pc3:
    # Put/Call 해석 가이드
    st.markdown("<br>", unsafe_allow_html=True)
    guide = [
        ("< 0.7",  "Extreme Greed", "#00cec9", "시장 낙관 과열. 콜 매수 급증."),
        ("0.7–0.9","Greed",         "#00b894", "투자자 낙관. 콜 우세."),
        ("0.9–1.1","Neutral",       "#fdcb6e", "균형. 방향성 불확실."),
        ("1.1–1.3","Fear",          "#e17055", "풋 증가. 헤지 수요 증가."),
        ("> 1.3",  "Extreme Fear",  "#d63031", "강한 하락 헤지. 패닉 매수 가능성."),
    ]
    for ratio_rng, lbl, color, desc in guide:
        is_cur = (pc["label"] == lbl) if pc["ratio"] else False
        bg = "#252540" if is_cur else "#1e1e2e"
        border = f"border: 2px solid {color}" if is_cur else f"border-left: 3px solid {color}"
        st.markdown(
            f'<div style="padding:7px 12px; margin:4px 0; background:{bg}; '
            f'{border}; border-radius:7px;">'
            f'<span style="color:{color};font-weight:700">{ratio_rng} — {lbl}</span>'
            f'<br><span style="color:#aaa;font-size:12px">{desc}</span></div>',
            unsafe_allow_html=True,
        )

# VIX vs Put/Call 복합 차트 (히스토리가 있을 때)
if pc["history"]:
    st.markdown('<div class="section-title">📉 VIX 추이 (Put/Call 기준선 포함)</div>',
                unsafe_allow_html=True)
    hist_df2 = pd.DataFrame(pc["history"])

    fig_combo = go.Figure()
    fig_combo.add_trace(go.Scatter(
        x=hist_df2["date"], y=hist_df2["vix"],
        mode="lines", line=dict(color="#ff9500", width=2),
        fill="tozeroy", fillcolor="rgba(255,149,0,0.1)",
        name="VIX",
    ))
    fig_combo.add_hline(y=20, line_dash="dash", line_color="#fdcb6e", opacity=0.6,
                        annotation_text="주의 20", annotation_font_color="#fdcb6e")
    fig_combo.add_hline(y=30, line_dash="dash", line_color="#d63031", opacity=0.6,
                        annotation_text="공포 30", annotation_font_color="#d63031")
    fig_combo.update_layout(
        paper_bgcolor="#0d0d1a", plot_bgcolor="#1e1e2e",
        height=240, margin=dict(t=10, b=20, l=10, r=10),
        font=dict(color="white"),
        xaxis=dict(showgrid=False, tickfont=dict(color="gray")),
        yaxis=dict(showgrid=True, gridcolor="#333", tickfont=dict(color="gray")),
        showlegend=False,
    )
    st.plotly_chart(fig_combo, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# 4. VIX 캔들차트
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📉 VIX 공포지수 상세</div>',
            unsafe_allow_html=True)

if not vix.empty:
    fig_vix = go.Figure()
    high_fear = vix[vix["close"] > 30]
    if not high_fear.empty:
        fig_vix.add_vrect(
            x0=high_fear.index[0], x1=high_fear.index[-1],
            fillcolor="rgba(214,48,49,0.15)", line_width=0,
            annotation_text="공포구간", annotation_font_color="#d63031",
        )

    fig_vix.add_trace(go.Scatter(
        x=vix.index, y=vix["close"],
        mode="lines",
        line=dict(color="#ff9500", width=2),
        fill="tozeroy",
        fillcolor="rgba(255,149,0,0.1)",
        name="VIX",
    ))
    fig_vix.add_hline(y=20, line_dash="dash", line_color="#fdcb6e", opacity=0.6,
                      annotation_text="주의 20", annotation_font_color="#fdcb6e")
    fig_vix.add_hline(y=30, line_dash="dash", line_color="#d63031", opacity=0.6,
                      annotation_text="공포 30", annotation_font_color="#d63031")
    fig_vix.update_layout(
        paper_bgcolor="#0d0d1a", plot_bgcolor="#1e1e2e",
        height=280, margin=dict(t=10, b=20, l=10, r=10),
        font=dict(color="white"),
        xaxis=dict(showgrid=False, tickfont=dict(color="gray")),
        yaxis=dict(showgrid=True, gridcolor="#333", tickfont=dict(color="gray")),
        showlegend=False,
    )
    st.plotly_chart(fig_vix, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("현재 VIX", f"{vix['close'].iloc[-1]:.2f}")
    c2.metric("기간 최고", f"{vix['high'].max():.2f}")
    c3.metric("기간 최저", f"{vix['low'].min():.2f}")
    c4.metric("평균",      f"{vix['close'].mean():.2f}")

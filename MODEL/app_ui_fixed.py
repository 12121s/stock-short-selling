"""
공매도 반등 타이밍 예측 대시보드
실행: streamlit run app_ui_fixed.py
"""

from __future__ import annotations

import base64
import html as _html
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="반등 타이밍 예측 대시보드",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# Resource images (base64)
# ─────────────────────────────────────────────────────────────
_RES = Path(__file__).parent / "res"

def _b64(fname: str) -> str:
    p = _RES / fname
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""

IMGS = {k: _b64(v) for k, v in {
    "app_icon": "app_icon.png",
    "home":     "home.png",
    "stock_bg": "stock_analysis.png",
    "calendar": "calendar.png",
    "chart_ic": "trend_chart.png",
    "score":    "score.png",
    "target":   "target.png",
    "defense":  "shield_check.png",
    "info":     "info.png",
}.items()}

def itag(key: str, style: str = "") -> str:
    b = IMGS.get(key, "")
    return f'<img src="data:image/png;base64,{b}" style="{style}" />' if b else ""

# ─────────────────────────────────────────────────────────────
# CSS — single-screen, no scroll
# ─────────────────────────────────────────────────────────────
st.markdown("""<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
* { font-family: 'Pretendard', sans-serif !important; }

:root {
  --card: rgba(255,255,255,.92);
  --shadow: 0 4px 20px rgba(15,23,42,.07);
  --line: rgba(148,163,184,.20);
  --icon-size: 20px;
}
html, body { overflow: hidden !important; }
[data-testid="stAppViewContainer"] {
  overflow: hidden !important; height: 100vh !important;
  background:
    radial-gradient(circle at 14% 4%, rgba(124,58,237,.13), transparent 28%),
    radial-gradient(circle at 86% 6%, rgba(37,99,235,.10), transparent 26%),
    linear-gradient(135deg, #eef2ff 0%, #f5f8ff 55%, #ffffff 100%) !important;
}
.main { overflow: hidden !important; }
.main .block-container {
  padding: 0.38rem 0.65rem 0 !important;
  max-width: 100% !important; overflow: hidden !important;
}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"] { display:none !important; }
[data-testid="stVerticalBlock"] { gap: 2rem !important; }
[data-testid="column"] { padding: 0 0.16rem !important; }
.st-emotion-cache-zy6yx3 {
    width: 100%;
    padding: 1rem 5rem 5rem;
    max-width: initial;
    min-width: auto;
}
.stMarkdown { margin-bottom: 0 !important; }
.element-container { margin-bottom: 0 !important; }
div[data-testid="stButton"] { margin: 0 !important; }

/* Controls */
div[data-testid="stSelectbox"] label { display:none !important; }
div[data-testid="stSelectbox"] > div > div {
  min-height: 36px !important; border-radius: 10px !important;
  border: 1px solid rgba(148,163,184,.28) !important;
  background: rgba(255,255,255,.88) !important; font-size: 12.5px !important;
}
button[kind="primary"] {
  min-height: 36px !important; border-radius: 10px !important;
  background: linear-gradient(135deg,#7c3aed,#4f46e5) !important;
  border:0 !important; font-weight:400 !important; font-size:12.5px !important;
}

/* LNB */
.lnb {
  min-height: calc(100vh - 5rem); border-radius: 16px;
  background: linear-gradient(180deg,#7c3aed 0%,#4f46e5 50%,#3b82f6 100%);
  display:flex; flex-direction:column; align-items:center;
  padding:12px 6px; gap:4px;
  box-shadow:0 8px 28px rgba(79,70,229,.22);
}
.lnb-logo { width:30px; height:30px; border-radius:10px; overflow:hidden; }
.lnb-logo img { width:100%; height:100%; object-fit:cover; }
.lnb-div { width:30px; height:1px; background:rgba(255,255,255,.28); margin:8px 0 4px; }
.lnb-btn {
  width:46px; height:46px; border-radius:13px;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  color:rgba(255,255,255,.5); font-size:12px; font-weight:400; gap:2px;
}
.lnb-btn.on { background:rgba(255,255,255,.22); color:#fff; box-shadow:0 3px 10px rgba(0,0,0,.12); }
.lnb-ico { font-size:50px; }

/* Card */
.card { background:var(--card); border:1px solid rgba(255,255,255,.78); border-radius:16px; box-shadow:var(--shadow); overflow:hidden; }
.cp { padding:11px 13px; }

/* Hero */
.hero-top { display:flex; justify-content:space-between; align-items:flex-start; gap:10px; }
.hero-badge { display:inline-flex; align-items:center; gap:4px; padding:3px 8px; border-radius:999px; background:#e0e7ff; color:#4338ca; font-size:12px; font-weight:500; }
.hero-name { margin-top:7px; display:flex; align-items:center; gap:7px; }
.hero-nm { font-size:22px; font-weight:750; letter-spacing:-.04em; }
.hero-cd { color:#94a3b8; font-size:18px; font-weight:350; }
.hero-desc { margin-top:5px; color:#64748b; font-size:15px; line-height:1.5; }
.hero-name img { width:var(--icon-size); height:var(--icon-size); }
.hero-circle { height:88px; }
.hero-circle img { width:100%; height:100%; object-fit:cover; }
.mg { display:grid; grid-template-columns:repeat(4,1fr); gap:6px; margin-top:8px; }
.mc { border:1px solid var(--line); border-radius:11px; background:#f8fafc; padding:7px 8px; }
.mc-l { color:#94a3b8; font-size:13px; font-weight:350; }
.mc-v { margin-top:3px; font-size:20px; font-weight:550; letter-spacing:-.03em; }
.mc-s { margin-top:2px; color:#94a3b8; font-size:11px; }

/* Section header */
.sec-hd { display:flex; align-items:center; gap:6px; font-size:15px; font-weight:500; color:#0f1f44; margin-bottom:7px; }
.sec-hd img { width:var(--icon-size); height:var(--icon-size); }
.sec-hint { font-size:13px; color:#94a3b8; font-weight:400; margin-left:auto; }

/* Calendar */
.cal-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:6px; }
.dc { border:1px solid var(--line); border-radius:11px; background:rgba(255,255,255,.7); padding:9px 6px; text-align:center; }
.dc.g { background:#ecfdf5; border-color:#86efac; }
.dc.b { background:#eff6ff; border-color:#bfdbfe; }
.dc.o { background:#fff7ed; border-color:#fed7aa; }
.dc.h { background:#f1f5f9; border-color:#cbd5e1; opacity:.75; }
.dc-t { font-size:15px; font-weight:550; }
.dc-d { font-size:12px; color:#64748b; font-weight:400; margin-top:2px; }
.dc-p { font-size:25px; font-weight:550; margin-top:9px; }
.dc-pill { margin-top:5px; display:inline-flex; padding:2px 6px; border-radius:999px; font-size:13px; font-weight:500; }
.lg { color:#15803d; background:#dcfce7; border:1px solid #bbf7d0; }
.lb { color:#1d4ed8; background:#dbeafe; border:1px solid #bfdbfe; }
.lo { color:#b45309; background:#ffedd5; border:1px solid #fed7aa; }
.lh { color:#64748b; background:#e2e8f0; border:1px solid #cbd5e1; }

/* Bottom cards */
.rr { display:grid; grid-template-columns:20px 1fr; gap:7px; align-items:start; padding:5px 0; border-bottom:1px solid rgba(148,163,184,.14); font-size:13px; color:#334155; line-height:1.4; }
.ci { width:18px; height:18px; border-radius:5px; display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:950; flex-shrink:0; }
.ck { background:#dcfce7; color:#16a34a; }
.cx { background:#f1f5f9; color:#94a3b8; }
.sr { display:grid; grid-template-columns:1fr auto; gap:6px; align-items:center; padding:5px 0; border-bottom:1px solid rgba(148,163,184,.14); font-size:13px; }
.sk { color:#475569; font-weight:350; }
.sv { font-size:17px; font-weight:550; }
.tr { display:grid; grid-template-columns:auto 1fr; gap:10px; padding:5px 0; border-bottom:1px solid rgba(148,163,184,.14); font-size:13px; }
.tk { color:#4f46e5; font-weight:500; white-space:nowrap; }
.td-desc { color:#64748b; }
.dsm { margin-top:7px; color:#94a3b8; font-size:13px; line-height:1.5; }

/* Table & chart containers */
[data-testid="stDataFrame"] div { font-size:14.5px !important; }
div[data-testid="stVerticalBlockBorderWrapper"] {
  background:var(--card) !important;
  border:1px solid rgba(255,255,255,.78) !important;
  border-radius:16px !important;
  box-shadow:var(--shadow) !important;
  overflow:hidden !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div { padding:7px 10px !important; }
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Data / model loading
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_assets():
    base = Path(__file__).parent
    df = pd.read_pickle(base / "df_full.pkl")
    models = joblib.load(base / "models.joblib")
    from short_signal_pipeline import FEATURE_COLS
    return df, models, FEATURE_COLS


df, models, FEATURE_COLS = load_assets()

HORIZONS = [1, 2, 3, 4, 5]
WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]
EASE_TH = 0.70

KR_HOLIDAYS = {
    pd.Timestamp("2026-01-01"),  # 신정
    pd.Timestamp("2026-01-28"),  # 설날연휴
    pd.Timestamp("2026-01-29"),  # 설날
    pd.Timestamp("2026-01-30"),  # 설날연휴
    pd.Timestamp("2026-03-01"),  # 삼일절
    pd.Timestamp("2026-05-05"),  # 어린이날
    pd.Timestamp("2026-05-24"),  # 부처님오신날
    pd.Timestamp("2026-06-06"),  # 현충일
    pd.Timestamp("2026-08-15"),  # 광복절
    pd.Timestamp("2026-09-24"),  # 추석연휴
    pd.Timestamp("2026-09-25"),  # 추석
    pd.Timestamp("2026-09-26"),  # 추석연휴
    pd.Timestamp("2026-10-03"),  # 개천절
    pd.Timestamp("2026-10-09"),  # 한글날
    pd.Timestamp("2026-12-25"),  # 크리스마스
}
PRESSURE_TH = 0.40

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def esc(v: Any) -> str:
    return _html.escape(str(v))


def pct(v: float) -> str:
    return f"{float(v) * 100:.0f}%"


def pct_1(v: float) -> str:
    return f"{float(v) * 100:+.1f}%"


def make_interest_label(first_ease_day, last_ease_day) -> str:
    if pd.isna(first_ease_day):
        return "탐지되지 않음"
    f = int(first_ease_day)
    l = int(last_ease_day)
    return f"D+{f}" if f == l else f"D+{f} ~ D+{l}"


def make_judgment(pressure_prob: float, first_ease_day) -> dict[str, str]:
    if pressure_prob < PRESSURE_TH:
        return {"label": "단기 안정", "class": "pill-blue", "color": "#2563eb",
                "desc": "공매도 하락 베팅이 적어 하락 압력이 없는 상태입니다."}
    if pd.isna(first_ease_day):
        return {"label": "하락 지속", "class": "pill-orange", "color": "#f59e0b",
                "desc": "공매도 압력이 강하고 줄어들 기미가 없습니다."}
    return {"label": "반등 후보", "class": "pill-green", "color": "#16a34a",
            "desc": "하락 압력이 꺾이는 시점이 예측됩니다."}


@st.cache_data(show_spinner=False)
def make_eval_df(date_sel):
    day_df = df.loc[df["date"] == date_sel].copy()
    if day_df.empty:
        return pd.DataFrame()
    day_df = day_df.dropna(subset=FEATURE_COLS)
    if day_df.empty:
        return pd.DataFrame()

    X = day_df[FEATURE_COLS]
    out = day_df[[
        "ISU_CD", "ISU_NM", "date",
        "short_ratio", "balance_ratio",
        "short_ratio_pct_vs_own_hist", "balance_ratio_pct_vs_own_hist",
    ]].copy()
    out["ISU_CD"] = out["ISU_CD"].astype(str)
    out["ISU_NM"] = out["ISU_NM"].astype(str)
    out["pressure_prob"] = models["pressure"].predict_proba(X)[:, 1]

    for h in HORIZONS:
        out[f"easing_{h}"]  = models[f"easing_{h}"].predict_proba(X)[:, 1]
        out[f"ret_q10_{h}"] = models[f"ret_q10_{h}"].predict(X)
        out[f"ret_q50_{h}"] = models[f"ret_q50_{h}"].predict(X)
        out[f"ret_q90_{h}"] = models[f"ret_q90_{h}"].predict(X)

    easing_cols = [f"easing_{h}" for h in HORIZONS]
    out["max_easing"] = out[easing_cols].max(axis=1)

    first_days, last_days = [], []
    for _, r in out.iterrows():
        candidates = [h for h in HORIZONS if r[f"easing_{h}"] >= EASE_TH]
        first_days.append(candidates[0]  if candidates else pd.NA)
        last_days.append(candidates[-1]  if candidates else pd.NA)

    out["first_ease_day"] = first_days
    out["last_ease_day"]  = last_days
    out["interest_label"] = out.apply(
        lambda r: make_interest_label(r["first_ease_day"], r["last_ease_day"]), axis=1)

    judgments = [make_judgment(r["pressure_prob"], r["first_ease_day"]) for _, r in out.iterrows()]
    out["judgment"]       = [j["label"] for j in judgments]
    out["judgment_class"] = [j["class"] for j in judgments]
    out["judgment_color"] = [j["color"] for j in judgments]

    priority = {"반등 후보": 0, "하락 지속": 1, "단기 안정": 2}
    out["_priority"] = out["judgment"].map(priority).fillna(9)
    out = out.sort_values(
        ["_priority", "max_easing", "pressure_prob"], ascending=[True, False, False]
    ).reset_index(drop=True)
    return out


def selected_rows_from_event(event) -> list[int]:
    try:
        return list(event.selection.rows)
    except Exception:
        try:
            return list(event.get("selection", {}).get("rows", []))
        except Exception:
            return []


# ─────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────
if "selected_isu_cd" not in st.session_state:
    st.session_state["selected_isu_cd"] = "005930"

available_dates = sorted(df["date"].dropna().unique())

# ─────────────────────────────────────────────────────────────
# Layout root: LNB + Content
# ─────────────────────────────────────────────────────────────
nav_col, content_col = st.columns([0.52, 9.48], gap="small")

# ── LNB ──────────────────────────────────────────────────────
with nav_col:
    st.markdown(f"""
<div class="lnb">
  <div class="lnb-logo">{itag("app_icon")}</div>
  <div class="lnb-div"></div>
  <div class="lnb-btn on">
    <span style="font-size:18px;">홈</span>
  </div>
</div>""", unsafe_allow_html=True)

# ── Content ───────────────────────────────────────────────────
with content_col:

    # ── Header ──────────────────────────────────────────────
    hc1, hc2, hc3, hc4 = st.columns([4.6, 2.2, 1.55, 0.6], gap="small")

    with hc1:
        st.markdown("""
<div style="display:contents;align-items:baseline;gap:9px;padding:4px 0 2px;">
  <span style="font-size:20px;font-weight:500;color:#0f1f44;letter-spacing:-.025em;white-space:nowrap;">
    공매도 종목 반등 타이밍 예측 대시보드
  </span>
  <span style="font-size:15px;color:#94a3b8;font-weight:300;white-space:nowrap;">
    공매도가 집중된 종목의 주가 반등 시점을 예측합니다.
  </span>
</div>""", unsafe_allow_html=True)

    with hc3:
        date_sel = st.selectbox(
            "기준일", available_dates,
            index=next((i for i, d in enumerate(available_dates) if pd.Timestamp(d).strftime("%Y-%m-%d") == "2026-06-16"), len(available_dates) - 1),
            format_func=lambda d: pd.Timestamp(d).strftime("%Y-%m-%d"),
            label_visibility="collapsed",
        )

    eval_df = make_eval_df(date_sel)
    if eval_df.empty:
        st.warning("선택한 기준일에 데이터가 없습니다. 다른 날짜를 선택해주세요.")
        st.stop()

    selected_code = str(st.session_state["selected_isu_cd"])
    if selected_code not in eval_df["ISU_CD"].astype(str).values:
        selected_code = str(eval_df["ISU_CD"].iloc[0])
        st.session_state["selected_isu_cd"] = selected_code

    option_labels = (eval_df["ISU_CD"].astype(str) + "   " + eval_df["ISU_NM"].astype(str)).tolist()
    current_label = option_labels[eval_df.index[eval_df["ISU_CD"].astype(str) == selected_code][0]]

    with hc2:
        selected_label = st.selectbox(
            "종목", option_labels,
            index=option_labels.index(current_label),
            label_visibility="collapsed",
        )
        box_code = selected_label.split()[0]
        if box_code != selected_code:
            st.session_state["selected_isu_cd"] = box_code
            st.rerun()

    with hc4:
        st.button("조회", type="primary", use_container_width=True)

    # ── Derived values ───────────────────────────────────────
    selected_code = str(st.session_state["selected_isu_cd"])
    selected = eval_df.loc[eval_df["ISU_CD"].astype(str) == selected_code].iloc[0]

    isu_name            = str(selected["ISU_NM"])
    pressure_prob       = float(selected["pressure_prob"])
    pressure_pct        = float(selected["short_ratio_pct_vs_own_hist"])
    balance_pct         = float(selected["balance_ratio_pct_vs_own_hist"])
    short_ratio_today   = float(selected["short_ratio"])
    balance_ratio_today = float(selected["balance_ratio"])
    easing   = {h: float(selected[f"easing_{h}"]) for h in HORIZONS}
    ret_band = {
        h: (float(selected[f"ret_q10_{h}"]),
            float(selected[f"ret_q50_{h}"]),
            float(selected[f"ret_q90_{h}"])) for h in HORIZONS
    }
    first_ease_day    = selected["first_ease_day"]
    last_ease_day     = selected["last_ease_day"]
    ease_day          = int(first_ease_day) if pd.notna(first_ease_day) else None
    ease_label        = str(selected["interest_label"])
    ease_prob_display = float(selected["max_easing"])
    judgment          = make_judgment(pressure_prob, first_ease_day)
    d1_q10, d1_q50, d1_q90 = ret_band[1]

    # ── Row 2: Hero card + 5-day calendar ───────────────────
    left_col, right_col = st.columns([1.08, 1.22], gap="medium")

    with left_col:
        st.markdown(f"""
<div class="card cp" style="background:radial-gradient(circle at 80% 18%,rgba(124,58,237,.11),transparent 30%),rgba(255,255,255,.92);">
  <div class="hero-top">
    <div style="flex:1;">
      <span class="hero-badge">현재 선택 종목</span>
      <div class="hero-name">
        {itag("defense", "margin-right:3px;")}
        <span class="hero-nm">{esc(isu_name)}</span>
        <span class="hero-cd">{esc(selected_code)}</span>
      </div>
      <div class="hero-desc">모델이 예측한 주가 방향과<br>반등 예상 시점을 한눈에 확인하세요.</div>
    </div>
    <div class="hero-circle">{itag("stock_bg")}</div>
  </div>
  <div class="mg">
    <div class="mc">
      <div class="mc-l">현재 판단</div>
      <div class="mc-v" style="color:{judgment['color']};">{esc(judgment['label'])}</div>
      <div class="mc-s">주가 방향</div>
    </div>
    <div class="mc">
      <div class="mc-l">관심 시점</div>
      <div class="mc-v" style="color:#4f46e5;font-size:16px;">{esc(ease_label)}</div>
      <div class="mc-s">매수 고려 시점</div>
    </div>
    <div class="mc">
      <div class="mc-l">반등 가능성</div>
      <div class="mc-v" style="color:{'#16a34a' if ease_prob_display >= EASE_TH else '#f59e0b'};">{pct(ease_prob_display)}</div>
      <div class="mc-s">모델 추정</div>
    </div>
    <div class="mc">
      <div class="mc-l">예상 변동폭</div>
      <div class="mc-v" style="color:#2563eb;font-size:15px;">{pct_1(d1_q10)}~{pct_1(d1_q90)}</div>
      <div class="mc-s">D+1 범위</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    with right_col:
        base_date = pd.Timestamp(date_sel)
        day_cards_html = []
        for h in HORIZONS:
            d = base_date + pd.Timedelta(days=h)
            prob = easing[h]
            is_holiday = d.weekday() >= 5 or d in KR_HOLIDAYS
            if is_holiday:
                guide, cls, lcls, pc = "공휴일", "h", "lh", "#94a3b8"
            elif ease_day == h:
                guide, cls, lcls = "반등 예상", "g", "lg"
                pc = "#16a34a"
            elif prob >= EASE_TH:
                guide, cls, lcls = "상승 지속", "g", "lg"
                pc = "#16a34a"
            elif prob >= 0.55:
                guide, cls, lcls = "부분 매수", "o", "lo"
                pc = "#f59e0b"
            else:
                guide, cls, lcls = "하락 유지", "b", "lb"
                pc = "#2563eb"
            prob_html = f'<div class="dc-p" style="color:{pc};">—</div>' if is_holiday else f'<div class="dc-p" style="color:{pc};">{pct(prob)}</div>'
            day_cards_html.append(f"""
<div class="dc {cls}">
  <div class="dc-t">D+{h}</div>
  <div class="dc-d">{d.strftime('%m/%d')} ({WEEKDAY_KR[d.weekday()]})</div>
  {prob_html}
  <div><span class="dc-pill {lcls}">{esc(guide)}</span></div>
</div>""")

        st.markdown(f"""
<div class="card cp">
  <div class="sec-hd">
    {itag("calendar")}
    <span>5영업일 타이밍 예측</span>
    <span class="sec-hint">기준일 {pd.Timestamp(date_sel).strftime('%Y-%m-%d')}</span>
  </div>
  <div class="cal-grid">{''.join(day_cards_html)}</div>
</div>""", unsafe_allow_html=True)

    # ── Row 3: Table + Chart ─────────────────────────────────
    tl_col, ch_col = st.columns([1.08, 1.22], gap="medium")

    with tl_col:
        with st.container(border=True):
            st.markdown(f"""
<div class="sec-hd">
  {itag("score")}
  <span>전체 종목 평가</span>
  <span class="sec-hint">행 클릭으로 종목 변경</span>
</div>""", unsafe_allow_html=True)

            # _priority → max_easing → pressure_prob 순 안정 정렬 (선택 종목 우선 제거)
            # _sel 기반 재정렬을 없애야 row 인덱스가 선택 변경 시 안 바뀜
            list_df = eval_df.sort_values(
                ["_priority", "max_easing", "pressure_prob"], ascending=[True, False, False]
            ).head(18).reset_index(drop=True)

            # 선택 종목이 상위 18개 밖에 있으면 마지막 행에 강제 포함
            if selected_code not in list_df["ISU_CD"].astype(str).values:
                sel_row = eval_df[eval_df["ISU_CD"].astype(str) == selected_code]
                if not sel_row.empty:
                    list_df = pd.concat([list_df.head(17), sel_row]).reset_index(drop=True)

            display_df = pd.DataFrame({
                "★":     ["★" if str(x) == selected_code else "☆" for x in list_df["ISU_CD"].astype(str)],
                "코드":   list_df["ISU_CD"].astype(str),
                "종목명": list_df["ISU_NM"].astype(str),
                "판단":   list_df["judgment"].astype(str),
                "약화":   (list_df["max_easing"] * 100).round(0).astype(int).astype(str) + "%",
                "시점":   list_df["interest_label"].astype(str),
            })

            try:
                # key에 selected_code 포함 → 종목 바뀔 때마다 위젯 초기화(체크 상태 리셋)
                event = st.dataframe(
                    display_df, use_container_width=True, hide_index=True, height=215,
                    on_select="rerun", selection_mode="single-row",
                    key=f"table_{selected_code}",
                )
                rows = selected_rows_from_event(event)
                if rows:
                    picked = str(list_df.iloc[rows[0]]["ISU_CD"])
                    if picked != selected_code:
                        st.session_state["selected_isu_cd"] = picked
                        st.rerun()
            except TypeError:
                st.dataframe(display_df, use_container_width=True, hide_index=True, height=215)
                st.caption("상단 드롭다운으로 종목을 선택해주세요.")

    with ch_col:
        with st.container(border=True):
            st.markdown(f"""
<div class="sec-hd">
  {itag("chart_ic")}
  <span>향후 5영업일 주가 방향 예측</span>
  <span class="sec-hint">하락 강도 · 반등 가능성 · 수익률 중앙값</span>
</div>""", unsafe_allow_html=True)

            days      = [f"D+{h}" for h in HORIZONS]
            ease_vals = [easing[h] * 100 for h in HORIZONS]
            pres_vals = [pressure_prob * 100 for _ in HORIZONS]
            q10 = [ret_band[h][0] * 100 for h in HORIZONS]
            q50 = [ret_band[h][1] * 100 for h in HORIZONS]
            q90 = [ret_band[h][2] * 100 for h in HORIZONS]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=days, y=ease_vals, mode="lines+markers", name="반등 가능성",
                line=dict(color="#16a34a", width=2.5), marker=dict(size=6),
                fill="tozeroy", fillcolor="rgba(22,163,74,.08)", yaxis="y1",
            ))
            fig.add_trace(go.Scatter(
                x=days, y=pres_vals, mode="lines+markers", name="하락 강도",
                line=dict(color="#2563eb", width=2.5), marker=dict(size=6), yaxis="y1",
            ))
            fig.add_trace(go.Scatter(
                x=days, y=q50, mode="lines+markers", name="수익률 중앙값",
                line=dict(color="#7c3aed", width=2.5), marker=dict(size=6), yaxis="y2",
            ))
            fig.add_trace(go.Scatter(
                x=days + days[::-1], y=q90 + q10[::-1],
                fill="toself", fillcolor="rgba(124,58,237,.07)",
                line=dict(color="rgba(0,0,0,0)"), name="변동폭", yaxis="y2",
            ))
            fig.add_hline(
                y=EASE_TH * 100, line_dash="dot", line_color="#94a3b8",
                annotation_text=f"{EASE_TH*100:.0f}%", annotation_font_size=10, yref="y",
            )
            fig.update_layout(
                height=235,
                margin=dict(t=8, r=50, b=20, l=40),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1,
                            font=dict(size=10, color="#475569")),
                font=dict(family="Arial", size=11, color="#334155"),
                xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#64748b")),
                yaxis=dict(
                    title="하락 강도/반등 가능성(%)", range=[0, 108],
                    gridcolor="rgba(148,163,184,.18)", zeroline=False,
                    title_font=dict(size=10, color="#64748b"),
                    tickfont=dict(size=10, color="#64748b"),
                ),
                yaxis2=dict(
                    title="수익률(%)", overlaying="y", side="right",
                    zeroline=True, zerolinecolor="rgba(148,163,184,.22)",
                    title_font=dict(size=10, color="#64748b"),
                    tickfont=dict(size=10, color="#64748b"),
                ),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Row 4: Bottom 3 cards ────────────────────────────────
    b1, b2, b3 = st.columns([1.15, 1.0, 1.35], gap="medium")

    cond_list = [
        ("공매도 비중이 평균 대비 70% 이상입니다.",                    pressure_pct  >= 0.70),
        ("공매도 잔고율이 평균 대비 70% 이상입니다.",                  balance_pct   >= 0.70),
        (f"5일 내 반등 가능성이 {EASE_TH*100:.0f}% 이상 추정됩니다.",    any(v >= EASE_TH for v in easing.values())),
        ("하락 압력 확률이 40% 이상입니다.",                              pressure_prob >= PRESSURE_TH),
    ]
    met = sum(1 for _, ok in cond_list if ok)
    sum_color = "#16a34a" if met >= 3 else "#f59e0b" if met >= 2 else "#64748b"

    with b1:
        rr_html = "".join(
            f'<div class="rr">'
            f'<div class="ci {"ck" if ok else "cx"}">{"✓" if ok else "–"}</div>'
            f'<div>{esc(label)}</div></div>'
            for label, ok in cond_list
        )
        st.markdown(f"""
<div class="card cp">
  <div class="sec-hd">
    {itag("target")}
    <span>반등 후보로 보는 이유</span>
  </div>
  {rr_html}
  <div style="margin-top:8px;font-size:14px;font-weight:550;color:{sum_color};">
    → 반등 조건 {met}/{len(cond_list)}개 충족
  </div>
</div>""", unsafe_allow_html=True)

    with b2:
        sr_html = "".join(
            f'<div class="sr"><div class="sk">{esc(k)}</div>'
            f'<div class="sv" style="color:{c};">{esc(v)}</div></div>'
            for k, v, c in [
                ("공매도 비중",      f"{short_ratio_today:.2f}%",   "#0f172a"),
                ("공매도 잔고율",    f"{balance_ratio_today:.2f}%", "#0f172a"),
                ("하락 강도",       pct(pressure_prob),             "#2563eb"),
                ("반등 가능성",     pct(ease_prob_display),
                 "#16a34a" if ease_prob_display >= EASE_TH else "#f59e0b"),
            ]
        )
        st.markdown(f"""
<div class="card cp">
  <div class="sec-hd">
    {itag("info")}
    <span>현재 주가 하락 강도</span>
  </div>
  {sr_html}
  <div class="dsm">※ 평소 대비: 최근 1년 기준 본인 종목 내 순위</div>
</div>""", unsafe_allow_html=True)

    with b3:
        tr_html = "".join(
            f'<div class="tr" ><div class="tk">{esc(t)}</div><div class="td-desc">{esc(d)}</div></div>'
            for t, d in [
                ("하락 강도 ≥ 40%",        "단기 하락 압력이 존재할 수 있습니다."),
                ("반등 가능성 ≥ 70%",      "주가 반등이 예상되는 후보일로 관찰할 수 있습니다."),
                ("예상 변동폭",             "방향 예측이 아니라 위아래로 흔들릴 수 있는 범위입니다."),
                ("5일 후 방향",             "가격 방향 확정 모델이 아니므로 추가 지표 확인이 필요합니다."),
            ]
        )
        st.markdown(f"""
<div class="card cp">
  <div class="sec-hd">
    {itag("defense")}
    <span>실전 활용 포인트</span>
  </div>
  {tr_html}
  <div class="dsm">※ 투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.</div>
</div>""", unsafe_allow_html=True)

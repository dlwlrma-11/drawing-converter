"""
도면 DXF 변환기 — 웹 배포 v2.1
버그픽스: CSS 텍스트 가시성·변환 오류처리·사이드바 정리
"""

import io, os, math, json, zipfile, datetime
import cv2, ezdxf, numpy as np
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from skimage.morphology import skeletonize as _skeletonize
    _SKEL_OK = True
except ImportError:
    _SKEL_OK = False

try:
    from scipy.ndimage import uniform_filter1d
    _SCIPY_OK = True
except ImportError:
    _SCIPY_OK = False

try:
    import plotly.graph_objects as go
    _PLOTLY_OK = True
except ImportError:
    _PLOTLY_OK = False

# ══════════════════════════════════════════
#  페이지 설정 & CSS
# ══════════════════════════════════════════
st.set_page_config(page_title="도면 DXF 변환기", page_icon="📐", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* 전체 폰트 */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* Streamlit 기본 UI 숨기기 */
#MainMenu, header, [data-testid="stToolbar"], footer, .stDeployButton {
    display: none !important;
}

/* 메인 배경 */
.stApp { background: #edf0f4 !important; }
.block-container { padding-top: 2rem !important; }

/* ── 사이드바 ── */
section[data-testid="stSidebar"] {
    background: #f4f6f9 !important;
    width: 380px !important;
    min-width: 380px !important;
}
/* 사이드바 텍스트 색상 강제 */
section[data-testid="stSidebar"] * {
    color: #1a3a5c !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
    color: #1a3a5c !important;
}
/* 슬라이더 색 */
section[data-testid="stSidebar"] [data-baseweb="slider"] > div > div > div {
    background: #0078d4 !important;
}
section[data-testid="stSidebar"] [role="slider"] {
    background: #0078d4 !important;
}

/* ── 패널 ── */
.panel {
    background: #fff;
    border-radius: 8px;
    padding: 14px 18px;
    border: 1px solid #d0d7e0;
    margin-bottom: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,.04);
}

/* ── 히어로 배너 ── */
.hero {
    background: #0d1117;
    border-radius: 10px;
    padding: 20px 28px;
    margin-bottom: 12px;
    border-left: 4px solid #0078d4;
}
.hero-title { color: #fff; font-size: 1.4rem; font-weight: 700; margin: 0 0 4px 0; }
.hero-sub { color: #7ec8ff; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; margin: 0; }

/* ── 통계 카드 ── */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: #d0d7e0;
    border: 1px solid #d0d7e0;
    border-radius: 8px;
    overflow: hidden;
    margin: 10px 0;
}
.stat-cell { background: #fff; padding: 12px; text-align: center; }
.stat-num { font-size: 1.4rem; font-weight: 700; color: #1a3a5c; font-family: 'JetBrains Mono', monospace; }
.stat-lbl { font-size: 0.65rem; color: #5a7a96; text-transform: uppercase; letter-spacing: .04em; font-weight: 600; }

/* ── 미리보기 레이블 ── */
.prev-label {
    font-size: 0.78rem; font-weight: 600;
    padding: 5px 10px; border-radius: 5px;
    margin-bottom: 6px; display: flex; align-items: center; gap: 6px;
}
.before-lbl { background: #f5f7fa; border-left: 3px solid #7a8fa6; color: #1a3a5c; }
.after-lbl  { background: #e8f0f9; border-left: 3px solid #0078d4; color: #1a3a5c; }
.diff-lbl   { background: #fff5f5; border-left: 3px solid #dc2626; color: #7f1d1d; }

/* ── 품질 뱃지 ── */
.grade-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 5px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
}

/* ── 리포트 행 ── */
.report-row {
    border: 1px solid #d0d7e0;
    border-left: 4px solid #0078d4;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 8px;
    background: #fff;
}

/* ── 파일 업로더 ── */
[data-testid="stFileUploader"] {
    background: #f0f6ff !important;
    border: 1.5px dashed #9ab5d0 !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session State 초기화 ──
for k, v in [("presets", {}), ("results", []), ("failed", [])]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════
#  핵심 처리 함수
# ══════════════════════════════════════════

def smooth_path(pts, window=9):
    if len(pts) < 4 or window < 4: return pts
    w = max(3, window | 1)
    if len(pts) <= w: w = max(3, len(pts) - (0 if len(pts) % 2 != 0 else 1))
    if w < 3: return pts
    try:
        from scipy.signal import savgol_filter
        xs = savgol_filter(pts[:, 0].astype(float), window_length=w, polyorder=2)
        ys = savgol_filter(pts[:, 1].astype(float), window_length=w, polyorder=2)
    except Exception:
        if _SCIPY_OK:
            xs = uniform_filter1d(pts[:, 0].astype(float), size=w)
            ys = uniform_filter1d(pts[:, 1].astype(float), size=w)
        else:
            return pts
    xs[0], xs[-1] = pts[0, 0], pts[-1, 0]
    ys[0], ys[-1] = pts[0, 1], pts[-1, 1]
    return np.column_stack([xs, ys])


def stitch_close_paths(paths, max_gap_px=4.0):
    if len(paths) < 2: return paths
    paths = [np.asarray(p, dtype=float) for p in paths]
    used = [False] * len(paths)
    out = []
    for i, p in enumerate(paths):
        if used[i]: continue
        used[i] = True
        chain = [p]
        changed = True
        while changed:
            changed = False
            cs, ce = chain[0][0], chain[-1][-1]
            for j, q in enumerate(paths):
                if used[j]: continue
                qs, qe = q[0], q[-1]
                if math.hypot(ce[0]-qs[0], ce[1]-qs[1]) < max_gap_px:
                    chain.append(q); used[j] = True; changed = True; break
                if math.hypot(ce[0]-qe[0], ce[1]-qe[1]) < max_gap_px:
                    chain.append(q[::-1]); used[j] = True; changed = True; break
                if math.hypot(cs[0]-qe[0], cs[1]-qe[1]) < max_gap_px:
                    chain.insert(0, q); used[j] = True; changed = True; break
                if math.hypot(cs[0]-qs[0], cs[1]-qs[1]) < max_gap_px:
                    chain.insert(0, q[::-1]); used[j] = True; changed = True; break
        out.append(np.vstack(chain))
    return out


def skeleton_to_paths(skeleton):
    skel = (skeleton > 0).astype(np.uint8)
    h, w = skel.shape
    visited = np.zeros((h, w), dtype=bool)
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    def nbrs(y, x):
        return [(y+dy, x+dx) for dy, dx in dirs
                if 0 <= y+dy < h and 0 <= x+dx < w and skel[y+dy, x+dx] == 1]

    ys, xs = np.where(skel == 1)
    if len(ys) == 0: return []
    starts = ([(int(y), int(x)) for y, x in zip(ys, xs) if len(nbrs(int(y),int(x))) == 1] +
              [(int(y), int(x)) for y, x in zip(ys, xs) if len(nbrs(int(y),int(x))) >= 3])
    if not starts: starts = [(int(ys[0]), int(xs[0]))]

    paths = []
    for sy, sx in starts:
        for ny, nx in nbrs(sy, sx):
            if visited[ny, nx]: continue
            path = [(sx, sy)]
            visited[ny, nx] = True
            cy, cx = ny, nx
            while True:
                path.append((cx, cy))
                nxt = [(y2, x2) for y2, x2 in nbrs(cy, cx) if not visited[y2, x2]]
                if not nxt: break
                cy, cx = nxt[0]
                visited[cy, cx] = True
                if len(nbrs(cy, cx)) >= 3:
                    path.append((cx, cy)); break
            if len(path) >= 2:
                paths.append(np.array(path, dtype=float))
    return paths


def auto_cleanup(binary, level="standard"):
    """끊긴 선 연결 + 잡선 제거"""
    cfg = {"light": (3,2,30), "standard": (5,3,50), "strong": (7,4,100)}
    k1, k2, min_area = cfg.get(level, cfg["standard"])
    result = binary.copy()
    bk = np.ones((k1, k1), np.uint8)
    result = cv2.dilate(result, bk, iterations=1)
    result = cv2.erode(result, bk, iterations=1)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(result, connectivity=8)
    clean = np.zeros_like(result)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            clean[labels == i] = 255
    ck = np.ones((k2, k2), np.uint8)
    return cv2.morphologyEx(clean, cv2.MORPH_CLOSE, ck)


def calc_quality_score(paths, circles, binary):
    """0~100점 + A+~F 등급"""
    total_px = max(1, int(np.count_nonzero(binary)))

    def plen(p):
        if len(p) < 2: return 0.0
        d = np.diff(p, axis=0)
        return float(np.sum(np.hypot(d[:,0], d[:,1])))

    continuity = min(40, int(np.mean([plen(p) for p in paths]) / 3)) if paths else 0
    geometry   = min(25, len(circles) * 5)
    cleanliness = int(20 * (1 - sum(1 for p in paths if plen(p) < 10) / max(1, len(paths)))) if paths else 0
    yield_pts  = min(15, int((len(paths)+len(circles)) / max(1, total_px/5000) * 3))
    score = max(0, min(100, continuity + geometry + cleanliness + yield_pts))

    grade = ("A+" if score>=90 else "A" if score>=80 else "B" if score>=70
             else "C" if score>=55 else "D" if score>=40 else "F")
    color = {"A+":"#16a34a","A":"#22c55e","B":"#0078d4",
             "C":"#f59e0b","D":"#ea580c","F":"#dc2626"}.get(grade,"#5a7a96")
    return {"score":score,"grade":grade,"color":color,
            "breakdown":{"continuity":continuity,"geometry":geometry,
                         "cleanliness":cleanliness,"yield":yield_pts}}


def convert_to_dxf_bytes(img_bytes, threshold_val=127, scale=0.1,
                          layer_name="OUTLINE", smooth_window=9,
                          min_path_len=6, stitch_gap=4,
                          use_circle=True, use_denoise=True,
                          use_normalize=False, use_gap_bridge=False,
                          use_auto_cleanup=False, cleanup_level="standard"):
    # 이미지 디코딩
    arr = np.asarray(bytearray(img_bytes), dtype=np.uint8)
    img_color = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img_color is None:
        raise ValueError("이미지를 읽을 수 없습니다. JPG/PNG 파일을 확인해주세요.")

    img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
    h, w = img_gray.shape

    # 전처리
    proc = cv2.bilateralFilter(img_gray, 9, 75, 75) if use_denoise else img_gray.copy()

    if threshold_val < 0:
        _, binary = cv2.threshold(proc, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        _, binary = cv2.threshold(proc, threshold_val, 255, cv2.THRESH_BINARY_INV)

    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, np.ones((2,2), np.uint8))

    if use_gap_bridge:
        bk = np.ones((5,5), np.uint8)
        binary = cv2.dilate(binary, bk); binary = cv2.erode(binary, bk)

    if use_normalize:
        dist = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
        _, center = cv2.threshold(dist, 0.5, 255, cv2.THRESH_BINARY)
        binary = cv2.dilate(center.astype(np.uint8), np.ones((2,2),np.uint8))

    if use_auto_cleanup:
        binary = auto_cleanup(binary, level=cleanup_level)

    # 원 감지
    circles_out = []
    if use_circle:
        try:
            circles_hough = cv2.HoughCircles(
                cv2.GaussianBlur(img_gray, (9,9), 2),
                cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                param1=50, param2=30, minRadius=8, maxRadius=min(h,w)//3
            )
            if circles_hough is not None:
                cmask = np.zeros_like(binary)
                for cx, cy, cr in circles_hough[0]:
                    cx,cy,cr = int(round(cx)),int(round(cy)),int(round(cr))
                    circles_out.append((cx,cy,cr))
                    cv2.circle(cmask,(cx,cy),cr,255,max(3,cr//8))
                binary = cv2.bitwise_and(binary, cv2.bitwise_not(cmask))
        except Exception:
            pass

    # 스켈레톤
    if _SKEL_OK:
        skeleton = _skeletonize((binary > 0).astype(np.uint8)).astype(np.uint8)
    else:
        # fallback: thinning
        skeleton = cv2.ximgproc.thinning(binary) if hasattr(cv2, 'ximgproc') else binary

    paths = skeleton_to_paths(skeleton)
    paths = [p for p in paths if (lambda p: float(np.sum(np.hypot(np.diff(p[:,0]), np.diff(p[:,1])))))(p) >= min_path_len]
    if stitch_gap > 0: paths = stitch_close_paths(paths, max_gap_px=float(stitch_gap))
    if smooth_window >= 4:
        paths = [smooth_path(p, smooth_window) if len(p) >= smooth_window else p for p in paths]

    # 품질 점수
    quality = calc_quality_score(paths, circles_out, binary)

    # DXF 생성
    doc = ezdxf.new('R2010')
    doc.layers.new(name=layer_name, dxfattribs={'color': 7})
    if circles_out: doc.layers.new(name="CIRCLE", dxfattribs={'color': 3})
    msp = doc.modelspace()

    n_lines = 0
    for pts in paths:
        if len(pts) < 2: continue
        dxf_pts = [(float(x)*scale, float(h-y)*scale) for x,y in pts]
        pl = msp.add_lwpolyline(dxf_pts, dxfattribs={'layer': layer_name})
        s, e = dxf_pts[0], dxf_pts[-1]
        if math.hypot(s[0]-e[0], s[1]-e[1]) < scale*3: pl.close(True)
        n_lines += 1

    for cx,cy,cr in circles_out:
        msp.add_circle((float(cx)*scale, float(h-cy)*scale), float(cr)*scale,
                       dxfattribs={'layer':'CIRCLE'})

    buf = io.BytesIO()
    doc.write(buf)

    report = {"img_w":w,"img_h":h,"lines":n_lines,"circles":len(circles_out),
              "scale":scale,"quality":quality}
    return buf.getvalue(), report, binary


def render_dxf_preview(dxf_bytes, bg="#1a1d2e", line_color="#e0e4ef"):
    try:
        doc = ezdxf.read(io.StringIO(dxf_bytes.decode("utf-8", errors="replace")))
        msp = doc.modelspace()
    except Exception as e:
        return str(e)
    entities = list(msp)
    if not entities: return "EMPTY"

    fig, ax = plt.subplots(figsize=(7,7))
    fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
    ax.set_aspect('equal'); ax.axis('off')
    for ent in entities:
        try:
            t = ent.dxftype()
            lc = "#4ec9b0" if ent.dxf.layer == "CIRCLE" else line_color
            if t == "LWPOLYLINE":
                pts = list(ent.get_points())
                if len(pts) >= 2:
                    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
                    if ent.is_closed: xs.append(xs[0]); ys.append(ys[0])
                    ax.plot(xs, ys, color=lc, linewidth=0.6)
            elif t == "CIRCLE":
                cx,cy,r = ent.dxf.center.x, ent.dxf.center.y, ent.dxf.radius
                theta = np.linspace(0, 2*math.pi, 80)
                ax.plot(cx+r*np.cos(theta), cy+r*np.sin(theta), color=lc, linewidth=0.6)
        except Exception: continue
    plt.tight_layout(pad=0)
    return fig


def render_diff_overlay(img_bytes, dxf_bytes):
    arr = np.asarray(bytearray(img_bytes), dtype=np.uint8)
    img_cv = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img_cv is None: return None, None
    h_img,w_img = img_cv.shape[:2]
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    _, orig_bin = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    dxf_bin = np.zeros((h_img,w_img), dtype=np.uint8)
    try:
        doc_o = ezdxf.read(io.StringIO(dxf_bytes.decode("utf-8", errors="replace")))
        msp_o = doc_o.modelspace()
        S = 0.1
        def to_px(x,y): return int(round(x/S)), int(round(h_img-y/S))
        for ent in msp_o:
            try:
                t = ent.dxftype()
                if t == "LWPOLYLINE":
                    plist = list(ent.get_points())
                    if len(plist) >= 2:
                        pp = np.array([to_px(p[0],p[1]) for p in plist], dtype=np.int32)
                        cv2.polylines(dxf_bin, [pp], False, 255, 2)
                elif t == "CIRCLE":
                    cx,cy = to_px(ent.dxf.center.x, ent.dxf.center.y)
                    r = int(round(ent.dxf.radius/S))
                    if r > 0: cv2.circle(dxf_bin,(cx,cy),r,255,2)
            except Exception: continue
    except Exception:
        return None, None

    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    orig_dil = cv2.dilate(orig_bin, k)
    dxf_dil  = cv2.dilate(dxf_bin, k)
    common_mask  = (orig_bin>0)&(dxf_dil>0)
    missing_mask = (orig_bin>0)&(dxf_dil==0)
    extra_mask   = (dxf_bin>0)&(orig_dil==0)

    out = np.full((h_img,w_img,3),(245,245,245),dtype=np.uint8)
    out[common_mask]  = (160,160,160)
    out[missing_mask] = (60,60,220)
    out[extra_mask]   = (30,180,200)

    n_orig = int(np.count_nonzero(orig_bin))
    n_common = int(np.count_nonzero(common_mask))
    n_missing = int(np.count_nonzero(missing_mask))
    coverage = n_common/n_orig*100 if n_orig>0 else 0
    miss_pct = n_missing/n_orig*100 if n_orig>0 else 0
    return cv2.cvtColor(out,cv2.COLOR_BGR2RGB), {"coverage":coverage,"missing":miss_pct}

# ══════════════════════════════════════════
#  UI
# ══════════════════════════════════════════

st.markdown("""
<div class="hero">
  <div class="hero-title">📐 도면 DXF 변환기 v2.1</div>
  <div class="hero-sub">이미지(JPG/PNG) → 벡터 DXF &nbsp;|&nbsp; 품질점수 · 프리셋 · 차이비교 · AutoCleanup &nbsp;|&nbsp; 도면팀-이영세</div>
</div>
""", unsafe_allow_html=True)

# ── 사이드바 ──
with st.sidebar:
    st.markdown("""
    <div style='background:#1a3a5c;padding:12px 14px;margin:-8px -14px 12px;
    border-bottom:2px solid #0078d4;'>
    <span style='color:#fff!important;font-weight:700;font-size:0.95rem;'>⚙️ 변환 설정</span>
    <span style='color:#6b9cc4!important;font-size:0.65rem;margin-left:8px;font-family:monospace;'>v2.1</span>
    </div>""", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "도면 이미지 선택 (다중 가능)",
        type=["jpg","jpeg","png"],
        accept_multiple_files=True
    )

    st.divider()

    # ── 프리셋 ──
    with st.expander("⭐ 프리셋 저장/불러오기", expanded=False):
        pnames = list(st.session_state["presets"].keys())
        sel_p = st.selectbox("저장된 프리셋", ["-- 선택 --"] + pnames, key="preset_sel")
        load_p = st.button("📂 불러오기", use_container_width=True, disabled=(sel_p=="-- 선택 --"))
        st.divider()
        new_name = st.text_input("저장할 이름", placeholder="예: 특허도면_기본", key="preset_name")
        save_p = st.button("💾 현재 설정 저장", use_container_width=True, disabled=(not new_name))
        if pnames:
            st.download_button("⬇️ 프리셋 내보내기",
                json.dumps(st.session_state["presets"], ensure_ascii=False, indent=2).encode(),
                "presets.json","application/json", use_container_width=True)
        f_import = st.file_uploader("⬆️ 프리셋 가져오기", type=["json"], key="p_import")
        if f_import:
            try:
                imp = json.loads(f_import.read().decode())
                st.session_state["presets"].update(imp)
                st.success(f"{len(imp)}개 가져오기 완료!")
            except Exception as e:
                st.error(f"오류: {e}")

    # 프리셋 값 가져오기
    _pv = st.session_state["presets"].get(sel_p, {}) if (load_p and sel_p != "-- 선택 --") else {}

    st.divider()

    # ── 기본 설정 ──
    with st.expander("🎚️ 기본 설정", expanded=True):
        threshold_val = st.slider("흑백 임계값 (−1=OTSU자동)", -1, 220, int(_pv.get("threshold_val", 127)))
        scale = st.slider("축척 (px→mm)", 0.05, 0.5, float(_pv.get("scale", 0.1)), step=0.01, format="%.2f")
        layer_name = st.text_input("레이어 이름", value=str(_pv.get("layer_name","OUTLINE")))

    with st.expander("🔬 고급 설정", expanded=False):
        smooth_window = st.slider("선 스무딩", 0, 25, int(_pv.get("smooth_window",9)))
        min_path_len  = st.slider("최소 경로 길이(px)", 2, 30, int(_pv.get("min_path_len",6)))
        stitch_gap    = st.slider("끊긴 선 잇기(px)", 0, 20, int(_pv.get("stitch_gap",4)))

    with st.expander("⭕ 원/호 인식", expanded=False):
        use_circle = st.checkbox("원·호 자동 인식", value=bool(_pv.get("use_circle",True)))

    with st.expander("🧹 전처리 / Auto Cleanup", expanded=False):
        use_denoise    = st.checkbox("노이즈 제거(Bilateral)", value=bool(_pv.get("use_denoise",True)))
        use_normalize  = st.checkbox("선 두께 정규화", value=bool(_pv.get("use_normalize",False)))
        use_gap_bridge = st.checkbox("Gap Bridge", value=bool(_pv.get("use_gap_bridge",False)))
        st.divider()
        use_auto_cleanup = st.checkbox("🧹 Auto Cleanup", value=bool(_pv.get("use_auto_cleanup",False)))
        cl_label = st.radio("강도", ["🟢 약함","🔵 표준","🟠 강함"], index=1,
                            disabled=not use_auto_cleanup)
        cleanup_level = {"🟢 약함":"light","🔵 표준":"standard","🟠 강함":"strong"}[cl_label]

    st.divider()

    # 프리셋 저장 처리
    if save_p and new_name:
        st.session_state["presets"][new_name] = {
            "threshold_val":threshold_val,"scale":scale,"layer_name":layer_name,
            "smooth_window":smooth_window,"min_path_len":min_path_len,"stitch_gap":stitch_gap,
            "use_circle":use_circle,"use_denoise":use_denoise,"use_normalize":use_normalize,
            "use_gap_bridge":use_gap_bridge,"use_auto_cleanup":use_auto_cleanup,
            "cleanup_level":cleanup_level,
            "saved_at":datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        st.success(f"✅ '{new_name}' 저장 완료!")

    do_convert = st.button("🚀 변환 시작", type="primary", use_container_width=True)

# ── 메인 ──
if not uploaded_files:
    st.info("← 왼쪽 사이드바에서 도면 이미지를 올려주세요 (JPG, PNG)")
    st.stop()

n_files = len(uploaded_files)
total_kb = sum(f.size for f in uploaded_files) / 1024
st.markdown(f"""
<div class="panel">
  <span style='font-weight:600;color:#1a3a5c;'>📂 {n_files}개 파일 선택됨</span>
  <span style='color:#5a7a96;font-size:0.8rem;margin-left:12px;font-family:monospace;'>총 {total_kb:.1f} KB</span>
</div>
""", unsafe_allow_html=True)

# ── 변환 실행 ──
if do_convert:
    results, failed = [], []
    prog = st.progress(0, text="변환 준비 중...")
    for idx, f in enumerate(uploaded_files):
        prog.progress(idx/n_files, text=f"변환 중: {f.name}")
        img_bytes = f.read()
        try:
            dxf_bytes, report, binary = convert_to_dxf_bytes(
                img_bytes,
                threshold_val=threshold_val, scale=scale, layer_name=layer_name,
                smooth_window=smooth_window, min_path_len=min_path_len,
                stitch_gap=stitch_gap, use_circle=use_circle,
                use_denoise=use_denoise, use_normalize=use_normalize,
                use_gap_bridge=use_gap_bridge,
                use_auto_cleanup=use_auto_cleanup, cleanup_level=cleanup_level,
            )
            out_name = os.path.splitext(f.name)[0] + "_dxf변환.dxf"
            results.append({"filename":out_name,"original":f.name,
                            "content":dxf_bytes,"image":img_bytes,"report":report})
        except Exception as e:
            failed.append({"name":f.name,"error":str(e)})
    prog.progress(1.0, text="✅ 변환 완료!")
    st.session_state["results"] = results
    st.session_state["failed"]  = failed

# ── 결과 ──
results = st.session_state.get("results",[])
failed  = st.session_state.get("failed",[])

if failed:
    for ff in failed:
        st.error(f"❌ {ff['name']} 실패: {ff['error']}")

if not results: st.stop()

n_ok = len(results)
total_lines   = sum(r["report"]["lines"] for r in results)
total_circles = sum(r["report"]["circles"] for r in results)
avg_score = int(sum(r["report"]["quality"]["score"] for r in results)/n_ok)
q0 = results[0]["report"]["quality"]
avg_grade = ("A+" if avg_score>=90 else "A" if avg_score>=80 else "B" if avg_score>=70
             else "C" if avg_score>=55 else "D" if avg_score>=40 else "F")
gc = {"A+":"#16a34a","A":"#22c55e","B":"#0078d4","C":"#f59e0b","D":"#ea580c","F":"#dc2626"}.get(avg_grade,"#5a7a96")

st.markdown(f"""
<div class="stat-grid">
  <div class="stat-cell"><div class="stat-num">{n_ok}</div><div class="stat-lbl">성공</div></div>
  <div class="stat-cell"><div class="stat-num">{total_lines}</div><div class="stat-lbl">추출 선</div></div>
  <div class="stat-cell"><div class="stat-num">{total_circles}</div><div class="stat-lbl">인식 원</div></div>
  <div class="stat-cell">
    <div class="stat-num" style="color:{gc};">{avg_score}</div>
    <div class="stat-lbl">품질점수</div>
    <span class="grade-badge" style="background:{gc}22;color:{gc};border:1px solid {gc}77;">{avg_grade}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# 다운로드
dl_cols = st.columns(min(n_ok,4))
for i,r in enumerate(results):
    with dl_cols[i % min(n_ok,4)]:
        st.download_button(f"📄 {r['filename']}", r["content"], r["filename"],
                           "application/dxf", key=f"dl_{i}", use_container_width=True)
zip_buf = io.BytesIO()
with zipfile.ZipFile(zip_buf,"w",zipfile.ZIP_DEFLATED) as zf:
    for r in results: zf.writestr(r["filename"], r["content"])
st.download_button(f"📦 전체 ZIP ({n_ok}개)", zip_buf.getvalue(),
                   "DXF_변환완료.zip","application/zip",
                   use_container_width=True, key="zip_dl")

# 미리보기
st.divider()
if n_ok > 1:
    opts = [r["original"] for r in results]
    preview_idx = opts.index(st.selectbox("미리볼 파일", opts))
else:
    preview_idx = 0

prev = results[preview_idx]
q = prev["report"]["quality"]
bd = q["breakdown"]

st.markdown(f"""
<div class="panel">
  <span style='font-weight:700;color:{q["color"]};font-size:1.1rem;'>{q["score"]}점</span>
  <span class="grade-badge" style='background:{q["color"]}22;color:{q["color"]};
  border:1px solid {q["color"]}77;margin-left:8px;'>{q["grade"]}</span>
  <span style='color:#5a7a96;font-size:0.75rem;margin-left:12px;font-family:monospace;'>
    연속성 {bd["continuity"]}/40 · 기하인식 {bd["geometry"]}/25 · 깔끔함 {bd["cleanliness"]}/20 · 변환량 {bd["yield"]}/15
  </span>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📷 Before / After", "🔍 차이 비교 (누락선)", "📊 리포트"])

with tab1:
    c1, c2 = st.columns(2, gap="small")
    with c1:
        st.markdown("<div class='prev-label before-lbl'>📷 Before — 원본</div>", unsafe_allow_html=True)
        arr = np.asarray(bytearray(prev["image"]),dtype=np.uint8)
        st.image(cv2.cvtColor(cv2.imdecode(arr,cv2.IMREAD_COLOR),cv2.COLOR_BGR2RGB), use_container_width=True)
    with c2:
        st.markdown("<div class='prev-label after-lbl'>📐 After — DXF</div>", unsafe_allow_html=True)
        with st.spinner("렌더링 중..."):
            fig = render_dxf_preview(prev["content"])
        if fig == "EMPTY": st.info("추출된 선이 없습니다.")
        elif isinstance(fig, str): st.warning(f"렌더링 오류: {fig}")
        else: st.pyplot(fig, use_container_width=True); plt.close(fig)

with tab2:
    st.markdown("<div class='prev-label diff-lbl'>🔍 파랑=누락선 · 청록=추가선 · 회색=일치</div>", unsafe_allow_html=True)
    with st.spinner("차이 분석 중..."):
        diff_img, diff_stats = render_diff_overlay(prev["image"], prev["content"])
    if diff_img is not None and diff_stats:
        c1,c2 = st.columns(2)
        c1.metric("커버리지", f"{diff_stats['coverage']:.1f}%")
        c2.metric("누락선 비율", f"{diff_stats['missing']:.1f}%")
        st.image(diff_img, use_container_width=True)
    else:
        st.warning("차이 비교를 생성할 수 없습니다.")

with tab3:
    for r in results:
        rpt=r["report"]; q2=rpt["quality"]; bd2=q2["breakdown"]
        w_mm=rpt['img_w']*rpt['scale']; h_mm=rpt['img_h']*rpt['scale']
        st.markdown(f"""
        <div class="report-row" style="border-left-color:{q2['color']};">
          <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;'>
            <b style='color:#1a3a5c;'>{r['original']}</b>
            <span class="grade-badge" style='background:{q2["color"]}22;color:{q2["color"]};
            border:1px solid {q2["color"]}77;'>{q2["score"]}점 / {q2["grade"]}</span>
          </div>
          <span style='color:#5a7a96;font-size:0.75rem;font-family:monospace;'>
            {rpt['img_w']}×{rpt['img_h']}px · ≈{w_mm:.0f}×{h_mm:.0f}mm · 선 {rpt['lines']}개 · 원 {rpt['circles']}개
          </span>
          <div style='margin-top:6px;font-size:0.7rem;color:#7a8fa6;font-family:monospace;'>
            연속성 {bd2["continuity"]}/40 · 기하 {bd2["geometry"]}/25 · 깔끔함 {bd2["cleanliness"]}/20 · 변환량 {bd2["yield"]}/15
          </div>
        </div>""", unsafe_allow_html=True)

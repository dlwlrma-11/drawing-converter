"""
도면 DXF 변환기 — 웹 배포 테스트 버전
원본: Auto_Web.py v6.3 (도면팀-이영세)
웹 최적화: easyocr·AI SR·SQLite 제거, 핵심 엔진 유지
"""

import io, os, math, zipfile, datetime
import cv2, ezdxf, numpy as np
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skimage.morphology import skeletonize
from scipy.ndimage import uniform_filter1d

try:
    from sklearn.cluster import DBSCAN
    _DBSCAN_OK = True
except ImportError:
    _DBSCAN_OK = False

try:
    import plotly.graph_objects as go
    _PLOTLY_OK = True
except ImportError:
    _PLOTLY_OK = False

# ══════════════════════════════════════════
#  페이지 설정
# ══════════════════════════════════════════
st.set_page_config(page_title="도면 DXF 변환기", page_icon="📐", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif!important;}
#MainMenu,header,[data-testid="stToolbar"],footer,.stDeployButton{display:none!important;}
.stApp{background:#edf0f4!important;}
.block-container{padding-top:2rem!important;}
section[data-testid="stSidebar"]{width:380px!important;min-width:380px!important;max-width:380px!important;background:#f4f6f9!important;}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,[data-testid="stSidebar"] label{color:#1a3a5c!important;}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p{color:#1a3a5c!important;}
.hero{background:#0d1117;border-radius:10px;padding:20px 28px;margin-bottom:12px;border-left:4px solid #0078d4;}
.hero-title{color:#fff;font-size:1.4rem;font-weight:700;margin:0 0 4px 0;}
.hero-sub{color:#7ec8ff;font-family:'JetBrains Mono',monospace;font-size:0.72rem;margin:0;}
.panel{background:#fff;border-radius:8px;padding:14px 18px;border:1px solid #d0d7e0;margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,.04);}
.stat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:#d0d7e0;border:1px solid #d0d7e0;border-radius:8px;overflow:hidden;margin:10px 0;}
.stat-cell{background:#fff;padding:12px;text-align:center;}
.stat-num{font-size:1.4rem;font-weight:700;color:#1a3a5c;font-family:'JetBrains Mono',monospace;}
.stat-lbl{font-size:0.65rem;color:#5a7a96;text-transform:uppercase;letter-spacing:.04em;font-weight:600;}
.prev-label{font-size:0.78rem;font-weight:600;padding:5px 10px;border-radius:5px;margin-bottom:6px;display:flex;align-items:center;gap:6px;}
.before-lbl{background:#f5f7fa;border-left:3px solid #7a8fa6;color:#1a3a5c;}
.after-lbl{background:#e8f0f9;border-left:3px solid #0078d4;color:#1a3a5c;}
[data-testid="stFileUploader"]{background:#f0f6ff!important;border:1.5px dashed #9ab5d0!important;border-radius:8px!important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
#  핵심 변환 함수들 (Auto_Web.py v6.3 엔진)
# ══════════════════════════════════════════

def smooth_path(pts, window=9):
    if len(pts) < window or window < 4: return pts
    w = max(3, window | 1)
    if len(pts) <= w: w = max(3, len(pts) - 1 if len(pts) % 2 == 0 else len(pts))
    if w < 3: return pts
    try:
        from scipy.signal import savgol_filter
        xs = savgol_filter(pts[:, 0].astype(float), window_length=w, polyorder=2)
        ys = savgol_filter(pts[:, 1].astype(float), window_length=w, polyorder=2)
    except Exception:
        xs = uniform_filter1d(pts[:, 0].astype(float), size=w)
        ys = uniform_filter1d(pts[:, 1].astype(float), size=w)
    xs[0], xs[-1] = pts[0, 0], pts[-1, 0]
    ys[0], ys[-1] = pts[0, 1], pts[-1, 1]
    return np.column_stack([xs, ys])


def fit_circle_algebraic(pts):
    if len(pts) < 3: return None, None, float('inf')
    x, y = pts[:, 0], pts[:, 1]
    A = np.column_stack([x, y, np.ones(len(x))])
    B = -(x**2 + y**2)
    try:
        res, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
        D, E, F = res
        cx, cy = -D / 2, -E / 2
        radius = math.sqrt(max(0, cx**2 + cy**2 - F))
        dists = np.sqrt((x - cx)**2 + (y - cy)**2)
        error = np.mean(np.abs(dists - radius))
        return (cx, cy), radius, error
    except Exception:
        return None, None, float('inf')


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
    """8방향 스켈레톤 그래프 순회로 경로 추출"""
    skel = (skeleton > 0).astype(np.uint8)
    h, w = skel.shape
    visited = np.zeros((h, w), dtype=bool)
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    def neighbors(y, x):
        return [(y+dy, x+dx) for dy, dx in dirs
                if 0 <= y+dy < h and 0 <= x+dx < w and skel[y+dy, x+dx] == 1]

    def degree(y, x):
        return len(neighbors(y, x))

    ys, xs = np.where(skel == 1)
    endpoints = [(int(y), int(x)) for y, x in zip(ys, xs) if degree(int(y), int(x)) == 1]
    branches  = [(int(y), int(x)) for y, x in zip(ys, xs) if degree(int(y), int(x)) >= 3]
    starts    = endpoints + branches if endpoints or branches else [(int(ys[0]), int(xs[0]))] if len(ys) > 0 else []

    paths = []
    for sy, sx in starts:
        for ny, nx in neighbors(sy, sx):
            if visited[ny, nx]: continue
            path = [(sx, sy)]
            visited[ny, nx] = True
            cy, cx = ny, nx
            while True:
                path.append((cx, cy))
                nbrs = [(y2, x2) for y2, x2 in neighbors(cy, cx) if not visited[y2, x2]]
                if not nbrs: break
                cy, cx = nbrs[0]
                visited[cy, cx] = True
                if degree(cy, cx) >= 3: path.append((cx, cy)); break
            if len(path) >= 2:
                paths.append(np.array(path, dtype=float))
    # 방문 안된 고립 픽셀 처리
    for y, x in zip(ys.tolist(), xs.tolist()):
        if not visited[y, x] and skel[y, x] == 1:
            paths.append(np.array([[x, y]], dtype=float))
    return paths


def preprocess_image(img_gray, threshold_val=127, denoise=True, deskew=False,
                     normalize_thickness=False, gap_bridge=False):
    """이미지 전처리 파이프라인"""
    if denoise:
        img_gray = cv2.bilateralFilter(img_gray, 9, 75, 75)
    if threshold_val < 0:
        _, binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        _, binary = cv2.threshold(img_gray, threshold_val, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((2, 2), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    if gap_bridge:
        bridge_k = np.ones((5, 5), np.uint8)
        binary = cv2.dilate(binary, bridge_k, iterations=1)
        binary = cv2.erode(binary, bridge_k, iterations=1)
    if normalize_thickness:
        dist = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
        _, center = cv2.threshold(dist, 0.5, 255, cv2.THRESH_BINARY)
        k = np.ones((2, 2), np.uint8)
        binary = cv2.dilate(center.astype(np.uint8), k, iterations=1)
    return binary


def convert_to_dxf_bytes(img_bytes, threshold_val=127, scale=0.1,
                          layer_name="OUTLINE", smooth_window=9,
                          min_path_len=6, stitch_gap=4,
                          use_circle=True, circle_error=2.5,
                          use_denoise=True, use_normalize=False,
                          use_gap_bridge=False):
    """이미지 → DXF 바이트 변환 (핵심 엔진)"""
    arr = np.asarray(bytearray(img_bytes), dtype=np.uint8)
    img_color = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img_color is None:
        raise ValueError("이미지를 읽을 수 없습니다.")

    img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
    h, w = img_gray.shape

    binary = preprocess_image(img_gray, threshold_val=threshold_val,
                               denoise=use_denoise,
                               normalize_thickness=use_normalize,
                               gap_bridge=use_gap_bridge)

    # 원/호 감지 (HoughCircles)
    circles_out = []
    circle_mask = np.zeros_like(binary)
    if use_circle:
        circles_hough = cv2.HoughCircles(
            cv2.GaussianBlur(img_gray, (9, 9), 2),
            cv2.HOUGH_GRADIENT, dp=1, minDist=20,
            param1=50, param2=30, minRadius=8, maxRadius=min(h, w) // 3
        )
        if circles_hough is not None:
            for cx, cy, cr in circles_hough[0]:
                cx, cy, cr = int(round(cx)), int(round(cy)), int(round(cr))
                circles_out.append((cx, cy, cr))
                cv2.circle(circle_mask, (cx, cy), cr, 255, thickness=max(3, cr // 8))
            # 원 영역을 binary에서 제거 (중복 방지)
            binary = cv2.bitwise_and(binary, cv2.bitwise_not(circle_mask))

    # 스켈레톤 → 경로 추출
    skel_input = (binary > 0).astype(np.uint8)
    skeleton = skeletonize(skel_input).astype(np.uint8)

    paths = skeleton_to_paths(skeleton)

    # 경로 필터 + 스무딩 + 잇기
    def path_len(p):
        if len(p) < 2: return 0
        d = np.diff(p, axis=0)
        return float(np.sum(np.hypot(d[:, 0], d[:, 1])))

    paths = [p for p in paths if path_len(p) >= min_path_len]
    if stitch_gap > 0:
        paths = stitch_close_paths(paths, max_gap_px=float(stitch_gap))
    if smooth_window >= 4:
        paths = [smooth_path(p, window=smooth_window) if len(p) >= smooth_window else p for p in paths]

    # DXF 생성
    doc = ezdxf.new('R2010')
    doc.layers.new(name=layer_name, dxfattribs={'color': 7})
    if circles_out:
        doc.layers.new(name="CIRCLE", dxfattribs={'color': 3})
    msp = doc.modelspace()

    n_lines, n_circles = 0, 0

    # 경로 → LWPOLYLINE
    for pts in paths:
        if len(pts) < 2: continue
        dxf_pts = [(float(x) * scale, float(h - y) * scale) for x, y in pts]
        polyline = msp.add_lwpolyline(dxf_pts, dxfattribs={'layer': layer_name})
        start, end = dxf_pts[0], dxf_pts[-1]
        dist = math.hypot(start[0] - end[0], start[1] - end[1])
        if dist < scale * 3:
            polyline.close(True)
        n_lines += 1

    # 원 → CIRCLE
    for cx, cy, cr in circles_out:
        dxf_cx = float(cx) * scale
        dxf_cy = float(h - cy) * scale
        dxf_r  = float(cr) * scale
        msp.add_circle((dxf_cx, dxf_cy), dxf_r, dxfattribs={'layer': 'CIRCLE'})
        n_circles += 1

    buf = io.BytesIO()
    doc.write(buf)

    report = {
        "img_w": w, "img_h": h,
        "lines": n_lines, "circles": n_circles,
        "scale": scale,
    }
    return buf.getvalue(), report


def render_dxf_preview(dxf_bytes, bg="#1a1d2e", line_color="#e0e4ef"):
    """DXF → matplotlib Figure"""
    try:
        doc = ezdxf.read(io.StringIO(dxf_bytes.decode("utf-8", errors="replace")))
        msp = doc.modelspace()
    except Exception as e:
        return str(e)

    entities = list(msp)
    if not entities:
        return "EMPTY"

    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.set_aspect('equal')
    ax.axis('off')

    for ent in entities:
        try:
            t = ent.dxftype()
            lc = "#4ec9b0" if ent.dxf.layer == "CIRCLE" else line_color
            if t == "LWPOLYLINE":
                pts = list(ent.get_points())
                if len(pts) >= 2:
                    xs = [p[0] for p in pts]
                    ys = [p[1] for p in pts]
                    if ent.is_closed: xs.append(xs[0]); ys.append(ys[0])
                    ax.plot(xs, ys, color=lc, linewidth=0.6)
            elif t == "CIRCLE":
                cx, cy = ent.dxf.center.x, ent.dxf.center.y
                r = ent.dxf.radius
                theta = np.linspace(0, 2 * math.pi, 80)
                ax.plot(cx + r * np.cos(theta), cy + r * np.sin(theta), color=lc, linewidth=0.6)
        except Exception:
            continue

    plt.tight_layout(pad=0)
    return fig


# ══════════════════════════════════════════
#  UI 레이아웃
# ══════════════════════════════════════════

# 배너
st.markdown("""
<div class="hero">
  <div class="hero-title">📐 도면 DXF 변환기</div>
  <div class="hero-sub">이미지(JPG/PNG) → 벡터 DXF | 웹 테스트 버전 | 도면팀-이영세</div>
</div>
""", unsafe_allow_html=True)

# ── 사이드바 ──────────────────────────────
with st.sidebar:
    st.markdown("<div style='background:#1a3a5c;padding:12px 14px;margin:-8px -14px 12px;border-bottom:2px solid #0078d4;'><span style='color:#fff;font-weight:700;font-size:0.95rem;'>⚙️ 변환 설정</span></div>", unsafe_allow_html=True)

    # 파일 업로드
    uploaded_files = st.file_uploader(
        "도면 이미지 선택 (다중 가능)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    st.divider()

    with st.expander("🎚️ 기본 설정", expanded=True):
        threshold_val = st.slider("흑백 임계값 (−1 = OTSU 자동)", -1, 220, 127)
        scale = st.slider("축척 (픽셀 → mm)", 0.05, 0.5, 0.1, step=0.01, format="%.2f")
        layer_name = st.text_input("레이어 이름", value="OUTLINE")

    with st.expander("🔬 고급 설정", expanded=False):
        smooth_window = st.slider("선 스무딩 (클수록 부드러움)", 0, 25, 9)
        min_path_len  = st.slider("최소 경로 길이 (px)", 2, 30, 6)
        stitch_gap    = st.slider("끊긴 선 잇기 허용 거리 (px)", 0, 20, 4)

    with st.expander("⭕ 원/호 인식", expanded=False):
        use_circle = st.checkbox("원·호 자동 인식 (HoughCircles)", value=True)
        circle_error = st.slider("원 피팅 허용 오차", 0.5, 8.0, 2.5, step=0.5)

    with st.expander("🧹 전처리 옵션", expanded=False):
        use_denoise   = st.checkbox("노이즈 제거 (Bilateral)", value=True)
        use_normalize = st.checkbox("선 두께 정규화", value=False)
        use_gap_bridge = st.checkbox("끊긴 선 메우기 (Gap Bridge)", value=False)

    st.divider()
    do_convert = st.button("🚀 변환 시작", type="primary", use_container_width=True)

# ── 메인 영역 ─────────────────────────────

if not uploaded_files:
    st.info("← 왼쪽 사이드바에서 도면 이미지를 올려주세요 (JPG, PNG)")
    st.stop()

# 파일 정보 표시
n_files = len(uploaded_files)
total_size = sum(f.size for f in uploaded_files)
st.markdown(f"""
<div class="panel">
  <span style='font-weight:600;color:#1a3a5c;'>📂 {n_files}개 파일 선택됨</span>
  <span style='color:#5a7a96;font-size:0.8rem;margin-left:12px;font-family:monospace;'>총 {total_size/1024:.1f} KB</span>
</div>
""", unsafe_allow_html=True)

# 변환 실행
if do_convert:
    results = []
    failed  = []
    progress = st.progress(0, text="변환 준비 중...")

    for idx, f in enumerate(uploaded_files):
        progress.progress((idx) / n_files, text=f"변환 중: {f.name}")
        img_bytes = f.read()
        try:
            dxf_bytes, report = convert_to_dxf_bytes(
                img_bytes,
                threshold_val=threshold_val,
                scale=scale,
                layer_name=layer_name,
                smooth_window=smooth_window,
                min_path_len=min_path_len,
                stitch_gap=stitch_gap,
                use_circle=use_circle,
                circle_error=circle_error,
                use_denoise=use_denoise,
                use_normalize=use_normalize,
                use_gap_bridge=use_gap_bridge,
            )
            out_name = os.path.splitext(f.name)[0] + "_dxf변환.dxf"
            results.append({
                "filename": out_name,
                "original": f.name,
                "content":  dxf_bytes,
                "image":    img_bytes,
                "report":   report,
            })
        except Exception as e:
            failed.append({"name": f.name, "error": str(e)})

    progress.progress(1.0, text="✅ 변환 완료!")
    st.session_state["results"] = results
    st.session_state["failed"]  = failed

# 결과 표시
results = st.session_state.get("results", [])
failed  = st.session_state.get("failed",  [])

if results:
    n_ok = len(results)
    n_fail = len(failed)
    total_lines   = sum(r["report"]["lines"] for r in results)
    total_circles = sum(r["report"]["circles"] for r in results)

    st.markdown(f"""
    <div class="stat-grid">
      <div class="stat-cell"><div class="stat-num">{n_ok}</div><div class="stat-lbl">성공</div></div>
      <div class="stat-cell"><div class="stat-num">{total_lines}</div><div class="stat-lbl">추출 선</div></div>
      <div class="stat-cell"><div class="stat-num">{total_circles}</div><div class="stat-lbl">인식 원</div></div>
    </div>
    """, unsafe_allow_html=True)

    if n_fail:
        st.error(f"❌ {n_fail}개 실패: " + ", ".join(f["name"] for f in failed))

    # 개별 다운로드
    st.markdown("<div class='panel'><b style='color:#1a3a5c;'>💾 개별 파일 다운로드</b></div>", unsafe_allow_html=True)
    cols = st.columns(min(n_ok, 4))
    for i, r in enumerate(results):
        with cols[i % min(n_ok, 4)]:
            st.download_button(
                label=f"📄 {r['filename']}",
                data=r["content"],
                file_name=r["filename"],
                mime="application/dxf",
                key=f"dl_{i}",
                use_container_width=True,
            )

    # ZIP 다운로드
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for r in results:
            zf.writestr(r["filename"], r["content"])
    st.download_button(
        label=f"📦 전체 ZIP 다운로드 ({n_ok}개)",
        data=zip_buf.getvalue(),
        file_name="DXF_변환완료.zip",
        mime="application/zip",
        use_container_width=True,
        key="zip_dl",
    )

    # 미리보기
    st.divider()
    preview_idx = 0
    if n_ok > 1:
        opts = [r["original"] for r in results]
        sel = st.selectbox("미리볼 파일 선택", opts)
        preview_idx = opts.index(sel)

    prev = results[preview_idx]
    col_orig, col_dxf = st.columns(2, gap="small")

    with col_orig:
        st.markdown("<div class='prev-label before-lbl'>📷 Before — 원본 이미지</div>", unsafe_allow_html=True)
        arr = np.asarray(bytearray(prev["image"]), dtype=np.uint8)
        img_rgb = cv2.cvtColor(cv2.imdecode(arr, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        st.image(img_rgb, use_container_width=True)

    with col_dxf:
        st.markdown("<div class='prev-label after-lbl'>📐 After — DXF 결과</div>", unsafe_allow_html=True)
        with st.spinner("DXF 렌더링 중..."):
            fig = render_dxf_preview(prev["content"])
        if fig == "EMPTY":
            st.info("ℹ️ 추출된 선이 없습니다.")
        elif isinstance(fig, str):
            st.warning(f"렌더링 오류: {fig}")
        else:
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

    # 변환 리포트
    with st.expander("📊 파일별 변환 리포트", expanded=False):
        for r in results:
            rpt = r["report"]
            w_mm = rpt['img_w'] * rpt['scale']
            h_mm = rpt['img_h'] * rpt['scale']
            st.markdown(f"""
            <div style='border:1px solid #d0d7e0;border-left:3px solid #0078d4;border-radius:6px;padding:8px 14px;margin-bottom:6px;background:#fff;'>
              <b style='color:#1a3a5c;font-size:0.85rem;'>{r['original']}</b>
              <span style='color:#5a7a96;font-size:0.75rem;margin-left:10px;font-family:monospace;'>
                {rpt['img_w']}×{rpt['img_h']}px · ≈{w_mm:.0f}×{h_mm:.0f}mm · 선 {rpt['lines']}개 · 원 {rpt['circles']}개
              </span>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.get("results") is not None:
    st.info("변환 결과가 없습니다. 설정을 조정하고 다시 시도해보세요.")

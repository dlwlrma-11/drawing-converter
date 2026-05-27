"""
이미지 일괄 DXF 변환 시스템 v6.9 (도면팀-이영세) — 웹 배포본 (app.py)
========================================================================
🌐 본 파일은 GitHub + Streamlit Cloud 등 웹 배포 전용 버전입니다.
   로컬 Windows 버전 (Auto_Web.py) 과 동일 코드이지만, Linux 환경에서는
   ODA File Converter / AutoCAD 자동 연동이 자동으로 비활성화됩니다.
   (Windows 가드: _IS_WINDOWS 체크가 모든 외부 도구 호출에 적용됨)

[v6.9 변경사항] ★ 파일명 단순화 + DXF→DWG 일괄변환 버튼 제거 ★
  ★ CHANGE: 파일명 규칙 단순화
      - 기존: 원본이름_dxf변환.dxf / 원본이름_dxf변환.dwg
      - 변경: 원본이름.dxf / 원본이름.dwg  (깔끔하고 직관적)
      - 중복 시: 원본이름 (2).dwg, 원본이름 (3).dwg 자동 번호
  ★ REMOVE: 결과 화면의 "DXF → DWG 일괄 변환" 버튼 섹션 제거
      - 변환 시점에 이미 DWG로 저장되므로 중복 기능
      - 메인 UI가 훨씬 깔끔해짐
  ★ KEEP: AutoCAD 자동 정리 기능은 그대로 유지
      - 🅰️ AutoCAD에서 첫 파일 자동 열기 (OVERKILL + PEDIT JOIN + 자동 저장)
      - 🅰️ 모든 파일 AutoCAD 자동 정리 (일괄 처리)
  ★ NEW: config.json 영구 저장/로드 시스템
      - 저장 항목: ODA 경로, AutoCAD 경로, DWG 버전, SCR 옵션, 출력 형식
      - 앱 껐다 켜도 설정 자동 복원 (재입력 불필요)
      - 저장 위치: Auto_Web.py와 같은 폴더 (config.json)
  ★ NEW: 사이드바 "💾 ODA·AutoCAD 경로 설정 저장" 버튼
      - 한 번 저장하면 이후부터 자동 로드
  ★ NEW: ODA·AutoCAD 자동 발견 시 config.json에도 자동 저장
      - 직접 저장 버튼 안 눌러도 자동 발견되면 바로 저장됨
  ★ NEW: 메인 화면 변환 버튼 위에 출력 형식 선택 라디오 추가
      - 🏗️ DWG만 저장 (기본, 권장)
      - 📐🏗️ DXF + DWG 둘 다 저장 (안전망)
      → 사이드바 안 열어도 한눈에 보임. 앱 켜자마자 DWG 변환 가능
  ★ CHANGE: 기본값을 'DWG만 저장'으로 변경 (기존: DXF만)
  ★ CHANGE: 'DXF만 저장' 옵션 메인 UI에서 제거 (사이드바·내부 로직은 보존)
      - 메인 화면에서는 DWG/둘다만 노출 — 사용자 의도와 일치
  ★ CHANGE: 사이드바 출력 형식 라디오 삭제 (메인으로 이동했으니 중복 제거)
  ★ NEW: ODA 설치 상태 배지 표시 (✅ 준비됨 / ❌ 미설치 / ⚠️ Windows 전용)
      - 변환 버튼 옆에 한눈에 보이는 상태 표시
      - ODA 미설치 시 친절한 설치 안내 expander 자동 표시
  ★ 안전 fallback (기존 그대로 유지):
      - ODA 없으면 DWG 요청해도 자동으로 DXF로 대체 저장 + 경고
      - 한 파일만 DWG 실패해도 그 파일만 DXF로 폴백, 나머지는 계속
[v6.6 변경사항] ★ 변환 시점 DWG 자동 저장 (사용자 요청 핵심 UX 개선) ★
  ★ NEW: 📤 사이드바 "출력 형식 선택" 라디오 추가
      🅳 DXF만 저장 (기본 동작)
      🅴 DWG만 저장 (변환 직후 자동으로 DWG 생성, DXF 파일 안 만듦)
      🅵 DXF + DWG 둘 다 저장 (ZIP에 두 파일 모두 포함)
  ★ NEW: 변환 버튼 라벨/진행률 텍스트가 선택한 출력 형식에 따라 자동 변경
      예: "📐 DXF 파일로 변환" → "🏗️ DWG 파일로 변환 (ODA 자동 호출)"
  ★ NEW: 변환 루프 내부에서 DWG 자동 생성 (별도 버튼 클릭 불필요)
      - convert_to_dxf_bytes() 직후 convert_dxf_to_dwg_via_oda() 자동 호출
      - 출력 형식에 맞춰 ZIP 파일명도 자동 변경 (DXF_변환완료.zip / DWG_변환완료.zip / DXF_DWG_변환완료.zip)
  ★ NEW: 개별 다운로드 버튼이 출력 형식에 따라 자동 적응
      - DXF만/DWG만/둘다 — 각각 적절한 버튼 표시
  ★ 안전 fallback:
      - ODA Converter 미설치 + DWG 선택 시 → 자동으로 DXF만 저장 + 경고
      - DWG 변환 실패 1개 발생 시 → 그 파일만 DXF로 fallback (전체 변환은 계속)
[v6.5 변경사항] ★ DWG 직접 저장 + AutoCAD 자동 후처리 (Windows 전용) ★
  ★ NEW: 🏗️ DXF → DWG 일괄 변환 (ODA File Converter 무료 도구 연동)
      - AutoCAD 2000/2004/2007/2010/2013/2018 모든 버전 출력 지원
      - 한글 경로 회피 자동 처리 (ASCII-only 임시 디렉터리 사용)
      - DWG ZIP 일괄 다운로드 버튼 추가
  ★ NEW: 🅰️ AutoCAD 자동 실행 + 자동 정리 SCR 스크립트
      - OVERKILL (중복선 자동 제거, 풀버전 전용)
      - PEDIT JOIN (분리된 polyline 자동 결합)
      - ZOOM EXTENTS (도면 전체 보기 자동)
      - PURGE (사용하지 않는 객체 정리, 선택)
      - QSAVE (자동 저장)
  ★ NEW: 🔧 사이드바 "DWG/AutoCAD 자동 연동" 설정 패널
      - ODA Converter / acad.exe 경로 자동 탐색 + 수동 지정 가능
      - DWG 출력 버전 선택 (R2018 ~ R2000)
      - SCR 자동 정리 옵션 토글 5종
[v6.4 변경사항] ★ 변환 품질 직접 개선 5종 + UI/UX 개선 3종 ★
  ★ [개선 ①] 이진화 blockSize 자동 계산 (enhance_edge)
      - 기존: blockSize=15 고정 → 고해상도(4K+) 도면에서 선 끊김 다발
      - 개선: 짧은 변의 약 1.5% 자동 계산 (1000px→15, 2000px→31, 4000px→61)
  ★ [개선 ②] MORPH_CLOSE 추가 (enhance_edge)
      - 기존: OPEN만 적용 → 1~2px 미세 끊김선 연결 안됨
      - 개선: OPEN→CLOSE 순서로 적용 → 스캔 도면 끊김 자동 연결
  ★ [개선 ③] Closed Path 자동 인식 (_add_lwpolyline_auto)
      - 기존: 사각형/원형 테두리도 open polyline → CAD 편집 불편
      - 개선: 시작점-끝점 거리 3px 이내면 자동 closed (해치 fill 가능)
  ★ [개선 ④] Adaptive Epsilon (_adaptive_epsilon)
      - 기존: 모든 path에 동일 epsilon → 짧은 path 형태 왜곡, 긴 path 노드 폭증
      - 개선: path 길이 비례 자동 조정 (짧은 path는 정밀, 긴 path는 단순화)
  ★ [개선 ⑤] Smooth Window 자동 상한 (smooth_path)
      - 기존: 짧은 path에 큰 window 적용 → 원/호 형태 손상
      - 개선: window를 path 길이의 1/4로 자동 제한
  ★ [UI ⑥] 퀵 변환 3단계 버튼 (⚡빠름/⚖️균형/🔬정밀)
  ★ [UI ⑦] 슬라이더 숫자 직접 입력 (정밀 조정 가능)
  ★ [UI ⑧] 고급 옵션 기본 접힘 (사이드바 가독성 향상)
[v6.3 변경사항] ★ AI/UX/CAD 6대 기능 추가 ★
  ★ NEW: 🤖 AI Super-Resolution (FSRCNN_x2.pb) - 저해상도 자동 업스케일 → 벡터화 성공률 향상
  ★ NEW: 🎯 Arc fitting RANSAC - 노이즈에 강한 원/호 인식 (algebraic + RANSAC 자동 fallback)
  ★ NEW: 🔤 OCR → MTEXT 업그레이드 - 신뢰도 0.5+ 필터링 + MTEXT 엔티티 + 한글 멀티라인 지원
  ★ NEW: 🔍 Plotly 인터랙티브 차이 비교 뷰어 - 줌/패닝으로 누락선 정밀 검수
  ★ NEW: 🖼️ st-canvas 시각적 Crop - 마우스 드래그로 변환 영역 직접 선택
  ★ NEW: 📐 사이드바 레이아웃 최적화 (DOM 실측값 기반: right=420, label-left=27)
[v6.2 변경사항] ★ 실무 워크플로우 4대 기능 추가 ★
  ★ NEW: ⭐ 사용자 정의 프리셋 저장 - 이름 붙여서 SQLite에 영구 저장 (회사별/프로젝트별 설정 관리)
  ★ NEW: 🤖 AI 추천 강화 - 이미지 분석 결과로 슬라이더 수치까지 구체적으로 자동 추천
  ★ NEW: 🎚️ 오버레이 투명도 슬라이더 - 실시간 alpha 조절 (검수 정밀도 향상)
  ★ NEW: 🔁 단일 파일 재변환 - 결과 화면에서 특정 파일만 설정 바꿔 다시 변환
[v6.1 변경사항] ★ 실무 자동화 3대 기능 추가 ★
  ★ NEW: 🪄 자동 CAD 정리 (Auto Cleanup) - 끊긴 선 연결 + 수직/수평 직교 보정 + 잡선 제거 (원클릭)
  ★ NEW: 📊 업로드 즉시 이미지 품질 자동 분석 - 해상도·선명도·노이즈 분석 → A~D 등급 + 추천 옵션
  ★ NEW: 🎯 누락선 강조 차이 비교 - 원본/DXF 차이를 빨강(누락)/청록(추출)로 시각화 (검수 시간 단축)
[v6.0 변경사항] ★ Scan2CAD급 6대 기능 추가 ★
  ★ NEW: 대시선/점선 자동 인식 - 선 종류별 DXF LINETYPE 자동 분류
  ★ NEW: 이미지 자동 클린 강화 - Deskew 기울기 보정 + Speckle 제거 + Gap Bridge
  ★ NEW: 선 종류별 레이어 자동 분리 - OUTLINE/HIDDEN/CENTER/CIRCLE/HATCH
  ★ NEW: 해치(Hatch) 패턴 자동 인식 - DXF SOLID 엔티티로 변환
  ★ NEW: 래스터 오버레이 미리보기 - 원본 이미지 + DXF 선 겹쳐보기
  ★ NEW: Bezier 곡선(SPLINE) 토글 - UI 토글로 ON/OFF 제어
[v5.0 변경사항] ★ 엔진 5종 개선 + UX 강화 ★
  ★ NEW: 잔가지(Spur) 자동 제거 - skeleton의 짧은 가지 반복 pruning
  ★ NEW: 코너 앵커링 - 직각/예각 검출 후 스무딩 전 보존 처리
  ★ NEW: DXF 품질 점수 시스템 - 0~100점 + 등급(A+~F) 자동 평가
  ★ NEW: 방향인식 선 잇기 - 접선 코사인 유사도로 잘못된 병합 방지
  ★ NEW: 변환 영역 자르기 (Crop) - 스캔 테두리/얼룩 사전 제거
  ★ UI: 결과 화면 품질 점수 카드 + 등급 뱃지
  ★ UI: 파일별 리포트에 품질 점수 표시
[v4.1 변경사항] ★ 미리보기 줌·배경·선정규화 패치 ★
  ★ NEW: DXF 미리보기 인터랙티브 줌/패닝 (Plotly 기반)
  ★ NEW: 미리보기 배경 전환 (CAD Dark / White Paper / Blueprint)
  ★ NEW: 선 두께 정규화 전처리 옵션 (distanceTransform 기반)
[v4.0 변경사항] ★ 통합 UI/기능 개선 패치 ★
  ★ NEW: 설정 저장/불러오기 (JSON 프리셋)
  ★ NEW: 7일 변환 통계 미니 차트
  ★ NEW: 변환 이력 관리 (SQLite 조회 패널)
  ★ NEW: 오류 파일 건너뛰기 + 부분 ZIP 다운로드
  ★ NEW: 파일별 변환 결과 리포트 (선/원/텍스트 통계)
  ★ UI: 통계 대시보드 7일 차트 추가
  ★ UI: 파일 업로드 정보 카드 (용량/개수)
  ★ UI: 3단 미리보기 단계 번호 + 하단 정보
  ★ UI: 변환 완료 통계 카드 (4분할)
  ★ UI: 진행 중 파일별 점 표시
[v3.2 변경사항]
  ★ 토글 초기 빨간색 flash 제거: JS 실행 즉시 parent <head>에 CSS 주입
  ★ 토글 thumb overflow 근본 수정: clip-path 적용
  ★ 토글 우측 정렬: getBoundingClientRect() 픽셀 직접 계산
[v3.1 변경사항]
  ★ 두줄 모드 엔진 교체: findContours → skeleton graph traversal (곡선 jagged 현상 해결)
  ★ 사이드바 기본/고급 옵션 분리 (초보자 부담 감소)
  ★ 호/원 자동 인식(ARC/CIRCLE) 사이드바 토글 추가
  ★ 파일명 규칙 통일: 원본이름_dxf변환.dxf
  ★ 미리보기 라벨 사용자 친화적 표현으로 변경
  ★ 두줄 모드 get_optimized_image_preview skeleton 방식 통일
[v3.0 변경사항]
  ★ 3단계 워크플로우 적용 (원본 이미지 -> 최적화된 도면 분석 -> DXF 변환 미리보기)
  ★ 중간 전처리 이미지(Skeleton) 시각화 기능 추가
"""

import io
import os
import math
import json
import zipfile
import uuid
import base64
import sqlite3
import datetime
import subprocess      # 🆕 v6.5: ODA File Converter / AutoCAD 외부 프로그램 호출
import tempfile        # 🆕 v6.5: DWG 변환 작업용 임시 디렉터리
import shutil          # 🆕 v6.5: ODA / AutoCAD 실행파일 탐색 및 파일 복사
import platform        # 🆕 v6.5: Windows 전용 기능 보호 가드
from contextlib import contextmanager

# ── 배경 이미지 base64 로드 (배너 / 메인 / 사이드바) ──
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_BASE_DIR, "config.json")

# ══════════════════════════════════════════════════════════════════
# 🆕 v6.8: config.json 영구 저장/로드 — ODA·AutoCAD 경로 기억
# 앱 껐다 켜도 경로 설정이 유지됩니다.
# 저장 위치: Auto_Web.py와 같은 폴더의 config.json
# ══════════════════════════════════════════════════════════════════
_CONFIG_KEYS = {
    "v65_oda_path":          "",          # ODA Converter 실행파일 경로
    "v65_acad_path":         "",          # AutoCAD 실행파일 경로
    "v65_dwg_version_code":  "ACAD2018",  # DWG 출력 버전
    "v65_use_overkill":      True,
    "v65_use_pedit_join":    True,
    "v65_use_zoom_extents":  True,
    "v65_use_purge":         False,
    "v65_auto_save":         True,
    "v66_output_format":     "dwg_only",  # 출력 형식 기본값
}

def _load_config():
    """config.json에서 설정을 읽어 session_state에 로드. 없으면 기본값 사용."""
    try:
        if os.path.isfile(_CONFIG_PATH):
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, default in _CONFIG_KEYS.items():
                if k not in st.session_state:
                    st.session_state[k] = data.get(k, default)
        else:
            # config.json 없으면 기본값으로 초기화
            for k, default in _CONFIG_KEYS.items():
                if k not in st.session_state:
                    st.session_state[k] = default
    except Exception:
        for k, default in _CONFIG_KEYS.items():
            if k not in st.session_state:
                st.session_state[k] = default

def _save_config():
    """현재 session_state의 설정을 config.json에 저장."""
    try:
        data = {k: st.session_state.get(k, default)
                for k, default in _CONFIG_KEYS.items()}
        with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def _load_image_b64(candidates):
    """후보 파일명들 중 첫 번째로 존재하는 파일을 base64로 반환"""
    for _name in candidates:
        _path = os.path.join(_BASE_DIR, _name)
        if os.path.exists(_path):
            try:
                with open(_path, "rb") as _f:
                    return base64.b64encode(_f.read()).decode(), _name
            except Exception:
                continue
    return "", ""

_HERO_IMG_B64, _HERO_LOADED = _load_image_b64(["banner_bg.png", "배너배경.png", "1.png"])
_MAIN_IMG_B64, _MAIN_LOADED = _load_image_b64(["main_bg.png", "메인배경.png", "2.png"])
_SIDE_IMG_B64, _SIDE_LOADED = _load_image_b64(["sidebar_bg.png", "사이드배경.png", "3.png"])


# ══════════════════════════════════════════════════════════════════════════════
# 🆕 v6.5  DWG 직접 저장 + AutoCAD 자동 연동 모듈
# ══════════════════════════════════════════════════════════════════════════════
# - ODA File Converter (무료) 를 외부 프로세스로 호출하여 DXF → DWG 변환
# - AutoCAD가 설치되어 있으면 SCR 스크립트와 함께 자동 실행 (OVERKILL + PEDIT JOIN + ZOOM E + QSAVE)
# - Windows 전용 기능. 비-Windows 환경에서는 전체 비활성화되어 기존 동작 그대로 유지.
# - 사용자 PC에 외부 프로그램이 설치되어 있지 않은 경우 안전 fallback (조용히 비활성화)
# ══════════════════════════════════════════════════════════════════════════════

_IS_WINDOWS = platform.system().lower().startswith("win")

# ODA File Converter 일반적 설치 경로 후보 (버전별)
_ODA_CANDIDATE_PATHS = [
    # 🆕 v6.7: 27.x 버전 추가
    r"C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe",
    r"C:\Program Files\ODA\ODAFileConverter 27.0.0\ODAFileConverter.exe",
    r"C:\Program Files\ODA\ODAFileConverter 26.5.0\ODAFileConverter.exe",
    r"C:\Program Files\ODA\ODAFileConverter 26.4.0\ODAFileConverter.exe",
    r"C:\Program Files\ODA\ODAFileConverter 25.5.0\ODAFileConverter.exe",
    r"C:\Program Files\ODA\ODAFileConverter 25.4.0\ODAFileConverter.exe",
    r"C:\Program Files\ODA\ODAFileConverter 24.12.0\ODAFileConverter.exe",
    r"C:\Program Files\ODA\ODAFileConverter 24.11.0\ODAFileConverter.exe",
    r"C:\Program Files\ODA\ODAFileConverter 24.10.0\ODAFileConverter.exe",
    r"C:\Program Files\ODA\ODAFileConverter 23.12.0\ODAFileConverter.exe",
    r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe",
    r"C:\Program Files (x86)\ODA\ODAFileConverter\ODAFileConverter.exe",
]

def _scan_oda_dir_dynamic():
    """🆕 v6.7: C:\\Program Files\\ODA\\ 하위 폴더를 버전 무관하게 동적 스캔.
    고정 버전 목록이 없어도 새 버전을 자동 발견한다.
    """
    if not _IS_WINDOWS:
        return ""
    for base in (r"C:\Program Files\ODA", r"C:\Program Files (x86)\ODA"):
        if not os.path.isdir(base):
            continue
        try:
            # ODAFileConverter로 시작하는 폴더를 최신 버전 순으로 정렬
            sub_dirs = sorted(
                [d for d in os.listdir(base) if d.lower().startswith("odafileconverter")],
                reverse=True,  # 버전 내림차순 — 최신 우선
            )
            for sub in sub_dirs:
                exe = os.path.join(base, sub, "ODAFileConverter.exe")
                if os.path.isfile(exe):
                    return exe
        except OSError:
            continue
    return ""

# AutoCAD 실행파일 일반적 경로 후보 (버전별)
_ACAD_CANDIDATE_PATHS = [
    r"C:\Program Files\Autodesk\AutoCAD 2027\acad.exe",   # 🆕 v6.8
    r"C:\Program Files\Autodesk\AutoCAD 2026\acad.exe",
    r"C:\Program Files\Autodesk\AutoCAD 2025\acad.exe",
    r"C:\Program Files\Autodesk\AutoCAD 2024\acad.exe",
    r"C:\Program Files\Autodesk\AutoCAD 2023\acad.exe",
    r"C:\Program Files\Autodesk\AutoCAD 2022\acad.exe",
    r"C:\Program Files\Autodesk\AutoCAD 2021\acad.exe",
    r"C:\Program Files\Autodesk\AutoCAD 2020\acad.exe",
    r"C:\Program Files\Autodesk\AutoCAD LT 2025\acadlt.exe",
    r"C:\Program Files\Autodesk\AutoCAD LT 2024\acadlt.exe",
    r"C:\Program Files\Autodesk\AutoCAD LT 2023\acadlt.exe",
]

def _scan_autocad_dir_dynamic():
    """🆕 v6.8: C:\\Program Files\\Autodesk\\ 하위에서 acad.exe 자동 탐색.
    버전 목록 업데이트 없이 AutoCAD 2028, 2029 등 미래 버전도 자동 발견.
    'AutoCAD 20XX' 형식의 폴더만 선택 (Raster Design 등 비버전 폴더 제외).
    """
    if not _IS_WINDOWS:
        return ""
    base = r"C:\Program Files\Autodesk"
    if not os.path.isdir(base):
        return ""
    try:
        import re
        # "AutoCAD 20XX" 패턴만 선택 (숫자 연도 포함된 폴더)
        sub_dirs = sorted(
            [d for d in os.listdir(base)
             if re.match(r"AutoCAD\s+20\d{2}$", d, re.IGNORECASE)],
            reverse=True,   # 최신 연도 우선
        )
        for sub in sub_dirs:
            exe = os.path.join(base, sub, "acad.exe")
            if os.path.isfile(exe):
                return exe
        # LT 버전도 시도 ("AutoCAD LT 20XX")
        lt_dirs = sorted(
            [d for d in os.listdir(base)
             if re.match(r"AutoCAD\s+LT\s+20\d{2}$", d, re.IGNORECASE)],
            reverse=True,
        )
        for sub in lt_dirs:
            exe = os.path.join(base, sub, "acadlt.exe")
            if os.path.isfile(exe):
                return exe
    except OSError:
        pass
    return ""

# ODA가 지원하는 출력 AutoCAD 버전 코드
_ODA_VERSION_MAP = {
    "AutoCAD 2018 (R2018)": "ACAD2018",
    "AutoCAD 2013 (R2013)": "ACAD2013",
    "AutoCAD 2010 (R2010)": "ACAD2010",
    "AutoCAD 2007 (R2007)": "ACAD2007",
    "AutoCAD 2004 (R2004)": "ACAD2004",
    "AutoCAD 2000 (R2000)": "ACAD2000",
}


def find_oda_converter(user_override_path=""):
    """🆕 v6.5 / 개선 v6.7: ODA File Converter 실행파일을 자동 탐색.

    탐색 순서:
      1. 사용자가 직접 지정한 경로 — 폴더 입력 시 exe 자동 보정
      2. 환경변수 ODA_FILE_CONVERTER
      3. 버전별 고정 후보 경로 목록
      4. C:\\Program Files\\ODA\\ 동적 폴더 스캔 (버전 무관, 최신 우선) ← v6.7 신규
      5. PATH 에 등록되어 있는 경우 (shutil.which)

    Returns:
        실행 파일 경로 (str) 또는 빈 문자열 ("" — 미발견)
    """
    if not _IS_WINDOWS:
        return ""

    # 1) 사용자 지정 경로 — 폴더를 입력해도 exe 자동 보정 (v6.7)
    if user_override_path:
        p = user_override_path.strip().strip('"')
        if os.path.isfile(p):
            return p
        # 폴더 경로를 입력한 경우 exe를 자동으로 붙여서 재시도
        exe_guess = os.path.join(p, "ODAFileConverter.exe")
        if os.path.isfile(exe_guess):
            return exe_guess

    # 2) 환경변수
    env_path = os.environ.get("ODA_FILE_CONVERTER", "").strip().strip('"')
    if env_path and os.path.isfile(env_path):
        return env_path

    # 3) 고정 후보 경로
    for p in _ODA_CANDIDATE_PATHS:
        if os.path.isfile(p):
            return p

    # 4) 🆕 v6.7: 동적 폴더 스캔 (버전 목록 업데이트 없이 미래 버전도 자동 발견)
    dynamic = _scan_oda_dir_dynamic()
    if dynamic:
        return dynamic

    # 5) PATH 검색
    which = shutil.which("ODAFileConverter") or shutil.which("ODAFileConverter.exe")
    if which:
        return which

    return ""


def find_autocad_exe(user_override_path=""):
    """🆕 v6.5 / 개선 v6.8: AutoCAD 실행파일 자동 탐색.

    탐색 순서:
      1. 사용자 지정 경로 — 폴더 입력 시 acad.exe 자동 보정 (v6.8)
      2. 환경변수 AUTOCAD_EXE
      3. 버전별 고정 후보 경로
      4. C:\\Program Files\\Autodesk\\ 동적 스캔 (버전 무관, 최신 우선) ← v6.8 신규
      5. PATH 검색 (shutil.which)

    Returns:
        실행 파일 경로 (str) 또는 빈 문자열
    """
    if not _IS_WINDOWS:
        return ""

    # 1) 사용자 지정 경로 — 폴더 입력 시 acad.exe 자동 보정
    if user_override_path:
        p = user_override_path.strip().strip('"')
        if os.path.isfile(p):
            return p
        # 폴더를 입력한 경우: acad.exe 자동으로 붙여 재시도
        for exe_name in ("acad.exe", "acadlt.exe"):
            exe_guess = os.path.join(p, exe_name)
            if os.path.isfile(exe_guess):
                return exe_guess

    # 2) 환경변수
    env_path = os.environ.get("AUTOCAD_EXE", "").strip().strip('"')
    if env_path and os.path.isfile(env_path):
        return env_path

    # 3) 고정 후보 경로
    for p in _ACAD_CANDIDATE_PATHS:
        if os.path.isfile(p):
            return p

    # 4) 동적 폴더 스캔 (v6.8 — 버전 무관 자동 발견)
    dynamic = _scan_autocad_dir_dynamic()
    if dynamic:
        return dynamic

    # 5) PATH 검색
    which = shutil.which("acad") or shutil.which("acad.exe")
    if which:
        return which

    return ""


def convert_dxf_to_dwg_via_oda(dxf_bytes, dwg_filename_stem,
                               oda_exe_path="",
                               target_version="ACAD2018",
                               timeout_sec=60):
    """🆕 v6.5: DXF 바이트 → DWG 바이트 변환 (ODA File Converter 호출).

    ODA File Converter CLI 호환 인자:
        ODAFileConverter.exe <inDir> <outDir> <outVer> <outFormat> <recurse> <audit> [<filter>]

    Args:
        dxf_bytes        : 변환할 DXF의 바이트 데이터
        dwg_filename_stem: 출력 파일 이름(확장자 제외). 예: "도면01"
        oda_exe_path     : ODA Converter 실행 파일 경로 ("" 이면 자동 탐색)
        target_version   : "ACAD2018" / "ACAD2013" / "ACAD2010" 등
        timeout_sec      : 외부 프로세스 최대 대기 시간 (초)

    Returns:
        (dwg_bytes 또는 None, message_str)
    """
    if not _IS_WINDOWS:
        return None, "❌ DWG 변환은 Windows 환경에서만 지원됩니다."

    oda = oda_exe_path or find_oda_converter()
    if not oda:
        return None, (
            "❌ ODA File Converter를 찾을 수 없습니다.\n"
            "    👉 https://www.opendesign.com/guestfiles/oda_file_converter 에서 무료 설치 후\n"
            "       사이드바 '🔧 DWG/AutoCAD 설정'에서 경로를 지정해주세요."
        )

    # 1) 한글 경로 회피용 임시 작업 디렉터리 생성 (ASCII-only)
    #    ODA File Converter는 한글 경로에서 종종 실패하므로 tempdir 안에서 작업
    with tempfile.TemporaryDirectory(prefix="dwg_") as work_root:
        in_dir  = os.path.join(work_root, "in")
        out_dir = os.path.join(work_root, "out")
        os.makedirs(in_dir,  exist_ok=True)
        os.makedirs(out_dir, exist_ok=True)

        # 입력 DXF 파일명을 ASCII-only로 강제 (한글이 들어가면 ODA가 깨질 수 있음)
        safe_stem = "input_dxf_" + uuid.uuid4().hex[:8]
        in_dxf_path = os.path.join(in_dir, safe_stem + ".dxf")
        try:
            with open(in_dxf_path, "wb") as f:
                f.write(dxf_bytes)
        except Exception as e:
            return None, f"❌ 임시 DXF 파일 쓰기 실패: {e}"

        # 2) ODA File Converter CLI 호출
        #    인자: inDir outDir outVer outFormat recurse audit
        #    outFormat: 0=DWG, 1=DXF
        cmd = [
            oda,
            in_dir,
            out_dir,
            str(target_version),
            "DWG",      # 출력 형식: DWG
            "0",        # recurse: 하위 폴더 검색 안함
            "1",        # audit: 자동 검사/복구
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=int(timeout_sec),
                check=False,
            )
        except subprocess.TimeoutExpired:
            return None, f"❌ ODA 변환 시간초과 ({timeout_sec}초). 더 큰 파일은 timeout 늘려주세요."
        except FileNotFoundError:
            return None, f"❌ ODA 실행 실패: 경로를 다시 확인해주세요. ({oda})"
        except Exception as e:
            return None, f"❌ ODA 실행 중 예외 발생: {e}"

        # 3) 변환 결과 확인
        out_dwg_path = os.path.join(out_dir, safe_stem + ".dwg")
        if not os.path.isfile(out_dwg_path):
            # ODA는 stdout/stderr가 비어 있어도 실패하는 경우가 있어 디렉터리 점검
            files_in_out = os.listdir(out_dir) if os.path.isdir(out_dir) else []
            err_msg = (
                f"❌ DWG 변환 실패: 출력 파일이 생성되지 않았습니다.\n"
                f"    return code: {result.returncode}\n"
                f"    out dir: {files_in_out}"
            )
            return None, err_msg

        try:
            with open(out_dwg_path, "rb") as f:
                dwg_bytes = f.read()
        except Exception as e:
            return None, f"❌ DWG 파일 읽기 실패: {e}"

        return dwg_bytes, f"✅ DWG 변환 성공 ({target_version}, {len(dwg_bytes):,} bytes)"


def build_autocad_cleanup_scr(use_overkill=True, use_pedit_join=True,
                              use_zoom_extents=True, use_purge=False, auto_save=True):
    """🆕 v6.5: AutoCAD 자동 정리용 SCR 스크립트 생성.

    SCR(Script) = AutoCAD 명령어 줄을 한 줄씩 자동 실행시키는 텍스트 파일.

    Args:
        use_overkill    : OVERKILL 명령 실행 (중복선 자동 제거) — AutoCAD 풀버전만
        use_pedit_join  : PEDIT 자동 JOIN (분리된 polyline 자동 연결)
        use_zoom_extents: ZOOM EXTENTS 자동 실행 (도면 전체 보기)
        use_purge       : PURGE All (사용하지 않는 객체 자동 제거)
        auto_save       : QSAVE 자동 저장

    Returns:
        SCR 스크립트 내용 (str)
    """
    lines = []
    # 화면 정리
    lines.append("_.FILEDIA 0")    # 파일 대화상자 비활성화 (스크립트 안정성)
    lines.append("_.CMDDIA 0")     # 명령 대화상자 비활성화

    if use_zoom_extents:
        lines.append("_.ZOOM _E")  # Extents (도면 전체 보기)

    if use_overkill:
        # OVERKILL: 중복/겹친 선 자동 제거 — AutoCAD 풀버전 전용
        # _.OVERKILL ALL <엔터> <엔터> = 모든 객체 선택 → 옵션 그대로 → 실행
        lines.append("_.-OVERKILL")  # 하이픈은 dialog 없이 명령창 모드
        lines.append("ALL")
        lines.append("")             # 선택 완료
        lines.append("")             # 옵션 기본값 그대로

    if use_pedit_join:
        # PEDIT Multiple Join: 분리된 라인/폴리라인을 자동으로 polyline 으로 결합
        lines.append("_.-PEDIT")
        lines.append("_M")           # Multiple
        lines.append("ALL")
        lines.append("")             # 선택 완료
        lines.append("_Y")           # 객체를 polyline 으로 변환할지: Yes
        lines.append("_J")           # Join
        lines.append("")             # 옵션 기본값
        lines.append("")             # 종료

    if use_purge:
        lines.append("_.-PURGE")
        lines.append("_A")           # All
        lines.append("*")            # 전체 객체
        lines.append("_N")           # 확인 안 함

    if auto_save:
        lines.append("_.QSAVE")      # 빠른 저장

    # 다시 dialog 복구
    lines.append("_.FILEDIA 1")
    lines.append("_.CMDDIA 1")

    return "\n".join(lines) + "\n"


def open_in_autocad(dxf_or_dwg_path, run_cleanup=True,
                    use_overkill=True, use_pedit_join=True,
                    use_zoom_extents=True, use_purge=False, auto_save=True,
                    acad_exe_path=""):
    """🆕 v6.5: 파일을 AutoCAD로 열고, 옵션에 따라 자동 정리 스크립트 실행.

    Args:
        dxf_or_dwg_path: 열고자 하는 DXF/DWG 절대경로
        run_cleanup    : True면 SCR 자동 실행
        나머지         : SCR 옵션 (build_autocad_cleanup_scr 참조)
        acad_exe_path  : AutoCAD 실행파일 경로 ("" 이면 자동 탐색)

    Returns:
        (성공여부 bool, 메시지 str)
    """
    if not _IS_WINDOWS:
        return False, "❌ AutoCAD 자동 실행은 Windows 환경에서만 지원됩니다."

    if not os.path.isfile(dxf_or_dwg_path):
        return False, f"❌ 파일을 찾을 수 없습니다: {dxf_or_dwg_path}"

    acad = acad_exe_path or find_autocad_exe()
    if not acad:
        return False, (
            "❌ AutoCAD 실행파일을 찾을 수 없습니다.\n"
            "    👉 AutoCAD가 설치되지 않았거나, 사이드바 '🔧 DWG/AutoCAD 설정'에서\n"
            "       acad.exe 경로를 직접 지정해주세요."
        )

    try:
        if run_cleanup:
            # SCR 스크립트를 파일과 같은 폴더에 임시로 저장 (스크립트 실행 후 자동 삭제는 AutoCAD가 알아서 함)
            scr_content = build_autocad_cleanup_scr(
                use_overkill=use_overkill,
                use_pedit_join=use_pedit_join,
                use_zoom_extents=use_zoom_extents,
                use_purge=use_purge,
                auto_save=auto_save,
            )
            scr_path = os.path.join(
                os.path.dirname(os.path.abspath(dxf_or_dwg_path)),
                f"_auto_cleanup_{uuid.uuid4().hex[:6]}.scr"
            )
            with open(scr_path, "w", encoding="utf-8") as f:
                f.write(scr_content)
            # AutoCAD 실행: 파일 + SCR
            # /b 스위치: 배치 스크립트 자동 실행
            subprocess.Popen([acad, "/b", scr_path, dxf_or_dwg_path])
            return True, f"✅ AutoCAD 실행됨 (자동 정리 SCR 함께 실행)\n   📄 {os.path.basename(dxf_or_dwg_path)}"
        else:
            # 그냥 파일만 열기
            subprocess.Popen([acad, dxf_or_dwg_path])
            return True, f"✅ AutoCAD 실행됨\n   📄 {os.path.basename(dxf_or_dwg_path)}"
    except FileNotFoundError:
        return False, f"❌ AutoCAD 실행 실패: 경로 확인 필요. ({acad})"
    except Exception as e:
        return False, f"❌ AutoCAD 실행 중 예외: {e}"

# ══════════════════════════════════════════════════════════════════════════════
# v6.5 DWG/AutoCAD 모듈 끝
# ══════════════════════════════════════════════════════════════════════════════

import cv2
import ezdxf
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import easyocr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skimage.morphology import skeletonize
from scipy.ndimage import uniform_filter1d
from scipy.spatial import KDTree

# DBSCAN 패턴 인식용
try:
    from sklearn.cluster import DBSCAN
    _DBSCAN_AVAILABLE = True
except ImportError:
    _DBSCAN_AVAILABLE = False

# Plotly 줌/패닝 미리보기용
try:
    import plotly.graph_objects as go
    _PLOTLY_AVAILABLE = True
except ImportError:
    _PLOTLY_AVAILABLE = False

# PIL (matplotlib → plotly 이미지 변환용)
try:
    from PIL import Image as _PILImage
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

# streamlit-drawable-canvas (Crop 도구용, 선택사항)
try:
    from streamlit_drawable_canvas import st_canvas
    _CANVAS_AVAILABLE = True
except ImportError:
    _CANVAS_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════
#  🆕 v6.3 신규: AI Super-Resolution (FSRCNN_x2.pb)
# ══════════════════════════════════════════════════════════════════
# OpenCV dnn_superres 모듈 가용성 체크 (opencv-contrib-python 필요)
_SR_MODEL_PATH = os.path.join(_BASE_DIR, "FSRCNN_x2.pb")
_SR_AVAILABLE = False
_SR_MODEL_EXISTS = os.path.exists(_SR_MODEL_PATH)
try:
    if hasattr(cv2, 'dnn_superres') and _SR_MODEL_EXISTS:
        _SR_AVAILABLE = True
except Exception:
    _SR_AVAILABLE = False

# SR 모델 로드는 처리 직전에 lazy 방식으로 (앱 시작 시간 지연 방지)
_SR_MODEL_CACHE = {"model": None, "loaded": False, "error": None}

def _load_sr_model():
    """FSRCNN_x2.pb 모델을 한 번만 로드하고 캐시.

    Returns
    -------
    cv2.dnn_superres.DnnSuperResImpl | None
    """
    if not _SR_AVAILABLE:
        return None
    if _SR_MODEL_CACHE["loaded"]:
        return _SR_MODEL_CACHE["model"]
    try:
        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        sr.readModel(_SR_MODEL_PATH)
        sr.setModel("fsrcnn", 2)  # 모델명, 배율
        _SR_MODEL_CACHE["model"] = sr
        _SR_MODEL_CACHE["loaded"] = True
        return sr
    except Exception as e:
        _SR_MODEL_CACHE["error"] = str(e)
        _SR_MODEL_CACHE["loaded"] = True
        _SR_MODEL_CACHE["model"] = None
        return None


def apply_super_resolution_auto(img_color, threshold_px=1500):
    """저해상도일 때만 자동으로 FSRCNN x2 업스케일 적용.

    Parameters
    ----------
    img_color : np.ndarray (BGR)
        원본 컬러 이미지
    threshold_px : int
        이 픽셀 미만(긴 변 기준)일 때만 업스케일 적용 (기본 1500)

    Returns
    -------
    (img_out, applied)
        img_out : np.ndarray (BGR)
        applied : bool — Super-Resolution이 실제 적용됐는지 여부
    """
    if img_color is None:
        return img_color, False
    h, w = img_color.shape[:2]
    long_side = max(h, w)
    # 이미 충분히 큰 이미지면 통과
    if long_side >= threshold_px:
        return img_color, False
    sr = _load_sr_model()
    if sr is None:
        return img_color, False
    try:
        img_up = sr.upsample(img_color)
        return img_up, True
    except Exception:
        return img_color, False


# ══════════════════════════════════════════════════════════════════
#  🆕 v6.3 신규: 차이 비교 뷰어 Plotly 인터랙티브 (줌/패닝)
# ══════════════════════════════════════════════════════════════════
def render_diff_overlay_plotly(img_bytes, dxf_bytes,
                                bg_color="#ffffff",
                                missing_color="#dc2626",
                                extra_color="#06b6d4",
                                common_color="#9ca3af",
                                line_thickness=2,
                                tolerance=3):
    """render_diff_overlay_preview의 Plotly 버전 — 마우스 줌/패닝/툴팁 지원.

    내부 픽셀 합성은 기존 함수와 동일하며 결과 RGB array를 Plotly에 표시.

    Returns
    -------
    (plotly.graph_objects.Figure | None, dict | None)
        figure, stats
    """
    if not _PLOTLY_AVAILABLE:
        return None, None
    try:
        arr = np.asarray(bytearray(img_bytes), dtype=np.uint8)
        img_cv = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img_cv is None:
            return None, None
    except Exception:
        return None, None

    h_img, w_img = img_cv.shape[:2]
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # 1) 원본 이진화
    blurred = cv2.bilateralFilter(gray, 9, 75, 75)
    _, orig_bin = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 2) DXF 렌더링
    dxf_bin = np.zeros((h_img, w_img), dtype=np.uint8)
    try:
        doc_o = ezdxf.read(io.StringIO(dxf_bytes.decode("utf-8", errors="replace")))
        msp_o = doc_o.modelspace()
        SCALE_GUESS = 0.1
        def dxf_to_px(x, y):
            px = int(round(x / SCALE_GUESS))
            py = int(round(h_img - y / SCALE_GUESS))
            return px, py

        for ent in msp_o:
            try:
                t = ent.dxftype()
                if t == "LINE":
                    p1 = dxf_to_px(ent.dxf.start.x, ent.dxf.start.y)
                    p2 = dxf_to_px(ent.dxf.end.x,   ent.dxf.end.y)
                    cv2.line(dxf_bin, p1, p2, 255, line_thickness)
                elif t == "LWPOLYLINE":
                    pts_d = list(ent.get_points())
                    if len(pts_d) >= 2:
                        pts_px = np.array([dxf_to_px(p[0], p[1]) for p in pts_d], dtype=np.int32)
                        cv2.polylines(dxf_bin, [pts_px], False, 255, line_thickness)
                elif t == "CIRCLE":
                    cx, cy = dxf_to_px(ent.dxf.center.x, ent.dxf.center.y)
                    r = int(round(ent.dxf.radius / SCALE_GUESS))
                    if r > 0:
                        cv2.circle(dxf_bin, (cx, cy), r, 255, line_thickness)
                elif t == "ARC":
                    cx, cy = dxf_to_px(ent.dxf.center.x, ent.dxf.center.y)
                    r = int(round(ent.dxf.radius / SCALE_GUESS))
                    a1 = float(ent.dxf.start_angle)
                    a2 = float(ent.dxf.end_angle)
                    if a2 < a1: a2 += 360.0
                    cv2.ellipse(dxf_bin, (cx, cy), (r, r), 0, -a2, -a1, 255, line_thickness)
            except Exception:
                continue
    except Exception:
        return None, None

    # 3) Dilate로 매칭 허용 거리
    k = max(1, int(tolerance))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    orig_dil = cv2.dilate(orig_bin, kernel, iterations=1)
    dxf_dil  = cv2.dilate(dxf_bin,  kernel, iterations=1)

    common_mask  = (orig_bin > 0) & (dxf_dil > 0)
    missing_mask = (orig_bin > 0) & (dxf_dil == 0)
    extra_mask   = (dxf_bin  > 0) & (orig_dil == 0)

    def _hex_to_rgb(hx):
        hx = hx.lstrip("#")
        return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))
    bg_rgb      = _hex_to_rgb(bg_color)
    missing_rgb = _hex_to_rgb(missing_color)
    extra_rgb   = _hex_to_rgb(extra_color)
    common_rgb  = _hex_to_rgb(common_color)

    out = np.full((h_img, w_img, 3), bg_rgb, dtype=np.uint8)
    out[common_mask]  = common_rgb
    out[extra_mask]   = extra_rgb
    out[missing_mask] = missing_rgb

    # 통계
    n_orig    = int(np.count_nonzero(orig_bin))
    n_missing = int(np.count_nonzero(missing_mask))
    n_extra   = int(np.count_nonzero(extra_mask))
    n_common  = int(np.count_nonzero(common_mask))
    coverage = (n_common / n_orig * 100.0) if n_orig > 0 else 0.0
    miss_pct = (n_missing / n_orig * 100.0) if n_orig > 0 else 0.0

    # Plotly Figure 생성
    fig = go.Figure()
    fig.add_trace(go.Image(z=out, hoverinfo="skip"))
    fig.update_layout(
        xaxis=dict(visible=False, range=[0, w_img], constrain='domain'),
        yaxis=dict(visible=False, range=[h_img, 0], scaleanchor='x', scaleratio=1, constrain='domain'),
        margin=dict(l=0, r=0, t=4, b=4),
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        dragmode='pan',
        height=520,
    )
    # 줌·홈·자동스케일 버튼만 노출
    fig.update_layout(
        modebar=dict(
            orientation='v',
            bgcolor='rgba(255,255,255,0.7)',
            color='#1a3a5c',
            activecolor='#0078d4',
        )
    )

    stats = {
        "coverage_pct": float(coverage),
        "missing_pct": float(miss_pct),
        "n_orig": n_orig,
        "n_missing": n_missing,
        "n_extra": n_extra,
        "n_common": n_common,
    }
    return fig, stats


# ══════════════════════════════════════════
#  🌐  페이지 설정
# ══════════════════════════════════════════

# ── 미리보기 배경 색상 매핑 ──
PREVIEW_BG_OPTIONS = {
    "🌑 CAD Dark":    {"bg": "#1a1d2e", "line": "#e0e4ef", "label": "AutoCAD 기본"},
    "⬜ White Paper":  {"bg": "#ffffff", "line": "#1a2040", "label": "출력·제출 검수"},
    "🔵 Blueprint":    {"bg": "#0d2b4e", "line": "#7ec8ff", "label": "청사진 스타일"},
}

st.set_page_config(
    page_title="DXF 변환 시스템",
    page_icon="📐",
    layout="wide"
)

# ══════════════════════════════════════════
#  🎨  CSS (Apple 테마 고정 + 토글 CSS fix v3.2 + v4.0 추가)
# ══════════════════════════════════════════

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Pretendard:wght@300;400;500;600;700&display=swap');

#MainMenu {{ visibility: hidden !important; }}
header[data-testid="stHeader"] {{ display: none !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}
[data-testid="stStatusWidget"] {{ display: none !important; }}
footer {{ display: none !important; }}
.stDeployButton {{ display: none !important; }}

html, body, [class*="css"] {{ font-family: 'IBM Plex Sans', 'Pretendard', sans-serif !important; }}

/* ── 메인 배경 기본값 ── */
.stApp {{
    background-color: #edf0f4 !important;
    min-height: 100vh;
}}
.block-container {{ padding-top: 3rem !important; padding-bottom: 0.5rem !important; }}

/* ── 메인 영역 라디오 버튼 텍스트 색상 (배경 선택 등) ── */
[data-testid="stMain"] [data-testid="stRadio"] span,
[data-testid="stMain"] [data-testid="stRadio"] p,
[data-testid="stMain"] [data-testid="stRadio"] label,
[data-testid="stMain"] [data-testid="stRadio"] [data-testid="stWidgetLabel"] p,
[data-testid="stMain"] [data-testid="stRadio"] > div > label > div > p {{
    color: #1a3a5c !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}}
[data-testid="stMain"] [data-testid="stRadio"] {{
    background: transparent !important;
}}
[data-testid="stMain"] [data-baseweb="radio"] [role="radio"] {{
    border-color: #0078d4 !important;
}}
[data-testid="stMain"] [data-baseweb="radio"] [role="radio"][aria-checked="true"] {{
    background-color: #0078d4 !important;
}}

/* ══════════════════════════════════════════════════════════
   사이드바 토글 버튼 (접힌 상태)
   ══════════════════════════════════════════════════════════ */
[data-testid="collapsedControl"] {{
    background: #1a3a5c !important;
    border-radius: 0 10px 10px 0 !important;
    width: 32px !important; height: 80px !important;
    top: 50% !important; transform: translateY(-50%) !important;
    box-shadow: 3px 0 16px rgba(26,58,92,0.35) !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
    border: none !important; transition: all 0.2s ease !important;
    position: fixed !important; left: 0 !important; z-index: 9999 !important;
    cursor: pointer !important; opacity: 1 !important; visibility: visible !important;
}}
[data-testid="collapsedControl"]:hover {{
    background: #0078d4 !important;
    box-shadow: 5px 0 20px rgba(0,120,212,0.4) !important;
}}
[data-testid="collapsedControl"] svg {{
    color: #ffffff !important; width: 16px !important; height: 16px !important;
}}

/* ══════════════════════════════════════════════════════════
   사이드바 폭 강제 고정
   ══════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    width: 420px !important;
    min-width: 420px !important;
    max-width: 420px !important;
    flex: 0 0 420px !important;
    flex-shrink: 0 !important;
    flex-grow: 0 !important;
    padding-top: 0 !important;
    border-right: 1px solid #dde3ec !important;
    box-shadow: 2px 0 10px rgba(0,0,0,0.06) !important;
}}
[data-testid="stSidebar"] {{
    width: 420px !important;
    min-width: 420px !important;
    max-width: 420px !important;
}}
section[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div {{
    width: 420px !important;
    min-width: 420px !important;
    max-width: 420px !important;
    overflow-x: hidden !important;
}}
[data-testid="stSidebarContent"] {{
    width: 420px !important;
    min-width: 420px !important;
    padding: 0 !important;
}}

/* ══════════════════════════════════════════════════════════
   🆕 v6.3 사이드바 레이아웃 최적화 (DOM 실측값 기반)
   - 사이드바 right: 420px, label left: 27px → 가용 너비 393px
   - 토글/슬라이더/expander 폭 통일, 우측 잘림 방지
   ══════════════════════════════════════════════════════════ */
/* 메인 컨테이너 좌우 패딩 정밀 조정 (좌측 14px, 우측 14px 유지하면서 393px 가용 폭 확보) */
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
    padding-left: 14px !important;
    padding-right: 13px !important;
    padding-top: 8px !important;
    padding-bottom: 16px !important;
    box-sizing: border-box !important;
}}
/* expander 폭을 사이드바 가용 폭에 맞춤 (393px) */
[data-testid="stSidebar"] [data-testid="stExpander"] {{
    width: 100% !important;
    max-width: 393px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    box-sizing: border-box !important;
    border-radius: 6px !important;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] > details > summary {{
    padding: 6px 10px !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] > details[open] > div {{
    padding: 6px 10px 8px 10px !important;
}}
/* 슬라이더 라벨 폰트 크기 통일 */
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] [data-testid="stSlider"] label {{
    font-size: 0.74rem !important;
    margin-bottom: 2px !important;
    line-height: 1.3 !important;
}}
/* 슬라이더 트랙 폭 명시적 (jagged 방지) */
[data-testid="stSidebar"] [data-testid="stSlider"] > div {{
    padding-left: 2px !important;
    padding-right: 2px !important;
}}
/* 토글 label 우측 여백 통일 — JS 동적 width 적용 전 기본값 */
[data-testid="stSidebar"] label[data-baseweb="checkbox"] {{
    padding-right: 2px !important;
    margin-bottom: 4px !important;
}}
/* selectbox / radio 폭 통일 */
[data-testid="stSidebar"] [data-baseweb="select"],
[data-testid="stSidebar"] [data-testid="stRadio"] > div {{
    width: 100% !important;
    max-width: 393px !important;
}}
/* file_uploader 폭 통일 */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {{
    width: 100% !important;
    max-width: 393px !important;
}}
[data-testid="stSidebar"] [data-testid="stFileUploader"] section {{
    padding: 8px 10px !important;
}}
/* button 폭 통일 */
[data-testid="stSidebar"] [data-testid="stButton"] > button {{
    width: 100% !important;
    max-width: 393px !important;
    box-sizing: border-box !important;
}}
/* columns 내 위젯도 가로 overflow 방지 */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {{
    gap: 6px !important;
    flex-wrap: nowrap !important;
}}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
    min-width: 0 !important;
    overflow: hidden !important;
}}
/* 섹션 헤더 간격 컴팩트화 (정보 밀도 향상) */
[data-testid="stSidebar"] .sb-group-header {{
    margin-top: 6px !important;
    margin-bottom: 4px !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.02em !important;
}}
/* hr 두께 절반으로 (시각적 노이즈 감소) */
[data-testid="stSidebar"] hr {{
    margin: 6px 0 !important;
    border-top: 1px solid #e1e7ef !important;
}}

/* ══════════════════════════════════════════════════════════
   사이드바 배경 강제 적용 (다크 테마 override)
   ══════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] > div > div,
[data-testid="stSidebarContent"],
[data-testid="stSidebarContent"] > div {{
    background: #f4f6f9 !important;
    background-color: #f4f6f9 !important;
}}

/* ══════════════════════════════════════════════════════════
   사이드바 내 모든 텍스트 색상 (다크 테마 override)
   ══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label,
[data-testid="stSidebar"] .stCheckbox label,
[data-testid="stSidebar"] .stSlider label p,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown span,
[data-testid="stSidebar"] .stMarkdown b,
[data-testid="stSidebar"] .stMarkdown strong,
[data-testid="stSidebar"] .stInfo p,
[data-testid="stSidebar"] [data-testid="stText"],
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span:not([data-testid]),
[data-testid="stSidebar"] label {{
    color: #1a3a5c !important;
    font-family: 'IBM Plex Sans', 'Pretendard', sans-serif !important;
}}
[data-testid="stSidebar"] .stSlider div[data-testid="stThumbValue"] {{
    color: #1a3a5c !important;
    background: #ffffff !important;
    border: 1px solid #c8d4e0 !important;
    font-size: 0.78rem !important;
    font-family: 'JetBrains Mono', monospace !important;
}}

/* ══════════════════════════════════════════════════════════
   사이드바 selectbox (도면 종류)
   ══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {{
    background: #ffffff !important;
    border: 1.5px solid #c8d4e0 !important;
    border-radius: 8px !important;
    color: #1a3a5c !important;
    min-height: 44px !important;
    font-size: 0.97rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    transition: border-color 0.15s ease !important;
}}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div > div {{
    color: #1a3a5c !important;
    font-size: 0.97rem !important;
    font-weight: 600 !important;
}}
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {{
    color: #0078d4 !important; fill: #0078d4 !important;
}}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div:hover {{
    border-color: #0078d4 !important;
    background: #f0f6ff !important;
}}

/* ══════════════════════════════════════════════════════════
   토글 스위치 — :not(#_) 고특이도 방식 (v3.2 final fix)
   ══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] [data-testid="stCheckbox"],
[data-testid="stSidebar"] [data-testid="stCheckbox"] > label,
[data-testid="stSidebar"] [data-baseweb="checkbox"] {{
    background: transparent !important;
    background-color: transparent !important;
}}
[data-testid="stSidebar"] [data-testid="stCheckbox"] {{
    padding: 4px 0 !important;
}}
[data-testid="stSidebar"] [data-testid="stCheckbox"] > label {{
    display: flex !important;
    flex-direction: row-reverse !important;
    align-items: center !important;
    justify-content: space-between !important;
    width: 100% !important;
    gap: 8px !important;
    border: none !important;
    padding: 2px 0 !important;
    cursor: pointer !important;
    min-height: 30px !important;
    background: transparent !important;
    box-sizing: border-box !important;
}}
[data-testid="stSidebar"] [data-testid="stCheckbox"] > label:hover,
[data-testid="stSidebar"] [data-testid="stCheckbox"] > label:focus-within {{
    background: transparent !important;
    outline: none !important;
    box-shadow: none !important;
}}
[data-testid="stSidebar"] [data-testid="stCheckbox"] p,
[data-testid="stSidebar"] [data-testid="stCheckbox"] label p {{
    color: #1a3a5c !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    background: transparent !important;
    margin: 0 !important;
}}

body [data-testid="stSidebar"] [role="checkbox"]:not(#_):not(#_),
body [data-testid="stSidebar"] [aria-roledescription="toggle"]:not(#_):not(#_) {{
    width: 44px !important;
    min-width: 44px !important;
    height: 24px !important;
    border-radius: 12px !important;
    background: #475569 !important;
    background-color: #475569 !important;
    border: 2px solid #334155 !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.4) !important;
    transition: background 0.2s ease, border-color 0.2s ease !important;
    flex-shrink: 0 !important;
    position: relative !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    overflow: hidden !important;
    clip-path: inset(0 round 12px) !important;
    box-sizing: border-box !important;
}}
body [data-testid="stSidebar"] [role="checkbox"][aria-checked="true"]:not(#_):not(#_),
body [data-testid="stSidebar"] [aria-roledescription="toggle"][aria-checked="true"]:not(#_):not(#_) {{
    background: #0066cc !important;
    background-color: #0066cc !important;
    border: 2px solid #0052a3 !important;
    box-shadow: 0 0 0 2px rgba(0,102,204,0.2) !important;
    overflow: hidden !important;
    clip-path: inset(0 round 12px) !important;
}}
body [data-testid="stSidebar"] [role="checkbox"] > div:not(#_),
body [data-testid="stSidebar"] [aria-roledescription="toggle"] > div:not(#_) {{
    width: 18px !important;
    height: 18px !important;
    border-radius: 50% !important;
    background: #ffffff !important;
    background-color: #ffffff !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.5) !important;
    flex-shrink: 0 !important;
}}

/* ══════════════════════════════════════════════════════════
   사이드바 — 세로 간격
   ══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: 0.55rem !important; }}
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stVerticalBlock"] {{ gap: 0.45rem !important; }}
[data-testid="stSidebar"] [data-testid="stSlider"] {{ margin-top: 2px !important; margin-bottom: 0.3rem !important; padding-top: 0 !important; }}
[data-testid="stSidebar"] [data-testid="stSlider"] label {{ margin-bottom: 2px !important; padding-bottom: 0 !important; }}
[data-testid="stSidebar"] [data-testid="stSlider"] > div {{ padding-top: 0 !important; }}
[data-testid="stSidebar"] [data-testid="stMarkdown"] {{ margin: 0 !important; padding: 0 !important; }}
[data-testid="stSidebar"] [data-testid="stExpander"] {{ margin-top: 5px !important; margin-bottom: 5px !important; }}
[data-testid="stSidebar"] [data-testid="stExpander"] > details > div {{ padding-top: 10px !important; padding-bottom: 10px !important; }}
[data-testid="stSidebar"] hr {{ margin: 8px 0 !important; }}
[data-testid="stSidebar"] [data-testid="stCheckbox"] {{ padding: 5px 0 !important; }}

/* ══════════════════════════════════════════════════════════
   섹션 라벨 강화
   ══════════════════════════════════════════════════════════ */
.sb-section-label {{
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #1a3a5c !important;
    margin: 10px 0 8px 0 !important;
    padding: 6px 0 6px 14px !important;
    letter-spacing: -0.01em !important;
    text-transform: none !important;
    border-left: 5px solid #0078d4 !important;
    background: linear-gradient(to right, rgba(0,120,212,0.1), transparent 50%) !important;
    border-radius: 0 4px 4px 0 !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    line-height: 1.2 !important;
}}
.sb-num {{
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 20px !important;
    height: 20px !important;
    border-radius: 50% !important;
    background: #0078d4 !important;
    color: #ffffff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    line-height: 1 !important;
    flex-shrink: 0 !important;
    box-shadow: 0 1px 3px rgba(0,120,212,0.3) !important;
}}
.sb-group-header {{
    font-size: 0.86rem !important;
    font-weight: 700 !important;
    color: #1a3a5c !important;
    margin: 8px 0 4px 0 !important;
    padding: 3px 0 4px 8px !important;
    border-bottom: 1.5px solid #e2e8f0 !important;
    border-left: 3px solid #6b8299 !important;
    display: flex !important;
    align-items: center !important;
    gap: 5px !important;
    letter-spacing: -0.005em !important;
    background: linear-gradient(to right, rgba(107,130,153,0.06), transparent 60%) !important;
}}
.sb-group-header.accent {{
    color: #0052a3 !important;
    border-left-color: #0078d4 !important;
    border-bottom-color: #cde0f5 !important;
    background: linear-gradient(to right, rgba(0,120,212,0.1), transparent 60%) !important;
}}

/* ══════════════════════════════════════════════════════════
   프리셋 버튼
   ══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] [data-testid="stButton"] > button {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 10px 8px !important;
    line-height: 1.2 !important;
    min-height: 56px !important;
    white-space: normal !important;
}}
[data-testid="stSidebar"] [data-testid="stButton"] > button > div,
[data-testid="stSidebar"] [data-testid="stButton"] > button p {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.25 !important;
    font-size: 0.83rem !important;
    font-weight: 600 !important;
}}

/* ══════════════════════════════════════════════════════════
   사이드바 슬라이더 (CAD 블루)
   ══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] > div > div > div {{
    background: #0078d4 !important;
}}
[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {{
    background: #0078d4 !important;
    border: 2px solid #ffffff !important;
    box-shadow: 0 1px 4px rgba(0,120,212,0.35) !important;
}}

/* ══════════════════════════════════════════════════════════
   사이드바 expander
   ══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] [data-testid="stExpander"],
[data-testid="stSidebar"] [data-testid="stExpander"] > details,
[data-testid="stSidebar"] [data-testid="stExpander"] > details > div {{
    background: transparent !important;
    background-color: transparent !important;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] summary {{
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1px solid #d0d8e4 !important;
    border-radius: 7px !important;
    padding-top: 9px !important;
    padding-bottom: 9px !important;
    transition: all 0.15s ease !important;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {{
    background: #e8f0f9 !important;
    border-color: #0078d4 !important;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] summary p,
[data-testid="stSidebar"] [data-testid="stExpander"] summary span,
[data-testid="stSidebar"] [data-testid="stExpander"] summary svg {{
    color: #1a3a5c !important;
    fill: #1a3a5c !important;
    font-weight: 700 !important;
}}

/* ══════════════════════════════════════════════════════════
   사이드바 커스텀 컴포넌트 클래스
   ══════════════════════════════════════════════════════════ */
.sb-compact-header {{
    background: #1a3a5c !important;
    padding: 12px 14px 9px 14px !important;
    margin: 0 !important;
    border-bottom: 2px solid #0078d4 !important;
}}
.sb-compact-header .sb-title {{
    font-size: 0.96rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    letter-spacing: 0.01em !important;
    display: flex !important;
    align-items: center !important;
    gap: 7px !important;
    margin: 0 !important;
}}
.sb-compact-header .sb-subtitle {{
    font-size: 0.6rem !important;
    color: #6b9cc4 !important;
    margin-top: 3px !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 0.07em !important;
    font-weight: 500 !important;
}}

.sb-brand {{ background: #1a3a5c; padding: 12px 16px; margin: 0; border-bottom: 2px solid #0078d4; }}
.sb-brand-logo {{ font-size: 0.93rem; font-weight: 600; color: #ffffff !important; display: flex; align-items: center; gap: 7px; }}
.sb-brand-sub {{ font-size: 0.62rem; color: #6b9cc4 !important; margin-top: 3px; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.06em; }}

/* ── 헤더 배너 ── */
.hero-banner {{
    position: relative;
    border-radius: 10px;
    padding: 22px 32px;
    margin-bottom: 8px;
    overflow: hidden;
    min-height: 120px;
    display: flex; align-items: center;
    background: #0d1117;
    border: none;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    background-size: auto 100% !important;
    background-position: right center !important;
    background-repeat: no-repeat !important;
}}
.hero-banner::before {{
    content: "";
    position: absolute; inset: 0;
    background: linear-gradient(90deg,
        rgba(13,17,23,0.96) 0%,
        rgba(13,17,23,0.85) 30%,
        rgba(13,17,23,0.45) 55%,
        rgba(13,17,23,0.10) 80%,
        rgba(13,17,23,0.0)  100%
    );
    z-index: 1;
    pointer-events: none;
}}
.hero-bg-img {{ display: none; }}
.hero-left {{ position: relative; z-index: 2; flex: 1; max-width: 60%; }}
.hero-badge {{ display: inline-block; background: rgba(255,255,255,0.12); color: #93c5fd; font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; padding: 3px 10px; border-radius: 4px; margin-bottom: 8px; border: 1px solid rgba(255,255,255,0.2); letter-spacing: 0.06em; font-weight: 500; }}
.hero-title {{ color: #ffffff; font-size: 1.45rem; font-weight: 700; letter-spacing: -0.3px; margin: 0 0 6px 0; text-shadow: 0 2px 12px rgba(0,0,0,0.6); }}
.hero-subtitle {{ color: rgba(255,255,255,0.75); font-size: 0.78rem; margin: 0; font-family: 'JetBrains Mono', monospace; text-shadow: 0 1px 6px rgba(0,0,0,0.4); }}

/* ── 패널 ── */
.work-panel {{ background: #ffffff !important; border-radius: 10px; padding: 14px 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #d0d7e0 !important; }}
.work-panel-compact {{ background: #ffffff !important; border-radius: 8px; padding: 10px 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.03); border: 1px solid #d0d7e0 !important; margin-bottom: 10px; }}
.panel-title {{ font-size: 0.74rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #7a8fa6; margin-bottom: 6px; }}

/* ── 미리보기 타이틀 (v4.0 단계 강조 강화) ── */
.preview-title {{
    font-size: 0.82rem; font-weight: 600;
    margin: 0 0 8px 2px; padding: 6px 10px;
    display: flex; align-items: center; gap: 8px;
    border-radius: 6px;
    background: #f5f7fa;
    border: 1px solid #d0d7e0;
}}
.preview-title.before {{ color: #1a3a5c; border-left: 3px solid #7a8fa6; }}
.preview-title.opt {{ color: #0078d4; border-left: 3px solid #0078d4; background: #f0f6ff; }}
.preview-title.after  {{ color: #1a3a5c; border-left: 3px solid #1a3a5c; background: #e8f0f9; }}
.preview-title .pt-meta {{ margin-left: auto; font-weight: 400; color: #7a8fa6; font-size: 0.7rem; font-family: 'JetBrains Mono', monospace; }}

/* ── v4.0 단계 번호 뱃지 ── */
.prev-step-num {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px; height: 22px;
    border-radius: 50%;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 700;
    flex-shrink: 0;
}}
.prev-step-num.s1 {{ background: #e2e8f0; color: #475569; }}
.prev-step-num.s2 {{ background: #0078d4; color: #ffffff; }}
.prev-step-num.s3 {{ background: #1a3a5c; color: #ffffff; }}

/* ── v4.0 미리보기 하단 정보 ── */
.prev-info-bar {{
    margin-top: 4px;
    padding: 6px 10px;
    background: #f5f7fa;
    border: 1px solid #d0d7e0;
    border-radius: 6px;
    font-size: 0.72rem;
    color: #5a7a96;
    font-family: 'JetBrains Mono', monospace;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

[data-testid="stMain"] [data-testid="stImage"],
[data-testid="stMain"] [data-testid="stPyplotChart"],
[data-testid="stMain"] .stImage,
[data-testid="stMain"] .stPyplotChart {{
    background: #ffffff !important;
    border-radius: 8px !important;
    padding: 10px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    border: 1px solid #d0d7e0 !important;
    max-height: calc(100vh - 230px) !important;
    overflow: hidden !important;
    margin: 0 !important;
    text-align: center !important;
}}
[data-testid="stMain"] [data-testid="stImage"] img,
[data-testid="stMain"] [data-testid="stPyplotChart"] img,
[data-testid="stMain"] .stImage img,
[data-testid="stMain"] .stPyplotChart img {{
    max-width: 100% !important;
    max-height: calc(100vh - 260px) !important;
    width: auto !important;
    height: auto !important;
    display: inline-block !important;
    margin: 0 auto !important;
    object-fit: contain !important;
    border-radius: 4px !important;
    background: transparent !important;
}}

/* ── 파일 올리기 ── */
[data-testid="stFileUploader"] {{
    background: #f0f6ff !important;
    border-radius: 8px !important;
    border: 1.5px dashed #9ab5d0 !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: #0078d4 !important;
    background: #e8f0f9 !important;
    box-shadow: 0 2px 12px rgba(0,120,212,0.12) !important;
}}
[data-testid="stFileUploader"] section {{ background: transparent !important; padding: 10px 16px !important; }}
[data-testid="stFileUploader"] section button {{
    background: #0078d4 !important; color: #ffffff !important; border: none !important; border-radius: 6px !important; font-weight: 500 !important; padding: 6px 22px !important; box-shadow: 0 2px 6px rgba(0,120,212,0.3) !important; white-space: nowrap !important; height: 40px !important; min-height: 40px !important; min-width: 150px !important; display: flex !important; align-items: center !important; justify-content: center !important;
}}
[data-testid="stFileUploader"] section button:hover {{ background: #1a6bb5 !important; box-shadow: 0 4px 12px rgba(0,120,212,0.4) !important; transform: translateY(-1px) !important; }}
[data-testid="stFileUploaderDropzoneInstructions"] > div > span:first-child {{ font-size: 0 !important; }}
[data-testid="stFileUploaderDropzoneInstructions"] > div > span:first-child::before {{ content: "📂 파일을 여기로 끌어다 놓거나 버튼을 눌러주세요"; font-size: 0.86rem !important; color: #1a6bb5 !important; font-weight: 600 !important; }}
[data-testid="stFileUploaderDropzoneInstructions"] > div > small {{ font-size: 0 !important; }}
[data-testid="stFileUploaderDropzoneInstructions"] > div > small::before {{ content: "지원 형식: JPG · JPEG · PNG (다중 선택 가능)"; font-size: 0.74rem !important; color: #5a7a96 !important; font-family: 'JetBrains Mono', monospace !important; }}
[data-testid="stFileUploader"] section button {{ font-size: 0 !important; }}
[data-testid="stFileUploader"] section button::before {{ content: "파일 올리기"; font-size: 0.95rem !important; color: #ffffff !important; white-space: nowrap !important; letter-spacing: 0.02em !important; font-weight: 500 !important; }}

/* ── 파일 칩 ── */
.file-chip {{ background: #ffffff; border: 1px solid #d0d7e0; border-left: 3px solid #0078d4; border-radius: 6px; padding: 10px 16px; margin: 10px 0; font-size: 0.85rem; color: #1a3a5c; font-weight: 500; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; box-shadow: 0 1px 4px rgba(0,0,0,0.03); font-family: 'JetBrains Mono', monospace; }}
.file-chip b {{ color: #0078d4; font-weight: 600; }}
.chip-sep {{ width: 1px; height: 14px; background: #d0d7e0; display: inline-block; margin: 0 4px; }}

/* ── v4.0 파일 정보 카드 ── */
.file-info-card {{
    background: #ffffff;
    border: 1px solid #d0d7e0;
    border-radius: 8px;
    padding: 0;
    margin: 10px 0;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}}
.file-info-top {{
    background: #f0f6ff;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    border-bottom: 1px solid #d0e4f5;
}}
.file-info-icon {{
    width: 36px; height: 36px;
    border-radius: 8px;
    background: #ffffff;
    border: 1px solid #c8d4e0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}}
.file-info-text {{ flex: 1; }}
.file-info-title {{ font-size: 0.92rem; font-weight: 600; color: #0052a3; margin: 0; }}
.file-info-sub {{ font-size: 0.72rem; color: #5a7a96; margin-top: 2px; font-family: 'JetBrains Mono', monospace; }}
.file-info-mode {{
    margin-left: auto;
    background: #0078d4;
    color: #ffffff;
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    white-space: nowrap;
}}
.file-info-chips {{
    padding: 8px 12px;
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    max-height: 78px;
    overflow-y: auto;
}}
.fchip {{
    background: #f5f7fa;
    border: 1px solid #e1e7ef;
    border-radius: 4px;
    padding: 3px 9px;
    font-size: 0.72rem;
    color: #5a7a96;
    font-family: 'JetBrains Mono', monospace;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}}

/* ── v4.0 변환 완료 통계 카드 (4분할) ── */
.result-stats {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: #d0d7e0;
    border: 1px solid #d0d7e0;
    border-radius: 8px;
    overflow: hidden;
    margin: 12px 0;
}}
.result-stat {{
    background: #ffffff;
    padding: 12px 14px;
    text-align: center;
}}
.result-stat-num {{
    font-size: 1.45rem;
    font-weight: 700;
    color: #1a3a5c;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.1;
    margin-bottom: 3px;
    letter-spacing: -0.02em;
}}
.result-stat-lbl {{
    font-size: 0.68rem;
    color: #5a7a96;
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}}

/* ── v4.0 7일 차트 ── */
.mini-chart-wrap {{
    background: #ffffff;
    border-radius: 5px;
    padding: 8px 10px;
    margin-top: 6px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}}
.mini-chart-title {{
    font-size: 0.58rem;
    color: #5a7a96;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-bottom: 5px;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
}}
.mini-chart-bars {{
    display: flex;
    align-items: flex-end;
    gap: 3px;
    height: 36px;
    padding: 0 1px;
}}
.mini-bar {{
    flex: 1;
    border-radius: 2px 2px 0 0;
    background: #c8d4e0;
    min-height: 3px;
    position: relative;
    transition: all 0.2s ease;
}}
.mini-bar.today {{
    background: #0078d4;
}}
.mini-bar:hover {{
    background: #1a6bb5;
}}
.mini-chart-labels {{
    display: flex;
    justify-content: space-between;
    font-size: 0.55rem;
    color: #7a8fa6;
    margin-top: 3px;
    font-family: 'JetBrains Mono', monospace;
}}

/* ── v4.0 변환 이력 행 ── */
.history-row {{
    background: #ffffff;
    border: 1px solid #d0d7e0;
    border-radius: 5px;
    padding: 6px 10px;
    margin-bottom: 3px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.72rem;
}}
.history-time {{
    color: #5a7a96;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    min-width: 80px;
}}
.history-mode {{
    background: #f0f6ff;
    color: #1a6bb5;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 0.62rem;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}
.history-count {{
    background: #1a3a5c;
    color: #ffffff;
    padding: 1px 7px;
    border-radius: 3px;
    font-size: 0.65rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}}

[data-testid="stHorizontalBlock"]:has([data-testid="stButton"]) {{ align-items: center !important; }}
button[kind="primary"], button[kind="secondary"] {{ height: 44px !important; min-height: 44px !important; display: flex !important; align-items: center !important; justify-content: center !important; }}

/* ── 프리셋 버튼 ── */
.preset-row [data-testid="stHorizontalBlock"] [data-testid="stColumn"] button,
.preset-row button[kind="primary"],
.preset-row button[kind="secondary"] {{ height: 38px !important; min-height: 38px !important; max-height: 38px !important; padding: 0 6px !important; font-size: 0.77rem !important; font-weight: 500 !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; line-height: 38px !important; width: 100% !important; border-radius: 6px !important; transform: none !important; display: block !important; }}
.preset-row button p, .preset-row button span {{ overflow: hidden !important; text-overflow: ellipsis !important; white-space: nowrap !important; line-height: 1 !important; }}
.preset-row button[kind="primary"]:hover, .preset-row button[kind="secondary"]:hover {{ transform: translateY(-1px) !important; }}

[data-testid="stTooltipIcon"] svg, [data-testid="stTooltipHoverTarget"] svg {{ color: #5a7a96 !important; fill: #5a7a96 !important; transition: all 0.2s ease !important; }}
[data-testid="stTooltipIcon"]:hover svg, [data-testid="stTooltipHoverTarget"]:hover svg {{ color: #0078d4 !important; fill: #0078d4 !important; transform: scale(1.15); }}

/* ── CAD 블루 버튼 ── */
button[kind="primary"] {{ background: #0078d4 !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 0 24px !important; height: 44px !important; min-height: 44px !important; font-weight: 600 !important; width: 100% !important; box-shadow: 0 2px 8px rgba(0,120,212,0.3) !important; transition: all 0.2s ease !important; display: flex !important; align-items: center !important; justify-content: center !important; letter-spacing: 0.02em !important; }}
button[kind="primary"]:hover {{ transform: translateY(-1px) !important; box-shadow: 0 4px 14px rgba(0,120,212,0.4) !important; background: #1a6bb5 !important; }}
button[kind="secondary"] {{ background: #ffffff !important; color: #5a7a96 !important; border: 1px solid #c8d2de !important; border-radius: 8px !important; padding: 0 24px !important; height: 44px !important; min-height: 44px !important; font-weight: 500 !important; width: 100% !important; box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important; transition: all 0.2s ease !important; display: flex !important; align-items: center !important; justify-content: center !important; }}
button[kind="secondary"]:hover {{ background: #f5f7fa !important; border-color: #0078d4 !important; color: #0078d4 !important; transform: translateY(-1px) !important; }}

[data-testid="stDownloadButton"] > button {{ background: #ffffff !important; color: #0078d4 !important; border: 1px solid #c8d2de !important; border-radius: 6px !important; padding: 11px 18px !important; font-weight: 500 !important; font-size: 0.85rem !important; transition: all 0.18s ease !important; width: 100% !important; text-align: left !important; }}
[data-testid="stDownloadButton"] > button:hover {{ background: #f0f6ff !important; border-color: #0078d4 !important; transform: translateY(-1px) !important; }}
.zip-btn [data-testid="stDownloadButton"] > button {{ background: #1a3a5c !important; color: #ffffff !important; border: none !important; font-size: 0.95rem !important; padding: 14px 24px !important; border-radius: 8px !important; font-weight: 600 !important; }}
.zip-btn [data-testid="stDownloadButton"] > button:hover {{ background: #0078d4 !important; }}

[data-testid="stProgressBar"] > div {{ background: #0078d4 !important; border-radius: 4px !important; }}

/* ── v4.0 변환 진행 도트 ── */
.prog-dots {{
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
    margin-top: 6px;
}}
.prog-dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #e1e7ef;
    border: 1px solid #c8d4e0;
    transition: all 0.2s ease;
}}
.prog-dot.done {{
    background: #4ade80;
    border-color: #22c55e;
}}
.prog-dot.fail {{
    background: #f87171;
    border-color: #ef4444;
}}
.prog-dot.active {{
    background: #0078d4;
    border-color: #0052a3;
    animation: pulse 1.2s ease-in-out infinite;
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50%      {{ opacity: 0.55; transform: scale(1.18); }}
}}

/* ── 상단 푸터 ── */
.main-footer {{
    position: fixed; top: 0; left: 0; right: 0; height: 38px;
    background: #ffffff;
    border-bottom: 1px solid #d0d7e0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    display: flex; align-items: center; justify-content: flex-end;
    padding: 0 20px;
    z-index: 99999;
    pointer-events: none;
}}
.main-footer-inner {{
    display: flex; align-items: center; gap: 8px;
    background: #1a3a5c;
    color: #e8f0f9;
    padding: 4px 12px; border-radius: 4px;
    font-size: 10.5px; font-weight: 500;
    box-shadow: 0 1px 4px rgba(26,58,92,0.15);
    letter-spacing: 0.02em;
    font-family: 'JetBrains Mono', monospace;
}}
</style>
<div class="main-footer"><div class="main-footer-inner">📐 도면팀-이영세 (Lee &amp; Mock IP) all rights reserved · v6.2</div></div>
""", unsafe_allow_html=True)

# ── 배경 이미지 별도 주입 ──
_bg_inject = "<style>\n"
if _HERO_IMG_B64:
    _bg_inject += f'.hero-banner {{ background-image: url("data:image/png;base64,{_HERO_IMG_B64}") !important; }}\n'
_bg_inject += "</style>"
st.markdown(_bg_inject, unsafe_allow_html=True)


# ══════════════════════════════════════════
#  🔧  엔진 설정
# ══════════════════════════════════════════

SCALE  = 0.1
INVERT = True

MIN_POINTS_MAP = {
    "기계도면 - 사시도":              4,
    "기계도면 - 정면도/단면도":        4,
    "깔끔한 디지털 선화":              3,
    "일반 이미지(간략한 표현,한줄)":   6,
    "일반 이미지(풍성한 표현,두줄)":   6,
}

PRESETS = {
    "기계도면 - 사시도": {
        "기본 🔷": {"sl_eps": 0.5, "sl_smooth": 9},
        "정밀 🔬":  {"sl_eps": 0.3, "sl_smooth": 5},
        "단순 ⚡":  {"sl_eps": 1.0, "sl_smooth": 13},
    },
    "기계도면 - 정면도/단면도": {
        "기본 🔷":  {"sl_eps": 1.2, "sl_smooth": 5},
        "정밀 🔬":  {"sl_eps": 0.8, "sl_smooth": 3},
        "단순 ⚡":  {"sl_eps": 2.5, "sl_smooth": 9},
    },
    "깔끔한 디지털 선화": {
        "기본 ⬜":  {"sl_eps": 0.4, "sl_smooth": 5},
        "정밀 🔬":  {"sl_eps": 0.2, "sl_smooth": 3},
        "단순 ⚡":  {"sl_eps": 0.8, "sl_smooth": 9},
    },
    "일반 이미지(간략한 표현,한줄)": {
        "기본 〰️":   {"sl_threshold": 127, "sl_straight": 2.0, "sl_eps": 0.8, "sl_spline": 120, "sl_smooth": 11},
        "흐린선 🌫️": {"sl_threshold": 80,  "sl_straight": 1.5, "sl_eps": 0.5, "sl_spline": 150, "sl_smooth": 15},
        "진한선 🖊️": {"sl_threshold": 170, "sl_straight": 3.0, "sl_eps": 1.2, "sl_spline": 100, "sl_smooth": 7},
    },
    "일반 이미지(풍성한 표현,두줄)": {
        "기본 🔲":  {"sl_threshold": 127, "sl_epsilon": 1.2},
        "단순 ⚡":  {"sl_threshold": 100, "sl_epsilon": 0.8},
        "세밀 🔬":  {"sl_threshold": 150, "sl_epsilon": 2.0},
    },
}

_SLIDER_DEFAULTS = {
    "sl_eps":        0.5,
    "sl_smooth":     9,
    "sl_threshold":  127,
    "sl_straight":   2.0,
    "sl_spline":     120,
    "sl_epsilon":    1.2,
}

def _apply_preset_callback(img_type, pname, preset_vals):
    st.session_state[f"active_preset_{img_type}"] = pname
    for k, v in preset_vals.items():
        st.session_state[k] = v

def _init_sliders():
    for k, v in _SLIDER_DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_sliders()

@st.cache_resource
def load_ocr_model():
    return easyocr.Reader(['ko', 'en'], gpu=False)


# ══════════════════════════════════════════
#  📊  SQLite 사용자 통계 시스템 (v4.0 이력 조회 강화)
# ══════════════════════════════════════════

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usage_stats.db")

@contextmanager
def _db():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_stats_db():
    with _db() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                visit_date TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                UNIQUE(user_id, visit_date)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                conv_date TEXT NOT NULL,
                conv_time TEXT NOT NULL,
                file_count INTEGER NOT NULL,
                image_type TEXT,
                success INTEGER DEFAULT 1
            )
        """)
        # ⭐ v6.2 신규: 사용자 정의 프리셋 (이름 붙인 영구 저장)
        c.execute("""
            CREATE TABLE IF NOT EXISTS user_presets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                preset_name TEXT NOT NULL,
                image_type TEXT,
                settings_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(user_id, preset_name)
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_conv_date ON conversions(conv_date)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_visit_date ON visits(visit_date)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_user_preset ON user_presets(user_id)")

def get_or_create_user_id():
    """
    영구 방문자 ID 관리 — URL query_params 기반.

    작동 원리:
      ① URL에 ?vid=... 가 있으면 그걸 사용 (새로고침 후에도 브라우저가 URL 유지)
      ② session_state에 있으면 URL에 쓰고 반환 (같은 탭, 재렌더링)
      ③ 둘 다 없으면 UUID 생성 → URL + session_state 양쪽에 저장

    SQLite UNIQUE(user_id, visit_date) 제약으로 DB 레벨에서 최종 중복 방지.
    브라우저를 완전히 닫으면 URL이 사라지므로 새 ID가 생성됩니다.
    """
    # ① URL query param 'vid' — 새로고침해도 브라우저가 URL을 유지함
    try:
        vid = st.query_params.get("vid", None)
        if vid and 6 <= len(vid) <= 20:
            st.session_state["user_id"] = vid
            return vid
    except Exception:
        pass

    # ② session_state — 같은 탭 내 재렌더링 시 (URL보다 후순위)
    if "user_id" in st.session_state:
        uid = st.session_state["user_id"]
        try:
            # URL에 없으면 추가 (다음 새로고침 시 ①에서 읽힘)
            if st.query_params.get("vid") != uid:
                st.query_params["vid"] = uid
        except Exception:
            pass
        return uid

    # ③ 완전 신규 방문 — UUID 생성 후 양쪽에 저장
    new_id = str(uuid.uuid4())[:12]
    st.session_state["user_id"] = new_id
    try:
        st.query_params["vid"] = new_id
    except Exception:
        pass
    return new_id

def record_visit(user_id):
    """
    오늘 날짜 + user_id(Streamlit 세션 ID) 기반으로 방문 기록.
    UNIQUE(user_id, visit_date) 제약으로 DB 레벨에서 중복 방지.
    새로고침해도 세션 ID가 동일하므로 IntegrityError → 무시됨.
    """
    today = datetime.date.today().isoformat()
    now   = datetime.datetime.now().isoformat(timespec="seconds")
    try:
        with _db() as c:
            try:
                c.execute(
                    "INSERT INTO visits (user_id, visit_date, first_seen_at) VALUES (?, ?, ?)",
                    (user_id, today, now)
                )
                return True   # 실제로 새 방문 기록됨
            except sqlite3.IntegrityError:
                return False  # 오늘 이미 기록된 세션 → 무시
    except Exception:
        return False

def record_conversion(user_id, file_count, image_type, success=True):
    today = datetime.date.today().isoformat()
    now   = datetime.datetime.now().isoformat(timespec="seconds")
    try:
        with _db() as c:
            c.execute(
                "INSERT INTO conversions (user_id, conv_date, conv_time, file_count, image_type, success) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, today, now, int(file_count), str(image_type), 1 if success else 0)
            )
    except Exception:
        pass

def get_stats():
    today = datetime.date.today().isoformat()
    try:
        with _db() as c:
            today_visitors = c.execute("SELECT COUNT(DISTINCT user_id) FROM visits WHERE visit_date = ?", (today,)).fetchone()[0]
            today_conv = c.execute("SELECT COALESCE(SUM(file_count),0) FROM conversions WHERE conv_date = ? AND success = 1", (today,)).fetchone()[0]
            total_conv = c.execute("SELECT COALESCE(SUM(file_count),0) FROM conversions WHERE success = 1").fetchone()[0]
            total_users = c.execute("SELECT COUNT(DISTINCT user_id) FROM visits").fetchone()[0]
            seven_days = c.execute("""
                SELECT conv_date, COALESCE(SUM(file_count),0) as cnt
                FROM conversions WHERE conv_date >= date('now','-6 days') AND success = 1
                GROUP BY conv_date ORDER BY conv_date
            """).fetchall()
        return {
            "today_visitors": today_visitors, "today_conv": today_conv,
            "total_conv": total_conv, "total_users": total_users,
            "last_7days": [{"date": d, "count": n} for d, n in seven_days]
        }
    except Exception:
        return {"today_visitors": 0, "today_conv": 0, "total_conv": 0, "total_users": 0, "last_7days": []}

# 🌟 v4.0: 변환 이력 조회 함수
def get_recent_conversions(user_id, limit=15):
    """현재 사용자의 최근 변환 내역을 조회"""
    try:
        with _db() as c:
            rows = c.execute("""
                SELECT conv_date, conv_time, file_count, image_type, success
                FROM conversions
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (user_id, limit)).fetchall()
        return [{"date": r[0], "time": r[1], "count": r[2], "type": r[3], "success": bool(r[4])} for r in rows]
    except Exception:
        return []


# ══════════════════════════════════════════
#  ⭐ v6.2: 사용자 정의 프리셋 (이름 붙여서 SQLite에 영구 저장) — 1순위 신규
# ══════════════════════════════════════════

def save_user_preset(user_id, preset_name, image_type, settings_dict):
    """
    사용자 프리셋을 SQLite에 저장 (또는 갱신).
    같은 이름이 있으면 덮어씁니다.

    Returns
    -------
    (success: bool, msg: str)
    """
    if not user_id or not preset_name:
        return False, "사용자 ID와 프리셋 이름이 필요합니다."
    preset_name = preset_name.strip()
    if not preset_name:
        return False, "프리셋 이름이 비어있습니다."
    if len(preset_name) > 50:
        return False, "프리셋 이름은 50자 이내여야 합니다."
    try:
        now = datetime.datetime.now().isoformat(timespec="seconds")
        settings_json = json.dumps(settings_dict, ensure_ascii=False, default=str)
        with _db() as c:
            # 존재하면 UPDATE, 없으면 INSERT
            existing = c.execute(
                "SELECT id FROM user_presets WHERE user_id=? AND preset_name=?",
                (user_id, preset_name)
            ).fetchone()
            if existing:
                c.execute("""
                    UPDATE user_presets
                    SET image_type=?, settings_json=?, updated_at=?
                    WHERE user_id=? AND preset_name=?
                """, (image_type, settings_json, now, user_id, preset_name))
                return True, f"프리셋 '{preset_name}' 갱신 완료"
            else:
                c.execute("""
                    INSERT INTO user_presets
                    (user_id, preset_name, image_type, settings_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, preset_name, image_type, settings_json, now, now))
                return True, f"프리셋 '{preset_name}' 저장 완료"
    except Exception as e:
        return False, f"저장 실패: {str(e)[:80]}"


def load_user_presets(user_id):
    """
    현재 사용자의 모든 프리셋을 최신순으로 조회.

    Returns
    -------
    list of dict [{"id":int, "name":str, "image_type":str, "settings":dict, "updated_at":str}, ...]
    """
    if not user_id:
        return []
    try:
        with _db() as c:
            rows = c.execute("""
                SELECT id, preset_name, image_type, settings_json, updated_at
                FROM user_presets
                WHERE user_id = ?
                ORDER BY updated_at DESC
            """, (user_id,)).fetchall()
        result = []
        for r in rows:
            try:
                settings = json.loads(r[3])
            except Exception:
                settings = {}
            result.append({
                "id": r[0],
                "name": r[1],
                "image_type": r[2] or "",
                "settings": settings,
                "updated_at": r[4] or "",
            })
        return result
    except Exception:
        return []


def delete_user_preset(user_id, preset_name):
    """프리셋 삭제. Returns (success, msg)."""
    if not user_id or not preset_name:
        return False, "삭제할 프리셋이 없습니다."
    try:
        with _db() as c:
            cur = c.execute(
                "DELETE FROM user_presets WHERE user_id=? AND preset_name=?",
                (user_id, preset_name)
            )
            if cur.rowcount > 0:
                return True, f"'{preset_name}' 삭제 완료"
            return False, "삭제할 프리셋을 찾지 못했습니다."
    except Exception as e:
        return False, f"삭제 실패: {str(e)[:80]}"


def collect_current_settings(state):
    """
    현재 session_state에서 저장 가능한 설정 키들만 모아 dict로 반환.
    DB 저장 + 복원용.

    Parameters
    ----------
    state : dict-like
        st.session_state

    Returns
    -------
    dict
    """
    # 저장 대상 키 화이트리스트 (sl_*, opt_*, v6_*, v61_*, layer_name 등)
    keys_of_interest = []
    try:
        for k in list(state.keys()):
            if not isinstance(k, str):
                continue
            if (k.startswith("sl_") or k.startswith("opt_")
                or k.startswith("v6_") or k.startswith("v61_") or k.startswith("v62_")
                or k in ("layer_name_input", "user_scale_input", "image_type_radio",
                         "preview_bg_choice", "preview_alpha")):
                keys_of_interest.append(k)
    except Exception:
        return {}
    settings = {}
    for k in keys_of_interest:
        try:
            v = state[k]
            # JSON 직렬화 가능한 형태만 저장
            if isinstance(v, (str, int, float, bool, type(None))):
                settings[k] = v
        except Exception:
            continue
    return settings


def apply_user_preset(state, settings_dict):
    """
    사용자 프리셋을 session_state에 적용.

    Parameters
    ----------
    state : dict-like (st.session_state)
    settings_dict : dict

    Returns
    -------
    int  적용된 키 수
    """
    if not isinstance(settings_dict, dict):
        return 0
    applied = 0
    for k, v in settings_dict.items():
        try:
            if isinstance(k, str) and isinstance(v, (str, int, float, bool, type(None))):
                state[k] = v
                applied += 1
        except Exception:
            continue
    return applied


# ══════════════════════════════════════════
#  🤖 v6.2: AI 슬라이더 수치 추천 — 2순위 신규
# ══════════════════════════════════════════

def recommend_slider_values(qa_result, image_type="기계도면(외곽선,깔끔 디테일)"):
    """
    analyze_image_quality 결과 + 도면 종류 기반으로 슬라이더 값까지 구체 추천.

    Parameters
    ----------
    qa_result : dict
        analyze_image_quality() 반환값
    image_type : str
        도면 종류

    Returns
    -------
    dict
        {
            "slider_values": {"sl_threshold": int, ...},
            "rationale": [str, ...],   # 왜 이 값을 추천하는지 설명
        }
    """
    if not qa_result:
        return {"slider_values": {}, "rationale": []}

    score = qa_result["score"]
    sharpness = qa_result["sharpness"]
    noise_ratio = qa_result["noise_ratio"]
    contrast = qa_result["contrast"]
    w, h = qa_result["resolution"]
    img_diag = math.hypot(w, h)

    sv = {}      # slider_values
    rat = []     # 추천 이유

    # ── 1) 임계값 (Threshold) ── 대비/노이즈 기반
    if contrast >= 50 and noise_ratio < 3.0:
        sv["sl_threshold"] = 130; rat.append("대비 양호 → 임계값 130 (표준)")
    elif contrast < 25:
        sv["sl_threshold"] = 110; rat.append(f"대비 부족({contrast:.0f}) → 임계값 110 (낮춤)")
    elif noise_ratio > 6.0:
        sv["sl_threshold"] = 145; rat.append(f"노이즈 많음({noise_ratio:.1f}%) → 임계값 145 (높임)")
    else:
        sv["sl_threshold"] = 125; rat.append("임계값 125 (보통)")

    # ── 2) approxPolyDP epsilon ── 선명도 기반
    if sharpness >= 300:
        sv["sl_epsilon"] = 0.5; rat.append("선명도 우수 → epsilon 0.5 (세밀)")
    elif sharpness >= 100:
        sv["sl_epsilon"] = 0.8; rat.append("선명도 보통 → epsilon 0.8")
    else:
        sv["sl_epsilon"] = 1.2; rat.append("선명도 낮음 → epsilon 1.2 (단순화 강화)")

    # ── 3) smooth window ── 노이즈/선명도 기반
    if noise_ratio < 2.0 and sharpness >= 200:
        sv["sl_smooth_window"] = 3; rat.append("깨끗한 이미지 → smooth 3 (최소)")
    elif noise_ratio > 5.0 or sharpness < 80:
        sv["sl_smooth_window"] = 9; rat.append("노이즈/흐림 → smooth 9 (적극)")
    else:
        sv["sl_smooth_window"] = 5; rat.append("smooth 5 (표준)")

    # ── 4) min_path_len ── 해상도 기반 (큰 이미지는 더 긴 path 필요)
    if img_diag > 2500:
        sv["sl_min_path_len"] = 12; rat.append(f"고해상도({w}×{h}) → 최소 path 12px")
    elif img_diag < 1000:
        sv["sl_min_path_len"] = 5; rat.append(f"저해상도({w}×{h}) → 최소 path 5px")
    else:
        sv["sl_min_path_len"] = 8; rat.append("최소 path 8px (표준)")

    # ── 5) stitch_gap (끊긴 선 연결 거리) ── 노이즈 기반
    if noise_ratio > 6.0:
        sv["sl_stitch_gap"] = 6.0; rat.append("노이즈로 끊김 多 → stitch 6.0")
    elif noise_ratio < 2.0:
        sv["sl_stitch_gap"] = 2.5; rat.append("깨끗 → stitch 2.5 (보수적)")
    else:
        sv["sl_stitch_gap"] = 4.0; rat.append("stitch 4.0 (표준)")

    # ── 6) dedup_dist ── 도면 종류 기반
    if image_type and "기계" in image_type:
        sv["sl_dedup_dist"] = 1.5; rat.append("기계도면 → 중복 1.5 (관대)")
    else:
        sv["sl_dedup_dist"] = 1.0; rat.append("중복 1.0 (표준)")

    # ── 7) speckle 최소 면적 ── 노이즈 기반
    if noise_ratio > 5.0:
        sv["v6_min_speckle_area"] = 8; rat.append(f"노이즈({noise_ratio:.1f}%) → speckle 8px²")
    elif noise_ratio > 2.0:
        sv["v6_min_speckle_area"] = 5; rat.append("speckle 5px²")
    # 노이즈 매우 적으면 추천 안 함

    # ── 8) gap_bridge_size ── 노이즈 기반
    if noise_ratio > 4.0:
        sv["v6_gap_bridge_size"] = 3; rat.append("끊김 多 → bridge 3px")

    # ── 9) sharpen 강도 ── 선명도 기반
    if sharpness < 100:
        sv["sl_sharpen_strength"] = 1.5; rat.append(f"흐림({sharpness:.0f}) → 샤픈 1.5")
    elif sharpness < 200:
        sv["sl_sharpen_strength"] = 1.0; rat.append("샤픈 1.0")

    return {
        "slider_values": sv,
        "rationale": rat,
    }


# 🌟 v4.0: 7일치 데이터 정규화 (날짜 비어있어도 0으로 채움)
def build_7day_chart_data(last_7days):
    today = datetime.date.today()
    by_date = {item["date"]: item["count"] for item in last_7days}
    series = []
    for i in range(7):
        d = (today - datetime.timedelta(days=6 - i)).isoformat()
        series.append({"date": d, "count": by_date.get(d, 0)})
    return series


# ══════════════════════════════════════════
#  💾  v4.0: 설정 JSON 저장/불러오기
# ══════════════════════════════════════════

def export_settings_json(image_type, layer_name, user_scale, opt_flags, slider_vals):
    """현재 설정을 JSON으로 직렬화"""
    payload = {
        "version": "v4.0",
        "saved_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "image_type": image_type,
        "layer_name": layer_name,
        "user_scale": user_scale,
        "flags": opt_flags,
        "sliders": slider_vals,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

def import_settings_json(json_bytes):
    """JSON 바이트에서 설정 복원"""
    try:
        data = json.loads(json_bytes.decode("utf-8"))
        if not isinstance(data, dict) or "version" not in data:
            return None, "올바르지 않은 설정 파일입니다."
        return data, None
    except Exception as e:
        return None, f"파일 파싱 실패: {e}"


# ══════════════════════════════════════════
#  🔧  이미지 처리 및 DXF 변환 코어
# ══════════════════════════════════════════

def fit_line_least_squares(pts):
    if len(pts) < 2: return None, float('inf')
    x = pts[:, 0].astype(float)
    y = pts[:, 1].astype(float)
    x_range = float(np.ptp(x))
    y_range = float(np.ptp(y))
    if x_range < 1e-3 or y_range < 1e-3:
        return np.array([[x[0], y[0]], [x[-1], y[-1]]]), 0.0
    if x_range >= y_range:
        coeffs = np.polyfit(x, y, 1)
        rms = float(np.sqrt(np.mean((y - np.polyval(coeffs, x)) ** 2)))
    else:
        coeffs = np.polyfit(y, x, 1)
        rms = float(np.sqrt(np.mean((x - np.polyval(coeffs, y)) ** 2)))
    return np.array([[x[0], y[0]], [x[-1], y[-1]]]), rms

def snap_angle(p1, p2, snap_degrees=(0, 30, 45, 60, 90, 120, 135, 150), tolerance_deg=2.5):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if abs(dx) < 1e-6 and abs(dy) < 1e-6: return p1, p2
    angle = math.degrees(math.atan2(dy, dx)) % 180
    length = math.hypot(dx, dy)
    for snap_deg in snap_degrees:
        snap_norm = snap_deg % 180
        diff = min(abs(angle - snap_norm), abs(angle - snap_norm - 180), abs(angle - snap_norm + 180))
        if diff < tolerance_deg:
            cx, cy = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
            rad = math.radians(snap_norm)
            half = length / 2
            return ((cx - half * math.cos(rad), cy - half * math.sin(rad)), (cx + half * math.cos(rad), cy + half * math.sin(rad)))
    return p1, p2

def extract_long_lines_hough(binary, min_length=40, max_gap=8, threshold=50):
    lines_raw = cv2.HoughLinesP(binary, rho=1, theta=np.pi / 180, threshold=int(threshold), minLineLength=int(min_length), maxLineGap=int(max_gap))
    if lines_raw is None: return [], binary.copy()
    masked = binary.copy()
    out = []
    for l in lines_raw:
        x1, y1, x2, y2 = l[0]
        out.append(((float(x1), float(y1)), (float(x2), float(y2))))
        cv2.line(masked, (x1, y1), (x2, y2), 0, thickness=3)
    return out, masked

def filter_short_paths(paths, min_length_px=8.0):
    out = []
    for p in paths:
        if len(p) < 2: continue
        diff = np.diff(p, axis=0)
        total_len = float(np.sum(np.hypot(diff[:, 0], diff[:, 1])))
        if total_len >= min_length_px: out.append(p)
    return out

def stitch_close_paths(paths, max_gap_px=4.0, min_direction_cos=None):
    """
    가까운 path 끝점을 이어붙임.
    
    [v5.0] min_direction_cos가 지정되면 방향 벡터 코사인 유사도를 검사해
    방향이 어긋난 path끼리 엉뚱하게 붙는 오류를 방지한다.
    예: 0.7 → 약 45도 이내, 0.85 → 약 32도 이내만 병합 허용.
    """
    if len(paths) < 2: return paths
    paths = [np.asarray(p, dtype=float) for p in paths]

    def _approach(path, at_end):
        """지정된 끝점으로 다가가는 방향 단위벡터"""
        if len(path) < 2: return np.array([0.0, 0.0])
        n_samp = min(5, len(path) - 1)
        if at_end:
            v = path[-1] - path[-1 - n_samp]
        else:
            v = path[0] - path[n_samp]
        nm = float(np.linalg.norm(v))
        return v / nm if nm > 1e-6 else np.array([0.0, 0.0])

    def _dir_ok(a, a_at_end, b, b_at_end):
        if min_direction_cos is None:
            return True
        va = _approach(a, a_at_end)
        vb = _approach(b, b_at_end)
        # 매끄럽게 이어지려면 두 접근방향이 서로 반대를 향해야 함 → dot이 -1에 가까움
        score = -float(np.dot(va, vb))
        return score >= float(min_direction_cos)

    used = [False] * len(paths)
    out = []
    for i, p in enumerate(paths):
        if used[i]: continue
        used[i] = True
        chain = [p]
        changed = True
        while changed:
            changed = False
            current_start = chain[0][0]
            current_end   = chain[-1][-1]
            for j, q in enumerate(paths):
                if used[j]: continue
                qs, qe = q[0], q[-1]
                d_es = math.hypot(current_end[0] - qs[0], current_end[1] - qs[1])
                d_ee = math.hypot(current_end[0] - qe[0], current_end[1] - qe[1])
                d_se = math.hypot(current_start[0] - qe[0], current_start[1] - qe[1])
                d_ss = math.hypot(current_start[0] - qs[0], current_start[1] - qs[1])

                if d_es < max_gap_px and _dir_ok(chain[-1], True, q, False):
                    chain.append(q); used[j] = True; changed = True; break
                if d_ee < max_gap_px and _dir_ok(chain[-1], True, q, True):
                    chain.append(q[::-1]); used[j] = True; changed = True; break
                if d_se < max_gap_px and _dir_ok(chain[0], False, q, True):
                    chain.insert(0, q); used[j] = True; changed = True; break
                if d_ss < max_gap_px and _dir_ok(chain[0], False, q, False):
                    chain.insert(0, q[::-1]); used[j] = True; changed = True; break
        out.append(np.vstack(chain))
    return out


# ══════════════════════════════════════════
#  🌟 v5.0 신규 함수들 (5종 개선)
# ══════════════════════════════════════════

def prune_skeleton_spurs(skeleton, max_spur_len=8, max_iterations=3):
    """
    [v5.0 NEW] Skeleton의 짧은 잔가지(spur)를 반복 제거.
    각 끝점(degree=1)에서 분기점(degree>=3)까지 추적해 경로 길이가
    max_spur_len 이하이면 (분기점 자체는 보존하고) 제거한다.
    
    Y자/T자 형태로 자라난 잡가지를 깔끔하게 정리해 곡선 품질을 끌어올린다.
    """
    if skeleton is None or skeleton.size == 0:
        return skeleton
    skel = (skeleton > 0).astype(np.uint8)
    h, w = skel.shape

    def _neighbors(y, x):
        out = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0: continue
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and skel[ny, nx] == 1:
                    out.append((ny, nx))
        return out

    for _ in range(max_iterations):
        ys, xs = np.where(skel == 1)
        if len(ys) == 0:
            break
        endpoints = []
        for y, x in zip(ys.tolist(), xs.tolist()):
            if len(_neighbors(y, x)) == 1:
                endpoints.append((y, x))
        if not endpoints:
            break

        changed = False
        for ey, ex in endpoints:
            if skel[ey, ex] == 0:
                continue  # 같은 iteration에서 이미 제거됨
            path = [(ey, ex)]
            visited = {(ey, ex)}
            current = (ey, ex)
            reached_branch = False

            for _step in range(max_spur_len + 1):
                nbrs = [n for n in _neighbors(*current) if n not in visited]
                if not nbrs:
                    break
                # 다음 점이 분기점이면 → 그 직전까지만 잔가지로 보고 멈춤
                nxt = nbrs[0]
                if len(_neighbors(*nxt)) >= 3:
                    reached_branch = True
                    break
                # 한 점에 이웃이 1개씩만 있는 직선 가지를 따라감
                if len(_neighbors(*current)) > 2 and current != (ey, ex):
                    # 중간에 분기점을 거쳤다면 더 이상 spur로 볼 수 없음
                    break
                visited.add(nxt)
                path.append(nxt)
                current = nxt

            # 분기점에 도달했고 가지 길이가 한계 이하면 제거
            if reached_branch and len(path) <= max_spur_len:
                for py, px in path:
                    skel[py, px] = 0
                changed = True

        if not changed:
            break

    return (skel * 255).astype(np.uint8)


def detect_corner_anchors(pts, angle_threshold_deg=40.0, min_segment_len=4):
    """
    [v5.0 NEW] Path 내 코너(직각/예각) 인덱스를 검출.
    스무딩 전에 호출하여, 해당 좌표는 후처리 후에도 원본 그대로 보존된다.
    
    Parameters:
    - angle_threshold_deg: 두 단위벡터 각도 변화가 이 값 이상이면 코너
    - min_segment_len: 코너 양쪽으로 필요한 최소 점 수
    """
    n = len(pts)
    if n < 2 * min_segment_len + 1:
        return [0, n - 1] if n > 1 else ([0] if n == 1 else [])

    anchors = [0]
    # 두 단위벡터의 dot 값이 이 값 미만이면 코너로 판정
    # 예: threshold 40도 → cos(40°)≈0.766. dot < 0.766이면 두 벡터 사이 각도 ≥40° (꺾인 상태)
    cos_thresh = math.cos(math.radians(float(angle_threshold_deg)))

    pts_arr = np.asarray(pts, dtype=float)
    for i in range(min_segment_len, n - min_segment_len):
        v1 = pts_arr[i] - pts_arr[i - min_segment_len]
        v2 = pts_arr[i + min_segment_len] - pts_arr[i]
        n1 = float(np.linalg.norm(v1))
        n2 = float(np.linalg.norm(v2))
        if n1 < 1e-6 or n2 < 1e-6:
            continue
        cos_a = float(np.dot(v1, v2) / (n1 * n2))
        if cos_a < cos_thresh:
            if i - anchors[-1] >= min_segment_len:
                anchors.append(i)

    if anchors[-1] != n - 1:
        anchors.append(n - 1)
    return anchors


def smooth_path_with_anchors(pts, window, anchors=None):
    """
    [v5.0 NEW] Anchor 인덱스의 좌표는 보존하면서 path를 스무딩.
    Anchor 사이의 각 구간만 개별 스무딩 → 직각 코너가 둥글게 깎이지 않음.
    """
    if anchors is None or len(anchors) <= 2:
        # 코너가 없으면 기존 스무딩 그대로
        return smooth_path(pts, window)

    pts_arr = np.asarray(pts, dtype=float)
    out_segments = []
    for k in range(len(anchors) - 1):
        i0 = anchors[k]
        i1 = anchors[k + 1]
        seg = pts_arr[i0:i1 + 1]
        if len(seg) >= max(window, 4):
            smoothed_seg = smooth_path(seg, window)
        else:
            smoothed_seg = seg.copy()
        # Anchor 좌표 강제 복원
        smoothed_seg[0]  = pts_arr[i0]
        smoothed_seg[-1] = pts_arr[i1]
        # 다음 구간의 시작과 겹치지 않도록 마지막 점은 마지막 구간에서만 포함
        if k < len(anchors) - 2:
            out_segments.append(smoothed_seg[:-1])
        else:
            out_segments.append(smoothed_seg)

    return np.vstack(out_segments)


def calculate_quality_score(report, path_count_raw=0, path_count_clean=0):
    """
    [v5.0 NEW] DXF 변환 결과의 품질 점수(0~100) + 등급(A+~F) 계산.
    
    배점:
    - 선 연속성 (40점): 후처리로 살아남은 path 비율 (잔가지/중복선 제거 효율)
    - 기하 인식률 (25점): ARC/CIRCLE 변환 비율
    - 깔끔함 (20점): 경고/이슈 수가 적을수록 가산
    - 변환 성공도 (15점): 추출된 선의 절대 수량
    """
    lines = int(report.get("lines", 0))
    circles = int(report.get("circles", 0))
    patterns = int(report.get("patterns", 0))
    warnings_n = len([w for w in report.get("warnings", []) if w])
    total_entities = lines + circles + patterns

    if total_entities == 0:
        return {"score": 0, "grade": "F", "breakdown": {
            "continuity": 0, "geometry": 0, "cleanliness": 0, "yield": 0
        }}

    # 1) 선 연속성 (40점)
    if path_count_raw > 0 and path_count_clean >= 0:
        # 후처리로 남은 비율 (1.0이면 군더더기 없음, 0.5면 절반이 잔가지/중복)
        ratio = max(0.0, min(1.0, path_count_clean / path_count_raw))
        # 0.7 이상이면 만점, 0.3 이하면 0점 (선형 매핑)
        if ratio >= 0.7:
            continuity = 40
        elif ratio >= 0.3:
            continuity = int(40 * (ratio - 0.3) / 0.4)
        else:
            continuity = 0
    else:
        continuity = 28  # 기본값 (정보 부족시 중간 점수)

    # 2) 기하 인식률 (25점)
    geo_entities = circles + patterns
    if total_entities >= 5:
        geo_ratio = geo_entities / total_entities
        # 10~30%가 가장 적절 → 그 구간이 만점
        if 0.05 <= geo_ratio <= 0.40:
            geometry = 25
        elif geo_ratio < 0.05:
            geometry = int(25 * (geo_ratio / 0.05) * 0.8 + 5)  # 5~25
        else:
            geometry = max(10, int(25 * (1.0 - (geo_ratio - 0.40) / 0.60)))
    else:
        geometry = 15  # 매우 작은 도면은 기본 점수

    # 3) 깔끔함 (20점) - 경고 1개당 -3점, 정보성 메시지는 영향 적음
    cleanliness = max(0, 20 - max(0, warnings_n - 2) * 3)

    # 4) 변환 성공도 (15점) - 추출된 선 수량
    if lines >= 20:
        yield_pts = 15
    elif lines >= 10:
        yield_pts = 12
    elif lines >= 5:
        yield_pts = 8
    elif lines >= 2:
        yield_pts = 5
    else:
        yield_pts = 2

    total = continuity + geometry + cleanliness + yield_pts
    total = max(0, min(100, total))

    if   total >= 90: grade = "A+"
    elif total >= 80: grade = "A"
    elif total >= 70: grade = "B"
    elif total >= 60: grade = "C"
    elif total >= 50: grade = "D"
    else:             grade = "F"

    return {
        "score": int(total),
        "grade": grade,
        "breakdown": {
            "continuity": int(continuity),
            "geometry":   int(geometry),
            "cleanliness": int(cleanliness),
            "yield":      int(yield_pts),
        }
    }


def apply_crop_to_bytes(img_bytes, top_pct, bottom_pct, left_pct, right_pct):
    """
    [v5.0 NEW] 이미지 바이트를 받아 상하좌우 %만큼 잘라낸 PNG 바이트를 반환.
    잘못된 입력(너무 많이 자름, 디코딩 실패)일 경우 원본 그대로 반환.
    """
    top_pct = max(0, min(45, int(top_pct or 0)))
    bottom_pct = max(0, min(45, int(bottom_pct or 0)))
    left_pct = max(0, min(45, int(left_pct or 0)))
    right_pct = max(0, min(45, int(right_pct or 0)))

    if top_pct + bottom_pct == 0 and left_pct + right_pct == 0:
        return img_bytes
    if top_pct + bottom_pct >= 95 or left_pct + right_pct >= 95:
        return img_bytes

    try:
        arr = np.asarray(bytearray(img_bytes), dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return img_bytes
        h, w = img.shape[:2]
        y0 = int(h * top_pct / 100)
        y1 = int(h * (100 - bottom_pct) / 100)
        x0 = int(w * left_pct / 100)
        x1 = int(w * (100 - right_pct) / 100)
        if y1 - y0 < 10 or x1 - x0 < 10:
            return img_bytes
        cropped = img[y0:y1, x0:x1]
        success, encoded = cv2.imencode(".png", cropped)
        if not success:
            return img_bytes
        return encoded.tobytes()
    except Exception:
        return img_bytes


def smooth_path(pts: np.ndarray, window: int) -> np.ndarray:
    """🆕 v6.4 [개선 ⑤]: window를 path 길이의 1/4 이하로 자동 제한.
    짧은 path(원/호 등)에 큰 window가 적용되어 형태가 왜곡되는 현상 방지.
    """
    if len(pts) < window or window < 4: return pts
    # 🆕 v6.4: path 길이 대비 window 자동 상한 (1/4 이하, 홀수)
    auto_max = max(3, len(pts) // 4)
    if auto_max % 2 == 0:
        auto_max -= 1
    w_in = min(int(window), int(auto_max))
    w  = max(3, w_in | 1)
    if len(pts) <= w: w = len(pts) if len(pts) % 2 != 0 else len(pts) - 1
    if w < 3: return pts
    try:
        from scipy.signal import savgol_filter
        xs = savgol_filter(pts[:, 0].astype(float), window_length=w, polyorder=2)
        ys = savgol_filter(pts[:, 1].astype(float), window_length=w, polyorder=2)
    except ImportError:
        xs = uniform_filter1d(pts[:, 0].astype(float), size=w)
        ys = uniform_filter1d(pts[:, 1].astype(float), size=w)
    xs[0], xs[-1] = pts[0, 0], pts[-1, 0]
    ys[0], ys[-1] = pts[0, 1], pts[-1, 1]
    return np.column_stack([xs, ys])


# ══════════════════════════════════════════════════════════════════
#  🆕 v6.4 신규 헬퍼: Closed Path 자동 인식 + Adaptive Epsilon
# ══════════════════════════════════════════════════════════════════
def _adaptive_epsilon(pts, base_eps, min_eps=0.3, max_eps=5.0, ref_len=200.0):
    """🆕 v6.4 [개선 ④]: path 길이에 따라 epsilon을 자동 조정.
    - 짧은 path (≤60px) → epsilon을 base의 0.3배 (형태 보존)
    - 기준 길이 (200px) → epsilon을 base 그대로
    - 긴 path (≥400px) → epsilon을 base의 2배 (불필요한 노드 감소)
    """
    try:
        if pts is None or len(pts) < 2:
            return float(base_eps)
        diffs = np.diff(np.asarray(pts, dtype=float), axis=0)
        path_len = float(np.sum(np.hypot(diffs[:, 0], diffs[:, 1])))
        if path_len <= 0:
            return float(base_eps)
        ratio = float(np.clip(path_len / float(ref_len), 0.3, 2.0))
        return float(np.clip(base_eps * ratio, min_eps, max_eps))
    except Exception:
        return float(base_eps)


def _is_path_closed(pts_xy_pixel, close_threshold_px=3.0):
    """🆕 v6.4 [개선 ③]: 픽셀 좌표 기준으로 path가 닫힌(closed) 도형인지 판정.
    시작점과 끝점의 픽셀 거리가 close_threshold_px 이내이면 닫힌 도형으로 본다.
    (DXF mm 좌표가 아니라 픽셀 좌표 기준으로 판정 → scale 영향 없음)
    """
    try:
        if pts_xy_pixel is None or len(pts_xy_pixel) < 3:
            return False
        p0 = pts_xy_pixel[0]
        pN = pts_xy_pixel[-1]
        d = math.hypot(float(p0[0]) - float(pN[0]), float(p0[1]) - float(pN[1]))
        return d < float(close_threshold_px)
    except Exception:
        return False


def _add_lwpolyline_auto(msp, pts_xy_pixel, pts_dxf_2d, dxfattribs,
                         close_threshold_px=3.0):
    """🆕 v6.4 [개선 ③]: lwpolyline 추가 + 닫힌 도형이면 자동 close().
    - pts_xy_pixel: 픽셀 좌표 (닫힘 판정용)
    - pts_dxf_2d  : 이미 to_pt()로 변환된 DXF 좌표 리스트
    반환: 추가된 entity. 닫힌 도형이면 .close() 처리되어 AutoCAD에서
          '닫힌 폴리라인'으로 인식됨 (hatch fill 등 가능).
    """
    if not pts_dxf_2d or len(pts_dxf_2d) < 2:
        return None
    pline = msp.add_lwpolyline(pts_dxf_2d, dxfattribs=dxfattribs)
    if _is_path_closed(pts_xy_pixel, close_threshold_px=close_threshold_px):
        try:
            pline.close(True)
        except Exception:
            try:
                # ezdxf 일부 버전 호환 fallback
                pline.dxf.flags = pline.dxf.flags | 1
            except Exception:
                pass
    return pline


def fit_circle_algebraic(pts):
    if len(pts) < 3: return None, None, float('inf')
    x = pts[:, 0]
    y = pts[:, 1]
    A = np.column_stack([x, y, np.ones(len(x))])
    B = -(x**2 + y**2)
    try:
        res, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
        D, E, F = res
        cx, cy = -D / 2, -E / 2
        radius = math.sqrt(max(0, cx**2 + cy**2 - F))
        distances = np.sqrt((x - cx)**2 + (y - cy)**2)
        error = np.mean(np.abs(distances - radius))
        return (cx, cy), radius, error
    except:
        return None, None, float('inf')


# 🆕 v6.3: 노이즈에 강한 RANSAC 기반 원/호 피팅
def _fit_circle_3pts(p1, p2, p3):
    """3점을 지나는 원의 (cx, cy, r) 계산. 일직선이면 None."""
    ax, ay = float(p1[0]), float(p1[1])
    bx, by = float(p2[0]), float(p2[1])
    cx_, cy_ = float(p3[0]), float(p3[1])
    d = 2.0 * (ax * (by - cy_) + bx * (cy_ - ay) + cx_ * (ay - by))
    if abs(d) < 1e-10:
        return None
    ux = ((ax*ax + ay*ay) * (by - cy_) + (bx*bx + by*by) * (cy_ - ay) + (cx_*cx_ + cy_*cy_) * (ay - by)) / d
    uy = ((ax*ax + ay*ay) * (cx_ - bx) + (bx*bx + by*by) * (ax - cx_) + (cx_*cx_ + cy_*cy_) * (bx - ax)) / d
    r = math.hypot(ax - ux, ay - uy)
    return (ux, uy, r)


def fit_circle_ransac(pts, max_iter=80, inlier_tol=2.0, min_inlier_ratio=0.55, random_seed=42):
    """RANSAC으로 원/호 피팅 — 아웃라이어에 매우 강함.

    알고리즘:
      1) pts에서 무작위 3점 추출 → 원 방정식 구성
      2) 모든 점과 원의 거리 계산 → tol 이내면 inlier
      3) max_iter번 반복하여 inlier 개수가 가장 많은 모델 채택
      4) 채택된 inlier들로 algebraic fitting 재실행 (refine)

    Parameters
    ----------
    pts : np.ndarray (N, 2)
        후보 점들
    max_iter : int
        RANSAC 반복 횟수 (기본 80)
    inlier_tol : float
        inlier 판정 거리 임계값 (픽셀)
    min_inlier_ratio : float
        전체 점 중 inlier가 이 비율 이상이어야 유효
    random_seed : int
        재현성 위한 난수 시드

    Returns
    -------
    ((cx, cy), radius, error, inlier_count) | (None, None, inf, 0)
    """
    n = len(pts)
    if n < 6:
        return None, None, float('inf'), 0

    rng = np.random.default_rng(random_seed)
    best_inliers_mask = None
    best_inlier_count = 0
    best_model = None

    for _ in range(max_iter):
        # 3점 무작위 추출 (중복 없음)
        idx = rng.choice(n, size=3, replace=False)
        sample = pts[idx]
        model = _fit_circle_3pts(sample[0], sample[1], sample[2])
        if model is None:
            continue
        ux, uy, r = model
        # 반경이 너무 작거나 너무 크면 스킵 (이상치 방지)
        if r < 3.0 or r > 1e5:
            continue
        # 거리 계산
        dists = np.abs(np.sqrt((pts[:, 0] - ux)**2 + (pts[:, 1] - uy)**2) - r)
        inliers = dists <= inlier_tol
        cnt = int(np.count_nonzero(inliers))
        if cnt > best_inlier_count:
            best_inlier_count = cnt
            best_inliers_mask = inliers
            best_model = (ux, uy, r)

    if best_model is None or best_inlier_count < max(6, int(n * min_inlier_ratio)):
        return None, None, float('inf'), 0

    # inlier들만으로 algebraic fitting refine
    inlier_pts = pts[best_inliers_mask]
    center, radius, error = fit_circle_algebraic(inlier_pts)
    if center is None:
        # refine 실패 시 RANSAC 모델 그대로
        ux, uy, r = best_model
        return (ux, uy), r, inlier_tol, best_inlier_count
    return center, radius, error, best_inlier_count


def fit_circle_robust(pts, prefer_ransac_threshold=20, inlier_tol=2.0):
    """algebraic + RANSAC 자동 선택 wrapper.

    - 점 수가 threshold 미만이면 algebraic (빠름)
    - 그 이상이면 RANSAC 우선, 실패 시 algebraic fallback

    Returns
    -------
    ((cx, cy), radius, error)  — fit_circle_algebraic과 동일 시그니처
    """
    if len(pts) < prefer_ransac_threshold:
        return fit_circle_algebraic(pts)
    center, radius, error, n_in = fit_circle_ransac(pts, inlier_tol=inlier_tol)
    if center is None:
        return fit_circle_algebraic(pts)
    return center, radius, error


def merge_circles(circles, threshold=10):
    merged = []
    for c in circles:
        x, y, r = int(c[0]), int(c[1]), int(c[2])
        is_duplicate = False
        for m in merged:
            dist = np.hypot(x - m[0], y - m[1])
            if dist < threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            merged.append((x, y, r))
    return merged

def normalize_line_thickness(binary, target_thickness=2):
    """
    선 두께 정규화 (distanceTransform 기반)
    불균일한 선 두께를 균일하게 만들어 skeleton 품질을 높임.
    """
    if binary is None or binary.size == 0:
        return binary
    b = binary.astype(np.uint8)
    # 거리 변환: 각 픽셀에서 가장 가까운 배경(0)까지의 거리
    dist = cv2.distanceTransform(b, cv2.DIST_L2, 5)
    # 중심선 추출: 거리값이 target_thickness * 0.4 이상인 픽셀만 남김
    thresh_val = max(0.5, target_thickness * 0.4)
    _, center = cv2.threshold(dist, thresh_val, 255, cv2.THRESH_BINARY)
    center = center.astype(np.uint8)
    # 균일한 두께로 복원 (팽창)
    k = max(1, int(target_thickness))
    kernel = np.ones((k, k), np.uint8)
    return cv2.dilate(center, kernel, iterations=1)


# ══════════════════════════════════════════
#  🆕 v6.0: Auto-Clean 강화 — Deskew / Speckle / Gap Bridge
# ══════════════════════════════════════════

def deskew_image(img_gray, max_angle=15):
    """HoughLines 기반 기울기 자동 보정. (각도, 보정이미지) 반환."""
    edges = cv2.Canny(img_gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=max(50, min(img_gray.shape) // 8))
    if lines is None:
        return img_gray, 0.0
    angles = []
    for line in lines:
        rho, theta = line[0]
        angle = float(np.degrees(theta)) - 90.0
        if abs(angle) <= max_angle:
            angles.append(angle)
    if not angles:
        return img_gray, 0.0
    median_angle = float(np.median(angles))
    if abs(median_angle) < 0.3:
        return img_gray, 0.0
    h, w = img_gray.shape
    M = cv2.getRotationMatrix2D((w // 2, h // 2), median_angle, 1.0)
    rotated = cv2.warpAffine(img_gray, M, (w, h),
                              flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_REPLICATE)
    return rotated, median_angle


def remove_speckles(binary, min_area=20):
    """연결 성분 크기 기반 노이즈 점 제거 — min_area 미만 제거."""
    nb, output, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    result = np.zeros_like(binary)
    for i in range(1, nb):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            result[output == i] = 255
    return result


def bridge_gaps(binary, kernel_size=3):
    """morphologyEx CLOSE로 끊어진 선 미세 연결."""
    k = max(2, int(kernel_size))
    kernel = np.ones((k, k), np.uint8)
    return cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)


# ══════════════════════════════════════════
#  🪄 v6.1: 자동 CAD 정리 (Auto Cleanup) — 1순위 신규 기능
# ══════════════════════════════════════════

def orthogonalize_path(pts, ortho_threshold_deg=2.5, min_segment_pts=2):
    """
    Path 내 거의 수직/수평인 구간을 완전 수직/수평으로 보정.

    Parameters
    ----------
    pts : np.ndarray (N, 2)
        path 좌표 배열
    ortho_threshold_deg : float
        이 각도 이하(0±또는 90±)면 직교 정렬
    min_segment_pts : int
        직교 보정 대상 최소 점 수 (2 이하면 무의미). 점이 적어도 직선 path는 보정 가능.

    Returns
    -------
    np.ndarray (N, 2)
        보정된 path. 길이가 짧거나 직교 대상이 아니면 원본 그대로 반환.
    """
    if pts is None or len(pts) < min_segment_pts:
        return pts
    pts_arr = np.asarray(pts, dtype=np.float64)
    p1 = pts_arr[0]
    p2 = pts_arr[-1]
    dx, dy = float(p2[0] - p1[0]), float(p2[1] - p1[1])
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return pts

    # 전체 방향 각도 (도, 0~90 범위)
    angle = math.degrees(math.atan2(abs(dy), abs(dx)))

    is_horizontal = angle <= ortho_threshold_deg
    is_vertical   = angle >= (90.0 - ortho_threshold_deg)

    if not (is_horizontal or is_vertical):
        return pts

    # 곡선 여부 검증 (직선이 아니면 보정 금지) — 3점 이상이면 항상 검증
    if len(pts_arr) >= 3:
        v = np.array([dx, dy])
        v_norm = v / length
        mid_pts = pts_arr[1:-1]
        rel = mid_pts - p1
        proj = np.dot(rel, v_norm)
        proj_pts = p1 + np.outer(proj, v_norm)
        residuals = np.linalg.norm(mid_pts - proj_pts, axis=1)
        rms = float(np.sqrt(np.mean(residuals ** 2)))
        # 잔차가 path 길이의 2% 또는 2px 초과면 곡선으로 판단
        if rms > max(2.0, length * 0.02):
            return pts

    # 직교 보정 — 모든 점을 평균 좌표로 정렬 (직선이라고 판정했으므로)
    out = pts_arr.copy()
    if is_horizontal:
        y_avg = (p1[1] + p2[1]) / 2.0
        out[:, 1] = y_avg
    else:  # is_vertical
        x_avg = (p1[0] + p2[0]) / 2.0
        out[:, 0] = x_avg

    return out


def auto_cleanup_paths(paths, level="standard", img_diag_px=1000.0):
    """
    DXF 출력 직전 path 리스트에 통합 자동 후처리 적용 (1순위 신규 기능).

    적용 순서:
      1. 짧은 path 제거 (filter_short_paths 활용)
      2. 끊긴 path 연결 (stitch_close_paths + 방향 인식)
      3. 직교 보정 (orthogonalize_path)

    Parameters
    ----------
    paths : list of np.ndarray
        skeleton에서 추출된 path 리스트 (각 path: (N, 2) 배열)
    level : str
        "light"    — 보수적 (잡선만 제거, 직교 보정 약함)
        "standard" — 표준 (실무 권장 기본값)
        "strong"   — 적극적 (CAD 후편집 최소화 우선)
    img_diag_px : float
        이미지 대각선 픽셀 길이 (큰 이미지는 임계값 비례 증가)

    Returns
    -------
    cleaned_paths : list of np.ndarray
    stats : dict
        {"removed_short": int, "ortho_fixed": int, "input_count": int, "output_count": int}
    """
    if not paths:
        return [], {"removed_short": 0, "ortho_fixed": 0, "input_count": 0, "output_count": 0}

    # 레벨별 파라미터
    cfg = {
        "light":    {"min_len": 3.0,  "ortho_deg": 1.5, "stitch_gap": 2.0, "dir_thresh": 0.90},
        "standard": {"min_len": 5.0,  "ortho_deg": 2.5, "stitch_gap": 3.5, "dir_thresh": 0.80},
        "strong":   {"min_len": 8.0,  "ortho_deg": 4.0, "stitch_gap": 5.5, "dir_thresh": 0.70},
    }.get(level, {"min_len": 5.0, "ortho_deg": 2.5, "stitch_gap": 3.5, "dir_thresh": 0.80})

    # 이미지 크기 비례 보정
    scale_factor = max(1.0, img_diag_px / 1000.0)
    min_len = cfg["min_len"] * scale_factor
    stitch_gap = cfg["stitch_gap"] * scale_factor

    stats = {"removed_short": 0, "ortho_fixed": 0, "input_count": len(paths), "output_count": 0}

    # 1단계: 짧은 path 제거
    before = len(paths)
    filtered = filter_short_paths(paths, min_length_px=min_len)
    stats["removed_short"] = before - len(filtered)

    # 2단계: 끊긴 path 연결 (방향 인식 ON)
    stitched = stitch_close_paths(filtered, max_gap_px=stitch_gap, min_direction_cos=cfg["dir_thresh"])

    # 3단계: 직교 보정
    cleaned = []
    for p in stitched:
        p_arr = np.asarray(p)
        new_p = orthogonalize_path(p_arr, ortho_threshold_deg=cfg["ortho_deg"])
        # 보정 여부 판정 (서로 다른 객체이면서 좌표가 바뀌었는지)
        try:
            if new_p is not p_arr and new_p.shape == p_arr.shape and not np.array_equal(new_p, p_arr):
                stats["ortho_fixed"] += 1
        except Exception:
            pass
        cleaned.append(new_p)

    stats["output_count"] = len(cleaned)
    return cleaned, stats


# ══════════════════════════════════════════
#  📊 v6.1: 이미지 품질 자동 분석 — 2순위 신규 기능
# ══════════════════════════════════════════

def analyze_image_quality(img_bytes):
    """
    업로드 이미지의 변환 적합도를 자동 분석.

    분석 항목:
      - 해상도   (총 픽셀 수)        ── 0~30점
      - 선명도   (Laplacian 분산)    ── 0~30점
      - 노이즈   (median diff 비율)  ── 0~20점
      - 대비     (히스토그램 분산)   ── 0~20점

    Returns
    -------
    dict | None
        {
          "score": 0~100,
          "grade": "A"|"B"|"C"|"D",
          "color": "#xxxxxx",
          "label": str,
          "resolution": (w, h),
          "sharpness": float,
          "noise_ratio": float,
          "contrast": float,
          "issues": [warning_str, ...],
          "recommendations": [tip_str, ...],
          "auto_options": dict   # 추천 옵션 자동 적용용
        }
    """
    try:
        arr = np.asarray(bytearray(img_bytes), dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return None
    except Exception:
        return None

    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1) 해상도 점수 (0~30점)
    total_px = w * h
    if   total_px >= 2_000_000: res_score = 30
    elif total_px >= 1_000_000: res_score = 25
    elif total_px >=   500_000: res_score = 20
    elif total_px >=   250_000: res_score = 12
    else:                       res_score = 5

    # 2) 선명도 점수 (Laplacian variance, 0~30점)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    sharpness = float(lap.var())
    if   sharpness >= 500: sharp_score = 30
    elif sharpness >= 200: sharp_score = 25
    elif sharpness >= 100: sharp_score = 18
    elif sharpness >=  50: sharp_score = 10
    else:                  sharp_score = 3

    # 3) 노이즈 점수 (median diff, 0~20점)
    blurred = cv2.medianBlur(gray, 3)
    noise_map = cv2.absdiff(gray, blurred)
    noise_ratio = float(np.mean(noise_map > 8)) * 100.0  # 노이즈 픽셀 비율(%)
    if   noise_ratio <=  1.0: noise_score = 20
    elif noise_ratio <=  3.0: noise_score = 16
    elif noise_ratio <=  6.0: noise_score = 10
    elif noise_ratio <= 10.0: noise_score = 5
    else:                     noise_score = 0

    # 4) 대비 점수 (0~20점)
    contrast = float(gray.std())
    if   contrast >= 60: contrast_score = 20
    elif contrast >= 40: contrast_score = 16
    elif contrast >= 25: contrast_score = 10
    elif contrast >= 15: contrast_score = 5
    else:                contrast_score = 0

    total_score = int(res_score + sharp_score + noise_score + contrast_score)

    # 등급 결정
    if   total_score >= 85: grade, color, label = "A", "#16a34a", "변환 최상 — 후처리 거의 불필요"
    elif total_score >= 70: grade, color, label = "B", "#0078d4", "변환 양호 — 기본 설정 권장"
    elif total_score >= 50: grade, color, label = "C", "#f59e0b", "변환 보통 — 보정 옵션 권장"
    else:                   grade, color, label = "D", "#dc2626", "변환 어려움 — 강한 보정 필요"

    # 문제점 진단
    issues = []
    if total_px   < 500_000: issues.append(f"해상도 부족 ({w}×{h}px)")
    if sharpness  < 100:     issues.append(f"이미지 흐림 (선명도 {sharpness:.0f})")
    if noise_ratio > 5.0:    issues.append(f"노이즈 많음 ({noise_ratio:.1f}%)")
    if contrast   < 25:      issues.append(f"대비 부족 ({contrast:.0f})")

    # 추천 옵션
    recommendations = []
    auto_options = {}
    if sharpness < 200:
        recommendations.append("엣지 강화 ON")
        auto_options["opt_use_enhance"] = True
    if noise_ratio > 3.0:
        recommendations.append("노이즈 점 제거 ON")
        auto_options["v6_use_speckle"] = True
    if noise_ratio > 6.0:
        recommendations.append("끊어진 선 연결 ON")
        auto_options["v6_use_gap_bridge"] = True
    if contrast < 25:
        recommendations.append("선 두께 정규화 ON")
        auto_options["opt_use_normalize"] = True
    if total_score < 70:
        recommendations.append("자동 CAD 정리 ON")
        auto_options["v61_use_auto_cleanup"] = True
    if not recommendations:
        recommendations.append("기본 설정 그대로 변환하셔도 좋습니다")

    return {
        "score":           total_score,
        "grade":           grade,
        "color":           color,
        "label":           label,
        "resolution":      (w, h),
        "sharpness":       sharpness,
        "noise_ratio":     noise_ratio,
        "contrast":        contrast,
        "issues":          issues,
        "recommendations": recommendations,
        "auto_options":    auto_options,
    }


# ══════════════════════════════════════════
#  🆕 v6.0: 대시선 / 점선 자동 분류
# ══════════════════════════════════════════

def classify_line_type(path, binary_img, sample_n=50):
    """
    skeleton path를 따라 원본 binary에서 픽셀 ON/OFF 비율을 측정해
    선 종류를 분류합니다.
    반환: "SOLID" | "DASHED" | "CENTER" | "DOTTED"
    """
    if binary_img is None or len(path) < 4:
        return "SOLID"
    h, w = binary_img.shape[:2]
    step = max(1, len(path) // sample_n)
    sampled = path[::step]
    if len(sampled) < 4:
        return "SOLID"

    on_count = 0
    gap_runs = []
    cur_gap = 0
    in_gap = False

    for pt in sampled:
        px = int(round(float(pt[0]))); py = int(round(float(pt[1])))
        px = max(0, min(w - 1, px)); py = max(0, min(h - 1, py))
        is_on = binary_img[py, px] > 0
        if is_on:
            on_count += 1
            if in_gap:
                gap_runs.append(cur_gap); cur_gap = 0; in_gap = False
        else:
            cur_gap += 1; in_gap = True
    if in_gap and cur_gap > 0:
        gap_runs.append(cur_gap)

    total = len(sampled)
    on_ratio = on_count / total if total > 0 else 1.0

    if on_ratio >= 0.82:
        return "SOLID"
    if not gap_runs:
        return "SOLID"

    avg_gap = float(np.mean(gap_runs))

    # 중심선(일점쇄선): ON 비율 높고 짧은 갭
    if on_ratio >= 0.60 and avg_gap <= 3:
        return "CENTER"
    # 대시선: 규칙적 중간 갭
    if 0.35 <= on_ratio < 0.82 and avg_gap <= 7:
        return "DASHED"
    # 점선: 매우 짧은 ON 구간
    if on_ratio < 0.35:
        return "DOTTED"
    return "DASHED"


# ══════════════════════════════════════════
#  🆕 v6.0: 해치 패턴 인식
# ══════════════════════════════════════════

def detect_hatch_regions(paths, angle_tol=8.0, spacing_tol=12.0, min_lines=4):
    """
    서로 평행하고 일정 간격인 선 그룹을 해치 영역으로 분류합니다.
    반환: (hatch_groups, non_hatch_paths)
      hatch_groups = [{"path_indices": [...], "angle": float, "spacing": float}, ...]
      non_hatch_paths = [path, ...] 해치가 아닌 나머지
    """
    if len(paths) < min_lines:
        return [], paths

    path_angles = []
    path_centers = []
    for p in paths:
        if len(p) < 2:
            path_angles.append(None); path_centers.append(None); continue
        dx = float(p[-1][0] - p[0][0]); dy = float(p[-1][1] - p[0][1])
        angle = float(np.degrees(np.arctan2(dy, dx))) % 180.0
        path_angles.append(angle)
        path_centers.append((float(np.mean(p[:, 0])), float(np.mean(p[:, 1]))))

    used = set()
    hatch_groups = []

    for i in range(len(paths)):
        if i in used or path_angles[i] is None:
            continue
        ai = path_angles[i]
        group = [i]

        for j in range(i + 1, len(paths)):
            if j in used or path_angles[j] is None:
                continue
            aj = path_angles[j]
            diff = abs(ai - aj)
            if diff > 90: diff = 180.0 - diff
            if diff <= angle_tol:
                group.append(j)

        if len(group) < min_lines:
            continue

        # 수직 방향 투영 후 간격 일관성 검사
        perp_rad = np.radians(ai + 90.0)
        proj = [path_centers[idx][0] * np.cos(perp_rad) + path_centers[idx][1] * np.sin(perp_rad)
                for idx in group]
        proj_sorted = sorted(proj)
        spacings = [proj_sorted[k + 1] - proj_sorted[k] for k in range(len(proj_sorted) - 1)]
        spacings = [s for s in spacings if s > 1.0]
        if not spacings:
            continue
        avg_sp = float(np.mean(spacings))
        std_sp = float(np.std(spacings))
        if std_sp <= spacing_tol and avg_sp > 2.0:
            hatch_groups.append({"path_indices": group, "angle": ai, "spacing": avg_sp})
            used.update(group)

    non_hatch = [p for i, p in enumerate(paths) if i not in used]
    return hatch_groups, non_hatch


def add_dxf_linetypes(doc):
    """DXF 문서에 DASHED / CENTER / DOTTED 라인타입 등록."""
    lt = doc.linetypes
    try:
        if "DASHED2" not in lt:
            lt.add("DASHED2", [0.6, 0.4, -0.2], description="Dashed")
    except Exception:
        pass
    try:
        if "CENTER2" not in lt:
            lt.add("CENTER2", [1.0, 0.6, -0.2, 0.2, -0.2], description="Center line")
    except Exception:
        pass
    try:
        if "DOTTED2" not in lt:
            lt.add("DOTTED2", [0.2, -0.2], description="Dotted")
    except Exception:
        pass


# ══════════════════════════════════════════
#  🆕 v6.0: 래스터 오버레이 미리보기
# ══════════════════════════════════════════

def render_dxf_overlay_preview(img_bytes, dxf_bytes, raster_alpha=0.40,
                                bg_color="#1a1d2e", line_color="#e0e4ef"):
    """원본 래스터 이미지 + DXF 선을 겹쳐서 matplotlib Figure 반환."""
    arr = np.asarray(bytearray(img_bytes), dtype=np.uint8)
    img_cv = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img_cv is None:
        return None
    h_img, w_img = img_cv.shape[:2]
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

    fig, ax = plt.subplots(figsize=(10, max(3, 10 * h_img // max(w_img, 1))))
    ax.set_facecolor(bg_color); fig.patch.set_facecolor(bg_color)
    ax.imshow(img_rgb, extent=[0, w_img, 0, h_img], alpha=float(raster_alpha),
              aspect='auto', origin='upper')

    layer_colors = {
        "OUTLINE": "#e0e4ef", "HIDDEN": "#E24B4A", "CENTER": "#EF9F27",
        "CIRCLE": "#7ec8ff",  "HATCH":  "#5DCAA5", "PATTERN": "#9FE1CB",
        "Converted_Texts": "#FAC775",
    }
    try:
        doc_o = ezdxf.read(io.StringIO(dxf_bytes.decode("utf-8", errors="replace")))
        msp_o = doc_o.modelspace()
        for ent in msp_o:
            lyr = ent.dxf.layer if hasattr(ent.dxf, "layer") else "1"
            ec = layer_colors.get(lyr, line_color)
            try:
                if ent.dxftype() == "LINE":
                    x1, y1 = ent.dxf.start.x, ent.dxf.start.y
                    x2, y2 = ent.dxf.end.x, ent.dxf.end.y
                    ax.plot([x1, x2], [y1, y2], color=ec, lw=0.8, alpha=0.95)
                elif ent.dxftype() == "LWPOLYLINE":
                    pts = list(ent.get_points())
                    if len(pts) >= 2:
                        ax.plot([p[0] for p in pts], [p[1] for p in pts],
                                color=ec, lw=0.8, alpha=0.95)
                elif ent.dxftype() == "CIRCLE":
                    circle_patch = plt.Circle(
                        (ent.dxf.center.x, ent.dxf.center.y), ent.dxf.radius,
                        fill=False, color=ec, lw=0.8, alpha=0.95)
                    ax.add_patch(circle_patch)
                elif ent.dxftype() == "ARC":
                    a1 = np.radians(ent.dxf.start_angle)
                    a2 = np.radians(ent.dxf.end_angle)
                    if a2 < a1: a2 += 2 * np.pi
                    theta = np.linspace(a1, a2, 60)
                    r = ent.dxf.radius
                    ax.plot(ent.dxf.center.x + r * np.cos(theta),
                            ent.dxf.center.y + r * np.sin(theta),
                            color=ec, lw=0.8, alpha=0.95)
                elif ent.dxftype() == "SOLID":
                    pts_s = [(ent.dxf.vtx0.x, ent.dxf.vtx0.y),
                             (ent.dxf.vtx1.x, ent.dxf.vtx1.y),
                             (ent.dxf.vtx2.x, ent.dxf.vtx2.y),
                             (ent.dxf.vtx3.x, ent.dxf.vtx3.y)]
                    from matplotlib.patches import Polygon as MplPolygon
                    poly = MplPolygon(pts_s, closed=True, fill=True,
                                     facecolor=ec, alpha=0.25, edgecolor=ec, lw=0.5)
                    ax.add_patch(poly)
            except Exception:
                pass
    except Exception:
        pass

    ax.set_xlim(0, w_img); ax.set_ylim(0, h_img); ax.axis("off")
    plt.tight_layout(pad=0)
    return fig


# ══════════════════════════════════════════
#  🎯 v6.1: 누락선 강조 차이 비교 — 3순위 신규 기능
# ══════════════════════════════════════════

def render_diff_overlay_preview(img_bytes, dxf_bytes,
                                 bg_color="#ffffff",
                                 missing_color="#dc2626",  # 빨강 — 누락된 선 (원본에만 있음)
                                 extra_color="#06b6d4",    # 청록 — 추출된 선 (DXF에만 있음)
                                 common_color="#9ca3af",   # 회색 — 공통 선
                                 line_thickness=2,
                                 tolerance=3):
    """
    원본 이진화 이미지와 DXF 렌더링을 픽셀 단위로 비교해
    누락된 선(빨강), DXF에 추가된 선(청록), 공통 선(회색)을 시각화.

    실무 검수에 유용 — 빨강만 보고 보완 작업하면 됨.

    Parameters
    ----------
    img_bytes : bytes
        원본 이미지 바이트
    dxf_bytes : bytes
        변환된 DXF 바이트
    bg_color : str
        배경색 (실무에서는 흰색 배경이 가독성 최상)
    missing_color : str
        원본에는 있지만 DXF에는 없는 선 (= 누락선) 색
    extra_color : str
        DXF에는 있지만 원본에는 없는 선 (= 잘못 추가된 선) 색
    common_color : str
        둘 다 있는 선 (= 정상 추출) 색
    line_thickness : int
        DXF 라인 두께 (픽셀)
    tolerance : int
        선 매칭 허용 거리 (픽셀, dilate 커널 크기)

    Returns
    -------
    matplotlib Figure | None
    """
    try:
        arr = np.asarray(bytearray(img_bytes), dtype=np.uint8)
        img_cv = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img_cv is None:
            return None
    except Exception:
        return None

    h_img, w_img = img_cv.shape[:2]
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # 1) 원본 → 이진화 (선 = 흰색 픽셀 = 255)
    blurred = cv2.bilateralFilter(gray, 9, 75, 75)
    _, orig_bin = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 2) DXF → 같은 크기 이진 이미지로 렌더
    dxf_bin = np.zeros((h_img, w_img), dtype=np.uint8)
    try:
        doc_o = ezdxf.read(io.StringIO(dxf_bytes.decode("utf-8", errors="replace")))
        msp_o = doc_o.modelspace()
        # DXF 좌표는 mm 기반 + 좌상 → 좌하 flip. scale 추정.
        # scale은 보통 0.1 mm/px → 1 mm == 10 px
        # 좌표 변환: dxf_x → px_x = dxf_x / scale,  dxf_y → px_y = h_img - dxf_y / scale
        SCALE_GUESS = 0.1
        def dxf_to_px(x, y):
            px = int(round(x / SCALE_GUESS))
            py = int(round(h_img - y / SCALE_GUESS))
            return px, py

        for ent in msp_o:
            try:
                t = ent.dxftype()
                if t == "LINE":
                    p1 = dxf_to_px(ent.dxf.start.x, ent.dxf.start.y)
                    p2 = dxf_to_px(ent.dxf.end.x,   ent.dxf.end.y)
                    cv2.line(dxf_bin, p1, p2, 255, line_thickness)
                elif t == "LWPOLYLINE":
                    pts_d = list(ent.get_points())
                    if len(pts_d) >= 2:
                        pts_px = np.array([dxf_to_px(p[0], p[1]) for p in pts_d], dtype=np.int32)
                        cv2.polylines(dxf_bin, [pts_px], False, 255, line_thickness)
                elif t == "CIRCLE":
                    cx, cy = dxf_to_px(ent.dxf.center.x, ent.dxf.center.y)
                    r = int(round(ent.dxf.radius / SCALE_GUESS))
                    if r > 0:
                        cv2.circle(dxf_bin, (cx, cy), r, 255, line_thickness)
                elif t == "ARC":
                    cx, cy = dxf_to_px(ent.dxf.center.x, ent.dxf.center.y)
                    r = int(round(ent.dxf.radius / SCALE_GUESS))
                    a1 = float(ent.dxf.start_angle)
                    a2 = float(ent.dxf.end_angle)
                    if a2 < a1: a2 += 360.0
                    # cv2.ellipse는 angle을 시계방향 → DXF는 반시계방향. y축 flip 고려
                    cv2.ellipse(dxf_bin, (cx, cy), (r, r), 0, -a2, -a1, 255, line_thickness)
            except Exception:
                continue
    except Exception:
        return None

    # 3) 두 이진 이미지를 살짝 dilate해 매칭 허용 거리(tolerance) 확보
    k = max(1, int(tolerance))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    orig_dil = cv2.dilate(orig_bin, kernel, iterations=1)
    dxf_dil  = cv2.dilate(dxf_bin,  kernel, iterations=1)

    # 4) 분류 마스크 생성
    #    공통:    orig_bin & dxf_dil  (원본 픽셀 중 DXF 근처에 매칭됨)
    #    누락:    orig_bin & ~dxf_dil (원본에만 있고 DXF에는 없음) ★ 핵심!
    #    추가:    dxf_bin  & ~orig_dil (DXF에만 있고 원본에는 없음)
    common_mask  = (orig_bin > 0) & (dxf_dil > 0)
    missing_mask = (orig_bin > 0) & (dxf_dil == 0)
    extra_mask   = (dxf_bin  > 0) & (orig_dil == 0)

    # 5) 결과 RGB 이미지 합성
    def _hex_to_rgb(hx):
        hx = hx.lstrip("#")
        return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))
    bg_rgb      = _hex_to_rgb(bg_color)
    missing_rgb = _hex_to_rgb(missing_color)
    extra_rgb   = _hex_to_rgb(extra_color)
    common_rgb  = _hex_to_rgb(common_color)

    out = np.full((h_img, w_img, 3), bg_rgb, dtype=np.uint8)
    out[common_mask]  = common_rgb
    out[extra_mask]   = extra_rgb
    out[missing_mask] = missing_rgb  # 누락선은 마지막에 그려서 가장 잘 보이게

    # 6) 통계 산출
    n_orig    = int(np.count_nonzero(orig_bin))
    n_missing = int(np.count_nonzero(missing_mask))
    n_extra   = int(np.count_nonzero(extra_mask))
    n_common  = int(np.count_nonzero(common_mask))
    coverage = (n_common / n_orig * 100.0) if n_orig > 0 else 0.0
    miss_pct = (n_missing / n_orig * 100.0) if n_orig > 0 else 0.0

    # 7) matplotlib Figure 생성 (범례 포함)
    fig, ax = plt.subplots(figsize=(10, max(3, 10 * h_img // max(w_img, 1))))
    ax.set_facecolor(bg_color); fig.patch.set_facecolor(bg_color)
    ax.imshow(out, aspect='auto', origin='upper')
    ax.set_xlim(0, w_img); ax.set_ylim(h_img, 0); ax.axis("off")

    # 범례를 figure 상단에 표시
    from matplotlib.patches import Patch
    legend_elems = [
        Patch(facecolor=missing_color, edgecolor='none',
              label=f'누락 ({miss_pct:.1f}%)'),
        Patch(facecolor=extra_color,   edgecolor='none',
              label=f'추가'),
        Patch(facecolor=common_color,  edgecolor='none',
              label=f'정상 ({coverage:.1f}%)'),
    ]
    leg = ax.legend(handles=legend_elems, loc='upper right',
                    fontsize=9, framealpha=0.92, facecolor='#ffffff',
                    edgecolor='#cccccc', labelcolor='#1a3a5c')
    for text in leg.get_texts():
        text.set_fontweight('bold')

    plt.tight_layout(pad=0)
    # 통계 정보를 figure 속성으로 첨부 (UI에서 활용)
    fig._diff_stats = {
        "coverage_pct": float(coverage),
        "missing_pct": float(miss_pct),
        "n_orig": n_orig,
        "n_missing": n_missing,
        "n_extra": n_extra,
        "n_common": n_common,
    }
    return fig


def _force_line_color(ax, line_color):
    """
    matplotlib ax 안의 모든 아티스트 색상을 line_color로 강제 적용.
    흰 배경(White Paper)에서 선이 안 보이는 문제 해결용.
    """
    try:
        for line in ax.lines:
            line.set_color(line_color)
    except Exception:
        pass
    try:
        for collection in ax.collections:
            try:
                collection.set_edgecolors([line_color])
            except Exception:
                pass
            try:
                fc = collection.get_facecolor()
                # 완전 투명이 아닌 경우(채워진 영역)만 색상 적용
                if fc is not None and len(fc) > 0 and any(c[3] > 0.1 for c in fc):
                    collection.set_facecolors([line_color])
                else:
                    collection.set_facecolors([(0, 0, 0, 0)])
            except Exception:
                pass
    except Exception:
        pass
    try:
        for patch in ax.patches:
            patch.set_edgecolor(line_color)
            try:
                fc = patch.get_facecolor()
                if fc[3] > 0.1:
                    patch.set_facecolor(line_color)
            except Exception:
                pass
    except Exception:
        pass


def render_dxf_preview(dxf_bytes, bg_color="#1a1d2e", line_color="#e0e4ef"):
    """
    DXF 미리보기 렌더링.
    - Plotly 사용 가능 시: 인터랙티브 줌/패닝 Figure 반환
    - Plotly 미설치 시: matplotlib Figure 반환 (폴백)
    반환값: plotly Figure | matplotlib Figure | "EMPTY" | str(오류)
    """
    try:
        from ezdxf.addons.drawing import RenderContext, Frontend
        from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
        from ezdxf.addons.drawing.config import Configuration

        doc = ezdxf.read(io.StringIO(dxf_bytes.decode("utf-8")))
        msp = doc.modelspace()

        fig_mpl = plt.figure(figsize=(8, 8))
        ax = fig_mpl.add_axes([0, 0, 1, 1])
        ax.set_facecolor(bg_color)
        fig_mpl.patch.set_facecolor(bg_color)

        ctx = RenderContext(doc)
        try:
            config = Configuration.defaults()
            backend = MatplotlibBackend(ax)
            frontend = Frontend(ctx, backend, config=config)
        except TypeError:
            backend = MatplotlibBackend(ax)
            frontend = Frontend(ctx, backend)
        frontend.draw_layout(msp)
        ax.autoscale()

        try:
            bbox = ax.dataLim
            w_data = float(bbox.width)
            h_data = float(bbox.height)
            if w_data > 0 and h_data > 0:
                aspect = h_data / w_data
                BASE = 7.5
                if aspect >= 1.0:
                    new_h = BASE
                    new_w = max(BASE / aspect, 3.0)
                else:
                    new_w = BASE
                    new_h = max(BASE * aspect, 3.0)
                new_w = min(max(new_w, 3.0), 10.0)
                new_h = min(max(new_h, 3.0), 10.0)
                fig_mpl.set_size_inches(new_w, new_h)
                pad_x = w_data * 0.03
                pad_y = h_data * 0.03
                ax.set_xlim(bbox.x0 - pad_x, bbox.x1 + pad_x)
                ax.set_ylim(bbox.y0 - pad_y, bbox.y1 + pad_y)
        except Exception:
            pass

        ax.set_aspect("equal")
        ax.axis("off")

        has_content = (any(len(c.get_paths()) > 0 for c in ax.collections)
                       or len(ax.lines) > 0 or len(ax.patches) > 0)
        if not has_content:
            plt.close(fig_mpl)
            return "EMPTY"

        # ── 배경에 맞게 선 색상 강제 적용 ──
        _force_line_color(ax, line_color)

        # ── Plotly 래핑: 줌/패닝 활성화 ──
        if _PLOTLY_AVAILABLE and _PIL_AVAILABLE:
            try:
                buf = io.BytesIO()
                dpi = 150
                fig_mpl.savefig(buf, format="png", dpi=dpi,
                                bbox_inches="tight", facecolor=bg_color, pad_inches=0)
                buf.seek(0)
                pil_img = _PILImage.open(buf).convert("RGB")
                img_arr = np.array(pil_img)
                plt.close(fig_mpl)

                h_px, w_px = img_arr.shape[:2]
                plotly_fig = go.Figure(go.Image(z=img_arr))
                plotly_fig.update_layout(
                    margin=dict(l=0, r=0, t=0, b=0),
                    paper_bgcolor=bg_color,
                    plot_bgcolor=bg_color,
                    xaxis=dict(showgrid=False, showticklabels=False,
                               zeroline=False, range=[0, w_px]),
                    yaxis=dict(showgrid=False, showticklabels=False,
                               zeroline=False, range=[h_px, 0]),
                    dragmode="zoom",
                )
                plotly_fig._is_plotly = True
                return plotly_fig
            except Exception:
                pass  # Plotly 변환 실패 시 matplotlib Figure로 폴백

        return fig_mpl

    except Exception as e:
        return str(e)


# ══════════════════════════════════════════
#  🔬  Edge 강화 + KD-tree 중복선 제거
# ══════════════════════════════════════════

def _calc_adaptive_block_size(h, w):
    """🆕 v6.4 [개선 ①]: 이미지 해상도에 비례한 adaptiveThreshold blockSize 자동 계산.
    - 짧은 변의 약 1.5% 길이를 blockSize로 사용 (최소 11, 반드시 홀수)
    - 1000px 이미지 → ~15px, 2000px → ~31px, 4000px → ~61px
    - 고해상도 도면에서 선이 끊기는 현상 방지
    """
    short_side = min(int(h), int(w))
    bs = max(11, int(short_side * 0.015))
    if bs % 2 == 0:
        bs += 1
    return bs

def enhance_edge(img_gray, sharpen_strength=1.0):
    """🆕 v6.4 개선 ①②: blockSize 자동 + MORPH_CLOSE 추가 (미세 끊김 방지)"""
    if sharpen_strength > 0.01:
        blurred = cv2.GaussianBlur(img_gray, (0, 0), sigmaX=2.0)
        sharpened = cv2.addWeighted(img_gray, 1.0 + sharpen_strength, blurred,  -sharpen_strength, 0)
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
    else:
        sharpened = img_gray.copy()

    # 🆕 v6.4 [개선 ①]: blockSize를 해상도 기반으로 자동 계산 (기존: 고정 15)
    h_img, w_img = img_gray.shape[:2]
    block_size = _calc_adaptive_block_size(h_img, w_img)
    binary_adapt = cv2.adaptiveThreshold(
        sharpened, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
        blockSize=block_size, C=8
    )
    # 🆕 v6.4 [개선 ②]: OPEN → CLOSE 순서로 적용
    #   OPEN  : 작은 노이즈 점 제거
    #   CLOSE : 1~2px 미세하게 끊긴 선 자동 연결 (스캔 도면에 특히 효과)
    kernel_open  = np.ones((2, 2), np.uint8)
    kernel_close = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(binary_adapt, cv2.MORPH_OPEN,  kernel_open)
    cleaned = cv2.morphologyEx(cleaned,       cv2.MORPH_CLOSE, kernel_close)
    return cleaned

def remove_duplicate_paths(paths, merge_dist=3.0):
    if len(paths) <= 1: return paths
    endpoints = []
    for p in paths:
        sx, sy = float(p[0][0]),  float(p[0][1])
        ex, ey = float(p[-1][0]), float(p[-1][1])
        endpoints.append((sx, sy, ex, ey))

    starts = np.array([[e[0], e[1]] for e in endpoints])
    ends   = np.array([[e[2], e[3]] for e in endpoints])
    tree_s = KDTree(starts)
    tree_e = KDTree(ends)

    keep = [True] * len(paths)
    for i in range(len(paths)):
        if not keep[i]: continue
        sx, sy, ex, ey = endpoints[i]
        dup_fwd = set(tree_s.query_ball_point([sx, sy], r=merge_dist)) & set(tree_e.query_ball_point([ex, ey], r=merge_dist))
        dup_rev = set(tree_s.query_ball_point([ex, ey], r=merge_dist)) & set(tree_e.query_ball_point([sx, sy], r=merge_dist))
        for j in (dup_fwd | dup_rev):
            if j > i: keep[j] = False
    return [p for p, k in zip(paths, keep) if k]

def detect_patterns(circles, eps=30, min_samples=3):
    if not _DBSCAN_AVAILABLE or len(circles) < min_samples: return []
    pts = np.array([[float(x), float(y)] for x, y, r in circles])
    labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(pts)
    clusters = {}
    for i, label in enumerate(labels):
        if label == -1: continue
        clusters.setdefault(label, []).append(circles[i])
    return list(clusters.values()) if len(clusters) >= 2 else []

def detect_and_mask_circles(gray_img, binary, use_hough, circle_sens, circle_min_r, circle_max_r, max_circles):
    if not use_hough: return None, binary
    blurred = cv2.GaussianBlur(gray_img, (9, 9), 2)
    h_img, w_img = gray_img.shape
    img_short = min(h_img, w_img)
    auto_min_dist = max(20, img_short // 25)
    auto_max_r    = min(circle_max_r, img_short // 3)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=auto_min_dist, param1=120, param2=circle_sens, minRadius=circle_min_r, maxRadius=auto_max_r)
    if circles is None: return None, binary
    raw = np.uint16(np.around(circles))[0]
    if len(raw) > max_circles: raw = raw[:max_circles]
    cluster_threshold = max(8, img_short // 80)
    detected = merge_circles(raw, threshold=cluster_threshold)
    masked = binary.copy()
    for x, y, r in detected:
        cv2.circle(masked, (int(x), int(y)), int(r) + 2, 0, -1)
    return detected, masked

def preprocess_bytes(img_gray, image_type, threshold_val, masked_binary=None, use_enhance=False, sharpen_strength=1.0, use_normalize=False, normalize_thickness=2, use_deskew=False, use_speckle=False, min_speckle_area=20, use_gap_bridge=False, gap_bridge_size=3):
    # 🆕 v6.0: Deskew 기울기 보정 (이진화 전에 원본 gray에 적용)
    if use_deskew:
        img_gray, _ = deskew_image(img_gray)
    def _apply_clean(binary):
        if use_speckle:
            binary = remove_speckles(binary, min_area=int(min_speckle_area))
        if use_gap_bridge:
            binary = bridge_gaps(binary, kernel_size=int(gap_bridge_size))
        return binary
    if masked_binary is not None:
        binary = _apply_clean(masked_binary)
        if use_normalize:
            binary = normalize_line_thickness(binary, normalize_thickness)
        return skeletonize(binary > 0).astype(np.uint8) * 255

    if use_enhance:
        binary = _apply_clean(enhance_edge(img_gray, sharpen_strength))
        if use_normalize:
            binary = normalize_line_thickness(binary, normalize_thickness)
        return skeletonize(binary > 0).astype(np.uint8) * 255

    if image_type == "깔끔한 디지털 선화":
        _, binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((2, 2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    elif image_type in ("기계도면 - 사시도", "기계도면 - 정면도/단면도"):
        blurred = cv2.bilateralFilter(img_gray, 9, 75, 75)
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        img_eq = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(img_gray)
        img_eq = cv2.GaussianBlur(img_eq, (3, 3), 0)
        _, binary = cv2.threshold(img_eq, threshold_val, 255, cv2.THRESH_BINARY)
        if INVERT: binary = cv2.bitwise_not(binary)
    binary = _apply_clean(binary)
    if use_normalize:
        binary = normalize_line_thickness(binary, normalize_thickness)
    return skeletonize(binary > 0).astype(np.uint8) * 255

def extract_skeleton_paths(skeleton, min_points=4, min_bbox_area=30):
    h, w    = skeleton.shape
    skel    = skeleton > 0
    visited = np.zeros((h, w), dtype=bool)
    paths   = []
    ys, xs  = np.where(skel)
    pixels  = list(zip(ys.tolist(), xs.tolist()))
    if not pixels: return []

    def get_neighbors(y, x):
        return [(y+dy, x+dx) for dy, dx in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
                if 0 <= y+dy < h and 0 <= x+dx < w and skel[y+dy, x+dx]]

    start_order = [p for p in pixels if len(get_neighbors(*p)) <= 1]
    def trace(sy, sx):
        path, current = [(sy, sx)], (sy, sx)
        visited[sy, sx] = True
        while True:
            unvisited = [n for n in get_neighbors(*current) if not visited[n]]
            if not unvisited: break
            if len(path) >= 2:
                py, px = path[-2]
                dy, dx = current[0]-py, current[1]-px
                unvisited.sort(key=lambda n: -(dy*(n[0]-current[0]) + dx*(n[1]-current[1])))
            nxt = unvisited[0]
            visited[nxt] = True
            path.append(nxt)
            current = nxt
        return path

    for p in start_order + pixels:
        if not visited[p]:
            res = trace(*p)
            if len(res) < min_points: continue
            pts = np.array([[x, y] for y, x in res], dtype=float)
            x_range, y_range = np.ptp(pts[:, 0]), np.ptp(pts[:, 1])
            if (x_range * y_range) < min_bbox_area and x_range < 5 and y_range < 5: continue
            paths.append(pts)
    return paths

@st.cache_data(show_spinner=False)
def get_optimized_image_preview(img_bytes, image_type, t_val, use_enhance, sharpen_strength, use_normalize=False, normalize_thickness=2):
    arr = np.asarray(bytearray(img_bytes), dtype=np.uint8)
    img_color = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    img_gray  = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
    if use_enhance:
        binary = enhance_edge(img_gray, sharpen_strength)
    elif image_type == "깔끔한 디지털 선화":
        _, binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((2, 2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    elif image_type in ("기계도면 - 사시도", "기계도면 - 정면도/단면도"):
        blurred = cv2.bilateralFilter(img_gray, 9, 75, 75)
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        img_eq = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(img_gray)
        img_eq = cv2.GaussianBlur(img_eq, (3, 3), 0)
        _, binary = cv2.threshold(img_eq, t_val, 255, cv2.THRESH_BINARY)
        binary = cv2.bitwise_not(binary)
    if use_normalize:
        binary = normalize_line_thickness(binary, normalize_thickness)
    return cv2.bitwise_not(binary)

def convert_to_dxf_bytes(
    file_bytes, layer_name, image_type, use_ocr,
    t_val, s_tol, s_eps, s_den, s_win, epsilon,
    use_hough=False, circle_sens=70, circle_min_r=10, circle_max_r=300, max_circles=40,
    use_pattern=False, use_spline=False, use_geometry_fitting=False, user_scale=0.1,
    use_enhance=False, sharpen_strength=1.0, dedup_dist=3.0,
    use_line_fit=False, line_rms_thresh=1.5,
    use_angle_snap=False, snap_tol_deg=2.5,
    use_hough_lines=False, hough_min_len=40, hough_max_gap=8, hough_thresh=50,
    min_path_len=0.0, stitch_gap=0.0,
    use_normalize=False, normalize_thickness=2,
    # v5.0 신규 파라미터
    use_spur_prune=False, spur_max_len=8,
    use_corner_anchor=False, corner_angle_deg=40.0,
    use_dir_stitch=False, dir_stitch_thresh=0.7,
    # 🆕 v6.0 신규 파라미터
    use_deskew=False, use_speckle=False, min_speckle_area=20,
    use_gap_bridge=False, gap_bridge_size=3,
    use_dash_detect=False, use_layer_split=False,
    use_hatch_detect=False,
    # 🪄 v6.1 신규 파라미터
    use_auto_cleanup=False, cleanup_level="standard",
    # 🆕 v6.3 신규 파라미터
    use_super_resolution=True, sr_threshold_px=1500
):
    arr       = np.asarray(bytearray(file_bytes), dtype=np.uint8)
    img_color = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    # 🆕 v6.3: 저해상도일 때만 자동 Super-Resolution (사용자 토글 OFF면 스킵)
    _sr_applied = False
    if use_super_resolution and img_color is not None:
        img_color, _sr_applied = apply_super_resolution_auto(img_color, threshold_px=int(sr_threshold_px))

    h_orig, w_orig = img_color.shape[:2]
    img_gray  = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
    scale = float(user_scale) if user_scale and user_scale > 0 else SCALE

    report = {"circles": 0, "patterns": 0, "lines": 0, "texts": 0, "scale": scale, "warnings": [], "img_w": w_orig, "img_h": h_orig}
    if _sr_applied:
        report["warnings"].append(f"🤖 AI Super-Resolution 자동 적용 (x2 업스케일)")
        report["sr_applied"] = True

    text_data = []
    if use_ocr:
        results = load_ocr_model().readtext(img_color, width_ths=0.7)
        for (bbox, text, prob) in results:
            # 🆕 v6.3: 신뢰도 임계값 0.3 → 0.5 상향 (노이즈 오인식 차단)
            if prob > 0.5:
                text_data.append((text, bbox[0], bbox[2], float(prob)))
                cv2.rectangle(img_color, (int(bbox[0][0]), int(bbox[0][1])), (int(bbox[2][0]), int(bbox[2][1])), (255, 255, 255), -1)

    doc = ezdxf.new(dxfversion="R2010")
    msp = doc.modelspace()
    doc.layers.add(layer_name, color=7)
    doc.layers.add("CIRCLE",          color=1)
    doc.layers.add("PATTERN",         color=4)
    doc.layers.add("Converted_Texts", color=3)
    # 🆕 v6.0: 선 종류별 레이어 / 라인타입
    add_dxf_linetypes(doc)
    if "OUTLINE" not in doc.layers:
        doc.layers.add("OUTLINE", color=7)
    if "HIDDEN" not in doc.layers:
        lh = doc.layers.add("HIDDEN", color=1)
        try: lh.dxf.linetype = "DASHED2"
        except Exception: pass
    if "CENTER" not in doc.layers:
        lc2 = doc.layers.add("CENTER", color=2)
        try: lc2.dxf.linetype = "CENTER2"
        except Exception: pass
    if "HATCH" not in doc.layers:
        doc.layers.add("HATCH", color=3)

    _IS_MECH = image_type in ("기계도면 - 사시도", "기계도면 - 정면도/단면도")

    def _layer_for_type(ltype):
        """line type 문자열 → DXF 레이어명"""
        if not use_layer_split or not _IS_MECH:
            return layer_name
        return {"SOLID": "OUTLINE", "DASHED": "HIDDEN",
                "DOTTED": "HIDDEN", "CENTER": "CENTER"}.get(ltype, "OUTLINE")

    min_pts  = MIN_POINTS_MAP.get(image_type, 6)
    def to_pt(x, y): return (float(x) * scale, float(h_orig - y) * scale)

    if image_type == "기계도면 - 사시도" or image_type == "기계도면 - 정면도/단면도":
        # 🆕 v6.0: Deskew 적용
        _img_gray_proc = img_gray
        if use_deskew:
            _img_gray_proc, _dskw_angle = deskew_image(img_gray)
            if abs(_dskw_angle) >= 0.3:
                report["warnings"].append(f"기울기 보정: {_dskw_angle:+.1f}° 회전")
        else:
            _img_gray_proc = img_gray

        if use_enhance:
            binary_base = enhance_edge(_img_gray_proc, sharpen_strength)
        else:
            blurred = cv2.bilateralFilter(_img_gray_proc, 9, 75, 75)
            _, binary_base = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # 🆕 v6.0: Speckle 제거 + Gap Bridge
        if use_speckle:
            binary_base = remove_speckles(binary_base, min_area=int(min_speckle_area))
        if use_gap_bridge:
            binary_base = bridge_gaps(binary_base, kernel_size=int(gap_bridge_size))

        circles, masked_bin = detect_and_mask_circles(_img_gray_proc, binary_base, use_hough, circle_sens, circle_min_r, circle_max_r, max_circles)

        if circles is not None:
            for x, y, r in circles: msp.add_circle(to_pt(x, y), float(r) * scale, dxfattribs={"layer": "CIRCLE"})
            report["circles"] += len(circles)
            if use_pattern:
                patterns = detect_patterns(list(circles))
                for cluster in patterns:
                    for x, y, r in cluster: msp.add_circle(to_pt(x, y), float(r) * scale, dxfattribs={"layer": "PATTERN"})
                report["patterns"] += len(patterns)

        if use_hough_lines:
            hough_lines, masked_bin = extract_long_lines_hough(masked_bin, min_length=hough_min_len, max_gap=hough_max_gap, threshold=hough_thresh)
            for (p1, p2) in hough_lines:
                a, b = p1, p2
                if use_angle_snap: a, b = snap_angle(p1, p2, tolerance_deg=snap_tol_deg)
                msp.add_line(to_pt(a[0], a[1]), to_pt(b[0], b[1]), dxfattribs={"layer": layer_name})
                report["lines"] += 1
            report["warnings"].append(f"HoughLinesP 직선 추출: {len(hough_lines)}개")

        skeleton = skeletonize(masked_bin > 0).astype(np.uint8) * 255
        if use_normalize:
            masked_norm = normalize_line_thickness(masked_bin, normalize_thickness)
            skeleton = skeletonize(masked_norm > 0).astype(np.uint8) * 255
        # 🌟 v5.0: 잔가지(spur) 자동 제거
        if use_spur_prune:
            skel_before_pixels = int(np.count_nonzero(skeleton))
            skeleton = prune_skeleton_spurs(skeleton, max_spur_len=int(spur_max_len), max_iterations=3)
            skel_after_pixels = int(np.count_nonzero(skeleton))
            removed = skel_before_pixels - skel_after_pixels
            if removed > 0:
                report["warnings"].append(f"잔가지 제거: {removed}px 정리")
        paths    = extract_skeleton_paths(skeleton, min_pts)
        # 🌟 v5.0: 후처리 전 path 수 기록 (품질 점수 계산용)
        report["_path_raw"] = len(paths)

        if min_path_len > 0:
            before = len(paths); paths = filter_short_paths(paths, min_length_px=min_path_len)
            report["warnings"].append(f"짧은 path 제거: {before - len(paths)}개")
        if stitch_gap > 0:
            before = len(paths)
            # 🌟 v5.0: 방향인식 stitch 옵션
            _dir_thresh = float(dir_stitch_thresh) if use_dir_stitch else None
            paths = stitch_close_paths(paths, max_gap_px=stitch_gap, min_direction_cos=_dir_thresh)
            report["warnings"].append(f"path 이음: {before - len(paths)}개 병합")
        if dedup_dist > 0:
            before = len(paths); paths = remove_duplicate_paths(paths, merge_dist=dedup_dist)
            report["warnings"].append(f"중복선 제거: {before - len(paths)}개 제거됨")
        # 🌟 v5.0: 후처리 후 path 수 기록
        report["_path_clean"] = len(paths)

        # 🪄 v6.1: 자동 CAD 정리 (Auto Cleanup) — 1순위 신규 기능
        if use_auto_cleanup and paths:
            _diag_px = math.hypot(w_orig, h_orig)
            paths, _ac_stats = auto_cleanup_paths(paths, level=cleanup_level, img_diag_px=_diag_px)
            report["_auto_cleanup_stats"] = _ac_stats
            _msgs = []
            if _ac_stats["removed_short"] > 0:
                _msgs.append(f"잡선 {_ac_stats['removed_short']}개 제거")
            if _ac_stats["ortho_fixed"] > 0:
                _msgs.append(f"직교 {_ac_stats['ortho_fixed']}개 보정")
            if _msgs:
                report["warnings"].append("🪄 자동 CAD 정리: " + " · ".join(_msgs))

        # 🆕 v6.0: 해치 패턴 인식 (기계도면 전용)
        _hatch_report = 0
        if use_hatch_detect and _IS_MECH:
            hatch_groups, paths = detect_hatch_regions(paths, min_lines=4)
            for hg in hatch_groups:
                # 해치 영역을 SOLID 엔티티로 표현 (경계 박스 기준)
                hatch_pts_all = np.vstack([paths[idx] for idx in hg["path_indices"]
                                           if idx < len(paths)] if hg["path_indices"] else [np.array([[0,0]])])
                try:
                    hatch_pts_all = np.vstack([p for i, p in enumerate(paths)
                                               if i in set(hg["path_indices"])])
                    xmin, ymin = hatch_pts_all.min(axis=0)
                    xmax, ymax = hatch_pts_all.max(axis=0)
                    cx, cy = (xmin+xmax)/2, (ymin+ymax)/2
                    hw, hh = (xmax-xmin)/2, (ymax-ymin)/2
                    msp.add_solid([
                        to_pt(cx-hw, cy-hh), to_pt(cx+hw, cy-hh),
                        to_pt(cx-hw, cy+hh), to_pt(cx+hw, cy+hh)
                    ], dxfattribs={"layer": "HATCH"})
                    _hatch_report += 1
                except Exception:
                    pass
            if _hatch_report > 0:
                report["warnings"].append(f"해치 패턴 인식: {_hatch_report}개 영역")

        for p in paths:
            # 🆕 v6.0: 대시선 분류 (기계도면 전용)
            if use_dash_detect and _IS_MECH:
                _ltype = classify_line_type(p, masked_bin)
            else:
                _ltype = "SOLID"
            _target_layer = _layer_for_type(_ltype)

            # 🌟 v5.0: 코너 앵커링 (스무딩 전에 코너 검출 → 보존 스무딩)
            if use_corner_anchor and len(p) > 10:
                anchors = detect_corner_anchors(p, angle_threshold_deg=float(corner_angle_deg), min_segment_len=4)
                smoothed = smooth_path_with_anchors(p, s_win, anchors)
            else:
                smoothed = smooth_path(p, s_win)
            fitted_geom = False

            if use_line_fit and len(smoothed) >= 2:
                line_endpoints, rms = fit_line_least_squares(smoothed)
                if line_endpoints is not None and rms < line_rms_thresh:
                    p1, p2 = tuple(line_endpoints[0]), tuple(line_endpoints[1])
                    if use_angle_snap: p1, p2 = snap_angle(p1, p2, tolerance_deg=snap_tol_deg)
                    msp.add_line(to_pt(p1[0], p1[1]), to_pt(p2[0], p2[1]), dxfattribs={"layer": _target_layer})
                    report["lines"] += 1
                    fitted_geom = True

            if not fitted_geom and use_geometry_fitting and len(smoothed) > 10:
                # 🆕 v6.3: RANSAC 자동 선택 (20점 이상이면 RANSAC, 미만이면 algebraic)
                center, r, err = fit_circle_robust(smoothed, prefer_ransac_threshold=20, inlier_tol=2.0)
                arc_length = cv2.arcLength(smoothed.astype(np.float32), False)
                if arc_length == 0: arc_length = 1
                max_allowed_r = max(w_orig, h_orig) * 1.5
                if center is not None and err < 0.85 and r < max_allowed_r and r < (arc_length * 4):
                    p1, p2 = smoothed[0], smoothed[-1]
                    dist_ends = math.hypot(p1[0]-p2[0], p1[1]-p2[1])
                    if dist_ends < 5.0 and arc_length > 15:
                        msp.add_circle(to_pt(center[0], center[1]), r * scale, dxfattribs={"layer": "CIRCLE"})
                        report["circles"] += 1; fitted_geom = True
                    else:
                        dy1, dx1 = p1[1]-center[1], p1[0]-center[0]
                        dy2, dx2 = p2[1]-center[1], p2[0]-center[0]
                        ang1 = math.degrees(math.atan2(-dy1, dx1)) % 360
                        ang2 = math.degrees(math.atan2(-dy2, dx2)) % 360
                        angle_diff = abs(ang1 - ang2)
                        if angle_diff > 180: angle_diff = 360 - angle_diff
                        if angle_diff > 10.0:
                            msp.add_arc(to_pt(center[0], center[1]), r * scale, min(ang1, ang2), max(ang1, ang2), dxfattribs={"layer": _target_layer})
                            report["lines"] += 1; fitted_geom = True

            if not fitted_geom:
                if use_spline and len(smoothed) > 12:
                    step = max(1, len(smoothed) // 15)
                    sampled = smoothed[::step]
                    if not np.array_equal(sampled[-1], smoothed[-1]): sampled = np.vstack([sampled, smoothed[-1]])
                    try:
                        msp.add_spline(fit_points=[to_pt(x, y) for x, y in sampled], dxfattribs={"layer": _target_layer})
                    except Exception:
                        # 🆕 v6.4 [개선 ④]: adaptive epsilon  /  [개선 ③]: closed path 자동 인식
                        _eps_adj = _adaptive_epsilon(smoothed, s_eps)
                        sim = cv2.approxPolyDP(smoothed.reshape(-1, 1, 2).astype(np.float32), _eps_adj, False).reshape(-1, 2)
                        if len(sim) >= 2:
                            _add_lwpolyline_auto(msp, sim,
                                [to_pt(x, y) for x, y in sim],
                                dxfattribs={"layer": _target_layer})
                else:
                    # 🆕 v6.4 [개선 ④]: adaptive epsilon  /  [개선 ③]: closed path 자동 인식
                    _eps_adj = _adaptive_epsilon(smoothed, s_eps)
                    sim = cv2.approxPolyDP(smoothed.reshape(-1, 1, 2).astype(np.float32), _eps_adj, False).reshape(-1, 2)
                    if len(sim) >= 2:
                        _add_lwpolyline_auto(msp, sim,
                            [to_pt(x, y) for x, y in sim],
                            dxfattribs={"layer": _target_layer})
                report["lines"] += 1

    elif image_type == "깔끔한 디지털 선화":
        skeleton = preprocess_bytes(img_gray, image_type, t_val, use_enhance=use_enhance, sharpen_strength=sharpen_strength, use_normalize=use_normalize, normalize_thickness=normalize_thickness)
        # 🌟 v5.0: 잔가지 제거
        if use_spur_prune:
            sb = int(np.count_nonzero(skeleton))
            skeleton = prune_skeleton_spurs(skeleton, max_spur_len=int(spur_max_len), max_iterations=3)
            sa = int(np.count_nonzero(skeleton))
            if sb - sa > 0:
                report["warnings"].append(f"잔가지 제거: {sb - sa}px 정리")
        paths    = extract_skeleton_paths(skeleton, min_pts)
        report["_path_raw"] = len(paths)
        if dedup_dist > 0:
            before = len(paths); paths = remove_duplicate_paths(paths, merge_dist=dedup_dist)
            report["warnings"].append(f"중복선 제거: {before - len(paths)}개 제거됨")
        report["_path_clean"] = len(paths)
        # 🪄 v6.1: 자동 CAD 정리
        if use_auto_cleanup and paths:
            _diag_px = math.hypot(w_orig, h_orig)
            paths, _ac_stats = auto_cleanup_paths(paths, level=cleanup_level, img_diag_px=_diag_px)
            report.setdefault("_auto_cleanup_stats", _ac_stats)
            _msgs = []
            if _ac_stats["removed_short"] > 0: _msgs.append(f"잡선 {_ac_stats['removed_short']}개 제거")
            if _ac_stats["ortho_fixed"]    > 0: _msgs.append(f"직교 {_ac_stats['ortho_fixed']}개 보정")
            if _msgs: report["warnings"].append("🪄 자동 CAD 정리: " + " · ".join(_msgs))
        for p in paths:
            # 🌟 v5.0: 코너 앵커링
            if use_corner_anchor and len(p) > 10:
                anchors = detect_corner_anchors(p, angle_threshold_deg=float(corner_angle_deg), min_segment_len=4)
                smoothed = smooth_path_with_anchors(p, s_win, anchors)
            else:
                smoothed = smooth_path(p, s_win)
            # 🆕 v6.4 [개선 ④]: adaptive epsilon  /  [개선 ③]: closed path 자동 인식
            _eps_adj = _adaptive_epsilon(smoothed, s_eps)
            sim = cv2.approxPolyDP(smoothed.reshape(-1, 1, 2).astype(np.float32), _eps_adj, False).reshape(-1, 2)
            if len(sim) >= 2:
                _add_lwpolyline_auto(msp, sim,
                    [to_pt(x, y) for x, y in sim],
                    dxfattribs={"layer": layer_name})
            report["lines"] += 1

    elif image_type == "일반 이미지(풍성한 표현,두줄)":
        _, thresh = cv2.threshold(img_gray, t_val, 255, cv2.THRESH_BINARY_INV)
        if use_normalize:
            thresh = normalize_line_thickness(thresh, normalize_thickness)
        skeleton = skeletonize(thresh > 0).astype(np.uint8) * 255
        # 🌟 v5.0: 잔가지 제거
        if use_spur_prune:
            sb = int(np.count_nonzero(skeleton))
            skeleton = prune_skeleton_spurs(skeleton, max_spur_len=int(spur_max_len), max_iterations=3)
            sa = int(np.count_nonzero(skeleton))
            if sb - sa > 0:
                report["warnings"].append(f"잔가지 제거: {sb - sa}px 정리")
        paths = extract_skeleton_paths(skeleton, min_pts)
        report["_path_raw"] = len(paths)
        if dedup_dist > 0:
            before = len(paths); paths = remove_duplicate_paths(paths, merge_dist=dedup_dist)
            report["warnings"].append(f"중복선 제거: {before - len(paths)}개 제거됨")
        report["_path_clean"] = len(paths)
        # 🪄 v6.1: 자동 CAD 정리
        if use_auto_cleanup and paths:
            _diag_px = math.hypot(w_orig, h_orig)
            paths, _ac_stats = auto_cleanup_paths(paths, level=cleanup_level, img_diag_px=_diag_px)
            report.setdefault("_auto_cleanup_stats", _ac_stats)
            _msgs = []
            if _ac_stats["removed_short"] > 0: _msgs.append(f"잡선 {_ac_stats['removed_short']}개 제거")
            if _ac_stats["ortho_fixed"]    > 0: _msgs.append(f"직교 {_ac_stats['ortho_fixed']}개 보정")
            if _msgs: report["warnings"].append("🪄 자동 CAD 정리: " + " · ".join(_msgs))
        for p in paths:
            if use_corner_anchor and len(p) > 10:
                anchors = detect_corner_anchors(p, angle_threshold_deg=float(corner_angle_deg), min_segment_len=4)
                smoothed = smooth_path_with_anchors(p, s_win, anchors)
            else:
                smoothed = smooth_path(p, s_win)
            # 🆕 v6.4 [개선 ④]: adaptive epsilon  /  [개선 ③]: closed path 자동 인식
            _eps_adj = _adaptive_epsilon(smoothed, epsilon)
            sim = cv2.approxPolyDP(smoothed.reshape(-1, 1, 2).astype(np.float32), _eps_adj, False).reshape(-1, 2)
            if len(sim) >= 2:
                _add_lwpolyline_auto(msp, sim,
                    [to_pt(x, y) for x, y in sim],
                    dxfattribs={"layer": layer_name})
            report["lines"] += 1

    else:
        skeleton = preprocess_bytes(img_gray, image_type, t_val, use_enhance=use_enhance, sharpen_strength=sharpen_strength, use_normalize=use_normalize, normalize_thickness=normalize_thickness)
        # 🌟 v5.0: 잔가지 제거
        if use_spur_prune:
            sb = int(np.count_nonzero(skeleton))
            skeleton = prune_skeleton_spurs(skeleton, max_spur_len=int(spur_max_len), max_iterations=3)
            sa = int(np.count_nonzero(skeleton))
            if sb - sa > 0:
                report["warnings"].append(f"잔가지 제거: {sb - sa}px 정리")
        paths    = extract_skeleton_paths(skeleton, min_pts)
        report["_path_raw"] = len(paths)
        if dedup_dist > 0:
            before = len(paths); paths = remove_duplicate_paths(paths, merge_dist=dedup_dist)
            report["warnings"].append(f"중복선 제거: {before - len(paths)}개 제거됨")
        report["_path_clean"] = len(paths)
        # 🪄 v6.1: 자동 CAD 정리
        if use_auto_cleanup and paths:
            _diag_px = math.hypot(w_orig, h_orig)
            paths, _ac_stats = auto_cleanup_paths(paths, level=cleanup_level, img_diag_px=_diag_px)
            report.setdefault("_auto_cleanup_stats", _ac_stats)
            _msgs = []
            if _ac_stats["removed_short"] > 0: _msgs.append(f"잡선 {_ac_stats['removed_short']}개 제거")
            if _ac_stats["ortho_fixed"]    > 0: _msgs.append(f"직교 {_ac_stats['ortho_fixed']}개 보정")
            if _msgs: report["warnings"].append("🪄 자동 CAD 정리: " + " · ".join(_msgs))
        for p in paths:
            if use_corner_anchor and len(p) > 10:
                anchors = detect_corner_anchors(p, angle_threshold_deg=float(corner_angle_deg), min_segment_len=4)
                smoothed = smooth_path_with_anchors(p, s_win, anchors)
            else:
                smoothed = smooth_path(p, s_win)
            # 🆕 v6.4 [개선 ④]: adaptive epsilon  /  [개선 ③]: closed path 자동 인식
            _eps_adj = _adaptive_epsilon(smoothed, s_eps)
            sim = cv2.approxPolyDP(smoothed.reshape(-1, 1, 2).astype(np.float32), _eps_adj, False).reshape(-1, 2)
            if len(sim) >= 2:
                _add_lwpolyline_auto(msp, sim,
                    [to_pt(x, y) for x, y in sim],
                    dxfattribs={"layer": layer_name})
            report["lines"] += 1

    # 🆕 v6.3: OCR 결과를 MTEXT 엔티티로 (한글 멀티라인 + CAD 편집성)
    for _ocr_item in text_data:
        # backward-compat: 길이 3(레거시) / 4(v6.3 신뢰도 포함) 모두 대응
        if len(_ocr_item) == 4:
            text, tl, br, _prob = _ocr_item
        else:
            text, tl, br = _ocr_item
            _prob = 1.0
        try:
            _bbox_h = abs(br[1] - tl[1])
            _bbox_w = abs(br[0] - tl[0])
            _char_h = max(1.0, _bbox_h * scale * 0.8)
            _ins_x  = float(tl[0]) * scale
            _ins_y  = float(h_orig - br[1]) * scale
            mtext = msp.add_mtext(
                str(text),
                dxfattribs={
                    "layer": "Converted_Texts",
                    "char_height": _char_h,
                    "width": max(_char_h * len(str(text)) * 0.7, _bbox_w * scale),
                    "attachment_point": 7,  # 7 = Bottom Left
                }
            )
            mtext.set_location((_ins_x, _ins_y))
        except Exception:
            # MTEXT가 실패하면 안전하게 TEXT로 fallback (기존 동작 유지)
            msp.add_text(
                str(text),
                dxfattribs={"height": abs(br[1] - tl[1]) * scale * 0.8, "layer": "Converted_Texts"}
            ).set_placement((tl[0] * scale, (h_orig - br[1]) * scale))
    report["texts"] = len(text_data)

    # 🌟 v5.0: DXF 품질 점수 자동 계산
    _q = calculate_quality_score(
        report,
        path_count_raw=int(report.get("_path_raw", 0)),
        path_count_clean=int(report.get("_path_clean", 0)),
    )
    report["quality_score"] = _q["score"]
    report["quality_grade"] = _q["grade"]
    report["quality_breakdown"] = _q["breakdown"]

    out = io.StringIO()
    doc.write(out)
    return out.getvalue().encode("utf-8"), report

@st.cache_data(show_spinner=False)
def convert_for_preview(img_bytes, layer_name, image_type, use_ocr,
                        t_val, s_tol, s_eps, s_den, s_win, epsilon,
                        use_hough, circle_sens, circle_min_r, circle_max_r,
                        max_circles, use_pattern=False, use_spline=False,
                        use_geometry_fitting=False, user_scale=0.1,
                        use_enhance=False, sharpen_strength=1.0, dedup_dist=3.0,
                        use_line_fit=False, line_rms_thresh=1.5,
                        use_angle_snap=False, snap_tol_deg=2.5,
                        use_hough_lines=False, hough_min_len=40, hough_max_gap=8, hough_thresh=50,
                        min_path_len=0.0, stitch_gap=0.0,
                        use_normalize=False, normalize_thickness=2,
                        # v5.0 신규
                        use_spur_prune=False, spur_max_len=8,
                        use_corner_anchor=False, corner_angle_deg=40.0,
                        use_dir_stitch=False, dir_stitch_thresh=0.7,
                        # 🆕 v6.0 신규
                        use_deskew=False, use_speckle=False, min_speckle_area=20,
                        use_gap_bridge=False, gap_bridge_size=3,
                        use_dash_detect=False, use_layer_split=False,
                        use_hatch_detect=False,
                        # 🪄 v6.1 신규
                        use_auto_cleanup=False, cleanup_level="standard",
                        # 🆕 v6.3 신규
                        use_super_resolution=True, sr_threshold_px=1500):
    dxf_bytes, _ = convert_to_dxf_bytes(
        img_bytes, layer_name, image_type, use_ocr,
        t_val, s_tol, s_eps, s_den, s_win, epsilon,
        use_hough, circle_sens, circle_min_r, circle_max_r, max_circles,
        use_pattern, use_spline, use_geometry_fitting, user_scale,
        use_enhance, sharpen_strength, dedup_dist,
        use_line_fit, line_rms_thresh,
        use_angle_snap, snap_tol_deg,
        use_hough_lines, hough_min_len, hough_max_gap, hough_thresh,
        min_path_len, stitch_gap,
        use_normalize, normalize_thickness,
        use_spur_prune, spur_max_len,
        use_corner_anchor, corner_angle_deg,
        use_dir_stitch, dir_stitch_thresh,
        use_deskew, use_speckle, min_speckle_area,
        use_gap_bridge, gap_bridge_size,
        use_dash_detect, use_layer_split,
        use_hatch_detect,
        # 🪄 v6.1
        use_auto_cleanup, cleanup_level,
        # 🆕 v6.3
        use_super_resolution, sr_threshold_px
    )
    return dxf_bytes


# ══════════════════════════════════════════
#  📊  전역 통계 초기화 (사이드바+메인화면 공용 v4.2)
# ══════════════════════════════════════════
init_stats_db()
_uid = get_or_create_user_id()
st.session_state["user_id"] = _uid  # ⭐ v6.2: 사용자 프리셋 저장에 사용
if not st.session_state.get("_visit_recorded", False):
    record_visit(_uid)
    st.session_state["_visit_recorded"] = True
_stats = get_stats()
_chart_data = build_7day_chart_data(_stats["last_7days"])
_max_count = max([d["count"] for d in _chart_data]) if _chart_data else 1
_max_count = max(_max_count, 1)
_today_str = datetime.date.today().isoformat()
_bars_html = ""
_labels_dates = []
for _ci, _citem in enumerate(_chart_data):
    _cpct = (_citem["count"] / _max_count) * 100 if _max_count > 0 else 0
    _cpct = max(_cpct, 6) if _citem["count"] > 0 else 6
    _cbar_class = "mini-bar today" if (_citem["date"] == _today_str) else "mini-bar"
    _bars_html += (
        f'<div class="{_cbar_class}" style="height:{_cpct:.1f}%"' +
        f' title="{_citem["date"]}: {_citem["count"]}건"></div>'
    )
    try:
        _labels_dates.append(_citem["date"][5:])
    except Exception:
        _labels_dates.append(_citem["date"])

# ══════════════════════════════════════════
#  🌐  사이드바
# ══════════════════════════════════════════

# 🆕 v6.8: 앱 시작 시 config.json 자동 로드 (ODA·AutoCAD 경로 복원)
_load_config()

with st.sidebar:
    # ── DXF 변환 옵션 헤더 ──
    st.markdown("""
    <div class="sb-compact-header" style="margin-top:-16px !important;">
        <div class="sb-title">📐 DXF 변환 옵션</div>
        <div class="sb-subtitle">★ 웹배포본 · CLEAN-FILENAME · v6.9</div>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════
    # 🌟 v4.2: 변환이력 (사이드바 최상단)
    # ══════════════════════════════════════
    with st.expander("📜 변환 이력 (최근 15건)", expanded=False):
        _sb_history = get_recent_conversions(_uid, limit=15)
        if not _sb_history:
            st.markdown("<div style='font-size:0.78rem;color:#7a8fa6;text-align:center;padding:10px 0;'>아직 변환 이력이 없습니다.</div>", unsafe_allow_html=True)
        else:
            _sb_rows = ""
            for _sbh in _sb_history:
                _sbt = _sbh["time"][11:16] if len(_sbh["time"]) >= 16 else _sbh["time"]
                _sbd = _sbh["date"][5:] if len(_sbh["date"]) >= 10 else _sbh["date"]
                _sbft = f"{_sbd} {_sbt}"
                _sbts = _sbh["type"].replace("기계도면 - ","").replace("일반 이미지","일반").replace("(","").replace(")","")
                if len(_sbts) > 18: _sbts = _sbts[:18] + "…"
                _sbic = "✅" if _sbh["success"] else "❌"
                _sb_rows += (
                    f"<div class='history-row'>"
                    f"<span style='font-size:0.85rem'>{_sbic}</span>"
                    f"<span class='history-time'>{_sbft}</span>"
                    f"<span class='history-mode'>{_sbts}</span>"
                    f"<span class='history-count'>{_sbh['count']}건</span>"
                    f"</div>"
                )
            st.markdown(_sb_rows, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # 🆕 v6.5: DWG/AutoCAD 자동 연동 설정 (사이드바)
    # ══════════════════════════════════════════════════════════════
    with st.expander("🔧 DWG / AutoCAD 자동 연동 (v6.5 ★)", expanded=False):
        if not _IS_WINDOWS:
            st.info(
                "🌐 **웹 배포본 안내**\n\n"
                "DWG 자동 변환과 AutoCAD 자동 후처리는 **Windows 로컬 환경 전용**입니다.\n\n"
                "현재 이 앱은 **Linux 서버**에서 실행 중이므로 모든 결과가 **DXF 파일**로 제공됩니다.\n\n"
                "👉 **DXF는 AutoCAD에서 정상적으로 열립니다.** AutoCAD에서 DWG로 다시 저장하시면 됩니다.\n\n"
                "💡 DWG 자동 변환이 꼭 필요하시면 로컬 Windows에서 Auto_Web.py를 직접 실행해주세요."
            )
        else:
            st.markdown(
                "<div style='font-size:0.72rem;color:#5a7a96;margin-bottom:6px;line-height:1.4;'>"
                "✨ DXF를 <b>DWG로 자동 변환</b>하고, AutoCAD를 자동 실행해서 "
                "<b>중복선 제거(OVERKILL) + 폴리라인 결합(PEDIT JOIN)</b>까지 한 번에 처리합니다.<br>"
                "사용 전에 ODA File Converter (무료) 또는 AutoCAD가 설치되어 있어야 합니다."
                "</div>",
                unsafe_allow_html=True
            )

            # 1) ODA File Converter (DWG 변환용)
            st.markdown("**📦 ODA File Converter (DWG 변환)**")
            _oda_auto = find_oda_converter("")
            if _oda_auto:
                st.success(f"✅ 자동 발견: `{os.path.basename(_oda_auto)}`")
                st.caption(f"📁 {_oda_auto}")
                # 🆕 v6.8: 자동 발견 시 session_state + config 모두 갱신
                if st.session_state.get("v65_oda_path") != _oda_auto:
                    st.session_state["v65_oda_path"] = _oda_auto
                    _save_config()
            else:
                st.info(
                    "ℹ️ ODA File Converter가 자동 발견되지 않았습니다.\n\n"
                    "👉 무료 다운로드: https://www.opendesign.com/guestfiles/oda_file_converter"
                )
                _oda_manual = st.text_input(
                    "🔍 ODA 경로 직접 지정 (폴더 또는 exe 파일)",
                    value=st.session_state.get("v65_oda_path", ""),
                    placeholder=r"예: C:\Program Files\ODA\ODAFileConverter 27.1.0",
                    key="v65_oda_path_input",
                    help=(
                        "폴더 경로만 입력해도 됩니다 — ODAFileConverter.exe를 자동으로 찾습니다.\n"
                        r"예시: C:\Program Files\ODA\ODAFileConverter 27.1.0"
                    )
                )
                if _oda_manual:
                    # 🆕 v6.7: 폴더 입력 시 exe 자동 보정
                    _resolved = find_oda_converter(_oda_manual)
                    if _resolved:
                        st.session_state["v65_oda_path"] = _resolved
                        st.success(f"✅ 경로 인식됨: `{_resolved}`")
                    else:
                        # exe를 직접 붙여도 없으면 구체적 안내
                        _exe_guess = os.path.join(_oda_manual.strip().strip('"'), "ODAFileConverter.exe")
                        st.error(
                            f"❌ ODAFileConverter.exe를 찾을 수 없습니다.\n\n"
                            f"확인 경로: `{_exe_guess}`\n\n"
                            f"💡 파일 탐색기에서 **ODAFileConverter.exe** 파일을 찾아서\n"
                            f"그 파일까지의 전체 경로를 붙여넣으세요."
                        )

            # 2) DWG 출력 버전 선택
            _dwg_ver_label = st.selectbox(
                "📐 DWG 출력 버전",
                list(_ODA_VERSION_MAP.keys()),
                index=0,
                key="v65_dwg_version",
                help="대상 AutoCAD 버전에 맞춰 선택하세요. 일반적으로 2018 (R2018)을 추천합니다."
            )
            st.session_state["v65_dwg_version_code"] = _ODA_VERSION_MAP[_dwg_ver_label]

            # 🆕 v6.7: 출력 형식 라디오는 메인 화면 변환 버튼 위로 이동됨
            #         (사이드바 안 열어도 보이도록)

            st.markdown("---")

            # 3) AutoCAD 실행파일 (자동 후처리용)
            st.markdown("**🅰️ AutoCAD 실행파일 (자동 후처리)**")
            _acad_auto = find_autocad_exe("")
            if _acad_auto:
                st.success(f"✅ 자동 발견: `{os.path.basename(_acad_auto)}`")
                st.caption(f"📁 {_acad_auto}")
                # 🆕 v6.8: 자동 발견 시 session_state + config 모두 갱신
                if st.session_state.get("v65_acad_path") != _acad_auto:
                    st.session_state["v65_acad_path"] = _acad_auto
                    _save_config()
            else:
                _acad_manual = st.text_input(
                    "🔍 AutoCAD 경로 직접 지정 (폴더 또는 exe 파일)",
                    value=st.session_state.get("v65_acad_path", ""),
                    placeholder=r"예: C:\Program Files\Autodesk\AutoCAD 2027",
                    key="v65_acad_path_input",
                    help=(
                        "폴더 경로만 입력해도 됩니다 — acad.exe를 자동으로 찾습니다.\n"
                        r"예시: C:\Program Files\Autodesk\AutoCAD 2027"
                    )
                )
                if _acad_manual:
                    # 🆕 v6.8: ODA와 동일하게 폴더 입력 시 exe 자동 보정
                    _resolved_acad = find_autocad_exe(_acad_manual)
                    if _resolved_acad:
                        st.session_state["v65_acad_path"] = _resolved_acad
                        _save_config()
                        st.success(f"✅ 경로 인식됨: `{_resolved_acad}`")
                    else:
                        _exe_guess = os.path.join(_acad_manual.strip().strip('"'), "acad.exe")
                        st.error(
                            f"❌ acad.exe를 찾을 수 없습니다.\n\n"
                            f"확인 경로: `{_exe_guess}`\n\n"
                            f"💡 파일 탐색기에서 **acad.exe** 파일을 찾아서\n"
                            f"그 파일까지의 전체 경로를 붙여넣으세요."
                        )

            # 4) 자동 후처리 옵션 (SCR 스크립트 옵션)
            st.markdown("**⚙️ AutoCAD 자동 정리 옵션 (SCR)**")
            st.session_state.setdefault("v65_use_overkill",    True)
            st.session_state.setdefault("v65_use_pedit_join",  True)
            st.session_state.setdefault("v65_use_zoom_extents",True)
            st.session_state.setdefault("v65_use_purge",       False)
            st.session_state.setdefault("v65_auto_save",       True)

            st.toggle("🔁 OVERKILL (중복선 자동 제거)",   key="v65_use_overkill",
                      help="겹치거나 중복된 선을 AutoCAD가 자동으로 정리합니다. ⚠️ AutoCAD 풀버전 전용 (LT는 미지원).")
            st.toggle("🔗 PEDIT JOIN (분리선 자동 결합)", key="v65_use_pedit_join",
                      help="끊어진 라인/폴리라인을 자동으로 하나의 polyline으로 결합합니다.")
            st.toggle("🔍 ZOOM EXTENTS (도면 전체보기)",  key="v65_use_zoom_extents",
                      help="파일을 연 직후 도면 전체가 보이도록 자동 확대.")
            st.toggle("🗑️ PURGE (사용 안하는 객체 제거)", key="v65_use_purge",
                      help="블록·레이어·라인타입 등 미사용 객체를 자동 정리.")
            st.toggle("💾 자동 저장 (QSAVE)",              key="v65_auto_save",
                      help="자동 정리 완료 후 파일을 자동으로 저장합니다.")

            # 🆕 v6.8: 경로 설정 영구 저장 버튼
            st.markdown("---")
            st.markdown(
                "<div style='font-size:0.72rem;color:#5a7a96;margin-bottom:6px;'>"
                "💾 경로 설정을 저장하면 앱을 껐다 켜도 자동으로 불러옵니다."
                "</div>",
                unsafe_allow_html=True
            )
            if st.button("💾 ODA·AutoCAD 경로 설정 저장",
                         use_container_width=True, type="primary",
                         key="v68_save_config_btn",
                         help="ODA 경로, AutoCAD 경로, DWG 버전, SCR 옵션을 config.json에 저장합니다."):
                if _save_config():
                    st.success(
                        f"✅ 설정이 저장되었습니다!\n\n"
                        f"📁 `{os.path.basename(_CONFIG_PATH)}`\n\n"
                        f"이제 앱을 껐다 켜도 경로 설정이 자동으로 유지됩니다."
                    )
                else:
                    st.error(f"❌ 저장 실패. 경로 확인: `{_CONFIG_PATH}`")

    # ══════════════════════════════════════
    # 🌟 v4.2: 설정저장/불러오기 (사이드바 최상단)
    # ══════════════════════════════════════
    with st.expander("💾 설정 저장/불러오기", expanded=False):
        st.markdown("<div style='font-size:0.74rem;color:#5a7a96;margin-bottom:6px;line-height:1.4;'>현재 슬라이더 값과 토글 상태를 JSON 파일로 내보내거나 불러올 수 있어요.</div>", unsafe_allow_html=True)
        # session_state에서 현재 값 수집 (슬라이더보다 먼저 렌더링되므로 세션 참조)
        _top_flags = {
            "use_ocr":              st.session_state.get("opt_use_ocr", False),
            "use_enhance":          st.session_state.get("opt_use_enhance", False),
            "use_dedup":            st.session_state.get("opt_use_dedup", False),
            "USE_LINE_FIT":         st.session_state.get("v6_use_line_fit", False),
            "USE_GEOMETRY_FITTING": st.session_state.get("v7_use_geom_fit", False),
            "USE_HOUGH_LINES":      st.session_state.get("v6_use_hough_lines", False),
            "USE_ANGLE_SNAP":       st.session_state.get("v6_use_angle_snap", False),
            # 🌟 v5.0
            "USE_SPUR_PRUNE":       st.session_state.get("v5_use_spur_prune", False),
            "USE_CORNER_ANCHOR":    st.session_state.get("v5_use_corner_anchor", False),
            "USE_DIR_STITCH":       st.session_state.get("v5_use_dir_stitch", False),
            "USE_CROP":             st.session_state.get("v5_use_crop", False),
            # 🆕 v6.0
            "USE_DESKEW":           st.session_state.get("v6_use_deskew", False),
            "USE_SPECKLE":          st.session_state.get("v6_use_speckle", False),
            "USE_GAP_BRIDGE":       st.session_state.get("v6_use_gap_bridge", False),
            "USE_DASH_DETECT":      st.session_state.get("v6_use_dash_detect", False),
            "USE_LAYER_SPLIT":      st.session_state.get("v6_use_layer_split", False),
            "USE_HATCH_DETECT":     st.session_state.get("v6_use_hatch_detect", False),
            "USE_SPLINE_V6":        st.session_state.get("v6_use_spline", False),
            # 🪄 v6.1
            "USE_AUTO_CLEANUP":     st.session_state.get("v61_use_auto_cleanup", False),
        }
        _top_sliders = {k: st.session_state.get(k) for k in [
            "sl_eps","sl_smooth","sl_threshold","sl_straight","sl_spline",
            "sl_epsilon","sl_sharpen","sl_dedup","v6_line_rms","v6_hough_min",
            "v6_hough_thr","v6_hough_gap","v6_snap_tol","v6_min_path_len","v6_stitch_gap",
            # 🌟 v5.0
            "v5_spur_max_len","v5_corner_angle","v5_dir_stitch_thresh",
            "v5_crop_top","v5_crop_bot","v5_crop_left","v5_crop_right",
            # 🆕 v6.0
            "v6_min_speckle","v6_gap_size"
        ]}
        _top_itype = st.session_state.get("_prev_image_type", "기계도면 - 사시도")
        _top_bytes = export_settings_json(_top_itype, "1", 0.1, _top_flags, _top_sliders)
        _top_fname = f"DXF설정_{_top_itype.replace(' ','_').replace('/','_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        st.download_button(
            label="📥 현재 설정 내보내기 (JSON)",
            data=_top_bytes,
            file_name=_top_fname,
            mime="application/json",
            use_container_width=True,
            key="dl_settings_top"
        )
        st.markdown("<div style='margin:6px 0;border-top:1px solid #e1e7ef'></div>", unsafe_allow_html=True)
        _top_loaded = st.file_uploader(
            "설정 파일 불러오기",
            type=["json"],
            label_visibility="collapsed",
            key="settings_uploader_top",
            help="이전에 내보낸 JSON 설정 파일을 올리면 슬라이더가 자동으로 채워집니다."
        )
        if _top_loaded is not None:
            if st.button("📤 이 파일로 설정 적용", use_container_width=True, key="apply_settings_top_btn"):
                _tdata, _terr = import_settings_json(_top_loaded.getvalue())
                if _terr:
                    st.error(f"❌ {_terr}")
                else:
                    for k, v in _tdata.get("sliders", {}).items():
                        if v is not None:
                            st.session_state[k] = v
                    st.success(f"✅ 설정 불러오기 완료! (저장시각: {_tdata.get('saved_at','알 수 없음')})")
                    st.rerun()

    # 파일을 올리기 전 안내
    if not st.session_state.get("main_uploader"):
        st.info("👈 메인 화면에서 변환할 이미지를 먼저 업로드하시면,\n이곳에서 최적화 및 변환 옵션을 자유롭게 조정하실 수 있습니다.")

    st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

    st.markdown("<div class='sb-section-label'>🛠️ 도면 종류</div>", unsafe_allow_html=True)

    image_type = st.selectbox(
        "🛠 도면 종류",
        (
            "기계도면 - 사시도", "기계도면 - 정면도/단면도", "깔끔한 디지털 선화",
            "일반 이미지(간략한 표현,한줄)", "일반 이미지(풍성한 표현,두줄)"
        ),
        label_visibility="collapsed",
        help="입력 이미지에 가장 적합한 변환 모드를 선택하세요."
    )

    # 도면 종류 변경 시 자동 프리셋 적용
    _prev_image_type = st.session_state.get("_prev_image_type", None)
    if _prev_image_type != image_type:
        st.session_state["_prev_image_type"] = image_type
        if image_type == "일반 이미지(간략한 표현,한줄)":
            _apply_preset_callback(image_type, "진한선 🖊️", PRESETS["일반 이미지(간략한 표현,한줄)"]["진한선 🖊️"])
        elif image_type == "일반 이미지(풍성한 표현,두줄)":
            _apply_preset_callback(image_type, "세밀 🔬", PRESETS["일반 이미지(풍성한 표현,두줄)"]["세밀 🔬"])

    # ══════════════════════════════════════════════════════════
    # 🆕 v6.4 [UI 개선 ⑥]: 퀵 변환 3단계 버튼 (빠름 / 균형 / 정밀)
    # ══════════════════════════════════════════════════════════
    st.markdown("<div class='sb-section-label' style='margin-top:8px;'>⚡ 퀵 변환 (v6.4)</div>", unsafe_allow_html=True)
    _q_cols = st.columns(3, gap="small")
    _active_quick = st.session_state.get("v64_active_quick", None)

    def _apply_quick_v64(mode):
        """⚡ 빠름 / ⚖️ 균형 / 🔬 정밀 — 자주 쓰는 슬라이더 조합을 한 번에 적용.
        기존 슬라이더 값을 session_state로 직접 덮어쓰므로 어떤 도면 종류에서도 동작."""
        if mode == "fast":
            _vals = {
                "sl_eps":      2.0,   # 곡선 단순화 강하게 → 노드 적게, 처리 빠름
                "sl_smooth":   5,     # 스무딩 약하게
                "sl_epsilon":  2.0,
                "sl_threshold":127,
                "sl_straight": 8.0,
                "sl_spline":   80,
                "sl_sharpen":  0.8,
            }
        elif mode == "precise":
            _vals = {
                "sl_eps":      0.5,   # 곡선 단순화 약하게 → 원본에 가까운 정밀선
                "sl_smooth":   11,    # 스무딩 강하게 → 매끄러운 곡선
                "sl_epsilon":  0.5,
                "sl_threshold":127,
                "sl_straight": 3.0,
                "sl_spline":   150,
                "sl_sharpen":  1.3,
            }
        else:  # balanced
            _vals = {
                "sl_eps":      1.2,
                "sl_smooth":   7,
                "sl_epsilon":  1.2,
                "sl_threshold":127,
                "sl_straight": 5.0,
                "sl_spline":   120,
                "sl_sharpen":  1.0,
            }
        for k, v in _vals.items():
            st.session_state[k] = v
        st.session_state["v64_active_quick"] = mode

    with _q_cols[0]:
        _btn_t = "primary" if _active_quick == "fast" else "secondary"
        st.button("⚡ 빠름", key="v64_quick_fast", use_container_width=True, type=_btn_t,
                  help="처리 속도 우선 (단순화 강함, 스무딩 약함). 빠른 검토용 변환에 적합.",
                  on_click=_apply_quick_v64, args=("fast",))
    with _q_cols[1]:
        _btn_b = "primary" if _active_quick == "balanced" else "secondary"
        st.button("⚖️ 균형", key="v64_quick_balanced", use_container_width=True, type=_btn_b,
                  help="속도와 품질의 균형 (실무 기본 권장값).",
                  on_click=_apply_quick_v64, args=("balanced",))
    with _q_cols[2]:
        _btn_p = "primary" if _active_quick == "precise" else "secondary"
        st.button("🔬 정밀", key="v64_quick_precise", use_container_width=True, type=_btn_p,
                  help="원본에 최대한 가깝게 변환 (단순화 약함, 스무딩 강함, 노드 多). 처리 시간 ↑",
                  on_click=_apply_quick_v64, args=("precise",))

    layer_name = "1"
    USER_SCALE = 0.1

    USE_HOUGH = False
    USE_PATTERN = False
    USE_SPLINE = False
    USE_GEOMETRY_FITTING = False
    # 🆕 v6.0 기본값
    USE_DESKEW       = False
    USE_SPECKLE      = False
    MIN_SPECKLE_AREA = 20
    USE_GAP_BRIDGE   = False
    GAP_BRIDGE_SIZE  = 3
    USE_DASH_DETECT  = False
    USE_LAYER_SPLIT  = False
    USE_HATCH_DETECT = False
    USE_LINE_FIT     = False
    LINE_RMS_THRESH  = 1.5
    USE_HOUGH_LINES  = False
    HOUGH_MIN_LEN    = 40
    HOUGH_MAX_GAP    = 8
    HOUGH_THRESH     = 50
    USE_ANGLE_SNAP   = False
    SNAP_TOL_DEG     = 2.5
    MIN_PATH_LEN     = 0.0
    STITCH_GAP       = 0.0
    CIRCLE_SENS      = 70
    CIRCLE_MIN_R     = 10
    CIRCLE_MAX_R     = 300
    MAX_CIRCLES      = 40
    THRESHOLD_VAL    = 127
    STRAIGHT_TOL     = 2.0
    SIMPLIFY_EPS     = 0.8
    SPLINE_DENSITY   = 120
    SMOOTH_WINDOW    = 7
    EPSILON          = 1.2
    SHARPEN_STR      = 1.0
    DEDUP_DIST       = 0.0
    use_normalize    = False
    NORMALIZE_THICKNESS = 2

    # 🌟 v5.0 신규 옵션 기본값 (기계도면 외에서는 토글로 켤 수 있도록 별도 추가)
    USE_SPUR_PRUNE    = False
    SPUR_MAX_LEN      = 8
    USE_CORNER_ANCHOR = False
    CORNER_ANGLE_DEG  = 40.0
    USE_DIR_STITCH    = False
    DIR_STITCH_THRESH = 0.70
    # Crop 옵션 기본값
    USE_CROP   = False
    CROP_TOP   = 0
    CROP_BOT   = 0
    CROP_LEFT  = 0
    CROP_RIGHT = 0

    # 🪄 v6.1: 자동 CAD 정리 기본값
    USE_AUTO_CLEANUP = False
    CLEANUP_LEVEL    = "standard"

    # 🆕 v6.3: Super-Resolution 기본값 (기본 ON, 1500px 미만일 때만 자동 적용)
    USE_SUPER_RESOLUTION = True
    SR_THRESHOLD_PX      = 1500

    # ── 고급 옵션 ──
    # 🆕 v6.4 [UI 개선 ⑧]: 고급 옵션 기본 접힘 (사이드바 가독성 향상)
    with st.expander("🔧 고급 옵션", expanded=False):
        use_ocr = st.toggle("🔤 문자 인식 (OCR)", key="opt_use_ocr", help="도면 안의 한글/영문/숫자를 자동으로 인식해 DXF 텍스트 객체로 변환합니다. 처리 시간이 다소 늘어날 수 있습니다.")

        # 🆕 v6.3: AI Super-Resolution 토글 (상태 표시 포함)
        st.markdown("<div class='sb-group-header accent'>🤖 AI 화질 향상 (v6.3 ★)</div>", unsafe_allow_html=True)
        if _SR_AVAILABLE:
            USE_SUPER_RESOLUTION = st.toggle(
                "🤖 AI Super-Resolution (FSRCNN x2)",
                value=True,
                key="v63_use_sr",
                help="저해상도 도면(긴 변 1500px 미만)을 FSRCNN 모델로 자동 업스케일합니다. CAD 벡터화 성공률이 크게 향상됩니다. 이미 고해상도면 자동 스킵됩니다."
            )
            if USE_SUPER_RESOLUTION:
                SR_THRESHOLD_PX = st.slider(
                    "자동 적용 기준 (긴 변 px 미만)",
                    min_value=800, max_value=3000, value=1500, step=100,
                    key="v63_sr_threshold",
                    help="이미지의 긴 변이 이 값 미만일 때만 Super-Resolution이 적용됩니다. 이미 큰 이미지는 처리 시간 절약을 위해 스킵됩니다."
                )
        else:
            USE_SUPER_RESOLUTION = False
            if not _SR_MODEL_EXISTS:
                st.markdown(
                    "<div style='font-size:0.72rem;color:#c2410c;background:#fff7ed;border:1px solid #fed7aa;border-radius:5px;padding:6px 10px;margin:4px 0;'>"
                    "⚠️ <b>FSRCNN_x2.pb</b> 파일이 없습니다.<br>도면변환 폴더에 모델을 배치하세요."
                    "</div>", unsafe_allow_html=True
                )
            else:
                st.markdown(
                    "<div style='font-size:0.72rem;color:#c2410c;background:#fff7ed;border:1px solid #fed7aa;border-radius:5px;padding:6px 10px;margin:4px 0;'>"
                    "⚠️ opencv-contrib-python 미설치<br>"
                    "<code style='font-size:0.68rem;'>pip install opencv-contrib-python</code>"
                    "</div>", unsafe_allow_html=True
                )

        st.markdown("<div class='sb-group-header'>🔬 품질 강화</div>", unsafe_allow_html=True)
        use_enhance = st.toggle("✨ 엣지 강화 (Adaptive + Unsharp)", value=(image_type == "기계도면 - 사시도"), key="opt_use_enhance",
            help="Adaptive Thresholding과 Unsharp Masking을 결합해 도면 선을 더 뚜렷하게 만듭니다.")
        if use_enhance:
            SHARPEN_STR = st.slider("선명화 강도", 0.0, 3.0, 1.0, 0.1, key="sl_sharpen",
                help="값이 클수록 선이 더 선명해지지만 노이즈도 함께 강조될 수 있습니다. 보통 0.8~1.5 범위를 권장합니다.")
        else:
            SHARPEN_STR = 1.0

        st.markdown("<div style='margin:4px 0'></div>", unsafe_allow_html=True)
        use_normalize = st.toggle("📏 선 두께 정규화 (Distance Transform)", value=False, key="opt_use_normalize",
            help="스캔 도면의 불균일한 선 두께를 균일하게 만든 뒤 skeleton을 추출합니다. 두꺼운 선에서 가지(branch) 발생을 억제해 DXF 품질이 올라갑니다.")
        if use_normalize:
            NORMALIZE_THICKNESS = st.slider("정규화 두께 (px)", 1, 5, 2, 1, key="sl_normalize_thickness",
                help="목표 선 두께(픽셀). 값이 작을수록 더 얇게 정규화됩니다. 일반 스캔 도면은 2~3 권장.")
        else:
            NORMALIZE_THICKNESS = 2

        st.markdown("<div style='margin:4px 0'></div>", unsafe_allow_html=True)
        use_dedup = st.toggle("🔗 중복선 제거 (KD-tree)", value=False, key="opt_use_dedup",
            help="KD-tree 알고리즘으로 서로 너무 가까운 선분을 하나로 병합합니다.")
        if use_dedup: DEDUP_DIST = st.slider("병합 거리 (px)", 1.0, 10.0, 3.0, 0.5, key="sl_dedup",
            help="이 거리(픽셀) 이내의 중복 선분을 하나로 합칩니다.")
        else: DEDUP_DIST = 0.0

        # 🆕 v6.0: Auto-Clean 강화
        st.markdown("<div class='sb-group-header'>🧹 Auto-Clean 강화 (v6.0)</div>", unsafe_allow_html=True)
        USE_DESKEW = st.toggle("📐 기울기 자동 보정 (Deskew)", value=False, key="v6_use_deskew",
            help="HoughLines로 스캔 기울기를 감지해 자동으로 반듯하게 보정합니다. 스캔 도면에 특히 효과적입니다.")
        USE_SPECKLE = st.toggle("🧹 노이즈 점 제거 (Speckle)", value=False, key="v6_use_speckle",
            help="연결 성분 크기 기준으로 작은 노이즈 점들을 제거합니다.")
        if USE_SPECKLE:
            MIN_SPECKLE_AREA = st.slider("최소 유지 면적 (px²)", 5, 200, 20, 5, key="v6_min_speckle",
                help="이 면적 이하의 연결 픽셀 덩어리를 노이즈로 제거합니다.")
        else:
            MIN_SPECKLE_AREA = 20
        USE_GAP_BRIDGE = st.toggle("🔗 끊어진 선 연결 (Gap Bridge)", value=False, key="v6_use_gap_bridge",
            help="morphologyEx CLOSE로 미세하게 끊어진 선을 자동으로 연결합니다.")
        if USE_GAP_BRIDGE:
            GAP_BRIDGE_SIZE = st.slider("연결 커널 크기 (px)", 2, 8, 3, 1, key="v6_gap_size",
                help="값이 클수록 더 멀리 떨어진 선도 연결합니다. 2~4 권장.")
        else:
            GAP_BRIDGE_SIZE = 3

        # SPLINE 토글 (전체 도면 종류 공통)
        st.markdown("<div style='margin:4px 0'></div>", unsafe_allow_html=True)
        USE_SPLINE = st.toggle("〰️ 곡선 SPLINE 변환", value=False, key="v6_use_spline",
            help="Polyline 대신 DXF SPLINE 엔티티로 곡선을 저장합니다. 점 수를 대폭 줄이고 CAD 편집성을 높입니다. 12점 이상 곡선에 적용됩니다.")

        # 🪄 v6.1: 자동 CAD 정리 (Auto Cleanup) — 1순위 신규 기능
        st.markdown("<div class='sb-group-header accent'>🪄 자동 CAD 정리 (v6.1 ★)</div>", unsafe_allow_html=True)
        USE_AUTO_CLEANUP = st.toggle("🪄 자동 CAD 정리 (원클릭)", value=False, key="v61_use_auto_cleanup",
            help="DXF 출력 직전 path에 통합 후처리 적용: ① 짧은 잡선 자동 제거 ② 끊어진 선 방향 인식 연결 ③ 거의 수직/수평인 선 → 완전 직교 보정. CAD 후편집 시간이 대폭 줄어듭니다.")
        if USE_AUTO_CLEANUP:
            CLEANUP_LEVEL_LABEL = st.radio(
                "정리 강도",
                ["🟢 약함 (보수적)", "🔵 표준 (권장)", "🟠 강함 (적극적)"],
                index=1,
                key="v61_cleanup_level_label",
                horizontal=True,
                label_visibility="collapsed",
                help="약함: 잡선만 제거, 직교 보정 최소화 · 표준: 실무 권장 · 강함: 후편집 최소화 우선"
            )
            CLEANUP_LEVEL = {"🟢 약함 (보수적)": "light",
                             "🔵 표준 (권장)": "standard",
                             "🟠 강함 (적극적)": "strong"}[CLEANUP_LEVEL_LABEL]
        else:
            CLEANUP_LEVEL = "standard"

        # 🌟 v5.0: Crop / ROI 도구  🆕 v6.3: 시각적 드래그 모드 옵션 추가
        st.markdown("<div style='margin:4px 0'></div>", unsafe_allow_html=True)
        USE_CROP = st.toggle("✂️ 변환 영역 자르기 (Crop)", value=False, key="v5_use_crop",
            help="스캔 테두리·표제란·얼룩 등 변환 대상이 아닌 영역을 사전에 잘라내고 변환합니다. 슬라이더(%) 또는 메인 화면의 마우스 드래그(v6.3)로 지정할 수 있습니다.")
        if USE_CROP:
            # 🆕 v6.3: 시각적 vs 슬라이더 모드 선택
            if _CANVAS_AVAILABLE:
                _crop_mode = st.radio(
                    "Crop 모드",
                    ["📐 슬라이더 (%)", "🖱️ 마우스 드래그 (v6.3)"],
                    index=0,
                    key="v63_crop_mode",
                    horizontal=True,
                    label_visibility="collapsed",
                    help="슬라이더: 비율(%) 단위 정밀 지정 · 마우스 드래그: 메인 화면에서 직접 영역 선택 (v6.3)"
                )
            else:
                _crop_mode = "📐 슬라이더 (%)"
                st.caption("💡 streamlit-drawable-canvas 설치 시 마우스 드래그 모드 가능")

            if _crop_mode == "📐 슬라이더 (%)":
                cc1, cc2 = st.columns(2)
                with cc1:
                    CROP_TOP   = st.slider("⬆ 위쪽 (%)",   0, 40, 0, 1, key="v5_crop_top",
                        help="이미지의 상단에서 이 비율만큼 잘라냅니다.")
                    CROP_LEFT  = st.slider("⬅ 왼쪽 (%)",   0, 40, 0, 1, key="v5_crop_left",
                        help="이미지의 좌측에서 이 비율만큼 잘라냅니다.")
                with cc2:
                    CROP_BOT   = st.slider("⬇ 아래쪽 (%)", 0, 40, 0, 1, key="v5_crop_bot",
                        help="이미지의 하단에서 이 비율만큼 잘라냅니다.")
                    CROP_RIGHT = st.slider("➡ 오른쪽 (%)", 0, 40, 0, 1, key="v5_crop_right",
                        help="이미지의 우측에서 이 비율만큼 잘라냅니다.")
            else:
                # 🆕 v6.3: 드래그 모드 - 메인 화면 캔버스에서 값을 받음 (session_state로 동기화)
                CROP_TOP   = int(st.session_state.get("v63_canvas_crop_top",   0))
                CROP_BOT   = int(st.session_state.get("v63_canvas_crop_bot",   0))
                CROP_LEFT  = int(st.session_state.get("v63_canvas_crop_left",  0))
                CROP_RIGHT = int(st.session_state.get("v63_canvas_crop_right", 0))
                st.caption(f"🖱️ 현재 드래그 영역: T{CROP_TOP} / B{CROP_BOT} / L{CROP_LEFT} / R{CROP_RIGHT} %")
        else:
            CROP_TOP = CROP_BOT = CROP_LEFT = CROP_RIGHT = 0

        if image_type in ("기계도면 - 사시도", "기계도면 - 정면도/단면도"):
            st.markdown("<hr style='margin:8px 0; border:none; border-top:1px solid #e1e7ef;'>", unsafe_allow_html=True)
            st.markdown("<div class='sb-group-header accent'>📐 직선·호 강화 (v3.1 ★)</div>", unsafe_allow_html=True)
            USE_LINE_FIT = st.toggle("✨ 직선 자동 변환 (LINE 치환)", value=True, key="v6_use_line_fit",
                help="스켈레톤 경로 중 직선에 가까운 구간을 DXF LINE 엔티티로 자동 변환합니다.")
            if USE_LINE_FIT: LINE_RMS_THRESH = st.slider("직선 잔차 임계값 (px)", 0.3, 5.0, 1.5, 0.1, key="v6_line_rms",
                help="값이 작을수록 더 엄격하게 직선을 판단합니다.")
            else: LINE_RMS_THRESH = 1.5

            USE_GEOMETRY_FITTING = st.toggle("⭕ 호/원 자동 인식 (ARC/CIRCLE)", value=False, key="v7_use_geom_fit",
                help="곡선 구간을 분석해 ARC, CIRCLE 엔티티로 자동 변환합니다.")

            USE_HOUGH_LINES = st.toggle("🎯 HoughLinesP 우선 추출", value=False, key="v6_use_hough_lines",
                help="Hough 변환으로 긴 직선을 먼저 추출한 뒤 나머지 부분을 스켈레톤으로 처리합니다.")
            if USE_HOUGH_LINES:
                hc1, hc2 = st.columns(2)
                with hc1:
                    HOUGH_MIN_LEN = st.slider("최소 길이(px)", 10, 200, 40, 5, key="v6_hough_min")
                    HOUGH_THRESH  = st.slider("탐지 엄격도", 20, 200, 50, 5, key="v6_hough_thr")
                with hc2:
                    HOUGH_MAX_GAP = st.slider("최대 간격(px)", 1, 30, 8, 1, key="v6_hough_gap")
            else:
                HOUGH_MIN_LEN = 40; HOUGH_MAX_GAP = 8; HOUGH_THRESH = 50

            USE_ANGLE_SNAP = st.toggle("📐 각도 스냅 (0/30/45/60/90도 정렬)", value=False, key="v6_use_angle_snap",
                help="직선의 각도를 주요 각도로 자동 정렬합니다.")
            if USE_ANGLE_SNAP: SNAP_TOL_DEG = st.slider("스냅 허용 오차 (도)", 0.5, 8.0, 2.5, 0.5, key="v6_snap_tol")
            else: SNAP_TOL_DEG = 2.5

            st.markdown("<hr style='margin:6px 0; border:none; border-top:1px solid #e1e7ef;'>", unsafe_allow_html=True)
            pc1, pc2 = st.columns(2)
            with pc1: MIN_PATH_LEN = st.slider("🧹 짧은 선 제거(px)", 0.0, 30.0, 5.0, 1.0, key="v6_min_path_len")
            with pc2: STITCH_GAP = st.slider("🪡 끊어진 선 잇기(px)", 0.0, 15.0, 3.0, 0.5, key="v6_stitch_gap")

            # 🌟 v5.0: 엔진 5종 개선 옵션
            st.markdown("<hr style='margin:8px 0; border:none; border-top:1px solid #e1e7ef;'>", unsafe_allow_html=True)
            st.markdown("<div class='sb-group-header accent'>🌟 v5.0 엔진 개선</div>", unsafe_allow_html=True)

            USE_SPUR_PRUNE = st.toggle("🧬 잔가지(Spur) 자동 제거", value=True, key="v5_use_spur_prune",
                help="Skeleton의 Y자 분기점에서 자라난 짧은 가지를 반복적으로 잘라냅니다. 곡선이 한층 매끄러워집니다.")
            if USE_SPUR_PRUNE:
                SPUR_MAX_LEN = st.slider("잔가지 최대 길이 (px)", 3, 20, 8, 1, key="v5_spur_max_len",
                    help="이 길이 이하의 짧은 가지만 제거합니다. 값이 크면 더 적극적으로 정리하지만 짧은 의도된 선까지 삭제될 수 있습니다.")
            else:
                SPUR_MAX_LEN = 8

            USE_CORNER_ANCHOR = st.toggle("📐 코너 앵커링 (직각 보존)", value=True, key="v5_use_corner_anchor",
                help="스무딩 전에 직각/예각 모서리를 검출해 앵커로 고정합니다. 기계도면의 직각 모서리가 둥글게 깎이는 현상을 막아줍니다.")
            if USE_CORNER_ANCHOR:
                CORNER_ANGLE_DEG = st.slider("코너 감지 각도 (도)", 20.0, 70.0, 40.0, 5.0, key="v5_corner_angle",
                    help="이 각도 이상 꺾인 곳을 코너로 판정합니다. 값이 작으면 더 민감(완만한 꺾임도 보존), 값이 크면 직각 같은 뚜렷한 코너만 보존.")
            else:
                CORNER_ANGLE_DEG = 40.0

            USE_DIR_STITCH = st.toggle("🧭 방향인식 선 잇기", value=False, key="v5_use_dir_stitch",
                help="끊어진 선 잇기 시 두 선의 접선 방향이 비슷할 때만 병합합니다. 방향이 다른 선끼리 엉뚱하게 붙는 오류를 막아줍니다. (위쪽 '끊어진 선 잇기' 값이 0보다 클 때 작동)")
            if USE_DIR_STITCH:
                DIR_STITCH_THRESH = st.slider("방향 유사도 기준", 0.30, 0.95, 0.70, 0.05, key="v5_dir_stitch_thresh",
                    help="두 접선의 코사인 유사도 임계값. 0.70 ≈ 45도 이내, 0.85 ≈ 32도 이내만 병합 허용.")
            else:
                DIR_STITCH_THRESH = 0.70

            # 🆕 v6.0: 기계도면 전용 고급 기능
            st.markdown("<hr style='margin:8px 0; border:none; border-top:1px solid #e1e7ef;'>", unsafe_allow_html=True)
            st.markdown("<div class='sb-group-header accent'>🆕 v6.0 선 분류 · 레이어 · 해치</div>", unsafe_allow_html=True)

            USE_DASH_DETECT = st.toggle("--- 대시선 / 점선 자동 인식", value=False, key="v6_use_dash_detect",
                help="각 선의 픽셀 ON/OFF 패턴을 분석해 실선(SOLID) / 대시선(DASHED) / 점선(DOTTED) / 중심선(CENTER)을 자동으로 분류합니다.")

            USE_LAYER_SPLIT = st.toggle("📂 선 종류별 레이어 자동 분리", value=False, key="v6_use_layer_split",
                help="대시선 인식 결과에 따라 OUTLINE / HIDDEN / CENTER / CIRCLE / HATCH 레이어로 자동 분리합니다. '대시선 자동 인식'과 함께 사용하면 효과적입니다.")

            USE_HATCH_DETECT = st.toggle("▦ 해치 패턴 인식 (Hatch)", value=False, key="v6_use_hatch_detect",
                help="서로 평행하고 일정 간격인 선 그룹을 해치 패턴으로 인식해 HATCH 레이어에 표시합니다. 단면도 도면에 효과적입니다.")

    # ── 파라미터 슬라이더 ──
    slider_label = {"기계도면 - 사시도": "⚙️ 사시도 파라미터", "기계도면 - 정면도/단면도": "⚙️ 정면도 파라미터", "깔끔한 디지털 선화": "⚙️ 선화 파라미터", "일반 이미지(간략한 표현,한줄)": "⚙️ 한줄 파라미터", "일반 이미지(풍성한 표현,두줄)": "⚙️ 두줄 파라미터"}.get(image_type, "⚙️ 파라미터")

    with st.expander(slider_label, expanded=True):
        mode_presets = PRESETS.get(image_type, {})
        if mode_presets:
            st.markdown("<div style='font-size:0.72rem;font-weight:700;color:#1d1d1f;letter-spacing:0.05em;margin-bottom:4px'>🎯 프리셋 <span style='color:#94a3b8;font-weight:500;font-size:0.68rem'>(클릭하면 자동 세팅됩니다)</span></div>", unsafe_allow_html=True)
            st.markdown("<div class='preset-row'>", unsafe_allow_html=True)
            preset_cols = st.columns(len(mode_presets))
            active_pname = st.session_state.get(f"active_preset_{image_type}")
            for col, (pname, pvals) in zip(preset_cols, mode_presets.items()):
                with col:
                    btn_type = "primary" if active_pname == pname else "secondary"
                    _preset_help = "이 프리셋이 설정하는 값:\n" + "\n".join([f"• {k.replace('sl_', '')}: {v}" for k, v in pvals.items()])
                    st.button(pname, use_container_width=True, key=f"preset_{image_type}_{pname}", type=btn_type, on_click=_apply_preset_callback, args=(image_type, pname, pvals), help=_preset_help)
            st.markdown("</div><hr style='margin:6px 0 8px'>", unsafe_allow_html=True)

        # ⭐ v6.2: 사용자 정의 프리셋 — 1순위 신규 기능
        with st.expander("⭐ 나만의 프리셋 (이름 붙여 저장)", expanded=False):
            _uid_for_preset = st.session_state.get("user_id", "anonymous")
            try:
                _my_presets = load_user_presets(_uid_for_preset)
            except Exception:
                _my_presets = []

            # ── 현재 설정 저장 ──
            st.markdown("<div style='font-size:0.72rem;font-weight:600;color:#1d1d1f;margin-bottom:4px;'>💾 현재 설정 저장</div>", unsafe_allow_html=True)
            _save_cols = st.columns([3, 1], gap="small")
            with _save_cols[0]:
                _new_preset_name = st.text_input(
                    "프리셋 이름",
                    placeholder="예: 우리회사_기계_정밀",
                    key="v62_new_preset_name",
                    label_visibility="collapsed",
                    max_chars=50,
                )
            with _save_cols[1]:
                if st.button("💾 저장", use_container_width=True, key="v62_save_preset_btn", type="primary"):
                    if _new_preset_name and _new_preset_name.strip():
                        _curr_settings = collect_current_settings(st.session_state)
                        _ok, _msg = save_user_preset(
                            _uid_for_preset, _new_preset_name.strip(),
                            image_type, _curr_settings
                        )
                        if _ok:
                            st.success(_msg)
                            st.session_state["v62_new_preset_name"] = ""
                            st.rerun()
                        else:
                            st.error(_msg)
                    else:
                        st.warning("프리셋 이름을 입력해 주세요.")

            # ── 저장된 프리셋 목록 ──
            if _my_presets:
                st.markdown(f"<div style='font-size:0.72rem;font-weight:600;color:#1d1d1f;margin:8px 0 4px;'>📋 저장된 프리셋 ({len(_my_presets)}개)</div>", unsafe_allow_html=True)
                for _p in _my_presets[:10]:  # 최대 10개만 표시
                    _p_name = _p["name"]
                    _p_type = _p["image_type"] or "?"
                    _p_updated = _p["updated_at"][:10] if _p["updated_at"] else "-"
                    _row_cols = st.columns([5, 1, 1], gap="small")
                    with _row_cols[0]:
                        st.markdown(
                            f"<div style='font-size:0.78rem;font-weight:600;color:#1a3a5c;line-height:1.2;'>{_p_name}</div>"
                            f"<div style='font-size:0.62rem;color:#7a8fa6;font-family:\"JetBrains Mono\",monospace;'>{_p_type[:18]} · {_p_updated}</div>",
                            unsafe_allow_html=True
                        )
                    with _row_cols[1]:
                        if st.button("📥", key=f"v62_load_{_p['id']}", help=f"'{_p_name}' 불러오기", use_container_width=True):
                            _n = apply_user_preset(st.session_state, _p["settings"])
                            st.success(f"✅ '{_p_name}' 적용 ({_n}개 설정)")
                            st.rerun()
                    with _row_cols[2]:
                        if st.button("🗑️", key=f"v62_del_{_p['id']}", help=f"'{_p_name}' 삭제", use_container_width=True):
                            _ok, _msg = delete_user_preset(_uid_for_preset, _p_name)
                            if _ok:
                                st.success(_msg)
                                st.rerun()
                            else:
                                st.error(_msg)
                if len(_my_presets) > 10:
                    st.caption(f"… 외 {len(_my_presets)-10}개 (오래된 프리셋은 삭제 후 확인)")
            else:
                st.caption("💡 자주 쓰는 설정 조합을 이름 붙여 저장해 두면 다음에 바로 불러올 수 있습니다.")

        st.markdown("<hr style='margin:6px 0 8px'>", unsafe_allow_html=True)

        if image_type == "기계도면 - 사시도":
            SIMPLIFY_EPS  = st.slider("곡선 세밀도 (epsilon)", 0.1, 3.0, step=0.1, key="sl_eps")
            SMOOTH_WINDOW = st.slider("스무딩 강도", 3, 25, step=2, key="sl_smooth")
        elif image_type == "기계도면 - 정면도/단면도":
            SIMPLIFY_EPS  = st.slider("직선 단순화 (epsilon)", 0.1, 5.0, step=0.1, key="sl_eps")
            SMOOTH_WINDOW = st.slider("스무딩 강도", 3, 25, step=2, key="sl_smooth")
        elif image_type == "깔끔한 디지털 선화":
            SIMPLIFY_EPS  = st.slider("곡선 세밀도 (epsilon)", 0.1, 3.0, step=0.1, key="sl_eps")
            SMOOTH_WINDOW = st.slider("스무딩 강도", 3, 25, step=2, key="sl_smooth")
        elif image_type == "일반 이미지(간략한 표현,한줄)":
            THRESHOLD_VAL  = st.slider("인식 민감도", 0, 255, step=1, key="sl_threshold")
            STRAIGHT_TOL   = st.slider("직선 공차", 1.0, 15.0, step=0.1, key="sl_straight")
            SIMPLIFY_EPS   = st.slider("곡선 세밀도", 0.1, 5.0, step=0.1, key="sl_eps")
            SPLINE_DENSITY = st.slider("스플라인 밀도", 40, 200, step=10, key="sl_spline")
            SMOOTH_WINDOW  = st.slider("스무딩 강도", 3, 25, step=2, key="sl_smooth")
        elif image_type == "일반 이미지(풍성한 표현,두줄)":
            THRESHOLD_VAL = st.slider("인식 민감도", 0, 255, step=1, key="sl_threshold")
            EPSILON       = st.slider("윤곽선 세밀도", 0.1, 5.0, step=0.1, key="sl_epsilon")

        # ════════════════════════════════════════════════════════════
        # 🆕 v6.4 [UI 개선 ⑦]: 슬라이더 숫자 직접 입력 (정밀 조정용)
        # ════════════════════════════════════════════════════════════
        with st.expander("✏️ 슬라이더 값 직접 입력 (v6.4 ★)", expanded=False):
            st.markdown(
                "<div style='font-size:0.72rem;color:#5a7a96;margin-bottom:6px;line-height:1.4;'>"
                "키보드로 정확한 수치를 입력하고 <b>'📥 적용'</b> 버튼을 누르면 위 슬라이더에 반영됩니다."
                "</div>",
                unsafe_allow_html=True
            )
            _num_specs = []  # (label, key, type, min, max, step, default)
            if image_type in ("기계도면 - 사시도", "깔끔한 디지털 선화"):
                _num_specs = [
                    ("곡선 세밀도 (epsilon)", "sl_eps",    "float", 0.1, 3.0, 0.1, 1.2),
                    ("스무딩 강도",           "sl_smooth", "int",   3,   25,  2,   7),
                ]
            elif image_type == "기계도면 - 정면도/단면도":
                _num_specs = [
                    ("직선 단순화 (epsilon)", "sl_eps",    "float", 0.1, 5.0, 0.1, 1.2),
                    ("스무딩 강도",           "sl_smooth", "int",   3,   25,  2,   7),
                ]
            elif image_type == "일반 이미지(간략한 표현,한줄)":
                _num_specs = [
                    ("인식 민감도",   "sl_threshold","int",   0,   255, 1,   127),
                    ("직선 공차",     "sl_straight", "float", 1.0, 15.0,0.1, 5.0),
                    ("곡선 세밀도",   "sl_eps",      "float", 0.1, 5.0, 0.1, 1.2),
                    ("스플라인 밀도", "sl_spline",   "int",   40,  200, 10,  120),
                    ("스무딩 강도",   "sl_smooth",   "int",   3,   25,  2,   7),
                ]
            elif image_type == "일반 이미지(풍성한 표현,두줄)":
                _num_specs = [
                    ("인식 민감도",   "sl_threshold","int",   0,   255, 1,   127),
                    ("윤곽선 세밀도", "sl_epsilon",  "float", 0.1, 5.0, 0.1, 1.2),
                ]

            _ni_values = {}
            for _lbl, _key, _typ, _mn, _mx, _stp, _df in _num_specs:
                _curr = st.session_state.get(_key, _df)
                if _typ == "int":
                    _ni_values[_key] = st.number_input(
                        _lbl, min_value=int(_mn), max_value=int(_mx),
                        value=int(_curr), step=int(_stp),
                        key=f"v64_ni_{_key}",
                    )
                else:
                    _ni_values[_key] = st.number_input(
                        _lbl, min_value=float(_mn), max_value=float(_mx),
                        value=float(_curr), step=float(_stp),
                        key=f"v64_ni_{_key}", format="%.2f",
                    )

            if st.button("📥 입력값을 슬라이더에 적용",
                         use_container_width=True, type="primary",
                         key="v64_apply_num_inputs",
                         help="입력 박스의 값을 위 슬라이더에 일괄 반영합니다."):
                _applied = 0
                for _key, _v in _ni_values.items():
                    if st.session_state.get(_key) != _v:
                        st.session_state[_key] = _v
                        _applied += 1
                if _applied > 0:
                    st.success(f"✅ {_applied}개 슬라이더에 적용되었습니다.")
                    st.rerun()
                else:
                    st.info("변경된 값이 없습니다.")

    SIMPLIFY_EPS   = st.session_state.get("sl_eps", SIMPLIFY_EPS)
    SMOOTH_WINDOW  = st.session_state.get("sl_smooth", SMOOTH_WINDOW)
    THRESHOLD_VAL  = st.session_state.get("sl_threshold", THRESHOLD_VAL)
    STRAIGHT_TOL   = st.session_state.get("sl_straight", STRAIGHT_TOL)
    SPLINE_DENSITY = st.session_state.get("sl_spline", SPLINE_DENSITY)
    EPSILON        = st.session_state.get("sl_epsilon", EPSILON)
    # 🆕 v6.0 session_state 읽기
    USE_DESKEW       = st.session_state.get("v6_use_deskew",      USE_DESKEW)
    USE_SPECKLE      = st.session_state.get("v6_use_speckle",     USE_SPECKLE)
    MIN_SPECKLE_AREA = st.session_state.get("v6_min_speckle",     MIN_SPECKLE_AREA)
    USE_GAP_BRIDGE   = st.session_state.get("v6_use_gap_bridge",  USE_GAP_BRIDGE)
    GAP_BRIDGE_SIZE  = st.session_state.get("v6_gap_size",        GAP_BRIDGE_SIZE)
    USE_DASH_DETECT  = st.session_state.get("v6_use_dash_detect", USE_DASH_DETECT)
    USE_LAYER_SPLIT  = st.session_state.get("v6_use_layer_split", USE_LAYER_SPLIT)
    USE_HATCH_DETECT = st.session_state.get("v6_use_hatch_detect",USE_HATCH_DETECT)
    USE_SPLINE       = st.session_state.get("v6_use_spline",      USE_SPLINE)
    # 🪄 v6.1
    USE_AUTO_CLEANUP = st.session_state.get("v61_use_auto_cleanup", USE_AUTO_CLEANUP)
    _cl_label = st.session_state.get("v61_cleanup_level_label", "🔵 표준 (권장)")
    CLEANUP_LEVEL = {"🟢 약함 (보수적)": "light",
                     "🔵 표준 (권장)": "standard",
                     "🟠 강함 (적극적)": "strong"}.get(_cl_label, "standard")



# ── 토글 JavaScript v5 FINAL ─────────────────────────────────────────
components.html("""
<script>
(function() {
    var SIDEBAR = '[data-testid="stSidebar"]';
    var STYLE_ID = 'dxf-toggle-fix-v5';

    (function injectAntiFlashCSS() {
        try {
            var doc = window.parent.document;
            if (doc.getElementById(STYLE_ID)) return;
            var s = doc.createElement('style');
            s.id = STYLE_ID;
            s.textContent = [
                '[data-testid="stSidebar"] [role="checkbox"],',
                '[data-testid="stSidebar"] [aria-roledescription="toggle"] {',
                '  background-color: #475569 !important;',
                '  border: 2px solid #334155 !important;',
                '  box-shadow: inset 0 2px 4px rgba(0,0,0,0.4) !important;',
                '  overflow: hidden !important;',
                '  clip-path: inset(0 round 12px) !important;',
                '}',
                '[data-testid="stSidebar"] [role="checkbox"][aria-checked="true"],',
                '[data-testid="stSidebar"] [aria-roledescription="toggle"][aria-checked="true"] {',
                '  background-color: #0066cc !important;',
                '  border: 2px solid #0052a3 !important;',
                '  box-shadow: 0 0 0 2px rgba(0,102,204,0.2) !important;',
                '}',
                '[data-testid="stSidebar"] [role="checkbox"] > div,',
                '[data-testid="stSidebar"] [aria-roledescription="toggle"] > div {',
                '  background-color: #ffffff !important;',
                '}'
            ].join('\\n');
            doc.head.appendChild(s);
        } catch(e) {}
    })();

    function applyToggle() {
        try {
            var doc = window.parent.document;
            var sidebarEl = doc.querySelector('[data-testid="stSidebarContent"]');
            if (!sidebarEl) return;
            var sidebarRight = sidebarEl.getBoundingClientRect().right;

            var inputs = doc.querySelectorAll(SIDEBAR + ' input[aria-checked]');
            inputs.forEach(function(inp) {
                var on = inp.getAttribute('aria-checked') === 'true';
                var track = inp.previousElementSibling;
                if (!track) return;

                track.style.setProperty('background-color',
                    on ? '#0066cc' : '#475569', 'important');
                track.style.setProperty('border',
                    on ? '2px solid #0052a3' : '2px solid #334155', 'important');
                track.style.setProperty('box-shadow',
                    on ? '0 0 0 2px rgba(0,102,204,0.2)'
                       : 'inset 0 2px 4px rgba(0,0,0,0.4)', 'important');
                track.style.setProperty('width',         '44px',                'important');
                track.style.setProperty('min-width',     '44px',                'important');
                track.style.setProperty('height',        '24px',                'important');
                track.style.setProperty('border-radius', '12px',                'important');
                track.style.setProperty('position',      'relative',            'important');
                track.style.setProperty('flex-shrink',   '0',                   'important');
                track.style.setProperty('cursor',        'pointer',             'important');
                track.style.setProperty('box-sizing',    'border-box',          'important');
                track.style.setProperty('overflow',      'hidden',              'important');
                track.style.setProperty('clip-path',     'inset(0 round 12px)', 'important');

                var thumb = track.querySelector('div');
                if (thumb) {
                    thumb.style.setProperty('background-color', '#ffffff', 'important');
                    thumb.style.setProperty('width',         '18px', 'important');
                    thumb.style.setProperty('height',        '18px', 'important');
                    thumb.style.setProperty('border-radius', '50%',  'important');
                    thumb.style.setProperty('box-shadow',
                        on ? '0 2px 6px rgba(0,0,0,0.35)'
                           : '0 1px 3px rgba(0,0,0,0.25)', 'important');
                    thumb.style.setProperty('flex-shrink', '0', 'important');
                }

                var label = inp.closest('label');
                if (label) {
                    var labelLeft = label.getBoundingClientRect().left;
                    var targetW = Math.floor(sidebarRight - labelLeft);
                    if (targetW > 50) {
                        label.style.setProperty('width', targetW + 'px', 'important');
                    }
                    label.style.setProperty('display',         'flex',          'important');
                    label.style.setProperty('flex-direction',  'row-reverse',   'important');
                    label.style.setProperty('justify-content', 'space-between', 'important');
                    label.style.setProperty('align-items',     'center',        'important');
                    label.style.setProperty('padding',         '2px 0',         'important');
                    label.style.setProperty('box-sizing',      'border-box',    'important');
                    label.style.setProperty('gap',             '8px',           'important');
                }
            });
        } catch(e) {}
    }

    [0, 300, 800, 1500, 3000, 5000].forEach(function(t) {
        setTimeout(applyToggle, t);
    });

    setTimeout(function() {
        try {
            var sidebar = window.parent.document.querySelector(SIDEBAR);
            if (sidebar) {
                new MutationObserver(applyToggle).observe(sidebar, {
                    subtree: true, childList: true,
                    attributes: true, attributeFilter: ['aria-checked']
                });
            }
        } catch(e) {}
    }, 1000);

    setInterval(applyToggle, 2000);
})();
</script>
""", height=0)


# ══════════════════════════════════════════
#  🌐  메인 화면
# ══════════════════════════════════════════

if not st.session_state.get("conversion_done", False):
    st.markdown(f"""
<div class="hero-banner">
    <div class="hero-bg-img"></div>
    <div class="hero-left">
        <div class="hero-badge">v6.9 · 🏗️ DWG 바로 저장 · 깔끔한 파일명 · UI 단순화</div>
        <div class="hero-title">📐 이미지 일괄 DWG/DXF 변환 시스템</div>
        <div class="hero-subtitle">🏗️ DWG 바로 저장 · 📐🏗️ 안전망 모드 · 🅰️ AutoCAD 자동 후처리 · ⚡ 퀵 변환 3단계</div>
    </div>
</div>
""", unsafe_allow_html=True)

    files = st.file_uploader(
        "📂 파일 올리기",
        type=["jpg", "png", "jpeg"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="main_uploader",
        help="JPG / JPEG / PNG 이미지를 여러 개 한꺼번에 올릴 수 있어요."
    )

    if files:
        # 🌟 v4.0: 파일 정보 카드 (용량 + 개수 + 파일 목록)
        _total_bytes = sum(len(f.getvalue()) for f in files)
        _total_mb = _total_bytes / (1024 * 1024)
        if _total_mb >= 1.0:
            _size_str = f"{_total_mb:.2f} MB"
        else:
            _size_str = f"{_total_bytes / 1024:.0f} KB"

        _chips = ""
        _shown = files[:8]
        for f in _shown:
            _fname_short = f.name if len(f.name) <= 22 else f.name[:19] + "…"
            _chips += f'<span class="fchip">📄 {_fname_short}</span>'
        if len(files) > 8:
            _chips += f'<span class="fchip" style="background:#e8f0f9;color:#0078d4;font-weight:600;">+{len(files)-8}개 더</span>'

        _ocr_chip = '<span class="fchip" style="background:#fef3c7;color:#92400e;border-color:#fde68a;">🔤 OCR ON</span>' if use_ocr else ''

        st.markdown(f"""
        <div class='file-info-card'>
          <div class='file-info-top'>
            <div class='file-info-icon'>📂</div>
            <div class='file-info-text'>
              <div class='file-info-title'>{len(files)}개 파일 선택됨 · 총 {_size_str}</div>
              <div class='file-info-sub'>JPG · JPEG · PNG 형식 지원 (다중 선택 가능)</div>
            </div>
            <div class='file-info-mode'>{image_type}</div>
          </div>
          <div class='file-info-chips'>{_chips}{_ocr_chip}</div>
        </div>
        """, unsafe_allow_html=True)

        # 📊 v6.1: 이미지 품질 자동 분석 카드 — 2순위 신규 기능
        try:
            _qa = analyze_image_quality(files[0].getvalue())
        except Exception:
            _qa = None
        if _qa is not None:
            _qa_issues_html = ""
            if _qa["issues"]:
                _qa_issues_html = "<div style='margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;'>" + \
                    "".join([f"<span style='background:#fef2f2;color:#991b1b;border:1px solid #fecaca;border-radius:4px;padding:2px 8px;font-size:0.7rem;'>⚠ {iss}</span>" for iss in _qa["issues"]]) + \
                    "</div>"
            _qa_recs_html = "<div style='margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;'>" + \
                "".join([f"<span style='background:#f0f9ff;color:#0c4a6e;border:1px solid #bae6fd;border-radius:4px;padding:2px 8px;font-size:0.7rem;font-weight:500;'>💡 {rec}</span>" for rec in _qa["recommendations"]]) + \
                "</div>"
            _w, _h = _qa["resolution"]
            st.markdown(f"""
            <div style='background:#ffffff;border:1px solid #d0d7e0;border-left:3px solid {_qa["color"]};border-radius:8px;padding:12px 16px;margin:0 0 10px 0;box-shadow:0 1px 4px rgba(0,0,0,0.03);'>
              <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;'>
                <div style='display:flex;align-items:center;gap:10px;'>
                  <div style='background:{_qa["color"]};color:#ffffff;font-weight:700;font-size:1.1rem;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:"JetBrains Mono",monospace;'>{_qa["grade"]}</div>
                  <div>
                    <div style='font-size:0.85rem;font-weight:600;color:#1a3a5c;'>📊 자동 품질 분석 (첫 번째 파일 기준)</div>
                    <div style='font-size:0.74rem;color:{_qa["color"]};font-weight:500;margin-top:1px;'>{_qa["label"]}</div>
                  </div>
                </div>
                <div style='text-align:right;font-family:"JetBrains Mono",monospace;'>
                  <div style='font-size:1.4rem;font-weight:700;color:{_qa["color"]};line-height:1;'>{_qa["score"]}<span style='font-size:0.7rem;color:#9ab5d0;font-weight:500;'>/100</span></div>
                  <div style='font-size:0.62rem;color:#7a8fa6;margin-top:3px;'>📐 {_w}×{_h}px · 선명도 {_qa["sharpness"]:.0f} · 노이즈 {_qa["noise_ratio"]:.1f}%</div>
                </div>
              </div>
              {_qa_issues_html}
              {_qa_recs_html}
            </div>
            """, unsafe_allow_html=True)

            # 🤖 v6.2: AI 추천 강화 — 슬라이더 수치까지 구체 추천 (2순위 신규)
            try:
                _slider_rec = recommend_slider_values(_qa, image_type=image_type)
            except Exception:
                _slider_rec = {"slider_values": {}, "rationale": []}

            _has_toggle_recs = bool(_qa.get("auto_options"))
            _has_slider_recs = bool(_slider_rec.get("slider_values"))

            if _has_toggle_recs or _has_slider_recs:
                _btn_cols = st.columns([2, 1, 1], gap="small")
                with _btn_cols[1]:
                    if _has_slider_recs and st.button(
                        "🤖 AI 슬라이더 수치 추천 보기",
                        use_container_width=True,
                        key="show_slider_recs_btn",
                        help="이미지 분석 결과를 바탕으로 임계값·smooth·epsilon 등 슬라이더 수치까지 구체적으로 추천합니다.",
                    ):
                        st.session_state["v62_show_ai_recs"] = not st.session_state.get("v62_show_ai_recs", False)
                with _btn_cols[2]:
                    # 🔧 v6.7 fix: on_click 콜백으로 변경
                    # 기존: if st.button() 블록 안에서 session_state 직접 수정
                    #   → 슬라이더가 이미 렌더링된 후라 StreamlitAPIException 발생
                    # 수정: on_click 콜백은 슬라이더 렌더링 전에 실행되므로 충돌 없음
                    def _apply_ai_recs_callback(
                        _toggle_dict=_qa.get("auto_options", {}),
                        _slider_dict=_slider_rec.get("slider_values", {}),
                    ):
                        """추천 토글 + 슬라이더 값을 session_state에 일괄 적용 (on_click 콜백)."""
                        for k, v in _toggle_dict.items():
                            st.session_state[k] = v
                        for k, v in _slider_dict.items():
                            st.session_state[k] = v
                        _total = len(_toggle_dict) + len(_slider_dict)
                        st.session_state["v67_ai_apply_count"] = _total

                    st.button(
                        "🎯 추천 일괄 적용",
                        use_container_width=True,
                        key="apply_recs_btn",
                        type="primary",
                        help="ON/OFF 추천 + AI 슬라이더 수치 추천을 모두 자동 적용합니다 (사이드바 값 변경)",
                        on_click=_apply_ai_recs_callback,
                    )
                    # 적용 완료 메시지 표시
                    _applied_count = st.session_state.pop("v67_ai_apply_count", None)
                    if _applied_count is not None:
                        st.success(f"✅ 총 {_applied_count}개 추천 설정을 자동 적용했습니다.")

                # AI 슬라이더 수치 추천 펼침 카드
                if _has_slider_recs and st.session_state.get("v62_show_ai_recs", False):
                    _sv = _slider_rec["slider_values"]
                    _rat = _slider_rec["rationale"]

                    _rows_html = ""
                    # 슬라이더 키 → 한글 라벨 매핑
                    _label_map = {
                        "sl_threshold":         ("인식 민감도 (Threshold)", ""),
                        "sl_epsilon":           ("윤곽선 세밀도 (epsilon)", ""),
                        "sl_eps":               ("곡선 세밀도 (epsilon)", ""),
                        "sl_smooth_window":     ("스무딩 강도 (smooth)", ""),
                        "sl_smooth":            ("스무딩 강도 (smooth)", ""),
                        "sl_min_path_len":      ("최소 path 길이", "px"),
                        "sl_stitch_gap":        ("끊김 연결 거리", "px"),
                        "sl_dedup_dist":        ("중복 제거 거리", "px"),
                        "v6_min_speckle_area":  ("Speckle 최소 면적", "px²"),
                        "v6_gap_bridge_size":   ("Gap Bridge 크기", "px"),
                        "sl_sharpen_strength":  ("샤픈 강도", ""),
                    }
                    for k, v in _sv.items():
                        _kor_label, _unit = _label_map.get(k, (k, ""))
                        _rows_html += f"""
                        <div style='display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px dashed #e5e7eb;font-size:0.74rem;'>
                          <span style='color:#475569;'>{_kor_label}</span>
                          <span style='font-family:"JetBrains Mono",monospace;font-weight:700;color:#0f766e;'>{v}{_unit}</span>
                        </div>"""
                    _rat_html = "".join([f"<li style='margin-bottom:2px;'>{r}</li>" for r in _rat])

                    st.markdown(f"""
                    <div style='background:#f0fdfa;border:1px solid #99f6e4;border-left:3px solid #14b8a6;border-radius:8px;padding:12px 16px;margin-top:8px;'>
                      <div style='font-size:0.78rem;font-weight:700;color:#0f766e;margin-bottom:8px;'>
                        🤖 AI 추천 슬라이더 값 ({len(_sv)}개)
                      </div>
                      <div style='display:grid;grid-template-columns:1fr 1fr;gap:0 16px;'>{_rows_html}</div>
                      <details style='margin-top:8px;'>
                        <summary style='font-size:0.72rem;color:#475569;cursor:pointer;font-weight:500;'>📝 추천 근거 ({len(_rat)}개)</summary>
                        <ul style='font-size:0.7rem;color:#64748b;margin:6px 0 0 18px;line-height:1.4;'>{_rat_html}</ul>
                      </details>
                    </div>
                    """, unsafe_allow_html=True)

        # 사용 절차 안내
        st.markdown("""
<div style="
    background: #ffffff;
    border: 1px solid #d0d7e0;
    border-left: 3px solid #0078d4;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0 10px 0;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
">
  <div style="font-size:1.1rem; margin-top:1px; color:#0078d4;">💡</div>
  <div>
    <div style="font-size:0.78rem; font-weight:600; color:#1a3a5c; margin-bottom:6px; letter-spacing:0.02em; font-family:'JetBrains Mono', monospace;">변환 전 확인해 주세요</div>
    <div style="display:flex; flex-wrap:wrap; gap:6px;">
      <span style="background:#f0f6ff; border:1px solid #b8d0eb; border-radius:4px; padding:3px 10px; font-size:0.74rem; font-weight:500; color:#1a6bb5;">
        ① 사이드바에서 <b>도면 종류</b> 선택
      </span>
      <span style="color:#9ab5d0; font-size:0.75rem; align-self:center; font-family:'JetBrains Mono', monospace;">→</span>
      <span style="background:#f0f6ff; border:1px solid #b8d0eb; border-radius:4px; padding:3px 10px; font-size:0.74rem; font-weight:500; color:#1a6bb5;">
        ② <b>고급 옵션</b> 및 <b>파라미터</b> 조절
      </span>
      <span style="color:#9ab5d0; font-size:0.75rem; align-self:center; font-family:'JetBrains Mono', monospace;">→</span>
      <span style="background:#f0f6ff; border:1px solid #b8d0eb; border-radius:4px; padding:3px 10px; font-size:0.74rem; font-weight:500; color:#1a6bb5;">
        ③ <b>3단 미리보기</b>로 결과 확인
      </span>
      <span style="color:#9ab5d0; font-size:0.75rem; align-self:center; font-family:'JetBrains Mono', monospace;">→</span>
      <span style="background:#0078d4; border:1px solid #0078d4; border-radius:4px; padding:3px 10px; font-size:0.74rem; font-weight:600; color:#ffffff;">
        ④ 🏗️ DWG 파일로 변환
      </span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ════════════════════════════════════════════════════════════════════
        # 🆕 v6.7 [핵심]: 메인 화면 출력 형식 선택 + ODA 상태 + 변환 버튼
        # ════════════════════════════════════════════════════════════════════
        # 사이드바 안 열어도 보이도록 변환 버튼 바로 위에 배치
        # 기본값: DWG만 저장 (사용자 요청 — DXF 파일 필요 없음)
        # ════════════════════════════════════════════════════════════════════

        # 현재 ODA 사용 가능 여부 체크
        _v67_oda_path  = st.session_state.get("v65_oda_path", "")
        _v67_oda_ready = bool(_v67_oda_path) and os.path.isfile(_v67_oda_path) and _IS_WINDOWS

        # 출력 형식 선택 UI
        st.markdown(
            "<div style='font-size:0.78rem; font-weight:700; color:#1a3a5c; "
            "letter-spacing:0.05em; margin-top:8px; margin-bottom:6px;'>"
            "📤 출력 형식 선택"
            "</div>",
            unsafe_allow_html=True
        )

        _fmt_cols = st.columns([3, 1], gap="medium")
        with _fmt_cols[0]:
            # 현재 세션값 → 라디오 인덱스로 변환
            _cur_fmt = st.session_state.get("v66_output_format", "dwg_only")
            # DXF만 옵션은 메인에서 노출 안 함. 만약 이전 세션에 dxf_only가 남아 있어도 dwg_only로 강제.
            if _cur_fmt == "dxf_only":
                _cur_fmt = "dwg_only"
                st.session_state["v66_output_format"] = "dwg_only"

            _fmt_options = [
                "🏗️ DWG만 저장 (기본, 권장)",
                "📐🏗️ DXF + DWG 둘 다 저장 (안전망)",
            ]
            _fmt_index = 0 if _cur_fmt == "dwg_only" else 1

            _selected_fmt_label = st.radio(
                "출력 형식 선택",
                options=_fmt_options,
                index=_fmt_index,
                key="v67_main_fmt_radio",
                horizontal=True,
                label_visibility="collapsed",
                help=(
                    "🏗️ DWG만: AutoCAD에서 바로 열기 좋음 (대부분 이 옵션 추천)\n"
                    "📐🏗️ 둘 다: 호환성 안전망 — DWG 변환 실패 대비용 DXF 백업도 함께 저장"
                ),
            )
            # 라벨 → 코드로 변환 후 세션에 저장
            st.session_state["v66_output_format"] = (
                "dwg_only" if _selected_fmt_label.startswith("🏗️ DWG만") else "both"
            )

        with _fmt_cols[1]:
            # ODA 설치 상태 표시 배지
            if _v67_oda_ready:
                _ver_code = st.session_state.get("v65_dwg_version_code", "ACAD2018")
                st.markdown(
                    f"<div style='background:#e8f5e9;border:1px solid #4caf50;"
                    f"border-radius:6px;padding:6px 10px;font-size:0.74rem;"
                    f"color:#1b5e20;text-align:center;font-weight:600;'>"
                    f"✅ ODA 준비됨<br>"
                    f"<span style='font-size:0.66rem;font-weight:400;'>{_ver_code}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            elif not _IS_WINDOWS:
                st.markdown(
                    "<div style='background:#fff3e0;border:1px solid #ff9800;"
                    "border-radius:6px;padding:6px 10px;font-size:0.74rem;"
                    "color:#e65100;text-align:center;font-weight:600;'>"
                    "🌐 웹 배포본<br>"
                    "<span style='font-size:0.66rem;font-weight:400;'>DXF로만 저장됨</span>"
                    "</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<div style='background:#ffebee;border:1px solid #f44336;"
                    "border-radius:6px;padding:6px 10px;font-size:0.74rem;"
                    "color:#b71c1c;text-align:center;font-weight:600;'>"
                    "❌ ODA 미설치<br>"
                    "<span style='font-size:0.66rem;font-weight:400;'>DXF로 대체됨</span>"
                    "</div>",
                    unsafe_allow_html=True,
                )

        # ODA 미설치 안내 (DWG 선택 + ODA 없음)
        if not _v67_oda_ready:
            _fmt_now_check = st.session_state.get("v66_output_format", "dwg_only")
            if _fmt_now_check in ("dwg_only", "both"):
                with st.expander("ℹ️ ODA File Converter 설치 안내 (DWG 변환 필수)", expanded=False):
                    st.markdown(
                        """
                        **DWG 변환에는 무료 도구 'ODA File Converter'가 필요합니다.**

                        - 다운로드: https://www.opendesign.com/guestfiles/oda_file_converter
                        - 무료 (이메일 가입만 필요)
                        - 설치 시 경로 그대로 두면 (`C:\\Program Files\\ODA\\...`) **자동으로 인식**됩니다.
                        - 설치 후 이 페이지를 새로고침하면 ODA 자동 발견됨.

                        💡 **지금은 ODA가 없어도 됩니다** — DWG 변환이 실패해도 자동으로 DXF로 대체 저장됩니다.

                        📍 ODA 경로를 직접 지정하려면: 사이드바 **'🔧 DWG / AutoCAD 자동 연동'** 펼치기
                        """
                    )

        # 🆕 v6.6: 변환 버튼 라벨을 출력 형식에 맞게 동적 변경
        _v66_fmt_btn = st.session_state.get("v66_output_format", "dwg_only")
        _v66_btn_label = {
            "dxf_only": "📐  DXF 파일로 변환",
            "dwg_only": "🏗️  DWG 파일로 변환",
            "both":     "📐🏗️  DXF + DWG 둘 다 변환",
        }.get(_v66_fmt_btn, "🏗️  DWG 파일로 변환")

        bcol1, bcol2 = st.columns([3, 1], gap="small")
        with bcol1:
            run_clicked = st.button(_v66_btn_label, use_container_width=True, type="primary", key="run_btn")
        with bcol2:
            cancel_clicked = st.button("✕ 취소", use_container_width=True, key="cancel_btn")

        if cancel_clicked:
            for k in ["main_uploader", "live_preview_tab", "preview_idx_main"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

        if run_clicked:
            res, z_buf = [], io.BytesIO()
            failed_files = []  # v4.0: 실패 파일 목록
            prog = st.progress(0, text="변환 준비 중...")
            dot_placeholder = st.empty()  # v4.0: 파일별 도트 표시
            name_counter = {}
            _success_count = 0

            # 🌟 v4.0: 변환 시작 시 도트 초기화 (모두 pending)
            def render_dots(states):
                """states: list of 'pending'|'active'|'done'|'fail'"""
                html = "<div class='prog-dots'>"
                for s in states:
                    html += f"<div class='prog-dot {s if s != 'pending' else ''}' title='{s}'></div>"
                html += "</div>"
                return html

            file_states = ["pending"] * len(files)
            dot_placeholder.markdown(render_dots(file_states), unsafe_allow_html=True)

            with zipfile.ZipFile(z_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for i, f in enumerate(files):
                    file_states[i] = "active"
                    dot_placeholder.markdown(render_dots(file_states), unsafe_allow_html=True)
                    # 🆕 v6.6: 진행률 텍스트에 출력 형식 표시
                    _fmt_label_dot = {
                        "dxf_only": "DXF",
                        "dwg_only": "DWG",
                        "both":     "DXF+DWG",
                    }.get(st.session_state.get("v66_output_format", "dwg_only"), "DWG")
                    prog.progress(i / len(files), text=f"⚙️ 변환 중 [{_fmt_label_dot}] ({i+1}/{len(files)}) · {f.name}")

                    try:
                        img_bytes = f.getvalue()
                        # 🌟 v5.0: Crop 적용 (켜진 경우만)
                        if USE_CROP:
                            img_bytes = apply_crop_to_bytes(img_bytes, CROP_TOP, CROP_BOT, CROP_LEFT, CROP_RIGHT)

                        # 🔁 v6.2: 재변환을 위해 변환 인자를 dict로 저장 (current_settings에서 갱신 가능)
                        _conv_kwargs = dict(
                            layer_name=layer_name, image_type=image_type, use_ocr=use_ocr,
                            t_val=THRESHOLD_VAL, s_tol=STRAIGHT_TOL, s_eps=SIMPLIFY_EPS,
                            s_den=SPLINE_DENSITY, s_win=SMOOTH_WINDOW, epsilon=EPSILON,
                            use_hough=USE_HOUGH, circle_sens=CIRCLE_SENS,
                            circle_min_r=CIRCLE_MIN_R, circle_max_r=CIRCLE_MAX_R, max_circles=MAX_CIRCLES,
                            use_pattern=USE_PATTERN, use_spline=USE_SPLINE,
                            use_geometry_fitting=USE_GEOMETRY_FITTING, user_scale=USER_SCALE,
                            use_enhance=use_enhance, sharpen_strength=SHARPEN_STR, dedup_dist=DEDUP_DIST,
                            use_line_fit=USE_LINE_FIT, line_rms_thresh=LINE_RMS_THRESH,
                            use_angle_snap=USE_ANGLE_SNAP, snap_tol_deg=SNAP_TOL_DEG,
                            use_hough_lines=USE_HOUGH_LINES, hough_min_len=HOUGH_MIN_LEN,
                            hough_max_gap=HOUGH_MAX_GAP, hough_thresh=HOUGH_THRESH,
                            min_path_len=MIN_PATH_LEN, stitch_gap=STITCH_GAP,
                            use_normalize=use_normalize, normalize_thickness=NORMALIZE_THICKNESS,
                            use_spur_prune=USE_SPUR_PRUNE, spur_max_len=SPUR_MAX_LEN,
                            use_corner_anchor=USE_CORNER_ANCHOR, corner_angle_deg=CORNER_ANGLE_DEG,
                            use_dir_stitch=USE_DIR_STITCH, dir_stitch_thresh=DIR_STITCH_THRESH,
                            use_deskew=USE_DESKEW, use_speckle=USE_SPECKLE,
                            min_speckle_area=MIN_SPECKLE_AREA,
                            use_gap_bridge=USE_GAP_BRIDGE, gap_bridge_size=GAP_BRIDGE_SIZE,
                            use_dash_detect=USE_DASH_DETECT, use_layer_split=USE_LAYER_SPLIT,
                            use_hatch_detect=USE_HATCH_DETECT,
                            use_auto_cleanup=USE_AUTO_CLEANUP, cleanup_level=CLEANUP_LEVEL,
                            # 🆕 v6.3
                            use_super_resolution=USE_SUPER_RESOLUTION,
                            sr_threshold_px=SR_THRESHOLD_PX,
                        )

                        d_bytes, rpt = convert_to_dxf_bytes(img_bytes, **_conv_kwargs)
                        base = os.path.splitext(f.name)[0]
                        # 🆕 v6.9: 파일명 규칙 단순화
                        #   기존: 원본이름_dxf변환.dxf, 원본이름_dxf변환 (2).dxf
                        #   변경: 원본이름.dxf, 원본이름 (2).dxf — 깔끔하고 직관적
                        if base not in name_counter:
                            name_counter[base] = 0
                            _suffix = ""
                        else:
                            name_counter[base] += 1
                            _suffix = f" ({name_counter[base] + 1})"  # (2), (3), ...
                        d_name = f"{base}{_suffix}.dxf"

                        # ════════════════════════════════════════════════════════════
                        # 🆕 v6.6 [핵심]: 출력 형식에 따라 DXF/DWG 자동 분기
                        # ════════════════════════════════════════════════════════════
                        _out_fmt = st.session_state.get("v66_output_format", "dwg_only")
                        _oda_path_now  = st.session_state.get("v65_oda_path", "")
                        _dwg_ver_now   = st.session_state.get("v65_dwg_version_code", "ACAD2018")
                        _oda_available = bool(_oda_path_now) and os.path.isfile(_oda_path_now)

                        # 🛡️ Windows가 아니거나 ODA 없으면 DXF로 강제 (안전 fallback)
                        if _out_fmt in ("dwg_only", "both") and (not _IS_WINDOWS or not _oda_available):
                            _out_fmt_actual = "dxf_only"
                            rpt.setdefault("warnings", []).append(
                                "⚠️ DWG 출력 요청됐으나 ODA Converter를 사용할 수 없어 DXF로만 저장됨"
                            )
                        else:
                            _out_fmt_actual = _out_fmt

                        # DWG 변환 시도 (필요한 경우만)
                        _dwg_bytes = None
                        _dwg_name  = ""
                        if _out_fmt_actual in ("dwg_only", "both"):
                            # 🆕 v6.9: DWG 파일명도 원본이름.dwg 형태로 단순화
                            _dwg_name = f"{base}{_suffix}.dwg"
                            _dwg_bytes, _dwg_msg = convert_dxf_to_dwg_via_oda(
                                dxf_bytes=d_bytes,
                                dwg_filename_stem=f"{base}{_suffix}",
                                oda_exe_path=_oda_path_now,
                                target_version=_dwg_ver_now,
                                timeout_sec=90,
                            )
                            if _dwg_bytes is None:
                                # DWG 변환 실패 → 경고 누적 + DXF로 fallback
                                rpt.setdefault("warnings", []).append(
                                    f"⚠️ DWG 변환 실패: {_dwg_msg[:120]} (DXF로 대신 저장)"
                                )
                                _out_fmt_actual = "dxf_only"
                                _dwg_bytes = None

                        # ZIP에 추가 + results 등록 (출력 형식에 맞춰)
                        if _out_fmt_actual == "dxf_only":
                            # DXF만
                            zf.writestr(d_name, d_bytes)
                            res.append({
                                "filename": d_name, "original_name": f.name,
                                "content": d_bytes, "image": img_bytes, "report": rpt,
                                "conv_kwargs": _conv_kwargs,
                                "format": "dxf",
                            })
                        elif _out_fmt_actual == "dwg_only":
                            # DWG만 (DXF는 ZIP에 안 넣음)
                            zf.writestr(_dwg_name, _dwg_bytes)
                            res.append({
                                "filename": _dwg_name, "original_name": f.name,
                                # content는 미리보기/재변환 호환성을 위해 DXF를 그대로 유지
                                "content": d_bytes,             # 미리보기/재변환용 DXF 원본
                                "dwg_content": _dwg_bytes,      # 실제 다운로드용 DWG
                                "image": img_bytes, "report": rpt,
                                "conv_kwargs": _conv_kwargs,
                                "format": "dwg",
                            })
                        else:  # "both" — DXF + DWG 둘 다
                            zf.writestr(d_name, d_bytes)
                            zf.writestr(_dwg_name, _dwg_bytes)
                            res.append({
                                "filename": d_name, "original_name": f.name,
                                "content": d_bytes, "image": img_bytes, "report": rpt,
                                "conv_kwargs": _conv_kwargs,
                                "dwg_filename": _dwg_name,
                                "dwg_content":  _dwg_bytes,
                                "format": "both",
                            })

                        _success_count += 1
                        file_states[i] = "done"
                    except Exception as e:
                        # 🌟 v4.0: 오류 파일 건너뛰기 (전체 중단하지 않음)
                        failed_files.append({"name": f.name, "error": str(e)})
                        file_states[i] = "fail"

                    dot_placeholder.markdown(render_dots(file_states), unsafe_allow_html=True)

            prog.progress(1.0, text=f"✅ 완료! 성공 {_success_count}건 / 실패 {len(failed_files)}건")
            if _success_count > 0:
                record_conversion(_uid, _success_count, image_type, success=True)
            if res or failed_files:
                st.session_state.update({
                    "dxf_results": res,
                    "zip_data": z_buf.getvalue(),
                    "conversion_done": True,
                    "failed_files": failed_files,
                    "conv_image_type": image_type,
                })
                st.rerun()

        # 3단 미리보기
        prev_idx = 0
        if len(files) > 1:
            prev_idx = st.selectbox("🔍 미리볼 파일 선택", range(len(files)), format_func=lambda i: files[i].name, key="preview_idx_main")
        selected_bytes_orig = files[prev_idx].getvalue()

        # 🆕 v6.3: 시각적 Crop 캔버스 (st-canvas, 드래그 모드 선택 시에만 표시)
        _crop_mode_active = (
            USE_CROP and _CANVAS_AVAILABLE and
            st.session_state.get("v63_crop_mode", "📐 슬라이더 (%)") == "🖱️ 마우스 드래그 (v6.3)"
        )
        if _crop_mode_active:
            with st.expander("🖱️ 시각적 Crop — 마우스로 변환 영역 선택 (v6.3 ★)", expanded=True):
                try:
                    # 원본 이미지를 PIL로 변환
                    _arr_c = np.asarray(bytearray(selected_bytes_orig), dtype=np.uint8)
                    _img_c = cv2.imdecode(_arr_c, cv2.IMREAD_COLOR)
                    _h_c, _w_c = _img_c.shape[:2]
                    _img_rgb = cv2.cvtColor(_img_c, cv2.COLOR_BGR2RGB)
                    if _PIL_AVAILABLE:
                        _pil_img = _PILImage.fromarray(_img_rgb)
                    else:
                        _pil_img = None

                    # 캔버스 표시 폭 결정 (메인 영역에 맞춤, 최대 900px)
                    _canvas_w_disp = min(900, _w_c)
                    _canvas_h_disp = int(_h_c * (_canvas_w_disp / _w_c))
                    _scale_ratio = _canvas_w_disp / _w_c  # 디스플레이 → 원본 좌표 변환비

                    st.caption("💡 사각형을 드래그해서 **유지할 영역**을 선택하세요. 그 외부가 잘립니다. 빈 캔버스면 Crop 없음.")

                    _cc1, _cc2 = st.columns([5, 1])
                    with _cc2:
                        if st.button("🔄 초기화", key="v63_canvas_reset", use_container_width=True,
                                     help="드래그 영역을 모두 지우고 Crop을 0으로 되돌립니다."):
                            st.session_state["v63_canvas_crop_top"]   = 0
                            st.session_state["v63_canvas_crop_bot"]   = 0
                            st.session_state["v63_canvas_crop_left"]  = 0
                            st.session_state["v63_canvas_crop_right"] = 0
                            # 캔버스 강제 리렌더링용 키 갱신
                            st.session_state["v63_canvas_nonce"] = int(st.session_state.get("v63_canvas_nonce", 0)) + 1
                            st.rerun()

                    with _cc1:
                        _canvas_key = f"v63_canvas_{prev_idx}_{st.session_state.get('v63_canvas_nonce', 0)}"
                        _canvas_result = st_canvas(
                            fill_color="rgba(0, 120, 212, 0.15)",
                            stroke_width=2,
                            stroke_color="#0078d4",
                            background_image=_pil_img,
                            update_streamlit=True,
                            height=_canvas_h_disp,
                            width=_canvas_w_disp,
                            drawing_mode="rect",
                            key=_canvas_key,
                            display_toolbar=True,
                        )

                    # 그려진 사각형 → Crop 비율 계산
                    if (_canvas_result is not None
                        and _canvas_result.json_data is not None
                        and _canvas_result.json_data.get("objects")):
                        _objs = _canvas_result.json_data["objects"]
                        # 가장 마지막에 그린 사각형만 사용
                        _rects = [o for o in _objs if o.get("type") == "rect"]
                        if _rects:
                            _r = _rects[-1]
                            # 캔버스 좌표 (디스플레이 픽셀 기준)
                            _rx = float(_r.get("left", 0)) + float(_r.get("strokeWidth", 0)) / 2
                            _ry = float(_r.get("top",  0)) + float(_r.get("strokeWidth", 0)) / 2
                            _rw = float(_r.get("width", 0)) * float(_r.get("scaleX", 1))
                            _rh = float(_r.get("height", 0)) * float(_r.get("scaleY", 1))
                            # 디스플레이 → 원본 픽셀
                            _orig_x = _rx / _scale_ratio
                            _orig_y = _ry / _scale_ratio
                            _orig_w = _rw / _scale_ratio
                            _orig_h = _rh / _scale_ratio
                            # 유지 영역의 비율 → 잘라낼 영역 % 계산 (캔버스는 유지 영역을 선택)
                            _crop_l_pct = max(0, min(40, round((_orig_x / _w_c) * 100)))
                            _crop_t_pct = max(0, min(40, round((_orig_y / _h_c) * 100)))
                            _crop_r_pct = max(0, min(40, round(((_w_c - _orig_x - _orig_w) / _w_c) * 100)))
                            _crop_b_pct = max(0, min(40, round(((_h_c - _orig_y - _orig_h) / _h_c) * 100)))
                            # session_state 업데이트 (변경 시에만)
                            _new_vals = {
                                "v63_canvas_crop_top":   int(_crop_t_pct),
                                "v63_canvas_crop_bot":   int(_crop_b_pct),
                                "v63_canvas_crop_left":  int(_crop_l_pct),
                                "v63_canvas_crop_right": int(_crop_r_pct),
                            }
                            _changed = False
                            for _k, _v in _new_vals.items():
                                if st.session_state.get(_k, -1) != _v:
                                    st.session_state[_k] = _v
                                    _changed = True
                            if _changed:
                                st.success(f"✅ Crop 영역 적용: T{_crop_t_pct} / B{_crop_b_pct} / L{_crop_l_pct} / R{_crop_r_pct} %")
                                st.rerun()
                    else:
                        # 캔버스가 비어 있으면 0으로 리셋 (사용자가 지웠을 때)
                        if any(st.session_state.get(k, 0) > 0 for k in
                               ["v63_canvas_crop_top","v63_canvas_crop_bot","v63_canvas_crop_left","v63_canvas_crop_right"]):
                            for _k in ["v63_canvas_crop_top","v63_canvas_crop_bot","v63_canvas_crop_left","v63_canvas_crop_right"]:
                                st.session_state[_k] = 0
                except Exception as _ce:
                    st.warning(f"⚠️ 시각적 Crop 초기화 실패: {_ce}. 사이드바의 슬라이더 모드를 사용하세요.")

        # 🌟 v5.0: Crop 적용 (켜진 경우만, 미리보기와 변환 둘 다 동일하게)
        if USE_CROP and (CROP_TOP + CROP_BOT + CROP_LEFT + CROP_RIGHT) > 0:
            selected_bytes = apply_crop_to_bytes(selected_bytes_orig, CROP_TOP, CROP_BOT, CROP_LEFT, CROP_RIGHT)
        else:
            selected_bytes = selected_bytes_orig

        col_orig, col_opt, col_dxf = st.columns(3, gap="small")

        # 🌟 v4.0: 미리보기 단계 번호 + 하단 정보
        with col_orig:
            _crop_active = USE_CROP and (CROP_TOP + CROP_BOT + CROP_LEFT + CROP_RIGHT) > 0
            _title_suffix = " <span style='color:#0078d4;font-size:0.7rem;background:#e6f1fb;border-radius:3px;padding:1px 6px;margin-left:6px;'>✂️ CROP</span>" if _crop_active else ""
            st.markdown(f"""<div class='preview-title before'>
                <span class='prev-step-num s1'>1</span>
                <span>원본 이미지{_title_suffix}</span>
            </div>""", unsafe_allow_html=True)
            st.image(selected_bytes, use_container_width=True)
            # 이미지 크기 정보
            try:
                _arr = np.asarray(bytearray(selected_bytes), dtype=np.uint8)
                _img = cv2.imdecode(_arr, cv2.IMREAD_COLOR)
                _h, _w = _img.shape[:2]
                _fname = files[prev_idx].name
                _fname_short = _fname if len(_fname) <= 28 else _fname[:25] + "…"
                _size_kb = len(selected_bytes) / 1024
                _crop_info = f" · ✂️ Crop T{CROP_TOP}/B{CROP_BOT}/L{CROP_LEFT}/R{CROP_RIGHT}%" if _crop_active else ""
                st.markdown(f"""<div class='prev-info-bar'>
                    <span>📄 {_fname_short}{_crop_info}</span>
                    <span>{_w}×{_h}px · {_size_kb:.0f}KB</span>
                </div>""", unsafe_allow_html=True)
            except Exception:
                pass

        with col_opt:
            st.markdown("""<div class='preview-title opt'>
                <span class='prev-step-num s2'>2</span>
                <span>변환용 분석 이미지</span>
            </div>""", unsafe_allow_html=True)
            with st.spinner("이미지 분석 및 최적화 중..."):
                opt_img = get_optimized_image_preview(
                    selected_bytes, image_type, THRESHOLD_VAL,
                    use_enhance, SHARPEN_STR
                )
                st.image(opt_img, use_container_width=True, clamp=True)
                _enhance_str = "엣지 강화 ON" if use_enhance else "기본 모드"
                # 🌟 v5.0: 적용 중인 엔진 개선 표시
                _v5_badges = []
                if USE_SPUR_PRUNE:    _v5_badges.append("🧬 잔가지")
                if USE_CORNER_ANCHOR: _v5_badges.append("📐 코너")
                if USE_DIR_STITCH:    _v5_badges.append("🧭 방향")
                _v5_str = " · ".join(_v5_badges) if _v5_badges else _enhance_str
                st.markdown(f"""<div class='prev-info-bar'>
                    <span>🔬 Skeleton 처리</span>
                    <span>{_v5_str}</span>
                </div>""", unsafe_allow_html=True)

        with col_dxf:
            st.markdown("""<div class='preview-title after'>
                <span class='prev-step-num s3'>3</span>
                <span>최종 DXF 미리보기</span>
            </div>""", unsafe_allow_html=True)

            # ── 배경 선택 (패널 인라인) ──
            _bg_choice = st.radio(
                "배경",
                list(PREVIEW_BG_OPTIONS.keys()),
                index=0,
                key="preview_bg_choice",
                horizontal=True,
                label_visibility="collapsed",
                help="CAD Dark · White Paper · Blueprint — DXF 파일에는 영향 없음"
            )
            _bg_cfg = PREVIEW_BG_OPTIONS[_bg_choice]
            PREVIEW_BG_COLOR = _bg_cfg["bg"]
            PREVIEW_LINE_COLOR = _bg_cfg["line"]

            if not _PLOTLY_AVAILABLE:
                st.markdown(
                    "<div style='font-size:0.72rem;color:#92400e;background:#fef3c7;"
                    "border-radius:5px;padding:5px 9px;margin-bottom:4px;'>"
                    "🔍 줌 기능을 쓰려면 터미널에서: "
                    "<code>pip install plotly pillow</code> 후 재시작</div>",
                    unsafe_allow_html=True
                )

            # 🆕 v6.0: 오버레이 미리보기 모드 선택 + 🎯 v6.1 차이 비교 추가
            _preview_mode = st.radio(
                "미리보기 모드",
                ["🌑 DXF 단독", "🖼️ 래스터 오버레이", "🎯 차이 비교 (검수)"],
                index=0,
                key="preview_mode_choice",
                horizontal=True,
                label_visibility="collapsed",
                help="DXF 단독: 변환된 벡터만 | 오버레이: 원본+DXF 겹쳐보기 | 차이 비교: 누락선(빨강)·추가선(청록)·정상(회색) 시각화 — 실무 검수용"
            )

            # 🎚️ v6.2: 오버레이 투명도 슬라이더 — 3순위 신규 기능
            if _preview_mode == "🖼️ 래스터 오버레이":
                _alpha_cols = st.columns([1, 4])
                with _alpha_cols[0]:
                    st.markdown("<div style='font-size:0.74rem;color:#475569;padding-top:6px;font-weight:500;'>🎚️ 원본 투명도</div>", unsafe_allow_html=True)
                with _alpha_cols[1]:
                    _overlay_alpha = st.slider(
                        "원본 투명도",
                        min_value=0.05, max_value=0.95, value=0.40, step=0.05,
                        key="v62_overlay_alpha",
                        label_visibility="collapsed",
                        help="원본 이미지의 투명도를 조절합니다. 낮을수록 DXF 선이 또렷하게 보이고, 높을수록 원본이 잘 보입니다."
                    )
            else:
                _overlay_alpha = 0.40

            with st.spinner("🔄 DXF 변환 렌더링 중..."):
                try:
                    _v6_args = (
                        USE_DESKEW, USE_SPECKLE, MIN_SPECKLE_AREA,
                        USE_GAP_BRIDGE, GAP_BRIDGE_SIZE,
                        USE_DASH_DETECT, USE_LAYER_SPLIT,
                        USE_HATCH_DETECT
                    )
                    preview_dxf = convert_for_preview(
                        selected_bytes, layer_name, image_type, use_ocr,
                        THRESHOLD_VAL, STRAIGHT_TOL, SIMPLIFY_EPS, SPLINE_DENSITY, SMOOTH_WINDOW, EPSILON,
                        USE_HOUGH, CIRCLE_SENS, CIRCLE_MIN_R, CIRCLE_MAX_R, MAX_CIRCLES,
                        USE_PATTERN, USE_SPLINE, USE_GEOMETRY_FITTING, USER_SCALE,
                        use_enhance, SHARPEN_STR, DEDUP_DIST,
                        USE_LINE_FIT, LINE_RMS_THRESH,
                        USE_ANGLE_SNAP, SNAP_TOL_DEG,
                        USE_HOUGH_LINES, HOUGH_MIN_LEN, HOUGH_MAX_GAP, HOUGH_THRESH,
                        MIN_PATH_LEN, STITCH_GAP,
                        use_normalize, NORMALIZE_THICKNESS,
                        # 🌟 v5.0
                        USE_SPUR_PRUNE, SPUR_MAX_LEN,
                        USE_CORNER_ANCHOR, CORNER_ANGLE_DEG,
                        USE_DIR_STITCH, DIR_STITCH_THRESH,
                        # 🆕 v6.0
                        *_v6_args,
                        # 🪄 v6.1
                        USE_AUTO_CLEANUP, CLEANUP_LEVEL,
                        # 🆕 v6.3
                        USE_SUPER_RESOLUTION, SR_THRESHOLD_PX
                    )

                    # 미리보기 모드 분기
                    if _preview_mode == "🖼️ 래스터 오버레이":
                        # 🆕 v6.0: 래스터 오버레이 + 🎚️ v6.2 alpha 슬라이더
                        _ov_fig = render_dxf_overlay_preview(
                            selected_bytes, preview_dxf,
                            raster_alpha=float(_overlay_alpha),
                            bg_color=PREVIEW_BG_COLOR,
                            line_color=PREVIEW_LINE_COLOR
                        )
                        if _ov_fig is not None:
                            st.pyplot(_ov_fig, use_container_width=True)
                            plt.close(_ov_fig)
                            st.caption(f"🖼️ 오버레이: 원본(투명도 {int(_overlay_alpha*100)}%) + DXF 선 겹쳐보기")
                        else:
                            st.info("오버레이 생성에 실패했습니다.")
                        fig = None
                    elif _preview_mode == "🎯 차이 비교 (검수)":
                        # 🎯 v6.1: 누락선 강조 차이 비교 + 🆕 v6.3 Plotly 인터랙티브 줌
                        # Plotly 사용 가능하면 인터랙티브 버전, 아니면 matplotlib fallback
                        _diff_used_plotly = False
                        _ds = None
                        if _PLOTLY_AVAILABLE:
                            _diff_pfig, _ds = render_diff_overlay_plotly(
                                selected_bytes, preview_dxf,
                                bg_color="#ffffff",
                                missing_color="#dc2626",
                                extra_color="#06b6d4",
                                common_color="#9ca3af",
                                line_thickness=2,
                                tolerance=3
                            )
                            if _diff_pfig is not None:
                                st.plotly_chart(_diff_pfig, use_container_width=True, config={
                                    "displaylogo": False,
                                    "scrollZoom": True,
                                    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
                                    "toImageButtonOptions": {"format": "png", "scale": 2, "filename": "diff_compare"},
                                })
                                st.caption("🔍 마우스 휠로 확대 · 드래그로 이동 · 더블클릭으로 리셋")
                                _diff_used_plotly = True

                        if not _diff_used_plotly:
                            # Plotly 미사용 시 기존 matplotlib 방식
                            _diff_fig = render_diff_overlay_preview(
                                selected_bytes, preview_dxf,
                                bg_color="#ffffff",
                                missing_color="#dc2626",
                                extra_color="#06b6d4",
                                common_color="#9ca3af",
                                line_thickness=2,
                                tolerance=3
                            )
                            if _diff_fig is not None:
                                st.pyplot(_diff_fig, use_container_width=True)
                                _ds = getattr(_diff_fig, "_diff_stats", None)
                                plt.close(_diff_fig)
                            else:
                                st.info("차이 비교 생성에 실패했습니다.")

                        # 통계 카드 (Plotly/matplotlib 공통)
                        if _ds:
                            _cov   = _ds["coverage_pct"]
                            _miss  = _ds["missing_pct"]
                            if   _cov >= 90: _cov_color = "#16a34a"
                            elif _cov >= 75: _cov_color = "#0078d4"
                            elif _cov >= 60: _cov_color = "#f59e0b"
                            else:            _cov_color = "#dc2626"
                            st.markdown(f"""
                            <div style='background:#ffffff;border:1px solid #d0d7e0;border-left:3px solid {_cov_color};border-radius:6px;padding:8px 12px;margin-top:6px;'>
                              <div style='display:flex;justify-content:space-between;align-items:center;'>
                                <div style='font-size:0.74rem;color:#5a7a96;font-family:"JetBrains Mono",monospace;'>
                                  <span style='color:#dc2626;font-weight:700;'>● 누락 {_miss:.1f}%</span> ·
                                  <span style='color:#06b6d4;font-weight:700;'>● 추가</span> ·
                                  <span style='color:#9ca3af;font-weight:700;'>● 정상</span>
                                </div>
                                <div style='font-size:0.84rem;font-weight:700;color:{_cov_color};font-family:"JetBrains Mono",monospace;'>
                                  커버리지 {_cov:.1f}%
                                </div>
                              </div>
                              <div style='font-size:0.7rem;color:#7a8fa6;margin-top:3px;'>
                                💡 <b style='color:#dc2626;'>빨간 부분</b>이 DXF에서 빠진 선입니다. 사이드바의 보정 옵션을 조정해보세요.
                              </div>
                            </div>
                            """, unsafe_allow_html=True)
                        fig = None
                    else:
                        fig = render_dxf_preview(preview_dxf, bg_color=PREVIEW_BG_COLOR, line_color=PREVIEW_LINE_COLOR)
                    if fig is None:
                        pass  # 오버레이/차이 비교 모드에서 이미 처리됨
                    elif fig == "EMPTY":
                        st.info("선이 감지되지 않았습니다. 사이드바에서 인식 민감도를 조정해 보세요.")
                    elif isinstance(fig, str):
                        st.warning(f"⚠️ 렌더링 오류:\n```\n{fig}\n```")
                    else:
                        if _PLOTLY_AVAILABLE and hasattr(fig, '_is_plotly'):
                            st.plotly_chart(fig, use_container_width=True, config={
                                "scrollZoom": True,
                                "displayModeBar": True,
                                "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                                "toImageButtonOptions": {"format": "png", "scale": 2},
                            })
                        else:
                            st.pyplot(fig, use_container_width=True)
                            plt.close(fig)
                        # 미리보기 변환 통계 + 품질 점수 미리보기 (v5.0)
                        try:
                            _, _preview_rpt = convert_to_dxf_bytes(
                                selected_bytes, layer_name, image_type, False,
                                THRESHOLD_VAL, STRAIGHT_TOL, SIMPLIFY_EPS, SPLINE_DENSITY, SMOOTH_WINDOW, EPSILON,
                                USE_HOUGH, CIRCLE_SENS, CIRCLE_MIN_R, CIRCLE_MAX_R, MAX_CIRCLES,
                                USE_PATTERN, USE_SPLINE, USE_GEOMETRY_FITTING, USER_SCALE,
                                use_enhance, SHARPEN_STR, DEDUP_DIST,
                                USE_LINE_FIT, LINE_RMS_THRESH,
                                USE_ANGLE_SNAP, SNAP_TOL_DEG,
                                USE_HOUGH_LINES, HOUGH_MIN_LEN, HOUGH_MAX_GAP, HOUGH_THRESH,
                                MIN_PATH_LEN, STITCH_GAP,
                                use_normalize, NORMALIZE_THICKNESS,
                                USE_SPUR_PRUNE, SPUR_MAX_LEN,
                                USE_CORNER_ANCHOR, CORNER_ANGLE_DEG,
                                USE_DIR_STITCH, DIR_STITCH_THRESH,
                                # 🆕 v6.0
                                USE_DESKEW, USE_SPECKLE, MIN_SPECKLE_AREA,
                                USE_GAP_BRIDGE, GAP_BRIDGE_SIZE,
                                USE_DASH_DETECT, USE_LAYER_SPLIT,
                                USE_HATCH_DETECT,
                                # 🪄 v6.1
                                USE_AUTO_CLEANUP, CLEANUP_LEVEL,
                                # 🆕 v6.3
                                USE_SUPER_RESOLUTION, SR_THRESHOLD_PX
                            )
                            _zoom_tip = " · 🔍 휠로 확대" if _PLOTLY_AVAILABLE else ""
                            _q_score = _preview_rpt.get("quality_score", 0)
                            _q_grade = _preview_rpt.get("quality_grade", "-")
                            # 등급별 색상
                            _grade_color = {"A+": "#16a34a", "A": "#16a34a", "B": "#0078d4",
                                            "C": "#f59e0b", "D": "#ea580c", "F": "#dc2626"}.get(_q_grade, "#5a7a96")
                            st.markdown(f"""<div class='prev-info-bar'>
                                <span>📐 선 {_preview_rpt["lines"]}개 · 원 {_preview_rpt["circles"]}개 · <b style='color:{_grade_color}'>품질 {_q_score}/100 · {_q_grade}</b></span>
                                <span>scale {_preview_rpt["scale"]:.2f}{_zoom_tip}</span>
                            </div>""", unsafe_allow_html=True)
                        except Exception:
                            pass
                except Exception as e:
                    st.error(f"❌ 미리보기 실패: {e}")
    else:
        # ── v4.2: 초기 화면 통계 대시보드 (파일 없을 때만 표시) ──
        _lbl_first   = _labels_dates[0] if _labels_dates else ""
        _chart_total = sum(d["count"] for d in _chart_data)
        _dash_html = (
            "<div style='background:#1a3a5c;border-radius:10px;padding:16px 18px 14px 18px;"
            "margin:0 0 12px 0;color:#fff;box-shadow:0 2px 12px rgba(26,58,92,0.22);"
            "border-left:3px solid #0078d4;'>"
            "<div style='font-size:0.65rem;font-weight:600;letter-spacing:0.1em;color:#6b9cc4;"
            "margin-bottom:10px;font-family:\"JetBrains Mono\",monospace;'>📊 USAGE DASHBOARD</div>"
            "<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:12px;'>"
              "<div style='background:#fff;border-radius:6px;padding:8px 12px;box-shadow:0 1px 3px rgba(0,0,0,.1);'>"
                "<div style='font-size:0.62rem;color:#5a7a96;font-weight:500;margin-bottom:2px;'>오늘 접속</div>"
                "<div style='font-size:1.45rem;font-weight:700;color:#1a3a5c;"
                "font-family:\"JetBrains Mono\",monospace;'>{tv}<span style='font-size:.72rem;color:#7a8fa6;margin-left:2px;'>명</span></div>"
              "</div>"
              "<div style='background:#fff;border-radius:6px;padding:8px 12px;box-shadow:0 1px 3px rgba(0,0,0,.1);'>"
                "<div style='font-size:0.62rem;color:#5a7a96;font-weight:500;margin-bottom:2px;'>오늘 변환</div>"
                "<div style='font-size:1.45rem;font-weight:700;color:#1a3a5c;"
                "font-family:\"JetBrains Mono\",monospace;'>{tc}<span style='font-size:.72rem;color:#7a8fa6;margin-left:2px;'>건</span></div>"
              "</div>"
              "<div style='background:#fff;border-radius:6px;padding:8px 12px;box-shadow:0 1px 3px rgba(0,0,0,.1);'>"
                "<div style='font-size:0.62rem;color:#5a7a96;font-weight:500;margin-bottom:2px;'>누적 변환</div>"
                "<div style='font-size:1.45rem;font-weight:700;color:#1a3a5c;"
                "font-family:\"JetBrains Mono\",monospace;'>{vc}<span style='font-size:.72rem;color:#7a8fa6;margin-left:2px;'>건</span></div>"
              "</div>"
              "<div style='background:#fff;border-radius:6px;padding:8px 12px;box-shadow:0 1px 3px rgba(0,0,0,.1);'>"
                "<div style='font-size:0.62rem;color:#5a7a96;font-weight:500;margin-bottom:2px;'>누적 사용자</div>"
                "<div style='font-size:1.45rem;font-weight:700;color:#1a3a5c;"
                "font-family:\"JetBrains Mono\",monospace;'>{vu}<span style='font-size:.72rem;color:#7a8fa6;margin-left:2px;'>명</span></div>"
              "</div>"
            "</div>"
            "<div style='background:rgba(255,255,255,.08);border-radius:6px;padding:10px 12px;'>"
              "<div style='font-size:0.6rem;color:#93c5fd;font-weight:600;letter-spacing:.05em;"
              "margin-bottom:6px;font-family:\"JetBrains Mono\",monospace;'>📈 최근 7일 변환 추이 (총 {ct}건)</div>"
              "<div style='display:flex;align-items:flex-end;gap:4px;height:52px;padding:0 2px;'>{bh}</div>"
              "<div style='display:flex;justify-content:space-between;font-size:0.58rem;"
              "color:#93c5fd;margin-top:4px;font-family:\"JetBrains Mono\",monospace;'>"
                "<span>{lf}</span><span style='color:#60a5fa;font-weight:700;'>오늘</span>"
              "</div>"
            "</div>"
            "</div>"
        ).format(
            tv=_stats["today_visitors"], tc=_stats["today_conv"],
            vc=_stats["total_conv"], vu=_stats["total_users"],
            ct=_chart_total, bh=_bars_html, lf=_lbl_first
        )
        st.markdown(_dash_html, unsafe_allow_html=True)
        st.markdown(
            "<div class='work-panel' style='text-align:center; padding:36px 20px;'>"
            "<div style='font-size:2.6rem;margin-bottom:8px'>📂</div>"
            "<div style='font-size:1.05rem;font-weight:700;color:#1d1d1f;margin-bottom:4px'>변환할 도면 이미지를 올려주세요</div>"
            "<div style='font-size:0.85rem;color:#6e6e73'>파일을 올리시면 원본, 최적화 이미지, DXF 결과물이 3단계로 표시되어 쉽게 확인하실 수 있습니다.</div>"
            "</div>", unsafe_allow_html=True
        )

# ══════════════════════════════════════════
#  🌟 v4.0: 변환 완료 화면 (통계 카드 + 실패 파일 표시)
# ══════════════════════════════════════════
if st.session_state.get("conversion_done", False):
    results = st.session_state.get("dxf_results", [])
    failed_files = st.session_state.get("failed_files", [])
    _conv_image_type = st.session_state.get("conv_image_type", "")
    # 배경 선택값은 session_state radio에서 가져옴 (없으면 기본 Dark)
    _bg_choice_res = st.session_state.get("preview_bg_choice", "🌑 CAD Dark")
    _bg_cfg_res = PREVIEW_BG_OPTIONS.get(_bg_choice_res, PREVIEW_BG_OPTIONS["🌑 CAD Dark"])
    PREVIEW_BG_COLOR = _bg_cfg_res["bg"]
    PREVIEW_LINE_COLOR = _bg_cfg_res["line"]
    col_succ, col_reset = st.columns([4, 1], gap="small")
    with col_succ:
        _success_count = len(results)
        _fail_count = len(failed_files)
        _hdr_color = "#1a3a5c" if _fail_count == 0 else "#92400e"
        _hdr_bg_border = "#38bdf8" if _fail_count == 0 else "#fbbf24"
        _hdr_bg = "#1a3a5c" if _fail_count == 0 else "#b45309"
        _hdr_text = f"✅ 변환 완료! 성공 {_success_count}건"
        if _fail_count > 0:
            _hdr_text += f" · ⚠️ 실패 {_fail_count}건"
        st.markdown(f"<div style='background:{_hdr_bg};color:#ffffff;border-radius:6px;padding:10px 16px;font-size:0.92rem;font-weight:600;border-left:3px solid {_hdr_bg_border};font-family:\"JetBrains Mono\", monospace;letter-spacing:0.02em;'>{_hdr_text}</div>", unsafe_allow_html=True)
    with col_reset:
        st.markdown("<div class='reset-btn'>", unsafe_allow_html=True)
        if st.button("↩ 처음으로 돌아가기", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 🌟 v5.0: 합산 통계 카드 (선/원/텍스트/스케일/품질 점수)
    if results:
        _total_lines = sum(r["report"].get("lines", 0) for r in results)
        _total_circles = sum(r["report"].get("circles", 0) for r in results) + sum(r["report"].get("patterns", 0) for r in results)
        _total_texts = sum(r["report"].get("texts", 0) for r in results)
        _scale = results[0]["report"].get("scale", 0.1) if results else 0.1
        # 🌟 v5.0: 평균 품질 점수
        _q_scores = [r["report"].get("quality_score", 0) for r in results if r["report"].get("quality_score") is not None]
        _avg_q = int(sum(_q_scores) / len(_q_scores)) if _q_scores else 0
        if   _avg_q >= 90: _avg_grade = "A+"; _q_color = "#16a34a"
        elif _avg_q >= 80: _avg_grade = "A";  _q_color = "#22c55e"
        elif _avg_q >= 70: _avg_grade = "B";  _q_color = "#0078d4"
        elif _avg_q >= 60: _avg_grade = "C";  _q_color = "#f59e0b"
        elif _avg_q >= 50: _avg_grade = "D";  _q_color = "#ea580c"
        else:              _avg_grade = "F";  _q_color = "#dc2626"

        st.markdown(f"""
        <div class='result-stats' style='grid-template-columns:repeat(5, 1fr) !important;'>
            <div class='result-stat'>
                <div class='result-stat-num'>{_total_lines:,}</div>
                <div class='result-stat-lbl'>총 선 (LINE)</div>
            </div>
            <div class='result-stat'>
                <div class='result-stat-num'>{_total_circles:,}</div>
                <div class='result-stat-lbl'>총 원 (CIRCLE)</div>
            </div>
            <div class='result-stat'>
                <div class='result-stat-num'>{_total_texts:,}</div>
                <div class='result-stat-lbl'>텍스트 (OCR)</div>
            </div>
            <div class='result-stat'>
                <div class='result-stat-num'>{_scale:.2f}</div>
                <div class='result-stat-lbl'>스케일 (mm/px)</div>
            </div>
            <div class='result-stat' style='border-left:3px solid {_q_color};'>
                <div class='result-stat-num' style='color:{_q_color};'>{_avg_q}<span style='font-size:0.55em;color:{_q_color};margin-left:4px;font-weight:700;'>{_avg_grade}</span></div>
                <div class='result-stat-lbl'>품질 점수 (평균)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 🌟 v5.0: 품질 점수 게이지 바
        _q_pct = max(0, min(100, _avg_q))
        st.markdown(f"""
        <div style='background:#ffffff;border:1px solid #d0d7e0;border-left:3px solid {_q_color};border-radius:6px;padding:10px 14px;margin:0 0 14px 0;box-shadow:0 1px 4px rgba(0,0,0,0.03);'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;'>
                <div style='font-size:0.78rem;font-weight:600;color:#1a3a5c;'>🏆 DXF 품질 게이지</div>
                <div style='font-size:0.72rem;color:#7a8fa6;font-family:"JetBrains Mono",monospace;'>{len(results)}개 파일 평균</div>
            </div>
            <div style='height:14px;background:#f1f5f9;border-radius:7px;overflow:hidden;border:1px solid #e2e8f0;'>
                <div style='height:100%;width:{_q_pct}%;background:linear-gradient(90deg, {_q_color}aa, {_q_color});border-radius:7px;transition:width 0.6s ease;'></div>
            </div>
            <div style='display:flex;justify-content:space-between;font-size:0.66rem;color:#94a3b8;margin-top:4px;font-family:"JetBrains Mono",monospace;'>
                <span>0 · F</span><span>50 · D</span><span>70 · B</span><span>90 · A+</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 🌟 v4.0: 실패 파일 안내
    if failed_files:
        with st.expander(f"⚠️ 변환 실패 파일 {len(failed_files)}개 보기", expanded=False):
            for ff in failed_files:
                st.markdown(f"""
                <div style='background:#fef2f2;border:1px solid #fecaca;border-left:3px solid #ef4444;border-radius:6px;padding:8px 12px;margin-bottom:6px;'>
                    <div style='font-size:0.84rem;font-weight:600;color:#991b1b;'>📄 {ff["name"]}</div>
                    <div style='font-size:0.72rem;color:#7f1d1d;margin-top:3px;font-family:"JetBrains Mono", monospace;'>{ff["error"][:120]}</div>
                </div>
                """, unsafe_allow_html=True)

    if not results:
        # 성공 파일이 0개면 다운로드 섹션 생략
        st.warning("성공한 변환 파일이 없습니다. 위 실패 메시지를 확인하고 다시 시도해 주세요.")
    else:
        preview_idx = st.selectbox("🔍 미리보기 파일", range(len(results)), format_func=lambda i: results[i]["filename"]) if len(results) > 1 else 0

        # 🔁 v6.2: 단일 파일 재변환 — 4순위 신규 기능
        _cur_result = results[preview_idx] if results else None
        if _cur_result is not None:
            _reconv_cols = st.columns([3, 1, 1], gap="small")
            with _reconv_cols[0]:
                _cur_score = _cur_result["report"].get("quality_score", 0)
                _cur_grade = _cur_result["report"].get("quality_grade", "-")
                _grade_clr = {"A+":"#16a34a","A":"#22c55e","B":"#0078d4","C":"#f59e0b","D":"#ea580c","F":"#dc2626"}.get(_cur_grade, "#5a7a96")
                st.markdown(
                    f"<div style='font-size:0.74rem;color:#475569;padding-top:6px;'>"
                    f"📄 <b>{_cur_result['filename']}</b> · "
                    f"<span style='color:{_grade_clr};font-weight:700;font-family:\"JetBrains Mono\",monospace;'>{_cur_grade} {_cur_score}점</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with _reconv_cols[1]:
                # 현재 사이드바 설정으로 이 파일만 재변환
                if st.button("🔁 이 파일만 재변환", use_container_width=True, key="v62_reconv_btn",
                             help="현재 사이드바 설정으로 이 파일을 다시 변환합니다 (다른 파일은 유지)"):
                    st.session_state["v62_do_reconvert"] = True
                    st.session_state["v62_reconv_idx"]  = preview_idx
                    st.rerun()
            with _reconv_cols[2]:
                # 원본 이미지로 다시 만들기 위해, 원본을 session_state에 보관
                _orig_bytes = _cur_result.get("image")
                if _orig_bytes:
                    st.download_button(
                        "📥 원본 이미지",
                        data=_orig_bytes,
                        file_name=f"원본_{os.path.splitext(_cur_result['filename'])[0]}.png",
                        mime="image/png",
                        use_container_width=True,
                        key="v62_dl_orig",
                        help="이 파일의 원본 이미지를 다운로드합니다."
                    )

        # 🔁 v6.2: 재변환 실행 처리
        if st.session_state.get("v62_do_reconvert", False):
            _r_idx = st.session_state.get("v62_reconv_idx", 0)
            if 0 <= _r_idx < len(results):
                _target = results[_r_idx]
                _orig_bytes_re = _target.get("image")
                _saved_kwargs = _target.get("conv_kwargs")
                if _orig_bytes_re and _saved_kwargs:
                    # 현재 사이드바 값으로 변환 인자 갱신
                    # (보관된 kwargs를 베이스로 하되, session_state에 있는 키만 덮어씀)
                    _ss = st.session_state
                    _new_kwargs = dict(_saved_kwargs)  # shallow copy

                    # session_state 키 → conv_kwargs 키 매핑 (있는 것만 덮어쓰기)
                    _key_map = {
                        "sl_threshold":           "t_val",
                        "sl_straight":            "s_tol",
                        "sl_eps":                 "s_eps",
                        "sl_spline":              "s_den",
                        "sl_smooth":              "s_win",
                        "sl_epsilon":             "epsilon",
                        "sl_sharpen":             "sharpen_strength",
                        "sl_dedup":               "dedup_dist",
                        "sl_normalize_thickness": "normalize_thickness",
                        "v6_min_speckle":         "min_speckle_area",
                        "v6_gap_size":            "gap_bridge_size",
                        "v6_line_rms":            "line_rms_thresh",
                        "v6_hough_min":           "hough_min_len",
                        "v6_hough_gap":           "hough_max_gap",
                        "v6_hough_thr":           "hough_thresh",
                        "v6_snap_tol":            "snap_tol_deg",
                        "v6_min_path_len":        "min_path_len",
                        "v6_stitch_gap":          "stitch_gap",
                        # 토글
                        "opt_use_ocr":            "use_ocr",
                        "opt_use_enhance":        "use_enhance",
                        "opt_use_normalize":      "use_normalize",
                        "v6_use_deskew":          "use_deskew",
                        "v6_use_speckle":         "use_speckle",
                        "v6_use_gap_bridge":      "use_gap_bridge",
                        "v6_use_spline":          "use_spline",
                        "v6_use_line_fit":        "use_line_fit",
                        "v6_use_hough_lines":     "use_hough_lines",
                        "v6_use_angle_snap":      "use_angle_snap",
                        "v6_use_dash_detect":     "use_dash_detect",
                        "v6_use_layer_split":     "use_layer_split",
                        "v6_use_hatch_detect":    "use_hatch_detect",
                        "v61_use_auto_cleanup":   "use_auto_cleanup",
                        # 🆕 v6.3
                        "v63_use_sr":             "use_super_resolution",
                        "v63_sr_threshold":       "sr_threshold_px",
                    }
                    _changed = 0
                    for _ss_key, _kw_key in _key_map.items():
                        if _ss_key in _ss:
                            if _new_kwargs.get(_kw_key) != _ss[_ss_key]:
                                _new_kwargs[_kw_key] = _ss[_ss_key]
                                _changed += 1
                    # cleanup_level 별도 처리 (라디오 라벨 → 코드)
                    if "v61_cleanup_level_label" in _ss:
                        _new_cl = {"🟢 약함 (보수적)":"light","🔵 표준 (권장)":"standard","🟠 강함 (적극적)":"strong"}.get(
                            _ss["v61_cleanup_level_label"], "standard"
                        )
                        if _new_kwargs.get("cleanup_level") != _new_cl:
                            _new_kwargs["cleanup_level"] = _new_cl
                            _changed += 1
                    # layer_name, user_scale, image_type은 위젯 key가 없어 갱신 불가 → 변환 시점 값 유지

                    try:
                        with st.spinner(f"🔁 '{_target['filename']}' 재변환 중... ({_changed}개 설정 갱신)"):
                            _new_dxf, _new_report = convert_to_dxf_bytes(_orig_bytes_re, **_new_kwargs)

                        # 결과 갱신 (메모리 + ZIP 재생성). conv_kwargs도 새것으로 교체.
                        results[_r_idx] = {
                            "filename":      _target["filename"],
                            "original_name": _target.get("original_name", _target["filename"]),
                            "content":       _new_dxf,
                            "image":         _orig_bytes_re,
                            "report":        _new_report,
                            "conv_kwargs":   _new_kwargs,
                        }
                        st.session_state["dxf_results"] = results

                        # ZIP 재생성
                        try:
                            _new_zip_buf = io.BytesIO()
                            with zipfile.ZipFile(_new_zip_buf, "w", zipfile.ZIP_DEFLATED) as _zf:
                                for _r in results:
                                    _zf.writestr(_r["filename"], _r["content"])
                            st.session_state["zip_data"] = _new_zip_buf.getvalue()
                        except Exception:
                            pass

                        _new_grade = _new_report.get('quality_grade','-')
                        _new_score = _new_report.get('quality_score',0)
                        _old_grade = _target['report'].get('quality_grade','-')
                        _old_score = _target['report'].get('quality_score',0)
                        st.success(
                            f"✅ '{_target['filename']}' 재변환 완료 — "
                            f"품질 {_old_grade} {_old_score}점 → {_new_grade} {_new_score}점"
                        )
                    except Exception as _re:
                        st.error(f"재변환 실패: {str(_re)[:120]}")
                else:
                    st.warning("원본 이미지 또는 변환 인자 정보를 찾을 수 없습니다. (재변환 기능은 v6.2 이후 변환된 파일에서만 작동합니다)")
            # 플래그 초기화
            st.session_state["v62_do_reconvert"] = False

        # 다운로드 섹션
        # 🆕 v6.7: 실제 저장된 형식 기반으로 표시 (ODA 폴백 여부 반영)
        _fmt_now = st.session_state.get("v66_output_format", "dwg_only")
        # 실제 결과에서 format 필드를 보고 진짜 저장 형식 파악
        _actual_fmts = [r.get("format", "dxf") for r in results]
        _has_dwg = any(f in ("dwg", "both") for f in _actual_fmts)
        _all_fallback = all(f == "dxf" for f in _actual_fmts) and _fmt_now in ("dwg_only", "both")

        if _all_fallback:
            # DWG 요청했는데 전부 DXF로 폴백된 경우 — 명확히 안내
            st.warning(
                "⚠️ DWG 변환을 요청했지만 **ODA File Converter가 설정되지 않아 DXF로 저장**되었습니다.\n\n"
                "사이드바 **'🔧 DWG / AutoCAD 자동 연동'** 에서 ODA 경로를 지정하면 다음 변환부터 DWG로 저장됩니다."
            )
            _fmt_label_show = "⚠️ DXF (DWG 폴백)"
        elif _has_dwg:
            _fmt_label_show = "🏗️ DWG"
        else:
            _fmt_label_show = "📄 DXF"

        st.markdown(
            f"<div style='font-size:0.78rem; font-weight:700; color:#6e6e73; letter-spacing:0.08em; margin-bottom:8px; margin-top:6px;'>"
            f"💾 개별 파일 다운로드 <span style='color:#0078d4;font-size:0.74rem;margin-left:8px;'>저장 형식: {_fmt_label_show}</span></div>",
            unsafe_allow_html=True
        )
        _dl_cols = st.columns(min(len(results), 4), gap="small")
        for idx, r in enumerate(results):
            with _dl_cols[idx % min(len(results), 4)]:
                _r_fmt = r.get("format", "dxf")
                if _r_fmt == "dwg":
                    st.download_button(
                        label=f"🏗️ {r['filename']}",
                        data=r.get("dwg_content", r["content"]),
                        file_name=r["filename"],
                        mime="application/octet-stream",
                        key=f"b_{idx}",
                        use_container_width=True
                    )
                elif _r_fmt == "both":
                    st.download_button(
                        label=f"📄 {r['filename']}",
                        data=r["content"],
                        file_name=r["filename"],
                        mime="application/dxf",
                        key=f"b_{idx}_dxf",
                        use_container_width=True
                    )
                    st.download_button(
                        label=f"🏗️ {r.get('dwg_filename', r['filename'].replace('.dxf','.dwg'))}",
                        data=r.get("dwg_content", b""),
                        file_name=r.get('dwg_filename', r['filename'].replace('.dxf','.dwg')),
                        mime="application/octet-stream",
                        key=f"b_{idx}_dwg",
                        use_container_width=True
                    )
                else:
                    # DXF (폴백 포함)
                    st.download_button(
                        label=f"📄 {r['filename']}",
                        data=r["content"],
                        file_name=r["filename"],
                        mime="application/dxf",
                        key=f"b_{idx}",
                        use_container_width=True
                    )

        # 🌟 v4.0: ZIP 일괄 다운로드 (성공한 것만 + 라벨 명확화)
        st.markdown("<div class='zip-btn' style='margin-top:6px; margin-bottom:10px'>", unsafe_allow_html=True)
        # 🆕 v6.6: 출력 형식에 따라 ZIP 라벨/파일명 변경
        _zip_fmt_label = {
            "dxf_only": ("DXF",     "DXF_변환완료.zip"),
            "dwg_only": ("DWG",     "DWG_변환완료.zip"),
            "both":     ("DXF+DWG", "DXF_DWG_변환완료.zip"),
        }.get(_fmt_now, ("DXF", "DXF_변환완료.zip"))
        _zip_kind, _zip_filename = _zip_fmt_label
        _zip_label = f"📦 성공한 {len(results)}개 ZIP 일괄 다운로드 ({_zip_kind})"
        if failed_files:
            _zip_label += f" (실패 {len(failed_files)}건 제외)"
        st.download_button(
            label=_zip_label,
            data=st.session_state.zip_data,
            file_name=_zip_filename,
            mime="application/zip",
            use_container_width=True,
            key="zip_dl"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # ════════════════════════════════════════════════════════════════
        # 🆕 v6.9: AutoCAD 자동 후처리 섹션
        #   - DXF→DWG 일괄 변환 버튼 제거 (변환 시점에 이미 DWG로 저장되므로 불필요)
        #   - AutoCAD 자동 정리만 유지
        # ════════════════════════════════════════════════════════════════
        if _IS_WINDOWS:
            st.markdown(
                "<div style='font-size:0.78rem; font-weight:700; color:#6e6e73; "
                "letter-spacing:0.08em; margin-top:18px; margin-bottom:8px;'>"
                "🅰️ AutoCAD 자동 정리 "
                "<span style='font-weight:500;color:#9aa3b2;'>"
                "(파일을 AutoCAD로 열어 중복선 제거·폴리라인 결합·자동 저장)"
                "</span></div>",
                unsafe_allow_html=True
            )

            _acad_path = st.session_state.get("v65_acad_path", "")
            _acad_ready = bool(_acad_path) and os.path.isfile(_acad_path)

            if not _acad_ready:
                st.warning(
                    "⚠️ AutoCAD 실행파일 경로가 설정되지 않았습니다.\n\n"
                    "사이드바 **'🔧 DWG/AutoCAD 자동 연동'** 에서 경로를 지정하세요.",
                    icon="⚠️"
                )
                _acad_btn_cols = st.columns(2, gap="medium")
                with _acad_btn_cols[0]:
                    st.button("🅰️ AutoCAD에서 첫 파일 열기", disabled=True, use_container_width=True,
                              key="v65_btn_acad_disabled")
                with _acad_btn_cols[1]:
                    st.button("🅰️ 모든 파일 AutoCAD 자동 정리", disabled=True, use_container_width=True,
                              key="v65_btn_acad_batch_disabled")
            else:
                _acad_btn_cols = st.columns(2, gap="medium")
                # 첫 번째 파일을 AutoCAD에서 자동 정리하며 열기
                _first = results[0] if results else None
                with _acad_btn_cols[0]:
                    if st.button("🅰️ AutoCAD에서 첫 파일 자동 열기",
                                 use_container_width=True, type="primary",
                                 key="v65_btn_acad_open",
                                 help="첫 번째 변환 결과를 AutoCAD에서 자동으로 열고, OVERKILL/PEDIT 등 자동 정리 SCR을 실행합니다."):
                        if _first is None:
                            st.error("변환 결과가 없습니다.")
                        else:
                            # 임시 파일로 저장 후 AutoCAD에 전달
                            _tmp_dir = tempfile.gettempdir()
                            _tmp_dxf = os.path.join(_tmp_dir, _first["filename"])
                            try:
                                with open(_tmp_dxf, "wb") as _tf:
                                    _tf.write(_first["content"])
                                _ok, _msg = open_in_autocad(
                                    _tmp_dxf,
                                    run_cleanup=True,
                                    use_overkill=    st.session_state.get("v65_use_overkill",     True),
                                    use_pedit_join=  st.session_state.get("v65_use_pedit_join",   True),
                                    use_zoom_extents=st.session_state.get("v65_use_zoom_extents", True),
                                    use_purge=       st.session_state.get("v65_use_purge",        False),
                                    auto_save=       st.session_state.get("v65_auto_save",        True),
                                    acad_exe_path=_acad_path,
                                )
                                if _ok:
                                    st.success(_msg)
                                    st.caption(f"📁 임시 경로: `{_tmp_dxf}`")
                                else:
                                    st.error(_msg)
                            except Exception as _ex:
                                st.error(f"❌ 파일 저장 또는 AutoCAD 실행 실패: {_ex}")

                with _acad_btn_cols[1]:
                    # 일괄 AutoCAD 실행 (정리만 자동, 열기는 한 번에 1개씩 권장)
                    if st.button("🅰️ 모든 파일 AutoCAD 자동 정리",
                                 use_container_width=True,
                                 key="v65_btn_acad_batch",
                                 help="모든 변환 결과를 AutoCAD에서 차례로 열어 자동 정리합니다. (큰 작업이므로 신중히 실행)"):
                        with st.spinner(f"🔄 {len(results)}개 파일을 AutoCAD로 순차 실행..."):
                            _batch_msgs = []
                            for _r in results:
                                _tmp_dir = tempfile.gettempdir()
                                _tmp_dxf = os.path.join(_tmp_dir, _r["filename"])
                                try:
                                    with open(_tmp_dxf, "wb") as _tf:
                                        _tf.write(_r["content"])
                                    _ok, _msg = open_in_autocad(
                                        _tmp_dxf,
                                        run_cleanup=True,
                                        use_overkill=    st.session_state.get("v65_use_overkill",     True),
                                        use_pedit_join=  st.session_state.get("v65_use_pedit_join",   True),
                                        use_zoom_extents=st.session_state.get("v65_use_zoom_extents", True),
                                        use_purge=       st.session_state.get("v65_use_purge",        False),
                                        auto_save=       st.session_state.get("v65_auto_save",        True),
                                        acad_exe_path=_acad_path,
                                    )
                                    _batch_msgs.append(f"{'✅' if _ok else '❌'} {_r['filename']}")
                                except Exception as _ex:
                                    _batch_msgs.append(f"❌ {_r['filename']}: {_ex}")
                            st.info("\n\n".join(_batch_msgs[:10]) +
                                    (f"\n\n... 외 {len(_batch_msgs)-10}개" if len(_batch_msgs) > 10 else ""))

            # 자동 후처리 옵션 안내 (활성화된 옵션 보여주기)
            _enabled_opts = []
            if st.session_state.get("v65_use_zoom_extents", True): _enabled_opts.append("🔍 ZOOM E")
            if st.session_state.get("v65_use_overkill",     True): _enabled_opts.append("🔁 OVERKILL")
            if st.session_state.get("v65_use_pedit_join",   True): _enabled_opts.append("🔗 PEDIT JOIN")
            if st.session_state.get("v65_use_purge",        False): _enabled_opts.append("🗑️ PURGE")
            if st.session_state.get("v65_auto_save",        True): _enabled_opts.append("💾 QSAVE")
            if _enabled_opts:
                st.caption(f"⚙️ AutoCAD 자동 정리 실행 항목: {' · '.join(_enabled_opts)}")
        else:
            # Windows 외 환경에서는 안내만 표시
            st.caption("ℹ️ DWG 변환과 AutoCAD 자동 후처리는 Windows 환경에서만 사용 가능합니다.")

        # 🌟 v4.0: 파일별 변환 리포트 expander
        with st.expander(f"📊 파일별 변환 결과 리포트 ({len(results)}개)", expanded=False):
            for idx, r in enumerate(results):
                _rpt = r["report"]
                _orig = r.get("original_name", r["filename"])
                _w = _rpt.get("img_w", 0)
                _h = _rpt.get("img_h", 0)
                _lines = _rpt.get("lines", 0)
                _circles = _rpt.get("circles", 0) + _rpt.get("patterns", 0)
                _texts = _rpt.get("texts", 0)
                _scale = _rpt.get("scale", 0.1)
                _real_w_mm = _w * _scale
                _real_h_mm = _h * _scale
                _warnings = _rpt.get("warnings", [])
                # 🌟 v5.0: 품질 점수 + 등급 + 세부 점수
                _q_score = _rpt.get("quality_score", 0)
                _q_grade = _rpt.get("quality_grade", "-")
                _q_bd = _rpt.get("quality_breakdown", {})
                _bd_cont = _q_bd.get("continuity", 0)
                _bd_geo = _q_bd.get("geometry", 0)
                _bd_clean = _q_bd.get("cleanliness", 0)
                _bd_yield = _q_bd.get("yield", 0)
                # 등급별 색상
                _grade_color = {"A+": "#16a34a", "A": "#22c55e", "B": "#0078d4",
                                "C": "#f59e0b", "D": "#ea580c", "F": "#dc2626"}.get(_q_grade, "#5a7a96")

                st.markdown(f"""
                <div style='background:#ffffff;border:1px solid #d0d7e0;border-left:3px solid {_grade_color};border-radius:6px;padding:10px 14px;margin-bottom:8px;'>
                    <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;'>
                        <div style='font-size:0.86rem;font-weight:600;color:#1a3a5c;'>📄 {_orig}</div>
                        <div style='display:flex;align-items:center;gap:6px;'>
                            <div style='font-size:0.72rem;color:#7a8fa6;font-family:"JetBrains Mono",monospace;'>품질</div>
                            <div style='background:{_grade_color};color:#ffffff;border-radius:4px;padding:2px 8px;font-size:0.72rem;font-weight:700;font-family:"JetBrains Mono",monospace;'>{_q_score}/100</div>
                            <div style='background:{_grade_color}22;color:{_grade_color};border:1px solid {_grade_color}77;border-radius:4px;padding:2px 7px;font-size:0.72rem;font-weight:700;'>{_q_grade}</div>
                        </div>
                    </div>
                    <div style='display:grid;grid-template-columns:repeat(auto-fit, minmax(120px, 1fr));gap:6px;font-size:0.74rem;font-family:"JetBrains Mono", monospace;'>
                        <div style='color:#5a7a96;'>📐 <b style='color:#1a3a5c;'>{_w}×{_h}px</b> (≈ {_real_w_mm:.1f}×{_real_h_mm:.1f}mm)</div>
                        <div style='color:#5a7a96;'>📏 선: <b style='color:#0078d4;'>{_lines}</b>개</div>
                        <div style='color:#5a7a96;'>⭕ 원: <b style='color:#0078d4;'>{_circles}</b>개</div>
                        <div style='color:#5a7a96;'>🔤 텍스트: <b style='color:#0078d4;'>{_texts}</b>개</div>
                    </div>
                    <div style='margin-top:6px;padding-top:6px;border-top:1px dashed #e1e7ef;display:grid;grid-template-columns:repeat(4, 1fr);gap:6px;font-size:0.7rem;color:#7a8fa6;font-family:"JetBrains Mono",monospace;'>
                        <div>연속성 <b style='color:{_grade_color};'>{_bd_cont}</b>/40</div>
                        <div>기하인식 <b style='color:{_grade_color};'>{_bd_geo}</b>/25</div>
                        <div>깔끔함 <b style='color:{_grade_color};'>{_bd_clean}</b>/20</div>
                        <div>변환량 <b style='color:{_grade_color};'>{_bd_yield}</b>/15</div>
                    </div>
                    {"<div style='margin-top:6px;padding-top:6px;border-top:1px dashed #e1e7ef;font-size:0.7rem;color:#7a8fa6;'>" + " · ".join(_warnings[:3]) + "</div>" if _warnings else ""}
                </div>
                """, unsafe_allow_html=True)

        # 미리보기 (하단)
        prev = results[preview_idx]
        rcol_orig, rcol_dxf = st.columns(2, gap="small")
        with rcol_orig:
            st.markdown("""<div class='preview-title before'>
                <span class='prev-step-num s1'>📷</span>
                <span>Before — 원본 이미지</span>
            </div>""", unsafe_allow_html=True)
            st.image(prev["image"], use_container_width=True)
        with rcol_dxf:
            st.markdown("""<div class='preview-title after'>
                <span class='prev-step-num s3'>📐</span>
                <span>After — DXF 결과</span>
            </div>""", unsafe_allow_html=True)
            with st.spinner("DXF 렌더링 중..."):
                fig_or_err = render_dxf_preview(prev["content"], bg_color=PREVIEW_BG_COLOR, line_color=PREVIEW_LINE_COLOR)
            if fig_or_err == "EMPTY": st.info("ℹ️ DXF에 선이 없습니다.")
            elif isinstance(fig_or_err, str): st.warning(f"⚠️ 렌더링 오류:\n```\n{fig_or_err}\n```")
            else:
                if _PLOTLY_AVAILABLE and hasattr(fig_or_err, '_is_plotly'):
                    st.plotly_chart(fig_or_err, use_container_width=True, config={
                        "scrollZoom": True,
                        "displayModeBar": True,
                        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                        "toImageButtonOptions": {"format": "png", "scale": 2},
                    })
                else:
                    st.pyplot(fig_or_err, use_container_width=True)
                    plt.close(fig_or_err)

# 📐 도면 이미지 → DXF/DWG 자동 변환기

**Auto_Web.py v7.3 기반** | 도면팀-이영세

이미지(JPG/PNG)로 된 도면을 AutoCAD에서 편집 가능한 **DXF** 또는 **DWG** 파일로 자동 변환하는 Streamlit 기반 웹 도구입니다.

---

## 🚀 Streamlit Cloud 배포 방법

### 1단계: GitHub에 업로드

1. [github.com](https://github.com) 에서 새 저장소(Repository) 만들기
   - 이름 예: `drawing-converter`
   - Private(비공개) 권장

2. 이 폴더의 파일 3개를 모두 업로드:
   - `app.py` — 메인 프로그램
   - `requirements.txt` — 필요한 패키지 목록
   - `README.md` — 이 안내문

   (선택) `FSRCNN_x2.pb` — AI 고해상도 업스케일 모델 (없으면 해당 기능만 자동 비활성화)
   (선택) `banner_bg.png` — 헤더 배너 이미지

### 2단계: Streamlit Cloud 배포

1. [share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 계정으로 로그인
3. **"New app"** 클릭
4. 저장소 선택 → `app.py` 선택 → **Deploy** 클릭
5. 약 3~5분 후 URL 자동 생성됨

### 3단계: 비공개 설정 (선택)

배포된 앱 → Settings → **Sharing** → "Only specific people" 선택하면 본인 또는 지정한 사람만 접근 가능합니다.

---

## 📦 주요 기능 (v7.3 기준)

### 🩺 v7.3 버그 수정 + 성능
- **OCR 텍스트 마스킹 무효화 수정** — 글자가 선으로 이중 변환되던 문제 해결
- **ARC(호) 방향 오류 수정** — 절반 확률로 반대쪽 호가 그려지던 문제 해결
- **🚀 고속 스켈레톤 토글** — cv2.ximgproc thinning (3~10배 빠름, 자동 폴백)
- **🚀 FLD 직선 추출 토글** — HoughLinesP 대체 엔진 (자동 폴백)
- **해치 인식 → 진짜 HATCH 엔티티** (ANSI31 패턴, 실패 시 SOLID 폴백)
- **저장 직전 doc.audit() 자가수리** — '안 열리는 DXF' 사전 차단
- **활성 옵션 요약 칩 + 변환 버튼 sticky 고정**

### ⚡ v7.0~v7.2 핵심 기능
- **배치 병렬 변환** — 다중 파일 2~4배 빠름 (OCR ON 시 자동 순차 전환)
- **🔍 CAD QA 자동 검수 리포트** — 미폐합/중복선/0길이선/레이어/텍스트 5종 검사 + 점수·등급
- **⚡ 자동 최적 변환** 원클릭 버튼 + **빠른 미리보기** (중앙 400px)
- **끊긴 외곽선 자동 폐합** 후처리 (OUTLINE_CLOSED 레이어)
- **선 굵기 복원(Lineweight)** + **곡률 기반 SPLINE 자동 감지**
- **변환 이력 설정 복원** (자동 프리셋) + **A/B 품질 비교**
- **작업자 이름 스탬프** — 브라우저별 자동 식별(localStorage), 첫 방문 시 이름 입력
- **예상 남은 시간(ETA) 진행률** + 실패 파일 즉시 표시 + 첫 사용 온보딩 가이드

### 🎨 변환 품질
- **이진화 blockSize 자동 계산** — 해상도에 비례해 자동 조정
- **MORPH_CLOSE** — 1~2px 미세 끊김선 자동 연결
- **Closed Path 자동 인식** — 닫힌 도형 CAD에서 닫힌 객체로 인식
- **Adaptive Epsilon** — path 길이에 비례한 단순화
- **AI 슬라이더 수치 추천** — 이미지 분석 기반 자동 최적값 제안

### 🔍 검수 도구
- **3단 미리보기** — 원본·전처리·DXF 결과 동시 비교
- **슬라이드 비교 뷰어** + Before/After 비교
- **Plotly 인터랙티브 차이 비교** — 줌/패닝으로 누락선 정밀 검수
- **시각적 Crop** — 마우스 드래그로 변환 영역 선택

### 📤 출력 형식
- **DXF 저장** (모든 환경) — AutoCAD에서 정상 열림
- **DWG 저장** (Windows 로컬 환경 전용) — ODA File Converter 필요
- **원본이름 그대로 저장** — `핸드폰.jpg` → `핸드폰.dxf` (중복 시 자동 번호)

### 📂 지원 입력 형식
- JPG / JPEG / PNG / BMP / WEBP
- 다중 파일 일괄 처리 가능

---

## 🌐 웹 배포본의 제한사항

**Streamlit Cloud 환경은 Linux 서버**라서 다음 기능은 자동 비활성화됩니다:

| 기능 | 웹 배포 | 로컬 Windows |
|:---|:---:|:---:|
| 이미지 → DXF 변환 | ✅ | ✅ |
| 배치 병렬 변환 (v7.0) | ✅ | ✅ |
| CAD QA 자동 검수 (v7.0) | ✅ | ✅ |
| AI 슬라이더 추천 / 품질 분석 | ✅ | ✅ |
| 변환 이력 관리 / 작업자 스탬프 | ✅ | ✅ |
| 시각적 Crop | ✅ | ✅ |
| OCR 텍스트 인식 | ⚠️ easyocr 설치 시만 (requirements 주석 해제) | ✅ |
| AI 고해상도 업스케일 (FSRCNN) | ⚠️ 모델 파일 별도 업로드 필요 | ✅ |
| **DWG 자동 변환** | ❌ → DXF로 자동 저장 | ✅ |
| **AutoCAD 자동 후처리** | ❌ | ✅ |

**👉 웹에서 DXF로 받으신 후 AutoCAD에서 열어 DWG로 저장하시면 됩니다.**

---

## 🛠️ 로컬 Windows에서 실행하기 (모든 기능 사용)

DWG 자동 변환과 AutoCAD 자동 후처리까지 사용하려면 로컬에서 실행하세요.

### 필요 환경
- Windows 10/11
- Python 3.11 (Python 3.14는 opencv-contrib-python 호환 문제로 미지원)
- (선택) ODA File Converter — DWG 변환용 무료 도구: [https://www.opendesign.com/guestfiles/oda_file_converter](https://www.opendesign.com/guestfiles/oda_file_converter)
- (선택) AutoCAD — 자동 후처리용

### 설치 및 실행
```cmd
pip install -r requirements.txt
py -3.11 -m streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

---

## 📋 출력 파일 규칙

| 입력 | 출력 (DXF) | 출력 (DWG) |
|:---|:---|:---|
| `핸드폰.jpg` | `핸드폰.dxf` | `핸드폰.dwg` |
| 같은 이름 중복 시 | `핸드폰 (2).dxf` | `핸드폰 (2).dwg` |

---

## 📝 라이선스

내부 도면팀 사용 도구 (도면팀-이영세)

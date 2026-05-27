# 📐 도면 이미지 → DXF/DWG 자동 변환기

**Auto_Web.py v6.9 기반** | 도면팀-이영세

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

### 2단계: Streamlit Cloud 배포

1. [share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 계정으로 로그인
3. **"New app"** 클릭
4. 저장소 선택 → `app.py` 선택 → **Deploy** 클릭
5. 약 3~5분 후 URL 자동 생성됨

### 3단계: 비공개 설정 (선택)

배포된 앱 → Settings → **Sharing** → "Only specific people" 선택하면 본인 또는 지정한 사람만 접근 가능합니다.

---

## 📦 주요 기능 (v6.9 기준)

### 🎨 변환 품질 (v6.4 개선)
- **이진화 blockSize 자동 계산** — 해상도에 비례해 자동 조정 (1000px→15, 4000px→61)
- **MORPH_CLOSE 추가** — 1~2px 미세 끊김선 자동 연결
- **Closed Path 자동 인식** — 닫힌 도형(사각형·원형) CAD에서 닫힌 객체로 인식
- **Adaptive Epsilon** — path 길이에 비례한 단순화 (짧은 path 형태 보존, 긴 path 노드 절감)
- **Smooth Window 자동 상한** — 짧은 원/호 형태 손상 방지

### ⚡ 사용 편의성
- **퀵 변환 3단계 버튼** — ⚡빠름 / ⚖️균형 / 🔬정밀 원클릭
- **슬라이더 숫자 직접 입력** — 정밀 조정 가능
- **AI 슬라이더 수치 추천** — 이미지 분석 기반 자동 최적값 제안
- **사용자 정의 프리셋** — 회사별/프로젝트별 설정 저장
- **변환 이력 관리** — SQLite 기반 최근 15건 조회
- **품질 점수 + 등급** — DXF 결과를 0~100점 + A+~F 자동 평가

### 🔍 검수 도구
- **3단 미리보기** — 원본·전처리·DXF 결과 동시 비교
- **Before/After 비교**
- **Plotly 인터랙티브 차이 비교** — 줌/패닝으로 누락선 정밀 검수
- **시각적 Crop** — 마우스 드래그로 변환 영역 선택

### 📤 출력 형식
- **DXF 저장** (모든 환경) — AutoCAD에서 정상 열림
- **DWG 저장** (Windows 로컬 환경 전용) — ODA File Converter 필요
- **원본이름 그대로 저장** — `핸드폰.jpg` → `핸드폰.dxf` 형식 (중복 시 자동 번호)

### 🅰️ AutoCAD 자동 후처리 (Windows 로컬 환경 전용)
- AutoCAD 자동 실행 + OVERKILL(중복선 제거) + PEDIT JOIN(분리선 결합) + 자동 저장
- 일괄 처리 가능

### 📂 지원 입력 형식
- JPG / JPEG / PNG / BMP / WEBP
- 다중 파일 일괄 처리 가능

---

## 🌐 웹 배포본의 제한사항

**Streamlit Cloud 환경은 Linux 서버**라서 다음 기능은 자동 비활성화됩니다:

| 기능 | 웹 배포 | 로컬 Windows |
|:---|:---:|:---:|
| 이미지 → DXF 변환 | ✅ | ✅ |
| AI 슬라이더 추천 | ✅ | ✅ |
| 품질 분석/검수 | ✅ | ✅ |
| 변환 이력 관리 | ✅ | ✅ |
| 시각적 Crop | ✅ | ✅ |
| OCR 텍스트 인식 | ✅ | ✅ |
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

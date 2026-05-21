# 📐 도면 DXF 변환기 — 웹 배포 버전

Auto_Web.py v6.3 기반 | 도면팀-이영세

## 🚀 Streamlit Cloud 배포 방법

### 1단계: GitHub에 올리기
1. [github.com](https://github.com) 에서 새 저장소(Repository) 만들기
   - 이름 예: `drawing-converter`
   - Private(비공개) 선택
2. 이 폴더 안 파일 3개를 모두 업로드:
   - `app.py`
   - `requirements.txt`
   - `README.md`

### 2단계: Streamlit Cloud 배포
1. [share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 계정으로 로그인
3. **"New app"** 클릭
4. 저장소 선택 → `app.py` 선택 → **Deploy** 클릭
5. 약 3~5분 후 URL 자동 생성됨!

### 3단계: 비공개 설정 (본인만 접근)
배포된 앱 → Settings → **Sharing** → "Only specific people" 선택

## 📦 포함된 기능
- JPG/PNG 도면 → DXF 변환 (다중 파일)
- 스켈레톤 기반 선 추출
- 원·호 자동 인식 (HoughCircles)
- Before/After 미리보기
- 개별 + ZIP 일괄 다운로드
- 변환 리포트

## ⚠️ 제거된 기능 (웹 최적화)
- OCR 텍스트 인식 (easyocr - 너무 무거움)
- AI 고해상도 업스케일 (FSRCNN 모델 파일 필요)
- 변환 이력 SQLite DB
- 시각적 크롭 (streamlit-canvas)

# AI 강의노트 퀴즈 생성기

PDF 강의노트를 업로드하면 생성형 AI가 자동으로 다양한 퀴즈를 생성하는 Streamlit 웹 애플리케이션입니다.

## 주요 기능

- 📄 PDF 강의노트 업로드
- 🤖 Google Gemini를 활용한 동적 퀴즈 생성 (매번 다른 퀴즈)
- 📝 다양한 퀴즈 유형: 객관식, 주관식, OX 퀴즈
- 📊 자동 채점 및 해설 제공
- ⚙️ 퀴즈 개수 및 유형 커스터마이징

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. `.env` 파일 생성 및 Gemini API 키 설정:
```bash
copy .env.example .env
```
그 다음 `.env` 파일을 열어 Gemini API 키를 입력하세요.

## 실행 방법

### 로컬 실행
```bash
streamlit run app.py
```

브라우저에서 자동으로 열립니다 (기본: http://localhost:8501)

### Streamlit Cloud 배포

1. [Streamlit Cloud](https://streamlit.io/cloud)에 로그인
2. "New app" 클릭
3. GitHub 저장소 선택: `jeilcom/Quiz`
4. Main file path: `app.py`
5. Deploy 클릭
6. 배포 후 Settings에서 Secrets 설정 (선택사항):
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   ```

## 사용 방법

1. 사이드바에서 퀴즈 개수와 유형을 선택
2. PDF 강의노트 파일 업로드
3. "퀴즈 생성하기" 버튼 클릭
4. 생성된 퀴즈 풀기
5. "채점하기" 버튼으로 결과 확인

## 참고사항

- Google Gemini API 키가 필요합니다 (https://aistudio.google.com/app/apikey)
- PDF 파일은 텍스트 추출이 가능한 형식이어야 합니다
- 매번 다른 퀴즈가 생성됩니다 (temperature=0.8 설정)

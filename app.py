import streamlit as st
import PyPDF2
import io
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

st.set_page_config(page_title="AI 퀴즈 생성기", page_icon="📚", layout="wide")

def extract_text_from_pdf(pdf_file):
    """PDF 파일에서 텍스트 추출"""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def generate_quiz(lecture_content, num_questions=5, quiz_types=None):
    """생성형 AI를 사용하여 퀴즈 생성"""
    if quiz_types is None:
        quiz_types = ["객관식", "주관식", "OX", "짝짓기"]
    
    quiz_types_str = ", ".join(quiz_types)
    
    prompt = f"""당신은 교육 전문가입니다. 다음 강의 노트 내용을 바탕으로 {num_questions}개의 퀴즈를 생성해주세요.
퀴즈 유형: {quiz_types_str}

강의 노트:
{lecture_content[:3000]}

다음 JSON 형식으로만 응답해주세요 (다른 텍스트 없이):
{{
    "quizzes": [
        {{
            "type": "객관식" 또는 "주관식" 또는 "OX" 또는 "짝짓기",
            "question": "질문 내용",
            "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
            "pairs": {{"항목1": "설명1", "항목2": "설명2", "항목3": "설명3"}},
            "answer": "정답",
            "explanation": "해설"
        }}
    ]
}}

주의사항:
- 객관식 퀴즈는 반드시 options 배열을 포함해야 합니다
- OX 퀴즈의 answer는 "O" 또는 "X"만 사용
- 주관식 퀴즈는 options 없이 answer만 제공
- 짝짓기 퀴즈는 pairs 객체를 포함하고, answer는 "항목1-설명1, 항목2-설명2, 항목3-설명3" 형식으로 제공
- 각 퀴즈는 강의 내용의 핵심 개념을 다루어야 합니다
- 매번 다른 질문이 생성되도록 다양한 관점에서 출제해주세요"""

    try:
        # gemini-2.5-flash 모델 사용
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.8,  # 다양성을 위해 높은 temperature 설정
                response_mime_type="application/json"
            )
        )
        
        quiz_data = json.loads(response.text)
        return quiz_data["quizzes"]
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            st.error("⚠️ API 할당량을 초과했습니다. 잠시 후 다시 시도해주세요.")
            st.info("💡 팁: 새로운 API 키를 발급받거나, 몇 분 후에 다시 시도해보세요.")
        elif "404" in error_msg:
            st.error("⚠️ 모델을 찾을 수 없습니다. API 키가 올바른지 확인해주세요.")
        else:
            st.error(f"퀴즈 생성 중 오류 발생: {error_msg}")
        return None

def main():
    st.title("📚 AI 강의노트 퀴즈 생성기")
    st.markdown("강의노트 PDF를 업로드하면 AI가 자동으로 퀴즈를 생성합니다!")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("🔑 API 키 설정")
        
        # 환경변수에서 API 키 가져오기 (있으면)
        default_api_key = os.getenv("GEMINI_API_KEY", "")
        
        api_key = st.text_input(
            "Gemini API 키를 입력하세요",
            value=default_api_key if default_api_key != "your_gemini_api_key_here" else "",
            type="password",
            help="https://aistudio.google.com/app/apikey 에서 무료로 발급받을 수 있습니다"
        )
        
        if api_key:
            genai.configure(api_key=api_key)
            st.success("✅ API 키가 설정되었습니다")
        else:
            st.warning("⚠️ API 키를 입력해주세요")
        
        st.markdown("---")
        
        st.header("⚙️ 퀴즈 설정")
        num_questions = st.slider("생성할 퀴즈 개수", 1, 10, 5)
        
        st.subheader("퀴즈 유형 선택")
        quiz_types = []
        if st.checkbox("객관식", value=True):
            quiz_types.append("객관식")
        if st.checkbox("주관식", value=True):
            quiz_types.append("주관식")
        if st.checkbox("OX 퀴즈", value=True):
            quiz_types.append("OX")
        if st.checkbox("짝짓기", value=True):
            quiz_types.append("짝짓기")
        
        if not quiz_types:
            st.warning("최소 하나의 퀴즈 유형을 선택해주세요.")
    
    # 메인 영역
    uploaded_file = st.file_uploader("강의노트 PDF 파일을 업로드하세요", type=['pdf'])
    
    if uploaded_file is not None:
        st.success(f"✅ 파일 업로드 완료: {uploaded_file.name}")
        
        # PDF 텍스트 추출
        with st.spinner("PDF 내용을 분석하는 중..."):
            lecture_text = extract_text_from_pdf(uploaded_file)
            st.info(f"📄 추출된 텍스트 길이: {len(lecture_text)} 자")
        
        # 퀴즈 생성 버튼
        if st.button("🎯 퀴즈 생성하기", type="primary", use_container_width=True):
            if not api_key:
                st.error("먼저 사이드바에서 Gemini API 키를 입력해주세요.")
                return
            
            if not quiz_types:
                st.error("퀴즈 유형을 최소 하나 선택해주세요.")
                return
            
            with st.spinner("AI가 퀴즈를 생성하는 중... 잠시만 기다려주세요."):
                quizzes = generate_quiz(lecture_text, num_questions, quiz_types)
            
            if quizzes:
                st.success(f"✨ {len(quizzes)}개의 퀴즈가 생성되었습니다!")
                
                # 세션 상태에 퀴즈 저장
                if 'quizzes' not in st.session_state:
                    st.session_state.quizzes = quizzes
                    st.session_state.user_answers = {}
                    st.session_state.show_results = False
                else:
                    st.session_state.quizzes = quizzes
                    st.session_state.user_answers = {}
                    st.session_state.show_results = False
    
    # 퀴즈 표시
    if 'quizzes' in st.session_state and st.session_state.quizzes:
        st.markdown("---")
        st.header("📝 퀴즈")
        
        for idx, quiz in enumerate(st.session_state.quizzes):
            with st.container():
                st.subheader(f"문제 {idx + 1} [{quiz['type']}]")
                st.markdown(f"**{quiz['question']}**")
                
                # 퀴즈 유형별 입력
                if quiz['type'] == "객관식":
                    answer = st.radio(
                        "답을 선택하세요:",
                        quiz.get('options', []),
                        key=f"q_{idx}",
                        index=None
                    )
                    if answer:
                        st.session_state.user_answers[idx] = answer
                
                elif quiz['type'] == "OX":
                    answer = st.radio(
                        "답을 선택하세요:",
                        ["O", "X"],
                        key=f"q_{idx}",
                        index=None
                    )
                    if answer:
                        st.session_state.user_answers[idx] = answer
                
                elif quiz['type'] == "주관식":
                    answer = st.text_input(
                        "답을 입력하세요:",
                        key=f"q_{idx}"
                    )
                    if answer:
                        st.session_state.user_answers[idx] = answer
                
                elif quiz['type'] == "짝짓기":
                    st.markdown("**왼쪽 항목과 오른쪽 설명을 매칭하세요:**")
                    pairs = quiz.get('pairs', {})
                    
                    if pairs:
                        items = list(pairs.keys())
                        descriptions = list(pairs.values())
                        
                        # 왼쪽 항목 표시
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**항목**")
                            for i, item in enumerate(items):
                                st.markdown(f"{i+1}. {item}")
                        
                        with col2:
                            st.markdown("**설명**")
                            for i, desc in enumerate(descriptions):
                                st.markdown(f"{chr(65+i)}. {desc}")
                        
                        # 사용자 답변 입력
                        st.markdown("**매칭 결과를 입력하세요 (예: 1-A, 2-B, 3-C):**")
                        user_matching = st.text_input(
                            "답변:",
                            key=f"q_{idx}",
                            placeholder="1-A, 2-B, 3-C"
                        )
                        if user_matching:
                            st.session_state.user_answers[idx] = user_matching
                
                st.markdown("---")
        
        # 제출 버튼
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📊 채점하기", type="primary", use_container_width=True):
                st.session_state.show_results = True
        
        # 결과 표시
        if st.session_state.show_results:
            st.markdown("---")
            st.header("📊 채점 결과")
            
            correct_count = 0
            for idx, quiz in enumerate(st.session_state.quizzes):
                user_answer = st.session_state.user_answers.get(idx, "")
                correct_answer = quiz['answer']
                
                # 짝짓기 문제는 순서 무관하게 비교
                if quiz['type'] == "짝짓기":
                    user_pairs = set(pair.strip() for pair in str(user_answer).split(','))
                    correct_pairs = set(pair.strip() for pair in str(correct_answer).split(','))
                    is_correct = user_pairs == correct_pairs
                else:
                    is_correct = str(user_answer).strip().lower() == str(correct_answer).strip().lower()
                
                if is_correct:
                    correct_count += 1
                
                with st.expander(f"문제 {idx + 1} - {'✅ 정답' if is_correct else '❌ 오답'}"):
                    st.markdown(f"**질문:** {quiz['question']}")
                    st.markdown(f"**당신의 답:** {user_answer if user_answer else '(답변 없음)'}")
                    st.markdown(f"**정답:** {correct_answer}")
                    st.markdown(f"**해설:** {quiz['explanation']}")
            
            score = (correct_count / len(st.session_state.quizzes)) * 100
            st.metric("최종 점수", f"{score:.1f}점", f"{correct_count}/{len(st.session_state.quizzes)} 정답")
            
            if score >= 80:
                st.balloons()
                st.success("🎉 훌륭합니다! 강의 내용을 잘 이해하셨네요!")
            elif score >= 60:
                st.info("👍 좋아요! 조금만 더 복습하면 완벽할 거예요!")
            else:
                st.warning("💪 다시 한번 강의노트를 복습해보세요!")

if __name__ == "__main__":
    main()

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from PyPDF2 import PdfReader
import openai
import json

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# OpenAI API 키 설정 (환경변수에서 가져오기)
openai.api_key = os.getenv('OPENAI_API_KEY')

def extract_text_from_pdf(pdf_path):
    """PDF에서 텍스트 추출"""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def generate_quiz(content, num_questions=5):
    """생성형 AI를 사용하여 퀴즈 생성"""
    prompt = f"""
다음 강의 노트 내용을 분석하여 {num_questions}개의 다양한 형태의 퀴즈를 생성해주세요.

퀴즈 형태:
- 객관식 (4지선다)
- O/X 문제
- 단답형
- 서술형

각 퀴즈는 다음 JSON 형식으로 작성해주세요:
{{
  "questions": [
    {{
      "type": "multiple_choice",
      "question": "질문 내용",
      "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
      "correct_answer": "정답",
      "explanation": "해설"
    }},
    {{
      "type": "true_false",
      "question": "질문 내용",
      "correct_answer": "O 또는 X",
      "explanation": "해설"
    }},
    {{
      "type": "short_answer",
      "question": "질문 내용",
      "correct_answer": "정답",
      "explanation": "해설"
    }}
  ]
}}

강의 노트 내용:
{content[:3000]}

JSON 형식으로만 응답해주세요.
"""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 교육 전문가입니다. 강의 내용을 분석하여 효과적인 퀴즈를 생성합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        quiz_data = json.loads(response.choices[0].message.content)
        return quiz_data
    except Exception as e:
        print(f"AI 퀴즈 생성 오류: {e}")
        return None

@app.route('/upload', methods=['POST'])
def upload_pdf():
    """PDF 파일 업로드 및 퀴즈 생성"""
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '파일이 선택되지 않았습니다'}), 400
    
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'PDF 파일만 업로드 가능합니다'}), 400
    
    # 파일 저장
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    # PDF 텍스트 추출
    try:
        content = extract_text_from_pdf(filepath)
    except Exception as e:
        return jsonify({'error': f'PDF 읽기 오류: {str(e)}'}), 500
    
    # 퀴즈 개수 (요청에서 받거나 기본값 5)
    num_questions = int(request.form.get('num_questions', 5))
    
    # AI로 퀴즈 생성
    quiz_data = generate_quiz(content, num_questions)
    
    if quiz_data is None:
        return jsonify({'error': '퀴즈 생성 실패'}), 500
    
    return jsonify({
        'success': True,
        'filename': file.filename,
        'quiz': quiz_data
    })

@app.route('/health', methods=['GET'])
def health():
    """서버 상태 확인"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

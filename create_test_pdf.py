from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def create_test_lecture_pdf():
    """테스트용 강의노트 PDF 생성"""
    filename = "test_lecture.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # 제목
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1*inch, height - 1*inch, "Python 프로그래밍 기초")
    
    # 내용
    c.setFont("Helvetica", 12)
    y_position = height - 1.5*inch
    
    content = [
        "1. 변수와 데이터 타입",
        "",
        "변수는 데이터를 저장하는 공간입니다.",
        "Python의 주요 데이터 타입:",
        "- 정수형(int): 1, 2, 3, -5",
        "- 실수형(float): 3.14, 2.5",
        "- 문자열(str): 'hello', \"world\"",
        "- 불린(bool): True, False",
        "",
        "2. 조건문",
        "",
        "if 문은 조건에 따라 코드를 실행합니다.",
        "예시:",
        "if x > 0:",
        "    print('양수입니다')",
        "else:",
        "    print('음수 또는 0입니다')",
        "",
        "3. 반복문",
        "",
        "for 문은 시퀀스를 반복합니다.",
        "while 문은 조건이 참인 동안 반복합니다.",
        "",
        "4. 함수",
        "",
        "함수는 재사용 가능한 코드 블록입니다.",
        "def 키워드로 정의합니다.",
        "예시:",
        "def add(a, b):",
        "    return a + b",
        "",
        "5. 리스트와 딕셔너리",
        "",
        "리스트는 순서가 있는 데이터 집합입니다.",
        "딕셔너리는 키-값 쌍으로 데이터를 저장합니다.",
    ]
    
    for line in content:
        c.drawString(1*inch, y_position, line)
        y_position -= 0.25*inch
        
        if y_position < 1*inch:
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - 1*inch
    
    c.save()
    print(f"테스트 PDF 생성 완료: {filename}")

if __name__ == "__main__":
    create_test_lecture_pdf()

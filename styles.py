# styles.py — 공통 색상 및 스타일 정의
# ✏️ 색상 바꾸고 싶으면 여기만 수정하면 전체 반영됨

PRIMARY   = "#0e9db5"   # 헤더, 버튼 메인 색상 (청녹색)
PRIMARY_DARK = "#0a7a8f"
BG        = "#f4fbfc"   # 전체 배경
INPUT_BG  = "#f4fbfc"   # 입력창 배경
BORDER    = "#b2dce4"   # 테두리 색
TEXT_MAIN = "#1a2a3a"   # 본문 텍스트
TEXT_SUB  = "#5a8a92"   # 보조 텍스트
WARNING   = "#fff8e1"   # 경고 박스 배경
WARNING_BORDER = "#ffc107"

WINDOW_STYLE = f"""
    QWidget {{
        background-color: {BG};
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
        font-size: 13px;
        color: {TEXT_MAIN};
    }}
    QLineEdit {{
        background: white;
        border: 1.5px solid {BORDER};
        border-radius: 7px;
        padding: 8px 12px;
        font-size: 13px;
        color: {TEXT_MAIN};
    }}
    QLineEdit:focus {{
        border: 1.5px solid {PRIMARY};
    }}
    QTextEdit {{
        background: white;
        border: 1.5px solid {BORDER};
        border-radius: 7px;
        padding: 8px 12px;
        font-size: 13px;
    }}
    QTextEdit:focus {{
        border: 1.5px solid {PRIMARY};
    }}
    QPushButton {{
        border-radius: 7px;
        padding: 9px 0;
        font-size: 13px;
        font-weight: bold;
    }}
    QListWidget {{
        background: white;
        border: 1.5px solid {BORDER};
        border-radius: 7px;
        padding: 4px;
    }}
    QListWidget::item {{
        padding: 10px 12px;
        border-bottom: 1px solid {BORDER};
    }}
    QListWidget::item:selected {{
        background: #e0f5f8;
        color: {PRIMARY_DARK};
    }}
"""

BTN_PRIMARY = f"""
    QPushButton {{
        background-color: {PRIMARY};
        color: white;
        border: none;
        border-radius: 7px;
        padding: 10px 0;
        font-size: 13px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {PRIMARY_DARK};
    }}
"""

BTN_OUTLINE = f"""
    QPushButton {{
        background-color: white;
        color: {PRIMARY};
        border: 1.5px solid {PRIMARY};
        border-radius: 7px;
        padding: 9px 0;
        font-size: 13px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: #e0f5f8;
    }}
"""

BTN_DANGER = f"""
    QPushButton {{
        background-color: white;
        color: #e74c3c;
        border: 1.5px solid #e74c3c;
        border-radius: 7px;
        padding: 9px 0;
        font-size: 13px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: #fdecea;
    }}
"""

LABEL_TITLE = f"""
    QLabel {{
        font-size: 20px;
        font-weight: bold;
        color: {PRIMARY};
        padding: 8px 0;
    }}
"""

LABEL_FIELD = f"""
    QLabel {{
        font-size: 11px;
        font-weight: bold;
        color: {TEXT_SUB};
        padding: 0;
    }}
"""

LABEL_HEADER = f"""
    QLabel {{
        background-color: {PRIMARY};
        color: white;
        font-size: 15px;
        font-weight: bold;
        padding: 14px 20px;
        border-radius: 0px;
    }}
"""

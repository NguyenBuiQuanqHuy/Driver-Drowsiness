# themes.py

DARK_THEME = """
QWidget {
    background-color: #0b132b;
    color: white;
}

QPushButton {
    background-color: #1c2541;
    border: 2px solid #5bc0be;
    padding: 10px;
    border-radius: 10px;
}

QPushButton:hover {
    background-color: #5bc0be;
    color: black;
}

QLabel {
    color: white;
    font-weight: bold;
}

QFrame QLabel#value[alert="true"],
QFrame QLabel#timeValue[alert="true"],
QLabel[alert="true"] {
    color: #ff4d4d;
    font-weight: bold;
}

QFrame {
    background-color: #1c2541;
    border: 2px solid #5bc0be;
    border-radius: 10px;
    padding: 10px;
}

QComboBox {
    background-color: #1c2541;
    color: white;
    border: 2px solid #5bc0be;
    border-radius: 8px;
    padding: 5px;
}

QLabel[alert="true"] {
    color: #ff4d4d;
    font-weight: bold;
}
"""

LIGHT_THEME = """
QWidget {
    background-color: white;
    color: black;
}

QPushButton {
    background-color: #e0e0e0;
    border: 2px solid #999;
    padding: 10px;
    border-radius: 10px;
    color: black;
}

QPushButton:hover {
    background-color: #cfcfcf;
}

QLabel {
    color: black;
    font-weight: bold;
}

QFrame QLabel#value[alert="true"],
QFrame QLabel#timeValue[alert="true"],
QLabel[alert="true"] {
    color: red;
    font-weight: bold;
}

QFrame {
    background-color: #f0f0f0;
    border: 2px solid #999;
    border-radius: 10px;
    padding: 10px;
}

QComboBox {
    background-color: #f0f0f0;
    color: black;
    border: 2px solid #999;
    border-radius: 8px;
    padding: 5px;
}

QLabel[alert="true"] {
    color: red;
    font-weight: bold;
}
"""
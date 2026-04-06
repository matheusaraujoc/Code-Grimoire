"""
widgets.py - Componentes reutilizáveis do CodeGrimoire
"""

import os
import re
import base64
import tempfile

from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QPushButton, QTextBrowser, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QTextCharFormat, QSyntaxHighlighter
from theme import SYNTAX_COLORS

# ─────────────────────────────────────────────────────────────────
#  ÍCONES PNG — gerados via Pillow e embutidos em base64.
#  O Qt NÃO suporta data URI em image: url() no QSS,
#  então extraímos os arquivos para temp/ na primeira execução.
# ─────────────────────────────────────────────────────────────────

_CHECK_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAUUlEQVR4nOWQORIAIAgDif//M7bIZYbGwnTOsEtQ5L+oqtr3msBWQgssBACjBh6mBf7uUpANVtWDIPugG3wI7IBvUsHhhE5CCbJt3fY2bIP32S6VNAMqhrDYAAAAAElFTkSuQmCC"
_DASH_PNG_B64  = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAh0lEQVR4nNySwQnAIAxFU/HiwR0cpY7SyTqK3aTdwYMXkSYFi7RNKHjzQ1CS/CfBaOiUhk6NBEgpOTqNMYdkePaptlhKCTHGmTNTDXv2nLOruRtARKWUx1i/IJTDWkCAt9ZuL4AE4cykCZg5aRyM5XqFMbOAFoJXx5lFQIUAyD8jAv5ogFU+AQAA//8kQIAlAAAABklEQVQDAFS1UQcMXDbWAAAAAElFTkSuQmCC"



def _extract_icon(b64_data: str, filename: str) -> str:
    icons_dir = os.path.join(tempfile.gettempdir(), "codegrimoire_icons")
    os.makedirs(icons_dir, exist_ok=True)
    path = os.path.join(icons_dir, filename)
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(base64.b64decode(b64_data))
    return path.replace("\\", "/")


ICON_CHECK = _extract_icon(_CHECK_PNG_B64, "check.png")
ICON_DASH  = _extract_icon(_DASH_PNG_B64,  "dash.png")


# ─────────────────────────────────────────────────────────────────
#  WIDGETS
# ─────────────────────────────────────────────────────────────────

class StatCard(QFrame):
    def __init__(self, value: str, label: str, parent=None):
        super().__init__(parent)
        self.setObjectName("stat_card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignCenter)

        self.lbl_value = QLabel(value)
        self.lbl_value.setObjectName("lbl_stat_value")
        self.lbl_value.setAlignment(Qt.AlignCenter)

        self.lbl_label = QLabel(label.upper())
        self.lbl_label.setObjectName("lbl_stat_label")
        self.lbl_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.lbl_value)
        layout.addWidget(self.lbl_label)

    def set_value(self, val: str):
        self.lbl_value.setText(val)


class StatusWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusbar_widget")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 14, 0)
        layout.setSpacing(6)

        self.dot = QLabel("●")
        self.dot.setObjectName("lbl_status_dot")
        self.dot.setFixedWidth(10)

        self.text = QLabel("Pronto")
        self.text.setObjectName("lbl_status_text")

        layout.addWidget(self.dot)
        layout.addWidget(self.text)

    def set_ready(self):
        self.text.setText("Pronto")
        self.dot.setStyleSheet("background:transparent; font-size:8px; color:#22c55e;")

    def set_busy(self, msg="Processando..."):
        self.text.setText(msg)
        self.dot.setStyleSheet("background:transparent; font-size:8px; color:#facc15;")

    def set_error(self, msg="Erro"):
        self.text.setText(msg)
        self.dot.setStyleSheet("background:transparent; font-size:8px; color:#ef4444;")

    def set_custom(self, msg: str, color: str):
        self.text.setText(msg)
        self.dot.setStyleSheet(f"background:transparent; font-size:8px; color:{color};")


class LogsPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("logs_panel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(4)

        header_row = QHBoxLayout()
        lbl = QLabel("LOGS")
        lbl.setObjectName("lbl_logs_title")

        self.btn_clear = QPushButton("Limpar")
        self.btn_clear.setObjectName("btn_clear_logs")

        header_row.addWidget(lbl)
        header_row.addStretch()
        header_row.addWidget(self.btn_clear)
        layout.addLayout(header_row)

        self.output = QTextBrowser()
        self.output.setObjectName("logs_view")
        self.output.setOpenExternalLinks(False)
        layout.addWidget(self.output)

        self.btn_clear.clicked.connect(self.output.clear)

    def log(self, message: str, level: str = "info"):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        colors = {
            "info":    "#5050a0",
            "success": "#22c55e",
            "warning": "#facc15",
            "error":   "#ef4444",
        }
        color = colors.get(level, "#5050a0")
        html = (
            f'<span style="color:#2a2a44;">[{ts}]</span> '
            f'<span style="color:{color};">{message}</span>'
        )
        self.output.append(html)
        sb = self.output.verticalScrollBar()
        sb.setValue(sb.maximum())


class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        c = SYNTAX_COLORS
        self._rules = []

        def fmt(color, bold=False, italic=False):
            f = QTextCharFormat()
            f.setForeground(QColor(color))
            if bold:
                f.setFontWeight(QFont.Bold)
            if italic:
                f.setFontItalic(True)
            return f

        self._rules += [
            (re.compile(r'^# .+'),   fmt(c["heading1"], bold=True)),
            (re.compile(r'^## .+'),  fmt(c["heading2"], bold=True)),
            (re.compile(r'^### .+'), fmt(c["heading3"], bold=True)),
            (re.compile(r'`[^`]+`'), fmt(c["filename"])),
            (re.compile(r'^```.*'),  fmt(c["code"])),
            (re.compile(r'^---+$'),  fmt("#1e1e30")),
            (re.compile(r'\b\d+\b'), fmt(c["number"])),
            (re.compile(r'#.*$'),    fmt(c["comment"], italic=True)),
            (re.compile(r'//.*$'),   fmt(c["comment"], italic=True)),
            (re.compile(r'"[^"]*"'), fmt(c["string"])),
            (re.compile(r"'[^']*'"), fmt(c["string"])),
            (re.compile(
                r'\b(import|from|def|class|return|if|else|elif|for|while|'
                r'in|not|and|or|True|False|None|const|let|var|function|'
                r'export|default|async|await)\b'
            ), fmt(c["keyword"])),
        ]

    def highlightBlock(self, text: str):
        for pattern, f in self._rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), f)
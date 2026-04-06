"""
theme.py - Tema visual do CodeGrimoire
"""

import os, base64, tempfile

# ── Extrai PNGs para disco (Qt não aceita data URI em image:url) ──
_CHECK_B64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAUUlEQVR4nO2PMRIAIAjDwP//ua4FgQMnB7vhkVhEfsYBAJ7XDcyStoAhVdWRIIMPgb/Px8NGEN3HcwQbAS9ksrCVf4ig7HfTIFuu4DKd+m9kAyzwM/xwWQppAAAAAElFTkSuQmCC"
_DASH_B64  = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAJ0lEQVR4nGNgGAWjgIGBEZnz////E0RrZGS0YGBgYGCitotGwUAAAOXrBATEyiHdAAAAAElFTkSuQmCC"
_ARROW_DOWN_B64 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAh0lEQVR4nNySwQnAIAxFU/HiwR0cpY7SyTqK3aTdwYMXkSYFi7RNKHjzQ1CS/CfBaOiUhk6NBEgpOTqNMYdkePaptlhKCTHGmTNTDXv2nLOruRtARKWUx1i/IJTDWkCAt9ZuL4AE4cykCZg5aRyM5XqFMbOAFoJXx5lFQIUAyD8jAv5ogFU+AQAA//8kQIAlAAAABklEQVQDAFS1UQcMXDbWAAAAAElFTkSuQmCC"

def _icon_path(b64: str, name: str) -> str:
    d = os.path.join(tempfile.gettempdir(), "codegrimoire_icons")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    if not os.path.exists(p):
        with open(p, "wb") as f:
            f.write(base64.b64decode(b64))
    return p.replace("\\", "/")

_CHECK_PATH = _icon_path(_CHECK_B64, "check.png")
_DASH_PATH  = _icon_path(_DASH_B64,  "dash.png")
_ARROW_DOWN_PATH = _icon_path(_ARROW_DOWN_B64, "arrow_down.png")

# ── QSS principal ──────────────────────────────────────────────
MAIN_QSS = f"""
/* =============================================
   RESET E BASE
   ============================================= */
* {{
    font-family: 'Segoe UI', system-ui, Arial, sans-serif;
    font-size: 13px;
}}

QWidget {{
    background-color: #13131f;
    color: #c8cdd8;
    border: none;
    margin: 0;
    padding: 0;
}}

QLabel {{
    background: transparent;
}}

QMainWindow {{
    background-color: #13131f;
}}

/* =============================================
   SCROLLBARS
   ============================================= */
QScrollBar:vertical {{
    background: transparent;
    width: 5px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: #2e2e48;
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: #5a5a8a; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
QScrollBar:horizontal {{ height: 5px; background: transparent; }}
QScrollBar::handle:horizontal {{ background: #2e2e48; border-radius: 3px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* =============================================
   TOPBAR
   ============================================= */
QWidget#topbar {{
    background-color: #0d0d18;
    border-bottom: 1px solid #1e1e30;
    min-height: 52px;
    max-height: 52px;
}}

QLabel#lbl_logo_code {{
    font-size: 17px;
    font-weight: 700;
    color: #e8ecf5;
}}

QLabel#lbl_logo_grimoire {{
    font-size: 17px;
    font-weight: 700;
    color: #8b6dfa;
}}

QPushButton#btn_generate {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6d28d9, stop:1 #4338ca);
    color: #ffffff;
    border: none;
    border-radius: 7px;
    padding: 0px 22px;
    font-weight: 600;
    font-size: 13px;
    min-height: 34px;
    min-width: 150px;
}}
QPushButton#btn_generate:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #4f46e5);
}}
QPushButton#btn_generate:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5b21b6, stop:1 #3730a3);
}}
QPushButton#btn_generate:disabled {{
    background: #1e1e30;
    color: #3d3d5c;
}}

QPushButton#btn_topbar {{
    background: #17172a;
    color: #6060a0;
    border: 1px solid #1e1e30;
    border-radius: 7px;
    padding: 0px 14px;
    font-size: 13px;
    min-height: 34px;
}}
QPushButton#btn_topbar:hover {{
    background: #1e1e3a;
    color: #c8cdd8;
    border-color: #2e2e50;
}}

/* =============================================
   PAINEL ESQUERDO
   ============================================= */
QWidget#left_panel {{
    background-color: #0f0f1c;
    border-right: 1px solid #1e1e30;
    min-width: 220px;
    max-width: 320px;
}}

QLabel#lbl_section {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.8px;
    color: #3d3d62;
}}

QFrame#project_frame {{
    background: #17172a;
    border: 1px solid #1e1e30;
    border-radius: 7px;
}}

QLabel#lbl_project_name {{
    font-size: 13px;
    font-weight: 600;
    color: #dde1ed;
}}

QLabel#lbl_project_path {{
    font-size: 11px;
    color: #3d3d62;
}}

QPushButton#btn_open_folder {{
    background: #1e1e30;
    border: 1px solid #252540;
    border-radius: 5px;
    color: #6060a0;
    font-size: 11px;
    padding: 3px 10px;
    min-height: 24px;
}}
QPushButton#btn_open_folder:hover {{
    background: #252550;
    color: #c8cdd8;
}}

QLineEdit#search_input {{
    background: #17172a;
    border: 1px solid #1e1e30;
    border-radius: 6px;
    padding: 5px 10px;
    color: #c8cdd8;
    font-size: 12px;
    selection-background-color: #4338ca;
}}
QLineEdit#search_input:focus {{
    border-color: #6d28d9;
}}
QLineEdit#search_input::placeholder {{
    color: #2e2e4e;
}}

QTreeWidget#file_tree {{
    background: transparent;
    border: none;
    outline: none;
    show-decoration-selected: 0;
    font-size: 12px;
}}
QTreeWidget#file_tree::item {{
    padding: 3px 2px;
    color: #7070a0;
    border-radius: 4px;
    min-height: 22px;
}}
QTreeWidget#file_tree::item:hover {{
    background: #17172a;
    color: #c8cdd8;
}}
QTreeWidget#file_tree::item:selected {{
    background: #1e1e3a;
    color: #dde1ed;
}}

QTreeWidget#file_tree::indicator {{
    width: 10px;
    height: 10px;
    border-radius: 2px;
    border: 2px solid #2e2e4e;
    background: #13131f;
}}
QTreeWidget#file_tree::indicator:unchecked {{
    background: #13131f;
    border-color: #2e2e4e;
}}
QTreeWidget#file_tree::indicator:checked {{
    background: #6d28d9;
    border-color: #6d28d9;
    image: url("{_CHECK_PATH}");
}}
QTreeWidget#file_tree::indicator:indeterminate {{
    background: #3d1f7a;
    border-color: #6d28d9;
    image: url("{_DASH_PATH}");
}}

QPushButton#btn_tree {{
    background: transparent;
    border: none;
    color: #3d3d62;
    font-size: 12px;
    padding: 1px 6px;
    min-height: 22px;
}}
QPushButton#btn_tree:hover {{ color: #8b6dfa; }}

QLabel#lbl_file_count {{
    font-size: 11px;
    color: #3d3d62;
}}

/* =============================================
   PAINEL CENTRAL
   ============================================= */
QWidget#center_panel {{
    background-color: #13131f;
}}

QStackedWidget#center_stack {{
    background: #13131f;
    border: none;
}}

QWidget#preview_topbar {{
    background: #0f0f1c;
    border-bottom: 1px solid #1e1e30;
    min-height: 38px;
    max-height: 38px;
}}

QLabel#lbl_preview_filename {{
    font-size: 12px;
    font-weight: 600;
    color: #c8cdd8;
}}

QLabel#lbl_preview_status {{
    font-size: 11px;
    color: #22c55e;
}}

QPushButton#btn_action_sm {{
    background: #17172a;
    border: 1px solid #1e1e30;
    border-radius: 5px;
    color: #5050a0;
    font-size: 12px;
    padding: 0px 12px;
    min-height: 26px;
}}
QPushButton#btn_action_sm:hover {{
    background: #1e1e3a;
    color: #c8cdd8;
    border-color: #2e2e50;
}}
QPushButton#btn_action_sm:disabled {{
    color: #2a2a44;
    border-color: #17172a;
}}

QTextBrowser#code_view {{
    background: #13131f;
    border: none;
    font-family: 'Cascadia Code', 'JetBrains Mono', 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    color: #c8cdd8;
    padding: 16px 20px;
    selection-background-color: #2e2e5a;
}}

/* =============================================
   MENUS SUSPENSOS (Substitutos limpos do ComboBox)
   ============================================= */
QPushButton#btn_dropdown {{
    background: #17172a;
    border: 1px solid #1e1e30;
    border-radius: 5px;
    padding: 5px 24px 5px 8px;
    color: #6060a0;
    min-height: 28px;
    font-size: 12px;
    text-align: left;
}}
QPushButton#btn_dropdown:hover {{ border-color: #2e2e50; color: #c8cdd8; }}
QPushButton#btn_dropdown:disabled {{ color: #3d3d62; border-color: #17172a; }}
QPushButton#btn_dropdown::menu-indicator {{
    image: url("{_ARROW_DOWN_PATH}");
    subcontrol-origin: padding;
    subcontrol-position: right center;
    width: 12px; height: 12px; right: 8px;
}}

QPushButton#btn_parts {{
    background: #1e1a38;
    border: 1px solid #6d28d9;
    border-radius: 13px;
    padding: 0px 30px 0px 14px;
    color: #a78bfa;
    min-height: 26px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#btn_parts:hover {{ background: #231d42; border-color: #8b6dfa; color: #c4b5fd; }}
QPushButton#btn_parts::menu-indicator {{
    image: url("{_ARROW_DOWN_PATH}");
    subcontrol-origin: padding;
    subcontrol-position: right center;
    width: 12px; height: 12px; right: 10px;
}}

QMenu {{
    background-color: #17172a;
    border: 1px solid #2e2e4e;
    border-radius: 4px;
    color: #c8cdd8;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 14px;
    border-radius: 4px;
    min-width: 150px;
}}
QMenu::item:selected {{ background-color: #2e1f5e; color: #c4b5fd; }}

/* =============================================
   PAINEL DIREITO
   ============================================= */
QWidget#right_panel {{
    background-color: #0f0f1c;
    border-left: 1px solid #1e1e30;
    min-width: 290px;
}}

QScrollArea#right_scroll {{
    background: transparent;
    border: none;
}}

QWidget#right_content {{
    background: transparent;
}}

QFrame#config_group {{
    background: #17172a;
    border: 1px solid #1e1e30;
    border-radius: 7px;
}}

QLabel#lbl_config_section {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.8px;
    color: #3d3d62;
}}

QRadioButton {{
    color: #6060a0;
    background: transparent;
    spacing: 8px;
    padding: 5px 6px;
    border-radius: 5px;
    min-height: 24px;
}}
QRadioButton:hover {{
    background: #1a1a2e;
    color: #c8cdd8;
}}
QRadioButton::indicator {{
    width: 8px;
    height: 8px;
    border-radius: 3px;
    border: 2px solid #2e2e4e;
}}
QRadioButton::indicator:checked {{
    border-color: #6d28d9;
    background: #6d28d9;
}}
QRadioButton:checked {{ color: #a78bfa; }}

QLabel#lbl_radio_hint {{
    font-size: 11px;
    color: #2a2a44;
    padding-left: 21px;
    margin-top: -2px;
    margin-bottom: 2px;
}}

QCheckBox {{
    color: #6060a0;
    background: transparent;
    spacing: 8px;
    padding: 4px 2px;
    min-height: 22px;
}}
QCheckBox:hover {{ color: #c8cdd8; }}
QCheckBox:checked {{ color: #a78bfa; }}

QCheckBox::indicator {{
    width: 10px;
    height: 10px;
    border-radius: 2px;
    border: 2px solid #2e2e4e;
    background: #13131f;
}}
QCheckBox::indicator:unchecked {{
    background: #13131f;
    border-color: #2e2e4e;
}}
QCheckBox::indicator:checked {{
    background: #6d28d9;
    border-color: #6d28d9;
    image: url("{_CHECK_PATH}");
}}
QCheckBox::indicator:indeterminate {{
    background: #3d1f7a;
    border-color: #6d28d9;
    image: url("{_DASH_PATH}");
}}

QLineEdit#config_input, QLineEdit {{
    background: #13131f;
    border: 1px solid #1e1e30;
    border-radius: 5px;
    padding: 5px 8px;
    color: #6060a0;
    font-size: 12px;
}}
QLineEdit:focus {{
    border-color: #6d28d9;
    color: #c8cdd8;
}}

QSpinBox {{
    background: #13131f;
    border: 1px solid #1e1e30;
    border-radius: 5px;
    padding: 3px 6px;
    color: #6060a0;
    min-height: 24px;
}}
QSpinBox:focus {{ border-color: #6d28d9; color: #c8cdd8; }}
QSpinBox::up-button, QSpinBox::down-button {{
    background: #1e1e30;
    border: none;
    width: 16px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background: #2e2e50;
}}

QPushButton#btn_secondary {{
    background: #17172a;
    border: 1px solid #1e1e30;
    border-radius: 5px;
    padding: 0px 10px;
    color: #5050a0;
    font-size: 12px;
    min-height: 26px;
}}
QPushButton#btn_secondary:hover {{
    background: #1e1e3a;
    color: #c8cdd8;
    border-color: #2e2e50;
}}

QFrame#stat_card {{
    background: #17172a;
    border: 1px solid #1e1e30;
    border-radius: 7px;
    min-height: 58px;
}}

QLabel#lbl_stat_value {{
    font-size: 20px;
    font-weight: 700;
    color: #dde1ed;
}}

QLabel#lbl_stat_label {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #3d3d62;
}}

/* =============================================
   LOGS
   ============================================= */
QFrame#logs_panel {{
    background: #14141e;
    border-top: 1px solid #2e2e4e; /* Linha de separação nítida */
    border-bottom: none;
    border-left: none;
    border-right: none;
    min-height: 110px;
    max-height: 110px;
}}

QLabel#lbl_logs_title {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.8px;
    color: #3d3d62;
}}

QTextBrowser#logs_view {{
    background: transparent;
    border: none;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 11px;
    color: #5050a0;
    padding: 0px 6px;
}}

QPushButton#btn_clear_logs {{
    background: transparent;
    border: none;
    color: #3d3d62;
    font-size: 12px;
    padding: 1px 8px;
}}
QPushButton#btn_clear_logs:hover {{ color: #ef4444; }}

/* =============================================
   STATUS BAR
   ============================================= */
QWidget#statusbar_widget {{
    background: #17172a;
    border-radius: 11px;
    border: 1px solid #1e1e30;
    min-height: 24px;
    max-height: 24px;
}}
QLabel#lbl_status_dot {{
    font-size: 8px;
    color: #22c55e;
}}
QLabel#lbl_status_text {{
    font-size: 12px;
    color: #5050a0;
}}

/* =============================================
   SPLITTER
   ============================================= */
QSplitter::handle {{ background: #1e1e30; }}
QSplitter::handle:horizontal {{ width: 1px; }}
QSplitter::handle:hover {{ background: #6d28d9; }}
"""

SYNTAX_COLORS = {
    "heading1": "#a78bfa",
    "heading2": "#8b6dfa",
    "heading3": "#7c5cfa",
    "filename": "#7eb8f7",
    "code":     "#86efac",
    "keyword":  "#c4b5fd",
    "string":   "#86efac",
    "comment":  "#3d3d62",
    "number":   "#fca47a",
    "normal":   "#c8cdd8",
}

PLACEHOLDER_HTML = (
    '<html><body style="background:#13131f; margin:0; padding:0;">'
    '<p style="color:#1e1e30; font-size:13px; '
    'font-family:Consolas,monospace; text-align:center; '
    'margin-top:120px; line-height:2.2;">'
    'Selecione um arquivo para visualizar<br>'
    '<span style="font-size:11px; color:#17172a;">'
    'ou gere o Markdown para ver o resultado'
    '</span></p></body></html>'
)
"""
theme.py - Tema visual do CodeGrimoire
Dark theme profissional inspirado no mockup de referência.
"""

MAIN_QSS = """
/* =============================================
   RESET E BASE
   ============================================= */
* {
    font-family: 'Segoe UI', system-ui, Arial, sans-serif;
    font-size: 13px;
}

QWidget {
    background-color: #13131f;
    color: #c8cdd8;
    border: none;
    margin: 0;
    padding: 0;
}

QMainWindow {
    background-color: #13131f;
}

/* =============================================
   SCROLLBARS
   ============================================= */
QScrollBar:vertical {
    background: transparent;
    width: 5px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #2e2e48;
    border-radius: 3px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #5a5a8a; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QScrollBar:horizontal { height: 5px; background: transparent; }
QScrollBar::handle:horizontal { background: #2e2e48; border-radius: 3px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* =============================================
   TOPBAR
   ============================================= */
QWidget#topbar {
    background-color: #0d0d18;
    border-bottom: 1px solid #1e1e30;
    min-height: 52px;
    max-height: 52px;
}

QLabel#lbl_logo_code {
    font-size: 17px;
    font-weight: 700;
    color: #e8ecf5;
    background: transparent;
}

QLabel#lbl_logo_grimoire {
    font-size: 17px;
    font-weight: 700;
    color: #8b6dfa;
    background: transparent;
}

QPushButton#btn_generate {
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
}
QPushButton#btn_generate:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #4f46e5);
}
QPushButton#btn_generate:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5b21b6, stop:1 #3730a3);
}
QPushButton#btn_generate:disabled {
    background: #1e1e30;
    color: #3d3d5c;
}

QPushButton#btn_topbar {
    background: #17172a;
    color: #6060a0;
    border: 1px solid #1e1e30;
    border-radius: 7px;
    padding: 0px 14px;
    font-size: 13px;
    min-height: 34px;
}
QPushButton#btn_topbar:hover {
    background: #1e1e3a;
    color: #c8cdd8;
    border-color: #2e2e50;
}

/* =============================================
   PAINEL ESQUERDO
   ============================================= */
QWidget#left_panel {
    background-color: #0f0f1c;
    border-right: 1px solid #1e1e30;
    min-width: 220px;
    max-width: 320px;
}

QLabel#lbl_section {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.8px;
    color: #3d3d62;
    background: transparent;
}

QFrame#project_frame {
    background: #17172a;
    border: 1px solid #1e1e30;
    border-radius: 7px;
}

QLabel#lbl_project_name {
    font-size: 13px;
    font-weight: 600;
    color: #dde1ed;
    background: transparent;
}

QLabel#lbl_project_path {
    font-size: 11px;
    color: #3d3d62;
    background: transparent;
}

QPushButton#btn_open_folder {
    background: #1e1e30;
    border: 1px solid #252540;
    border-radius: 5px;
    color: #6060a0;
    font-size: 11px;
    padding: 3px 10px;
    min-height: 24px;
}
QPushButton#btn_open_folder:hover {
    background: #252550;
    color: #c8cdd8;
}

QLineEdit#search_input {
    background: #17172a;
    border: 1px solid #1e1e30;
    border-radius: 6px;
    padding: 5px 10px;
    color: #c8cdd8;
    font-size: 12px;
    selection-background-color: #4338ca;
}
QLineEdit#search_input:focus {
    border-color: #6d28d9;
}
QLineEdit#search_input::placeholder {
    color: #2e2e4e;
}

QTreeWidget#file_tree {
    background: transparent;
    border: none;
    outline: none;
    show-decoration-selected: 0;
    font-size: 12px;
}
QTreeWidget#file_tree::item {
    padding: 3px 2px;
    color: #7070a0;
    border-radius: 4px;
    min-height: 22px;
}
QTreeWidget#file_tree::item:hover {
    background: #17172a;
    color: #c8cdd8;
}
QTreeWidget#file_tree::item:selected {
    background: #1e1e3a;
    color: #dde1ed;
}

/* =============================================
   SETINHAS DA ÁRVORE (BRANCHES) - SVG BASE64
   ============================================= */
QTreeWidget#file_tree::branch:has-children:!has-siblings:closed,
QTreeWidget#file_tree::branch:closed:has-children:has-siblings {
    border-image: none;
    /* Ícone de seta para a DIREITA (Pasta Fechada) */
    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM3MDcwYTAiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSI5IDE4IDE1IDEyIDkgNiI+PC9wb2x5bGluZT48L3N2Zz4=);
}

QTreeWidget#file_tree::branch:open:has-children:!has-siblings,
QTreeWidget#file_tree::branch:open:has-children:has-siblings  {
    border-image: none;
    /* Ícone de seta para BAIXO (Pasta Aberta) */
    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM3MDcwYTAiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSI2IDkgMTIgMTUgMTggOSI+PC9wb2x5bGluZT48L3N2Zz4=);
}

/* O código continua normalmente abaixo com...
QPushButton#btn_tree {
    background: transparent;
    ...
*/

QPushButton#btn_tree {
    background: transparent;
    border: none;
    color: #3d3d62;
    font-size: 12px;
    padding: 1px 6px;
    min-height: 22px;
}
QPushButton#btn_tree:hover { color: #8b6dfa; }

QLabel#lbl_file_count {
    font-size: 11px;
    color: #3d3d62;
    background: transparent;
}

/* =============================================
   PAINEL CENTRAL
   ============================================= */
QWidget#center_panel {
    background-color: #13131f;
}

QWidget#preview_topbar {
    background: #0f0f1c;
    border-bottom: 1px solid #1e1e30;
    min-height: 38px;
    max-height: 38px;
}

QLabel#lbl_preview_filename {
    font-size: 12px;
    font-weight: 600;
    color: #c8cdd8;
    background: transparent;
}

QLabel#lbl_preview_status {
    font-size: 11px;
    color: #22c55e;
    background: transparent;
}

QPushButton#btn_action_sm {
    background: #17172a;
    border: 1px solid #1e1e30;
    border-radius: 5px;
    color: #5050a0;
    font-size: 12px;
    padding: 0px 12px;
    min-height: 26px;
}
QPushButton#btn_action_sm:hover {
    background: #1e1e3a;
    color: #c8cdd8;
    border-color: #2e2e50;
}

QTextBrowser#code_view {
    background: #13131f;
    border: none;
    font-family: 'Cascadia Code', 'JetBrains Mono', 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    color: #c8cdd8;
    padding: 16px 20px;
    selection-background-color: #2e2e5a;
}

/* =============================================
   PAINEL DIREITO
   ============================================= */
QWidget#right_panel {
    background-color: #0f0f1c;
    border-left: 1px solid #1e1e30;
    min-width: 290px; /* Aumentado para o conteúdo caber com folga */
    /* A trava de max-width foi removida! Agora ele estica se você puxar a divisória. */
}

QScrollArea#right_scroll {
    background: transparent;
    border: none;
}

QWidget#right_content {
    background: transparent;
}

QFrame#config_group {
    background: #17172a;
    border: 1px solid #1e1e30;
    border-radius: 7px;
}

QFrame#h_divider {
    background: #1e1e30;
    min-height: 1px;
    max-height: 1px;
    border: none;
    border-radius: 0;
}

QLabel#lbl_config_section {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.8px;
    color: #3d3d62;
    background: transparent;
}

QRadioButton {
    color: #6060a0;
    background: transparent;
    spacing: 8px;
    padding: 5px 6px;
    border-radius: 5px;
    min-height: 24px;
}
QRadioButton:hover {
    background: #1a1a2e;
    color: #c8cdd8;
}
QRadioButton::indicator {
    width: 13px;
    height: 13px;
    border-radius: 7px;
    border: 2px solid #2e2e4e;
    background: transparent;
}
QRadioButton::indicator:checked {
    border-color: #6d28d9;
    background: #6d28d9;
}
QRadioButton:checked { color: #a78bfa; }

QLabel#lbl_radio_hint {
    font-size: 11px;
    color: #2a2a44;
    background: transparent;
    padding-left: 21px;
    margin-top: -2px;
    margin-bottom: 2px;
}

QCheckBox {
    color: #6060a0;
    background: transparent;
    spacing: 8px;
    padding: 4px 2px;
    min-height: 22px;
}
QCheckBox:hover { color: #c8cdd8; }
QCheckBox::indicator {
    width: 13px;
    height: 13px;
    border-radius: 3px;
    border: 2px solid #2e2e4e;
    background: transparent;
}
QCheckBox::indicator:checked {
    background: #6d28d9;
    border-color: #6d28d9;
}

QLineEdit#config_input {
    background: #13131f;
    border: 1px solid #1e1e30;
    border-radius: 5px;
    padding: 5px 8px;
    color: #6060a0;
    font-size: 12px;
}
QLineEdit#config_input:focus {
    border-color: #6d28d9;
    color: #c8cdd8;
}

QPushButton#toggle_on {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6d28d9, stop:1 #4338ca);
    border: none;
    border-radius: 9px;
    min-width: 34px; max-width: 34px;
    min-height: 18px; max-height: 18px;
    font-size: 1px; color: transparent;
}
QPushButton#toggle_off {
    background: #1e1e30;
    border: 1px solid #2e2e4e;
    border-radius: 9px;
    min-width: 34px; max-width: 34px;
    min-height: 18px; max-height: 18px;
    font-size: 1px; color: transparent;
}

QComboBox {
    background: #17172a;
    border: 1px solid #1e1e30;
    border-radius: 5px;
    padding: 5px 8px;
    color: #6060a0;
    min-height: 28px;
    font-size: 12px;
}
QComboBox:hover { border-color: #2e2e50; color: #c8cdd8; }
QComboBox:focus { border-color: #6d28d9; }
QComboBox::drop-down { border: none; width: 16px; }
QComboBox QAbstractItemView {
    background: #17172a;
    border: 1px solid #2e2e4e;
    selection-background-color: #1e1e3a;
    color: #c8cdd8;
    outline: none;
}

QPushButton#btn_secondary {
    background: #17172a;
    border: 1px solid #1e1e30;
    border-radius: 5px;
    padding: 0px 10px;
    color: #5050a0;
    font-size: 12px;
    min-height: 26px;
}
QPushButton#btn_secondary:hover {
    background: #1e1e3a;
    color: #c8cdd8;
    border-color: #2e2e50;
}

QFrame#stat_card {
    background: #17172a;
    border: 1px solid #1e1e30;
    border-radius: 7px;
    min-height: 58px;
}

QLabel#lbl_stat_value {
    font-size: 20px;
    font-weight: 700;
    color: #dde1ed;
    background: transparent;
}

QLabel#lbl_stat_label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #3d3d62;
    background: transparent;
}

/* =============================================
   LOGS
   ============================================= */
QWidget#logs_panel {
    background: #0a0a14;
    border-top: 1px solid #1e1e30;
    min-height: 100px;
    max-height: 100px;
}

QLabel#lbl_logs_title {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.8px;
    color: #3d3d62;
    background: transparent;
}

QTextBrowser#logs_view {
    background: transparent;
    border: none;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 11px;
    color: #5050a0;
    padding: 0px 6px;
}

QPushButton#btn_clear_logs {
    background: transparent;
    border: none;
    color: #3d3d62;
    font-size: 12px;
    padding: 1px 8px;
}
QPushButton#btn_clear_logs:hover { color: #ef4444; }

/* =============================================
   STATUS BAR
   ============================================= */
QWidget#statusbar_widget {
    background: #17172a;
    border-radius: 11px;
    border: 1px solid #1e1e30;
    min-height: 24px;
    max-height: 24px;
}
QLabel#lbl_status_dot {
    background: transparent;
    font-size: 8px;
    color: #22c55e;
}
QLabel#lbl_status_text {
    background: transparent;
    font-size: 12px;
    color: #5050a0;
}

/* =============================================
   SPLITTER
   ============================================= */
QSplitter::handle { background: #1e1e30; }
QSplitter::handle:horizontal { width: 1px; }
QSplitter::handle:hover { background: #6d28d9; }
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
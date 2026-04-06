"""
main.py - CodeGrimoire
Janela principal: monta a interface e conecta toda a lógica.
"""

import sys
import os
import json
import re

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QPushButton, QLabel, QLineEdit, QFileDialog,
    QTreeWidget, QTreeWidgetItem, QMessageBox, QInputDialog,
    QTextBrowser, QFrame, QRadioButton, QButtonGroup,
    QCheckBox, QScrollArea, QSizePolicy, QSpinBox,
    QGridLayout, QMenu, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QColor

from theme import MAIN_QSS, PLACEHOLDER_HTML
from widgets import StatCard, StatusWidget, LogsPanel, MarkdownHighlighter


# ─────────────────────────────────────────────
#  WORKER THREAD — Geração em background
# ─────────────────────────────────────────────
class GeneratorWorker(QThread):
    finished = Signal(list, dict)   # (partes_md, stats_dict)
    error    = Signal(str)

    def __init__(self, files, config, parent=None):
        super().__init__(parent)
        self.files  = files
        self.config = config

    def run(self):
        try:
            result_parts, stats = self._generate()
            self.finished.emit(result_parts, stats)
        except Exception as e:
            self.error.emit(str(e))

    def _generate(self):
        cfg           = self.config
        files         = self.files
        only_tree     = cfg["only_tree"]
        include_tree  = cfg["include_tree"]
        tree_scope    = cfg["tree_scope"]
        include_toc   = cfg["include_toc"]
        rm_comments   = cfg["rm_comments"]
        is_split      = cfg["is_split"]
        limit_lines   = cfg["limit_lines"]
        nome_projeto  = cfg["nome_projeto"]
        tree_text     = cfg["tree_text"]
        header_content = f"# {nome_projeto}\n\n"

        if include_tree:
            header_content += "## Estrutura do Projeto\n\n```\n"
            header_content += f"{nome_projeto}/\n"
            header_content += tree_text
            header_content += "```\n\n"

        if include_toc and not only_tree:
            header_content += "## Sumário de Arquivos\n\n"
            base = cfg["base_folder"]
            for fp in files:
                rel = os.path.relpath(fp, base).replace(os.sep, '/')
                header_content += f"- {rel}\n"
            header_content += "\n"

        if not only_tree:
            header_content += "## Conteúdo dos Arquivos\n\n"

        md_parts      = []
        current_md    = header_content
        current_lines = current_md.count('\n')
        total_size    = 0
        total_lines   = current_lines
        exts_found    = {}
        base          = cfg["base_folder"]

        if not only_tree:
            for fp in files:
                rel  = os.path.relpath(fp, base).replace(os.sep, '/')
                _, ext = os.path.splitext(fp)
                lang = ext.lstrip('.')
                if lang:
                    exts_found[lang] = exts_found.get(lang, 0) + 1

                try:
                    with open(fp, 'r', encoding='utf-8') as f:
                        code = f.read()
                    if rm_comments:
                        code = self._strip_comments(code, lang)
                    snippet = f"### `{rel}`\n\n```{lang}\n{code}\n```\n\n---\n\n"
                except (UnicodeDecodeError, PermissionError):
                    snippet = f"### `{rel}`\n\n*[Arquivo binário ou sem permissão — ignorado]*\n\n---\n\n"
                except Exception as e:
                    snippet = f"### `{rel}`\n\n*[Erro: {e}]*\n\n---\n\n"

                snip_lines = snippet.count('\n')

                if is_split and (current_lines + snip_lines) > limit_lines \
                        and current_lines > header_content.count('\n'):
                    md_parts.append(current_md)
                    current_md    = f"# {nome_projeto} (Parte {len(md_parts) + 1})\n\n"
                    current_lines = current_md.count('\n')

                current_md    += snippet
                current_lines += snip_lines
                total_lines   += snip_lines
                total_size    += len(snippet.encode('utf-8'))

        if current_md:
            md_parts.append(current_md)

        if only_tree:
            total_size  = len(header_content.encode('utf-8'))
            total_lines = header_content.count('\n')

        stats = {
            "n_files": len(files),
            "n_langs": len(exts_found),
            "size":    total_size,
            "lines":   total_lines,
        }
        return md_parts, stats

    _PY_COMMENT  = re.compile(r'(?<!["\'])#(?!["\']).*$', re.MULTILINE)
    _PY_DOCSTR3  = re.compile(r'""".*?"""', re.DOTALL)
    _PY_DOCSTR1  = re.compile(r"'''.*?'''", re.DOTALL)
    _SL_COMMENT  = re.compile(r'(?<!"http:)(?<!"https:)//(?!/).*$', re.MULTILINE)

    def _strip_comments(self, code: str, lang: str) -> str:
        if lang in ('py',):
            placeholders, i = {}, 0
            for pat in (self._PY_DOCSTR3, self._PY_DOCSTR1):
                for m in pat.finditer(code):
                    key = f"__DS{i}__"
                    placeholders[key] = m.group()
                    code = code.replace(m.group(), key, 1)
                    i += 1
            code = self._PY_COMMENT.sub('', code)
            for key, val in placeholders.items():
                code = code.replace(key, val)
            return code

        if lang in ('js', 'ts', 'tsx', 'jsx', 'java', 'c', 'cpp', 'cs', 'go', 'rust', 'rs'):
            return self._SL_COMMENT.sub('', code)

        return code


# ─────────────────────────────────────────────
#  TOPBAR
# ─────────────────────────────────────────────
class TopBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topbar")
        row = QHBoxLayout(self)
        row.setContentsMargins(16, 0, 16, 0)
        row.setSpacing(8)

        lbl_code = QLabel("Code")
        lbl_code.setObjectName("lbl_logo_code")
        lbl_grim = QLabel("Grimoire")
        lbl_grim.setObjectName("lbl_logo_grimoire")
        row.addWidget(lbl_code)
        row.addWidget(lbl_grim)
        row.addStretch()

        self.btn_open = QPushButton("Abrir Projeto")
        self.btn_open.setObjectName("btn_topbar")
        row.addWidget(self.btn_open)

        self.btn_generate = QPushButton("Gerar Markdown")
        self.btn_generate.setObjectName("btn_generate")
        self.btn_generate.setEnabled(False)
        row.addWidget(self.btn_generate)


# ─────────────────────────────────────────────
#  PAINEL ESQUERDO — Explorador
# ─────────────────────────────────────────────
class LeftPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("left_panel")
        col = QVBoxLayout(self)
        col.setContentsMargins(10, 12, 10, 10)
        col.setSpacing(8)

        lbl = QLabel("PROJETO")
        lbl.setObjectName("lbl_section")
        col.addWidget(lbl)

        self.project_frame = QFrame()
        self.project_frame.setObjectName("project_frame")
        pf_layout = QHBoxLayout(self.project_frame)
        pf_layout.setContentsMargins(10, 8, 10, 8)
        pf_layout.setSpacing(8)

        info = QVBoxLayout()
        info.setSpacing(2)
        self.lbl_name = QLabel("Nenhum projeto")
        self.lbl_name.setObjectName("lbl_project_name")
        self.lbl_path = QLabel("—")
        self.lbl_path.setObjectName("lbl_project_path")
        info.addWidget(self.lbl_name)
        info.addWidget(self.lbl_path)

        self.btn_refresh = QPushButton("↻")
        self.btn_refresh.setObjectName("btn_open_folder") # Reaproveita o estilo escuro do botão Abrir
        self.btn_refresh.setToolTip("Atualizar arquivos e estrutura")
        self.btn_refresh.setEnabled(False) # Só ativa quando houver projeto

        self.btn_open = QPushButton("Abrir")
        self.btn_open.setObjectName("btn_open_folder")

        pf_layout.addLayout(info, 1)
        pf_layout.addWidget(self.btn_refresh)
        pf_layout.addWidget(self.btn_open)
        col.addWidget(self.project_frame)

        self.search = QLineEdit()
        self.search.setObjectName("search_input")
        self.search.setPlaceholderText("Buscar arquivos...")

        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._exec_filter)
        self.search.textChanged.connect(lambda t: self.search_timer.start(300))
        col.addWidget(self.search)

        self.tree = QTreeWidget()
        self.tree.setObjectName("file_tree")
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(20)
        self.tree.setAnimated(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        col.addWidget(self.tree, 1)

        footer = QHBoxLayout()
        self.btn_all = QPushButton("Marcar tudo")
        self.btn_all.setObjectName("btn_tree")
        self.btn_none = QPushButton("Desmarcar")
        self.btn_none.setObjectName("btn_tree")
        footer.addWidget(self.btn_all)
        footer.addWidget(self.btn_none)
        footer.addStretch()
        col.addLayout(footer)

        self.lbl_count = QLabel("0 arquivos selecionados")
        self.lbl_count.setObjectName("lbl_file_count")
        col.addWidget(self.lbl_count)

    def set_project(self, folder: str):
        name = os.path.basename(folder) or folder
        self.lbl_name.setText(name)
        short = folder if len(folder) <= 42 else "..." + folder[-39:]
        self.lbl_path.setText(short)

    def _exec_filter(self):
        text = self.search.text().lower().strip()

        def apply(item) -> bool:
            match      = text in item.text(0).lower()
            child_vis  = any(apply(item.child(i)) for i in range(item.childCount()))
            visible    = match or child_vis
            item.setHidden(not visible if text else False)
            if text and visible:
                item.setExpanded(True)
            return visible

        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            apply(root.child(i))


# ─────────────────────────────────────────────
#  PAINEL CENTRAL — Preview
# ─────────────────────────────────────────────
class CenterPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("center_panel")
        col = QVBoxLayout(self)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)

        # ── Barra superior ──────────────────────────────────────────────────
        bar = QWidget()
        bar.setObjectName("preview_topbar")
        bar_row = QHBoxLayout(bar)
        bar_row.setContentsMargins(14, 0, 12, 0)
        bar_row.setSpacing(8)

        self.lbl_filename = QLabel("PREVIEW.md")
        self.lbl_filename.setObjectName("lbl_preview_filename")
        self.lbl_status = QLabel("")
        self.lbl_status.setObjectName("lbl_preview_status")

        # Menu Suspenso de partes (Substitui QComboBox)
        self.btn_parts = QPushButton("Partes")
        self.btn_parts.setObjectName("btn_parts")
        self.btn_parts.setVisible(False)
        self.menu_parts = QMenu(self)
        self.btn_parts.setMenu(self.menu_parts)

        self.btn_show_md = QPushButton("← Ver Markdown")
        self.btn_show_md.setObjectName("btn_action_sm")
        self.btn_show_md.setVisible(False)

        self.btn_copy = QPushButton("Copiar")
        self.btn_copy.setObjectName("btn_action_sm")
        self.btn_export = QPushButton("Exportar")
        self.btn_export.setObjectName("btn_action_sm")

        bar_row.addWidget(self.lbl_filename)
        bar_row.addWidget(self.lbl_status)
        bar_row.addStretch()
        bar_row.addWidget(self.btn_parts)
        bar_row.addWidget(self.btn_show_md)
        bar_row.addWidget(self.btn_copy)
        bar_row.addWidget(self.btn_export)
        col.addWidget(bar)

        # ── Stacked: modo arquivo vs modo markdown ──────────────────────────
        self.stack = QStackedWidget()
        self.stack.setObjectName("center_stack")

        self.file_view = QTextBrowser()
        self.file_view.setObjectName("code_view")
        self.file_view.setOpenExternalLinks(False)

        self.md_view = QTextBrowser()
        self.md_view.setObjectName("code_view")
        self.md_view.setOpenExternalLinks(False)
        self.md_view.setHtml(PLACEHOLDER_HTML)

        self.stack.addWidget(self.file_view)
        self.stack.addWidget(self.md_view)
        self.stack.setCurrentIndex(1)
        col.addWidget(self.stack, 1)

        self._hl_file = MarkdownHighlighter(self.file_view.document())
        self._hl_md   = MarkdownHighlighter(self.md_view.document())

    def show_file(self, path: str):
        name = os.path.basename(path)
        self.lbl_filename.setText(name)
        self.lbl_status.setText("")
        self.stack.setCurrentIndex(0)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.file_view.setPlainText(f.read())
        except Exception as e:
            self.file_view.setPlainText(f"Não foi possível ler o arquivo.\n\n{e}")

    def show_markdown(self, content: str, title="PREVIEW.md"):
        self.lbl_filename.setText(title)
        self.lbl_status.setText("● Atualizado agora")
        self.stack.setCurrentIndex(1)

        self.md_view.clear()
        cursor = self.md_view.textCursor()
        fmt    = cursor.charFormat()
        fmt.setForeground(QColor("#c8cdd8"))
        self.md_view.setCurrentCharFormat(fmt)
        self.md_view.setPlainText(content)

    def reset_to_placeholder(self):
        self.md_view.setHtml(PLACEHOLDER_HTML)
        self.stack.setCurrentIndex(1)
        self.lbl_filename.setText("PREVIEW.md")
        self.lbl_status.setText("")


# ─────────────────────────────────────────────
#  PAINEL DIREITO — Configurações
# ─────────────────────────────────────────────
class RightPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("right_panel")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("right_scroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("right_content")
        col = QVBoxLayout(content)
        col.setContentsMargins(12, 14, 12, 14)
        col.setSpacing(14)

        lbl_title = QLabel("CONFIGURAÇÕES")
        lbl_title.setObjectName("lbl_section")
        col.addWidget(lbl_title)

        self._build_format_group(col)
        self._build_structure_group(col)
        self._build_include_group(col)
        self._build_split_group(col)
        self._build_filters_group(col)
        self._build_optimizations_group(col)
        self._build_presets_group(col)

        col.addStretch()
        self._build_stats(col)
        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _make_group(self, title: str):
        group  = QFrame()
        group.setObjectName("config_group")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)
        lbl = QLabel(title)
        lbl.setObjectName("lbl_config_section")
        layout.addWidget(lbl)
        return group, layout

    def _build_structure_group(self, parent):
        group, lay = self._make_group("Configurações da Árvore")
        lay.addWidget(QLabel("Escopo da Estrutura:"))
        
        # Botão + QMenu substituindo QComboBox
        self.btn_tree_scope = QPushButton("Apenas Selecionados")
        self.btn_tree_scope.setObjectName("btn_dropdown")
        self.menu_tree_scope = QMenu(self)
        self.btn_tree_scope.setMenu(self.menu_tree_scope)
        
        for scope in ["Apenas Selecionados", "Projeto Completo", "Apenas Pastas"]:
            act = self.menu_tree_scope.addAction(scope)
            act.triggered.connect(lambda checked=False, text=scope: self.btn_tree_scope.setText(text))
            
        lay.addWidget(self.btn_tree_scope)

        self.chk_only_tree = QCheckBox("Gerar apenas estrutura (Sem código)")
        self.chk_only_tree.setObjectName("chk_config")
        lay.addWidget(self.chk_only_tree)
        parent.addWidget(group)

    def _build_format_group(self, parent):
        group, lay = self._make_group("Formato de Saída")
        self.radio_simple   = QRadioButton("Markdown Simples")
        self.radio_detailed = QRadioButton("Markdown Detalhado")
        self.radio_toc      = QRadioButton("Com Tabela de Conteúdo")
        self.radio_simple.setChecked(True)
        self._fmt_group = QButtonGroup()
        for r in (self.radio_simple, self.radio_detailed, self.radio_toc):
            self._fmt_group.addButton(r)
        for radio, hint in zip(
            (self.radio_simple, self.radio_detailed, self.radio_toc),
            ["Estrutura limpa e direta", "Inclui comentários e informações", "Gera sumário automático"],
        ):
            lay.addWidget(radio)
            lbl = QLabel(hint)
            lbl.setObjectName("lbl_radio_hint")
            lay.addWidget(lbl)
        parent.addWidget(group)

    def _build_include_group(self, parent):
        group, lay = self._make_group("Incluir")
        self.chk_folders = QCheckBox("Estrutura de Pastas")
        self.chk_folders.setChecked(True)
        self.chk_langs   = QCheckBox("Linguagens Detectadas")
        self.chk_langs.setChecked(True)
        self.chk_stats   = QCheckBox("Estatísticas do Projeto")
        for w in (self.chk_folders, self.chk_langs, self.chk_stats):
            lay.addWidget(w)
        parent.addWidget(group)

    def _build_split_group(self, parent):
        group, lay = self._make_group("Limites da IA (Divisão)")
        self.chk_split = QCheckBox("Dividir Markdown em partes")
        spin_row = QHBoxLayout()
        self.spin_lines = QSpinBox()
        self.spin_lines.setRange(500, 50000)
        self.spin_lines.setValue(3000)
        spin_row.addWidget(QLabel("Tamanho aprox:"))
        spin_row.addWidget(self.spin_lines)
        lay.addWidget(self.chk_split)
        lay.addLayout(spin_row)
        parent.addWidget(group)

    def _build_filters_group(self, parent):
        group, lay = self._make_group("Filtros")
        self.field_ignore = QLineEdit("node_modules, .git, dist")
        lay.addWidget(QLabel("Ignorar arquivos:"))
        lay.addWidget(self.field_ignore)
        parent.addWidget(group)

    def _build_optimizations_group(self, parent):
        group, lay = self._make_group("Otimizações")
        self.chk_rm_comments = QCheckBox("Remover comentários")
        self.chk_minify      = QCheckBox("Minificar espaços")
        lay.addWidget(self.chk_rm_comments)
        lay.addWidget(self.chk_minify)
        parent.addWidget(group)

    def _build_presets_group(self, parent):
        group, lay = self._make_group("Presets de Seleção")
        
        # Botão + QMenu substituindo QComboBox
        self.btn_presets = QPushButton("Nenhum preset")
        self.btn_presets.setObjectName("btn_dropdown")
        self.menu_presets = QMenu(self)
        self.btn_presets.setMenu(self.menu_presets)
        self.btn_presets.setEnabled(False)
        lay.addWidget(self.btn_presets)
        
        btns = QHBoxLayout()
        self.btn_load   = QPushButton("Carregar")
        self.btn_save   = QPushButton("Salvar")
        self.btn_delete = QPushButton("Excluir")
        for b in (self.btn_load, self.btn_save, self.btn_delete):
            b.setObjectName("btn_secondary")
            btns.addWidget(b)
        lay.addLayout(btns)
        parent.addWidget(group)

    def _build_stats(self, parent):
        lbl = QLabel("ESTATÍSTICAS")
        lbl.setObjectName("lbl_section")
        parent.addWidget(lbl)
        grid = QGridLayout()
        self.card_files = StatCard("0",   "Arquivos")
        self.card_langs = StatCard("0",   "Linguagens")
        self.card_size  = StatCard("0 B", "Tamanho")
        self.card_lines = StatCard("0",   "Linhas")
        grid.addWidget(self.card_files, 0, 0)
        grid.addWidget(self.card_langs, 0, 1)
        grid.addWidget(self.card_size,  1, 0)
        grid.addWidget(self.card_lines, 1, 1)
        parent.addLayout(grid)

    def update_stats(self, n_files: int, n_langs: int, size_bytes: int, total_lines: int):
        self.card_files.set_value(str(n_files))
        self.card_langs.set_value(str(n_langs))
        self.card_lines.set_value(f"{total_lines:,}".replace(",", "."))
        if size_bytes < 1024:
            s = f"{size_bytes} B"
        elif size_bytes < 1024 ** 2:
            s = f"{size_bytes/1024:.1f} KB"
        else:
            s = f"{size_bytes/1024**2:.1f} MB"
        self.card_size.set_value(s)


# ─────────────────────────────────────────────
#  JANELA PRINCIPAL
# ─────────────────────────────────────────────
class CodeGrimoireApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CodeGrimoire — Transforme código em conhecimento")
        self.resize(1280, 820)
        self.setMinimumSize(900, 600)

        self.current_folder  = ""
        self.presets_file    = os.path.join(os.path.expanduser("~"), ".codegrimoire_presets.json")
        self._md_parts       = []
        self._current_part_idx = 0
        self.root_item       = None
        self._worker         = None

        self.setStyleSheet(MAIN_QSS)
        self._build_ui()
        self._connect()

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("central_widget")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.topbar = TopBar()
        root.addWidget(self.topbar)

        self.splitter = QSplitter(Qt.Horizontal)
        self.left     = LeftPanel()
        self.center   = CenterPanel()
        self.right    = RightPanel()
        self.splitter.addWidget(self.left)
        self.splitter.addWidget(self.center)
        self.splitter.addWidget(self.right)
        self.splitter.setSizes([280, 740, 260])
        root.addWidget(self.splitter, 1)

        self.logs = LogsPanel()
        root.addWidget(self.logs)

        status_row = QHBoxLayout()
        status_row.setContentsMargins(10, 4, 10, 6)
        self.status = StatusWidget()
        status_row.addWidget(self.status)
        status_row.addStretch()
        root.addLayout(status_row)

        self.count_timer = QTimer()
        self.count_timer.setSingleShot(True)
        self.count_timer.timeout.connect(self._actual_update_count)

    def _connect(self):
        self.topbar.btn_open.clicked.connect(self.select_folder)
        self.left.btn_open.clicked.connect(self.select_folder)
        self.left.btn_refresh.clicked.connect(self.refresh_project)
        self.topbar.btn_generate.clicked.connect(self.generate_markdown)

        self.left.btn_all.clicked.connect(lambda: self._set_all(True))
        self.left.btn_none.clicked.connect(lambda: self._set_all(False))
        self.left.tree.itemClicked.connect(self._on_item_click)
        self.left.tree.itemChanged.connect(lambda item, col: self.count_timer.start(50))

        self.center.btn_show_md.clicked.connect(self._restore_md_view)
        self.center.btn_copy.clicked.connect(self._copy_clipboard)
        self.center.btn_export.clicked.connect(self._export)

        self.right.btn_load.clicked.connect(self._load_preset)
        self.right.btn_save.clicked.connect(self._save_preset)
        self.right.btn_delete.clicked.connect(self._delete_preset)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta do projeto")
        if not folder:
            return
        self.current_folder = folder
        self._md_parts = []
        self._current_part_idx = 0
        self.center.btn_show_md.setVisible(False)
        self.center.btn_parts.setVisible(False)
        self.center.reset_to_placeholder()

        self.left.set_project(folder)
        self._populate_tree(folder)
        self.topbar.btn_generate.setEnabled(True)
        self.right.btn_presets.setEnabled(True)
        self.left.btn_refresh.setEnabled(True)
        self._update_preset_combo()
        self.logs.log(f"Projeto aberto: {os.path.basename(folder)}", "info")
        self.status.set_ready()
    
    def refresh_project(self):
        """Recarrega a árvore de arquivos preservando os itens que estavam marcados."""
        if not self.current_folder:
            return

        self.status.set_busy("Atualizando arquivos...")
        self.logs.log("Atualizando estrutura do projeto...", "info")

        # 1. Fazer "backup" da seleção atual
        saved_files = []
        if self.root_item:
            self._collect_files(self.root_item, saved_files)
        
        favorites = {os.path.normpath(f) for f in saved_files}

        # 2. Recriar a árvore JÁ com os favoritos injetados (super rápido)
        self._populate_tree(self.current_folder, favorites)

        self.logs.log("Projeto atualizado com sucesso.", "success")
        self.status.set_custom("Atualizado", "#22c55e")
        QTimer.singleShot(1500, self.status.set_ready)

    def _on_item_click(self, item, _col):
        if item.childCount() > 0:
            item.setExpanded(not item.isExpanded())

        path = item.data(0, Qt.UserRole)
        if path and os.path.isfile(path):
            self.center.show_file(path)
            if self._md_parts:
                self.center.btn_show_md.setVisible(True)
                self.center.btn_show_md.setEnabled(True)

    def _actual_update_count(self):
        if self.root_item:
            files = []
            self._collect_files(self.root_item, files)
            n = len(files)
            self.left.lbl_count.setText(
                f"{n} arquivo{'s' if n != 1 else ''} selecionado{'s' if n != 1 else ''}"
            )

    def generate_markdown(self):
        if not self.current_folder:
            return

        files_to_process = []
        self._collect_files(self.root_item, files_to_process)

        only_tree = self.right.chk_only_tree.isChecked()

        if not files_to_process and not only_tree:
            QMessageBox.warning(self, "Aviso", "Nenhum arquivo selecionado para inclusão de conteúdo.")
            return

        self.topbar.btn_generate.setEnabled(False)
        self.status.set_busy("Gerando...")
        self.logs.log("Iniciando geração...", "info")

        config = {
            "only_tree":    only_tree,
            "include_tree": self.right.chk_folders.isChecked(),
            "tree_scope":   self.right.btn_tree_scope.text(),
            "include_toc":  self.right.radio_toc.isChecked(),
            "rm_comments":  self.right.chk_rm_comments.isChecked(),
            "is_split":     self.right.chk_split.isChecked(),
            "limit_lines":  self.right.spin_lines.value() if self.right.chk_split.isChecked() else float('inf'),
            "nome_projeto": os.path.basename(self.current_folder) or self.current_folder,
            "tree_text":    self._build_tree_text(self.root_item, scope=self.right.btn_tree_scope.text()),
            "base_folder":  self.current_folder,
        }

        self._worker = GeneratorWorker(files_to_process, config)
        self._worker.finished.connect(self._on_generation_done)
        self._worker.error.connect(self._on_generation_error)
        self._worker.start()

    def _on_generation_done(self, md_parts, stats):
        self._md_parts = md_parts
        self._current_part_idx = 0

        self.right.update_stats(
            stats["n_files"], stats["n_langs"],
            stats["size"],    stats["lines"]
        )

        # Atualiza o menu de Partes
        self.center.menu_parts.clear()
        for i, part in enumerate(md_parts):
            p_lines = part.count('\n')
            label = f"Parte {i+1}  ({p_lines} linhas)"
            act = self.center.menu_parts.addAction(label)
            
            # Closure para garantir que o click passe o index e label corretos
            def make_handler(idx, txt):
                return lambda checked=False: (self.center.btn_parts.setText(txt), self._change_md_part(idx))
            
            act.triggered.connect(make_handler(i, label))
            
            if i == 0:
                self.center.btn_parts.setText(label)

        self.center.btn_parts.setVisible(len(md_parts) > 1)
        self._restore_md_view()

        msg = f"Gerado com sucesso! {len(md_parts)} parte(s), {stats['lines']} linhas."
        self.logs.log(msg, "success")
        self.status.set_ready()
        self.topbar.btn_generate.setEnabled(True)

    def _on_generation_error(self, msg):
        self.logs.log(f"Erro na geração: {msg}", "error")
        self.status.set_error("Erro")
        self.topbar.btn_generate.setEnabled(True)

    def _restore_md_view(self):
        if self._md_parts:
            idx = self._current_part_idx
            self._change_md_part(idx)
            self.center.btn_show_md.setEnabled(False)
            if len(self._md_parts) > 1:
                self.center.btn_parts.setVisible(True)

    def _change_md_part(self, index):
        if 0 <= index < len(self._md_parts):
            self._current_part_idx = index
            md    = self._md_parts[index]
            title = "PREVIEW.md" if len(self._md_parts) == 1 \
                    else f"PREVIEW — Parte {index+1}.md"
            self.center.show_markdown(md, title)

    def _copy_clipboard(self):
        if not self._md_parts:
            return
        idx = self._current_part_idx
        QApplication.clipboard().setText(self._md_parts[idx])
        label = "Conteúdo" if len(self._md_parts) == 1 else f"Parte {idx+1}"
        self.logs.log(f"{label} copiada para a área de transferência.", "success")
        self.status.set_custom("Copiado", "#22c55e")
        self.center.btn_copy.setText("Copiado! ✓")
        QTimer.singleShot(2000, lambda: self.center.btn_copy.setText("Copiar"))
        QTimer.singleShot(1800, self.status.set_ready)

    def _export(self):
        if not self._md_parts:
            QMessageBox.information(self, "Aviso", "Gere o Markdown primeiro.")
            return
        nome = os.path.basename(self.current_folder) or "projeto"

        if len(self._md_parts) == 1:
            path, _ = QFileDialog.getSaveFileName(
                self, "Exportar Markdown", f"{nome}_contexto.md", "Markdown (*.md)"
            )
            if path:
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(self._md_parts[0])
                    self.logs.log(f"Salvo em: {path}", "success")
                except Exception as e:
                    QMessageBox.critical(self, "Erro", str(e))
        else:
            folder = QFileDialog.getExistingDirectory(
                self, "Selecione a pasta para exportar as partes"
            )
            if folder:
                try:
                    for i, part_md in enumerate(self._md_parts):
                        full_path = os.path.join(folder, f"{nome}_parte_{i+1}.md")
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(part_md)
                    self.logs.log(f"Exportadas {len(self._md_parts)} partes em: {folder}", "success")
                    QMessageBox.information(
                        self, "Sucesso", f"{len(self._md_parts)} partes exportadas."
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Erro", str(e))

    def _populate_tree(self, folder: str, favorites: set = None):
        # Apenas congela o visual (não os sinais) para preservar o Tristate
        self.left.tree.setUpdatesEnabled(False)
        self.left.tree.clear()

        # Lê os filtros de ignorar
        raw_ignores = self.right.field_ignore.text().split(',')
        self._IGNORE = {item.strip() for item in raw_ignores if item.strip()}

        nome = os.path.basename(folder) or folder
        self.root_item = QTreeWidgetItem(self.left.tree, [f"📁 {nome}"])
        self.root_item.setData(0, Qt.UserRole, os.path.normpath(folder))
        self.root_item.setFlags(
            self.root_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsAutoTristate
        )
        
        self.root_item.setCheckState(0, Qt.Checked if favorites is None else Qt.Unchecked)

        self._add_items(self.root_item, folder, favorites)
        self.root_item.setExpanded(True)

        self.left.tree.setUpdatesEnabled(True)
        self._actual_update_count()

    def _add_items(self, parent, path: str, favorites: set = None):
        try:
            entries = os.listdir(path)
        except PermissionError:
            return

        dirs  = sorted(e for e in entries
                       if os.path.isdir(os.path.join(path, e)) and e not in self._IGNORE)
        files = sorted(e for e in entries
                       if os.path.isfile(os.path.join(path, e)))

        for d in dirs:
            full = os.path.normpath(os.path.join(path, d))
            item = QTreeWidgetItem(parent, [f"🗁 {d}"])
            item.setData(0, Qt.UserRole, full)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsAutoTristate)
            
            # Se tem favoritos, inicia desmarcado
            item.setCheckState(0, Qt.Checked if favorites is None else Qt.Unchecked)
            self._add_items(item, full, favorites)

        for fname in files:
            full = os.path.normpath(os.path.join(path, fname))
            item = QTreeWidgetItem(parent, [f"🗋 {fname}"])
            item.setData(0, Qt.UserRole, full)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            
            # Checa se este arquivo específico estava no backup (favorites)
            if favorites is not None:
                state = Qt.Checked if full in favorites else Qt.Unchecked
            else:
                state = Qt.Checked
                
            item.setCheckState(0, state)

    def _set_all(self, checked: bool):
        if self.root_item:
            self.left.tree.setUpdatesEnabled(False)
            self.root_item.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)
            self.left.tree.setUpdatesEnabled(True)
            self._actual_update_count()

    def _collect_files(self, item, out: list, visited: set = None):
        if visited is None:
            visited = set()
        if item.childCount():
            for i in range(item.childCount()):
                self._collect_files(item.child(i), out, visited)
        elif item.checkState(0) == Qt.Checked:
            path = item.data(0, Qt.UserRole)
            if path and os.path.isfile(path):
                real = os.path.realpath(path)
                if real not in visited:
                    visited.add(real)
                    out.append(path)

    def _build_tree_text(self, item, prefix="", scope="Apenas Selecionados") -> str:
        result = ""
        valid_children = []
        for i in range(item.childCount()):
            child = item.child(i)
            caminho = child.data(0, Qt.UserRole)
            is_dir  = os.path.isdir(caminho)
            if scope == "Apenas Selecionados":
                if child.checkState(0) != Qt.Unchecked:
                    valid_children.append(child)
            elif scope == "Apenas Pastas":
                if is_dir:
                    valid_children.append(child)
            else:
                valid_children.append(child)

        for i, child in enumerate(valid_children):
            caminho    = child.data(0, Qt.UserRole)
            clean_name = os.path.basename(caminho)
            if os.path.isdir(caminho):
                clean_name += "/"
            is_last = (i == len(valid_children) - 1)
            con     = "└── " if is_last else "├── "
            result += f"{prefix}{con}{clean_name}\n"
            if child.childCount() > 0:
                ext = "    " if is_last else "│   "
                result += self._build_tree_text(child, prefix + ext, scope)
        return result

    def _load_json(self) -> dict:
        if os.path.exists(self.presets_file):
            try:
                with open(self.presets_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_json(self, data: dict):
        with open(self.presets_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _get_presets(self) -> dict:
        if not self.current_folder:
            return {}
        return self._load_json().get(os.path.normpath(self.current_folder), {})

    def _write_presets(self, presets: dict):
        if not self.current_folder:
            return
        data = self._load_json()
        data[os.path.normpath(self.current_folder)] = presets
        self._save_json(data)

    def _update_preset_combo(self):
        self.right.menu_presets.clear()
        p = self._get_presets()
        items = p.keys() if p else ["Nenhum preset"]
        
        for item in items:
            act = self.right.menu_presets.addAction(item)
            act.triggered.connect(lambda checked=False, txt=item: self.right.btn_presets.setText(txt))
            
        if items:
            self.right.btn_presets.setText(list(items)[0])
        else:
            self.right.btn_presets.setText("Nenhum preset")

    def _save_preset(self):
        name, ok = QInputDialog.getText(self, "Salvar Preset", "Nome do preset:")
        if ok and name.strip():
            files    = []
            self._collect_files(self.root_item, files)
            base     = self.current_folder
            rel_list = [os.path.relpath(f, base).replace(os.sep, '/') for f in files]
            p = self._get_presets()
            p[name.strip()] = rel_list
            self._write_presets(p)
            self._update_preset_combo()
            self.logs.log(f"Preset '{name}' salvo.", "success")

    def _load_preset(self):
        name = self.right.btn_presets.text()
        p    = self._get_presets()
        if name in p:
            base      = self.current_folder
            abs_files = {
                os.path.normpath(os.path.join(base, rel))
                for rel in p[name]
            }
            
            self.left.tree.setUpdatesEnabled(False)
            
            self.root_item.setCheckState(0, Qt.Unchecked)
            self._apply_preset(self.root_item, abs_files)
            
            self.left.tree.setUpdatesEnabled(True)
            self._actual_update_count()
            
            self.logs.log(f"Preset '{name}' carregado.", "info")

    def _delete_preset(self):
        name = self.right.btn_presets.text()
        p    = self._get_presets()
        if name in p:
            del p[name]
            self._write_presets(p)
            self._update_preset_combo()
            self.logs.log(f"Preset '{name}' excluído.", "warning")

    def _apply_preset(self, item, favorites: set):
        path = item.data(0, Qt.UserRole)
        if item.childCount() == 0:
            state = Qt.Checked if os.path.normpath(path) in favorites else Qt.Unchecked
            item.setCheckState(0, state)
        for i in range(item.childCount()):
            self._apply_preset(item.child(i), favorites)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = CodeGrimoireApp()
    win.show()
    sys.exit(app.exec())
"""
main.py - CodeGrimoire
Janela principal: monta a interface e conecta toda a lógica.
"""

import sys
import os
import json

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QPushButton, QLabel, QLineEdit, QFileDialog,
    QTreeWidget, QTreeWidgetItem, QMessageBox, QInputDialog,
    QTextBrowser, QFrame, QRadioButton, QButtonGroup,
    QCheckBox, QComboBox, QScrollArea, QSizePolicy, QSpinBox, QGridLayout, QMenu
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

from theme import MAIN_QSS, PLACEHOLDER_HTML
from widgets import StatCard, StatusWidget, LogsPanel, MarkdownHighlighter

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

        self.btn_generate = QPushButton("⚡  Gerar Markdown")
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

        self.btn_open = QPushButton("Abrir")
        self.btn_open.setObjectName("btn_open_folder")

        pf_layout.addLayout(info, 1)
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
        self.tree.setIndentation(16)
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
            match = text in item.text(0).lower()
            child_vis = any(apply(item.child(i)) for i in range(item.childCount()))
            visible = match or child_vis
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

        bar = QWidget()
        bar.setObjectName("preview_topbar")
        bar_row = QHBoxLayout(bar)
        bar_row.setContentsMargins(14, 0, 12, 0)
        bar_row.setSpacing(8)

        self.lbl_filename = QLabel("PREVIEW.md")
        self.lbl_filename.setObjectName("lbl_preview_filename")
        self.lbl_status = QLabel("")
        self.lbl_status.setObjectName("lbl_preview_status")
        
        # NOVO: Combo box para navegar pelas partes do Markdown
        self.combo_parts = QComboBox()
        self.combo_parts.setVisible(False) # Só aparece quando tiver partes

        self.btn_show_md = QPushButton("👁 Ver Markdown Gerado")
        self.btn_show_md.setObjectName("btn_action_sm")
        self.btn_show_md.setVisible(False)
        
        self.btn_copy = QPushButton("Copiar")
        self.btn_copy.setObjectName("btn_action_sm")
        self.btn_export = QPushButton("Exportar")
        self.btn_export.setObjectName("btn_action_sm")

        bar_row.addWidget(self.lbl_filename)
        bar_row.addWidget(self.lbl_status)
        bar_row.addStretch()
        bar_row.addWidget(self.combo_parts)
        bar_row.addWidget(self.btn_show_md)
        bar_row.addWidget(self.btn_copy)
        bar_row.addWidget(self.btn_export)
        col.addWidget(bar)

        self.code_view = QTextBrowser()
        self.code_view.setObjectName("code_view")
        self.code_view.setOpenExternalLinks(False)
        self.code_view.setHtml(PLACEHOLDER_HTML)
        col.addWidget(self.code_view, 1)

        self._highlighter = MarkdownHighlighter(self.code_view.document())

    def show_file(self, path: str):
        name = os.path.basename(path)
        self.lbl_filename.setText(name)
        self.lbl_status.setText("")
        self.combo_parts.setVisible(False) # Esconde o seletor de partes ao ver arquivo isolado
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.code_view.setPlainText(f.read())
        except Exception as e:
            self.code_view.setPlainText(f"Não foi possível ler o arquivo.\n\n{e}")

    def show_markdown(self, content: str, title="PREVIEW.md"):
        self.lbl_filename.setText(title)
        self.lbl_status.setText("● Atualizado agora")
        self.code_view.setPlainText(content)

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

        # Chamada das seções de configuração
        self._build_format_group(col)
        self._build_structure_group(col)  # <-- ESTA É A NOVA SEÇÃO
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
        group = QFrame()
        group.setObjectName("config_group")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)
        lbl = QLabel(title)
        lbl.setObjectName("lbl_config_section")
        layout.addWidget(lbl)
        return group, layout

    # --- NOVA FUNÇÃO QUE CRIA OS WIDGETS QUE ESTAVAM FALTANDO ---
    def _build_structure_group(self, parent):
        group, lay = self._make_group("Configurações da Árvore")
        
        lay.addWidget(QLabel("Escopo da Estrutura:"))
        self.combo_tree_scope = QComboBox()
        self.combo_tree_scope.setObjectName("config_input")
        self.combo_tree_scope.addItems([
            "Apenas Selecionados", 
            "Projeto Completo", 
            "Apenas Pastas"
        ])
        lay.addWidget(self.combo_tree_scope)

        self.chk_only_tree = QCheckBox("Gerar apenas estrutura (Sem código)")
        self.chk_only_tree.setObjectName("chk_config")
        lay.addWidget(self.chk_only_tree)
        
        parent.addWidget(group)

    # ... Mantenha as outras funções (_build_format_group, _build_include_group, etc.) como estavam ...
    # Mas certifique-se de manter o método update_stats e os StatCards abaixo:

    def _build_format_group(self, parent):
        group, lay = self._make_group("Formato de Saída")
        self.radio_simple   = QRadioButton("Markdown Simples")
        self.radio_detailed = QRadioButton("Markdown Detalhado")
        self.radio_toc      = QRadioButton("Com Tabela de Conteúdo")
        self.radio_simple.setChecked(True)
        self._fmt_group = QButtonGroup()
        for r in (self.radio_simple, self.radio_detailed, self.radio_toc):
            self._fmt_group.addButton(r)
        for radio, hint in zip((self.radio_simple, self.radio_detailed, self.radio_toc), 
                               ["Estrutura limpa e direta", "Inclui comentários e informações", "Gera sumário automático"]):
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
        self.chk_minify = QCheckBox("Minificar espaços")
        lay.addWidget(self.chk_rm_comments)
        lay.addWidget(self.chk_minify)
        parent.addWidget(group)

    def _build_presets_group(self, parent):
        group, lay = self._make_group("Presets de Seleção")
        self.combo_presets = QComboBox()
        self.combo_presets.setEnabled(False)
        lay.addWidget(self.combo_presets)
        btns = QHBoxLayout()
        self.btn_load = QPushButton("Carregar")
        self.btn_save = QPushButton("Salvar")
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
        self.card_files = StatCard("0", "Arquivos")
        self.card_langs = StatCard("0", "Linguagens")
        self.card_size  = StatCard("0 B", "Tamanho")
        self.card_lines = StatCard("0", "Linhas")
        grid.addWidget(self.card_files, 0, 0)
        grid.addWidget(self.card_langs, 0, 1)
        grid.addWidget(self.card_size, 1, 0)
        grid.addWidget(self.card_lines, 1, 1)
        parent.addLayout(grid)

    def update_stats(self, n_files: int, n_langs: int, size_bytes: int, total_lines: int):
        self.card_files.set_value(str(n_files))
        self.card_langs.set_value(str(n_langs))
        self.card_lines.set_value(f"{total_lines:,}".replace(",", "."))
        s = f"{size_bytes} B" if size_bytes < 1024 else f"{size_bytes/1024:.1f} KB" if size_bytes < 1024 ** 2 else f"{size_bytes/1024**2:.1f} MB"
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

        self.current_folder = ""
        self.presets_file   = os.path.join(os.path.expanduser("~"), ".codegrimoire_presets.json")
        
        # NOVO: O Markdown agora é uma Lista de partes
        self._md_parts = []
        self.root_item = None

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
        self.left   = LeftPanel()
        self.center = CenterPanel()
        self.right  = RightPanel()
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
        self.topbar.btn_generate.clicked.connect(self.generate_markdown)

        self.left.btn_all.clicked.connect(lambda: self._set_all(True))
        self.left.btn_none.clicked.connect(lambda: self._set_all(False))
        self.left.tree.itemClicked.connect(self._on_item_click)
        self.left.tree.itemExpanded.connect(self._on_folder_expand)
        self.left.tree.itemCollapsed.connect(self._on_folder_collapse)
        self.left.tree.itemChanged.connect(lambda item, col: self.count_timer.start(50))

        # Eventos do preview e visualização multi-partes
        self.center.btn_show_md.clicked.connect(self._restore_md_view)
        self.center.combo_parts.currentIndexChanged.connect(self._change_md_part)

        self.center.btn_copy.clicked.connect(self._copy_clipboard)
        self.center.btn_export.clicked.connect(self._export)

        self.right.btn_load.clicked.connect(self._load_preset)
        self.right.btn_save.clicked.connect(self._save_preset)
        self.right.btn_delete.clicked.connect(self._delete_preset)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta do projeto")
        if not folder: return
        self.current_folder = folder
        
        # Limpa tudo
        self._md_parts = []
        self.center.btn_show_md.setVisible(False)
        self.center.combo_parts.setVisible(False)
        self.center.code_view.setHtml(PLACEHOLDER_HTML)
        self.center.lbl_filename.setText("PREVIEW.md")
        self.center.lbl_status.setText("")

        self.left.set_project(folder)
        self._populate_tree(folder)
        self.topbar.btn_generate.setEnabled(True)
        self.right.combo_presets.setEnabled(True)
        self._update_preset_combo()
        self.logs.log(f"Projeto aberto: {os.path.basename(folder)}", "info")
        self.status.set_ready()

    def _on_item_click(self, item, _col):
        if item.childCount() > 0:
            item.setExpanded(not item.isExpanded())

        path = item.data(0, Qt.UserRole)
        if path and os.path.isfile(path):
            self.center.show_file(path)
            # Se já temos MD gerado, libera o botão para o usuário poder "Voltar" pra ele
            if self._md_parts:
                self.center.btn_show_md.setEnabled(True)

    def _on_folder_expand(self, item):
        text = item.text(0)
        if text.startswith("▶ "): item.setText(0, text.replace("▶ ", "▼ ", 1))

    def _on_folder_collapse(self, item):
        text = item.text(0)
        if text.startswith("▼ "): item.setText(0, text.replace("▼ ", "▶ ", 1))

    def _actual_update_count(self):
        if self.root_item:
            files = []
            self._collect_files(self.root_item, files)
            n = len(files)
            self.left.lbl_count.setText(f"{n} arquivo{'s' if n != 1 else ''} selecionado{'s' if n != 1 else ''}")

    # ==========================================
    # GERAÇÃO INTELIGENTE (DIVISÃO EM PARTES)
    # ==========================================
    def generate_markdown(self):
        """
        Gera o conteúdo Markdown final baseado nas seleções da árvore e 
        nas configurações de escopo e otimização.
        """
        if not self.current_folder:
            return

        # 1. Coleta de arquivos para o CONTEÚDO (baseado no que está marcado)
        files_to_process = []
        self._collect_files(self.root_item, files_to_process)
        
        # Flags e Configurações da UI
        only_tree    = self.right.chk_only_tree.isChecked()
        include_tree = self.right.chk_folders.isChecked()
        tree_scope   = self.right.combo_tree_scope.currentText() # "Apenas Selecionados", "Projeto Completo", "Apenas Pastas"
        include_toc  = self.right.radio_toc.isChecked()
        rm_comments  = self.right.chk_rm_comments.isChecked()
        is_split     = self.right.chk_split.isChecked()
        limit_lines  = self.right.spin_lines.value() if is_split else float('inf')
        
        # Validação inicial
        if not files_to_process and not only_tree:
            QMessageBox.warning(self, "Aviso", "Nenhum arquivo selecionado para inclusão de conteúdo.")
            return

        self.status.set_busy("Gerando...")
        self.logs.log(f"Iniciando geração (Modo: {'Apenas Estrutura' if only_tree else 'Completo'})...", "info")
        
        nome_projeto = os.path.basename(self.current_folder) or self.current_folder
        
        # 2. CONSTRUÇÃO DO CABEÇALHO (Header + Estrutura + TOC)
        header_content = f"# {nome_projeto}\n\n"
        
        if include_tree:
            header_content += "## Estrutura do Projeto\n\n```\n"
            header_content += f"{nome_projeto}/\n"
            # Chama a função recursiva com o escopo selecionado
            header_content += self._build_tree_text(self.root_item, scope=tree_scope)
            header_content += "```\n\n"

        if include_toc and not only_tree:
            header_content += "## Sumário de Arquivos\n\n"
            for fp in files_to_process:
                rel = os.path.relpath(fp, self.current_folder).replace(os.sep, '/')
                header_content += f"- {rel}\n"
            header_content += "\n"

        header_content += "## Conteúdo dos Arquivos\n\n" if not only_tree else ""

        # 3. PROCESSAMENTO DE CONTEÚDO E DIVISÃO EM PARTES
        self._md_parts = []
        current_md = header_content
        current_lines = current_md.count('\n')
        
        total_size_bytes = 0
        total_lines_all = current_lines
        exts_found = {}

        if not only_tree:
            for fp in files_to_process:
                rel = os.path.relpath(fp, self.current_folder).replace(os.sep, '/')
                _, ext = os.path.splitext(fp)
                lang = ext.lstrip('.')
                if lang:
                    exts_found[lang] = exts_found.get(lang, 0) + 1
                
                try:
                    with open(fp, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    if rm_comments:
                        code = self._strip_comments(code, lang)
                    
                    file_snippet = f"### `{rel}`\n\n```{lang}\n{code}\n```\n\n---\n\n"
                    
                except (UnicodeDecodeError, PermissionError):
                    file_snippet = f"### `{rel}`\n\n*[Arquivo binário ou sem permissão de leitura — ignorado]*\n\n---\n\n"
                except Exception as e:
                    file_snippet = f"### `{rel}`\n\n*[Erro ao ler arquivo: {str(e)}]*\n\n---\n\n"

                snippet_lines = file_snippet.count('\n')
                
                # Lógica de Divisão (Split)
                # Se adicionar este arquivo estourar o limite E já tivermos conteúdo além do header
                if is_split and (current_lines + snippet_lines) > limit_lines and current_lines > header_content.count('\n'):
                    self._md_parts.append(current_md)
                    # Nova parte começa com identificação
                    current_md = f"# {nome_projeto} (Parte {len(self._md_parts) + 1})\n\n"
                    current_lines = current_md.count('\n')

                current_md += file_snippet
                current_lines += snippet_lines
                total_lines_all += snippet_lines
                total_size_bytes += len(file_snippet.encode('utf-8'))

        # Adiciona a última (ou única) parte
        if current_md:
            self._md_parts.append(current_md)

        # 4. ATUALIZAÇÃO DA INTERFACE E ESTATÍSTICAS
        n_langs = len(exts_found.keys())
        # Se for apenas árvore, o tamanho é apenas do header
        if only_tree:
            total_size_bytes = len(header_content.encode('utf-8'))
            total_lines_all = header_content.count('\n')

        self.right.update_stats(
            len(files_to_process), 
            n_langs, 
            total_size_bytes, 
            total_lines_all
        )
        
        # Configura o Seletor de Partes (ComboBox)
        self.center.combo_parts.blockSignals(True)
        self.center.combo_parts.clear()
        
        for i, part_text in enumerate(self._md_parts):
            p_lines = part_text.count('\n')
            label = f"Parte {i+1} ({p_lines} linhas)"
            if len(self._md_parts) > 1:
                label = "📦 " + label
            self.center.combo_parts.addItem(label)
            
        self.center.combo_parts.blockSignals(False)
        self.center.combo_parts.setVisible(len(self._md_parts) > 1)

        # Exibe o resultado no Preview
        self._restore_md_view()
        
        msg_sucesso = f"Gerado com sucesso! {len(self._md_parts)} parte(s), {total_lines_all} linhas totais."
        self.logs.log(msg_sucesso, "success")
        self.status.set_ready()

    def _restore_md_view(self):
        """Volta para a visão do Markdown gerado sem recalcular"""
        if self._md_parts:
            idx = self.center.combo_parts.currentIndex()
            idx = 0 if idx < 0 else idx
            self._change_md_part(idx)
            self.center.btn_show_md.setEnabled(False) # Desabilita o botão (já estamos nele)
            if len(self._md_parts) > 1:
                self.center.combo_parts.setVisible(True)

    def _change_md_part(self, index):
        """Troca o texto principal dependendo de qual parte foi selecionada no combo"""
        if 0 <= index < len(self._md_parts):
            md = self._md_parts[index]
            titulo = "PREVIEW.md" if len(self._md_parts) == 1 else f"PREVIEW - Parte {index+1}.md"
            self.center.show_markdown(md, titulo)

    def _copy_clipboard(self):
        """Copia exatamente a parte que o usuário está visualizando"""
        if not self._md_parts: return
        
        # Pega a parte atual
        idx = self.center.combo_parts.currentIndex()
        idx = 0 if idx < 0 else idx
        
        QApplication.clipboard().setText(self._md_parts[idx])
        
        txt_log = "Conteúdo" if len(self._md_parts) == 1 else f"Parte {idx+1}"
        self.logs.log(f"{txt_log} copiada para a área de transferência.", "success")
        
        self.status.set_custom("Copiado", "#22c55e")
        self.center.btn_copy.setText("Copiado! ✓")
        QTimer.singleShot(2000, lambda: self.center.btn_copy.setText("Copiar"))
        QTimer.singleShot(1800, self.status.set_ready)

    def _export(self):
        """Se tiver partes, salva todas. Se tiver 1, salva normal."""
        if not self._md_parts:
            QMessageBox.information(self, "Aviso", "Gere o Markdown primeiro.")
            return
            
        nome = os.path.basename(self.current_folder) or "projeto"
        
        if len(self._md_parts) == 1:
            path, _ = QFileDialog.getSaveFileName(self, "Exportar Markdown", f"{nome}_contexto.md", "Markdown (*.md)")
            if path:
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(self._md_parts[0])
                    self.logs.log(f"Salvo em: {path}", "success")
                except Exception as e:
                    QMessageBox.critical(self, "Erro", str(e))
        else:
            # Multiplas partes - pergunta pela pasta
            folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta para exportar as partes")
            if folder:
                try:
                    for i, part_md in enumerate(self._md_parts):
                        file_name = f"{nome}_parte_{i+1}.md"
                        full_path = os.path.join(folder, file_name)
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(part_md)
                    self.logs.log(f"Salvo {len(self._md_parts)} arquivos em: {folder}", "success")
                    QMessageBox.information(self, "Sucesso", f"{len(self._md_parts)} partes exportadas com sucesso.")
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao exportar: {str(e)}")

    def _populate_tree(self, folder: str):
        self.left.tree.blockSignals(True)
        self.left.tree.setUpdatesEnabled(False)
        self.left.tree.clear()
        
        nome = os.path.basename(folder) or folder
        self.root_item = QTreeWidgetItem(self.left.tree, [f"▼ 📁 {nome}"])
        self.root_item.setData(0, Qt.UserRole, os.path.normpath(folder))
        self.root_item.setFlags(self.root_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsAutoTristate)
        self.root_item.setCheckState(0, Qt.Checked)
        
        self._add_items(self.root_item, folder)
        self.root_item.setExpanded(True)
        
        self.left.tree.setUpdatesEnabled(True)
        self.left.tree.blockSignals(False)
        self._actual_update_count()

    _IGNORE = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.idea', '.vscode', 'dist', 'build'}

    def _add_items(self, parent, path: str):
        try:
            entries = os.listdir(path)
        except PermissionError:
            return

        dirs  = sorted(e for e in entries if os.path.isdir(os.path.join(path, e)) and e not in self._IGNORE)
        files = sorted(e for e in entries if os.path.isfile(os.path.join(path, e)))

        for d in dirs:
            full = os.path.normpath(os.path.join(path, d))
            item = QTreeWidgetItem(parent, [f"▶ 📁 {d}"])
            item.setData(0, Qt.UserRole, full)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsAutoTristate)
            item.setCheckState(0, Qt.Checked)
            self._add_items(item, full)

        for fname in files:
            full = os.path.normpath(os.path.join(path, fname))
            item = QTreeWidgetItem(parent, [f"📄 {fname}"])
            item.setData(0, Qt.UserRole, full)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Checked)

    def _set_all(self, checked: bool):
        if self.root_item:
            self.left.tree.blockSignals(True)
            self.left.tree.setUpdatesEnabled(False)
            self.root_item.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)
            self.left.tree.setUpdatesEnabled(True)
            self.left.tree.blockSignals(False)
            self._actual_update_count()

    def _collect_files(self, item, out: list):
        if item.childCount():
            for i in range(item.childCount()):
                self._collect_files(item.child(i), out)
        elif item.checkState(0) == Qt.Checked:
            path = item.data(0, Qt.UserRole)
            if path and os.path.isfile(path):
                out.append(path)

    def _strip_comments(self, code: str, lang: str) -> str:
        if lang in ('py',): return '\n'.join(l for l in code.splitlines() if not l.strip().startswith('#'))
        if lang in ('js', 'ts', 'tsx', 'jsx', 'java', 'c', 'cpp', 'cs'):
            return '\n'.join(l for l in code.splitlines() if not l.strip().startswith('//'))
        return code

    def _build_tree_text(self, item, prefix="", scope="Apenas Selecionados") -> str:
        """Constrói a árvore de texto baseada no escopo escolhido pelo usuário"""
        result = ""
        valid_children = []
        
        # Filtra os filhos baseado no escopo escolhido
        for i in range(item.childCount()):
            child = item.child(i)
            caminho_real = child.data(0, Qt.UserRole)
            is_dir = os.path.isdir(caminho_real)
            
            if scope == "Apenas Selecionados":
                if child.checkState(0) != Qt.Unchecked:
                    valid_children.append(child)
            elif scope == "Apenas Pastas":
                if is_dir:
                    valid_children.append(child)
            else: # "Projeto Completo"
                valid_children.append(child)
                
        for i, child in enumerate(valid_children):
            caminho_real = child.data(0, Qt.UserRole)
            clean_name = os.path.basename(caminho_real)
            
            if os.path.isdir(caminho_real):
                clean_name += "/"
            
            is_last = (i == len(valid_children) - 1)
            con  = "└── " if is_last else "├── "
            result += f"{prefix}{con}{clean_name}\n"
            
            if child.childCount() > 0:
                ext = "    " if is_last else "│   "
                result += self._build_tree_text(child, prefix + ext, scope)
                
        return result

    def _load_json(self) -> dict:
        if os.path.exists(self.presets_file):
            try:
                with open(self.presets_file, 'r', encoding='utf-8') as f: return json.load(f)
            except Exception: pass
        return {}

    def _save_json(self, data: dict):
        with open(self.presets_file, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

    def _get_presets(self) -> dict:
        if not self.current_folder: return {}
        return self._load_json().get(os.path.normpath(self.current_folder), {})

    def _write_presets(self, presets: dict):
        if not self.current_folder: return
        data = self._load_json()
        data[os.path.normpath(self.current_folder)] = presets
        self._save_json(data)

    def _update_preset_combo(self):
        self.right.combo_presets.clear()
        p = self._get_presets()
        self.right.combo_presets.addItems(p.keys() if p else ["Nenhum preset"])

    def _save_preset(self):
        name, ok = QInputDialog.getText(self, "Salvar Preset", "Nome do preset:")
        if ok and name.strip():
            files = []
            self._collect_files(self.root_item, files)
            p = self._get_presets()
            p[name.strip()] = files
            self._write_presets(p)
            self._update_preset_combo()
            self.logs.log(f"Preset '{name}' salvo.", "success")

    def _load_preset(self):
        name = self.right.combo_presets.currentText()
        p    = self._get_presets()
        if name in p:
            self._set_all(False)
            self._apply_preset(self.root_item, p[name])
            self.logs.log(f"Preset '{name}' carregado.", "info")

    def _delete_preset(self):
        name = self.right.combo_presets.currentText()
        p    = self._get_presets()
        if name in p:
            del p[name]
            self._write_presets(p)
            self._update_preset_combo()
            self.logs.log(f"Preset '{name}' excluído.", "warning")

    def _apply_preset(self, item, favorites: list):
        path = item.data(0, Qt.UserRole)
        if item.childCount() == 0:
            item.setCheckState(0, Qt.Checked if path in favorites else Qt.Unchecked)
        for i in range(item.childCount()):
            self._apply_preset(item.child(i), favorites)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = CodeGrimoireApp()
    win.show()
    sys.exit(app.exec())
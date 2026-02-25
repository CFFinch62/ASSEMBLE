# assemble/app.py - Full MainWindow for ASSEMBLE IDE

from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QLabel, QMainWindow, QMessageBox,
    QSplitter, QStatusBar, QToolBar, QVBoxLayout, QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from assemble.browser.file_browser import FileBrowser
from assemble.build.build_manager import BuildManager
from assemble.config.settings import Settings
from assemble.config.settings_dialog import SettingsDialog
from assemble.config.themes import apply_theme_to_app, get_theme
from assemble.editor.find_replace import FindReplaceDialog
from assemble.editor.tab_widget import EditorTabWidget
from assemble.terminal.terminal_widget import TerminalWidget

_OPEN_FILTER = (
    "Assembly Files (*.asm *.s *.S *.nasm *.inc);;"
    "All Files (*)"
)
_SAVE_FILTER = (
    "NASM Assembly (*.asm);;"
    "GAS Assembly (*.s);;"
    "Include File (*.inc);;"
    "All Files (*)"
)

# Extensions that imply AT&T/GAS syntax
_ATT_EXTENSIONS = {".s", ".S"}
_INTEL_EXTENSIONS = {".asm", ".nasm"}


class MainWindow(QMainWindow):
    """ASSEMBLE main application window."""

    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.setWindowTitle("ASSEMBLE — Assembly Teaching Environment")
        self.resize(1024, 768)
        self._setup_ui()
        self._create_toolbar()
        self._load_settings()
        self.apply_theme()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.main_splitter)

        self.file_browser = FileBrowser()
        self.file_browser.file_selected.connect(self.open_file_from_browser)
        self.main_splitter.addWidget(self.file_browser)

        self.right_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.addWidget(self.right_splitter)

        self.editor_tabs = EditorTabWidget()
        self.right_splitter.addWidget(self.editor_tabs)

        self.terminal = TerminalWidget()
        self.right_splitter.addWidget(self.terminal)

        self.main_splitter.setSizes([200, 800])
        self.right_splitter.setSizes([500, 268])

        self.build_manager = BuildManager(self.terminal, self)
        self.build_manager.build_status.connect(self._on_build_status)

        self._create_menus()
        self._setup_status_bar()

    def _create_menus(self) -> None:
        mb = self.menuBar()

        # ── File ──────────────────────────────────────────────────────
        file_menu = mb.addMenu("&File")
        self.new_action = QAction("&New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.new_action.triggered.connect(self.new_file)
        file_menu.addAction(self.new_action)

        self.open_action = QAction("&Open…", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_file)
        file_menu.addAction(self.open_action)

        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_file)
        file_menu.addAction(self.save_action)

        save_as_action = QAction("Save &As…", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ── Edit ──────────────────────────────────────────────────────
        edit_menu = mb.addMenu("&Edit")
        find_action = QAction("&Find/Replace…", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_find_replace)
        edit_menu.addAction(find_action)
        edit_menu.addSeparator()
        prefs_action = QAction("&Preferences…", self)
        prefs_action.triggered.connect(self.open_settings)
        edit_menu.addAction(prefs_action)

        # ── View ──────────────────────────────────────────────────────
        view_menu = mb.addMenu("&View")
        self.toggle_browser = QAction("Show &File Browser", self)
        self.toggle_browser.setCheckable(True)
        self.toggle_browser.setChecked(True)
        self.toggle_browser.triggered.connect(
            lambda c: self.file_browser.setVisible(c)
        )
        view_menu.addAction(self.toggle_browser)

        self.toggle_terminal = QAction("Show &Terminal", self)
        self.toggle_terminal.setCheckable(True)
        self.toggle_terminal.setChecked(True)
        self.toggle_terminal.triggered.connect(
            lambda c: self.terminal.setVisible(c)
        )
        view_menu.addAction(self.toggle_terminal)

        # ── Build ─────────────────────────────────────────────────────
        build_menu = mb.addMenu("&Build")

        self.run_action = QAction("Assemble && &Run", self)
        self.run_action.setShortcut("Ctrl+R")
        self.run_action.setToolTip("Assemble, link, and run the current file")
        self.run_action.triggered.connect(self.assemble_link_and_run)
        build_menu.addAction(self.run_action)

        self.asm_action = QAction("Assemble &Only", self)
        self.asm_action.setShortcut("Ctrl+B")
        self.asm_action.setToolTip("Assemble to .o (no link)")
        self.asm_action.triggered.connect(self.assemble_only)
        build_menu.addAction(self.asm_action)

        self.asm_link_action = QAction("Assemble && &Link", self)
        self.asm_link_action.setShortcut("Ctrl+Shift+B")
        self.asm_link_action.setToolTip("Assemble and link (no run)")
        self.asm_link_action.triggered.connect(self.assemble_and_link)
        build_menu.addAction(self.asm_link_action)

        run_last_action = QAction("Run Last &Build", self)
        run_last_action.setShortcut("Ctrl+Shift+R")
        run_last_action.triggered.connect(lambda: self.build_manager.run())
        build_menu.addAction(run_last_action)
        build_menu.addSeparator()

        clean_action = QAction("&Clean Build Output", self)
        clean_action.triggered.connect(self.build_manager.clean)
        build_menu.addAction(clean_action)
        build_menu.addSeparator()

        clear_action = QAction("Clear &Terminal", self)
        clear_action.triggered.connect(self.terminal.clear)
        build_menu.addAction(clear_action)

        restart_action = QAction("&Restart Terminal", self)
        restart_action.triggered.connect(self.terminal.restart)
        build_menu.addAction(restart_action)

        interrupt_action = QAction("&Interrupt", self)
        interrupt_action.setShortcut("Ctrl+Shift+C")
        interrupt_action.triggered.connect(self.terminal.interrupt)
        build_menu.addAction(interrupt_action)

        # ── Help ──────────────────────────────────────────────────────
        help_menu = mb.addMenu("&Help")
        about_action = QAction("&About ASSEMBLE", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _create_toolbar(self) -> None:
        tb = QToolBar("Main Toolbar")
        self.addToolBar(tb)
        tb.addAction(self.new_action)
        tb.addAction(self.open_action)
        tb.addAction(self.save_action)
        tb.addSeparator()
        tb.addAction(self.run_action)
        tb.addAction(self.asm_action)

    def _setup_status_bar(self) -> None:
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.cursor_label = QLabel("Ln 1, Col 1")
        self.cursor_label.setMinimumWidth(100)
        self.syntax_label = QLabel("")
        self.syntax_label.setMinimumWidth(80)
        self.status_bar.addPermanentWidget(self.cursor_label)
        self.status_bar.addPermanentWidget(self.syntax_label)
        self._update_syntax_label()
        self.status_bar.showMessage("Ready")
        self.editor_tabs.currentChanged.connect(self._on_tab_changed)
        self._on_tab_changed(0)

    def _update_syntax_label(self):
        flavor = self.settings.get("build", "syntax_flavor") or "intel"
        self.syntax_label.setText("Intel/NASM" if flavor == "intel" else "AT&T/GAS")

    def _on_build_status(self, msg: str):
        self.status_bar.showMessage(msg)

    # ------------------------------------------------------------------
    # Cursor tracking
    # ------------------------------------------------------------------

    def _on_tab_changed(self, index: int) -> None:
        editor = self.editor_tabs.get_current_editor()
        if editor:
            try:
                editor.cursorPositionChanged.disconnect(self.update_cursor_position)
            except (RuntimeError, TypeError):
                pass
            editor.cursorPositionChanged.connect(self.update_cursor_position)
            self.update_cursor_position()
        else:
            self.cursor_label.setText("")

    def update_cursor_position(self) -> None:
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        self.cursor_label.setText(
            f"Ln {cursor.blockNumber()+1}, Col {cursor.columnNumber()+1}"
        )

    # ------------------------------------------------------------------
    # File actions
    # ------------------------------------------------------------------

    def new_file(self) -> None:
        self.editor_tabs.new_file()

    def open_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Assembly File", "", _OPEN_FILTER
        )
        if not path:
            return
        self._load_file(Path(path))

    def open_file_from_browser(self, path: str) -> None:
        self._load_file(Path(path))

    def _load_file(self, p: Path) -> None:
        try:
            editor = self.editor_tabs.open_file(p, p.read_text(encoding="utf-8"))
            self._auto_detect_syntax(p, editor)
            self.status_bar.showMessage(f"Opened {p.name}")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{exc}")

    def _auto_detect_syntax(self, p: Path, editor) -> None:
        """Switch highlighter flavor based on file extension."""
        suffix = p.suffix  # case-sensitive: .s ≠ .S
        if suffix in _ATT_EXTENSIONS:
            editor.set_syntax("att")
            self.settings.set("build", "syntax_flavor", "att")
        elif suffix in _INTEL_EXTENSIONS:
            editor.set_syntax("intel")
            self.settings.set("build", "syntax_flavor", "intel")
        self._update_syntax_label()

    def save_file(self) -> None:
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            return
        fp = editor.property("file_path")
        if fp:
            self._write_file(editor, fp)
        else:
            self.save_file_as()

    def save_file_as(self) -> None:
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Assembly File", "", _SAVE_FILTER
        )
        if path:
            self._write_file(editor, path)

    def _write_file(self, editor, path: str) -> None:
        try:
            p = Path(path)
            p.write_text(editor.toPlainText(), encoding="utf-8")
            editor.setProperty("file_path", str(p))
            editor.document().setModified(False)
            idx = self.editor_tabs.indexOf(editor)
            self.editor_tabs.setTabText(idx, p.name)
            self.status_bar.showMessage(f"Saved {p.name}")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Could not save file:\n{exc}")

    # ------------------------------------------------------------------
    # Build actions
    # ------------------------------------------------------------------

    def _current_file_path(self) -> str | None:
        """Return the saved path of the current file, auto-saving if needed."""
        editor = self.editor_tabs.get_current_editor()
        if not editor:
            self.status_bar.showMessage("No file open.")
            return None
        fp = editor.property("file_path")
        if not fp:
            ans = QMessageBox.question(
                self, "Save First",
                "The file must be saved before it can be assembled.\nSave now?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel,
            )
            if ans == QMessageBox.StandardButton.Save:
                self.save_file_as()
                fp = editor.property("file_path")
            if not fp:
                return None
        if editor.document().isModified():
            self._write_file(editor, fp)
        return fp

    def assemble_link_and_run(self) -> None:
        fp = self._current_file_path()
        if fp:
            self.build_manager.assemble_link_and_run(fp)
            self.terminal.setFocus()

    def assemble_only(self) -> None:
        fp = self._current_file_path()
        if fp:
            self.build_manager.assemble(fp, then_link=False)

    def assemble_and_link(self) -> None:
        fp = self._current_file_path()
        if fp:
            self.build_manager.assemble_and_link(fp)

    # ------------------------------------------------------------------
    # Edit / preferences
    # ------------------------------------------------------------------

    def show_find_replace(self) -> None:
        editor = self.editor_tabs.get_current_editor()
        if editor:
            FindReplaceDialog(editor, self).show()

    def open_settings(self) -> None:
        dlg = SettingsDialog(self, self.settings)
        if dlg.exec():
            self._update_syntax_label()
            self.apply_theme()
            # Apply updated syntax flavor to current editor
            flavor = self.settings.get("build", "syntax_flavor") or "intel"
            editor = self.editor_tabs.get_current_editor()
            if editor:
                editor.set_syntax(flavor)

    def apply_theme(self) -> None:
        theme = get_theme(self.settings.get("theme"))
        apply_theme_to_app(QApplication.instance(), theme)

    def show_about(self) -> None:
        QMessageBox.about(
            self, "About ASSEMBLE",
            "ASSEMBLE — Assembly Language Teaching Environment\n"
            "Version 0.1.0\n\n"
            "Supports Intel/NASM and AT&T/GAS syntax.\n"
            "Targets Linux x86-64 with NASM + GNU ld.\n\n"
            "© 2025–2026 Chuck Finch — Fragillidae Software",
        )

    # ------------------------------------------------------------------
    # Window state
    # ------------------------------------------------------------------

    def _load_settings(self) -> None:
        geo = self.settings.get("window", "geometry")
        if geo:
            self.restoreGeometry(bytes.fromhex(geo))
        sp = self.settings.get("window", "splitter_state")
        if sp:
            self.main_splitter.restoreState(bytes.fromhex(sp))
        rp = self.settings.get("window", "right_splitter_state")
        if rp:
            self.right_splitter.restoreState(bytes.fromhex(rp))

    def closeEvent(self, event) -> None:  # noqa: N802
        self.settings.set("window", "geometry",
                          self.saveGeometry().toHex().data().decode())
        self.settings.set("window", "splitter_state",
                          self.main_splitter.saveState().toHex().data().decode())
        self.settings.set("window", "right_splitter_state",
                          self.right_splitter.saveState().toHex().data().decode())
        self.settings.save()
        self.terminal.pty.terminate_process()
        self.terminal.pty.wait(2000)
        event.accept()

# assemble/config/settings_dialog.py - Preferences dialog for ASSEMBLE

from PyQt6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QRadioButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget,
)

from assemble.config.settings import Settings
from assemble.config.asm_detector import (
    detect_assemblers, detect_linkers, validate_tool_path,
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings: Settings | None = None):
        super().__init__(parent)
        self.settings = settings or Settings()
        self.setWindowTitle("Preferences — ASSEMBLE")
        self.setMinimumWidth(520)
        self._assemblers = []
        self._linkers = []
        self._build_ui()
        self._load_values()

    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.tabs.addTab(self._editor_tab(), "Editor")
        self.tabs.addTab(self._build_tab(), "Build")
        self.tabs.addTab(self._appearance_tab(), "Appearance")
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _editor_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self.font_family = QLineEdit()
        self.font_size = QSpinBox(); self.font_size.setRange(6, 72)
        self.tab_width = QSpinBox(); self.tab_width.setRange(1, 16)
        self.show_lines = QCheckBox("Show line numbers")
        form.addRow("Font family:", self.font_family)
        form.addRow("Font size:", self.font_size)
        form.addRow("Tab width:", self.tab_width)
        form.addRow(self.show_lines)
        return w

    def _build_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        # Syntax flavor
        flavor_group = QGroupBox("Syntax Flavor")
        fg = QHBoxLayout(flavor_group)
        self.intel_radio = QRadioButton("Intel / NASM  (mov rax, 1)")
        self.att_radio = QRadioButton("AT&T / GAS  (movq $1, %rax)")
        self._flavor_group = QButtonGroup()
        self._flavor_group.addButton(self.intel_radio)
        self._flavor_group.addButton(self.att_radio)
        fg.addWidget(self.intel_radio)
        fg.addWidget(self.att_radio)
        layout.addWidget(flavor_group)

        # Assembler
        asm_group = QGroupBox("Assembler")
        ag = QFormLayout(asm_group)
        self.asm_combo = QComboBox()
        asm_ref_btn = QPushButton("Refresh")
        asm_ref_btn.clicked.connect(self._refresh_assemblers)
        asm_row = QHBoxLayout()
        asm_row.addWidget(self.asm_combo, 1)
        asm_row.addWidget(asm_ref_btn)
        ag.addRow("Detected:", asm_row)
        self.asm_ver_label = QLabel("")
        self.asm_ver_label.setWordWrap(True)
        ag.addRow("Version:", self.asm_ver_label)
        self.asm_combo.currentIndexChanged.connect(self._on_asm_changed)
        self.asm_path = QLineEdit()
        self.asm_path.setPlaceholderText("Custom path to assembler")
        asm_test_btn = QPushButton("Test")
        self.asm_test_result = QLabel("")
        asm_test_btn.clicked.connect(lambda: self._test_tool(self.asm_path, self.asm_test_result))
        asm_path_row = QHBoxLayout()
        asm_path_row.addWidget(self.asm_path, 1)
        asm_path_row.addWidget(asm_test_btn)
        ag.addRow("Path:", asm_path_row)
        ag.addRow("", self.asm_test_result)
        self.asm_flags = QLineEdit()
        self.asm_flags.setPlaceholderText("e.g. -f elf64")
        ag.addRow("Flags:", self.asm_flags)
        layout.addWidget(asm_group)

        # Linker
        ld_group = QGroupBox("Linker")
        lg = QFormLayout(ld_group)
        self.ld_combo = QComboBox()
        ld_ref_btn = QPushButton("Refresh")
        ld_ref_btn.clicked.connect(self._refresh_linkers)
        ld_row = QHBoxLayout()
        ld_row.addWidget(self.ld_combo, 1)
        ld_row.addWidget(ld_ref_btn)
        lg.addRow("Detected:", ld_row)
        self.ld_combo.currentIndexChanged.connect(self._on_ld_changed)
        self.ld_path = QLineEdit()
        self.ld_path.setPlaceholderText("Custom path to linker (ld, gcc, etc.)")
        ld_test_btn = QPushButton("Test")
        self.ld_test_result = QLabel("")
        ld_test_btn.clicked.connect(lambda: self._test_tool(self.ld_path, self.ld_test_result))
        ld_path_row = QHBoxLayout()
        ld_path_row.addWidget(self.ld_path, 1)
        ld_path_row.addWidget(ld_test_btn)
        lg.addRow("Path:", ld_path_row)
        lg.addRow("", self.ld_test_result)
        self.ld_flags = QLineEdit()
        self.ld_flags.setPlaceholderText("e.g. -no-pie (when using gcc as linker)")
        lg.addRow("Flags:", self.ld_flags)
        layout.addWidget(ld_group)
        layout.addStretch()
        return w

    def _appearance_tab(self) -> QWidget:
        w = QWidget()
        from PyQt6.QtWidgets import QFormLayout
        form = QFormLayout(w)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        form.addRow("Theme:", self.theme_combo)
        return w

    # ------------------------------------------------------------------
    def _load_values(self):
        self.font_family.setText(self.settings.get("editor", "font_family") or "Monospace")
        self.font_size.setValue(self.settings.get("editor", "font_size") or 14)
        self.tab_width.setValue(self.settings.get("editor", "tab_width") or 8)
        self.show_lines.setChecked(bool(self.settings.get("editor", "show_line_numbers")))
        # Syntax flavor
        flavor = self.settings.get("build", "syntax_flavor") or "intel"
        self.intel_radio.setChecked(flavor == "intel")
        self.att_radio.setChecked(flavor == "att")
        # Assembler
        self._refresh_assemblers()
        self.asm_path.setText(self.settings.get("build", "assembler_path") or "nasm")
        self.asm_flags.setText(self.settings.get("build", "assembler_flags") or "-f elf64")
        # Linker
        self._refresh_linkers()
        self.ld_path.setText(self.settings.get("build", "linker_path") or "ld")
        self.ld_flags.setText(self.settings.get("build", "linker_flags") or "")
        # Theme
        theme = self.settings.get("theme") or "dark"
        idx = self.theme_combo.findText(theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

    def _refresh_assemblers(self):
        self._assemblers = detect_assemblers()
        self.asm_combo.clear()
        for a in self._assemblers:
            self.asm_combo.addItem(f"{a.name}  ({a.path})", a)
        if not self._assemblers:
            self.asm_combo.addItem("No assemblers found — install NASM")

    def _refresh_linkers(self):
        self._linkers = detect_linkers()
        self.ld_combo.clear()
        for l in self._linkers:
            self.ld_combo.addItem(f"{l.name}  ({l.path})", l)
        if not self._linkers:
            self.ld_combo.addItem("No linkers found")

    def _on_asm_changed(self, idx: int):
        if not self._assemblers or idx >= len(self._assemblers):
            return
        a = self._assemblers[idx]
        self.asm_ver_label.setText(a.version or "")
        self.asm_path.setText(a.path)
        if a.syntax == "att":
            self.att_radio.setChecked(True)
        else:
            self.intel_radio.setChecked(True)

    def _on_ld_changed(self, idx: int):
        if not self._linkers or idx >= len(self._linkers):
            return
        self.ld_path.setText(self._linkers[idx].path)

    def _test_tool(self, path_edit: QLineEdit, result_label: QLabel):
        ok, msg = validate_tool_path(path_edit.text().strip())
        if ok:
            result_label.setText(f"✓ {msg}")
            result_label.setStyleSheet("color: green;")
        else:
            result_label.setText(f"✗ {msg}")
            result_label.setStyleSheet("color: red;")

    def _save_and_accept(self):
        self.settings.set("editor", "font_family", self.font_family.text())
        self.settings.set("editor", "font_size", self.font_size.value())
        self.settings.set("editor", "tab_width", self.tab_width.value())
        self.settings.set("editor", "show_line_numbers", self.show_lines.isChecked())
        flavor = "intel" if self.intel_radio.isChecked() else "att"
        self.settings.set("build", "syntax_flavor", flavor)
        self.settings.set("build", "assembler_path", self.asm_path.text().strip() or "nasm")
        self.settings.set("build", "assembler_flags", self.asm_flags.text().strip())
        self.settings.set("build", "linker_path", self.ld_path.text().strip() or "ld")
        self.settings.set("build", "linker_flags", self.ld_flags.text().strip())
        self.settings.set("theme", self.theme_combo.currentText())
        self.settings.save()
        self.accept()

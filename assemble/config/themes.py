# assemble/config/themes.py - Theme definitions for ASSEMBLE

from dataclasses import dataclass
from PyQt6.QtWidgets import QApplication


@dataclass
class Theme:
    name: str
    background: str
    foreground: str
    line_number_bg: str
    line_number_fg: str
    selection_bg: str
    mnemonic: str        # MOV ADD SUB JMP CALL RET etc. (bold)
    register: str        # rax rbx rcx %rax etc.
    directive: str       # section global extern db dw .text .data
    label: str           # main: loop_start:
    size_specifier: str  # BYTE WORD DWORD QWORD
    macro: str           # %define %macro %include
    syscall: str         # syscall instruction / hints
    string: str          # "quoted strings"
    comment: str         # ; line comments  # GAS comments
    number: str          # 42 0x1F 1Fh 10110b
    operator: str        # [ ] + - * ,
    app_background: str
    app_foreground: str
    widget_background: str
    border: str
    button_background: str
    button_foreground: str
    highlight: str
    tab_background: str


DARK_THEME = Theme(
    name="dark",
    background="#1e1e2e",        # Catppuccin-inspired dark
    foreground="#cdd6f4",
    line_number_bg="#181825",
    line_number_fg="#585b70",
    selection_bg="#313244",
    mnemonic="#89b4fa",          # Blue — instructions
    register="#f38ba8",          # Red — registers
    directive="#f5c2e7",         # Pink — assembler directives
    label="#a6e3a1",             # Green — labels
    size_specifier="#94e2d5",    # Teal — BYTE/WORD/DWORD/QWORD
    macro="#cba6f7",             # Purple — %define %macro
    syscall="#fab387",           # Peach — syscall/system numbers
    string="#a6e3a1",            # Green — strings
    comment="#6c7086",           # Subtle grey — comments
    number="#fab387",            # Peach — numerics
    operator="#89dceb",          # Sky — punctuation/operators
    app_background="#1e1e2e",
    app_foreground="#cdd6f4",
    widget_background="#181825",
    border="#313244",
    button_background="#313244",
    button_foreground="#cdd6f4",
    highlight="#89b4fa",
    tab_background="#24273a",
)

LIGHT_THEME = Theme(
    name="light",
    background="#ffffff",
    foreground="#1e1e1e",
    line_number_bg="#f3f3f3",
    line_number_fg="#6e6e6e",
    selection_bg="#add6ff",
    mnemonic="#0000ff",
    register="#a31515",
    directive="#811f3f",
    label="#267f99",
    size_specifier="#008080",
    macro="#7b3f9e",
    syscall="#c65a00",
    string="#008000",
    comment="#808080",
    number="#098658",
    operator="#000000",
    app_background="#f5f5f5",
    app_foreground="#1e1e1e",
    widget_background="#ffffff",
    border="#cccccc",
    button_background="#e8e8e8",
    button_foreground="#1e1e1e",
    highlight="#0078d4",
    tab_background="#ececec",
)


def get_theme(name: str | None) -> Theme:
    if name == "light":
        return LIGHT_THEME
    return DARK_THEME


def apply_theme_to_app(app: QApplication, theme: Theme) -> None:
    if app is None:
        return
    app.setStyleSheet(f"""
        QMainWindow, QDialog, QWidget {{
            background-color: {theme.app_background};
            color: {theme.app_foreground};
        }}
        QMenuBar {{
            background-color: {theme.widget_background};
            color: {theme.app_foreground};
        }}
        QMenuBar::item:selected {{ background-color: {theme.highlight}; color: white; }}
        QMenu {{ background-color: {theme.widget_background}; color: {theme.app_foreground};
                 border: 1px solid {theme.border}; }}
        QMenu::item:selected {{ background-color: {theme.highlight}; color: white; }}
        QToolBar {{
            background-color: {theme.widget_background};
            border-bottom: 1px solid {theme.border};
        }}
        QStatusBar {{
            background-color: {theme.widget_background};
            color: {theme.app_foreground};
        }}
        QTabWidget::pane {{ border: 1px solid {theme.border}; }}
        QTabBar::tab {{
            background-color: {theme.tab_background};
            color: {theme.app_foreground};
            padding: 5px 10px;
            border: 1px solid {theme.border};
        }}
        QTabBar::tab:selected {{ background-color: {theme.background}; }}
        QTreeView, QListView {{
            background-color: {theme.widget_background};
            color: {theme.app_foreground};
            border: none;
        }}
        QTreeView::item:selected {{ background-color: {theme.highlight}; color: white; }}
        QSplitter::handle {{ background-color: {theme.border}; }}
        QPushButton {{
            background-color: {theme.button_background};
            color: {theme.button_foreground};
            border: 1px solid {theme.border};
            padding: 4px 12px;
            border-radius: 3px;
        }}
        QPushButton:hover {{ background-color: {theme.highlight}; color: white; }}
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {theme.background};
            color: {theme.foreground};
            border: 1px solid {theme.border};
        }}
        QScrollBar:vertical {{ background: {theme.widget_background}; width: 12px; }}
        QScrollBar::handle:vertical {{
            background: {theme.border}; min-height: 20px; border-radius: 4px;
        }}
        QScrollBar:horizontal {{ background: {theme.widget_background}; height: 12px; }}
        QScrollBar::handle:horizontal {{
            background: {theme.border}; min-width: 20px; border-radius: 4px;
        }}
        QLabel {{ color: {theme.app_foreground}; }}
        QCheckBox, QRadioButton {{ color: {theme.app_foreground}; }}
        QComboBox {{
            background-color: {theme.widget_background};
            color: {theme.app_foreground};
            border: 1px solid {theme.border};
        }}
        QGroupBox {{
            color: {theme.app_foreground};
            border: 1px solid {theme.border};
            margin-top: 6px;
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 8px;
        }}
    """)

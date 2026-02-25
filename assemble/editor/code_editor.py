# assemble/editor/code_editor.py - Code editor for Assembly

from PyQt6.QtWidgets import QPlainTextEdit, QWidget
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QKeyEvent, QPainter, QTextCursor

from assemble.editor.highlighter import AsmHighlighter
from assemble.config.settings import Settings
from assemble.config.themes import get_theme


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self._editor.paint_line_numbers(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self._setup_font()
        self.line_number_area = LineNumberArea(self)
        self._syntax = self.settings.get("build", "syntax_flavor") or "intel"
        self.highlighter = AsmHighlighter(self.document(), syntax=self._syntax)
        self.blockCountChanged.connect(self._update_line_number_margin)
        self.updateRequest.connect(self._update_line_number_area)
        self._update_line_number_margin()

    def _setup_font(self):
        family = self.settings.get("editor", "font_family") or "Monospace"
        size   = self.settings.get("editor", "font_size") or 14
        font = QFont(family, size)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        tab_width = self.settings.get("editor", "tab_width") or 8
        fm = QFontMetrics(font)
        self.setTabStopDistance(tab_width * fm.horizontalAdvance(" "))

    def apply_theme(self, theme_name: str | None = None):
        theme = get_theme(theme_name or self.settings.get("theme"))
        self.highlighter.set_theme(theme)
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme.background};
                color: {theme.foreground};
                selection-background-color: {theme.selection_bg};
                border: none;
            }}
        """)
        self.line_number_area.setStyleSheet(
            f"background-color: {theme.line_number_bg};"
        )

    def set_syntax(self, flavor: str):
        """Switch highlighter between 'intel' and 'att' modes."""
        self._syntax = flavor
        self.highlighter.set_syntax(flavor)

    def line_number_area_width(self) -> int:
        digits = max(1, len(str(self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_line_number_margin(self):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect: QRect, dy: int):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self._update_line_number_margin()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def paint_line_numbers(self, event):
        painter = QPainter(self.line_number_area)
        theme = get_theme(self.settings.get("theme"))
        painter.fillRect(event.rect(), QColor(theme.line_number_bg))
        painter.setFont(self.font())
        block = self.firstVisibleBlock()
        block_num = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QColor(theme.line_number_fg))
                painter.drawText(
                    0, top,
                    self.line_number_area.width() - 5,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    str(block_num + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_num += 1

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            indent = ""
            for ch in cursor.block().text():
                if ch in (" ", "\t"):
                    indent += ch
                else:
                    break
            super().keyPressEvent(event)
            self.insertPlainText(indent)
        elif event.key() == Qt.Key.Key_Tab:
            tab_width = self.settings.get("editor", "tab_width") or 8
            self.insertPlainText(" " * tab_width)
        else:
            super().keyPressEvent(event)

    def selected_text(self) -> str:
        return self.textCursor().selectedText().replace("\u2029", "\n")

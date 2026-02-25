# assemble/terminal/terminal_widget.py - PTY-backed terminal panel

import os
import pyte
from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import (
    QPainter, QFont, QColor, QFontMetrics, QKeyEvent, QBrush,
    QMouseEvent, QGuiApplication,
)
from assemble.terminal.pty_process import PTYProcess
from assemble.config.settings import Settings


class TerminalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.cols, self.rows = 80, 24
        self.screen = pyte.Screen(self.cols, self.rows)
        self.stream = pyte.Stream(self.screen)
        self.pty = PTYProcess()
        self.pty.data_received.connect(self.on_data_received)
        self.pty.process_exited.connect(self.on_process_exited)
        self._setup_font()
        self.cursor_visible = True
        self._cursor_timer = QTimer(self)
        self._cursor_timer.timeout.connect(self._toggle_cursor)
        self._cursor_timer.start(500)
        self._sel_start: tuple | None = None
        self._sel_end: tuple | None = None
        self._selecting = False
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)
        self.pty.start()

    def _setup_font(self):
        family = self.settings.get("editor", "font_family") or "Monospace"
        size   = self.settings.get("editor", "font_size") or 14
        self.font = QFont(family, size)
        self.font.setStyleHint(QFont.StyleHint.Monospace)
        self.fm = QFontMetrics(self.font)
        self.char_width  = self.fm.horizontalAdvance("W")
        self.char_height = self.fm.height()
        self.resize_terminal()

    def resizeEvent(self, event):
        self.resize_terminal()
        super().resizeEvent(event)

    def resize_terminal(self):
        nc = max(1, self.width() // self.char_width)
        nr = max(1, self.height() // self.char_height)
        if nc != self.cols or nr != self.rows:
            self.cols, self.rows = nc, nr
            self.screen.resize(self.rows, self.cols)
            self.pty.resize(self.rows, self.cols)
            self.update()

    def on_data_received(self, data: bytes):
        try:
            self.stream.feed(data.decode("utf-8", errors="replace"))
            self.update()
        except Exception:
            pass

    def on_process_exited(self, code: int):
        self.stream.feed(f"\r\n[Shell exited with code {code}]\r\n")
        self.update()

    def write(self, data: bytes):
        self.pty.write(data)

    def send_text(self, text: str):
        self.pty.write(text.encode("utf-8"))

    def keyPressEvent(self, event: QKeyEvent):
        key  = event.key()
        text = event.text()
        mods = event.modifiers()
        sequences = {
            Qt.Key.Key_Return:    b"\r",
            Qt.Key.Key_Backspace: b"\x7f",
            Qt.Key.Key_Tab:       b"\t",
            Qt.Key.Key_Up:        b"\x1b[A",
            Qt.Key.Key_Down:      b"\x1b[B",
            Qt.Key.Key_Right:     b"\x1b[C",
            Qt.Key.Key_Left:      b"\x1b[D",
            Qt.Key.Key_Home:      b"\x1b[H",
            Qt.Key.Key_End:       b"\x1b[F",
        }
        if key == Qt.Key.Key_C and mods & Qt.KeyboardModifier.ControlModifier:
            if self._get_sel() is not None:
                self._copy_selection()
            else:
                self.write(b"\x03")
        elif key == Qt.Key.Key_D and mods & Qt.KeyboardModifier.ControlModifier:
            self.write(b"\x04")
        elif key in sequences:
            self.write(sequences[key])
        elif text:
            self.write(text.encode("utf-8"))

    def _cell(self, pos: QPoint):
        return (
            max(0, min(self.rows - 1, pos.y() // self.char_height)),
            max(0, min(self.cols - 1, pos.x() // self.char_width)),
        )

    def mousePressEvent(self, e: QMouseEvent):
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        if e.button() == Qt.MouseButton.LeftButton:
            self._sel_start = self._sel_end = self._cell(e.pos())
            self._selecting = True
            self.update()
        e.accept()

    def mouseMoveEvent(self, e: QMouseEvent):
        if self._selecting and e.buttons() & Qt.MouseButton.LeftButton:
            self._sel_end = self._cell(e.pos())
            self.update()

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.LeftButton:
            self._selecting = False
            if self._sel_start == self._sel_end:
                self._sel_start = self._sel_end = None
            self.update()

    def _get_sel(self):
        if not self._sel_start or not self._sel_end:
            return None
        s, e = self._sel_start, self._sel_end
        return (min(s, e), max(s, e))

    def _in_sel(self, row, col):
        sel = self._get_sel()
        if not sel:
            return False
        (sr, sc), (er, ec) = sel
        if row < sr or row > er:
            return False
        if row == sr and col < sc:
            return False
        if row == er and col > ec:
            return False
        return True

    def _copy_selection(self):
        sel = self._get_sel()
        if not sel:
            return
        (sr, sc), (er, ec) = sel
        lines = []
        for row in range(sr, er + 1):
            chars = self.screen.buffer[row]
            c0, c1 = (sc if row == sr else 0), (ec if row == er else self.cols - 1)
            lines.append("".join(chars[c].data for c in range(c0, c1 + 1)).rstrip())
        text = "\n".join(lines)
        if text:
            QGuiApplication.clipboard().setText(text)

    def _context_menu(self, point: QPoint):
        menu = QMenu(self)
        copy_act = menu.addAction("Copy")
        copy_act.setEnabled(self._get_sel() is not None)
        copy_act.triggered.connect(self._copy_selection)
        menu.exec(self.mapToGlobal(point))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self.font)
        painter.fillRect(self.rect(), QColor("#0f0f0f"))
        fg = QColor("#cccccc")
        sel_color = QColor(0, 120, 200, 120)
        for y in range(self.rows):
            row_chars = self.screen.buffer[y]
            for x in range(self.cols):
                if self._in_sel(y, x):
                    painter.fillRect(
                        x * self.char_width, y * self.char_height,
                        self.char_width, self.char_height, sel_color,
                    )
                painter.setPen(fg)
                painter.drawText(
                    x * self.char_width,
                    y * self.char_height + self.fm.ascent(),
                    row_chars[x].data,
                )
        if self.cursor_visible and self.pty.running:
            cx, cy = self.screen.cursor.x, self.screen.cursor.y
            painter.setBrush(QBrush(QColor(200, 200, 200, 100)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(
                cx * self.char_width, cy * self.char_height,
                self.char_width, self.char_height,
            )

    def _toggle_cursor(self):
        self.cursor_visible = not self.cursor_visible
        cx, cy = self.screen.cursor.x, self.screen.cursor.y
        self.update(cx * self.char_width, cy * self.char_height,
                    self.char_width, self.char_height)

    def restart(self):
        self.pty.terminate_process()
        self.pty.wait()
        self.screen.reset()
        self._sel_start = self._sel_end = None
        self.pty = PTYProcess()
        self.pty.data_received.connect(self.on_data_received)
        self.pty.process_exited.connect(self.on_process_exited)
        self.pty.start()
        self.pty.resize(self.rows, self.cols)
        self.update()

    def clear(self):
        self.screen.reset()
        self._sel_start = self._sel_end = None
        self.update()

    def interrupt(self):
        self.write(b"\x03")

    def focusInEvent(self, event):
        self.cursor_visible = True
        self.update()
        super().focusInEvent(event)

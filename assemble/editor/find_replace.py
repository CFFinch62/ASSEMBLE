# assemble/editor/find_replace.py - Find / Replace dialog

from PyQt6.QtWidgets import (
    QCheckBox, QDialog, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextDocument, QTextCursor


class FindReplaceDialog(QDialog):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Find / Replace")
        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint
        )
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        for label, attr in [("Find:", "find_input"), ("Replace:", "replace_input")]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            setattr(self, attr, QLineEdit())
            row.addWidget(getattr(self, attr))
            layout.addLayout(row)
        self.case_check = QCheckBox("Case sensitive")
        layout.addWidget(self.case_check)
        btn_row = QHBoxLayout()
        for label, slot in [
            ("Find Next",   self.find_next),
            ("Replace",     self.replace_one),
            ("Replace All", self.replace_all),
            ("Close",       self.close),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

    def _flags(self):
        f = QTextDocument.FindFlag(0)
        if self.case_check.isChecked():
            f |= QTextDocument.FindFlag.FindCaseSensitively
        return f

    def find_next(self) -> bool:
        text = self.find_input.text()
        if not text:
            return False
        found = self.editor.find(text, self._flags())
        if not found:
            c = self.editor.textCursor()
            c.movePosition(QTextCursor.MoveOperation.Start)
            self.editor.setTextCursor(c)
            found = self.editor.find(text, self._flags())
        self.status_label.setText("" if found else "Not found.")
        return found

    def replace_one(self):
        if self.editor.textCursor().hasSelection():
            self.editor.textCursor().insertText(self.replace_input.text())
        self.find_next()

    def replace_all(self):
        text, rep = self.find_input.text(), self.replace_input.text()
        if not text:
            return
        c = self.editor.textCursor()
        c.movePosition(QTextCursor.MoveOperation.Start)
        self.editor.setTextCursor(c)
        count = 0
        while self.editor.find(text, self._flags()):
            self.editor.textCursor().insertText(rep)
            count += 1
        self.status_label.setText(f"Replaced {count} occurrence(s).")

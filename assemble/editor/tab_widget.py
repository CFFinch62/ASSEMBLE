# assemble/editor/tab_widget.py

from pathlib import Path
from PyQt6.QtWidgets import QTabWidget
from assemble.editor.code_editor import CodeEditor


class EditorTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.new_file()

    def new_file(self) -> CodeEditor:
        editor = CodeEditor()
        idx = self.addTab(editor, "untitled.asm")
        editor.setProperty("file_path", "")
        editor.document().modificationChanged.connect(
            lambda modified, i=idx: self._on_modified(modified, i)
        )
        self.setCurrentIndex(idx)
        return editor

    def open_file(self, path: Path, content: str) -> CodeEditor:
        for i in range(self.count()):
            w = self.widget(i)
            if w.property("file_path") == str(path):
                self.setCurrentIndex(i)
                return w
        editor = CodeEditor()
        editor.setPlainText(content)
        editor.setProperty("file_path", str(path))
        editor.document().setModified(False)
        idx = self.addTab(editor, path.name)
        editor.document().modificationChanged.connect(
            lambda modified, i=idx: self._on_modified(modified, i)
        )
        self.setCurrentIndex(idx)
        return editor

    def close_tab(self, index: int):
        self.removeTab(index)
        if self.count() == 0:
            self.new_file()

    def get_current_editor(self) -> CodeEditor | None:
        return self.currentWidget()

    def _on_modified(self, modified: bool, index: int):
        if index < self.count():
            title = self.tabText(index).rstrip("*")
            self.setTabText(index, title + ("*" if modified else ""))

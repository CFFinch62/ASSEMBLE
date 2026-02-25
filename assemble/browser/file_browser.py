# assemble/browser/file_browser.py - File browser filtered to Assembly files

import shutil
from pathlib import Path

from PyQt6.QtWidgets import (
    QInputDialog, QMenu, QMessageBox, QTreeView, QVBoxLayout, QWidget,
    QHBoxLayout, QLabel, QToolButton
)
from PyQt6.QtCore import QDir, QSortFilterProxyModel, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QFileSystemModel, QFont

from assemble.config.settings import Settings


_ASM_EXTENSIONS = {".asm", ".s", ".S", ".nasm", ".inc"}


class AsmFileFilterProxy(QSortFilterProxyModel):
    def filterAcceptsRow(self, row: int, parent) -> bool:
        model = self.sourceModel()
        idx = model.index(row, 0, parent)
        if model.isDir(idx):
            return True
        name = model.fileName(idx)
        # .S is uppercase — must preserve case
        suffix = Path(name).suffix
        return suffix in _ASM_EXTENSIONS or suffix.lower() in _ASM_EXTENSIONS


class FileBrowser(QWidget):
    file_selected = pyqtSignal(str)
    root_path_changed = pyqtSignal(str)
    bookmarks_changed = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self._root_path: Path | None = None
        self._bookmarks: list[Path] = []
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header for Toolbar
        self.header = QWidget()
        self.header.setStyleSheet("background-color: #2D2D2D; padding: 4px;")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(4, 4, 4, 4)

        self.title_label = QLabel("EXPLORER")
        self.title_label.setFont(QFont("Monospace", 9, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #808080;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        # Navigation buttons
        self.home_btn = QToolButton()
        self.home_btn.setText("⌂")
        self.home_btn.setToolTip("Go to Home Directory")
        self.home_btn.clicked.connect(self._go_home)
        self.home_btn.setStyleSheet("QToolButton { background: transparent; color: #808080; border: none; font-size: 14px; padding: 0 4px; } QToolButton:hover { color: #D4D4D4; }")
        header_layout.addWidget(self.home_btn)

        self.up_btn = QToolButton()
        self.up_btn.setText("↑")
        self.up_btn.setToolTip("Go Up to Parent Folder")
        self.up_btn.clicked.connect(self._go_up)
        self.up_btn.setStyleSheet("QToolButton { background: transparent; color: #808080; border: none; font-size: 14px; padding: 0 4px; } QToolButton:hover { color: #D4D4D4; }")
        header_layout.addWidget(self.up_btn)

        self.bookmarks_btn = QToolButton()
        self.bookmarks_btn.setText("★")
        self.bookmarks_btn.setToolTip("Bookmarks")
        self.bookmarks_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.bookmarks_btn.setStyleSheet("QToolButton { background: transparent; color: #808080; border: none; font-size: 14px; padding: 0 4px; } QToolButton::menu-indicator { image: none; } QToolButton:hover { color: #D4D4D4; }")
        
        self.bookmarks_menu = QMenu(self)
        self.bookmarks_menu.aboutToShow.connect(self._update_bookmarks_menu)
        self.bookmarks_btn.setMenu(self.bookmarks_menu)
        header_layout.addWidget(self.bookmarks_btn)

        layout.addWidget(self.header)

        # File system model
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())

        self.proxy = AsmFileFilterProxy()
        self.proxy.setSourceModel(self.model)
        self.proxy.setDynamicSortFilter(True)

        self.tree = QTreeView()
        self.tree.setModel(self.proxy)
        self.tree.setHeaderHidden(True)
        for col in range(1, self.model.columnCount()):
            self.tree.hideColumn(col)
        self.tree.setAnimated(True)
        self.tree.setExpandsOnDoubleClick(False)
        self.tree.setSortingEnabled(True)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        self.tree.doubleClicked.connect(self._on_double_clicked)
        layout.addWidget(self.tree)

        self._load_settings()

    def set_root(self, path: str) -> None:
        self._root_path = Path(path)
        src_idx = self.model.index(str(self._root_path))
        proxy_idx = self.proxy.mapFromSource(src_idx)
        self.tree.setRootIndex(proxy_idx)
        self.title_label.setText(self._root_path.name.upper())
        self.settings.set("browser", "last_directory", str(self._root_path))
        self.settings.save()
        self.root_path_changed.emit(str(self._root_path))

    def _go_home(self):
        self.set_root(str(Path.home()))

    def _go_up(self):
        if self._root_path and self._root_path.parent != self._root_path:
            self.set_root(str(self._root_path.parent))

    def get_bookmarks(self) -> list[str]:
        return [str(p) for p in self._bookmarks]

    def set_bookmarks(self, paths: list[str]):
        self._bookmarks = [Path(p) for p in paths if p]
        self._save_bookmarks_to_settings()

    def _save_bookmarks_to_settings(self):
        self.settings.set("browser", "bookmarks", self.get_bookmarks())
        self.settings.save()

    def _update_bookmarks_menu(self):
        self.bookmarks_menu.clear()
        if self._root_path and self._root_path not in self._bookmarks:
            action = self.bookmarks_menu.addAction(f"Bookmark '{self._root_path.name}'")
            action.triggered.connect(lambda: self._add_bookmark(self._root_path))
            self.bookmarks_menu.addSeparator()
            
        if not self._bookmarks:
            disabled = self.bookmarks_menu.addAction("(No bookmarks)")
            disabled.setEnabled(False)
        else:
            for path in self._bookmarks:
                action = self.bookmarks_menu.addAction(path.name)
                action.setToolTip(str(path))
                action.triggered.connect(lambda checked, p=path: self.set_root(str(p)))
            self.bookmarks_menu.addSeparator()
            clear_action = self.bookmarks_menu.addAction("Clear Bookmarks")
            clear_action.triggered.connect(self._clear_bookmarks)

    def _add_bookmark(self, path: Path):
        if path not in self._bookmarks:
            self._bookmarks.append(path)
            self._save_bookmarks_to_settings()
            self.bookmarks_changed.emit([str(p) for p in self._bookmarks])

    def _clear_bookmarks(self):
        self._bookmarks.clear()
        self._save_bookmarks_to_settings()
        self.bookmarks_changed.emit([])

    def _src(self, proxy_idx):
        return self.proxy.mapToSource(proxy_idx)

    def _on_double_clicked(self, proxy_idx):
        src = self._src(proxy_idx)
        path = self.model.filePath(src)
        if self.model.isDir(src):
            self.set_root(path)
        else:
            self.file_selected.emit(path)

    def _show_context_menu(self, pos):
        proxy_idx = self.tree.indexAt(pos)
        src_idx = self._src(proxy_idx)
        is_dir = self.model.isDir(src_idx)
        path = self.model.filePath(src_idx) if src_idx.isValid() else ""

        menu = QMenu(self)

        new_file = QAction("New Assembly File", self)
        new_file.triggered.connect(
            lambda: self._new_file(path if is_dir else str(Path(path).parent))
        )
        menu.addAction(new_file)

        new_folder = QAction("New Folder", self)
        new_folder.triggered.connect(
            lambda: self._new_folder(path if is_dir else str(Path(path).parent))
        )
        menu.addAction(new_folder)

        if src_idx.isValid():
            menu.addSeparator()
            if is_dir:
                open_folder = QAction("Open Folder", self)
                open_folder.triggered.connect(lambda: self.set_root(path))
                menu.addAction(open_folder)
            
            rename = QAction("Rename", self)
            rename.triggered.connect(lambda: self._rename(path))
            menu.addAction(rename)
            delete = QAction("Delete", self)
            delete.triggered.connect(lambda: self._delete(path, is_dir))
            menu.addAction(delete)

        menu.exec(self.tree.viewport().mapToGlobal(pos))

    def _new_file(self, dir_path: str):
        if not dir_path:
            dir_path = str(self._root_path)
        name, ok = QInputDialog.getText(
            self, "New Assembly File", "File name:", text="untitled.asm"
        )
        if ok and name:
            if not any(name.endswith(e) for e in _ASM_EXTENSIONS):
                name += ".asm"
            path = Path(dir_path) / name
            try:
                path.touch(exist_ok=False)
            except FileExistsError:
                QMessageBox.warning(self, "Error", f"File already exists: {name}")

    def _new_folder(self, dir_path: str):
        if not dir_path:
            dir_path = str(self._root_path)
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and name:
            try:
                (Path(dir_path) / name).mkdir(parents=False, exist_ok=False)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _rename(self, path: str):
        p = Path(path)
        name, ok = QInputDialog.getText(self, "Rename", "New name:", text=p.name)
        if ok and name:
            try:
                p.rename(p.parent / name)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _delete(self, path: str, is_dir: bool):
        p = Path(path)
        ans = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete {'folder' if is_dir else 'file'} '{p.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if ans == QMessageBox.StandardButton.Yes:
            try:
                shutil.rmtree(p) if is_dir else p.unlink()
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def _load_settings(self):
        last_dir = self.settings.get("browser", "last_directory")
        if last_dir and Path(last_dir).is_dir():
            self.set_root(last_dir)
        else:
            self.set_root(str(Path.home()))
            
        saved_bookmarks = self.settings.get("browser", "bookmarks")
        if saved_bookmarks and isinstance(saved_bookmarks, list):
            self.set_bookmarks(saved_bookmarks)

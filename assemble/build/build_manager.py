# assemble/build/build_manager.py
# Two-step build pipeline: assemble (.asm → .o) then link (.o → binary).

import os
from pathlib import Path

from PyQt6.QtCore import QObject, QProcess, pyqtSignal

from assemble.config.settings import Settings


class BuildManager(QObject):
    # ── Per-step signals ────────────────────────────────────────────────
    assemble_started  = pyqtSignal(str)          # emits command string
    assemble_finished = pyqtSignal(int, str)     # (return_code, output)
    link_started      = pyqtSignal(str)          # emits command string
    link_finished     = pyqtSignal(int, str)     # (return_code, output)
    run_started       = pyqtSignal(str)          # emits executable path
    build_status      = pyqtSignal(str)          # status bar text

    def __init__(self, terminal, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.terminal = terminal
        self._last_binary: str = ""
        self._pending_link_obj: str = ""
        self._pending_run: bool = False
        self._proc = QProcess(self)
        self._proc.readyReadStandardOutput.connect(self._on_stdout)
        self._proc.readyReadStandardError.connect(self._on_stderr)
        self._proc.finished.connect(self._on_finished)
        self._output_buf: list[str] = []
        self._current_phase: str = ""  # "assemble" or "link"
        self._source_path: str = ""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def assemble(self, source_path: str, *, then_link: bool = False, then_run: bool = False) -> None:
        """Assemble *source_path* to an object file."""
        if self._proc.state() != QProcess.ProcessState.NotRunning:
            self._print("[BuildManager] Build already in progress.\n")
            return
        self._source_path = source_path
        self._pending_link_obj = ""
        self._pending_run = then_run

        p = Path(source_path)
        output_dir = self._resolve_output_dir(p)
        obj = str(output_dir / (p.stem + ".o"))

        asm_path  = self.settings.get("build", "assembler_path") or "nasm"
        asm_flags = self.settings.get("build", "assembler_flags") or "-f elf64"
        args = asm_flags.split() + [source_path, "-o", obj]
        cmd = f"{asm_path} {' '.join(args)}"

        self._current_phase = "assemble"
        self._output_buf = []
        self._pending_link_obj = obj if then_link or then_run else ""

        self.build_status.emit(f"Assembling {p.name}…")
        self.assemble_started.emit(cmd)
        self._print(f"\n\033[1;34m▶ {cmd}\033[0m\n")
        self._proc.start(asm_path, args)

    def assemble_and_link(self, source_path: str) -> None:
        self.assemble(source_path, then_link=True, then_run=False)

    def assemble_link_and_run(self, source_path: str) -> None:
        self.assemble(source_path, then_link=True, then_run=True)

    def link(self, obj_path: str) -> None:
        """Link *obj_path* to a binary."""
        if self._proc.state() != QProcess.ProcessState.NotRunning:
            self._print("[BuildManager] Build already in progress.\n")
            return
        p = Path(obj_path)
        output_dir = self._resolve_output_dir(p)
        binary = str(output_dir / p.stem)
        self._last_binary = binary

        ld_path  = self.settings.get("build", "linker_path") or "ld"
        ld_flags = self.settings.get("build", "linker_flags") or ""
        args = (ld_flags.split() if ld_flags.strip() else []) + [obj_path, "-o", binary]
        cmd = f"{ld_path} {' '.join(args)}"

        self._current_phase = "link"
        self._output_buf = []

        self.build_status.emit(f"Linking {p.stem}…")
        self.link_started.emit(cmd)
        self._print(f"\033[1;34m▶ {cmd}\033[0m\n")
        self._proc.start(ld_path, args)

    def run(self, executable_path: str | None = None) -> None:
        """Run the binary in the terminal."""
        path = executable_path or self._last_binary
        if not path:
            self._print("[BuildManager] No binary to run — build first.\n")
            return
        if not os.path.isfile(path):
            self._print(f"[BuildManager] Executable not found: {path}\n")
            return
        self.run_started.emit(path)
        self.build_status.emit("Running…")
        self._print(f"\033[1;32m▶ {path}\033[0m\n")
        self.terminal.send_text(f"{path}\n")

    def clean(self) -> None:
        """Delete the object file and binary for the last source."""
        if not self._source_path:
            return
        p = Path(self._source_path)
        output_dir = self._resolve_output_dir(p)
        for target in [output_dir / (p.stem + ".o"), output_dir / p.stem]:
            if target.exists():
                target.unlink()
                self._print(f"[Clean] Removed {target}\n")
        self.build_status.emit("Cleaned.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_output_dir(self, source_path: Path) -> Path:
        out_dir = self.settings.get("build", "output_dir") or "."
        if out_dir == ".":
            return source_path.parent
        d = Path(out_dir)
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _print(self, text: str) -> None:
        self.terminal.send_text(text)

    def _on_stdout(self):
        data = self._proc.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self._output_buf.append(data)
        self._print(data)

    def _on_stderr(self):
        data = self._proc.readAllStandardError().data().decode("utf-8", errors="replace")
        self._output_buf.append(data)
        self._print(data)

    def _on_finished(self, exit_code: int, _exit_status):
        output = "".join(self._output_buf)
        if self._current_phase == "assemble":
            self.assemble_finished.emit(exit_code, output)
            if exit_code == 0:
                self._print("\033[1;32m✓ Assembly succeeded.\033[0m\n")
                self.build_status.emit("Assembly succeeded.")
                if self._pending_link_obj:
                    self.link(self._pending_link_obj)
            else:
                self._print(f"\033[1;31m✗ Assembly failed (exit {exit_code}).\033[0m\n")
                self.build_status.emit(f"Assembly failed (exit {exit_code}).")
        elif self._current_phase == "link":
            self.link_finished.emit(exit_code, output)
            if exit_code == 0:
                self._print(f"\033[1;32m✓ Link succeeded → {self._last_binary}\033[0m\n")
                self.build_status.emit("Build succeeded.")
                if self._pending_run:
                    self.run()
            else:
                self._print(f"\033[1;31m✗ Link failed (exit {exit_code}).\033[0m\n")
                self.build_status.emit(f"Link failed (exit {exit_code}).")
        self._current_phase = ""

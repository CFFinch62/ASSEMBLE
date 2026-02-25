# assemble/terminal/pty_process.py - PTY process wrapper

import os
import ptyprocess
from PyQt6.QtCore import QThread, pyqtSignal


class PTYProcess(QThread):
    data_received = pyqtSignal(bytes)
    process_exited = pyqtSignal(int)

    def __init__(self, command=None, parent=None):
        super().__init__(parent)
        self.command = command or ["/bin/bash"]
        self._process = None
        self.running = False

    def start(self):
        # 1. Copy the current environment
        env = os.environ.copy()
        
        # 2. Add the TERM variable so commands like 'clear' work
        env["TERM"] = "xterm-256color" 
        
        # 3. Pass the env dictionary to spawn()
        self._process = ptyprocess.PtyProcess.spawn(self.command, env=env)
        
        self.running = True
        super().start()

    def run(self):
        while self.running:
            try:
                data = self._process.read(1024)
                if data:
                    self.data_received.emit(data)
            except EOFError:
                break
            except Exception:
                break
        self.running = False
        self.process_exited.emit(self._process.exitstatus or 0)

    def write(self, data: bytes):
        if self._process and self.running:
            try:
                self._process.write(data)
            except Exception:
                pass

    def resize(self, rows: int, cols: int):
        if self._process and self.running:
            try:
                self._process.setwinsize(rows, cols)
            except Exception:
                pass

    def terminate_process(self):
        self.running = False
        if self._process:
            try:
                self._process.terminate()
            except Exception:
                pass

    def wait(self, msecs: int = 2000):
        super().wait(msecs)

# assemble/config/settings.py - Persistent settings manager

import json
import os
from pathlib import Path

_DEFAULTS = {
    "theme": "dark",
    "editor": {
        "font_family": "Monospace",
        "font_size": 14,
        "tab_width": 8,          # Traditional assembly convention
        "show_line_numbers": True,
        "default_directory": str(Path.home()),
    },
    "build": {
        "assembler_path": "nasm",
        "assembler_flags": "-f elf64",
        "linker_path": "ld",
        "linker_flags": "",
        "output_dir": ".",
        "syntax_flavor": "intel",  # "intel" (NASM) or "att" (GAS)
    },
    "window": {
        "geometry": "",
        "splitter_state": "",
        "right_splitter_state": "",
    },
    "asm_filter": [".asm", ".s", ".S", ".nasm", ".inc"],
}


class Settings:
    """Load / save IDE settings from ~/.config/assemble/settings.json."""

    def __init__(self):
        config_dir = Path.home() / ".config" / "assemble"
        config_dir.mkdir(parents=True, exist_ok=True)
        self._path = config_dir / "settings.json"
        self._data: dict = {}
        self.load()

    def load(self) -> None:
        if self._path.exists():
            try:
                with open(self._path, encoding="utf-8") as f:
                    loaded = json.load(f)
                self._data = self._merge(_DEFAULTS, loaded)
                return
            except Exception:
                pass
        self._data = json.loads(json.dumps(_DEFAULTS))

    def save(self) -> None:
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception as exc:
            print(f"Warning: could not save settings: {exc}")

    def get(self, *keys):
        node = self._data
        for k in keys:
            if isinstance(node, dict) and k in node:
                node = node[k]
            else:
                return None
        return node

    def set(self, *keys_and_value) -> None:
        *keys, value = keys_and_value
        node = self._data
        for k in keys[:-1]:
            node = node.setdefault(k, {})
        node[keys[-1]] = value

    @staticmethod
    def _merge(defaults: dict, overrides: dict) -> dict:
        result = json.loads(json.dumps(defaults))
        for k, v in overrides.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = Settings._merge(result[k], v)
            else:
                result[k] = v
        return result

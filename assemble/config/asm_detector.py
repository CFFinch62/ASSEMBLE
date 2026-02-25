# assemble/config/asm_detector.py - Detect installed assemblers and linkers

import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class Assembler:
    name: str
    path: str
    version: str = ""
    syntax: str = "intel"        # "intel" or "att"


@dataclass
class Linker:
    name: str
    path: str
    version: str = ""


_KNOWN_ASSEMBLERS = [
    ("NASM (Intel syntax)",   "nasm",  ["--version"], "intel"),
    ("YASM (Intel/AT&T)",     "yasm",  ["--version"], "intel"),
    ("GNU Assembler (AT&T)",  "as",    ["--version"], "att"),
    ("Flat Assembler",        "fasm",  ["-?"],         "intel"),
]

_KNOWN_LINKERS = [
    ("GNU ld",    "ld"),
    ("LLVM lld",  "lld"),
    ("gcc (linker mode)", "gcc"),
]


def _run_version(path: str, args: list[str]) -> str:
    try:
        result = subprocess.run(
            [path] + args,
            capture_output=True, text=True, timeout=3
        )
        out = (result.stdout + result.stderr).strip()
        return out.split("\n")[0][:80] if out else ""
    except Exception:
        return ""


def detect_assemblers() -> list[Assembler]:
    found: list[Assembler] = []
    seen: set[str] = set()
    for name, cmd, vargs, syntax in _KNOWN_ASSEMBLERS:
        path = shutil.which(cmd)
        if path and path not in seen:
            seen.add(path)
            found.append(Assembler(
                name=name,
                path=path,
                version=_run_version(path, vargs),
                syntax=syntax,
            ))
    return found


def detect_linkers() -> list[Linker]:
    found: list[Linker] = []
    seen: set[str] = set()
    for name, cmd in _KNOWN_LINKERS:
        path = shutil.which(cmd)
        if path and path not in seen:
            seen.add(path)
            found.append(Linker(
                name=name,
                path=path,
                version=_run_version(path, ["--version"]),
            ))
    return found


def get_default_assembler() -> Assembler | None:
    assemblers = detect_assemblers()
    return assemblers[0] if assemblers else None


def get_default_linker() -> Linker | None:
    linkers = detect_linkers()
    return linkers[0] if linkers else None


def validate_tool_path(path: str) -> tuple[bool, str]:
    import os
    resolved = shutil.which(path) or (path if os.path.isfile(path) else None)
    if not resolved:
        return False, f"Not found: {path}"
    version = _run_version(resolved, ["--version"])
    return True, version or "version unknown"

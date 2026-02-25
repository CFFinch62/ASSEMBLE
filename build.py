"""
build.py — ASSEMBLE packaging helper
=====================================
Usage:
    python3 build.py
"""

import importlib.util
import os
import pathlib
import platform
import shutil
import sys

APP_NAME    = "ASSEMBLE"
ENTRY_POINT = "assemble/main.py"
SCRIPT_DIR  = pathlib.Path(__file__).parent.resolve()


def _inject_venv_paths() -> None:
    venv_dir = SCRIPT_DIR / "venv"
    if not venv_dir.exists():
        return
    py_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"
    site_pkgs = venv_dir / "lib" / py_ver / "site-packages"
    if site_pkgs.exists() and str(site_pkgs) not in sys.path:
        sys.path.insert(0, str(site_pkgs))
        print(f"[build] Added venv site-packages: {site_pkgs}")


_inject_venv_paths()
import PyInstaller.__main__  # noqa: E402


def _add_data(module_name: str, sep: str) -> list[str]:
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"[build] WARNING: '{module_name}' not found — skipping.")
        return []
    if spec.submodule_search_locations:
        pkg_dir = str(pathlib.Path(spec.origin).parent)
        return ["--add-data", f"{pkg_dir}{sep}{module_name}"]
    return ["--add-data", f"{spec.origin}{sep}."]


def clean():
    for d in ["build", "dist"]:
        if os.path.exists(d):
            shutil.rmtree(d)


def build():
    clean()
    system = platform.system()
    sep    = ";" if system == "Windows" else ":"
    args = [
        "--name",   APP_NAME,
        "--clean",
        "--noconfirm",
        "--windowed",
        "--hidden-import", "PyQt6",
        *_add_data("pyte",       sep),
        *_add_data("ptyprocess", sep),
        "--add-data", f"images{sep}images",
        "--add-data", f"examples{sep}examples",
    ]
    if system == "Darwin":
        args += ["--target-architecture", "universal2"]
    elif system == "Windows":
        args += ["--icon", f"images{sep}assemble_icon.png"]
    args.append(ENTRY_POINT)
    print(f"Building {APP_NAME} for {system}…")
    try:
        PyInstaller.__main__.run(args)
        print(f"\nBuild complete! → dist/{APP_NAME}/")
    except Exception as exc:
        print(f"Build failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    build()

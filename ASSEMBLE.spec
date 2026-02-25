# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['assemble/main.py'],
    pathex=[],
    binaries=[],
    datas=[('/home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/IDES/IDE_Suite 2/ASSEMBLE/venv/lib/python3.13/site-packages/pyte', 'pyte'), ('/home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/IDES/IDE_Suite 2/ASSEMBLE/venv/lib/python3.13/site-packages/ptyprocess', 'ptyprocess'), ('images', 'images'), ('examples', 'examples')],
    hiddenimports=['PyQt6'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ASSEMBLE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ASSEMBLE',
)

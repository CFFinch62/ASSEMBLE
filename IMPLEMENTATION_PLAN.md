# ASSEMBLE Implementation Plan
## ASSEMBLE: Assembly Language Teaching Environment (Assembly IDE)

**Author:** Chuck Finch — Fragillidae Software  
**Reference Design:** FORTE (Fortran IDE) — see `../FORTE`  
**Stack:** Python 3.10+, PyQt6, ptyprocess, pyte  
**Target:** Linux-first (x86-64 primary), portable to macOS/Windows

---

## Architecture Overview

```
ASSEMBLE/
├── assemble/
│   ├── main.py                  # Entry point
│   ├── app.py                   # MainWindow (QMainWindow)
│   ├── browser/
│   │   └── file_browser.py      # Left-panel file tree
│   ├── config/
│   │   ├── asm_detector.py      # Detect nasm/as/yasm assemblers
│   │   ├── settings.py          # JSON settings (~/.config/assemble/)
│   │   ├── settings_dialog.py   # Tabbed preferences dialog
│   │   └── themes.py            # Dark/Light theme dataclasses + QSS
│   ├── editor/
│   │   ├── code_editor.py       # QPlainTextEdit + line number gutter
│   │   ├── find_replace.py      # Find/Replace dialog
│   │   ├── highlighter.py       # Assembly syntax highlighter
│   │   └── tab_widget.py        # Multi-tab editor container
│   └── terminal/
│       ├── pty_process.py       # PTY process wrapper (QThread)
│       └── terminal_widget.py   # pyte-based terminal display widget
├── examples/                    # Sample .asm programs (NASM syntax)
├── images/                      # assemble_icon.png
├── requirements.txt
├── run.sh / setup.sh
└── IMPLEMENTATION_PLAN.md
```

### Key Design Decisions vs FORTE

| Aspect | FORTE | ASSEMBLE |
|--------|-------|----------|
| Language | Fortran (.f90/.f) | Assembly (.asm/.s/.S) |
| Runtime model | Compile → Run | Assemble + Link → Run (two-step) |
| Compiler detector | fortran_detector | asm_detector |
| File extensions | .f90 .f95 .f03 .f .for | .asm .s .S .nasm |
| Tab width default | 3 | 8 (traditional assembly convention) |
| Settings dir | ~/.config/forte | ~/.config/assemble |
| Build system | gfortran (single step) | assemble (nasm) + link (ld/gcc) |
| Case sensitivity | Case-insensitive | Mixed (mnemonics: insensitive; labels: sensitive) |
| Comment style | `!` | `;` (NASM) or `#` (AT&T/GAS) |
| Syntax flavors | N/A | Intel/NASM (default) vs AT&T/GAS |
| Clean artifacts | binary only | binary + .o object file |

---

## Phase Checklist

| Phase | Title | Status |
|-------|-------|--------|
| 1 | Project Bootstrap | ☐ |
| 2 | Config Layer | ☐ |
| 3 | File Browser | ☐ |
| 4 | Editor Layer | ☐ |
| 5 | Terminal Widget | ☐ |
| 6 | Build System | ☐ |
| 7 | Main Window | ☐ |
| 8 | Examples & Polish | ☐ |
| 9 | Packaging | ☐ |

Mark each phase ☑ when all tasks pass acceptance criteria.

---

## Phase 1 — Project Bootstrap

**Goal:** The project runs and shows a placeholder window.

### Tasks

- [ ] 1.1 Verify `assemble/main.py` launches cleanly with `python3 -m assemble.main`
- [ ] 1.2 Confirm `setup.sh` creates venv and installs `requirements.txt` without errors
- [ ] 1.3 Confirm `run.sh` activates venv and launches the app
- [ ] 1.4 Placeholder `MainWindow` appears (title "ASSEMBLE - Assembly Teaching Environment", 1024×768)
- [ ] 1.5 Create `images/` directory; add placeholder `assemble_icon.png`

### Files

| File | Action |
|------|--------|
| `assemble/main.py` | Create — copy FORTE/forte/main.py; rename forte→assemble |
| `assemble/app.py` | Create — stub placeholder window |
| `assemble/__init__.py` | Create — `__version__ = "0.1.0"` |
| `setup.sh` | Create — copy FORTE/setup.sh; rename forte→assemble |
| `run.sh` | Create — copy FORTE/run.sh; rename forte→assemble |
| `requirements.txt` | Create — PyQt6, ptyprocess, pyte, pyinstaller |
| `images/assemble_icon.png` | Create (64×64 PNG placeholder) |

### Acceptance Criteria

- `./run.sh` shows a window titled "ASSEMBLE - Assembly Teaching Environment"
- No import errors in the terminal

---

## Phase 2 — Config Layer

**Goal:** Settings, themes, assembler detection, and linker detection all work correctly.

### Tasks

#### 2a — `assemble/config/settings.py`
- [ ] 2a.1 Copy `FORTE/forte/config/settings.py` as starting point
- [ ] 2a.2 Change config dir to `~/.config/assemble/`
- [ ] 2a.3 Replace "build" section with expanded build section:
  ```python
  "build": {
      "assembler_path": "/usr/bin/nasm",
      "assembler_flags": "-f elf64",
      "linker_path": "/usr/bin/ld",
      "linker_flags": "",
      "output_dir": ".",
      "syntax_flavor": "intel"
  }
  ```
  > `"syntax_flavor"` is `"intel"` (NASM) or `"att"` (GAS/AT&T)
- [ ] 2a.4 Change `"fortran_filter"` → `"asm_filter": True`
- [ ] 2a.5 Set default `"tab_width": 8`
- [ ] 2a.6 Write unit test: settings load/save round-trip, defaults applied

#### 2b — `assemble/config/themes.py`
- [ ] 2b.1 Copy `FORTE/forte/config/themes.py` as starting point
- [ ] 2b.2 Rename/add color fields for Assembly:
  - `mnemonic` (MOV, ADD, SUB, JMP, CALL, RET, etc.) — replaces `keyword`
  - `register` (rax, rbx, rcx, xmm0, etc.)
  - `directive` (section, global, extern, times, db, dw, dd, dq, equ, etc.)
  - `label` (label definitions: `main:`, `loop_start:`)
  - `type_keyword` → repurpose as `size_specifier` (BYTE, WORD, DWORD, QWORD, PTR)
  - `intrinsic` → repurpose as `syscall` (syscall numbers/names)
  - `preprocessor` → keep as `macro` (`%define`, `%macro`, `%include`, `%ifdef`)
- [ ] 2b.3 Dark theme:
  - mnemonic `#89b4fa` (blue — instructions)
  - register `#f38ba8` (red — registers)
  - directive `#f5c2e7` (pink — assembler directives)
  - label `#a6e3a1` (green — labels)
  - size_specifier `#94e2d5` (teal)
  - syscall `#fab387` (peach)
  - macro `#cba6f7` (purple)
- [ ] 2b.4 Light theme: analogous lighter palette
- [ ] 2b.5 Update `apply_theme_to_app()` QSS

#### 2c — `assemble/config/asm_detector.py`
- [ ] 2c.1 Copy `FORTE/forte/config/fortran_detector.py` as starting point
- [ ] 2c.2 Rename: `Assembler` dataclass with `name`, `path`, `version`, `syntax`
- [ ] 2c.3 `KNOWN_ASSEMBLERS` in preference order:
  ```python
  ("nasm",  "NASM (Intel syntax)", ["--version"], "intel", <parser>),
  ("yasm",  "YASM (Intel/AT&T)",   ["--version"], "intel", <parser>),
  ("as",    "GNU Assembler (AT&T)",["--version"], "att",   <parser>),
  ("fasm",  "Flat Assembler",      ["-?"],        "intel", <parser>),
  ```
- [ ] 2c.4 Implement `detect_assemblers()`, `get_default_assembler()`, `is_valid_assembler()`
- [ ] 2c.5 Also detect linker: `ld` (GNU ld), `lld` (LLVM ld) for the linker step
- [ ] 2c.6 Write unit test: mock `shutil.which`, verify detection list

#### 2d — `assemble/config/settings_dialog.py`
- [ ] 2d.1 Copy `FORTE/forte/config/settings_dialog.py` as starting point
- [ ] 2d.2 Rename all "fortran" → "asm", update imports
- [ ] 2d.3 **Editor tab:** font (monospace recommended), font size, tab width (default 8),
           show line numbers
- [ ] 2d.4 **Build tab:**
  - Assembler dropdown (from `asm_detector`), custom path checkbox, assembler flags
  - Linker path field, linker flags field
  - Output directory with Browse button
  - **Syntax Flavor** radio: ◉ Intel/NASM  ○ AT&T/GAS
- [ ] 2d.5 **Appearance tab:** dark/light theme combo

### Acceptance Criteria

- `Settings()` creates `~/.config/assemble/settings.json` with correct defaults
- `get_theme("dark")` returns a `Theme` with all Assembly color fields
- `detect_assemblers()` returns `nasm` if installed
- Preferences dialog opens; all tabs render; settings save/load correctly

---

## Phase 3 — File Browser

**Goal:** Left-panel file tree filters Assembly files; double-click opens in editor.

### Tasks

- [ ] 3.1 Copy `FORTE/forte/browser/file_browser.py` as starting point
- [ ] 3.2 Rename filter class `AsmFileFilterProxy`
- [ ] 3.3 Accepted extensions: `.asm`, `.s`, `.S`, `.nasm`, `.inc` (include files)
- [ ] 3.4 Setting key: `browser → asm_filter`
- [ ] 3.5 Context menu: New File → default name `untitled.asm`
- [ ] 3.6 Emit `file_selected(str)` signal on double-click
- [ ] 3.7 Persist `last_directory` in settings

### Acceptance Criteria

- File tree opens to last-used directory on startup
- Non-Assembly files hidden when filter is enabled
- Double-clicking a `.asm` file emits `file_selected`
- Context menu: New File, New Folder, Rename, Delete all functional

---

## Phase 4 — Editor Layer

**Goal:** Syntax-highlighted, multi-tab code editor with line numbers and find/replace.

### Tasks

#### 4a — `assemble/editor/highlighter.py`
- [ ] 4a.1 Copy `FORTE/forte/editor/highlighter.py` structure as starting point
- [ ] 4a.2 Name class `AsmHighlighter(QSyntaxHighlighter)`
- [ ] 4a.3 Support **two syntax modes**: Intel/NASM and AT&T/GAS.
  Add a `set_syntax(flavor: str)` method that rebuilds rules.
- [ ] 4a.4 **Intel/NASM rule groups** (applied in order):
  1. **Numbers** — decimal `42`, hex `0x1F`/`1Fh`/`$1F`, binary `10110b`, octal `17o`
  2. **Labels** — `^[A-Za-z_][A-Za-z0-9_]*:` → label color (at start of line)
  3. **Size specifiers** — `\b(BYTE|WORD|DWORD|QWORD|OWORD|TWORD|PTR)\b`
     → size_specifier color (case-insensitive)
  4. **Registers (x86-64 Intel)** — `\b(rax|rbx|rcx|rdx|rsi|rdi|rbp|rsp|r8|r9|r10|r11|r12|r13|r14|r15|eax|ebx|ecx|edx|esi|edi|ebp|esp|r8d|r9d|r10d|r11d|r12d|r13d|r14d|r15d|ax|bx|cx|dx|si|di|bp|sp|al|bl|cl|dl|ah|bh|ch|dh|sil|dil|bpl|spl|r8b|r9b|r10b|r11b|r12b|r13b|r14b|r15b|xmm[0-9]+|ymm[0-9]+|zmm[0-9]+|mm[0-7]|st[0-7]|cr[0-9]+|dr[0-9]+|cs|ds|es|fs|gs|ss|rip|eflags|flags)\b`
     → register color (case-insensitive)
  5. **Assembler directives** — `\b(section|segment|global|extern|common|default|bits|use16|use32|use64|org|times|db|dw|dd|dq|dt|do|dy|dz|resb|resw|resd|resq|rest|reso|resy|resz|equ|align|alignb|struc|endstruc|istruc|iend|at|incbin|cpu|float)\b`
     → directive color (case-insensitive)
  6. **Macros/Preprocessor** — `^\s*%(define|macro|endmacro|include|ifdef|ifndef|else|endif|elseifdef|undef|assign|rep|endrep|rotate|exit|unmacro|use|push|pop|error|warning|fatal|line|local)\b`
     → macro color
  7. **Syscall hints** — inline comments with `; sys_` or `SYS_` identifiers → syscall color (optional stretch)
  8. **Mnemonics (Intel x86-64)** — word-boundary, case-insensitive:
     `MOV`, `MOVSX`, `MOVZX`, `MOVSXD`, `MOVSS`, `MOVSD`, `MOVAPS`, `MOVUPS`,
     `PUSH`, `POP`, `LEA`, `XCHG`, `ADD`, `ADC`, `SUB`, `SBB`, `MUL`, `IMUL`,
     `DIV`, `IDIV`, `INC`, `DEC`, `NEG`, `NOT`, `AND`, `OR`, `XOR`,
     `SHL`, `SHR`, `SAL`, `SAR`, `ROL`, `ROR`, `RCL`, `RCR`,
     `CMP`, `TEST`, `JMP`, `JE`, `JNE`, `JZ`, `JNZ`, `JG`, `JL`,
     `JGE`, `JLE`, `JA`, `JB`, `JAE`, `JBE`, `JS`, `JNS`, `JO`, `JNO`,
     `CALL`, `RET`, `RETN`, `RETF`, `LEAVE`, `ENTER`,
     `NOP`, `HLT`, `INT`, `SYSCALL`, `SYSENTER`, `SYSEXIT`, `SYSRET`,
     `CPUID`, `RDTSC`, `RDMSR`, `WRMSR`, `CLFLUSH`, `MFENCE`, `SFENCE`, `LFENCE`,
     `PUSHF`, `POPF`, `PUSHFD`, `POPFD`, `PUSHFQ`, `POPFQ`,
     `LAHF`, `SAHF`, `CLC`, `STC`, `CMC`, `CLD`, `STD`, `CLI`, `STI`,
     `MOVS`, `MOVSB`, `MOVSW`, `MOVSD`, `MOVSQ`,
     `LODS`, `LODSB`, `LODSW`, `LODSD`, `LODSQ`,
     `STOS`, `STOSB`, `STOSW`, `STOSD`, `STOSQ`,
     `CMPS`, `SCAS`, `REP`, `REPE`, `REPNE`, `REPZ`, `REPNZ`,
     `LOOP`, `LOOPE`, `LOOPNE`, `LOOPZ`, `LOOPNZ`,
     `XADD`, `CMPXCHG`, `CMPXCHG8B`, `CMPXCHG16B`,
     `BSF`, `BSR`, `BT`, `BTS`, `BTR`, `BTC`, `BSWAP`,
     `SETCC`, `SETE`, `SETNE`, `SETG`, `SETL`, `SETGE`, `SETLE`,
     `SETA`, `SETB`, `SETAE`, `SETBE`, `SETS`, `SETNS`,
     `IMUL`, `MULSS`, `MULSD`, `ADDSS`, `ADDSD`, `SUBSS`, `SUBSD`,
     `DIVSS`, `DIVSD`, `SQRTSS`, `SQRTSD`, `CVTSI2SS`, `CVTSI2SD`,
     `CVTSS2SI`, `CVTSD2SI`, `CVTSS2SD`, `CVTSD2SS`,
     `MOVD`, `MOVQ`, `PADDB`, `PADDW`, `PADDD`, `PADDQ`,
     `PSUBB`, `PSUBW`, `PSUBD`, `PSUBQ`,
     `PAND`, `POR`, `PXOR`, `PMULLW`,
     `PUNPCKLBW`, `PUNPCKLWD`, `PUNPCKLDQ`, `PUNPCKLQDQ`,
     `PSHUFB`, `PSHUFD`, `PSHUFHW`, `PSHUFLW`,
     `VMOVAPS`, `VADDPS`, `VSUBPS`, `VMULPS`, `VDIVPS`,
     `VPAND`, `VPOR`, `VPXOR`
     → mnemonic color (bold)
  9. **Strings** — `"[^"]*"` and `'[^']*'` → string color
  10. **Comments** — `\;.*` → comment color *(last, overrides everything)*
- [ ] 4a.5 **AT&T/GAS rule groups** (alternate mode via `set_syntax("att")`):
  - Registers: `%rax`, `%rbx`, ... (prefixed with `%`) → register color
  - Immediate values: `$42`, `$0x1F` → number color
  - Directives: `.section`, `.text`, `.data`, `.bss`, `.global`, `.extern`,
    `.byte`, `.word`, `.long`, `.quad`, `.string`, `.ascii`, `.asciz`,
    `.align`, `.space`, `.fill`, `.set`, `.equ`, `.comm` → directive color
  - Mnemonics: same set as Intel but optionally with AT&T size suffixes
    (`b`, `w`, `l`, `q`): `movl`, `movq`, `pushq`, `popq`, etc.
  - Comments: `#.*` → comment color
  - Labels: `^[A-Za-z_.][A-Za-z0-9_.]*:` → label color
  - Strings: `"[^"]*"` → string color
- [ ] 4a.6 Manual test: open a NASM `.asm` file and a GAS `.s` file; confirm both highlight correctly

#### 4b — `assemble/editor/code_editor.py`
- [ ] 4b.1 Copy `FORTE/forte/editor/code_editor.py` as starting point
- [ ] 4b.2 Replace `FortranHighlighter` → `AsmHighlighter`
- [ ] 4b.3 Default tab width 8 from settings
- [ ] 4b.4 Auto-indent on Return (same leading whitespace)
- [ ] 4b.5 Line number gutter: copy verbatim
- [ ] 4b.6 Add `set_syntax(flavor: str)` method forwarding to highlighter
- [ ] 4b.7 Tab key inserts spaces (not `\t`) per the tab_width setting

#### 4c — `assemble/editor/tab_widget.py`
- [ ] 4c.1 Copy `FORTE/forte/editor/tab_widget.py`
- [ ] 4c.2 Import `from assemble.editor.code_editor import CodeEditor`
- [ ] 4c.3 `new_file()`: default tab label `"untitled.asm"`

#### 4d — `assemble/editor/find_replace.py`
- [ ] 4d.1 Copy `FORTE/forte/editor/find_replace.py` verbatim
- [ ] 4d.2 Update imports to use `assemble.*` namespace

### Acceptance Criteria

- Intel/NASM: mnemonics, registers, directives, labels, macros, strings, comments in distinct colors
- AT&T/GAS: `%reg`, `$imm`, `.directive`, `#comment` all correctly colored
- Syntax flavor can be switched; highlighter rebuilds correctly
- Line numbers, multi-tab, auto-indent, Find/Replace all functional

---

## Phase 5 — Terminal Widget

**Goal:** Working PTY terminal (bash shell) in the lower panel.

### Tasks

- [ ] 5.1 Copy `FORTE/forte/terminal/pty_process.py` verbatim → `assemble/terminal/pty_process.py`
- [ ] 5.2 Copy `FORTE/forte/terminal/terminal_widget.py` → `assemble/terminal/terminal_widget.py`
- [ ] 5.3 Default command: system shell (`$SHELL` or `/bin/bash`) — same as FORTE
- [ ] 5.4 Update all imports to `assemble.*` namespace

### Acceptance Criteria

- Terminal panel shows a working shell on startup
- Keyboard input, Ctrl+C, Ctrl+D, Tab completion all work
- Terminal resizes correctly; `clear()` and `restart()` work

---

## Phase 6 — Build System

**Goal:** Save → Assemble → Link → Run workflow with output in the terminal panel.

### Design

```
assemble/build/
    __init__.py
    build_manager.py     # Orchestrates assemble (nasm) + link (ld/gcc) + run
```

Assembly requires **two** steps: assembler produces `.o`, linker produces the binary.
This is fundamentally different from FORTE's single compiler step.

### Tasks

- [ ] 6a.1 Create empty `assemble/build/__init__.py`
- [ ] 6b.1 Copy `FORTE/forte/build/build_manager.py` as starting point
- [ ] 6b.2 Add signals:
  - `assemble_started = pyqtSignal(str)` — emits assembler command
  - `assemble_finished = pyqtSignal(int, str)` — emits (return_code, output)
  - `link_started = pyqtSignal(str)` — emits linker command
  - `link_finished = pyqtSignal(int, str)` — emits (return_code, output)
  - `run_started = pyqtSignal(str)` — emits executable path
- [ ] 6b.3 `assemble(source_path: str) -> None`:
  - Read `assembler_path`, `assembler_flags` from settings
  - `output_obj = output_dir / (stem + '.o')`
  - Run: `[assembler_path] + flags.split() + [source_path, '-o', output_obj]`
    (NASM: `nasm -f elf64 hello.asm -o hello.o`)
  - Use `QProcess`; on finish emit `assemble_finished`
- [ ] 6b.4 `link(obj_path: str) -> None`:
  - Read `linker_path`, `linker_flags` from settings
  - `output_bin = output_dir / stem` (no extension)
  - Run: `[linker_path] + flags.split() + [obj_path, '-o', output_bin]`
    (ld: `ld -o hello hello.o`)
    > Note: For programs using C stdlib, use gcc as linker:
    > `gcc -no-pie -o hello hello.o`
  - Use `QProcess`; on finish emit `link_finished`
- [ ] 6b.5 `assemble_and_link(source_path: str) -> None`: chain assemble → link on success
- [ ] 6b.6 `assemble_link_and_run(source_path: str) -> None`: chain assemble → link → run
- [ ] 6b.7 `run(executable_path: str) -> None`: write to terminal PTY
- [ ] 6b.8 Handle errors: coloured ASSEMBLE message in terminal on non-zero exit
- [ ] 6b.9 `clean()`: delete binary AND `.o` object file
- [ ] 6b.10 Unit test: mock QProcess, verify two-step command construction (deferred)

### Menu items (wired in Phase 7):

| Action | Shortcut | Calls |
|--------|----------|-------|
| Assemble & Run | Ctrl+R | `build_manager.assemble_link_and_run(current_file)` |
| Assemble Only | Ctrl+B | `build_manager.assemble(current_file)` |
| Assemble & Link | Ctrl+Shift+B | `build_manager.assemble_and_link(current_file)` |
| Run Last Build | Ctrl+Shift+R | `build_manager.run(last_binary)` |
| Clean | — | Delete binary + `.o` |

### Acceptance Criteria

- Ctrl+R assembles + links + runs a `.asm` file; output visible in terminal
- Errors from assembler or linker appear with file/line info in terminal
- Ctrl+B only assembles (produces `.o`); Ctrl+Shift+B assembles + links
- `clean()` removes both binary AND `.o` object file

---

## Phase 7 — Main Window

**Goal:** Fully wired `MainWindow` with all panels, menus, toolbar, and status bar.

### Tasks

- [ ] 7.1 Copy `FORTE/forte/app.py` as starting point
- [ ] 7.2 Replace "fortran"/"FORTE" → "asm"/"ASSEMBLE"
- [ ] 7.3 Update all imports to `assemble.*` namespace
- [ ] 7.4 Instantiate `BuildManager`; connect signals to status bar and terminal
- [ ] 7.5 **Layout:** same as FORTE — horizontal + vertical splitters,
  default sizes `[200,800]`/`[500,268]`
- [ ] 7.6 **File Menu:** New/Open/Save/Save As/Exit
  - Open filter: `"Assembly Files (*.asm *.s *.S *.nasm *.inc);;All Files (*)"`
  - Save As filter: `"NASM Assembly (*.asm);;GAS Assembly (*.s);;Include (*.inc);;All Files (*)"`
- [ ] 7.7 **Edit Menu:** Find/Replace (Ctrl+F), Preferences
- [ ] 7.8 **View Menu:** Show File Browser (checkable), Show Terminal (checkable)
- [ ] 7.9 **Build Menu:**
  - Assemble & Run (Ctrl+R)
  - Assemble Only (Ctrl+B)
  - Assemble & Link (Ctrl+Shift+B)
  - Run Last Build (Ctrl+Shift+R)
  - Separator
  - Clean Build Output
  - Separator
  - Clear Terminal Output
  - Restart Terminal
  - Interrupt (Ctrl+Shift+C)
- [ ] 7.10 **Help Menu:** About ASSEMBLE
- [ ] 7.11 **Toolbar:** New, Open, Save | Assemble & Run, Assemble Only
- [ ] 7.12 **Status bar:** "Ready" + cursor position (Ln/Col)
- [ ] 7.13 Wire `file_browser.file_selected` → `open_file_from_browser()`
- [ ] 7.14 Wire `editor_tabs.currentChanged` → `update_cursor_position()`
- [ ] 7.15 When a file is opened, detect syntax flavor from extension:
  `.s` / `.S` → AT&T/GAS; `.asm` / `.nasm` → Intel/NASM; update highlighter
- [ ] 7.16 `apply_theme()` on startup and after preferences save
- [ ] 7.17 `closeEvent()`: save geometry, splitter state, terminate PTY
- [ ] 7.18 **About dialog:** "ASSEMBLE — Assembly Language Teaching Environment"

### Acceptance Criteria

- All menus present and functional; full assemble→link→run workflow works
- Window geometry / splitter positions persist across restarts
- Syntax flavor auto-detected from file extension and applied to highlighter
- Theme applies correctly; About dialog shows correct information

---

## Phase 8 — Examples & Polish

**Goal:** Include beginner-friendly Assembly example programs; fix rough edges.

### Example Programs (`examples/`)
All examples use **NASM Intel syntax** targeting **Linux x86-64**.

- [ ] 8a.1 `hello_world.asm` — syscall write to stdout: `sys_write + sys_exit`
  ```nasm
  section .data
    msg db 'Hello, World!', 10
    len equ $ - msg
  section .text
    global _start
  _start:
    mov rax, 1     ; sys_write
    mov rdi, 1     ; stdout
    mov rsi, msg
    mov rdx, len
    syscall
    mov rax, 60    ; sys_exit
    xor rdi, rdi
    syscall
  ```
- [ ] 8a.2 `variables.asm` — `.data` + `.bss` sections: `db`, `dw`, `dd`, `dq`, `resb`
- [ ] 8a.3 `arithmetic.asm` — `ADD`, `SUB`, `MUL`, `IMUL`, `DIV`, `IDIV`; signed vs unsigned
- [ ] 8a.4 `conditionals.asm` — `CMP` + `Jcc` (JE, JNE, JG, JL, JGE, JLE)
- [ ] 8a.5 `loops.asm` — `LOOP` instruction + manual `DEC/JNZ` loop patterns
- [ ] 8a.6 `procedures.asm` — `CALL`/`RET`, stack frame (`PUSH RBP`/`MOV RBP,RSP`/`POP RBP`)
- [ ] 8a.7 `strings.asm` — `MOVSB`, `REP STOSD`, `SCASB` string operations
- [ ] 8a.8 `syscalls.asm` — Common Linux x86-64 syscall reference:
  sys_read(0), sys_write(1), sys_open(2), sys_close(3), sys_exit(60)

Also include AT&T/GAS equivalents (`.s` files) for Phase 8 stretch:
- [ ] 8a.9 `hello_world_gas.s` — AT&T syntax equivalent of 8a.1

### Polish Tasks
- [ ] 8b.1 Create proper `images/assemble_icon.png` (64×64 and 256×256)
- [ ] 8b.2 Ensure no hardcoded theme colors in `code_editor.py`
- [ ] 8b.3 Add `--version` CLI flag to `main.py`
- [ ] 8b.4 NASM error parsing — parse `file.asm:5: error: ...` to highlight error lines (stretch)
- [ ] 8b.5 Status bar build indicator: "Assembling…" / "Linking…" / "Build succeeded" / "Build failed"
- [ ] 8b.6 Unsaved file check before assemble: auto-save or prompt
- [ ] 8b.7 Include a `linux_syscalls.inc` reference file in `examples/` with common syscall constants

### Acceptance Criteria

- All 8 NASM example files assemble and link cleanly with `nasm -f elf64` + `ld`
- No hardcoded colors; build status visible in status bar (two-phase: Assembling / Linking)

---

## Phase 9 — Packaging

**Goal:** Distributable standalone binary via PyInstaller.

### Tasks

- [ ] 9.1 Create `ASSEMBLE.spec` (reference: `FORTE/FORTE.spec`)
- [ ] 9.2 Include `images/` and `examples/` in datas
- [ ] 9.3 Test `pyinstaller ASSEMBLE.spec` produces a working binary
- [ ] 9.4 Create `build.py` helper script (reference: `FORTE/build.py`)
- [ ] 9.5 Test built binary: window opens, --version works, assets in _internal/
- [ ] 9.6 Bare-machine test (deferred)

### Acceptance Criteria

- `python3 build.py` produces `dist/ASSEMBLE` executable
- Binary runs standalone; all assets accessible

---

## Assembly-Specific Notes

### NASM Invocation (Linux x86-64)
```bash
# Assemble to object file
nasm -f elf64 -o hello.o hello.asm

# Link to executable (bare — no C stdlib)
ld -o hello hello.o

# Link to executable (with C stdlib via gcc)
gcc -no-pie -o hello hello.o

# One-shot via gcc (if using C-compatible entry point 'main')
gcc -no-pie -o hello hello.o -nostartfiles
```

### GAS Invocation (Linux x86-64)
```bash
# Assemble AT&T syntax
as -o hello.o hello.s

# Link
ld -o hello hello.o
```

### NASM Error Format
```
hello.asm:5: error: symbol `xyz' undefined
hello.asm:10: warning: label alone on a line without a colon might be in error
```

### GNU ld Error Format
```
hello.o: in function `_start':
hello.asm:(.text+0x5): undefined reference to `_exit'
```

### Linux x86-64 Syscall Calling Convention
- Syscall number: `rax`
- Arguments: `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9`
- Return value: `rax`
- Use `syscall` instruction

### Two-Step Build Strategy
Students will frequently see BOTH assembler errors AND linker errors.
The status bar should clearly distinguish:
- "Assembling hello.asm…" → "Assembly succeeded" / "Assembly failed (line N)"
- "Linking hello.o…" → "Link succeeded" / "Link failed"

---

## Reference Files (by phase)

| Phase | Primary Reference | Notes |
|-------|------------------|-------|
| 1 | `FORTE/forte/main.py`, `setup.sh`, `run.sh` | Rename forte→assemble |
| 2a | `FORTE/forte/config/settings.py` | asm_filter, tab_width=8; two-part build section |
| 2b | `FORTE/forte/config/themes.py` | New fields: mnemonic, register, directive, label, etc. |
| 2c | `FORTE/forte/config/fortran_detector.py` | Adapt for nasm/as/yasm + ld detection |
| 2d | `FORTE/forte/config/settings_dialog.py` | Add linker fields + syntax flavor radio |
| 3 | `FORTE/forte/browser/file_browser.py` | .asm/.s/.S extensions |
| 4a | `FORTE/forte/editor/highlighter.py` | Structure only; all rules new; two flavor modes |
| 4b–4d | `FORTE/forte/editor/` | Copy; swap import namespaces; add set_syntax forwarding |
| 5 | `FORTE/forte/terminal/` | Copy verbatim |
| 6 | `FORTE/forte/build/build_manager.py` | Major adaptation: two-step assemble+link pipeline |
| 7 | `FORTE/forte/app.py` | Adapt menus; add syntax auto-detection on file open |
| 9 | `FORTE/FORTE.spec`, `FORTE/build.py` | Adapt |

---

## Progress Log

| Date | Phase | Notes |
|------|-------|-------|
| 2026-02-23 | 0 | Implementation plan created (adapted from FORTE) |

---

*ASSEMBLE — Assembly Language Teaching Environment*  
*(c) Fragillidae Software — Chuck Finch*

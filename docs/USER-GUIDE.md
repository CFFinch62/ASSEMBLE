# ASSEMBLE User Guide

Welcome to the **ASSEMBLE — Assembly Language Teaching Environment**. ASSEMBLE is a specialized IDE designed to help students and developers learn and write x86-64 assembly language for Linux.

## Key Features

- **Dual Syntax Support**: Real-time syntax highlighting for both Intel (NASM/YASM) and AT&T (GNU Assembler/GAS) flavors.
- **Two-Step Build Manager**: One-click assembly and linking with integrated error reporting.
- **Dedicated Terminal**: Built-in bash terminal for executing programs and viewing `stdout` output.
- **Auto-Detection**: Automatically detects installed assemblers (`nasm`, `as`, `yasm`, `fasm`) and linkers (`ld`, `gcc`).
- **Memory/Register Highlighting**: Distinct colors for mnemonics, registers, directives, labels, and macros.

---

## 1. Getting Started

### Installation
You must have an assembler and a linker installed on your system.
For Ubuntu/Debian:
```bash
sudo apt install nasm binutils gcc
```

### Initial Configuration
Upon launching ASSEMBLE, navigate to **Edit > Preferences**.
1. **Editor Tab**: Adjust font size and select your preferred tab width (assembly traditional is 8, but you may prefer 4).
2. **Build Tab**:
   - Verify the IDE has detected your assembler (default: `nasm`) and linker (default: `ld`).
   - Choose your preferred **Syntax Flavor** (Intel/NASM vs. AT&T/GAS).
3. **Appearance**: Choose between Dark and Light mode.

---

## 2. The IDE Interface

### Code Editor
The text editor is customized for assembly language:
- **Case awareness**: Highlights mnemonics and registers case-insensitively, while leaving labels case-sensitive.
- **Auto-detection**: If you open a `.s` or `.S` file, the editor automatically switches to AT&T/GAS syntax mode. If you open `.asm` or `.nasm`, it switches to Intel mode.

### File Browser
The left panel displays your project files.
- It automatically filters to show only relevant extensions: `.asm`, `.s`, `.S`, `.nasm`, and `.inc`.
- Right-click in the browser to create new assembly files, folders, or rename/delete files.

### Terminal Panel
The bottom panel runs a real pseudo-terminal (PTY) instance of your system shell (e.g., `/bin/bash`).
- You can interact with it just like a normal terminal.
- Standard shell commands (e.g., `ls`, `cd`, `grep`) work perfectly.
- If a program loops infinitely, click inside the terminal and press **Ctrl+C** (or use **Build > Interrupt**, default shortcut `Ctrl+Shift+C`).
- To copy text from the terminal, highlight it with the mouse and press **Ctrl+C**.

---

## 3. The Build Workflow

Writing assembly natively for Linux requires a two-step process: **Assembling** (source code to object file) and **Linking** (object file to executable binary).

ASSEMBLE handles this through the **Build** menu:

| Action              | Shortcut       | Description                                                                                                      |
| ------------------- | -------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Assemble & Run**  | `Ctrl+R`       | Assembles the code, links the resulting `.o` file, and executes the binary in the terminal.                      |
| **Assemble Only**   | `Ctrl+B`       | Runs only the assembler (e.g., `nasm`) to produce a `.o` file. Useful for finding syntax errors without linking. |
| **Assemble & Link** | `Ctrl+Shift+B` | Assembles and links, producing the final binary, but does not run it.                                            |
| **Run Last Build**  | `Ctrl+Shift+R` | Executes the binary from the last successful link step.                                                          |

### Handling Errors
If there is a syntax error, the **Assemble** step will fail. The terminal will display the exact line number of the error (e.g., `hello.asm:5: error: symbol undefined`).

If the assembly succeeds but you are missing an entry point (like `_start` or `main`), the **Link** step will fail. The status bar at the bottom of the window will always indicate which phase failed.

### Cleaning Output
To delete the `.o` object file and the final binary for the currently open source file, use **Build > Clean Build Output**.

---

## 4. Keyboard Shortcuts

| Shortcut       | Action                            |
| -------------- | --------------------------------- |
| `Ctrl+N`       | New File                          |
| `Ctrl+O`       | Open File                         |
| `Ctrl+S`       | Save File                         |
| `Ctrl+Shift+S` | Save As                           |
| `Ctrl+F`       | Find / Replace                    |
| `Ctrl+R`       | Assemble, Link, and Run           |
| `Ctrl+B`       | Assemble to object file only      |
| `Ctrl+Shift+B` | Assemble and Link                 |
| `Ctrl+Shift+R` | Run last built binary             |
| `Ctrl+Shift+C` | Interrupt Terminal (sends SIGINT) |

---

## 5. Troubleshooting

**"No assembler found" / "No linker found"**
- The IDE could not find `nasm`, `as`, or `ld` in your PATH. Install them using your OS package manager (`apt`, `pacman`, `brew`, `dnf`), then go to Preferences > Build and click **Refresh**.

**"ld: warning: cannot find entry symbol _start"**
- By default, the `ld` linker looks for a label named `_start` to begin execution. Ensure you have exported it:
  ```nasm
  global _start
  _start:
      ...
  ```

**The program crashes with "Segmentation fault"**
- This usually means you tried to access unallocated memory, or you corrupted the stack during a `CALL`/`RET` sequence, or you attempted to execute data. Use a debugger (like `gdb` via the integrated terminal) to find the crash location.

**I get an infinite loop and the terminal is stuck!**
- Click inside the terminal and press `Ctrl+C`. Alternatively, use `Ctrl+Shift+C` from the IDE window, or use the **Build > Interrupt** menu option.

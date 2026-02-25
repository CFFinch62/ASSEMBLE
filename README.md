# ASSEMBLE - Assembly Teaching Environment

ASSEMBLE is a comprehensive, standalone integrated development environment (IDE) specifically designed for learning and writing Assembly language (NASM/GAS). It features a dedicated code editor, an integrated file browser, syntax highlighting, and a built-in terminal.

## Features

- **Code Editor**: Syntax highlighting tailored for NASM and AT&T/GAS flavors.
- **File Browser**: Easily navigate your project files with FABLE-like enhancements (Home, Up, Bookmarks, double-click to navigate).
- **Integrated Terminal**: Built-in Pyte-based terminal for compiling and execution.
- **Build System**: Assemble and Link your projects directly from the IDE.
- **Examples**: Comes with a suite of beginner-friendly assembly examples (e.g. `hello_world.asm`, `loops.asm`, `syscalls.asm`).

## Running the Application

1. Make sure Python 3 is installed.
2. Run `setup.sh` to initialize the virtual environment and install dependencies.
3. Launch the IDE by running `run.sh`.

## Building a Release

Use the provided PyInstaller script to package the application into a standalone executable:
```bash
python3 build.py
```
The executable will be located in the `dist/ASSEMBLE/` directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

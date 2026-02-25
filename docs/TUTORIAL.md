# ASSEMBLE Interactive Tutorial

Welcome to the **ASSEMBLE Interactive Tutorial**! Assembly language is the closest you can get to the bare metal of a computer processor while still writing human-readable instructions.

In this tutorial, we will learn how to write **x86-64 assembly** for Linux using the **NASM** (Intel) syntax.

---

## Lesson 1: Our First Instruction

Assembly isn't like Python or Java; you don't have variables or functions built into the language itself. Instead, you manipulate small, fast storage areas inside the CPU called **Registers**.

Let's load the value `42` into the `rax` register.

1. Open ASSEMBLE.
2. Click **File > New** (or press `Ctrl+N`).
3. Name the file `lesson1.asm`.
4. Type the following:

```nasm
section .text
    global _start

_start:
    mov rax, 42
```

### What's happening?
- `section .text`: This directive tells the assembler "this is where my code goes".
- `global _start`: This tells the linker that `_start` is the entry point of our program.
- `_start:`: This is a **label**. It marks the memory address where execution begins.
- `mov rax, 42`: This is an **instruction**. `mov` means "move" (copy). We are copying the immediate value `42` into the destination register `rax`.

---

## Lesson 2: How to Exit Cleanly

If you were to press `Ctrl+R` (Assemble & Run) on Lesson 1 right now, the program would crash with a "Segmentation fault". Why? Because when the CPU finishes `mov rax, 42`, it blindly continues to the next instruction in memory, which is garbage!

To stop a program properly, we must ask the operating system (Linux) to terminate us. We do this using a **System Call** (syscall). 

Linux expects the syscall number in `rax`, and the first argument in `rdi`.

```nasm
section .text
    global _start

_start:
    ; Do some work
    mov rax, 42

    ; sys_exit(0)
    mov rax, 60     ; 60 is the syscall number for sys_exit
    mov rdi, 0      ; 0 is our exit code (Success)
    syscall         ; Ask the kernel to do it
```

Press **Ctrl+R**. Check the terminal panel at the bottom. It should say `[Shell exited with code 0]`. Congratulations!

---

## Lesson 3: Hello, World (sys_write)

Let's do something visible. We'll use `sys_write` (syscall number 1) to print text to the screen. 
`sys_write` expects:
- `rdi`: File descriptor (1 is standard output)
- `rsi`: Address of the string to print
- `rdx`: Number of bytes to print

To store a string, we introduce `section .data`.

```nasm
section .data
    msg db 'Hello, World!', 10  ; 10 is the ASCII code for newline (\n)

section .text
    global _start

_start:
    ; sys_write(stdout, msg, 14)
    mov rax, 1      ; syscall 1 (sys_write)
    mov rdi, 1      ; fd 1 (stdout)
    mov rsi, msg    ; address of our string
    mov rdx, 14     ; length of our string
    syscall

    ; sys_exit(0)
    mov rax, 60
    xor rdi, rdi    ; xor'ing a register with itself sets it to 0 (faster than mov rdi, 0)
    syscall
```

Press **Ctrl+R**. You should see "Hello, World!" in the terminal.

---

## Lesson 4: Basic Math

In assembly, math is done directly on the registers.

- `add dst, src` (dst = dst + src)
- `sub dst, src` (dst = dst - src)
- `inc dst`      (dst = dst + 1)
- `dec dst`      (dst = dst - 1)

Let's add 5 and 7:

```nasm
section .text
    global _start

_start:
    mov rax, 5      ; rax = 5
    add rax, 7      ; rax = 5 + 7 = 12

    mov rbx, 10
    sub rax, rbx    ; rax = 12 - 10 = 2

    inc rax         ; rax = 3

    mov rax, 60
    xor rdi, rdi
    syscall
```

*Note: Since we aren't printing the result, the best way to verify this works is using a debugger like `gdb` via the ASSEMBLE terminal panel.*

---

## Lesson 5: Jumps and Loops

Code executes top-to-bottom unless you change the Instruction Pointer (`rip`). You do this with jumps.

The `jmp` instruction jumps unconditionally. But conditional jumps allow you to build `if` statements and loops!

Before a conditional jump, you must use `cmp` (compare).

Let's write a loop that runs 5 times:

```nasm
section .text
    global _start

_start:
    mov rcx, 5      ; rcx will be our loop counter

.my_loop:
    ; ... do something 5 times ...

    dec rcx         ; subtract 1 from rcx
    cmp rcx, 0      ; compare rcx to 0
    jne .my_loop    ; Jump if Not Equal

    ; The loop finishes, so we exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## Conclusion

This concludes the accelerated ASSEMBLE tutorial!
For more complex examples covering:
- Multiplication/Division
- Stack and procedures (`CALL` / `RET`)
- String operations (`REP MOVSB`)

Please see the `.asm` files in the `examples/` directory via the ASSEMBLE File Browser.

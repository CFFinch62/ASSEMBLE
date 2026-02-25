# ASSEMBLE x86-64 Language Reference

This reference is for the **NASM (Intel) syntax** targeting **Linux x86-64**.

---

## 1. Registers

The x86-64 architecture has 16 general-purpose registers. Each is 64 bits wide, but you can access lower portions of them.

| 64-bit     | 32-bit       | 16-bit       | 8-bit        | Typical Usage                               |
| ---------- | ------------ | ------------ | ------------ | ------------------------------------------- |
| `rax`      | `eax`        | `ax`         | `al`         | Accumulator, return values                  |
| `rbx`      | `ebx`        | `bx`         | `bl`         | Base register (callee-saved)                |
| `rcx`      | `ecx`        | `cx`         | `cl`         | Counter (loops, shifts)                     |
| `rdx`      | `edx`        | `dx`         | `dl`         | Data (I/O, multiply/divide high bits)       |
| `rsi`      | `esi`        | `si`         | `sil`        | Source Index (strings, 2nd arg)             |
| `rdi`      | `edi`        | `di`         | `dil`        | Destination Index (strings, 1st arg)        |
| `rbp`      | `ebp`        | `bp`         | `bpl`        | Base Pointer (stack frame)                  |
| `rsp`      | `esp`        | `sp`         | `spl`        | Stack Pointer (top of stack)                |
| `r8`-`r15` | `r8d`-`r15d` | `r8w`-`r15w` | `r8b`-`r15b` | General purpose (args 5 & 6 are `r8`, `r9`) |

---

## 2. Memory Sizes & Directives

When dealing with memory, you must often specify the size of the operand, especially if it is ambiguous (e.g., `mov [rax], 0`).

| Name        | Size    | Define (Data) | Reserve (BSS) | Size Specifier        |
| ----------- | ------- | ------------- | ------------- | --------------------- |
| Byte        | 8 bits  | `db`          | `resb`        | `BYTE` / `byte ptr`   |
| Word        | 16 bits | `dw`          | `resw`        | `WORD` / `word ptr`   |
| Double Word | 32 bits | `dd`          | `resd`        | `DWORD` / `dword ptr` |
| Quad Word   | 64 bits | `dq`          | `resq`        | `QWORD` / `qword ptr` |

**Example:**
```nasm
mov byte [rax], 0xFF
mov qword [rbx], 0xDEADBEEF
```

---

## 3. Addressing Modes

Memory is accessed by enclosing a register (or expression) in square brackets `[]`.
The general formula is: `[Base + Index * Scale + Displacement]`

- **Base**: Any 64-bit general-purpose register.
- **Index**: Any 64-bit general-purpose register (except `rsp`).
- **Scale**: 1, 2, 4, or 8 (size of elements).
- **Displacement**: Constant offset.

**Examples:**
```nasm
mov rax, [rbx]              ; Base only
mov rax, [rbx + rsi]        ; Base + Index
mov rax, [rbx + rsi*4]      ; Base + Index*Scale (Array of 32-bit ints)
mov rax, [rbx + rsi*8 + 16] ; Base + Index*Scale + Displacement
mov rax, [rel my_var]       ; RIP-relative addressing (Position Independent Code)
```

---

## 4. Common Instructions

### Data Movement
- `mov dst, src` : Copies `src` to `dst`.
- `lea dst, [mem]` : **Load Effective Address**. Computes the address inside `[]` and stores it in `dst` (does not dereference). Useful for math: `lea rax, [rbx + rcx*2]`.
- `xchg a, b` : Swaps values of `a` and `b`.

### Stack Operations
- `push src` : Decrements `rsp` by 8, then stores `src` at `[rsp]`.
- `pop dst` : Loads `[rsp]` into `dst`, then increments `rsp` by 8.

### Arithmetic
- `add dst, src` : `dst = dst + src`
- `sub dst, src` : `dst = dst - src`
- `inc dst` / `dec dst` : Add 1 / Subtract 1
- `mul reg/mem` : Unsigned multiply. `rdx:rax = rax * operand`
- `imul dst, src` : Signed multiply. `dst = dst * src`
- `div reg/mem` : Unsigned divide. `rdx:rax / operand` -> quotient in `rax`, remainder in `rdx`. **Must zero `rdx` first!** (`xor rdx, rdx`)
- `idiv reg/mem` : Signed divide. Prior to dividing, sign-extend `rax` into `rdx:rax` using the `cqo` instruction.

### Logical
- `and dst, src` : Bitwise AND
- `or dst, src` : Bitwise OR
- `xor dst, src` : Bitwise XOR (often used to clear a register: `xor rax, rax`)
- `not dst` : Bitwise NOT (flip all bits)
- `shl dst, count` / `shr dst, count` : Shift Left / Shift Right (Logical)
- `sal dst, count` / `sar dst, count` : Shift Arithmetic (preserves sign bit)

### Control Flow
- `cmp a, b` : Compares `a` and `b` (performs `a - b` but only updates flags).
- `test a, b` : Performs bitwise `a AND b` and updates flags (often used to check if a register is zero: `test rax, rax`).
- `jmp target` : Unconditional jump.
- **Conditional Jumps (Signed):**
  - `je` (Equal) / `jne` (Not Equal)
  - `jg` (Greater) / `jge` (Greater or Equal)
  - `jl` (Less) / `jle` (Less or Equal)
- **Conditional Jumps (Unsigned):**
  - `ja` (Above) / `jae` (Above or Equal)
  - `jb` (Below) / `jbe` (Below or Equal)
- `loop target` : Decrements `rcx`. If `rcx != 0`, jumps to `target`.

### Subroutines
- `call target` : Pushes return address (`rip`) to stack, jumps to `target`.
- `ret` : Pops address from stack into `rip`.

---

## 5. Linux x86-64 Calling Convention (System V ABI)

When calling C library functions or writing your own ABI-compliant functions:

1. **Arguments** are passed in registers in this order:
   1. `rdi`
   2. `rsi`
   3. `rdx`
   4. `rcx`
   5. `r8`
   6. `r9`
   (Additional arguments pushed to stack right-to-left)
2. **Return value** is placed in `rax`.
3. **Callee-saved** registers: `rbp`, `rbx`, `r12`, `r13`, `r14`, `r15`. If your function uses these, it must push them at the start and pop them at the end.
4. **Caller-saved** registers: `rax`, `rcx`, `rdx`, `rsi`, `rdi`, `r8`, `r9`, `r10`, `r11`. A function you call is free to overwrite these.
5. **Stack Alignment**: The stack pointer `rsp` must be 16-byte aligned *before* making a `call` instruction.

---

## 6. Linux System Calls
Instead of `call`, system calls use the `syscall` instruction.

- Syscall number goes in `rax`.
- Arguments go in `rdi`, `rsi`, `rdx`, `r10`, `r8`, `r9`.
- Return value in `rax`.

### Common Syscalls
| Name        | rax | rdi          | rsi        | rdx   |
| ----------- | --- | ------------ | ---------- | ----- |
| `sys_read`  | 0   | fd           | buffer_ptr | count |
| `sys_write` | 1   | fd           | buffer_ptr | count |
| `sys_open`  | 2   | filename_ptr | flags      | mode  |
| `sys_close` | 3   | fd           | -          | -     |
| `sys_exit`  | 60  | exit_code    | -          | -     |

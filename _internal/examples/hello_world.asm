; hello_world.asm - ASSEMBLE Example 1: Hello, World!
; NASM syntax, Linux x86-64
;
; Build steps (Ctrl+R does this automatically):
;   nasm -f elf64 -o hello_world.o hello_world.asm
;   ld -o hello_world hello_world.o
;   ./hello_world

section .data
    msg     db  'Hello, World!', 10    ; 10 = newline
    msglen  equ $ - msg                ; $ = current position, so len = end - start

section .text
    global _start                      ; entry point for linker

_start:
    ; sys_write(1, msg, msglen)
    mov     rax, 1          ; syscall number: sys_write
    mov     rdi, 1          ; file descriptor: stdout (fd 1)
    mov     rsi, msg        ; pointer to string
    mov     rdx, msglen     ; byte count
    syscall                 ; invoke kernel

    ; sys_exit(0)
    mov     rax, 60         ; syscall number: sys_exit
    xor     rdi, rdi        ; exit code 0  (xor reg,reg = fastest way to zero)
    syscall

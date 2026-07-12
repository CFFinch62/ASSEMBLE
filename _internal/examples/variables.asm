; variables.asm - ASSEMBLE Example 2: Data Types and Memory
; Demonstrates .data (initialized) and .bss (uninitialized) sections.
;
; Build: nasm -f elf64 -o variables.o variables.asm && ld -o variables variables.o

section .data
    ; Byte (8-bit)
    byte_val    db  42                  ; 1 byte,  value 42
    char_val    db  'A'                 ; 1 byte,  ASCII 65
    ; Word (16-bit)
    word_val    dw  1000                ; 2 bytes
    ; Double word (32-bit)
    dword_val   dd  100000              ; 4 bytes
    ; Quad word (64-bit)
    qword_val   dq  1234567890          ; 8 bytes
    ; String
    hello       db  'Hello', 0          ; null-terminated string
    hello_len   equ $ - hello

    ; Numeric literals
    hex_val     db  0xFF                ; hexadecimal
    bin_val     db  11001010b           ; binary
    ; Array of bytes
    arr         db  1, 2, 3, 4, 5      ; 5 bytes
    arr_len     equ $ - arr
    ; Repeated values (times directive)
    ten_zeros   times 10 db 0          ; 10 zero bytes

section .bss
    ; Reserve uninitialized space
    ibuf        resb 8                  ; reserve 8 bytes
    ibuf16      resw 4                  ; reserve 4 words (8 bytes)
    ibuf32      resd 2                  ; reserve 2 dwords (8 bytes)
    ibuf64      resq 1                  ; reserve 1 qword  (8 bytes)

section .text
    global _start

_start:
    ; Load various sizes into registers
    movzx   rax, byte [byte_val]        ; zero-extend byte → rax
    movzx   rax, word [word_val]        ; zero-extend word → rax
    mov     eax, [dword_val]            ; 32-bit load (upper 32 of rax zeroed)
    mov     rax, [qword_val]            ; 64-bit load

    ; Store a value
    mov     qword [ibuf], 0xDEADBEEF   ; store to .bss buffer
    mov     byte [ibuf + 4], 99        ; store single byte offset 4

    ; sys_exit(0)
    mov     rax, 60
    xor     rdi, rdi
    syscall

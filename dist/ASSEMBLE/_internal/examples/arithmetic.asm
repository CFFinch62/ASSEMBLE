; arithmetic.asm - ASSEMBLE Example 3: Arithmetic Operations
; Demonstrates ADD SUB MUL IMUL DIV IDIV and flag usage.
;
; Build: nasm -f elf64 -o arithmetic.o arithmetic.asm && ld -o arithmetic arithmetic.o

section .data
    pos_a   dq  100
    pos_b   dq  25
    neg_a   dq  -7
    neg_b   dq  3

section .bss
    result  resq 1

section .text
    global _start

_start:
    ; ── Basic arithmetic ─────────────────────────────────────────────
    mov     rax, [pos_a]        ; rax = 100
    add     rax, [pos_b]        ; rax = 125  (100 + 25)
    mov     [result], rax

    mov     rax, [pos_a]
    sub     rax, [pos_b]        ; rax = 75   (100 - 25)

    ; ── Unsigned multiply ─────────────────────────────────────────────
    ; MUL: rdx:rax = rax * operand  (unsigned)
    mov     rax, 10
    mov     rbx, 20
    mul     rbx                 ; rdx:rax = 10 * 20 = 200
                                ; rdx = 0 (high 64 bits), rax = 200

    ; ── Signed multiply (IMUL forms) ──────────────────────────────────
    imul    rax, rbx            ; 2-operand: rax = rax * rbx
    imul    rax, rbx, 5        ; 3-operand: rax = rbx * 5

    ; ── Unsigned divide ───────────────────────────────────────────────
    ; DIV: rdx:rax / operand → quotient=rax, remainder=rdx
    mov     rax, 100
    xor     rdx, rdx            ; clear rdx (high bits of dividend)
    mov     rbx, 7
    div     rbx                 ; rax = 14 (quotient), rdx = 2 (remainder)

    ; ── Signed divide (IDIV) ─────────────────────────────────────────
    mov     rax, [neg_a]        ; -7
    cqo                         ; sign-extend rax into rdx:rax
    mov     rbx, [neg_b]        ; 3
    idiv    rbx                 ; rax = -2 (quotient), rdx = -1 (remainder)

    ; ── Increment / Decrement ─────────────────────────────────────────
    mov     rcx, 10
    inc     rcx                 ; rcx = 11
    dec     rcx                 ; rcx = 10

    ; ── Negation ──────────────────────────────────────────────────────
    mov     rax, 42
    neg     rax                 ; rax = -42

    ; ── Shift-based multiply / divide ─────────────────────────────────
    mov     rax, 5
    shl     rax, 3              ; rax = 5 * 8 = 40  (shift left = multiply by 2^n)
    shr     rax, 1              ; rax = 20           (shift right = divide by 2)

    ; sys_exit(0)
    mov     rax, 60
    xor     rdi, rdi
    syscall

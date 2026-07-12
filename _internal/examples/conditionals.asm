; conditionals.asm - ASSEMBLE Example 4: Comparisons and Branches
; Demonstrates CMP + Jcc (conditional jumps) — the core of all control flow.
;
; Build: nasm -f elf64 -o conditionals.o conditionals.asm && ld -o conditionals conditionals.o

section .data
    ; Output messages
    msg_pos db 'Positive', 10, 0
    msg_neg db 'Negative', 10, 0
    msg_zer db 'Zero',     10, 0
    msg_max db 'Max found', 10, 0

section .bss
    max_val resq 1

section .text
    global _start

; Helper: print a null-terminated string at rsi
print_str:
    push    rbp
    mov     rbp, rsp
    ; find length
    mov     rdi, rsi
.len_loop:
    cmp     byte [rdi], 0
    je      .found_len
    inc     rdi
    jmp     .len_loop
.found_len:
    sub     rdi, rsi            ; length in rdi
    mov     rdx, rdi
    mov     rax, 1              ; sys_write
    mov     rdi, 1              ; stdout
    syscall
    pop     rbp
    ret

_start:
    ; ── if/else: classify a number ────────────────────────────────────
    mov     rax, 42             ; change to -5 or 0 to test other branches
    cmp     rax, 0
    jl      .negative
    je      .zero

.positive:
    mov     rsi, msg_pos
    call    print_str
    jmp     .done_classify

.negative:
    mov     rsi, msg_neg
    call    print_str
    jmp     .done_classify

.zero:
    mov     rsi, msg_zer
    call    print_str

.done_classify:

    ; ── Signed comparison table ───────────────────────────────────────
    ; JE  / JZ   — equal / zero flag set
    ; JNE / JNZ  — not equal
    ; JG  / JNLE — greater (signed)
    ; JL  / JNGE — less (signed)
    ; JGE / JNL  — greater or equal (signed)
    ; JLE / JNG  — less or equal (signed)

    ; ── Unsigned comparison table ─────────────────────────────────────
    ; JA  / JNBE — above (unsigned greater)
    ; JB  / JNAE — below (unsigned less)
    ; JAE / JNB  — above or equal
    ; JBE / JNA  — below or equal

    ; ── Max of two values ────────────────────────────────────────────-
    mov     rax, 17
    mov     rbx, 42
    cmp     rax, rbx
    jge     .rax_is_max         ; if rax >= rbx, rax is already max
    mov     rax, rbx            ; else rax = rbx
.rax_is_max:
    mov     [max_val], rax

    mov     rsi, msg_max
    call    print_str

    ; sys_exit(0)
    mov     rax, 60
    xor     rdi, rdi
    syscall

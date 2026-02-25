; loops.asm - ASSEMBLE Example 5: Loop Patterns
; Demonstrates LOOP instruction and manual DEC/JNZ patterns.
;
; Build: nasm -f elf64 -o loops.o loops.asm && ld -o loops loops.o

section .data
    digit_buf   db  '0', 10     ; '0' + newline: we overwrite '0' each iteration
    digit_len   equ 2

section .text
    global _start

; Print digit in rax (0-9) to stdout
print_digit:
    add     rax, '0'            ; convert number → ASCII character
    mov     [digit_buf], al     ; overwrite buffer byte
    mov     rax, 1              ; sys_write
    mov     rdi, 1              ; stdout
    mov     rsi, digit_buf
    mov     rdx, digit_len
    syscall
    ret

_start:
    ; ── Pattern 1: LOOP instruction ───────────────────────────────────
    ; LOOP decrements rcx; jumps if rcx != 0
    ; Count down from 5 to 1
    mov     rcx, 5
.loop1:
    mov     rax, rcx            ; copy counter
    call    print_digit
    loop    .loop1              ; dec rcx; jnz .loop1

    ; ── Pattern 2: DEC / JNZ (more flexible, faster on modern CPUs) ──
    ; Count 5 down to 1
    mov     rcx, 5
.loop2:
    mov     rax, rcx
    call    print_digit
    dec     rcx
    jnz     .loop2              ; jump while rcx != 0

    ; ── Pattern 3: INC / CMP / JL — for-style loop ────────────────────
    ; Print 1 through 5
    mov     rcx, 1
.loop3:
    cmp     rcx, 6
    jge     .loop3_done
    mov     rax, rcx
    call    print_digit
    inc     rcx
    jmp     .loop3
.loop3_done:

    ; ── Pattern 4: while loop ─────────────────────────────────────────
    ; Sum 1 + 2 + ... + 10
    xor     rax, rax            ; accumulator = 0
    mov     rcx, 1
.while_loop:
    cmp     rcx, 11             ; while rcx < 11
    jge     .while_done
    add     rax, rcx
    inc     rcx
    jmp     .while_loop
.while_done:
    ; rax = 55

    ; ── Pattern 5: LOOPE / LOOPNE ─────────────────────────────────────
    ; LOOPE: loop while rcx != 0 AND ZF=1  (loop while equal/zero)
    ; LOOPNE: loop while rcx != 0 AND ZF=0 (loop while not equal)
    ; Useful for scanning arrays with an exit condition.

    ; sys_exit(0)
    mov     rax, 60
    xor     rdi, rdi
    syscall

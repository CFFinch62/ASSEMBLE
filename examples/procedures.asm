; procedures.asm - ASSEMBLE Example 6: Procedures and the Call Stack
; Demonstrates CALL/RET, stack frames, register preservation (callee-saves).
;
; Build: nasm -f elf64 -o procedures.o procedures.asm && ld -o procedures procedures.o
;
; Linux x86-64 System V ABI calling convention:
;   Integer args:    rdi rsi rdx rcx r8 r9 (then stack)
;   Return value:    rax (rdx for 128-bit)
;   Callee-saves:    rbx rbp r12 r13 r14 r15  (must preserve across calls)
;   Caller-saves:    rax rcx rdx rsi rdi r8-r11 (may be clobbered by calls)
;   Stack aligned:   16-byte aligned before CALL instruction

section .data
    newline db 10

section .text
    global _start

; ─────────────────────────────────────────
; add_two(a: rdi, b: rsi) -> rax
; Simple function: no stack frame needed for leaf functions.
; ─────────────────────────────────────────
add_two:
    lea     rax, [rdi + rsi]    ; rax = rdi + rsi (LEA avoids flags modification)
    ret

; ─────────────────────────────────────────
; factorial(n: rdi) -> rax
; Recursive function — needs a proper stack frame.
; ─────────────────────────────────────────
factorial:
    push    rbp                 ; save caller's base pointer
    mov     rbp, rsp            ; set up our frame
    push    rbx                 ; callee-save rbx (we'll use it)

    mov     rbx, rdi            ; save n in rbx

    cmp     rdi, 1
    jle     .base_case          ; if n <= 1, return 1

    ; recursive call: factorial(n-1)
    dec     rdi                 ; rdi = n - 1
    call    factorial           ; rax = factorial(n-1)
    imul    rax, rbx            ; rax = n * factorial(n-1)
    jmp     .done

.base_case:
    mov     rax, 1

.done:
    pop     rbx                 ; restore callee-save
    pop     rbp                 ; restore caller's frame
    ret

; ─────────────────────────────────────────
; print_char(char: rdi)
; Print a single character to stdout.
; ─────────────────────────────────────────
print_char:
    push    rbp
    mov     rbp, rsp
    sub     rsp, 16             ; allocate 16 bytes (keep 16-byte alignment)
    mov     [rsp], dil          ; store byte
    mov     rax, 1              ; sys_write
    mov     rdi, 1              ; stdout
    lea     rsi, [rsp]          ; pointer to our byte
    mov     rdx, 1              ; 1 byte
    syscall
    add     rsp, 16
    pop     rbp
    ret

_start:
    ; Call add_two(10, 32)
    mov     rdi, 10
    mov     rsi, 32
    call    add_two             ; rax = 42

    ; Call factorial(6) → 720
    mov     rdi, 6
    call    factorial           ; rax = 720

    ; Print newline to confirm we ran
    mov     rdi, 10             ; '\n'
    call    print_char

    ; sys_exit(0)
    mov     rax, 60
    xor     rdi, rdi
    syscall

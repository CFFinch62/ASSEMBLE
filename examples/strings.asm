; strings.asm - ASSEMBLE Example 7: String Operations
; Demonstrates MOVSB (copy), STOSB (fill/store), SCASB (scan), REP prefix.
;
; Build: nasm -f elf64 -o strings.o strings.asm && ld -o strings strings.o

section .data
    src     db  'Hello, Assembly!', 0   ; source string
    src_len equ $ - src

section .bss
    dst     resb 32                     ; destination buffer
    result  resb 32

section .text
    global _start

; strlen(ptr: rdi) -> rax
; Count bytes until null terminator.
strlen:
    xor     rax, rax
.loop:
    cmp     byte [rdi + rax], 0
    je      .done
    inc     rax
    jmp     .loop
.done:
    ret

; memcpy using REP MOVSB
; strcopy(dst: rdi, src: rsi, len: rcx)
strcopy:
    push    rbp
    mov     rbp, rsp
    rep movsb                   ; copy rcx bytes from [rsi] to [rdi]
    pop     rbp
    ret

; memset using REP STOSB: fill rdi with al, rcx bytes
memset_zero:
    xor     al, al              ; byte value = 0
    rep stosb                   ; store al at [rdi], dec rcx, repeat
    ret

; Find character (al) in string (rdi), return offset or -1
strchr:
    xor     rcx, rcx
.scan:
    cmp     byte [rdi + rcx], 0
    je      .not_found
    cmp     byte [rdi + rcx], al
    je      .found
    inc     rcx
    jmp     .scan
.found:
    mov     rax, rcx
    ret
.not_found:
    mov     rax, -1
    ret

_start:
    ; ── strlen ────────────────────────────────────────────────────────
    mov     rdi, src
    call    strlen              ; rax = 16

    ; ── strcopy (REP MOVSB) ───────────────────────────────────────────
    mov     rdi, dst
    mov     rsi, src
    mov     rcx, src_len        ; includes null terminator
    call    strcopy

    ; ── Print copied string ───────────────────────────────────────────
    mov     rdi, dst            ; find length
    call    strlen
    mov     rax, 1              ; sys_write
    mov     rdi, 1              ; stdout
    mov     rsi, dst
    mov     rdx, 17             ; 'Hello, Assembly!' + newline
    syscall

    ; ── memset (REP STOSB) ────────────────────────────────────────────
    mov     rdi, result
    mov     rcx, 32
    call    memset_zero

    ; ── SCASB — scan for character 'A' in src ─────────────────────────
    ; SCASB: compare al with [rdi], advance rdi, dec rcx
    mov     rdi, src
    mov     al, 'A'
    mov     rcx, src_len
    repne scasb                 ; scan until al == [rdi] or rcx == 0
    ; After: if ZF=1, found at rdi-1

    ; sys_exit(0)
    mov     rax, 60
    xor     rdi, rdi
    syscall

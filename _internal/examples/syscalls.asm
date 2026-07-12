; syscalls.asm - ASSEMBLE Example 8: Linux x86-64 System Calls
; Common syscalls with full argument breakdown.
; Include linux_syscalls.inc for named constants.
;
; Build: nasm -f elf64 -o syscalls.o syscalls.asm && ld -o syscalls syscalls.o

%include "linux_syscalls.inc"

section .data
    ; sys_write
    msg_w   db  'Hello via sys_write!', 10
    msg_w_l equ $ - msg_w

    ; Filename for open/read demo
    fname   db  '/etc/hostname', 0

    ; Prompt
    msg_ok  db  'OK', 10
    msg_ok_l equ $ - msg_ok

section .bss
    fd      resq 1          ; file descriptor
    buf     resb 64         ; read buffer

section .text
    global _start

_start:
    ; ═══════════════════════════════════════════════
    ; 1. sys_write(fd, buf, count)
    ;    rax=1  rdi=fd  rsi=buf  rdx=count
    ; ═══════════════════════════════════════════════
    mov     rax, SYS_WRITE
    mov     rdi, STDOUT
    mov     rsi, msg_w
    mov     rdx, msg_w_l
    syscall                 ; returns bytes written in rax

    ; ═══════════════════════════════════════════════
    ; 2. sys_open(path, flags, mode)
    ;    rax=2  rdi=path  rsi=flags  rdx=mode
    ;    Flags: O_RDONLY=0, O_WRONLY=1, O_RDWR=2, O_CREAT=0x40
    ; ═══════════════════════════════════════════════
    mov     rax, SYS_OPEN
    mov     rdi, fname      ; path
    xor     rsi, rsi        ; O_RDONLY = 0
    xor     rdx, rdx        ; mode (only matters with O_CREAT)
    syscall
    test    rax, rax
    js      .open_failed    ; check for error (negative = -errno)
    mov     [fd], rax       ; save file descriptor

    ; ═══════════════════════════════════════════════
    ; 3. sys_read(fd, buf, count)
    ;    rax=0  rdi=fd  rsi=buf  rdx=count
    ; ═══════════════════════════════════════════════
    mov     rax, SYS_READ
    mov     rdi, [fd]
    mov     rsi, buf
    mov     rdx, 63
    syscall                 ; rax = bytes read, or negative errno

    ; Write what we read to stdout
    mov     rdx, rax        ; bytes read = count to write
    mov     rax, SYS_WRITE
    mov     rdi, STDOUT
    mov     rsi, buf
    syscall

    ; ═══════════════════════════════════════════════
    ; 4. sys_close(fd)
    ;    rax=3  rdi=fd
    ; ═══════════════════════════════════════════════
    mov     rax, SYS_CLOSE
    mov     rdi, [fd]
    syscall

.open_failed:
    ; ═══════════════════════════════════════════════
    ; 5. sys_exit(code)
    ;    rax=60  rdi=exit_code
    ; ═══════════════════════════════════════════════
    mov     rax, SYS_EXIT
    xor     rdi, rdi        ; exit code 0
    syscall

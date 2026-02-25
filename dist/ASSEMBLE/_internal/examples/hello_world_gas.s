/* hello_world_gas.s - ASSEMBLE Example 9: Hello World (AT&T/GAS syntax)
 * Equivalent of hello_world.asm but in GNU Assembler (AT&T) syntax.
 *
 * Build:
 *   as -o hello_world_gas.o hello_world_gas.s
 *   ld -o hello_world_gas hello_world_gas.o
 *
 * Key AT&T differences from Intel syntax:
 *   - Registers prefixed with %:  %rax  %rdi  %rsi
 *   - Immediates prefixed with $: $1  $60  $0
 *   - Source, Destination order:  mov $1, %rax   (Intel: mov rax, 1)
 *   - Size suffixes on mnemonics: movq (quad), movl (long/dword), movb (byte)
 *   - Memory operands:            (%rsi)  rather than [rsi]
 *   - Directives start with .:    .section  .text  .data  .globl  .byte
 *   - Comments:                   # this is a comment  (or C-style  slash-star)
 */

        .section .data
msg:    .ascii "Hello, World!\n"     # 14 bytes; no null needed for write()
msglen  = . - msg                   # assembler-time constant (GAS syntax)

        .section .text
        .globl _start               # entry point

_start:
        # sys_write(1, msg, msglen)
        movq    $1,         %rax    # syscall number: sys_write
        movq    $1,         %rdi    # fd: stdout
        movq    $msg,       %rsi    # address of string
        movq    $msglen,    %rdx    # byte count
        syscall

        # sys_exit(0)
        movq    $60,        %rax    # syscall number: sys_exit
        xorq    %rdi,       %rdi    # exit code 0
        syscall

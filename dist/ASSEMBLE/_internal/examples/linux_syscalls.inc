; linux_syscalls.inc - Linux x86-64 Syscall Constants (NASM %define)
; Include with: %include "linux_syscalls.inc"
; Syscall convention: rax=number, rdi rsi rdx r10 r8 r9 = args, rax = return

; ── I/O ──────────────────────────────────────────────────────────────
%define SYS_READ        0
%define SYS_WRITE       1
%define SYS_OPEN        2
%define SYS_CLOSE       3
%define SYS_STAT        4
%define SYS_FSTAT       5
%define SYS_LSTAT       6
%define SYS_POLL        7
%define SYS_LSEEK       8
%define SYS_MMAP        9
%define SYS_MPROTECT    10
%define SYS_MUNMAP      11
%define SYS_BRK         12
%define SYS_IOCTL       16
%define SYS_READV       19
%define SYS_WRITEV      20
%define SYS_PIPE        22
%define SYS_DUP         32
%define SYS_DUP2        33

; ── Filesystem ───────────────────────────────────────────────────────
%define SYS_ACCESS      21
%define SYS_MKDIR       83
%define SYS_RMDIR       84
%define SYS_CREAT       85
%define SYS_UNLINK      87
%define SYS_RENAME      82
%define SYS_READLINK    89
%define SYS_GETCWD      79
%define SYS_CHDIR       80
%define SYS_OPENAT      257
%define SYS_MKDIRAT     258
%define SYS_UNLINKAT    263

; ── Process ──────────────────────────────────────────────────────────
%define SYS_EXIT        60
%define SYS_EXIT_GROUP  231
%define SYS_FORK        57
%define SYS_VFORK       58
%define SYS_EXECVE      59
%define SYS_CLONE       56
%define SYS_WAIT4       61
%define SYS_KILL        62
%define SYS_GETPID      39
%define SYS_GETPPID     110
%define SYS_GETTID      186
%define SYS_SCHED_YIELD 24
%define SYS_NANOSLEEP   35

; ── Memory ───────────────────────────────────────────────────────────
%define SYS_MMAP2       192
%define SYS_MREMAP      25
%define SYS_MSYNC       26

; ── Signals ──────────────────────────────────────────────────────────
%define SYS_RT_SIGACTION    13
%define SYS_RT_SIGPROCMASK  14
%define SYS_RT_SIGRETURN    15
%define SYS_PAUSE           34
%define SYS_ALARM           37

; ── Sockets ──────────────────────────────────────────────────────────
%define SYS_SOCKET      41
%define SYS_CONNECT     42
%define SYS_ACCEPT      43
%define SYS_SENDTO      44
%define SYS_RECVFROM    45
%define SYS_BIND        49
%define SYS_LISTEN      50
%define SYS_GETSOCKOPT  55
%define SYS_SETSOCKOPT  54

; ── Time ─────────────────────────────────────────────────────────────
%define SYS_TIME        201
%define SYS_GETTIMEOFDAY 96
%define SYS_CLOCK_GETTIME 228
%define SYS_CLOCK_NANOSLEEP 230

; ── File descriptor constants ─────────────────────────────────────────
%define STDIN           0
%define STDOUT          1
%define STDERR          2

; ── open() flags ─────────────────────────────────────────────────────
%define O_RDONLY        0
%define O_WRONLY        1
%define O_RDWR          2
%define O_CREAT         0x40
%define O_TRUNC         0x200
%define O_APPEND        0x400
%define O_NONBLOCK      0x800

; ── mmap() flags ─────────────────────────────────────────────────────
%define PROT_NONE       0
%define PROT_READ       1
%define PROT_WRITE      2
%define PROT_EXEC       4
%define MAP_SHARED      1
%define MAP_PRIVATE     2
%define MAP_ANON        0x20
%define MAP_ANONYMOUS   0x20

; ── exit() codes ─────────────────────────────────────────────────────
%define EXIT_SUCCESS    0
%define EXIT_FAILURE    1

; ── Signals ──────────────────────────────────────────────────────────
%define SIGHUP      1
%define SIGINT      2
%define SIGQUIT     3
%define SIGILL      4
%define SIGTRAP     5
%define SIGABRT     6
%define SIGFPE      8
%define SIGKILL     9
%define SIGSEGV     11
%define SIGPIPE     13
%define SIGALRM     14
%define SIGTERM     15

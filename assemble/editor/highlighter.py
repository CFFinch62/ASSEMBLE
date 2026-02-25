# assemble/editor/highlighter.py - Assembly syntax highlighter
#
# Supports two syntax flavors:
#   "intel" — NASM/YASM Intel syntax (.asm, .nasm)
#   "att"   — GNU Assembler AT&T syntax (.s, .S)
#
# Call set_syntax("intel") or set_syntax("att") to switch; highlighter rebuilds rules.

import re
from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat
from assemble.config.themes import Theme, DARK_THEME


def _fmt(color: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
    f = QTextCharFormat()
    f.setForeground(QColor(color))
    if bold:
        f.setFontWeight(QFont.Weight.Bold)
    if italic:
        f.setFontItalic(True)
    return f


# ---------------------------------------------------------------------------
# Intel/NASM register names (x86-64)
# ---------------------------------------------------------------------------
_INTEL_REGISTERS = (
    r"rax|rbx|rcx|rdx|rsi|rdi|rbp|rsp|rip|"
    r"r8|r9|r10|r11|r12|r13|r14|r15|"
    r"eax|ebx|ecx|edx|esi|edi|ebp|esp|"
    r"r8d|r9d|r10d|r11d|r12d|r13d|r14d|r15d|"
    r"ax|bx|cx|dx|si|di|bp|sp|"
    r"r8w|r9w|r10w|r11w|r12w|r13w|r14w|r15w|"
    r"al|bl|cl|dl|ah|bh|ch|dh|sil|dil|bpl|spl|"
    r"r8b|r9b|r10b|r11b|r12b|r13b|r14b|r15b|"
    r"xmm[0-9]|xmm1[0-5]|ymm[0-9]|ymm1[0-5]|"
    r"zmm[0-9]|zmm1[0-5]|zmm2[0-9]|zmm3[01]|"
    r"mm[0-7]|st[0-7]|"
    r"cr[0-9]|cr1[0-5]|dr[0-9]|"
    r"cs|ds|es|fs|gs|ss|eflags|flags|rflags"
)

_INTEL_MNEMONICS = (
    r"mov(?:sx|zx|sxd|ss|sd|aps|ups|dqa|dqu|ntdq|ntps|ntpd|q|d)?|"
    r"push(?:f|fd|fq)?|pop(?:f|fd|fq)?|lea|xchg|bswap|"
    r"add(?:ss|sd|ps|pd)?|adc|sub(?:ss|sd|ps|pd)?|sbb|"
    r"mul(?:ss|sd|ps|pd)?|imul|div(?:ss|sd|ps|pd)?|idiv|"
    r"inc|dec|neg|not|and(?:ps|pd)?|or(?:ps|pd)?|xor(?:ps|pd)?|"
    r"shl|shr|sal|sar|rol|ror|rcl|rcr|"
    r"cmp(?:xchg(?:8b|16b)?|ss|sd|ps|pd)?|test|"
    r"jmp|je|jne|jz|jnz|jg|jl|jge|jle|ja|jb|jae|jbe|"
    r"js|jns|jo|jno|jp|jpe|jnp|jpo|jcxz|jecxz|jrcxz|"
    r"call|ret(?:n|f)?|leave|enter|"
    r"nop|hlt|int(?:o)?|into|iret(?:d|q)?|"
    r"syscall|sysenter|sysexit|sysret|"
    r"cpuid|rdtsc|rdtscp|rdmsr|wrmsr|"
    r"clflush|mfence|sfence|lfence|pause|"
    r"lahf|sahf|clc|stc|cmc|cld|std|cli|sti|"
    r"movs(?:b|w|d|q)?|lods(?:b|w|d|q)?|stos(?:b|w|d|q)?|"
    r"scas(?:b|w|d|q)?|cmps(?:b|w|d|q)?|"
    r"rep(?:e|ne|z|nz)?|loop(?:e|ne|z|nz)?|"
    r"xadd|bsf|bsr|bt(?:s|r|c)?|"
    r"set(?:e|ne|z|nz|g|l|ge|le|a|b|ae|be|s|ns|o|no|p|np)|"
    r"push(?:a|ad|aw)?|pop(?:a|ad|aw)?|"
    r"cvtsi2s[sd]|cvts[sd]2si|cvts[sd]2s[sd]|"
    r"sqrts[sd]|"
    r"movd|movq|"
    r"padd[bwdq]|psub[bwdq]|pmull?[wdq]?|"
    r"pand(?:n)?|por|pxor|"
    r"punpckl(?:bw|wd|dq|qdq)|punpckh(?:bw|wd|dq|qdq)|"
    r"pshuf(?:b|d|hw|lw)|"
    r"vmov(?:aps|ups|dqa|dqu)|"
    r"vadd(?:ps|pd|ss|sd)|vsub(?:ps|pd|ss|sd)|"
    r"vmul(?:ps|pd|ss|sd)|vdiv(?:ps|pd|ss|sd)|"
    r"vpand|vpor|vpxor|vpmulld|"
    r"xgetbv|xsetbv|"
    r"lar|lsl|lgdt|sgdt|sidt|lldt|sldt|ltr|str|"
    r"in|out|ins(?:b|w|d)?|outs(?:b|w|d)?|"
    r"xlat(?:b)?|aam|aad|aas|aaa|das|daa|"
    r"bound|arpl|verr|verw|"
    r"clts|invd|wbinvd|invlpg|"
    r"lmsw|smsw|lgs|lfs|lss|"
    r"ud2|prefetch(?:nta|t[012])?|"
    r"emms|femms|"
    r"fld(?:1|z|pi|l2t|l2e|lg2|ln2|cw|env|l|s)?|"
    r"fst(?:p|cw|env|sw)?|fabs|fchs|fsqrt|"
    r"fadd(?:p)?|fsub(?:r?p?)?|fmul(?:p)?|fdiv(?:r?p?)?|"
    r"fcom(?:p{1,2}|i|ip)?|ftst|fxam|"
    r"fsin|fcos|fsincos|fptan|fpatan|f2xm1|fyl2x|fscale|frndint"
)

_INTEL_DIRECTIVES = (
    r"section|segment|global|extern|common|default|bits|use16|use32|use64|org|"
    r"times|db|dw|dd|dq|dt|do|dy|dz|"
    r"resb|resw|resd|resq|rest|reso|resy|resz|"
    r"equ|align|alignb|"
    r"struc|endstruc|istruc|iend|at|"
    r"incbin|cpu|float"
)

_INTEL_MACROS = (
    r"%define|%undef|%assign|%macro|%endmacro|%unmacro|%include|"
    r"%ifdef|%ifndef|%elifdef|%elifndef|%else|%endif|"
    r"%if|%elif|%elifidn|%elifidni|%elifid|%elifnum|%elifstr|%eliftoken|"
    r"%rep|%endrep|%rotate|%exit|%error|%warning|%fatal|%line|%local|"
    r"%push|%pop|%use|%repl"
)

_INTEL_SIZE_SPECS = r"BYTE|WORD|DWORD|QWORD|OWORD|TWORD|YWORD|ZWORD|PTR"

# AT&T register prefix (already has %) — no word boundary needed
_ATT_REGISTERS = r"%(?:rax|rbx|rcx|rdx|rsi|rdi|rbp|rsp|rip|eax|ebx|ecx|edx|" \
                 r"esi|edi|ebp|esp|ax|bx|cx|dx|si|di|bp|sp|" \
                 r"al|bl|cl|dl|ah|bh|ch|dh|" \
                 r"r[89]|r1[0-5]|r[89][dwb]|r1[0-5][dwb]|" \
                 r"mm[0-7]|xmm[0-9]|xmm1[0-5]|ymm[0-9]|ymm1[0-5]|" \
                 r"cs|ds|es|fs|gs|ss)"

_ATT_DIRECTIVES = (
    r"\.(?:section|text|data|bss|rodata|global|globl|extern|"
    r"byte|word|long|quad|short|single|double|"
    r"string|ascii|asciz|space|fill|zero|comm|"
    r"align|balign|p2align|skip|"
    r"equ|set|equiv|"
    r"type|size|ident|"
    r"include|incbin|"
    r"if|ifdef|ifndef|else|endif|"
    r"macro|endm|irp|irpc|rept|endr|"
    r"lcomm|weak|hidden|protected|"
    r"code16|code32|code64|"
    r"intel_syntax|att_syntax)"
)

_ATT_MNEMONICS = (
    r"mov[bwlq]?|movs(?:b|bl|bq|bw|l|lq|w|wl|wq)?|movz(?:b|bl|bq|bw|l|lq|w|wq)?|"
    r"push[lq]?|pop[lq]?|lea[lq]?|"
    r"add[bwlq]?|adc[bwlq]?|sub[bwlq]?|sbb[bwlq]?|"
    r"mul[bwlq]?|imul[bwlq]?|div[bwlq]?|idiv[bwlq]?|"
    r"inc[bwlq]?|dec[bwlq]?|neg[bwlq]?|not[bwlq]?|"
    r"and[bwlq]?|or[bwlq]?|xor[bwlq]?|"
    r"shl[bwlq]?|shr[bwlq]?|sal[bwlq]?|sar[bwlq]?|"
    r"cmp[bwlq]?|test[bwlq]?|"
    r"jmp|je|jne|jz|jnz|jg|jl|jge|jle|ja|jb|jae|jbe|"
    r"js|jns|jo|jno|jp|jpe|jnp|jpo|"
    r"call[lq]?|ret[lq]?|leave|enter|nop|hlt|"
    r"syscall|sysenter|sysexit|sysret|"
    r"int|into|iret[lq]?|"
    r"cpuid|rdtsc|rdtscp|"
    r"clflush|mfence|sfence|lfence|pause|"
    r"rep(?:e|ne|z|nz)?|"
    r"movs[bwlq]?|lods[bwlq]?|stos[bwlq]?|scas[bwlq]?|cmps[bwlq]?|"
    r"xchg[bwlq]?|bswap|"
    r"set(?:e|ne|z|nz|g|l|ge|le|a|b|ae|be|s|ns|o|no|p|np)[bwlq]?"
)


def _build_intel_rules(theme: Theme) -> list[tuple[re.Pattern, QTextCharFormat]]:
    """Rules for Intel/NASM syntax. Order matters."""
    return [
        # Block comment /* ... */ handled separately
        # Strings
        (re.compile(r'"[^"\n]*"'), _fmt(theme.string)),
        (re.compile(r"'[^'\n]*'"), _fmt(theme.string)),
        # Line comment (must come after strings)
        (re.compile(r";[^\n]*"),   _fmt(theme.comment, italic=True)),
        # Numbers: hex 0x1F / 1Fh / $1F, binary 1010b, octal 7o, decimal
        (re.compile(r"\b0[xX][0-9a-fA-F]+\b"),              _fmt(theme.number)),
        (re.compile(r"\b[0-9][0-9a-fA-F]*[hH]\b"),          _fmt(theme.number)),
        (re.compile(r"\$[0-9a-fA-F]+\b"),                    _fmt(theme.number)),
        (re.compile(r"\b[01]+[bB]\b"),                       _fmt(theme.number)),
        (re.compile(r"\b[0-7]+[oOqQ]\b"),                    _fmt(theme.number)),
        (re.compile(r"\b\d+\.?\d*(?:[eE][+-]?\d+)?\b"),      _fmt(theme.number)),
        # NASM macros / preprocessor (must start at beginning of significant content)
        (re.compile(r"(?:" + _INTEL_MACROS + r")\b", re.IGNORECASE), _fmt(theme.macro)),
        # Labels: identifier followed by colon at start of line (possibly indented)
        (re.compile(r"^\s*\.?[A-Za-z_][A-Za-z0-9_]*:", re.MULTILINE), _fmt(theme.label, bold=True)),
        # Size specifiers
        (re.compile(r"\b(?:" + _INTEL_SIZE_SPECS + r")\b", re.IGNORECASE), _fmt(theme.size_specifier)),
        # Registers (case-insensitive in Intel syntax)
        (re.compile(r"\b(?:" + _INTEL_REGISTERS + r")\b", re.IGNORECASE), _fmt(theme.register)),
        # Directives
        (re.compile(r"\b(?:" + _INTEL_DIRECTIVES + r")\b", re.IGNORECASE), _fmt(theme.directive)),
        # Mnemonics (bold)
        (re.compile(r"\b(?:" + _INTEL_MNEMONICS + r")\b", re.IGNORECASE), _fmt(theme.mnemonic, bold=True)),
    ]


def _build_att_rules(theme: Theme) -> list[tuple[re.Pattern, QTextCharFormat]]:
    """Rules for AT&T/GAS syntax. Order matters."""
    return [
        # Strings
        (re.compile(r'"[^"\n]*"'), _fmt(theme.string)),
        # Line comment
        (re.compile(r"#[^\n]*"),   _fmt(theme.comment, italic=True)),
        # Numbers: $42 $0x1F hex plain
        (re.compile(r"\$0[xX][0-9a-fA-F]+"), _fmt(theme.number)),
        (re.compile(r"\$-?\d+"),              _fmt(theme.number)),
        (re.compile(r"\b0[xX][0-9a-fA-F]+\b"),_fmt(theme.number)),
        (re.compile(r"\b\d+\.?\d*(?:[eE][+-]?\d+)?\b"), _fmt(theme.number)),
        # Labels
        (re.compile(r"^\s*\.?[A-Za-z_][A-Za-z0-9_.]*:", re.MULTILINE), _fmt(theme.label, bold=True)),
        # Registers (%rax etc.) — no word boundary needed as % is prefix
        (re.compile(_ATT_REGISTERS, re.IGNORECASE), _fmt(theme.register)),
        # Directives (.section .text etc.)
        (re.compile(_ATT_DIRECTIVES + r"\b", re.IGNORECASE), _fmt(theme.directive)),
        # Mnemonics
        (re.compile(r"\b(?:" + _ATT_MNEMONICS + r")\b", re.IGNORECASE), _fmt(theme.mnemonic, bold=True)),
    ]


class AsmHighlighter(QSyntaxHighlighter):
    def __init__(self, document, theme: Theme = DARK_THEME, syntax: str = "intel"):
        super().__init__(document)
        self.theme = theme
        self._syntax = syntax
        self._rules: list[tuple[re.Pattern, QTextCharFormat]] = []
        self._comment_fmt = _fmt(theme.comment, italic=True)
        self._build_rules()

    def set_syntax(self, syntax: str):
        """Switch between 'intel' and 'att' syntax modes."""
        if syntax != self._syntax:
            self._syntax = syntax
            self._build_rules()
            self.rehighlight()

    def set_theme(self, theme: Theme):
        self.theme = theme
        self._comment_fmt = _fmt(theme.comment, italic=True)
        self._build_rules()
        self.rehighlight()

    def _build_rules(self):
        if self._syntax == "att":
            self._rules = _build_att_rules(self.theme)
        else:
            self._rules = _build_intel_rules(self.theme)

    def highlightBlock(self, text: str):
        for pattern, fmt in self._rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)

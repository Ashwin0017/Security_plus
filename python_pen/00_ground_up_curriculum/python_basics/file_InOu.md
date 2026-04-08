How open() works under the hood
	with open("/usr/share/wordlists/rockyou.txt", "r", encoding="latin-1") as f:
When Python executes open(), it makes the open() syscall to the Linux kernel. The kernel:

Looks up the path in the filesystem (ext4, in Kali's case)
Checks read permissions against your UID (User ID)
Allocates a file descriptor — an integer handle (e.g., fd=5) in the kernel's per-process file descriptor table
Returns control to Python, which wraps that file descriptor in a Python file object

The file object Python gives you is a TextIOWrapper — a buffered text stream layered over a BufferedReader, layered over a FileIO object. That stack looks like this:
your code
    ↓
TextIOWrapper     — decodes bytes → str using the specified encoding
    ↓
BufferedReader    — maintains an in-memory read buffer (default 8 KB)
    ↓
FileIO            — makes read() syscalls to the kernel
    ↓
kernel VFS        — Virtual Filesystem layer
    ↓
ext4 driver       — reads from disk in 4 KB blocks
The BufferedReader layer is important: even when you ask for one line, the kernel is actually reading 8 KB at a time from disk into a buffer. This is because disk I/O (Input/Output) has high latency — fetching 8 KB in one syscall is far cheaper than making hundreds of syscalls for individual lines. Python then serves lines to your code from that buffer, only issuing another read() syscall when the buffer is exhausted.

Why encoding="latin-1" — the full explanation
The ASCII problem first:
ASCII uses 7 bits, encoding characters 0–127. Every standard English letter, digit, and common symbol fits here. The byte 0x41 = 'A', 0x61 = 'a', etc.
What happens above 127:
Bytes 0x80–0xFF (128–255) are outside ASCII. Different encoding standards define these differently:

UTF-8: Variable-width encoding. Bytes above 127 are part of multi-byte sequences. A byte like 0x80 alone is invalid UTF-8 — it signals the continuation of a multi-byte sequence, but if there's no leading byte before it, Python raises UnicodeDecodeError.
latin-1 (ISO 8859-1): Fixed-width, single-byte encoding. Every byte value 0x00–0xFF maps directly and unambiguously to a Unicode code point of the same value. Byte 0x80 → Unicode U+0080. No multi-byte sequences. No invalid byte sequences. It is impossible to get a decode error with latin-1.

Why rockyou.txt triggers this:
rockyou.txt was compiled from real leaked passwords. Real users create passwords with accented characters (é, ñ, ü), Cyrillic, and other non-ASCII characters. Those were stored as raw bytes in whatever encoding the original system used — often Windows-1252 or latin-1. The file is not consistently encoded. It contains a mix of encodings across different lines.
Attempting UTF-8:
pythonwith open("rockyou.txt", "r", encoding="utf-8") as f:
    for line in f:
        ...
# Raises: UnicodeDecodeError: 'utf-8' codec can't decode byte 0x?? in position ?
With latin-1, byte 0xE9 (which in latin-1 is é) is decoded to Unicode U+00E9 (é) — not necessarily what the original user typed, but it decodes without error. For password cracking, you're going to hash the string anyway, so what matters is that the byte sequence is faithfully preserved and hashable, not that the Unicode interpretation is semantically correct.
The errors= parameter as an alternative:
# Instead of latin-1, you can keep UTF-8 and instruct Python how to handle bad bytes:
with open("rockyou.txt", "r", encoding="utf-8", errors="ignore") as f:
    ...  # Silently drops bytes that aren't valid UTF-8

with open("rockyou.txt", "r", encoding="utf-8", errors="replace") as f:
    ...  # Substitutes ? for invalid bytes
Both are worse than latin-1 for wordlists. errors="ignore" silently truncates passwords containing non-ASCII bytes — you'd miss valid candidates. errors="replace" corrupts the password with ? characters — same problem. latin-1 is the correct choice because it preserves every byte.

Line-by-line iteration vs readlines() — the memory model
What readlines() does:
f.readlines()
# Returns: ['password\n', '123456\n', 'password1\n', ...]
readlines() reads the entire file from disk into RAM (Random Access Memory) in one operation, then splits on newlines and returns a list of strings. For rockyou.txt at 133 MB, this allocates roughly 133 MB of RAM immediately, plus the overhead of the list object itself and each individual string object (each Python str has ~50 bytes of object overhead regardless of content). Total memory cost: ~200–250 MB.
This is the memory profile over time:
Memory
  ^
250MB|          ████████████████████████████
     |         █                            █
     |        █                              █
  0MB|_______█________________________________█___→ Time
              load                          script ends
Everything allocated at once, held until the script finishes or you explicitly del the list.

What line-by-line iteration does:
for line in f:
    word = line.strip()
When you iterate a file object directly, Python calls the file object's __next__() method on each loop iteration. Internally this does:

Check the BufferedReader's 8 KB in-memory buffer
If the buffer contains a newline, return everything up to and including it as a string
If the buffer is exhausted, issue one read(8192) syscall to refill it from disk, then return the next line

At any point in time, your script holds one line in memory plus the 8 KB buffer. For rockyou.txt with ~14 million lines, you process all 14 million passwords while never using more than ~8 KB + one line's worth of memory.
Memory profile:
Memory
  ^
 8KB|  ████████████████████████████████████
     |
     |
  0MB|__████████████████████████████████████→ Time
      constant throughout execution

Why this is a generator (technically: an iterator)
A generator produces values on demand, one at a time, without pre-computing the full sequence. Python file objects implement the iterator protocol: they have __iter__() and __next__() methods. When you write for line in f, Python calls f.__iter__() (returns f itself), then calls f.__next__() on each iteration until StopIteration is raised at end-of-file.
This is different from a generator function (using yield), but the consumption pattern from your code's perspective is identical: one value at a time, on demand.
You can see this distinction explicitly:
# File object IS an iterator — no intermediate list created
for line in f:           # calls f.__next__() each iteration
    process(line)

# readlines() breaks the lazy evaluation — forces full materialisation
lines = f.readlines()    # entire file read NOW, stored in list
for line in lines:       # iterates the list, file already fully loaded
    process(line)

What line.strip() actually removes
word = line.strip()
strip() removes leading and trailing whitespace, where whitespace includes:

\n — LF (Line Feed), Unix line ending
\r\n — CRLF (Carriage Return Line Feed), Windows line ending — strip() removes both characters
\r — CR (Carriage Return) alone, old Mac line ending
  — spaces, \t tabs

Why this matters for hashing: if you don't strip and the wordlist uses CRLF endings, your candidate password is "password\r" not "password". The MD5 of "password\r" is completely different from the MD5 of "password". You'd never get a match even if the password is in your wordlist.
pythonimport hashlib

hashlib.md5(b"password").hexdigest()    # 5f4dcc3b5aa765d61d8327deb882cf99
hashlib.md5(b"password\r").hexdigest() # completely different hash — missed match

The if word: guard
if word:
    # attempt something
After strip(), a blank line in the wordlist becomes an empty string "". In Python, an empty string is falsy — bool("") == False. So if word: skips empty strings without an explicit len(word) == 0 check.
Why blank lines exist in wordlists: some wordlists have trailing newlines at the end of the file, or blank separator lines between sections. Without this guard, you'd attempt an authentication or hash comparison with an empty string — wasting a network round trip or a hash computation, and potentially logging a suspicious empty-string login attempt on the target system.

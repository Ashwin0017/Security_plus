What an exception actually is at the Python level
When Python encounters an error condition, it constructs an exception object — an instance of some exception class — and raises it. Raising means Python:

Stops executing the current code path immediately
Walks back up the call stack frame by frame, looking for a matching except clause
If it finds one, transfers control there
If it reaches the top of the call stack without finding one, prints the traceback and terminates the process

The exception object carries three things: the exception class (its type), a message string, and a traceback object recording where it was raised.

The exception class hierarchy — why order matters
Python exceptions are organised in an inheritance tree. This is the relevant subtree for socket programming:
BaseException
└── Exception
    └── OSError  (also aliased as IOError, EnvironmentError)
        ├── socket.timeout       (subclass of OSError since Python 3.3)
        ├── socket.gaierror      (subclass of OSError)
        ├── ConnectionRefusedError  (subclass of OSError)
        ├── ConnectionResetError
        ├── BrokenPipeError
        └── TimeoutError         (same as socket.timeout in Python 3.3+)
When Python evaluates except SomeClass:, it checks whether the raised exception is an instance of SomeClass or any of its subclasses. This is the same isinstance() check used everywhere in Python.
This means if you write:
except OSError:
    print("OS error")
except socket.timeout:
    print("timed out")
And a socket.timeout is raised — Python checks the first clause: isinstance(socket.timeout_instance, OSError) → True, because socket.timeout is a subclass of OSError. The first handler matches and runs. The second handler is never reached. The socket.timeout clause is now dead code.
The correct order — specific before general:
except socket.timeout:          # most specific first
    print("timed out")
except socket.gaierror:         # also specific
    print("DNS failed")
except ConnectionRefusedError:  # specific
    print("port closed")
except OSError as e:            # general catch-all for remaining OS errors
    print(f"OS error: {e}")
Python evaluates except clauses top to bottom and executes the first match only. Once a clause matches, the rest are skipped entirely.

connect() vs connect_ex() — two different error models
These two methods connect to a remote host but handle failure completely differently.
connect() — raises exceptions on failure:
 s.connect((host, port))
# If port is closed  → raises ConnectionRefusedError
# If host unreachable → raises OSError
# If timeout        → raises socket.timeout
connect_ex() — returns an errno integer on failure:
 result = s.connect_ex((host, port))
# If success         → returns 0
# If port is closed  → returns 111 (ECONNREFUSED on Linux)
# If timeout         → returns 110 (ETIMEDOUT on Linux)
# If no route        → returns 113 (EHOSTUNREACH on Linux)
The errno values come directly from the Linux kernel. They are defined in /usr/include/asm-generic/errno.h and /usr/include/asm-generic/errno-base.h. You can inspect them in Python:
pythonimport errno
print(errno.ECONNREFUSED)  # 111
print(errno.ETIMEDOUT)     # 110
print(errno.EHOSTUNREACH)  # 113
print(errno.ENETUNREACH)   # 101

# Full mapping of code → name:
print(errno.errorcode[111])  # 'ECONNREFUSED'
When to use which:
Use connect_ex() in a port scanner because a refused connection is an expected, normal outcome — it means the port is closed. Using connect() would force you to catch ConnectionRefusedError as an exception on every closed port, which is semantically wrong (it's not an error in the context of scanning — it's information). connect_ex() treats both open and closed ports as normal return values and only raises exceptions for genuinely abnormal conditions (DNS failure, interface down, etc.).
Use connect() in an SSH brute-forcer or HTTP client because a refused connection there is genuinely unexpected — if port 22 refuses you, something is wrong with your target selection, not your password.

The except ... as e syntax
 except socket.gaierror as e:
    print(f"DNS resolution failed for {host}: {e}")
The as e clause binds the exception object to the name e within the handler block. The exception object has:

str(e) or f"{e}" — human-readable message, what you print
e.args — tuple of raw arguments passed to the exception constructor
e.errno — for OSError subclasses, the integer errno code
e.strerror — for OSError subclasses, the string description of that errno
e.__class__.__name__ — the exception class name as a string

 except OSError as e:
    print(e.errno)     # e.g., 111
    print(e.strerror)  # e.g., 'Connection refused'
    print(e.args)      # e.g., (111, 'Connection refused')
After the except block exits, e is deleted from the local namespace. This is intentional — exception objects hold references to stack frames, and keeping them alive would cause memory leaks via reference cycles. If you need the exception object after the handler, assign it explicitly:
 except OSError as e:
    saved = e  # survives the block

finally — the guaranteed cleanup clause
 finally:
    s.close()
The finally block executes unconditionally: whether the try block succeeded, whether an exception was raised and caught, whether an exception was raised and not caught, and even if the try block contains a return or sys.exit() statement.
The execution paths:
try block succeeds
→ finally runs
→ code after try/except continues

try block raises, except clause matches
→ except handler runs
→ finally runs
→ code after try/except continues

try block raises, NO except clause matches
→ finally runs
→ exception propagates up the call stack (NOT silenced)

try block contains return
→ finally runs BEFORE the function actually returns
→ then function returns
The critical pentest implication: if connect_ex() times out and raises socket.timeout, and you don't have an except socket.timeout clause, the exception will propagate — but finally still runs first, so s.close() still executes. You don't leak file descriptors even in unhandled exception paths.
Why s.close() in finally matters for pentesting specifically:
Each socket consumes a file descriptor. Linux imposes a per-process limit on open file descriptors — check yours with:
bashulimit -n  # typically 1024 or 4096
A port scanner without s.close() that hits an exception mid-scan will accumulate open sockets until it hits the file descriptor limit, then start raising OSError: [Errno 24] Too many open files on every subsequent socket.socket() call. Your scan silently stops working. Using finally: s.close() means every socket is closed regardless of outcome, keeping your file descriptor count at 1 throughout the entire scan.
The context manager (with socket.socket() as s:) does this automatically — its __exit__ method calls s.close(). The finally pattern is the equivalent for cases where you can't use with.

socket.gaierror and sys.exit(1) — why exit here specifically
 except socket.gaierror as e:
    print(f"DNS resolution failed for {host}: {e}")
    sys.exit(1)
socket.gaierror is raised by getaddrinfo() — the function the kernel calls to resolve a hostname to an IP address. If this fails, it means one of:

The hostname doesn't exist in DNS (Domain Name System)
No network connectivity at all
DNS server unreachable

In either case, every subsequent connection attempt in your script will fail with the same error. There is no point catching it per-attempt and continuing the loop — you'd just print the same error 10,000 times while burning through your wordlist achieving nothing.
sys.exit(1) here is deliberate early termination — a fast-fail on a condition that makes the entire script's purpose impossible. The exit code 1 signals failure to any calling shell or wrapper script.
Contrast this with ConnectionRefusedError in a port scanner — a refused connection on port 23 tells you port 23 is closed, but port 24 might still be open. You catch it, record the result, and continue the loop. That is not a fast-fail condition.

Putting the full pattern together as a decision framework
When designing exception handling for any pentest script, ask these three questions for each failure mode:
QuestionAnswer determinesIs this failure expected as a normal outcome?Use return codes (connect_ex) or catch and continueIs this failure fatal to the script's purpose?Catch and sys.exit(1)Is this failure transient and worth retrying?Catch, sleep, retry with a counter
Applied to an SSH brute-forcer:
 def attempt_login(host, port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, port=port, username=username,
                       password=password, timeout=3)
        return True                          # success — stop the loop

    except paramiko.AuthenticationException:
        return False                         # expected — wrong password, continue loop

    except socket.timeout:
        return False                         # transient — treat as failure, continue

    except paramiko.SSHException as e:
        print(f"[!] Protocol error: {e}")
        return False                         # abnormal but non-fatal, continue

    except socket.gaierror as e:
        print(f"[!] DNS failure: {e}")
        sys.exit(1)                          # fatal — entire script is pointless

    finally:
        client.close()                       # always runs
Each exception class maps to a distinct decision. That mapping — not the syntax — is what exception handling architecture means.


????. if the script runs into an exception does it try again with different host and port or does it completely stop running the script?12:31 PMDepends entirely on where the exception is caught — inside the loop or outside it.

Exception caught INSIDE the loop → continues
 def scan_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            result = s.connect_ex((host, port))
            return result == 0
        except socket.timeout:
            return False  # caught here — function returns, loop continues

 def scan_range(host, start, end):
    for port in range(start, end + 1):
        if scan_port(host, port):  # exception handled inside here
            print(f"[+] {port} open")
        # loop keeps going regardless
scan_port() catches the exception internally and returns False. The calling loop in scan_range() never sees the exception — it just gets False back and moves to the next port. The loop never stops.

Exception caught OUTSIDE the loop → stops everything
 def scan_range(host, start, end):
    try:
        for port in range(start, end + 1):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((host, port))
            # exception raised here ↑ propagates OUT of the loop
    except socket.timeout:
        print("timed out")
        # loop is dead — execution continues AFTER the try block
        # no more ports scanned
The try wraps the entire loop. When an exception fires on port 45 (for example), Python exits the loop entirely to reach the except clause. Ports 46 onward are never scanned.

Exception not caught at all → script terminates
 def scan_range(host, start, end):
    for port in range(start, end + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((host, port))
        # if connect_ex raises socket.gaierror here with no except anywhere
        # Python unwinds the entire call stack and prints a traceback
        # script process exits
No handler anywhere → Python prints the traceback and the process dies.

The rule
The loop only survives an exception if the exception is caught at a scope that is inside the loop — either within the loop body itself, or inside a function called by the loop.
If the except clause is at the same level as or outside the for statement, the loop is already dead by the time the handler runs.
This is exactly why the scaffold pattern separates scan_port() from scan_range() — exception handling lives in scan_port(), so the loop in scan_range() is structurally insulated from every individual port's failure modes.

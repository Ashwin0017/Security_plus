'''

connect() vs connect_ex() — hands-on comparison

'''
import socket

host = "localhost"

print("=== connect() — raises on failure ===")
# Port 1 is almost certainly closed
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    s.connect((host, 1))
    print("connected")
except ConnectionRefusedError:
    print("ConnectionRefusedError raised — port closed")
finally:
    s.close()

print()
print("=== connect_ex() — returns errno on failure ===")
ports = [22, 80, 1, 443, 2]
for port in ports:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        result = s.connect_ex((host, port))
        if result == 0:
            print(f"  Port {port}: OPEN (returned 0)")
        else:
            print(f"  Port {port}: closed/filtered (errno {result})")

'''
Run this. Notice connect_ex() never raises — it returns the errno integer for every outcome. For a port scanner this is exactly what you want: both "open" and "closed" are normal results,
not exceptional conditions.
'''
'''
settimeout() — why it's not optional
'''
import time

host = "192.0.2.1"  # RFC 5737 documentation address — guaranteed to be unreachable
port = 80

print("=== Without timeout — blocks indefinitely ===")
print("(interrupting after 3 seconds with Ctrl+C to demonstrate)")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
start = time.time()
try:
    s.connect((host, port))  # blocks here with no timeout set
except KeyboardInterrupt:
    elapsed = time.time() - start
    print(f"Interrupted after {elapsed:.1f}s — would block forever")
except OSError as e:
    elapsed = time.time() - start
    print(f"OS gave up after {elapsed:.1f}s: {e}")
finally:
    s.close()

print()
print("=== With settimeout(2) — returns after 2 seconds ===")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
start = time.time()
try:
    s.connect((host, port))
except socket.timeout:
    elapsed = time.time() - start
    print(f"socket.timeout raised after {elapsed:.1f}s — moved on")
finally:
    s.close()
'''

Without settimeout(), your scanner hangs on every filtered port until the OS TCP retransmission timer expires — typically 2 minutes.
With settimeout(1), you wait at most 1 second. The difference between a scan that takes 3 days and one that takes 18 hours for a full 65535-port range.
'''

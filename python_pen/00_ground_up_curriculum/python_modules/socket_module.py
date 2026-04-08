'''
A socket is a communication endpoint. Think of it like a telephone — before you can talk, you need to pick up the phone (create the socket),
 dial a number (connect to host:port), then speak and listen (send/recv). When done, you hang up (close).

'''
import socket

# Step 1: Create the socket — "pick up the phone"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Step 2: Connect — "dial the number"
s.connect(("example.com", 80))

# Step 3: Send data — "speak"
s.sendall(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")

# Step 4: Receive response — "listen"
data = s.recv(4096)
print(data[:100])

# Step 5: Close — "hang up"
s.close()

'''
What AF_INET and SOCK_STREAM actually mean
These are constants that tell the kernel what kind of socket to create.

'''
# AF = Address Family — what addressing scheme to use
print(socket.AF_INET)   # 2  — IPv4 addresses (e.g., 192.168.1.1)
print(socket.AF_INET6)  # 10 — IPv6 addresses (e.g., fe80::1)

# SOCK_STREAM = TCP — connection-oriented, reliable, ordered
# SOCK_DGRAM  = UDP — connectionless, fire-and-forget
print(socket.SOCK_STREAM)  # 1
print(socket.SOCK_DGRAM)  #2
'''
TCP guarantees delivery and order. If you send packets A, B, C — the receiver gets A, B, C in that order, or the connection errors out. The kernel handles retransmission automatically.
UDP sends and forgets. If packet B gets lost, it's gone. The receiver might get A, C. No retransmission. 
Used for DNS queries, VoIP, games — anything where speed matters more than guaranteed delivery.
For pentesting: use SOCK_STREAM (TCP) for port scanning, banner grabbing, brute-forcing. Use SOCK_DGRAM (UDP) for UDP port scanning or DNS queries.

What happens inside the kernel when you call socket.socket()
Your Python code          Kernel space
─────────────────         ────────────────────────────────
socket.socket()     →     socket() syscall
                          ↓
                          Allocates file descriptor (integer, e.g. fd=5)
                          Creates socket struct in kernel memory
                          Adds fd=5 to your process's file descriptor table
                          Returns fd=5 to Python
                          ↓
Python wraps fd=5 in a socket object and returns it to you




'''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(s.fileno())   # prints the actual integer fd — e.g., 3 or 4 or 5
s.close()
print(s.fileno())   # prints -1 — fd released back to kernel




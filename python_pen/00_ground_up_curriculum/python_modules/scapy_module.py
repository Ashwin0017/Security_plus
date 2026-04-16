'''
All previous modules use the kernel's TCP/IP stack. You ask the kernel to connect somewhere, 
and it handles the packet construction, IP headers, TCP headers, and checksums.
Scapy bypasses all of that — you construct packets field by field and inject them directly onto the network.
'''

from scapy.all import IP, TCP, sr1


# Build a packet manually:
# IP layer  → destination address
# TCP layer → destination port, SYN flag
packet = IP(dst="192.168.0.10") / TCP(dport=80, flags="S")

# Send it and wait for one response
response = sr1(packet, timeout=2, verbose=False)

if response:
    print(f"Got response: {response.summary()}")
    if response[TCP].flags == "SA":  # SYN-ACK
        print("Port 80 is OPEN")
    elif response[TCP].flags == "RA":  # RST-ACK
        print("Port 80 is CLOSED")
else:
    print(f"no response :{response}")



'''
This is a SYN scan — the same technique Nmap uses by default. 
The kernel's TCP stack would never let you send a bare SYN without completing the handshake.
Scapy bypasses the kernel stack entirely with raw sockets.
'''
'''
The / operator — layer stacking explained
'''

from scapy.all import Ether, IP, TCP, UDP, ICMP, Raw

# / is NOT division — it's Scapy's layer composition operator
# Each layer wraps the next, exactly as real protocols work

# Layer 2 / Layer 3 / Layer 4 / Layer 7
packet = Ether() / IP(dst="192.168.128.1") / TCP(dport=80) / Raw(b"GET / HTTP/1.1\r\n")

# Inspect each layer
packet.show()   # prints every field of every layer with values

# Access specific layers by type
print(packet[Ether].dst)    # destination MAC
print(packet[IP].dst)       # destination IP
print(packet[TCP].dport)    # destination port

# Scapy fills in sensible defaults:
# Ether: src MAC = your interface MAC, dst MAC = gateway MAC
# IP: src = your IP, ttl = 64, checksum = auto-computed
# TCP: src port = random, seq = random, checksum = auto-computed

'''
ARP host discovery — why it works when ICMP ping doesn't
'''

from scapy.all import ARP, Ether, srp
# Must run as root — raw socket required

def arp_scan(network):
    """
    network: string like "192.168.1.0/24"
    Returns list of (ip, mac) tuples for live hosts
    """
    # Ether broadcast + ARP request — "who has each IP in the range?"
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network)

    # srp = send/receive at Layer 2
    # srp1 = send/receive, return only first response
    # sr  = send/receive at Layer 3
    answered, unanswered = srp(packet, timeout=2, verbose=False)

    print(f"[*] Sent {len(answered) + len(unanswered)} ARP requests")
    print(f"[*] {len(unanswered)} hosts did not respond")
    print(f"[*] {len(answered)} hosts responded\n")

    live_hosts = []
    for sent, received in answered:
        ip  = received.psrc   # psrc = protocol source = sender's IP
        mac = received.hwsrc  # hwsrc = hardware source = sender's MAC
        print(f"[+] {ip:20s} {mac}")
        live_hosts.append((ip, mac))

    return live_hosts

arp_scan("192.168.0.46/24")
# Run on your local network (replace with your actual subnet)
# hosts = arp_scan("192.168.1.0/24")

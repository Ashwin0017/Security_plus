import sys

# If you run: python3 scan.py 192.168.1.1 80
# sys.argv = ['scan.py', '192.168.1.1', '80']

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)  # Exit with code 1 = failure

host = sys.argv[1]
port = int(sys.argv[2])  # argv values are always strings; cast explicitly

print(host,port)


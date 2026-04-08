import argparse

parser = argparse.ArgumentParser(description="TCP Port Scanner")
parser.add_argument("host", help="Target IP or hostname")
parser.add_argument("-p", "--port", type=int, default=80, help="Target port")
parser.add_argument("-t", "--timeout", type=float, default=1.0)
args = parser.parse_args()

# Access as: args.host, args.port, args.timeout


print(args.host, args.port, args.timeout)

'''
What argparse.ArgumentParser() actually does
pythonparser = argparse.ArgumentParser(description="TCP Port Scanner")
This instantiates an ArgumentParser object. Internally, it initialises several data structures:

A list to hold registered argument definitions
A namespace object that will eventually hold parsed values
Default handlers for --help and --version

The description string only appears in the auto-generated --help output. It has no functional effect on parsing.

Positional vs Optional arguments
pythonparser.add_argument("host", ...)        # Positional
parser.add_argument("-p", "--port", ...) # Optional


Positional argument ("host"):
No - or -- prefix
Mandatory by default — argparse raises an error if it's missing
Consumed from sys.argv by position, left to right
The string "host" becomes the attribute name on the args namespace → args.host

Optional argument ("-p", "--port"):

-p = short form (single dash, single character)
--port = long form (double dash, full word)
Not mandatory by default — if absent, the default value is used
The long form --port determines the attribute name → args.port (argparse strips the -- and converts - to _ for multi-word flags like --target-port → args.target_port)


What type=int and type=float actually do
pythonparser.add_argument("-p", "--port", type=int, default=80)
parser.add_argument("-t", "--timeout", type=float, default=1.0)
sys.argv is always a list of strings — every value from the terminal arrives as str. The type parameter tells argparse to call that callable on the raw string before storing it.
Internally argparse does exactly this:
pythonraw_value = "8080"          # what came from sys.argv
converted = int(raw_value)  # type=int means argparse calls int() on it
# args.port = 8080          # stored as int, not str
If conversion fails — e.g., you pass --port abc — argparse catches the ValueError from int("abc") and prints a clean error message then exits, before your code ever runs:
error: argument -p/--port: invalid int value: 'abc'
Without type=int, args.port would be the string "8080". Passing that to socket.connect((host, port)) would raise TypeError because connect() requires an integer port — and the error would be confusing because it would appear inside your socket code, not at argument parsing time.

What default=80 does
If -p is not supplied on the command line at all, args.port is set to 80. The default value bypasses the type conversion — you specify it already in the correct type. If you wrote default="80" with type=int, argparse would not run int() on the default — it stores it as-is. So always match the default's type to the type parameter.

What parse_args() does step by step
pythonargs = parser.parse_args()

Reads sys.argv[1:] (everything after the script name)
Iterates through the token list, matching each token against registered argument definitions
For positional arguments: consumes tokens left to right
For optional arguments: looks for -p or --port, then consumes the next token as its value
Applies type conversion to each consumed value
Applies default for any optional argument not present in sys.argv
Stores everything in an argparse.Namespace object and returns it

The Namespace object is nothing special — it's essentially a plain object where argparse sets attributes dynamically:
python# What args looks like after parsing "192.168.1.1 -p 443 -t 2.5"
args.host    = "192.168.1.1"   # str — no type= specified, stays as str
args.port    = 443             # int — type=int applied
args.timeout = 2.5             # float — type=float applied

How --help is auto-generated
Argparse registers --help / -h by default. When you run python3 tcp_port_scanner.py --help, argparse intercepts that flag, constructs the help string from all your add_argument() calls, prints it, and calls sys.exit(0). Your script body never executes. This is the output for the example above:
usage: tcp_port_scanner.py [-h] [-p PORT] [-t TIMEOUT] host

TCP Port Scanner

positional arguments:
  host                  Target IP or hostname

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Target port
  -t TIMEOUT, --timeout TIMEOUT

Putting it together — what a complete invocation looks like
bashpython3 tcp_port_scanner.py 192.168.1.1 -p 443 -t 2.5
sys.argv = ['tcp_port_scanner.py', '192.168.1.1', '-p', '443', '-t', '2.5']
                                    ↑ positional    ↑ flag  ↑ val  ↑ flag ↑ val

args.host    → "192.168.1.1"
args.port    → 443    (int)
args.timeout → 2.5    (float)
bashpython3 tcp_port_scanner.py 192.168.1.1
# -p and -t not supplied → defaults kick in

args.host    → "192.168.1.1"
args.port    → 80     (default)
args.timeout → 1.0    (default)
bashpython3 tcp_port_scanner.py
# host not supplied → argparse exits with error before args = parser.parse_args() returns

error: the following arguments are required: host
That last case is the key advantage of argparse over manual sys.argv indexing — the validation, type conversion, and error messaging all happen before your script logic runs, so your functions always receive correctly typed, validated inputs.

'''

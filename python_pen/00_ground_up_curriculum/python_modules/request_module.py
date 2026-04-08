'''
requests is socket wrapped in many layers of convenience. Instead of manually formatting HTTP bytes, you call a function and get a structured response object back.
'''
import requests

# This single line does: DNS resolution, TCP connect, 
# HTTP request formatting, send, receive, response parsing
r = requests.get("http://example.com", timeout=3)

print(r.status_code)        # 200
print(r.headers["Server"])  # server software
print(r.text[:200])         # response body as string


'''
The abstraction stack — what actually happens
Every requests.get() call traverses this stack:
requests.get("http://example.com")
    ↓
requests.Session.request()        — builds Request object
    ↓
urllib3.PoolManager.urlopen()     — manages connection pool
    ↓
urllib3.HTTPConnectionPool        — reuses TCP connections
    ↓
http.client.HTTPConnection        — formats raw HTTP/1.1 bytes
    ↓
socket.makefile() / socket.send() — writes bytes to kernel TCP buffer
    ↓
[network]
    ↓
socket.recv()                     — reads bytes from kernel TCP buffer
    ↓
http.client parses status + headers
    ↓
requests.Response object returned to you
'''

'''
You can see the raw bytes requests is sending by using a debug proxy or by dropping down to http.client directly:

'''
'''
import http.client

# Enable debug output — shows raw bytes sent and received
http.client.HTTPConnection.debuglevel = 1

import requests
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

r = requests.get("http://example.com", timeout=3)
#Run this and you'll see the exact bytes going over the wire — the raw HTTP request and response.
'''

'''
status_code, headers, text, content — the distinction matters
'''
import requests

r = requests.get("http://example.com", timeout=3, allow_redirects=False)

# status_code — integer, not string
print(type(r.status_code))    # <class 'int'>
print(r.status_code)          # 200, 301, 403, 404, 500...
print(r.status_code == 200)   # True — compare as int, not "200"

# headers — case-insensitive dict
print(type(r.headers))           # requests.structures.CaseInsensitiveDict
print(r.headers["server"])       # works
print(r.headers["Server"])       # also works — case-insensitive
print(r.headers.get("X-Powered-By", "not present"))  # safe access

# text vs content — critical difference
print(type(r.text))     # <class 'str'>   — decoded Unicode
print(type(r.content))  # <class 'bytes'> — raw bytes

# When to use content instead of text:
# Downloading a file (image, binary, zip) — use r.content
# Reading HTML/JSON — use r.text


'''
allow_redirects=False — why this matters for enumeration
'''
import requests

# With redirects followed (default)
r = requests.get("http://example.com/login", timeout=3, allow_redirects=True)
print(f"Final URL    : {r.url}")         # may be completely different URL
print(f"Status code  : {r.status_code}") # 200 from wherever it landed

print()

# With redirects disabled
r = requests.get("http://example.com/admin", timeout=3, allow_redirects=False)
print(f"Original URL : {r.url}")
print(f"Status code  : {r.status_code}") # 301 or 302 — the redirect itself
print(f"Redirect to  : {r.headers.get('Location', 'no redirect')}")

'''
In directory brute-forcing, if /admin returns 302 → /login, you want to know that /admin exists and requires auth — which is a finding. 
With allow_redirects=True, you just see a 200 from /login and think nothing is there. The redirect itself is the signal.
'''
'''
requests.Session() — authenticated requests
'''
import requests

# Without Session — each request is independent, no cookie persistence
r1 = requests.post("http://httpbin.org/cookies/set/sessionid/abc123")
r2 = requests.get("http://httpbin.org/cookies")
print("Without session:", r2.json())  # empty — cookie not carried over

print()

# With Session — cookies persist automatically across requests
session = requests.Session()
r1 = session.get("http://httpbin.org/cookies/set/sessionid/abc123")
r2 = session.get("http://httpbin.org/cookies")
print("With session:", r2.json())  # sessionid=abc123 is present
print("Stored cookies:", dict(session.cookies))

'''
In a pentest workflow: session.post("/login", data={...}) — the server sets a session cookie in the Set-Cookie response header. 
The Session object stores it automatically. Every subsequent session.get() sends that cookie back. You stay authenticated without manually tracking and injecting cookie headers.
'''


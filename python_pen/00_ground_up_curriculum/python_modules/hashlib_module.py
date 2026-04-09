'''
A hash function takes input of any size and produces a fixed-size output (the digest). The same input always produces the same output. 
Changing even one character of input produces a completely different output.
'''
import hashlib

print(hashlib.md5(b"password").hexdigest())   # 5f4dcc3b5aa765d61d8327deb882cf99
print(hashlib.md5(b"Password").hexdigest())   # dc647eb65e6711e155375218212b3964
print(hashlib.md5(b"password1").hexdigest())  # 7c6a180b36896a0a8c02787eeafb0e4c
# One character difference → completely different hash

'''
The hash object state machine
hashlib works as a state machine. You can feed data in chunks and finalise at the end:
'''
import hashlib

# All three of these produce identical output:

# Method 1: one-liner
d1 = hashlib.md5(b"hello world").hexdigest()

# Method 2: create then update
h = hashlib.md5()
h.update(b"hello world")
d2 = h.hexdigest()

# Method 3: update in chunks — same as feeding the data piece by piece
h = hashlib.md5()
h.update(b"hello")
h.update(b" ")
h.update(b"world")
d3 = h.hexdigest()

print(d1 == d2 == d3)  # True — all identical

# This chunk-feeding behaviour matters when hashing large files
# You read 8KB at a time and update() the hash, never loading the full file

'''
hexdigest() vs digest()
'''
import hashlib

h = hashlib.md5(b"password")

raw    = h.digest()     # bytes object — raw binary digest
hexstr = h.hexdigest()  # str object — hex-encoded digest

print(type(raw))     # <class 'bytes'>
print(type(hexstr))  # <class 'str'>
print(raw)           # b'_M\xcc;Z\xa7e\xd6\x1d\x83\'\xde\xb8\x82\xcf\x99'
print(hexstr)        # 5f4dcc3b5aa765d61d8327deb882cf99

# In a cracker: compare against a stored hash string
target = "5f4dcc3b5aa765d61d8327deb882cf99"
candidate = "password"
if hashlib.md5(candidate.encode()).hexdigest() == target:
    print(f"[+] Cracked: {candidate}")

'''
Use hexdigest() when comparing against hash strings stored as hex (which is how they appear in database dumps, /etc/shadow, and CTF challenges). 
Use digest() when working with binary protocols or HMAC (Hash-based Message Authentication Code) constructions.
'''

'''
All available hashes
'''


import hashlib

word = b"password"

# See everything available on your system
print(hashlib.algorithms_available)   # includes OpenSSL-provided algorithms
print(hashlib.algorithms_guaranteed)  # guaranteed on every Python installation

# Common ones you'll encounter in pentesting:
print(f"MD5    : {hashlib.md5(word).hexdigest()}")
print(f"SHA1   : {hashlib.sha1(word).hexdigest()}")
print(f"SHA256 : {hashlib.sha256(word).hexdigest()}")
print(f"SHA512 : {hashlib.sha512(word).hexdigest()}")

# Identify which algorithm produced a hash by its length:
# MD5    → 32 hex chars (128 bits)
# SHA1   → 40 hex chars (160 bits)
# SHA256 → 64 hex chars (256 bits)
# SHA512 → 128 hex chars (512 bits)

hashes = {
    "5f4dcc3b5aa765d61d8327deb882cf99": "MD5",
    "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8": "SHA1",
}
for h, algo in hashes.items():
    print(f"Length {len(h)} chars → {algo}")










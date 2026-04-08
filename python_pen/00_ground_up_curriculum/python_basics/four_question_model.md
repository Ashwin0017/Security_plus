1.1. Every pentester needs to ask four questions.

	1. What protocol or OS primitive am I interacting with?
A pentest script always interacts with something real. A TCP socket, an HTTP request response cycle, an SSH handshake, Address resolution broadcast, a file system pathway or a process memory space. Identify this first because the protocol defines the data that is sent. And what format it expects and what a valid response looks like.
		a. Example - brute force SSH --> the primitive is the SSH protocol, which means you are establishing a TCP connection to port 22, completing a cryptographic key exchange, then attempting an authentication handshake.
	2. What is the minimal input/output contract?
Strip everything away except what the script needs to produce what.
	3. What can fail and at which layer of the OSI model?
		a. Network layer: host unreachable, connection refused, timeout
		b. Application layer: authentication rejected, banner mismatch, protocol error
		c. Script layer : file not found, wrong encoding, list exhausted.
	4. What is the performance constraint?
Is this task serial(one attempt at a time), parallelisable(multiple simultaneous attempts) or rate limited by the target? This determines whether to use a simple loop, python's threading module, or a controlled sleep/delay mechanism.
	



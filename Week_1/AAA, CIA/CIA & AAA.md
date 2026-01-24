**Confidentiality**: Ensures that only authorized individuals have access to information and resources, preventing unauthorized disclosure.

&nbsp;	Encryption is a way to provide confidentiality. Access controls is another. Two factor authentication

**Integrity**: Protects information from unauthorized changes, ensuring that data remains accurate and trustworthy.

&nbsp;	Hashing, Digital signatures, Certificates and Non repudiation are some of the ways to ensure integrity.

**Availability**: Ensures that authorized individuals can access information and systems when needed, preventing disruptions like denial of service attacks.

&nbsp;	Redundancy( services that are always available), Fault tolerance and patching all security holes are a way to ensure availability.



Security Objectives : CIA





**Non - Repudiation :**  Proof of integrity and proof of origin.



proof of integrity is done through hash confirmation. 









**Identification**: The individual makes a claim about their identity without presenting proof.

**Authentication**: The individual proves their identity, such as showing a driver's license.

**Authorization**: The system checks if the individual is allowed to access the resource.

**AAA Process**: Authentication, Authorization, and Accounting are crucial for tracking and managing access.

**Digital** **Application**: In digital systems, identification is often done with usernames, authentication with passwords, and authorization with access control lists.

**Accounting :** Track of all the activity.



**Identification** (pre-step)

Before “AAA” really starts, a user first claims an identity (usually by typing a username or selecting an account). This is not proof—it's just saying “I am alex,” which is why identification must be followed by authentication.

​



**Authentication** (1st A)

Authentication is the step where you prove you are who you claimed to be, commonly with a password plus other factors (MFA) if required. In the VPN example, your username/password is submitted to the VPN concentrator, which then asks a central AAA server if those credentials match a valid user record. If the AAA server approves them, the concentrator can trust the result and treat you as authenticated.

​



**Authorization** (2nd A)

Authorization answers “Now that we know who you are, what are you allowed to access/do?”—for example, shipping users can access shipping systems but not finance data. In practice, authorization is usually implemented using an authorization model (an abstraction layer) so you don’t assign permissions one user at a time for every app/file/resource. A common scalable approach is group/role-based access: put users into a “Shipping and Receiving” group, and assign the group permissions once; everyone added to that group inherits the needed access.



**Accounting** (3rd A)

Accounting is the logging/auditing part: it records what happened during access, such as login time, logout time, and potentially how much data was sent/received. These records support troubleshooting, compliance, and incident investigations by giving you a timeline of activity tied to an authenticated identity.

​

​



**Device authentication with certificates**

Sometimes you must authenticate a device (like a company laptop) that can’t “type a password,” or you don’t want a static password stored on it. In that case, you can use a device certificate as an authentication factor: a Certificate Authority (CA) issues and digitally signs a certificate for that laptop, and systems can later verify it was signed by a CA they trust. This lets a VPN concentrator (or management system) confirm the connecting endpoint is an approved company device before granting access.





**Authorization models** scale access control by abstracting users/services from direct resource permissions, avoiding manual per-user setups. Without models, you'd assign individual rights (e.g., "create shipping label," "track shipment") to each of hundreds of shipping users across dozens of resources—impractical and error-prone. Models like role-based (RBAC) or group-based fix this: create a "Shipping and Receiving" group/role, grant it all needed permissions once, then add users to the group for instant inheritance. SY0-701 covers more (e.g., attribute-based) in section 4.6; they use roles, attributes, or org structures for efficient management



​


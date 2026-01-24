GAP analysis:   where you are to where you want to be. a lot of study and research is required.

Work towards a baseline. formal standards a good place to start. like NIST / ISO/IEC 27001.

Get a baseline of the employees. Formal training they've had, Current knowledge of security policies and procedures.

Examine the current process. such as existing security policies and the IT system.

Compare the existing system with where you want to be.









Zero trust:  many networks are not secure once you pass the through the firewall. Zero trust is an approach to net security where every device, every process and every person is covered. AAA when trying to access any device, process or person. Everything is verified. Splitting the network into separate functional planes. it could be anything. physical, virtual and / or cloud components.  Two planes: DATA plane - process the frames, packets and network data. Processing forwarding encryption.

CONTROL plane : manages the actions of the data plane, define polices and rules, determines how packets should be forwarded, and also routing tables, session tables NAT tables

physical example would be a switch. Where data plane is all the plugins where data is forwarded and the Control plane is the configuration part.

Adaptive identity :  consider the source and the requested resource.  multiple risk indicators should be verified such as the relationship to the org, their physical location thr type of connection, and IP address.

Threat Scope reduction :  decrease the entry points to trusted and secure points only.

**Policy driven access control :**



**Security zones :**  where you are connecting from and where you are connecting to. such as trusted connection to untrusted connection or vise versa

Internal to external network. Different VPNs and different branches of the organisation i.e. from HR to accounting. Using zones is enough to deny access. Some zones are implicitly trusted such as an internal zone traffic is trusted altogether.



**Policy enforcement points :**  any subjects or application trying to access resources should pass through the policy Enforcement Points. it is a gatekeeper and all traffic should pass through this point. can consist of multiple components.

For decision on whether a traffic is allowed or not is done by Policy Decision point.

POLICY ENGINE : evaluates each access decision based on the policy and then grants , denies or revokes the passage for the said traffic.

POLICY ADMINISTRATOR : Communicates with the PEP and generates access tokens and credentials. And then tells PEP to allow or disallow access.



**PHYSICAL Security :**



prevent access through barricades or bollards. To channel people through a specific access point.



Fences. Guards and access badges. Lighting. 







**Deception and Disruption :** 

Honeypot - Attract the bad guys and trap them there. And use it to understand what type of attack bad guys use.

Honeypot contains multiple components - such as servers , workstations, router, switches and firewalls. and honeynet contains multiple honeypots.

projecthoneypot.org is a website to understand honeypots in more detail.

Honeytokens - add some traceable data to the honeynet. if the data is stolen you know from where it was stolen.

&nbsp;Fake email address. database records, browser cookies, web page pixels are all honeytokens.







TASK - Why ZERO TRUST exists --- Zero trust exists to protect the oprganisation or the network even after an attacker gains access to it through the firewall. With zero trust every resource access requires AAA process which in turn protects the network from disallowed access.



Perimeter security and AAA difference - perimeter security is the firewalls, VPN concentrators Intrusion detection and prevention systems. it assumes everything beyond or inside the perimeter is trusted. AAA works through the perimeter and at the perimeter to verify  and control access.





&nbsp;


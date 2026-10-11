#!/usr/bin/env python3
# EC-05 traffic generator - builds a synthetic PCAP for the CTF lab.
# Author: IT24103798
from scapy.all import IP, TCP, Raw, wrpcap

# ---- values: must match EC-06 ----
FLAG   = "ECORP{exfil_over_http_traced}"
HOST   = "10.10.10.50"
USER   = "analyst"
PASS   = "NightShift104"

ATTACKER = "10.30.5.20"     # fake attacker machine
SERVER   = "10.30.5.10"     # fake internal server

packets = []

def http_exchange(payload, sport):
    """Build a tiny fake TCP/HTTP request + response as packets."""
    syn     = IP(src=ATTACKER, dst=SERVER)/TCP(sport=sport, dport=80, flags="S", seq=1000)
    synack  = IP(src=SERVER, dst=ATTACKER)/TCP(sport=80, dport=sport, flags="SA", seq=2000, ack=1001)
    ack     = IP(src=ATTACKER, dst=SERVER)/TCP(sport=sport, dport=80, flags="A", seq=1001, ack=2001)
    request = IP(src=ATTACKER, dst=SERVER)/TCP(sport=sport, dport=80, flags="PA", seq=1001, ack=2001)/Raw(load=payload)
    return [syn, synack, ack, request]

# 1) Some normal-looking traffic (noise, so it's not too obvious)
packets += http_exchange(
    "GET /index.html HTTP/1.1\r\nHost: ecorp.local\r\n\r\n", sport=40001)

# 2) The suspicious data-exfiltration request (this hides the clues)
exfil = (
    "POST /upload HTTP/1.1\r\n"
    "Host: ecorp.local\r\n"
    "Content-Type: text/plain\r\n\r\n"
    f"flag={FLAG}\r\n"
    f"transfer_target={HOST}\r\n"
    f"svc_user={USER}\r\n"
    f"svc_pass={PASS}\r\n"
)
packets += http_exchange(exfil, sport=40002)

# 3) A bit more noise
packets += http_exchange(
    "GET /style.css HTTP/1.1\r\nHost: ecorp.local\r\n\r\n", sport=40003)

wrpcap("network_capture.pcap", packets)
print(f"[+] Wrote network_capture.pcap with {len(packets)} packets")
print(f"[+] Hidden flag: {FLAG}")

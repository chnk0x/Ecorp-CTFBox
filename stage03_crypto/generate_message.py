#!/usr/bin/env python3
"""
EC-03 : The Three-Layer Attacker Message  (Cryptography stage)
Operation E Corp Breach

*** ORGANIZER-ONLY. NEVER DEPLOY THIS FILE TO THE CHALLENGE ZONE. ***

This script holds no secrets. The plaintext and the Vigenere key live in
private/, which is never served. Only public/attacker_message.txt is published.

Build order  :  Plaintext -> Vigenere(KEY) -> Hex -> Base64
Solve order (player, reverse) : Base64 decode -> Hex decode -> Vigenere decrypt

Usage:
    python3 generate_message.py            # build and write the artefact
    python3 generate_message.py --check    # verify only, write nothing
    python3 generate_message.py --show     # also print each intermediate layer
"""

import argparse
import base64
import os
import sys

# Paths resolve relative to this script, so it behaves the same however it is
# invoked (from a shell, from build.sh, or from cron).
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRIVATE_DIR = os.path.join(BASE_DIR, "private")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

PLAINTEXT_FILE = os.path.join(PRIVATE_DIR, "plaintext.txt")
KEY_FILE = os.path.join(PRIVATE_DIR, "key.txt")
OUTPUT_FILE = os.path.join(PUBLIC_DIR, "attacker_message.txt")


def load_secret(path, label):
    """Read an organizer-only input file and fail loudly if it is missing."""
    if not os.path.isfile(path):
        sys.exit(
            f"[FATAL] {label} not found at {path}\n"
            f"        Create it before running this script."
        )
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def vigenere_encrypt(text, key):
    """Shift letters only. Digits, {, }, _ and spaces pass through unchanged.
    The key does not advance on non-letters, which matches the CyberChef
    default so players get the same result with the standard tooling."""
    out = []
    ki = 0
    for ch in text:
        if ch.isalpha():
            base = 65 if ch.isupper() else 97
            k = ord(key[ki % len(key)].upper()) - 65
            out.append(chr((ord(ch) - base + k) % 26 + base))
            ki += 1
        else:
            out.append(ch)
    return "".join(out)


def vigenere_decrypt(text, key):
    """Inverse of vigenere_encrypt. Used for verification."""
    out = []
    ki = 0
    for ch in text:
        if ch.isalpha():
            base = 65 if ch.isupper() else 97
            k = ord(key[ki % len(key)].upper()) - 65
            out.append(chr((ord(ch) - base - k) % 26 + base))
            ki += 1
        else:
            out.append(ch)
    return "".join(out)


def build(plaintext, key):
    """Apply the three layers in order. Returns all three for inspection."""
    layer1 = vigenere_encrypt(plaintext, key)            # 1. Vigenere
    layer2 = layer1.encode("utf-8").hex()                # 2. Hex
    layer3 = base64.b64encode(layer2.encode()).decode()  # 3. Base64
    return layer1, layer2, layer3


def solve(artefact, key):
    """Reverse the layers exactly as a player would."""
    step1 = base64.b64decode(artefact).decode()      # Base64 decode
    step2 = bytes.fromhex(step1).decode("utf-8")     # Hex decode
    return vigenere_decrypt(step2, key)              # Vigenere decrypt


def main():
    parser = argparse.ArgumentParser(description="Generate the EC-03 artefact.")
    parser.add_argument("--check", action="store_true",
                        help="verify the round trip without writing anything")
    parser.add_argument("--show", action="store_true",
                        help="print each intermediate layer")
    args = parser.parse_args()

    plaintext = load_secret(PLAINTEXT_FILE, "plaintext.txt")
    key = load_secret(KEY_FILE, "key.txt").strip()

    layer1, layer2, artefact = build(plaintext, key)
    recovered = solve(artefact, key)

    # Self-test. An artefact that does not decode back to the intended
    # plaintext would make EC-03 unsolvable and stall every later stage,
    # so refuse to publish it.
    if recovered != plaintext:
        sys.exit("[FATAL] Round trip failed. Artefact NOT written.")

    if args.show:
        print(f"[Layer 1] Vigenere : {layer1[:60].replace(chr(10), ' ')} ...")
        print(f"[Layer 2] Hex      : {layer2[:60]} ...")
        print(f"[Layer 3] Base64   : {artefact[:60]} ...")
        print()

    if args.check:
        print("[OK] Round trip verified. Nothing written (--check).")
        return

    os.makedirs(PUBLIC_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(artefact + "\n")
    os.chmod(OUTPUT_FILE, 0o644)  # world-readable: the platform serves this

    print("[OK] Round trip verified.")
    print(f"[OK] Wrote {OUTPUT_FILE} ({len(artefact)} characters)")
    print("     This is the ONLY file to publish for EC-03.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Write secrets/flags.json from the plain flags.

Only SHA-256 hashes are stored, so the file the server reads never contains a
usable flag. Edit FLAGS below if you change a challenge, then re-run this.

    python3 seed_flags.py
"""

import hashlib
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRETS_DIR = os.path.join(BASE_DIR, "secrets")
OUT = os.path.join(SECRETS_DIR, "flags.json")

FLAGS = {
    "ec01": "ECORP{h34d3r_1nsp3ct10n_r3v34ls_th3_tru7h}",
    "ec02": "ECORP{st3g0_h1dd3n_1n_pl41n_s1ght}",
    "ec03": "ECORP{l4y3r3d_crypt0_vig3n3r3_h3x_b4s364}",
    "ec04": "ECORP{broken_access_control_774}",
    "ec05": "ECORP{exfil_over_http_traced}",
    "ec06": "ECORP{breach_fully_reconstructed}",
}

if __name__ == "__main__":
    os.makedirs(SECRETS_DIR, exist_ok=True)
    hashed = {k: hashlib.sha256(v.strip().encode()).hexdigest() for k, v in FLAGS.items()}
    with open(OUT, "w") as f:
        json.dump(hashed, f, indent=2)
        f.write("\n")
    os.chmod(OUT, 0o600)

    print(f"[OK] wrote {OUT} (0600)")
    for k, v in hashed.items():
        print(f"     {k}  sha256:{v[:16]}...")
    print()
    print("Keep this script out of the deployed folder, or at least out of git.")

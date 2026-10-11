#!/usr/bin/env bash
#
# Operation E Corp Breach - master build script for EC-01 to EC-03
#
# Builds every player-facing artefact from the organizer-only sources and
# locks down permissions on private/. Safe to re-run: each stage rebuilds
# from scratch, so this doubles as the reset procedure.
#
# Usage:
#   ./build.sh                 # build all three stages
#   ./build.sh my_photo.jpg    # same, but use your own photo for EC-02
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

COVER="${1:-}"

echo "==========================================================="
echo " Operation E Corp Breach - building EC-01 to EC-03"
echo "==========================================================="

# --------------------------------------------------------------- EC-01 ----
# EC-01 is a static file. There is nothing to generate: the .eml already
# lives in stage01_forensics/public/. We only confirm it is present and intact.
echo
echo "--- EC-01 : The Forged Security Alert ---------------------"
EML="stage01_forensics/public/suspicious_email.eml"
[[ -f "$EML" ]] || { echo "[FATAL] missing $EML"; exit 1; }

EXPECTED_FLAG="$(tr -d '\r\n' < stage01_forensics/private/expected_flag.txt)"
grep -q "X-Investigation-Flag: $EXPECTED_FLAG" "$EML" \
    || { echo "[FATAL] flag header missing or wrong in $EML"; exit 1; }
grep -q "X-Incident-Reference: ECORP-104" "$EML" \
    || { echo "[FATAL] incident reference header missing"; exit 1; }
grep -qi "company_event.jpg" "$EML" \
    || { echo "[FATAL] no reference to company_event.jpg"; exit 1; }
chmod 644 "$EML"
echo "[OK] $EML verified (flag, ECORP-104 and image reference present)"

# --------------------------------------------------------------- EC-02 ----
echo
echo "--- EC-02 : The Password-Protected Image ------------------"
# Steghide refuses to embed into an image that already carries a payload,
# so remove any previous build before rebuilding.
rm -f stage02_stego/public/company_event.jpg
if [[ -n "$COVER" ]]; then
    ./stage02_stego/build_ec02.sh "$COVER"
else
    ./stage02_stego/build_ec02.sh
fi

# --------------------------------------------------------------- EC-03 ----
echo
echo "--- EC-03 : The Three-Layer Attacker Message --------------"
python3 stage03_crypto/generate_message.py

# ---------------------------------------------------------- permissions ----
echo
echo "--- Locking down organizer-only material ------------------"
chmod 700 stage01_forensics/private stage02_stego/private stage03_crypto/private
chmod 600 stage01_forensics/private/* stage02_stego/private/* stage03_crypto/private/*
echo "[OK] private/ directories set to 0700, contents to 0600"

echo
echo "==========================================================="
echo " BUILD COMPLETE"
echo "==========================================================="
echo
echo " Publish ONLY these three files to the CTF platform:"
echo "   stage01_forensics/public/suspicious_email.eml"
echo "   stage02_stego/public/company_event.jpg"
echo "   stage03_crypto/public/attacker_message.txt"
echo
echo " Run ./verify.sh to execute the T01-T05 validation tests."

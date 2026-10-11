#!/usr/bin/env bash
#
# EC-02 : The Password-Protected Image  (Steganography stage)
# Operation E Corp Breach
#
# *** ORGANIZER-ONLY. Run on the organizer workstation (Kali), not in the box. ***
#
# Produces public/company_event.jpg :
#   1. creates (or reuses) a cover JPEG
#   2. writes the metadata clue into the Comment field
#   3. embeds private/hidden_message.txt with Steghide
#   4. verifies the clue survived AND the payload still extracts
#
# Usage:
#   ./build_ec02.sh                  # generate a cover image automatically
#   ./build_ec02.sh my_photo.jpg     # use your own photo as the cover
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRIVATE="$HERE/private"
PUBLIC="$HERE/public"

PAYLOAD="$PRIVATE/hidden_message.txt"
PASSWORD_FILE="$PRIVATE/stego_password.txt"
OUTPUT="$PUBLIC/company_event.jpg"

CLUE="Incident refs must be lowercase with no separators"

# ---------------------------------------------------------------- checks ----
for tool in steghide exiftool; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "[FATAL] $tool is not installed."
        echo "        sudo apt update && sudo apt install -y steghide libimage-exiftool-perl"
        exit 1
    fi
done

[[ -f "$PAYLOAD" ]]       || { echo "[FATAL] missing $PAYLOAD"; exit 1; }
[[ -f "$PASSWORD_FILE" ]] || { echo "[FATAL] missing $PASSWORD_FILE"; exit 1; }

PASSWORD="$(tr -d '\r\n' < "$PASSWORD_FILE")"
mkdir -p "$PUBLIC"

# ------------------------------------------------------- 1. cover image ----
# Steghide supports JPEG, BMP, WAV and AU only. PNG will not work.
if [[ $# -ge 1 ]]; then
    echo "[1/4] Using supplied cover image: $1"
    cp "$1" "$OUTPUT"
else
    echo "[1/4] Generating a cover image with Python/Pillow"
    python3 "$HERE/make_cover.py" "$OUTPUT"
fi

echo "      cover ready: $(du -h "$OUTPUT" | cut -f1)"

# --------------------------------------------------- 2. embed payload ----
#
# ORDER MATTERS. Steghide rewrites the JPEG when it embeds, and that rewrite
# DROPS the COM (comment) segment. So embedding must come FIRST and the
# metadata clue must be written afterwards.
#
# The reverse order silently destroys the clue: the build appears to succeed,
# but players get an image with no instruction on how to derive the password,
# which makes EC-02 unsolvable.
#
# Writing metadata afterwards is safe because ExifTool only touches the
# metadata segments and leaves the DCT coefficients, where the payload lives,
# untouched. Step 4 verifies both facts rather than trusting them.
#
# Steghide also refuses to embed into an image that already carries a payload,
# so a rebuild always starts from a fresh cover (handled above and in build.sh).
echo "[2/4] Embedding $(basename "$PAYLOAD") with Steghide"
steghide embed -cf "$OUTPUT" -ef "$PAYLOAD" -p "$PASSWORD" -q

# ---------------------------------------------------- 3. metadata clue ----
echo "[3/4] Writing the metadata clue into the Comment field"
exiftool -overwrite_original -Comment="$CLUE" "$OUTPUT" >/dev/null

# ------------------------------------------------------- 4. verify ----
echo "[4/4] Verifying the built artefact"

# 4a. is the clue present in the finished file?
FOUND_CLUE="$(exiftool -s3 -Comment "$OUTPUT" || true)"
if [[ "$FOUND_CLUE" != "$CLUE" ]]; then
    echo "[FATAL] metadata clue is not present in the finished image."
    echo "        expected: $CLUE"
    echo "        found   : $FOUND_CLUE"
    exit 1
fi
echo "      [OK] metadata clue present: $FOUND_CLUE"

# 4b. did the payload survive the ExifTool write?
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
steghide extract -sf "$OUTPUT" -p "$PASSWORD" -xf "$TMP/out.txt" -q
if ! diff -q "$PAYLOAD" "$TMP/out.txt" >/dev/null; then
    echo "[FATAL] extracted payload does not match the source."
    exit 1
fi
echo "      [OK] payload still extracts after the metadata write"

chmod 644 "$OUTPUT"
echo
echo "[DONE] $OUTPUT"
echo "       This is the ONLY file to publish for EC-02."

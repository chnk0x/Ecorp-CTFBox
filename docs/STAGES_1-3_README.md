# Operation E Corp Breach — EC-01 to EC-03

Implementation of the first three stages of the CTF play box: Digital
Forensics, Steganography and Cryptography. Built and tested on Kali Linux.

---

## 1. What is in here

```
ecorp-ctf/
├── build.sh                    # builds all three stages (also the reset procedure)
├── verify.sh                   # runs tests T01–T05 by solving each stage as a player
│
├── ec01/                       # The Forged Security Alert  (Forensics, 100 pts)
│   ├── private/expected_flag.txt
│   └── public/suspicious_email.eml          <- PUBLISH THIS
│
├── ec02/                       # The Password-Protected Image  (Stego, 100 pts)
│   ├── build_ec02.sh
│   ├── make_cover.py
│   ├── private/
│   │   ├── hidden_message.txt               # the embedded payload
│   │   ├── stego_password.txt               # ecorp104
│   │   └── expected_flag.txt
│   └── public/company_event.jpg             <- PUBLISH THIS
│
├── ec03/                       # The Three-Layer Attacker Message  (Crypto, 150 pts)
│   ├── generate_message.py
│   ├── private/
│   │   ├── plaintext.txt                    # flag, portal, employee ID
│   │   ├── key.txt                          # NIGHTSHIFT
│   │   └── expected_flag.txt
│   └── public/attacker_message.txt          <- PUBLISH THIS
│
└── ctfd/CTFD_SETUP.md          # descriptions, flags, hints, prerequisites
```

**The rule that matters:** everything under `public/` is served to players.
Nothing under `private/` ever leaves the organizer machine. `build.sh` sets
`private/` to `0700` and its contents to `0600` on every run.

---

## 2. Requirements

```bash
sudo apt update
sudo apt install -y steghide libimage-exiftool-perl python3 python3-pil
```

| Tool | Used for |
|---|---|
| `steghide` | embedding and extracting the EC-02 payload |
| `exiftool` | writing and reading the EC-02 metadata clue |
| `python3` | EC-03 generation, EC-02 cover image |
| `python3-pil` | only if you let the script generate a cover image |

---

## 3. Build

```bash
cd ecorp-ctf
chmod +x build.sh verify.sh ec02/build_ec02.sh
./build.sh
```

To use your own photograph as the EC-02 cover instead of the generated one:

```bash
./build.sh /path/to/your_photo.jpg
```

The cover **must** be JPEG, BMP, WAV or AU — Steghide does not support PNG.
A detailed photograph carries more payload than a flat graphic. If Steghide
reports the payload is too large, use a larger or more detailed image.

`build.sh` is safe to re-run. It deletes and rebuilds `ec02/public/company_event.jpg`
each time, because Steghide refuses to embed into an image that already
carries a payload. **This is also the reset procedure (test T08).**

---

## 4. Verify

```bash
./verify.sh
```

This solves all three stages the way a player would, using only the files in
`public/`. The EC-02 password is derived from the EC-01 header at runtime —
it is not read from `private/` — so a broken dependency chain shows up as a
failure rather than silently passing.

Expected on a correctly built box:

```
 RESULT: 11 passed, 0 failed
```

Exit code is `0` on success and `1` on any failure, so it drops straight into
CI or a pre-deployment check.

| Test | Checks |
|---|---|
| T01 | From ≠ Reply-To, SPF/DMARC fail, flag 1 and `ECORP-104` recoverable |
| T02 | metadata clue survived the Steghide embed |
| T03 | payload extracts with the **derived** password, yields flag 2 and `NIGHTSHIFT` |
| T04 | Base64 → Hex → Vigenère returns flag 3, portal address and ID 1042 |
| T05 | the whole chain holds end to end |

T06 (wrong flags rejected), T07 (hints and penalties) and T08 (reset) are
platform-level and are covered in `ctfd/CTFD_SETUP.md`.

---

## 5. Publish

Upload exactly these three files to CTFd, one per challenge:

```
ec01/public/suspicious_email.eml
ec02/public/company_event.jpg
ec03/public/attacker_message.txt
```

Then follow `ctfd/CTFD_SETUP.md` for descriptions, flags, hints and — most
importantly — **prerequisites**, which enforce the stage ordering.

Never upload `build.sh`, `verify.sh`, `generate_message.py`, `build_ec02.sh`
or anything under `private/`.

---

## 6. The dependency chain

```
EC-01  suspicious_email.eml
   │   X-Incident-Reference: ECORP-104
   │   references company_event.jpg
   ▼
EC-02  company_event.jpg
   │   metadata clue: "lowercase, no separators"
   │   ECORP-104 → ecorp104 → steghide password
   │   payload yields NIGHTSHIFT and names attacker_message.txt
   ▼
EC-03  attacker_message.txt
   │   Base64 → Hex → Vigenère(NIGHTSHIFT)
   ▼
EC-04  portal: http://portal.ecorp.local/login
       employee ID: 1042
```

Each handover carries two things: a value to use, and the name of the file to
use it on. That is what makes the path deducible rather than guessable.

---

## 7. Changing the content

**A different flag, portal or employee ID for EC-03**

```bash
nano ec03/private/plaintext.txt
python3 ec03/generate_message.py        # rebuilds and self-tests
```

The script refuses to write the artefact if it does not decode back to the
plaintext, so a bad edit cannot ship an unsolvable challenge.

**A different Vigenère key**

Change `ec03/private/key.txt` **and** the `Decryption key:` line in
`ec02/private/hidden_message.txt`, then run `./build.sh`. Both must match or
T05 will fail.

**A different incident reference**

Change it in three places, then rebuild: the `X-Incident-Reference` header in
`ec01/public/suspicious_email.eml`, the URL in that email's body, and
`ec02/private/stego_password.txt` (normalised form).

**A different EC-04 portal address**

If the Web Security stage changes, update `Portal:` in
`ec03/private/plaintext.txt` and re-run the generator. This is the handover
recorded in Section 12.1 of the design report.

After any change: run `./verify.sh` and re-upload the affected file.

---

## 8. Troubleshooting

**`steghide: could not extract any data with that passphrase!`**
The password is wrong, or the image was re-saved after embedding. Any tool
that re-compresses the JPEG destroys the payload. Rebuild with `./build.sh`.

**`steghide: the cover file is too small`**
The payload does not fit. Use a larger or more detailed cover image — flat
graphics have very little capacity.

**Metadata clue missing after building**
Steghide rewrites the JPEG when it embeds, and that rewrite **drops the COM
(comment) segment**. The clue must therefore be written *after* embedding, not
before. `build_ec02.sh` does it in that order and verifies both the clue and
the payload afterwards. If you change the script, keep the order:

```
steghide embed   →   exiftool -Comment=   →   verify both
```

The reverse order fails silently at build time and produces an unsolvable
challenge, because players get an image with no instruction on how to derive
the password. ExifTool is safe to run afterwards because it only touches
metadata segments and leaves the DCT coefficients, where the payload lives,
untouched.

**`verify.sh` reports `[SKIP]` lines**
`steghide` or `exiftool` is not installed. Install them (section 2) and re-run;
skipped tests do not prove anything.

**Players solve EC-02 without doing EC-01**
Prerequisites are not configured in CTFd, or you are testing with an admin
account — admins bypass prerequisites. Test with an ordinary account.

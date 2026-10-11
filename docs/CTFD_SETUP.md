# CTFd Configuration — EC-01 to EC-03

Enter these in **Admin Panel → Challenges → + Create Challenge**.
Create them in order, because each one's *Prerequisite* points at the
previous challenge.

---

## EC-01 — The Forged Security Alert

| Field | Value |
|---|---|
| Name | The Forged Security Alert |
| Category | Digital Forensics |
| Type | standard |
| Value | 100 |
| State | visible |
| Prerequisites | *(none — this is the entry point)* |

**Description**

> E Corp's SOC has flagged a message that reached an employee inbox during the
> incident window. It claims to come from internal IT Security, but the SOC is
> not convinced.
>
> Examine the message and establish who really sent it. Record the incident
> reference you find — the investigation will need it.

**File to upload:** `ec01/public/suspicious_email.eml`

**Flag:** `ECORP{h34d3r_1nsp3ct10n_r3v34ls_th3_tru7h}` — type `static`, **case sensitive**

**Hints**

| # | Cost | Text |
|---|---|---|
| 1 | 0 | An `.eml` file is plain text. Open it in a text editor rather than a mail client. |
| 2 | 10 | If you replied to this message, where would the reply actually go? |
| 3 | 25 | Headers beginning with `X-` are non-standard. Read all of them. |

---

## EC-02 — The Password-Protected Image

| Field | Value |
|---|---|
| Name | The Password-Protected Image |
| Category | Steganography |
| Type | standard |
| Value | 100 |
| State | visible |
| Prerequisites | **The Forged Security Alert** |

**Description**

> The email referenced an image that was attached to the original incident
> record. Forensics believes the attacker used it to move data past the mail
> filter.
>
> Something is embedded in this image. The image itself tells you how to
> construct the password — you already hold the value it applies to.

**File to upload:** `ec02/public/company_event.jpg`

**Flag:** `ECORP{st3g0_h1dd3n_1n_pl41n_s1ght}` — type `static`, **case sensitive**

**Hints**

| # | Cost | Text |
|---|---|---|
| 1 | 0 | Before looking at the pixels, look at the file's metadata. `exiftool` reads it. |
| 2 | 10 | The Comment field is an instruction, not the password. Apply it to what EC-01 gave you. |
| 3 | 25 | The tool is `steghide`. Use `steghide extract -sf <image> -p <password>`. |

---

## EC-03 — The Three-Layer Attacker Message

| Field | Value |
|---|---|
| Name | The Three-Layer Attacker Message |
| Category | Cryptography |
| Type | standard |
| Value | 150 |
| State | visible |
| Prerequisites | **The Password-Protected Image** |

**Description**

> Recovered from the attacker's staging host. The message has been wrapped
> several times to survive transit and to keep casual readers out.
>
> Unwrap it from the outside in. One of those layers takes a key — and you
> recovered that key from the image.

**File to upload:** `ec03/public/attacker_message.txt`

**Flag:** `ECORP{l4y3r3d_crypt0_vig3n3r3_h3x_b4s364}` — type `static`, **case sensitive**

**Hints**

| # | Cost | Text |
|---|---|---|
| 1 | 0 | Trailing `=` and an A–Z a–z 0–9 + / alphabet. Start there. |
| 2 | 15 | Under the first layer is an even-length string of `0-9a-f` only. |
| 3 | 30 | The final layer is a Vigenère cipher. The key is the one word from EC-02. |

---

## Global settings to check

**Admin Panel → Config → Settings**

- **Challenge visibility** → `private` (only logged-in users see challenges)
- **Score visibility** → `public` or `private`, as your group prefers
- **Account visibility** → `private`

**Admin Panel → Config → Security**

- Enable rate limiting on flag submission if your instance supports it. This
  blunts automated flag guessing.

**Verify prerequisites actually work**

1. Create a test account (do not use the admin account — admins bypass
   prerequisites).
2. Log in as the test account. Only EC-01 should be visible or unlocked.
3. Solve EC-01. EC-02 should unlock; EC-03 should stay locked.
4. This is test **T05** from the report and it is the single most important
   configuration check. Without it, a player could download
   `company_event.jpg` before ever seeing EC-01 and brute-force the password.

**Test rejection of wrong flags (test T06)**

Submit `ECORP{wrong}` to each challenge. CTFd must answer *Incorrect* without
revealing the expected value anywhere in the response. CTFd compares flags
server-side by default, so this should pass — confirm it rather than assume it.

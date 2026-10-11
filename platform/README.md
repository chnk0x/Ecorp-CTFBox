# Operation E Corp Breach — Playable Platform

The landing page with EC-01 to EC-03 wired up as real, playable challenges:
server-side flag validation, sequential unlocking, gated downloads, hints with
point penalties, and a live scoreboard.

---

## 1. Quick start

```bash
cd ecorp-webapp
pip install -r requirements.txt

# copy the three built artefacts from your ecorp-ctf box
cp ../ecorp-ctf/ec01/public/suspicious_email.eml   artefacts/
cp ../ecorp-ctf/ec02/public/company_event.jpg      artefacts/
cp ../ecorp-ctf/ec03/public/attacker_message.txt   artefacts/

python3 seed_flags.py     # writes secrets/flags.json (hashes only)
python3 app.py            # -> http://127.0.0.1:5000
```

> **`company_event.jpg` must be the one built by `ecorp-ctf/build.sh`.** Any
> other JPEG has no embedded payload, so EC-02 becomes unsolvable. `app.py`
> warns at startup if an artefact is missing, but it cannot tell whether an
> image carries the payload — use the built one.

Open the site, click **REGISTER**, pick a callsign, and play. The same form
signs you back in later.

---

## 2. Files

```
ecorp-webapp/
├── app.py               # Flask backend — all validation happens here
├── seed_flags.py        # writes secrets/flags.json from the plain flags
├── index.html           # the page (served by app.py)
├── requirements.txt
├── artefacts/           # NOT web-reachable; served only by /api/download
│   ├── suspicious_email.eml
│   ├── company_event.jpg
│   └── attacker_message.txt
├── secrets/             # NOT web-reachable
│   ├── flags.json       # SHA-256 hashes, 0600
│   └── session.key      # generated on first run, 0600
└── ctf.db               # SQLite: users, solves, hints, attempts
```

---

## 3. How the security design maps to the report

| Report claim | How it is implemented |
|---|---|
| "Flags are compared server-side" | `POST /api/submit` hashes the submission and compares it against `secrets/flags.json`. The response is only `correct: true/false` — the expected value never reaches the browser, not even on a wrong answer. |
| "Successful completion releases the next stage" | `is_unlocked()` checks the prerequisite against the `solves` table on every request. Unlock state is in the database, not in the cookie or in `localStorage`, so it cannot be edited client-side. |
| "Only the player-facing artefact is distributed" | `artefacts/` sits outside the web root. `/api/download/<stage>` is the only route to it and returns **403** unless that stage is unlocked. `/artefacts/...`, `/secrets/...` and `/app.py` all return **404**. |
| Hint penalties | `POST /api/hint` records the cost and subtracts it from the score. **Unpaid hint text is never sent to the browser** — it cannot be read out of the page source. |
| Brute-force resistance | 12 wrong answers per challenge per minute returns **429**. Passwords are PBKDF2-HMAC-SHA256 with 120,000 iterations and a per-user salt. |

**Verify it yourself** — with the server running:

```bash
# no flag anywhere in the page source
curl -s http://127.0.0.1:5000/ | grep -c "ECORP{h34d3r"        # -> 0

# artefacts and secrets are unreachable by path
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5000/artefacts/company_event.jpg   # -> 404
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5000/secrets/flags.json            # -> 404

# a locked stage refuses to hand over its file
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5000/api/download/ec02             # -> 401 or 403
```

These three commands are worth running in the viva. Press **F12** and search
the page source for `ECORP{` — nothing real comes back.

---

## 4. Changing a flag or a challenge

**A flag:** edit `FLAGS` in `seed_flags.py`, run `python3 seed_flags.py`, then
rebuild the matching artefact in `ecorp-ctf` and copy it over. No restart
needed — `flags.json` is re-read per request.

**Points, hints, names, difficulty:** edit the `CHALLENGES` list in `app.py`
and restart. The page reads all of this from `/api/state`, so the cards update
on their own.

**Adding EC-04 to EC-06:** append entries to `CHALLENGES` with
`"requires": "ec03"` and so on, add their artefacts, add their flags to
`seed_flags.py`, then replace the `Start Challenge →` link in those cards with
`<div class="play" data-ch="ec04"></div>`. Everything else is automatic.

---

## 5. Resetting

```bash
rm ctf.db          # clears all accounts, solves and scores
python3 app.py     # recreated empty on next start
```

Artefacts are rebuilt in the `ecorp-ctf` box with `./build.sh` and copied over.

---

## 6. Running it for the group

`app.py` binds to `127.0.0.1` — only your machine. To let others on the same
network play, change the last line to `host="0.0.0.0"` and share your LAN IP.

For anything beyond a classroom demo, put it behind Nginx with TLS and run it
under gunicorn rather than Flask's development server:

```bash
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

That matches the Nginx-reverse-proxy layer in your architecture diagram.

---

## 7. Notes

- The solve counts on the cards (214, 198, 142) are the original design
  placeholders. Real counts are in `/api/scoreboard` if you want to wire them up.
- EC-04 to EC-06 still show `Start Challenge →` and link to registration, since
  those stages belong to the rest of the group.
- Three broken `</p>` tags and two spelling errors in the original page were
  fixed while adding the challenges.

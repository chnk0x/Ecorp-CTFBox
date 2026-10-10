<div align="center">

<img src="docs/assets/ecorp-ctf-2026-banner.svg" alt="Ecorp-CTF-2026 — Operation E Corp Breach" width="100%">

<br>

![Stages](https://img.shields.io/badge/stages-6-5cffc0?style=for-the-badge&labelColor=06151b)
![Points](https://img.shields.io/badge/base_points-1%2C000-2ee6ff?style=for-the-badge&labelColor=06151b)
![Docker](https://img.shields.io/badge/docker-compose_v2-2496ED?style=for-the-badge&logo=docker&logoColor=white&labelColor=06151b)
![Python](https://img.shields.io/badge/python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=06151b)
![Flask](https://img.shields.io/badge/flask-API-ffffff?style=for-the-badge&logo=flask&logoColor=white&labelColor=06151b)
![Exposure](https://img.shields.io/badge/exposure-127.0.0.1_only-ff5f56?style=for-the-badge&labelColor=06151b)

**Operation E Corp Breach** — a six-stage, story-driven cybersecurity capture-the-flag range.
<br>
Follow one incident from a *forged alert* to a *compromised Linux host*.

[**Quick start**](#-quick-start) · [**Investigation**](#-the-six-stage-investigation) · [**Architecture**](#-architecture) · [**ATT&CK map**](#-mitre-attck-mapping) · [**Run a session**](#-running-a-session) · [**Troubleshooting**](#-troubleshooting)

</div>

---

> [!WARNING]
> **This is an intentionally vulnerable training lab.** It uses fictional data and loopback-only Docker port mappings. Keep it isolated. Never expose the targets to a public network and never use these techniques against systems you do not own or have written permission to test.

## 📑 Contents

- [Mission brief](#-mission-brief)
- [The six-stage investigation](#-the-six-stage-investigation)
- [What makes this range different](#-what-makes-this-range-different)
- [Architecture](#-architecture)
- [Quick start](#-quick-start)
- [Preflight health check](#-preflight-health-check)
- [Player field kit](#-player-field-kit)
- [MITRE ATT&CK mapping](#-mitre-attck-mapping)
- [Learning outcomes](#-learning-outcomes)
- [Scoring](#-scoring)
- [Running a session](#-running-a-session)
- [Organizer workflow](#-organizer-workflow)
- [Project layout](#-project-layout)
- [Design and accessibility](#-design-and-accessibility)
- [Safety model and spoiler policy](#-safety-model-and-spoiler-policy)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Roadmap](#-roadmap)
- [Author](#-author)

---

## 🎯 Mission brief

E Corp has reported a suspicious security alert, unexplained data movement, and a missing incident report. Investigators work through six linked exercises, moving from digital evidence to a live fictional portal, then into a packet capture and finally a Linux host.

The range combines a responsive web platform with a Flask JSON API, SQLite-backed player progress, gated evidence downloads, and two deliberately vulnerable target services. It is built for guided demonstrations, classroom labs, and small-team CTF exercises.

```text
┌─────────────────────────────────────────────────────────────┐
│  CASE FILE   : EC-2026-BREACH                               │
│  CLIENT      : E Corp (fictional)                           │
│  STATUS      : OPEN                                         │
│  OBJECTIVE   : Reconstruct the attack, recover every flag   │
│  RULES       : Evidence unlocks in order. Follow the trail. │
└─────────────────────────────────────────────────────────────┘
```

### Technology stack

| Layer | Technologies |
|---|---|
| Interface | Semantic HTML, responsive CSS, vanilla JavaScript, inline SVG |
| Platform API | Python 3.11, Flask, JSON endpoints |
| State | SQLite, server-managed sessions and progression |
| Range services | Docker Compose, separate Flask portal, isolated Linux/SSH target |
| Organizer workflow | Bash and Python build, synchronization, and verification scripts |

---

## 🕵️ The six-stage investigation

| Stage | Mission | Domain | Base points | Evidence / activity |
|---|---|---|---:|---|
| **EC-01** | The Forged Security Alert | Digital forensics | 100 | Inspect a suspicious email and its headers. |
| **EC-02** | The Password-Protected Image | Steganography | 100 | Examine image metadata and extract a hidden message. |
| **EC-03** | The Three-Layer Attacker Message | Cryptography | 150 | Reverse layered Base64, hexadecimal, and Vigenère encoding. |
| **EC-04** | The Compromised Employee Portal | Web security | 150 | Investigate exposed paths and intentionally broken access control. |
| **EC-05** | Tracing the Data Exfiltration | Networking | 200 | Analyze a PCAP and follow the suspicious HTTP conversation. |
| **EC-06** | The Final Breach Investigation | Linux / system security | 300 | Investigate a fictional SSH host, logs, hidden files, and a protected report. |

The path is **sequential**: submit the current stage's correct flag to unlock the next stage's evidence and tools. Challenge cards can be opened directly with `?challenge=ec01` through `?challenge=ec06`.

### Difficulty curve

```mermaid
pie showData title Base points by stage
    "EC-01 Forensics" : 100
    "EC-02 Stego" : 100
    "EC-03 Crypto" : 150
    "EC-04 Web" : 150
    "EC-05 Network" : 200
    "EC-06 Linux" : 300
```

Points rise with depth: the final host investigation is worth three times the opening stage.

---

## ✨ What makes this range different

| | Feature | Why it matters |
|---|---|---|
| 📖 | **One continuous story** | Every stage is a chapter of the same incident, so players practice *investigating*, not just solving isolated puzzles. |
| 🔐 | **Server-owned progression** | Flag digests, unlocks, and scoring live in the API. Browser state cannot skip a stage. |
| 🚪 | **Gated evidence** | Downloads are served through an access-controlled endpoint and open only when the previous stage is solved. |
| 🧪 | **Real tooling, safe targets** | Players use the same tools they would on the job (header analysis, Wireshark, SSH) against fictional systems. |
| 💡 | **Progressive hints with a cost** | Hints get stronger as they are used, and the deduction shows up in the score. |
| 🏆 | **Live scoreboard** | Accepted solves feed a shared ranking for classroom or team play. |
| 🎖️ | **Completion badge** | Finishing all six stages reveals a personalized achievement badge (SVG and PNG download). |
| 🧰 | **Organizer scripts** | Build, sync, and verify scripts keep every player-facing artifact consistent. |
| ♿ | **Accessible UI** | Reduced-motion support, visible keyboard focus, semantic links, and live status messages. |
| 📦 | **No CDN needed** | The platform UI needs no external fonts or JavaScript CDNs and works on an offline lab network. |

---

## 🏗️ Architecture

```mermaid
flowchart LR
    P[Investigator] --> UI[Responsive HTML / CSS / JavaScript UI]
    UI --> API[Flask JSON API]
    API --> DB[(SQLite accounts and progress)]
    API --> V[Server-side flag and unlock checks]
    API --> E[Authenticated evidence downloads]
    UI -. unlocked mission .-> WEB[EC-04 fictional Flask portal]
    UI -. final mission .-> SSH[EC-06 isolated SSH host]
    E --> PCAP[EC-05 packet capture]
```

The browser presents the mission interface; the API owns progression and scoring decisions. EC-04 and EC-06 are separate services in the Compose range.

### Flag submission flow

```mermaid
sequenceDiagram
    autonumber
    actor P as Player
    participant UI as Browser UI
    participant API as Flask API
    participant DB as SQLite
    P->>UI: Submit flag for stage N
    UI->>API: POST flag (authenticated session)
    API->>DB: Check stage N-1 is solved
    API->>API: Compare flag digest (server-side)
    alt correct
        API->>DB: Record solve, apply hint deductions
        API-->>UI: Success + next stage unlocked
    else incorrect
        API-->>UI: Failure (expected answer is never returned)
    end
```

### Network zones

```mermaid
flowchart TB
    subgraph HOST["Your machine — 127.0.0.1 only"]
        direction TB
        subgraph COMPOSE["Docker Compose network"]
            PL["platform<br/>Flask :5000"]
            E4["ec04<br/>Flask :8080"]
            E6["ec06<br/>SSH :22"]
        end
    end
    PL -. published as .-> A1["127.0.0.1:5001"]
    E4 -. published as .-> A2["127.0.0.1:8081"]
    E6 -. published as .-> A3["127.0.0.1:2223"]
    NET(["Public internet"]) -. no route .-x HOST
```

| Component | Host address | Container service |
|---|---|---|
| CTF platform | `http://127.0.0.1:5001` | Flask on port `5000` |
| EC-04 portal | `http://127.0.0.1:8081` | Flask on port `8080` |
| EC-06 SSH target | `127.0.0.1:2223` | SSH on port `22` |

The Compose file binds host ports to `127.0.0.1`; the portal and SSH target are part of the fictional lab, not public internet services.

---

## 🚀 Quick start

### Requirements

- Docker Engine with the Docker Compose v2 plugin
- A shell capable of running the included Bash scripts

### Launch

From the project root:

```bash
bash sync_artefacts.sh
docker compose up -d --build
```

Open **http://127.0.0.1:5001**, create a callsign, and begin with **EC-01**. The portal and SSH target are reached later through the challenge clues and access cards.

### Operator commands

```bash
docker compose ps                         # inspect service status
docker compose logs -f platform           # follow platform logs
docker compose logs -f ec04 ec06          # inspect target logs
docker compose down                       # stop and remove the containers
```

> [!NOTE]
> If you intentionally change a host port, update the corresponding clue card, the EC-03 generated message where applicable, the integration notes, and the verification checks together.

---

## 🩺 Preflight health check

Run this before a class or event to confirm the whole range is reachable. Every check is local.

```bash
# 1. containers are up
docker compose ps

# 2. platform answers on the loopback port
curl -sI http://127.0.0.1:5001 | head -n 1

# 3. EC-04 portal answers
curl -sI http://127.0.0.1:8081 | head -n 1

# 4. EC-06 SSH port is listening
nc -zv 127.0.0.1 2223

# 5. confirm nothing is bound to all interfaces
docker compose ps --format '{{.Name}}  {{.Ports}}'
```

Step 5 should show only `127.0.0.1:` bindings. If you ever see `0.0.0.0:` in front of a published port, stop the range and fix `docker-compose.yml` before continuing.

You can also run the full organizer suite at any time:

```bash
bash verify.sh
```

---

## 🧰 Player field kit

Tools players commonly reach for. None are bundled; install what you prefer.

| Stage | Domain | Suggested tools |
|---|---|---|
| EC-01 | Forensics | A text editor or mail client that shows raw headers, `grep`, online header analyzers |
| EC-02 | Steganography | `exiftool`, `strings`, `file`, common steganography extraction tools |
| EC-03 | Cryptography | [CyberChef](https://gchq.github.io/CyberChef/), Python, a Vigenère reference |
| EC-04 | Web security | Browser dev tools, `curl`, a content-discovery tool, an intercepting proxy |
| EC-05 | Networking | Wireshark or `tshark`, follow-stream, export-objects |
| EC-06 | Linux | `ssh`, `ls -la`, `find`, `grep`, `less`, log inspection |

---

## 🗺️ MITRE ATT&CK mapping

A suggested mapping of each stage to adversary behavior, useful for debriefs and for tying the exercise to a recognized framework. Adjust technique IDs to match your final scenario wording.

| Stage | Tactic | Representative technique |
|---|---|---|
| EC-01 | Initial Access | [T1566](https://attack.mitre.org/techniques/T1566/) Phishing (spoofed sender) |
| EC-02 | Defense Evasion | [T1027.003](https://attack.mitre.org/techniques/T1027/003/) Steganography |
| EC-03 | Defense Evasion | [T1027](https://attack.mitre.org/techniques/T1027/) Obfuscated Files or Information, [T1140](https://attack.mitre.org/techniques/T1140/) Deobfuscate/Decode |
| EC-04 | Initial Access / Discovery | [T1190](https://attack.mitre.org/techniques/T1190/) Exploit Public-Facing Application, [T1595.003](https://attack.mitre.org/techniques/T1595/003/) Wordlist Scanning |
| EC-05 | Exfiltration | [T1048.003](https://attack.mitre.org/techniques/T1048/003/) Exfiltration Over Unencrypted Non-C2 Protocol |
| EC-06 | Discovery / Collection | [T1083](https://attack.mitre.org/techniques/T1083/) File and Directory Discovery, [T1005](https://attack.mitre.org/techniques/T1005/) Data from Local System |

```mermaid
flowchart LR
    A["Initial Access<br/>EC-01 · EC-04"] --> B["Defense Evasion<br/>EC-02 · EC-03"] --> C["Discovery<br/>EC-04 · EC-06"] --> D["Collection<br/>EC-06"] --> E["Exfiltration<br/>EC-05"]
```

---

## 🎓 Learning outcomes

After completing the range, a player should be able to:

- [ ] Read raw email headers and identify signs of spoofing
- [ ] Inspect file metadata and recover hidden data from an image
- [ ] Recognize and reverse stacked encodings, and tell encoding apart from encryption
- [ ] Explain broken access control and why hidden paths are not security
- [ ] Follow a suspicious conversation through a packet capture and extract what was moved
- [ ] Navigate an unfamiliar Linux host: hidden files, logs, permissions
- [ ] Write a short incident timeline that links all six findings into one story

**Suggested debrief question:** *which single control would have stopped the attack earliest, and at which stage?*

---

## 🏆 Scoring

| Rule | Behavior |
|---|---|
| Base points | Up to **1,000** across the six stages |
| Hints | Progressively stronger; each hint's cost is deducted from that stage's score |
| Validation | Flag digests are checked on the server; responses never reveal the expected answer |
| Unlocks | Checked against recorded solves in SQLite, not browser state |
| Ranking | Accepted solves contribute to the shared scoreboard |
| Completion | Solving all six stages reveals the personalized badge |

---

## 🧑‍🏫 Running a session

The range works as a self-paced lab, a guided class, or a small-team event.

| Format | Setup | Suggested pacing |
|---|---|---|
| **Guided demo** | Presenter runs EC-01 to EC-03 live; audience follows along | Short session, stop before the networked stages |
| **Classroom lab** | One range per student on their own machine | Stages 1 to 3 in the first sitting, 4 to 6 in the second |
| **Team CTF** | One shared range on an isolated lab network, scoreboard on a projector | Teams race through all six; award the badge at the end |

**Facilitator tips**

- Run the [preflight check](#-preflight-health-check) before participants arrive.
- Keep the scoreboard visible; the ranking drives engagement in team mode.
- Hold the debrief back until everyone is finished, then walk the [ATT&CK map](#-mitre-attck-mapping) stage by stage.
- Ask players to write the final incident timeline in their own words as the closing exercise.

> [!IMPORTANT]
> For shared events, run the range on an isolated lab network and give each participant their own callsign. Do not change the `127.0.0.1` bindings to expose the targets to other machines unless you fully control that network.

---

## 🛠️ Organizer workflow

The supplied archive already contains player-facing evidence. These commands are for organizers who are rebuilding or editing it.

```bash
bash build.sh                 # rebuild/check EC-01 to EC-03 artifacts
bash sync_artefacts.sh        # copy player artifacts into the platform
bash verify.sh                # run the organizer validation suite
```

The EC-02 builder uses steganography tooling; the EC-03 generator uses only Python's standard library. EC-05 traffic can be regenerated with `python3 stage05_network/generate_traffic.py` when its Scapy dependency is available. Re-run synchronization after changing a source artifact so the platform and EC-04 portal receive the same player-facing file.

### Organizer checklist

- [ ] `bash build.sh` completes without errors
- [ ] `bash sync_artefacts.sh` run after every artifact change
- [ ] `bash verify.sh` passes
- [ ] `docker compose up -d --build` starts all three services
- [ ] Preflight shows only `127.0.0.1` bindings
- [ ] `stage0*/private/`, `platform/seed_flags.py`, and `platform/secrets/` are **excluded** from the player distribution
- [ ] A test player completes EC-01 to EC-06 end to end

For the platform alone, see [`platform/README.md`](platform/README.md). Additional deployment and stage notes are in [`docs/`](docs/) and [`platform/INTEGRATION_NOTES.md`](platform/INTEGRATION_NOTES.md).

---

## 🗂️ Project layout

```text
Ecorp-CTF-2026/
├── README.md                         # project guide and operator quickstart
├── docker-compose.yml                # loopback-only range topology
├── build.sh                          # EC-01–EC-03 organizer build
├── sync_artefacts.sh                 # publish/synchronize player evidence
├── verify.sh                         # organizer validation checks
├── docs/
│   ├── assets/ecorp-ctf-2026-banner.svg
│   ├── CTFD_SETUP.md
│   └── STAGES_1-3_README.md
├── platform/
│   ├── app.py                        # Flask API, auth, progression, scoring
│   ├── index.html                    # responsive mission interface
│   ├── seed_flags.py                 # organizer flag-hash seeder
│   ├── artefacts/                    # platform-served evidence
│   └── secrets/                      # private server-side material
├── stage01_forensics/                # email evidence
├── stage02_stego/                    # image and hidden payload
├── stage03_crypto/                   # layered message generator
├── stage04_web/                      # fictional employee portal
├── stage05_network/                  # PCAP generator and capture
└── stage06_linux/                    # isolated Linux/SSH target
```

Each stage folder contains maintainer sources and, where applicable, separate `public/` and `private/` material. Keep private files out of player-facing downloads.

---

## 🎨 Design and accessibility

The platform uses a dark operations-console visual language with mint/cyan accents, inline SVG iconography, responsive layouts, and restrained interaction feedback.

| Area | Behavior |
|---|---|
| Motion | Ambient background drift, hero illustration, hover states, and short modal/toast transitions, without a continuous JavaScript animation loop |
| Reduced motion | Honors `prefers-reduced-motion` in both the platform and the README banner |
| Keyboard | Visible focus states on interactive elements |
| Semantics | Real links for challenge navigation, live regions for key status messages |
| Dependencies | No external fonts or JavaScript CDNs required |

---

## 🛡️ Safety model and spoiler policy

### Safety model

| Control | Detail |
|---|---|
| Training scope | EC-04 intentionally demonstrates unsafe discovery and access-control behavior; EC-06 is a deliberately configured practice host |
| Loopback exposure | Compose publishes services on `127.0.0.1`. Never change this to `0.0.0.0` or forward it to an untrusted network |
| Organizer material | `stage0*/private/`, `platform/seed_flags.py`, `platform/secrets/`, and some design/deployment documents contain answer or operator information |
| Synthetic data | E Corp, people, credentials, incidents, and artifacts are fictional |
| No production claim | This is an educational CTF range, not a hardened production service |

### Spoiler policy

This README intentionally contains **no flags, credentials, or solution steps**. If you contribute walkthroughs, keep them in a separate organizer-only document and never in a player-facing distribution. Writeups shared publicly should wait until after an event ends.

---

## 🔧 Troubleshooting

<details>
<summary><strong>The platform page loads, but evidence or solves are unavailable</strong></summary>

Check that the platform container is healthy with `docker compose ps`, then inspect `docker compose logs -f platform`. Confirm the evidence sync completed before starting the range.

</details>

<details>
<summary><strong>The EC-04 portal or EC-06 SSH connection does not respond</strong></summary>

Check the `ec04` and `ec06` services with `docker compose ps` and review their logs. Confirm that the host ports `8081` and `2223` are not already in use. The container ports remain `8080` and `22` respectively.

</details>

<details>
<summary><strong>The EC-03 clue points to the wrong portal port</strong></summary>

The decoded address comes from `stage03_crypto/private/plaintext.txt`. Regenerate the public message with `python3 stage03_crypto/generate_message.py`, then run `bash sync_artefacts.sh` and `bash verify.sh`.

</details>

<details>
<summary><strong>A port is already in use on my machine</strong></summary>

Find what is using it (`ss -ltnp | grep -E '5001|8081|2223'`), stop that process, or change the host-side port in `docker-compose.yml` and update the matching clue card, EC-03 message, integration notes, and verification checks together.

</details>

<details>
<summary><strong>I want to reset all player progress</strong></summary>

Stop the range with `docker compose down`, remove the platform's SQLite data volume or file according to your Compose setup, then start again with `docker compose up -d --build`. Back up first if you need the scoreboard.

</details>

<details>
<summary><strong>The banner image does not show on GitHub</strong></summary>

Confirm the file exists at `docs/assets/ecorp-ctf-2026-banner.svg` in the repository and that it was committed (`git add docs/assets/ecorp-ctf-2026-banner.svg`). The path in the README is relative to the repository root.

</details>

---

## ❓ FAQ

**Do I need internet access to play?**
No. The platform has no external font or CDN dependency. You only need internet to build the Docker images the first time.

**Can I run it on a shared server?**
Only on an isolated network you control. The targets are intentionally vulnerable.

**Can players skip ahead?**
No. Unlocks are enforced server-side against recorded solves.

**Where do the answers live?**
In organizer-only files (`private/`, `seed_flags.py`, `secrets/`). Keep them out of player distributions.

**Can I add a seventh stage?**
Yes. Follow the existing stage-folder pattern, seed its flag digest, register its evidence in the platform, then update `sync_artefacts.sh` and `verify.sh`.

---

## 🧭 Roadmap

Ideas for future versions (not yet implemented):

- [ ] Optional timed event mode with a countdown and freeze-able scoreboard
- [ ] Per-team accounts and team scoring
- [ ] Organizer dashboard for live solve and hint statistics
- [ ] Printable incident-report template for the final debrief
- [ ] Bonus side-quests that do not affect the main 1,000 points

---

## 👤 Author

**Chanuka Nuwan** (`chnk0x`) — cybersecurity undergraduate at SLIIT.

[![GitHub](https://img.shields.io/badge/GitHub-chnk0x-181717?style=flat-square&logo=github)](https://github.com/chnk0x)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Chanuka_Nuwan-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/chanuka-nuwan-1a07b8393)

Feedback, issues, and stage ideas are welcome.

---

<div align="center">
  <sub>OPERATION E CORP · FOLLOW THE EVIDENCE · VERIFY EVERY FLAG · CLOSE THE INCIDENT</sub>
</div>

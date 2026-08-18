# Operation E Corp Breach

> A six-stage cybersecurity Capture the Flag challenge based on investigating a fictional corporate security breach.

## Project Overview

Operation E Corp Breach is an educational Capture the Flag (CTF) platform designed to help participants develop practical cybersecurity investigation skills.

E Corp has been compromised by an unknown attacker. Participants act as cybersecurity investigators responsible for examining suspicious evidence, identifying vulnerabilities, analyzing compromised systems, and recovering six hidden flags.

Each challenge represents a different stage of the investigation and introduces a specific cybersecurity domain.

## Scenario

An E Corp employee receives a suspicious security alert. Following this initial incident, investigators discover hidden information inside an image, encrypted attacker communications, an exposed employee portal, suspicious network traffic, and evidence on a compromised Linux server.

Players must connect these clues to reconstruct the attack and complete the investigation.

### Investigation Flow

```text
Suspicious Phishing Email
          ↓
Hidden Information Inside an Image
          ↓
Encrypted Attacker Communication
          ↓
Compromised Employee Web Portal
          ↓
Suspicious Network Traffic
          ↓
Compromised Linux Server
```

## Project Objectives

- Provide practical experience across multiple cybersecurity domains.
- Teach participants how to investigate a realistic security incident.
- Develop analytical thinking and problem-solving skills.
- Demonstrate how individual security weaknesses can contribute to a larger breach.
- Introduce common cybersecurity tools and investigation techniques.
- Provide an educational environment for practicing ethical security analysis.

## Target Audience

This CTF is designed for:

- Undergraduate cybersecurity students.
- Information technology students.
- Beginners interested in ethical hacking.
- Participants with basic Linux and networking knowledge.
- Students learning digital forensics, cryptography, and web security.

## Challenge Overview

| Stage | Challenge | Cybersecurity Domain | Difficulty | Points |
|---|---|---|---|---:|
| EC-01 | The Forged Security Alert | Digital Forensics | Easy | 100 |
| EC-02 | The Password-Protected Image | Steganography | Easy | 100 |
| EC-03 | The Three-Layer Attacker Message | Cryptography | Moderate | 150 |
| EC-04 | The Compromised Employee Portal | Web Security | Moderate | 150 |
| EC-05 | Tracing the Data Exfiltration | Networking | Moderate–Hard | 200 |
| EC-06 | The Final Breach Investigation | Linux / System Security | Hard | 300 |
| **Total** | **6 Challenges** | **6 Domains** | **Progressive Difficulty** | **1,000** |

## Challenge Descriptions

### EC-01: The Forged Security Alert

**Domain:** Digital Forensics  
**Difficulty:** Easy  
**Points:** 100

An E Corp employee receives a suspicious email claiming to originate from the internal security team.

Participants investigate the email to identify phishing indicators and determine whether the message is legitimate.

**Skills assessed:**

- Email header analysis.
- Sender verification.
- Phishing detection.
- Evidence identification.

**Suggested tools:**

- Text editor.
- Email viewer.
- Linux terminal.
- `grep`.

### EC-02: The Password-Protected Image

**Domain:** Steganography  
**Difficulty:** Easy  
**Points:** 100

Investigators discover a company image associated with the suspicious email. Although it appears ordinary, the image contains hidden information.

Participants must examine the image and extract its concealed contents.

**Skills assessed:**

- Image metadata analysis.
- Hidden file discovery.
- Steganography techniques.
- Password clue identification.

**Suggested tools:**

- ExifTool.
- Steghide.
- Linux terminal.
- Image metadata viewers.

### EC-03: The Three-Layer Attacker Message

**Domain:** Cryptography  
**Difficulty:** Moderate  
**Points:** 150

The hidden image reveals an attacker communication protected by multiple encoding and encryption layers.

Participants must identify the transformations and reverse them in the correct order.

**Skills assessed:**

- Base64 decoding.
- Hexadecimal decoding.
- Classical cipher analysis.
- Multi-layer cryptographic problem solving.

**Suggested tools:**

- CyberChef.
- Python.
- Base64 decoder.
- Hexadecimal decoder.
- Vigenère cipher tools.

### EC-04: The Compromised Employee Portal

**Domain:** Web Security  
**Difficulty:** Moderate  
**Points:** 150

The attacker’s communication leads investigators to an E Corp employee portal containing exposed resources and improperly protected information.

Participants investigate the application and identify the relevant incident record.

**Skills assessed:**

- Web resource discovery.
- Application enumeration.
- API analysis.
- Broken access control identification.
- Exposed configuration investigation.

**Suggested tools:**

- Web browser.
- Browser developer tools.
- `curl`.
- Postman.
- Burp Suite Community Edition.

### EC-05: Tracing the Data Exfiltration

**Domain:** Networking  
**Difficulty:** Moderate–Hard  
**Points:** 200

Investigators obtain a packet capture containing network traffic associated with the E Corp breach.

Participants analyze the traffic to identify suspicious communications and recover evidence relevant to the compromised server.

**Skills assessed:**

- Packet capture analysis.
- Protocol filtering.
- TCP stream reconstruction.
- Identification of insecure communications.
- Network-based evidence correlation.

**Suggested tools:**

- Wireshark.
- TShark.
- `tcpdump`.
- Network protocol filters.

### EC-06: The Final Breach Investigation

**Domain:** Linux / System Security  
**Difficulty:** Hard  
**Points:** 300

The final stage takes participants to a compromised Linux environment containing hidden files, suspicious logs, a simulated scheduled task, and protected evidence.

Participants combine information from previous stages to complete the investigation.

**Skills assessed:**

- Linux command-line navigation.
- Hidden file discovery.
- Log analysis.
- Scheduled task inspection.
- Archive extraction.
- Incident reconstruction.

**Suggested tools:**

- SSH.
- `ls`.
- `find`.
- `grep`.
- `cat`.
- `crontab`.
- `unzip`.

## Difficulty Progression

| Stage Range | Difficulty | Purpose |
|---|---|---|
| Stages 1–2 | Easy | Introduce the storyline and basic investigation techniques. |
| Stages 3–4 | Moderate | Require participants to apply cybersecurity tools and analytical methods. |
| Stage 5 | Moderate–Hard | Combine network analysis with evidence correlation. |
| Stage 6 | Hard | Integrate information from earlier stages into a final investigation. |

## Flag Format

All challenge flags follow this format:

```text
ECORP{flag_description}
```

Example:

```text
ECORP{example_flag_format}
```

Flags must be submitted exactly as displayed, including:

- Uppercase `ECORP` prefix.
- Curly brackets.
- Correct spelling.
- Underscores where applicable.

Actual challenge flags should not be published in this public repository.

## Proposed Technology Stack

### Platform

- Python.
- Flask.
- Docker or Docker Compose.
- Linux-based operating environment.
- CTF scoring platform or custom flag-validation application.

### Security and Investigation Tools

- Wireshark.
- TShark.
- ExifTool.
- Steghide.
- CyberChef.
- Burp Suite Community Edition.
- OpenSSH.
- `tcpdump`.
- Standard Linux command-line utilities.

### Development Tools

- Visual Studio Code.
- Git.
- GitHub.
- Python virtual environments.

## Proposed Project Structure

```text
operation-ecorp-breach/
│
├── README.md
├── docker-compose.yml
├── requirements.txt
├── .gitignore
│
├── challenges/
│   │
│   ├── stage-01-digital-forensics/
│   │   ├── challenge.md
│   │   └── evidence/
│   │       └── suspicious_email.eml
│   │
│   ├── stage-02-steganography/
│   │   ├── challenge.md
│   │   └── evidence/
│   │       └── company_event.jpg
│   │
│   ├── stage-03-cryptography/
│   │   ├── challenge.md
│   │   ├── evidence/
│   │   │   └── attacker_message.txt
│   │   └── scripts/
│   │       └── generate_message.py
│   │
│   ├── stage-04-web-security/
│   │   ├── challenge.md
│   │   ├── app.py
│   │   ├── templates/
│   │   └── Dockerfile
│   │
│   ├── stage-05-networking/
│   │   ├── challenge.md
│   │   └── evidence/
│   │       └── network_capture.pcap
│   │
│   └── stage-06-linux-security/
│       ├── challenge.md
│       ├── setup/
│       ├── evidence/
│       └── Dockerfile
│
├── platform/
│   ├── app.py
│   ├── templates/
│   ├── static/
│   └── validation/
│
├── docs/
│   ├── architecture.md
│   ├── challenge-specifications.md
│   ├── deployment-guide.md
│   ├── testing-plan.md
│   └── risk-assessment.md
│
└── tests/
    ├── test_challenges.py
    ├── test_platform.py
    └── test_integration.py
```

> This structure represents the intended implementation and may evolve during development.

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
```

### 2. Open the Project Directory

```bash
cd operation-ecorp-breach
```

### 3. Create a Python Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

On Windows:

```bash
venv\Scripts\activate
```

On Linux or macOS:

```bash
source venv/bin/activate
```

### 5. Install Dependencies

Once `requirements.txt` has been added:

```bash
pip install -r requirements.txt
```

### 6. Start the Platform

If the project uses Flask:

```bash
python platform/app.py
```

If the project uses Docker Compose:

```bash
docker compose up --build
```

### 7. Access the Platform

Open the configured local platform address in a browser:

```text
http://localhost:5000
```

The actual port and startup commands may change depending on the final implementation.

## Team Roles and Responsibilities

| Team Member | Responsibility | Main Contribution |
|---|---|---|
| Member 1 | CTF Platform and Architecture | Platform design, deployment, environment configuration, and infrastructure. |
| Member 2 | Challenge Design A | Digital Forensics, Steganography, and Cryptography challenges. |
| Member 3 | Challenge Design B | Web Security, Networking, and Linux Security challenges. |
| Member 4 | Integration, Testing, and Documentation | Testing strategy, validation, risk assessment, and documentation. |

All team members contribute to integration, review, and final project delivery.

## Security Controls

This project must be deployed only in an isolated educational environment.

Recommended controls include:

- Use fictional company information and fictional user accounts.
- Do not include real passwords, personal data, or production credentials.
- Restrict vulnerable services to a private lab network.
- Disable unnecessary external network access.
- Avoid deploying intentionally vulnerable services on public servers.
- Use restricted accounts for Linux challenges.
- Maintain clean backups and reset procedures.
- Review packet captures to ensure they contain only synthetic traffic.
- Keep organizer solutions and actual flags separate from public documentation.
- Monitor service availability and challenge integrity.

## Challenge Reset and Recovery

| Stage | Recovery Method |
|---|---|
| EC-01 | Restore the original email evidence file. |
| EC-02 | Restore the prepared image file. |
| EC-03 | Restore or regenerate the encrypted message. |
| EC-04 | Restart or redeploy the web application container. |
| EC-05 | Restore the original synthetic packet capture. |
| EC-06 | Restore a virtual-machine snapshot or rebuild the Linux challenge container. |

## Learning Outcomes

After completing the CTF, participants should be able to:

1. Identify suspicious email characteristics and phishing indicators.
2. Inspect image metadata and extract concealed information.
3. Decode layered messages and apply basic cryptographic techniques.
4. Identify exposed web resources and broken access controls.
5. Analyze network traffic and reconstruct suspicious communications.
6. Investigate Linux systems using standard command-line tools.
7. Correlate evidence across multiple stages of a security incident.
8. Explain how separate vulnerabilities contributed to a broader attack.

## Ethical Use

This project is intended strictly for:

- Academic coursework.
- Authorized cybersecurity training.
- Controlled Capture the Flag exercises.
- Ethical security research within isolated environments.

Do not use the tools or techniques described in this repository against systems without explicit authorization.

## Project Status

**Current phase:** Challenge design and platform planning.

The six-stage scenario, difficulty progression, domain selection, and investigation workflow have been defined. Implementation, testing, and deployment will be completed according to the approved project design.

## Academic Context

This project was developed as part of a cybersecurity coursework assignment requiring:

- A minimum of six cybersecurity challenges.
- Coverage of at least four cybersecurity domains.
- Progressive difficulty from easy to hard.
- A connected investigation scenario.
- Complete stage specifications.
- Documented validation, hints, dependencies, and recovery procedures.

The proposed project includes six stages across six cybersecurity domains.

---

**Operation E Corp Breach**  
*Investigate the incident. Connect the evidence. Recover the flags.*

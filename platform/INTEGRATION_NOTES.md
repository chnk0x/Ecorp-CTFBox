# EC-04 / EC-05 / EC-06 integration notes

All six challenges are now wired into the platform.

What was added/changed:
- app.py            : ec04, ec05, ec06 added to CHALLENGES (requires chain ec03->ec04->ec05->ec06, 150/200/300 pts, hints).
- seed_flags.py     : ec04/05/06 flags added. (Re-run `python seed_flags.py` after any flag change.)
- index.html        : the Stage 4/5/6 cards are now live "play" cards instead of static links.
- artefacts/
    network_capture.pcap      -> EC-05 evidence (download).
    ec04_portal_access.txt     -> EC-04 access card (points players to the live portal).
    ec06_ssh_access.txt        -> EC-06 access card (SSH details).
    company_event.jpg          -> added so EC-02 download works (was missing).

Flags (organizer-only):
    ec04  ECORP{broken_access_control_774}
    ec05  ECORP{exfil_over_http_traced}
    ec06  ECORP{breach_fully_reconstructed}

Two live services EC-04 and EC-06 need running (your Docker containers):
    EC-04 portal :  docker run -d --name ec04 -p 127.0.0.1:8080:8080 -e EC04_FLAG='ECORP{broken_access_control_774}' ec04-portal
    EC-06 linux  :  docker run -d --name ec06 -p 127.0.0.1:2222:22 ec06-linux
The access cards above point players to 127.0.0.1:8080 and 127.0.0.1:2222.

TO ALIGN WITH THE TEAM:
- Stage 3 decodes to portal "http://portal.ecorp.local/login". Either map that
  name to 127.0.0.1:8080, or update the EC-03 plaintext to the real portal URL,
  so there is no broken link in the chain.

## UPDATE: portal URL fixed
EC-03's attacker_message.txt was regenerated so it now decodes to
"Portal: http://127.0.0.1:8080" (matches the EC-04 container). The EC-03
flag is unchanged. If your team hosts the portal elsewhere, re-generate
EC-03 (Member 2's generate_message.py) with that address, or edit the
EC-04 access card.

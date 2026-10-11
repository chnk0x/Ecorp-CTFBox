#!/bin/bash
# Copy each stage's player-facing file into the platform, so every stage
# folder stays the single source of truth. Run after changing any stage.
set -e
cd "$(dirname "$0")"
A=platform/artefacts
cp stage01_forensics/public/suspicious_email.eml   $A/
cp stage02_stego/public/company_event.jpg          $A/
cp stage03_crypto/public/attacker_message.txt      $A/
cp stage05_network/network_capture.pcap            $A/
cp stage05_network/network_capture.pcap            stage04_web/evidence/   # EC-04 hands this out
echo "[OK] artefacts synced into $A (and EC-04 evidence)"

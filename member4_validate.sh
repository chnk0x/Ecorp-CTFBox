#!/bin/bash

echo "============================================"
echo "E Corp CTF - Member 4 Integration Validation"
echo "============================================"
echo "Date: $(date)"
echo

PASS=0
FAIL=0

check_pass() {
    echo "[PASS] $1"
    PASS=$((PASS + 1))
}

check_fail() {
    echo "[FAIL] $1"
    FAIL=$((FAIL + 1))
}

echo "1. Docker services"
echo "------------------"

docker compose ps
echo

for service in platform ec04 ec06
do
    if docker compose ps --status running --services | grep -qx "$service"; then
        check_pass "$service container is running"
    else
        check_fail "$service container is not running"
    fi
done

echo
echo "2. CTF Platform"
echo "---------------"

if curl -fsS http://127.0.0.1:5001/ > /dev/null; then
    check_pass "CTF platform reachable on port 5001"
else
    check_fail "CTF platform unavailable on port 5001"
fi

echo
echo "3. EC-04 Web Challenge"
echo "----------------------"

if curl -fsS http://127.0.0.1:8081/ > /dev/null; then
    check_pass "EC-04 portal reachable on port 8081"
else
    check_fail "EC-04 portal unavailable"
fi

if curl -fsS http://127.0.0.1:8081/robots.txt > /dev/null; then
    check_pass "EC-04 robots.txt is accessible"
else
    check_fail "EC-04 robots.txt is unavailable"
fi

echo
echo "4. EC-06 SSH"
echo "-------------"

if nc -z 127.0.0.1 2223; then
    check_pass "EC-06 SSH port 2223 is reachable"
else
    check_fail "EC-06 SSH port 2223 is unavailable"
fi

echo
echo "5. Public Challenge Artefacts"
echo "-----------------------------"

FILES=(
    "stage01_forensics/public/suspicious_email.eml"
    "stage02_stego/public/company_event.jpg"
    "stage03_crypto/public/attacker_message.txt"
    "stage05_network/network_capture.pcap"
)

for file in "${FILES[@]}"
do
    if [ -f "$file" ]; then
        check_pass "$file exists"
    else
        check_fail "$file is missing"
    fi
done

echo
echo "============================================"
echo "Validation Summary"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "============================================"

if [ "$FAIL" -eq 0 ]; then
    exit 0
else
    exit 1
fi

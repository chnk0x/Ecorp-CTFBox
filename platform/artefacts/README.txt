Challenge artefacts go here. They are NOT web-reachable: the only way to fetch
one is /api/download/<stage>, which refuses unless the player has unlocked
that stage.

Copy all three from your built ecorp-ctf box:

    cp ../ecorp-ctf/ec01/public/suspicious_email.eml  .
    cp ../ecorp-ctf/ec02/public/company_event.jpg     .
    cp ../ecorp-ctf/ec03/public/attacker_message.txt  .

company_event.jpg MUST be the one produced by ecorp-ctf/build.sh. Any other
JPEG has no embedded payload and EC-02 becomes unsolvable.

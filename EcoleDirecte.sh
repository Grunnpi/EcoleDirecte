#!/bin/bash
echo "Lancement EcoleDirecte.py"

# Lecture du fichier config
CONFIG_FILE="/config/my_scripts/EcoleDirecte/config.txt"
while read -r line; do
    [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
    key="${line%%=*}"
    value="${line#*=}"
    declare "$key=$value"
done < "$CONFIG_FILE"

python3 /config/my_scripts/EcoleDirecte/EcoleDirecte.py \
    --user="$user" \
    --pwd="$pwd" \
    --cred="/config/my_scripts/AuPair.json" \
    --telegram=yes \
    --token="$token" \
    --chatid=-339490946 \
    > /config/my_scripts/EcoleDirecte/EcoleDirecte.log 2>&1 &
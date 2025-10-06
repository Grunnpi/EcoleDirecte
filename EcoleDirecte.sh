#!/bin/bash
echo "Lancement EcoleDirecte.py"
#echo "$(ls)"
python3 /config/my_scripts/EcoleDirecte/EcoleDirecte.py --user=Grunnagel --pwd=mdpspc1978+1976=4 --cred="/config/my_scripts/AuPair.json" --telegram=yes --token=714930347:AAHDNpKK24k7TwzRE4DW60zYgH4G0qqsR8Y --chatid=-339490946 > /config/my_scripts/EcoleDirecte/EcoleDirecte.log 2>&1 &
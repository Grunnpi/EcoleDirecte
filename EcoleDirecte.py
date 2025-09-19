import requests
import json
import os
import argparse
import csv
import os.path
import urllib.parse
import sys
import logging
import http.client as http_client
from http.client import HTTPConnection


from requests.packages.urllib3.exceptions import InsecureRequestWarning

import telegram

import gspread
from oauth2client.service_account import ServiceAccountCredentials

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


EcoleDirectVersion = 'v5.1'


readFile = False #bypass direct api fetch
readFile_fichierJsonEleve = 'c://apps/2025-06-24-NotesXXX.json'
readFileJson_EleveFake = {
    "data": {
        "accounts": [
            {
                "profile": {
                    "eleves": [
                        {
                            "id": 1,
                            "prenom": "XXX"
                        }
                    ]
                }
            }
        ]
    },
    'token': "fakeToken"
}


ecoleDirecteVersion="4.82.2"

proxies = {}
sep = ","


class UnEnfant:
    "Notes"
    prenom = ''
    onglet = ''

    def __init__(self):
        self.prenom = ''
    def __eq__(self, other):
        """Comparaison de deux au pair"""
        return self.prenom == other.prenom
    def toString(self, sep):
        """Format du dump fichier"""
        return self.prenom \
               + sep + self.onglet

class UneNote:
    "Notes"
    periode = ''
    libelleMatiere = ''
    valeur = ''
    noteSur = ''
    coef = ''
    typeDevoir = ''
    devoir = ''
    date = ''
    nonSignificatif = False
    def __init__(self, periode, libelleMatiere,valeur,noteSur,coef,typeDevoir,devoir,date,nonSignificatif):
        self.periode = periode
        self.libelleMatiere = libelleMatiere
        self.valeur = valeur
        self.noteSur = noteSur
        self.coef = coef
        self.typeDevoir = typeDevoir
        self.devoir = devoir
        self.date = date
        self.nonSignificatif = nonSignificatif
    def __eq__(self, other):
        """Comparaison de deux notes"""
        return self.periode == other.periode \
               and self.libelleMatiere == other.libelleMatiere \
               and str(self.devoir) == str(other.devoir) \
               and self.date == other.date
    def __lt__(self, other):
        """Trie de deux notes"""
        if self.periode == other.periode:
            if self.libelleMatiere == other.libelleMatiere:
                if self.date == other.date:
                    if ( str(self.valeur).isnumeric() and str(other.valeur).isnumeric() ):
                        return self.valeur < other.valeur
                    else:
                        return -1
                else:
                    return self.date < other.date
            else:
                return self.libelleMatiere < other.libelleMatiere
        else:
            return self.periode < other.periode
    def toString(self, sep):
        """Format du dump fichier"""
        return self.periode \
               + sep + self.libelleMatiere \
               + sep + self.valeur \
               + sep + self.noteSur \
               + sep + self.coef \
               + sep + self.typeDevoir \
               + sep + self.devoir \
               + sep + self.date

def func(self):
        print('Hello')

def dump( champ, bulletProof ):
    returnMe = ""
    if ( bulletProof ):
        returnMe = repr(str(champ.encode('utf8')))[2:-1]
    else:
        returnMe = "'" + str(champ) + "'"
    returnMe = returnMe.replace("'", "\"")
    return returnMe

def listeNoteGoogle(sheetOnglet):
    all_kid_notes = []
    all_kid_notes_sheet = sheetOnglet.get_all_records()
    #
    for rec in all_kid_notes_sheet:
        uneNote = UneNote('', '', '', '', '', '', '', '','')
        for item in rec.items():
            # print(item[0], " -- ", item[1], "<", item, ">",)
            if ( item[0] == 'periode'):
                uneNote.periode = item[1]
            if ( item[0] == 'libelleMatiere'):
                uneNote.libelleMatiere = item[1]
            if ( item[0] == 'valeur'):
                uneNote.valeur = item[1]
            if ( item[0] == 'noteSur'):
                uneNote.noteSur = item[1]
            if ( item[0] == 'coef'):
                uneNote.coef = item[1]
            if ( item[0] == 'typeDevoir'):
                uneNote.typeDevoir = item[1]
            if ( item[0] == 'devoir'):
                uneNote.devoir = item[1]
            if ( item[0] == 'date'):
                uneNote.date = item[1]
        all_kid_notes.append(uneNote)

    all_kid_notes = sorted(all_kid_notes)
    return all_kid_notes

# fonction pour lister toutes les notes d'un eleve sur base de son ID
def listeNoteSite(eleve_id, token):
    all_kid_notes = []

    if readFile:
        with open(readFile_fichierJsonEleve, 'r', encoding='utf-8') as fichier:
            # Charge le contenu du fichier dans une variable
            notesEnJSON = json.load(fichier)
    else:
        payloadNotes = "data={\"anneeScolaire\": \"\"}"
        headersNotes = {'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1', 'content-type': 'application/x-www-form-urlencoded','X-Token':token}
        r = requests.post("https://api.ecoledirecte.com/v3/eleves/" + str(eleve_id) + "/notes.awp?verbe=get&v=" + ecoleDirecteVersion,
                          data=payloadNotes, headers=headersNotes, proxies=proxies, verify=False)
        if r.status_code != 200:
            print(r.status_code, r.reason)
        notesEnJSON = json.loads(r.content)
    print(notesEnJSON)
    if len(notesEnJSON['data']['notes']) > 0:
        for note in notesEnJSON['data']['notes']:
            uneNote = UneNote( \
                    note['codePeriode'] \
                ,   note['libelleMatiere'] \
                ,   note['valeur'].replace(".", ",") \
                ,   note['noteSur'] \
                ,   note['coef'].replace(".", ",") \
                ,   note['typeDevoir'] \
                ,   note['devoir'] \
                ,   note['date'] \
                ,   note['nonSignificatif'] \
                )
            all_kid_notes.append(uneNote)
        all_kid_notes = sorted(all_kid_notes)
    else:
        print("pas de notes encore")
    return all_kid_notes


# partie principale
if __name__ == "__main__":

    parser=argparse.ArgumentParser(description='Ecole Direct extact process')

    # Ecole Directe cred
    parser.add_argument('--user', help='ED User', type=str, required=True)
    parser.add_argument('--pwd', help='ED Password', type=str, required=True)
    parser.add_argument('--proxy', help='Proxy if behind firewall : https://uzer:pwd@name:port', type=str, default="")
    # credential google
    parser.add_argument('--cred', help='Google Drive json credential file', type=str, required=True)
    # telegram mode
    parser.add_argument('--token', help='Telegram bot token', type=str, default="")
    parser.add_argument('--chatid', help='Telegram chatid', type=str, default="")
    parser.add_argument('--telegram', help='Telegram flag (use or not)', type=str, default="no")

    #parser.print_help()

    args=parser.parse_args()

    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(str(args.cred), scope)
    client = gspread.authorize(creds)

    # collect all kids and related setup
    notes_ConfigurationSheet = client.open("Notes_EcoleDirecte").worksheet("Configuration")
    list_configuration = notes_ConfigurationSheet.get_all_records()
    listeEnfants = []
    for rec in list_configuration:
        unEnfant = UnEnfant()
        for item in rec.items():
            if ( item[0] == 'Prénom'):
                unEnfant.prenom = item[1]
                print(item[1])
            if ( item[0] == 'Onglet'):
                unEnfant.onglet = item[1]
                print(item[1])
        listeEnfants.append(unEnfant)

    print("**** sboub")

    if args.proxy:
        print("Proxy provided")
        proxies = {
            "https": str(args.proxy)
        }


    http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    #requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
    HTTPConnection.debuglevel = 1


    if readFile:
        retourEnJson = readFileJson_EleveFake
    else:
        headers = {'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1', 'content-type': 'application/x-www-form-urlencoded', 'Accept':'application/json, text/plain, */*', 'Origin':'https://www.ecoledirecte.com', 'Referer':'https://www.ecoledirecte.com/'}

        mySession = requests.Session()

        r = mySession.get("https://api.ecoledirecte.com/v3/login.awp?gtk=1&v=" + ecoleDirecteVersion, headers=headers, proxies=proxies, verify=False)
        if r.status_code != 200:
            print(r.status_code, r.reason)

        print("GTK", mySession.cookies.get("GTK"))

        new_header =  {
            "X-GTK": mySession.cookies.get("GTK")
        }
        headers.update(new_header)


    #    headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
        payload = "data={ \"identifiant\": \"" + str(args.user) + "\", \"motdepasse\" : \"" + urllib.parse.quote(str(args.pwd),safe="=") + "\", \"isReLogin\": false, \"uuid\":\"\", \"fa\" : [{ \"cn\":\"ED_UExVTUVfMDU3MjkzMUJfMV8xODkw\", \"cv\": \"Njc2NzM1NTc3NTQ3NGM0ZDUwNmM0MTQ2NTUyYjMwNmU0ODcwNjg2YTZjMzI0MjQ1N2EyZjQzNTk=\" }] }"
    #    payload = 'data={"uuid": "", "identifiant": "hardcodeme", "motdepasse": "hardcodedstuff", "isReLogin": false }'
        print("*X***********************")
        print(payload)
        print("*XX***********************")

        r = mySession.post("https://api.ecoledirecte.com/v3/login.awp?v=" + ecoleDirecteVersion, data=payload, headers=headers, proxies=proxies, verify=False)
        if r.status_code != 200:
            print(r.status_code, r.reason)
        print("************************")
        print(r.content)
        retourEnJson = json.loads(r.content)
        print(retourEnJson['code'])
        if ( retourEnJson['code']!=200):
            print(">>>>>>>>>>> Error / stop ")
            exit(-1)
    print("Generation des fichiers ici : [" + os.getcwd() + "]")

    telegram_message = "*EcoleDirect(" + EcoleDirectVersion + ")* "
    compteurTotalNouvelleNote = 0
    for eleve in retourEnJson['data']['accounts'][0]['profile']['eleves']:
        eleveId = str(eleve['id'])
        elevePrenom = str(eleve['prenom'])
        print("Eleve(" + eleveId + ")[" + elevePrenom + "]")
        trouveEleve = False
        nbCreate = 0
        erreurApiMax = False
        for x in listeEnfants:
            if x.prenom == elevePrenom:
                print(">> Eleve config trouvé : ", x.onglet)
                trouveEleve = True
                print(">>> Extract Google")

                sheet_ongleNotes = client.open("Notes_EcoleDirecte").worksheet(x.onglet)
                eleveNotesDansGoogle = listeNoteGoogle(sheet_ongleNotes)
                print(">>> Extract Site")
                eleveNotesDansSite = listeNoteSite(eleveId, retourEnJson['token'])

                print("Notes dans google[", len(eleveNotesDansGoogle), "] / notes sur site [", len(eleveNotesDansSite), "]")
                googleNextRow = len(eleveNotesDansGoogle) + 2 # header + new row

                inventaireNote = ""
                for uneNoteSite in eleveNotesDansSite:
                    isNoteSiteDejaSurGoogle = False
                    for uneNoteGoogle in eleveNotesDansGoogle:
                        if ( uneNoteSite == uneNoteGoogle ):
                            isNoteSiteDejaSurGoogle = True
                            break
                    if ( not isNoteSiteDejaSurGoogle ):
                        print("Ajoute %s" % uneNoteSite.valeur, " @ ligne %d" % googleNextRow)
                        theValeur = uneNoteSite.valeur
                        if ( uneNoteSite.valeur.replace(",", ".").isnumeric()):
                            theValeur = float(theValeur.replace(",", "."))
                        theNoteSur = uneNoteSite.noteSur
                        if ( uneNoteSite.noteSur.replace(",", ".").isnumeric()):
                            theNoteSur = float(theNoteSur.replace(",", "."))
                        theCoef = uneNoteSite.coef
                        if ( uneNoteSite.coef.replace(",", ".").isnumeric()):
                            theCoef = float(theCoef.replace(",", "."))

                        VRAI_NOTE = 'TRUE'
                        if ( uneNoteSite.nonSignificatif == True ):
                            VRAI_NOTE = 'FALSE'

                        row = [uneNoteSite.periode, uneNoteSite.libelleMatiere, theValeur, theNoteSur, theCoef, uneNoteSite.typeDevoir, uneNoteSite.devoir, uneNoteSite.date, '=SI(ESTNUM(C' + str(googleNextRow) + ');C' + str(googleNextRow) + '/D' + str(googleNextRow) + '*20;NA())', '=I' + str(googleNextRow) + '*E' + str(googleNextRow) + '', '=SI(ESTNUM(I' + str(googleNextRow) + ');ET(VRAI;M' + str(googleNextRow) + ');FAUX)', '=GAUCHE(A' + str(googleNextRow) + ';4)',VRAI_NOTE]
                        try:
                            sheet_ongleNotes.insert_row(row, googleNextRow, 'USER_ENTERED')
                        except gspread.exceptions.APIError as argh:
                            print("Maximum d'ajout pour Google sheet - relancer dans 2 min")
                            print("api error : ", argh, file=sys.stderr)
                            inventaireNote = inventaireNote + "\n__api.error.max__"
                            erreurApiMax = True
                            break

                        inventaireNote = inventaireNote + "\n " + uneNoteSite.libelleMatiere.lower() + " " + str(theValeur) + "/" + str(theNoteSur) + " (" + str(theCoef) + ")"
                        if ( uneNoteSite.nonSignificatif == True ):
                            inventaireNote = inventaireNote + "_ns_"

                        googleNextRow = googleNextRow + 1
                        nbCreate = nbCreate + 1
                    else:
                        print("Note %s" % uneNoteSite.valeur, " @ déjà présente")
                print("Nombre de notes ajoutées pour ",elevePrenom," = ", nbCreate)
                telegram_message = telegram_message + "\n *"  + elevePrenom + "* :`" + str(nbCreate) + "`"
                if ( (nbCreate > 0) or (erreurApiMax) ):
                    telegram_message = telegram_message + inventaireNote
                break
        if ( not trouveEleve ):
            print(">> Eleve config non trouvé !!")
    print("Fin extraction.\nTotal nouvelles notes=" + str(compteurTotalNouvelleNote))

    if ( str(args.telegram) == "yes" ) :
        bot = telegram.Bot(token=str(args.token))
        bot.send_message(chat_id=str(args.chatid), text=telegram_message, parse_mode=telegram.ParseMode.MARKDOWN)


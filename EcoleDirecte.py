import requests
import json
import os
import argparse
import csv
import os.path

proxies = {}

sep = ","

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
    def __init__(self, periode, libelleMatiere,valeur,noteSur,coef,typeDevoir,devoir,date):
        self.periode = periode
        self.libelleMatiere = libelleMatiere
        self.valeur = valeur
        self.noteSur = noteSur
        self.coef = coef
        self.typeDevoir = typeDevoir
        self.devoir = devoir
        self.date = date
    def __eq__(self, other):
        """Comparaison de deux notes"""
        return self.periode == other.periode \
               and self.libelleMatiere == other.libelleMatiere \
               and self.devoir == other.devoir \
               and self.date == other.date
    def __lt__(self, other):
        """Trie de deux notes"""
        if self.periode == other.periode:
            if self.libelleMatiere == other.libelleMatiere:
                if self.date == other.date:
                    return self.valeur < other.valeur
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

# fonction pour lister toutes les notes d'un eleve sur base de son ID
def listeNote(eleve_id, eleve_prenom, token):
    payloadNotes = "data={\"token\": \"" + token + "\"}"
    headersNotes = {'content-type': 'application/x-www-form-urlencoded'}

    r = requests.post("https://vmws17.ecoledirecte.com/v3/eleves/" + str(eleve_id) + "/notes.awp?verbe=get&",
                      data=payloadNotes, headers=headersNotes, proxies=proxies, verify=False)
    if r.status_code != 200:
        print(r.status_code, r.reason)
    # print(r.content)

    compteurNote = 0
    compteurNouvelleNote = 0

    notesEnJSON = json.loads(r.content)
    if len(notesEnJSON['data']['notes']) > 0:
        nomDuFichier = eleve_prenom + '.csv'

        notesSite = []
        notesFichier = []
        for note in notesEnJSON['data']['notes']:
            uneNote = UneNote( \
                    dump(note['codePeriode'], False) \
                ,   dump(note['libelleMatiere'], True) \
                ,   dump(note['valeur'].replace(",", "."), False) \
                ,   dump(note['noteSur'], True) \
                ,   dump(note['coef'], True) \
                ,   dump(note['typeDevoir'], False) \
                ,   dump(note['devoir'], False) \
                ,   dump(note['date'], True) \
                )
            notesSite.append(uneNote)

        nouveauFichier = True
        if ( os.path.isfile(nomDuFichier) ):
            nouveauFichier = False
            # lire les notes déjà presente si existe
            line_count = 0
            with open(nomDuFichier) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=sep)
                for row in csv_reader:
                    if line_count == 0:
                        #print(f'Column names are {", ".join(row)}')
                        line_count += 1
                    else:
                        #print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                        uneNote = UneNote( \
                            dump(row[0], False) \
                            ,   dump(row[1], True) \
                            ,   dump(row[2], False) \
                            ,   dump(row[3], True) \
                            ,   dump(row[4], True) \
                            ,   dump(row[5], False) \
                            ,   dump(row[6], False) \
                            ,   dump(row[7], True) \
                            )
                        notesFichier.append(uneNote)
                        line_count += 1

        notesSite = sorted(notesSite)
        notesFichier = sorted(notesFichier)

        with open(nomDuFichier, "a") as n:
            if ( nouveauFichier ):
            # header du fichier
                n.write(
                    'periode'
                    + sep + 'libelleMatiere'
                    + sep + 'valeur'
                    + sep + 'noteSur'
                    + sep + 'coef'
                    + sep + 'typeDevoir'
                    + sep + 'devoir'
                    + sep + 'date'
                    + "\n"
                )
            for note in notesSite:
                compteurNote = compteurNote + 1
                nouvelleNote = True
                for ancienneNote in notesFichier:
                    if ( note == ancienneNote ):
                        nouvelleNote = False
                        break
                if ( nouvelleNote ):
                    n.write( note.toString(sep) + "\n" )
                    compteurNouvelleNote = compteurNouvelleNote + 1

            print('[' + str(compteurNouvelleNote) + '] nouvelles notes, pour un total de [' + str(compteurNote) + '] notes')
    else:
        print("pas de notes encore")
    return compteurNouvelleNote


# partie principale
if __name__ == "__main__":

    parser=argparse.ArgumentParser()

    parser.add_argument('--user', help='User', type=str)
    parser.add_argument('--pwd', help='Password', type=str)
    parser.add_argument('--proxy', help='https://uzer:pwd@name:port', type=str, default="")
    args=parser.parse_args()

    #print(args.user)
    #print(args.pwd)
    #print(args.proxy)

    if args.proxy:
        print("Proxy provided")
        proxies = {
            "https": str(args.proxy)
        }

    payload = "data={\"identifiant\": \"" + str(args.user) + "\", \"motdepasse\" : \"" + str(args.pwd) + "\"}"
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    #print(payload)

    r = requests.post("https://vmws06.ecoledirecte.com/v3/login.awp", data=payload, headers=headers, proxies=proxies, verify=False)
    if r.status_code != 200:
        print(r.status_code, r.reason)
    retourEnJson = json.loads(r.content)
    print("Generation des fichiers ici : [" + os.getcwd() + "]")

    compteurTotalNouvelleNote = 0
    for eleve in retourEnJson['data']['accounts'][0]['profile']['eleves']:
        eleveId = str(eleve['id'])
        elevePrenom = str(eleve['prenom'])
        print("Eleve(" + eleveId + ")[" + elevePrenom + "]")
        compteurTotalNouvelleNote = compteurTotalNouvelleNote + listeNote(eleveId, elevePrenom, retourEnJson['token'])

    print("Fin extraction.\nTotal nouvelles notes=" + str(compteurTotalNouvelleNote))

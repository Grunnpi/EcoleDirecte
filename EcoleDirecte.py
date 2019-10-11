import requests
import json
import os
import argparse

proxies = {}

# fonction pour lister toutes les notes d'un eleve sur base de son ID
def listeNote(eleve_id, eleve_prenom, token):
    payloadNotes = "data={\"token\": \"" + token + "\"}"
    headersNotes = {'content-type': 'application/x-www-form-urlencoded'}

    r = requests.post("https://vmws17.ecoledirecte.com/v3/eleves/" + str(eleve_id) + "/notes.awp?verbe=get&",
                      data=payloadNotes, headers=headersNotes, proxies=proxies, verify=False)
    if r.status_code != 200:
        print(r.status_code, r.reason)
    # print(r.content)

    notesEnJSON = json.loads(r.content)
    if len(notesEnJSON['data']['notes']) > 0:
        for note in notesEnJSON['data']['notes']:
            nomDuFichier = eleve_prenom + '-' + note['codePeriode'] + '.csv'
            with open(nomDuFichier, "a") as n:
                n.write(str(note['libelleMatiere'].encode('utf8')) + ";" + str(note['date'].encode('utf8')) + ";" + str(
                    note['valeur'].encode('utf8')) + ";" + str(note['noteSur'].encode('utf8')) + ";" + str(
                    note['coef'].encode('utf8')) + ";" + str(note['typeDevoir'].encode('utf8')) + ";" + str(
                    note['devoir'].encode('utf8')) + "\n")
    else:
        print("pas de notes encore")
    return


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

    for eleve in retourEnJson['data']['accounts'][0]['profile']['eleves']:
        eleveId = str(eleve['id'])
        elevePrenom = str(eleve['prenom'])
        print("Eleve(" + eleveId + ")[" + elevePrenom + "]")
        listeNote(eleveId, elevePrenom, retourEnJson['token'])

    print("Fin extraction")

import socket

# Client POP3 simplifié avec menu interactif
def pop3_client():
    serveur = ("127.0.0.1", 1100)

    utilisateur = input("Adresse e-mail POP3 : ").strip()
    motdepasse = input("Mot de passe POP3 : ").strip()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(serveur)

        # Lecture ligne par ligne
        f = s.makefile("r", encoding="utf-8", newline="\r\n")

        # Lire une ligne (réponse simple)
        def lire_ligne():
            ligne = f.readline()
            if ligne == "":
                return ""
            return ligne.rstrip("\r\n")

        # Lire une réponse multi-lignes (se termine par ".")
        def lire_multiligne():
            lignes = []
            while True:
                ligne = f.readline() # Lire jusqu'à \r\n
                if ligne == "": # Connexion fermée 
                    break
                ligne = ligne.rstrip("\r\n") # Enlever fin de ligne : \r\n
                if ligne == ".":   # Fin de la réponse
                    break
                lignes.append(ligne)
            return lignes

        # Envoyer une commande
        def envoyer(cmd):
            s.sendall((cmd + "\r\n").encode("utf-8")) # Envoyer avec \r\n

        # Vérifier réponse +OK / -ERR
        def ok(reponse):
            return reponse.startswith("+OK")

        # Extraire l'objet d'un message à partir de quelques lignes (TOP)
        def recuperer_objet(message_id):
            # On demande les 30 premières lignes (suffisant pour trouver "Objet:")
            envoyer("TOP " + str(message_id) + " 30")

            rep = lire_ligne()
            if not ok(rep): # si erreur
                return "(objet indisponible)"

            lignes = lire_multiligne()

            # Chercher "Objet:" (ou "Subject:" si jamais)
            for l in lignes:
                l_strip = l.strip() # enlever espaces
                if l_strip.lower().startswith("objet:"): # chercher "Objet:"
                    return l_strip[6:].strip() # retourner le reste
                if l_strip.lower().startswith("subject:"): # chercher "Subject:"
                    return l_strip[8:].strip() # retourner le reste

            return "(sans objet)" # si pas trouvé

        # Connexion + Auth
        rep = lire_ligne() 
        if rep != "": 
            print(rep)

        envoyer("USER " + utilisateur) # Envoyer USER
        rep = lire_ligne()
        if not ok(rep):
            print("Erreur USER :", rep)
            return

        envoyer("PASS " + motdepasse) # Envoyer PASS
        rep = lire_ligne()
        if not ok(rep):
            print("Erreur PASS :", rep)
            return

        print("Authentification OK.\n")

        # Menu utilisateur
        while True:
            print("=== MENU POP3 ===")
            print("1 - STAT (etat de la boite)")
            print("2 - LIST (liste des messages + objet)")
            print("3 - RETR (lire un message complet)")
            print("4 - TOP (voir debut d'un message)")
            print("5 - UIDL (identifiants uniques)")
            print("6 - CAPA (capacites serveur)")
            print("7 - QUIT (quitter)")
            choix = input("Choix : ").strip()
            print("\n")

            # STAT 
            if choix == "1":
                envoyer("STAT")
                rep = lire_ligne() # Lire réponse
                print(rep)
                print()

            # LIST + Objet 
            elif choix == "2":
                envoyer("LIST")
                rep = lire_ligne() # Lire réponse
                if not ok(rep):
                    print(rep)
                    print()
                    continue

                lignes = lire_multiligne()

                if len(lignes) == 0:
                    print("(Aucun message)")
                    print()
                    continue

                print("ID | Taille | Objet")
                print("---------------------------")

                # lignes : "1 73", "2 86", etc.
                for l in lignes: 
                    morceaux = l.split() # Séparer par espace
                    if len(morceaux) >= 2: 
                        mid = morceaux[0]
                        taille = morceaux[1]
                        sujet = recuperer_objet(mid)
                        print(mid + "  | " + taille + "     | " + sujet) # Afficher

                print()

            # RETR : lire message complet
            elif choix == "3":
                mid = input("Numero du message : ").strip()
                envoyer("RETR " + mid) # Envoyer RETR
                rep = lire_ligne() # Lire réponse
                print(rep)
                if ok(rep): # si OK
                    lignes = lire_multiligne()
                    print("----- MESSAGE " + mid + " -----")
                    for l in lignes:
                        print(l)
                    print("-------------------------")
                print()

            # TOP : voir debut message
            elif choix == "4":
                mid = input("Numero du message : ").strip()
                k = input("Nombre de lignes a afficher : ").strip()
                if k == "": # valeur par defaut
                    k = "20" # afficher 20 lignes
                envoyer("TOP " + mid + " " + k)
                rep = lire_ligne()
                print(rep)
                if ok(rep):
                    lignes = lire_multiligne()
                    for l in lignes:
                        print(l)
                print()

            # UIDL : identifiants uniques
            elif choix == "5":
                envoyer("UIDL")
                rep = lire_ligne()
                print(rep)
                if ok(rep):
                    lignes = lire_multiligne()
                    for l in lignes:
                        print(l)
                print()

            # CAPA : capacites serveur
            elif choix == "6":
                envoyer("CAPA")
                rep = lire_ligne()
                print(rep)
                if ok(rep):
                    lignes = lire_multiligne()
                    for l in lignes:
                        print(l)
                print()

            # QUIT
            elif choix == "7":
                envoyer("QUIT")
                rep = lire_ligne()
                print(rep)
                break

            else:
                print("Choix invalide.\n")


if __name__ == "__main__":
    pop3_client()

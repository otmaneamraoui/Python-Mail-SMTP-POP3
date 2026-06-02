import socket   # Module socket : communication réseau en TCP
import os       # Module os : gestion des fichiers et dossiers



# Chargement des utilisateurs depuis un fichier texte
USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "users.txt")
# Fonction : charger les utilisateurs et mots de passe
def charger_utilisateurs():
    utilisateurs = {}
    # Si le fichier users.txt n'existe pas, on retourne une liste vide
    if not os.path.exists(USERS_FILE):
        return utilisateurs
    # Lecture du fichier users.txt
    f = open(USERS_FILE, "r", encoding="utf-8")
    for ligne in f:
        ligne = ligne.strip()
        if ligne == "" or ":" not in ligne:
            continue
        user, pwd = ligne.split(":", 1)
        utilisateurs[user] = pwd
    f.close()

    return utilisateurs


# Chemin du dossier contenant les boîtes mail
# (le même dossier utilisé par le serveur SMTP)
MAILBOX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mailboxes")

# Séparateur utilisé par le serveur SMTP pour séparer les mails
SEPARATEUR = "----------------------------------------"


# Fonction : découper le contenu d'un fichier mailbox
# en plusieurs messages distincts
def decouper_messages(contenu_fichier):
    # On découpe le contenu à chaque séparateur
    blocs = contenu_fichier.split(SEPARATEUR)

    messages = []

    # On nettoie chaque bloc
    for bloc in blocs:
        # Supprime les espaces et retours à la ligne inutiles
        bloc_nettoye = bloc.strip()

        # On garde uniquement les blocs non vides
        if bloc_nettoye != "":
            messages.append(bloc_nettoye)

    # On retourne la liste des messages
    return messages


# Fonction : charger une mailbox depuis le disque
def charger_mailbox(nom_mailbox):
    # Construire le chemin du fichier mailbox
    chemin = os.path.join(MAILBOX_DIR, nom_mailbox + ".txt")

    # Si le dossier mailboxes n'existe pas, il n'y a aucun mail
    if not os.path.exists(MAILBOX_DIR):
        return []

    # Si le fichier mailbox n'existe pas, aucun message
    if not os.path.exists(chemin):
        return []

    # Ouvrir le fichier en lecture
    fichier = open(chemin, "r", encoding="utf-8")

    # Lire tout le contenu du fichier
    contenu = fichier.read()

    # Fermer le fichier
    fichier.close()

    # Découper le contenu en messages
    return decouper_messages(contenu)


# Fonction : calculer la taille d'un message
# (approximative, suffisante pour POP3)
def taille_message(message):
    # Conversion en UTF-8 puis comptage des octets
    return len(message.encode("utf-8"))


# Fonction utilitaire : envoyer une ligne POP3
# Ajoute automatiquement \r\n
def envoyer_ligne(service, ligne):
    service.sendall((ligne + "\r\n").encode("utf-8"))


# Fonction principale : gestion d'un client POP3
def gerer_client(service):

    # Gestion de l'authentification POP3
    utilisateurs = charger_utilisateurs()
    auth_ok = False
    utilisateur_courant = ""

    # Message d'accueil POP3 (obligatoire)
    envoyer_ligne(service, "+OK Serveur POP3 pret")

    # Tampon pour recevoir les données ligne par ligne
    tampon = ""

    # Boucle principale de la session POP3
    while True:
        # Réception de données depuis le client
        try:
            data = service.recv(1024)
        except ConnectionResetError:
            print("Client a ferme la connexion brutalement.")
            return


        # Si aucune donnée reçue, le client a fermé la connexion
        if not data:
            break

        # Ajout des données reçues dans le tampon
        tampon += data.decode("utf-8", errors="replace")

        # Tant qu'il y a une ligne complète à traiter
        while "\n" in tampon:
            ligne, tampon = tampon.split("\n", 1)

            # Nettoyer la ligne
            commande = ligne.strip()

            # Ignorer les lignes vides
            if commande == "":
                continue

            # Affichage côté serveur (debug)
            print("     - POP3 Recu :", commande)

            # Conversion en majuscule pour comparaison
            cmd_up = commande.upper()

            # commande AUTH USER : indiquer l'utilisateur
            if cmd_up.startswith("USER"):
                morceaux = commande.split(maxsplit=1)
                # Vérifier la syntaxe
                if len(morceaux) != 2:
                    envoyer_ligne(service, "-ERR Syntaxe: USER <utilisateur>")
                    continue
                # Extraire le nom d'utilisateur
                utilisateur_courant = morceaux[1]
                # Vérifier si l'utilisateur existe
                if utilisateur_courant in utilisateurs:
                    envoyer_ligne(service, "+OK Utilisateur reconnu")
                else:
                    envoyer_ligne(service, "-ERR Utilisateur inconnu")

                continue

            # commande AUTH PASS : vérifier le mot de passe
            elif cmd_up.startswith("PASS"):
                morceaux = commande.split(maxsplit=1)
                # Vérifier la syntaxe
                if len(morceaux) != 2:
                    envoyer_ligne(service, "-ERR Syntaxe: PASS <motdepasse>")
                    continue
                # Vérifier qu'un utilisateur a été indiqué avant
                if utilisateur_courant == "":
                    envoyer_ligne(service, "-ERR USER requis avant PASS")
                    continue
                # Extraire le mot de passe
                motdepasse = morceaux[1]
                # Vérifier le mot de passe
                if utilisateurs.get(utilisateur_courant) == motdepasse:
                    auth_ok = True

                    # Charger la mailbox de l'utilisateur authentifié
                    messages = charger_mailbox(utilisateur_courant)

                    envoyer_ligne(service, "+OK Authentification reussie")
                else:
                    envoyer_ligne(service, "-ERR Mot de passe incorrect")

                continue

            # Refus des commandes si non authentifié
            if not auth_ok and cmd_up not in ["QUIT", "NOOP", "CAPA"]:
                envoyer_ligne(service, "-ERR Authentification requise")
                continue

            # --- 1 Commande QUIT (pour quitter la session POP3) ---
            if cmd_up == "QUIT":
                envoyer_ligne(service, "+OK Au revoir")
                return

            # --- 2 Commande STAT (connaître l’état de la boîte mail) ---
            elif cmd_up == "STAT":
                # Nombre de messages
                nb = len(messages)

                # Calcul de la taille totale
                total = 0
                for msg in messages:
                    total = total + taille_message(msg)

                # Envoi de la réponse STAT
                envoyer_ligne(service, "+OK " + str(nb) + " " + str(total))

            # --- 3 Commande LIST (obtenir la liste des messages stockés dans la boîte mail) ---
            elif cmd_up == "LIST":
                # Première ligne de réponse
                envoyer_ligne(service, "+OK")

                # Envoi des messages un par un
                index = 1
                for msg in messages:
                    envoyer_ligne(service, str(index) + " " + str(taille_message(msg)))
                    index = index + 1

                # Fin de liste POP3
                envoyer_ligne(service, ".")

            # --- 4 Commande RETR n (obtenir le contenu du message n) ---
            elif cmd_up.startswith("RETR"):
                morceaux = commande.split()

                # Vérifier la syntaxe
                if len(morceaux) != 2:
                    envoyer_ligne(service, "-ERR Syntaxe: RETR n")
                    continue

                # Vérifier que n est un entier
                try:
                    n = int(morceaux[1])
                except:
                    envoyer_ligne(service, "-ERR n invalide")
                    continue

                # Vérifier que le message existe
                if n < 1 or n > len(messages):
                    envoyer_ligne(service, "-ERR Message inexistant")
                    continue

                # Envoi du message demandé
                envoyer_ligne(service, "+OK")

                contenu = messages[n - 1]

                # Envoi ligne par ligne
                for l in contenu.splitlines():
                    envoyer_ligne(service, l)

                # Fin du message
                envoyer_ligne(service, ".")
                
            # --- 5 commande NOOP : ne fait rien, sert juste à tester si le serveur répond ---
            elif cmd_up == "NOOP":
                envoyer_ligne(service, "+OK")

            # --- 6 commande UIDL : identifiant unique des messages ---
            elif cmd_up == "UIDL":
                envoyer_ligne(service, "+OK")

                i = 1
                for msg in messages:
                    uid = str(i) + "_" + str(taille_message(msg))
                    envoyer_ligne(service, str(i) + " " + uid)
                    i = i + 1

                envoyer_ligne(service, ".")

            # --- 7 commande TOP n k : premières lignes du message ---
            elif cmd_up.startswith("TOP"):
                morceaux = commande.split()

                # Vérification syntaxe
                if len(morceaux) != 3:
                    envoyer_ligne(service, "-ERR Syntaxe: TOP n k")
                    continue
                # Vérification que n et k sont des entiers
                try:
                    n = int(morceaux[1])
                    k = int(morceaux[2])
                except:
                    envoyer_ligne(service, "-ERR n et k doivent etre des entiers")
                    continue
                # Vérification que le message existe
                if n < 1 or n > len(messages):
                    envoyer_ligne(service, "-ERR Message inexistant")
                    continue
                # Envoi des k premières lignes du message n
                envoyer_ligne(service, "+OK")
                # Récupération des lignes du message
                lignes = messages[n - 1].splitlines()
                compteur = 0
                # Envoi des lignes une par une
                for l in lignes:
                    if compteur >= k:
                        break
                    envoyer_ligne(service, l)
                    compteur = compteur + 1
                # Fin du message
                envoyer_ligne(service, ".")

            # --- 8 commande CAPA : capacités du serveur ---
            elif cmd_up == "CAPA":
                envoyer_ligne(service, "+OK Capacites du serveur :")
                envoyer_ligne(service, "STAT")
                envoyer_ligne(service, "LIST")
                envoyer_ligne(service, "RETR")
                envoyer_ligne(service, "NOOP")
                envoyer_ligne(service, "TOP")
                envoyer_ligne(service, "UIDL")
                envoyer_ligne(service, ".")

            # Commande inconnue
            else:
                envoyer_ligne(service, "-ERR Commande inconnue")


# Fonction : démarrer le serveur POP3
def demarrer_serveur_pop3():
    # Création de la socket TCP d'écoute
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ecoute:

        # Autoriser la réutilisation rapide du port
        ecoute.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Liaison de la socket au port POP3 (1100)
        ecoute.bind(("", 1100))

        # Mise en écoute
        ecoute.listen()

        print(" -> Serveur POP3 demarre sur le port 1100...")
        print(" -> En attente de connexions...\n")

        # Boucle serveur infinie
        while True:
            # Attente d'un client
            service, adresse = ecoute.accept()
            print("--> Client POP3 connecte :", adresse)

            # Gestion de la session client
            with service:
                gerer_client(service)
                print(" --> Session POP3 terminee.\n")

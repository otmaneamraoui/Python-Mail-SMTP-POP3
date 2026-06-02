import socket   # Pour la communication réseau (sockets)
import os       # Pour créer des dossiers/fichiers locaux


# Dossier où les mails seront sauvegardés
MAILBOX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mailboxes")

# Fonction pour sauvegarder un message dans un fichier
def sauvegarder_mail(expediteur, destinataire, contenu):
    # Crée le dossier des boîtes mail s’il n’existe pas encore
    if not os.path.exists(MAILBOX_DIR):
        os.makedirs(MAILBOX_DIR)

    # On garde uniquement les caractères alphanumériques et certains symboles autorisés
    import re
    destinataire_sain = re.sub(r'[^a-zA-Z0-9@._-]', '', destinataire)
    
    # Le nom du fichier sera le nom du destinataire (ex : otmane.amraoui@univ-tlse3.fr.txt)
    chemin = os.path.join(MAILBOX_DIR, destinataire_sain + ".txt")


    # Ouvre le fichier en mode ajout (append), "a" pour ne pas écraser les mails précédents
    fichier = open(chemin, "a", encoding="utf-8")

    # Écrit les informations du mail dans le fichier
    fichier.write("From: " + expediteur + "\n")
    fichier.write("To: " + destinataire + "\n")
    fichier.write(contenu + "\n")
    fichier.write("----------------------------------------\n")

    # Ferme le fichier après écriture
    fichier.close()

    # Message de confirmation côté serveur
    print("\n -> Mail sauvegardé pour :", destinataire, "\n")

# Fonction principale pour gérer la communication SMTP
def gerer_client(service):
    # Variables pour stocker les informations du mail
    expediteur = ""
    destinataire = ""
    contenu = ""
    data_mode = False   # devient True quand on entre dans la commande DATA

    # Message d’accueil envoyé au client
    service.sendall("220 Serveur SMTP pret\r\n".encode("utf-8"))

    # buffer pour stocker les données reçues
    tampon = ""

    # Boucle principale de communication avec le client
    while True:
        # Attend un message du client (jusqu’à 1024 octets)
        data = service.recv(1024)

        # Si aucune donnée n’est reçue, on quitte la boucle
        if not data:
            break

        # Ajoute les données reçues dans un tampon
        tampon += data.decode("utf-8")

        # Tant qu'on trouve une fin de ligne dans le tampon
        while "\n" in tampon:
            ligne, tampon = tampon.split("\n", 1)
            commande = ligne.strip()
            print("     - Reçu :", commande)
            
            # =============== VERSION 2 : HELO / EHLO ==================
            if commande.upper().startswith("EHLO"):
                service.sendall("502 Command not implemented\r\n".encode("utf-8"))
                continue

            elif commande.upper().startswith("HELO"):
                service.sendall("250 OK HELO\r\n".encode("utf-8"))
                continue

            # 1 --- Commande MAIL FROM ---
            if commande.upper().startswith("MAIL FROM:"):
                # Extrait l’expéditeur entre les <>
                expediteur = commande[10:].strip("<>")
                # Répond au client
                service.sendall("250 OK MAIL FROM\r\n".encode("utf-8"))

            # 2 --- Commande RCPT TO ---
            elif commande.upper().startswith("RCPT TO:"):
                # Extrait le destinataire
                destinataire = commande[8:].strip("<>")
                service.sendall("250 OK RCPT TO\r\n".encode("utf-8"))

            # 3 --- Commande DATA ---
            elif commande.upper() == "DATA":
                # Active le mode DATA "lecture du contenu"
                data_mode = True
                contenu = ""
                # Invite le client à écrire le message
                service.sendall("354 Entrez le message. Terminez par un point seul sur une ligne.\r\n".encode("utf-8"))

            # 4 --- Mode DATA actif (Lecture du corps du message) ---
            elif data_mode:
                # Ajoute la ligne au contenu brut
                contenu += commande + "\n"

                # Si le message se termine par un point seul (fin du mail)
                if commande == ".":
                    data_mode = False
                    # Supprimer le dernier point et la ligne vide
                    contenu = contenu.rstrip(".\n")
                    # Sauvegarder le message
                    sauvegarder_mail(expediteur, destinataire, contenu)
                    # Confirmer la réception
                    service.sendall("250 Message accepte\r\n".encode("utf-8"))


            # --- 5 Commande QUIT ---
            elif commande.upper() == "QUIT":
                # Répond au client puis sort de la boucle
                service.sendall("221 Fermeture de la connexion\r\n".encode("utf-8"))
                return  # On quitte la fonction proprement

            # --- 6 NOOP : ne fait rien, sert juste à tester si le serveur répond ---
            if commande.upper() == "NOOP":
                service.sendall("250 OK\r\n".encode("utf-8"))
                continue

            # --- 7 HELP : affiche les commandes supportées par le serveur ---
            elif commande.upper() == "HELP":
                service.sendall("214 Commandes: HELO, EHLO, MAIL FROM, RCPT TO, DATA, RSET, NOOP, HELP, QUIT\r\n".encode("utf-8"))
                continue

            # --- 8 RSET : réinitialise la transaction mail en cours (annule MAIL/RCPT/DATA) ---
            elif commande.upper() == "RSET":
                expediteur = ""
                destinataire = ""
                contenu = ""
                data_mode = False
                service.sendall("250 OK\r\n".encode("utf-8"))
                continue

            # --- 9 Commande inconnue ---
            else:
                # Réponse d’erreur générique
                service.sendall("500 Commande inconnue\r\n".encode("utf-8"))


    # Fermeture de la communication avec ce client
    service.close()
    print(" --> Connexion terminée avec le client.\n")

# Fonction pour démarrer le serveur SMTP (appelée depuis main)
def demarrer_serveur_smtp():
    # Crée une socket TCP (IPv4 + flux fiable)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ecoute:
        # Lie la socket à l’adresse locale et au port 2525
        ecoute.bind(("", 2525))

        # Met le serveur en mode écoute (attente de connexions)
        ecoute.listen()

        print(" -> Serveur SMTP démarré sur le port 2525...")
        print(" -> En attente de connexions...\n")

        # Boucle infinie pour accepter plusieurs clients à la suite
        while True:
            # Attente d’une demande de connexion
            service, adresse_client = ecoute.accept()

            # Affiche l’adresse du client connecté
            print("--> Client connecté :", adresse_client)

            # Gère la communication avec le client
            with service:
                gerer_client(service)


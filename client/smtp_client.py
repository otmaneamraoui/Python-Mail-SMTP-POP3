import socket   # Pour la communication réseau (connexion TCP avec le serveur)

# Client SMTP simplifié avec réception des réponses du serveur
def envoyer_message():
    # Adresse du serveur SMTP
    serveur = ("127.0.0.1", 2525)

    # --- Étape 1 : demander les infos ---
    expediteur = input("Adresse e-mail de l'expéditeur : ")
    destinataire = input("Adresse e-mail du destinataire : ")
    objet = input("Objet du message : ")

    print("\nSaisissez votre message (Terminez par un point . seul sur une ligne.) :")
    lignes = []
    while True:
        ligne = input()
        if ligne == ".":
            break
        lignes.append(ligne)

    # Assemble le corps du mail
    contenu = "Objet: " + objet + "\n" + "\n".join(lignes)

    # --- Étape 2 : connexion au serveur ---
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(serveur)

        # Fonction locale pour lire la réponse du serveur
        def lire_reponse():
            reponse = s.recv(1024).decode("utf-8").strip()
            print("Serveur ->", reponse)
            return reponse

        # --- Étape 3 : communication SMTP ---
        # Accueil serveur
        lire_reponse()
        
        # ---- VERSION 2 : HELO  ----
        s.sendall(b"HELO client\r\n")
        lire_reponse()

        # Envoi de l’expéditeur
        s.sendall(("MAIL FROM:<" + expediteur + ">\r\n").encode("utf-8"))
        lire_reponse()

        # Envoi du destinataire
        s.sendall(("RCPT TO:<" + destinataire + ">\r\n").encode("utf-8"))
        lire_reponse()

        # Passage en mode DATA
        s.sendall(b"DATA\r\n")
        lire_reponse()

        # Envoi du contenu + fin avec un point
        s.sendall((contenu + "\r\n.\r\n").encode("utf-8"))
        lire_reponse()

        # Quitter proprement
        s.sendall(b"QUIT\r\n")
        lire_reponse()

        print("\n--> Message envoyé et connexion terminée.")

# Lancement du client
if __name__ == "__main__":
    envoyer_message()

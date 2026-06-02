from serveur.smtp_server import demarrer_serveur_smtp
from serveur.pop3_server import demarrer_serveur_pop3


if __name__ == "__main__":
    print("=== Projet E-Mail : Version 4 ===\n")
    print("1 - Lancer le serveur SMTP")
    print("2 - Lancer le serveur POP3")
    print("3 - Quitter")

    choix = input("Votre choix : ").strip()

    if choix == "1":
        print("\n=== SMTP ===\n")
        demarrer_serveur_smtp()

    elif choix == "2":
        print("\n=== POP3 ===\n")
        demarrer_serveur_pop3()

    else:
        print("Fin du programme.")

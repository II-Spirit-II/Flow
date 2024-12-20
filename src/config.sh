#!/bin/bash

if [ $EUID -ne 0 ]; then
  echo -e "\e[31mVous devez être root pour exécuter ce script.\e[0m"
  exit 1
fi

if [ -d "data" ]; then
    chmod -R 755 data
fi

while true; do
  # Afficher le menu
  echo -e "\e[33mQue voulez-vous faire ?\n\e[0m"
  echo -e "\e[34m1. Générer un certificat SSL autosigné"
  echo -e "2. Initialiser l'environnement"
  echo -e "3. Supprimer les données sensibles\n"
  echo -e "\e[31m4. Supprimer l'environement\e[0m"
  echo -e "\e[31m\nQ. Quitter\n\e[0m"

  # Lire le choix de l'utilisateur
  read -p $'\e[33mVotre choix : \e[0m' CHOICE

  # Exécuter l'action correspondant au choix de l'utilisateur
  case "$CHOICE" in
    1)
      # Créer le répertoire "ssl" s'il n'existe pas déjà
      if [ ! -d "ssl" ]; then
        mkdir ssl
      fi

      # Se placer dans le répertoire "ssl"
      cd ssl

      # Générer une clé privée RSA de 2048 bits et la stocker dans le répertoire "ssl"
      openssl genrsa -out server.key 2048

      # Créer une demande de signature de certificat (CSR) pour la clé privée
      openssl req -new -key server.key -out server.csr

      # Générer un certificat SSL autosigné valide pour 365 jours
      openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

      # Afficher le contenu du certificat pour vérifier qu'il a été correctement généré
      openssl x509 -in server.crt -text -noout
      cd ..

      # Afficher un message de fin en vert
      echo -e "\e[32mToutes les générations ont été exécutées avec succès !\e[0m"
      ;;
    2)
      # Indiquer les interfaces IP de la machine
      echo -e '\e[33mVoici vos interfaces :\n\e[0m'
      ip -c -br a
      # Demander les informations d'environnement à l'utilisateur
      read -p $'\e[33mVeuillez entrer l\'IP/domaine du server : \e[0m' SERVER_IP
      read -p $'\e[33mVeuillez entrer votre nom d\'utilisateur de la database : \e[0m' POSTGRES_USER
      read -sp $'\e[33mVeuillez entrer votre mot de passe de la database : \e[0m' POSTGRES_PASSWORD
      read -p $'\e[33m\nVeuillez entrer l\'identifiant du sender (émetteur des notifications mails) : \e[0m' EMAIL_HOST_USER
      read -sp $'\e[33mVeuillez entrer le mot de passe du sender (émetteur des notifications mails) : \e[0m' EMAIL_HOST_PASSWORD

      # Enregistrer ces informations dans le fichier d'environnement
      touch .dbenv
      echo "POSTGRES_DB=postgres" > .dbenv
      echo "POSTGRES_USER=$POSTGRES_USER" >> .dbenv
      echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >> .dbenv
      sed -i "s/^CSRF_TRUSTED_ORIGINS =.*/CSRF_TRUSTED_ORIGINS = ['https:\/\/*.$SERVER_IP']/" Flow/settings.py
      sed -i '/EMAIL_HOST_USER/c\EMAIL_HOST_USER = '\'$EMAIL_HOST_USER''\'' ' Flow/settings.py
      sed -i '/EMAIL_HOST_PASSWORD/c\EMAIL_HOST_PASSWORD = '\'$EMAIL_HOST_PASSWORD''\'' ' Flow/settings.py



      echo -e "\e[32m\nLes informations d'environnement ont été enregistrées avec succès !\e[0m"
      ;;
    3)
      # Demander une confirmation avant de supprimer les données sensibles
      read -p $'\e[33mÊtes-vous sûr de vouloir supprimer les données sensibles ? Cette action doit être réalisée lorsque la stack a déjà été démarrée au moins une fois. Après cela, les informations sensibles comme les mots de passes ne pourront plus être détournées et ne seront plus stockées dans les fichiers d\'environnement. Appuyez sur Entrée pour continuer ou tapez \'q\' pour quitter :\e[0m' CONFIRMATION

      # Sortir du script si l'utilisateur tape "q" ou "Q"
      if [[ "$CONFIRMATION" =~ ^[qQ]$ ]]; then
        echo -e "\e[31mAnnulation de la suppression des données sensibles.\e[0m"
        continue
      fi

      # Supprimer les données sensibles
      sed -i '/env_file:/d; s/- .dbenv//' docker-compose.yml
      rm .dbenv

      echo -e "\e[32m\nLes données sensibles ont été supprimées avec succès !\e[0m"
      ;;
    q|Q)
      echo -e "\e[31m\nBye !\e[0m"
      exit 0
      ;;
    4)
      # Demander une confirmation avant de supprimer l'environnement
      read -p $'\e[33mÊtes-vous sûr de vouloir supprimer l\'environnement ? (appuyez sur Entrée pour continuer ou tapez "q" pour quitter) : \e[0m' CONFIRMATION

      # Sortir du script si l'utilisateur tape "q" ou "Q"
      if [[ "$CONFIRMATION" =~ ^[qQ]$ ]]; then
        echo -e "\e[31mAnnulation de la suppression.\e[0m"
        continue
      fi

      # Supprimer les répertoires et fichiers de l'environnement
      rm -rf data
      rm -rf ssl
      rm .dbenv

      echo -e "\e[32m\nL'environnement a été supprimé avec succès !\e[0m"
      ;;
    *)
      # Afficher un message d'erreur en rouge si le choix est invalide
      echo -e "\e[31mChoix invalide !\e[0m"
      ;;
  esac

  # Demander à l'utilisateur s'il veut revenir au menu principal ou quitter le script
  read -p $'\e[33mAppuyez sur Entrée pour revenir au menu principal ou tapez "q" pour quitter : \e[0m' REPLY

  # Sortir du script si l'utilisateur tape "q" ou "Q"
  if [[ "$REPLY" =~ ^[qQ]$ ]]; then
    echo -e "\e[31mBye !\e[0m"
    exit 0
  fi

done

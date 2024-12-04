#!/bin/bash

# Script pour installer Docker et Docker Compose sur Debian

# Fonction pour afficher les messages
function echo_info() {
  echo -e "\e[1;34m$1\e[0m"
}

function echo_error() {
  echo -e "\e[1;31m$1\e[0m"
}

# Vérification des droits root
if [ "$EUID" -ne 0 ]; then
  echo_error "Ce script doit être exécuté en tant que root ou avec sudo."
  exit 1
fi

echo_info "Mise à jour des paquets..."
apt update && apt upgrade -y

echo_info "Installation des dépendances nécessaires..."
apt install -y ca-certificates curl gnupg lsb-release

echo_info "Ajout de la clé GPG officielle de Docker..."
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo_info "Ajout du dépôt Docker officiel..."
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
$(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

echo_info "Mise à jour des dépôts..."
apt update

echo_info "Installation de Docker et des plugins associés..."
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo_info "Activation et démarrage du service Docker..."
systemctl enable docker
systemctl start docker

echo_info "Ajout de l'utilisateur courant au groupe Docker..."
usermod -aG docker "$USER"

echo_info "Installation terminée. Vérification des versions..."
docker --version
docker compose version

echo_info "Installation réussie ! Déconnectez-vous et reconnectez-vous pour que les modifications prennent effet."

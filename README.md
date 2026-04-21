## 📌 Description du projet

Dans le cadre de mon projet de fin d’année en BTS CIEL, j’ai participé à la réalisation d’une solution de sécurisation des salles serveurs en collaboration avec la métropole de Montpellier.

L’objectif du projet est de mettre en place un système de surveillance automatisée capable de détecter des intrusions, d’enregistrer des preuves vidéo et d’alerter les utilisateurs via une interface web.

Le système repose sur un Raspberry Pi 5 équipé d’une caméra, utilisant TensorFlow Lite pour la détection d’individus.

---

## ⚙️ Fonctionnalités principales
- Détection d’intrusion basée sur une solution open-source (TensorFlow Lite)
- Enregistrement vidéo automatique avec :
- 5 secondes avant détection (buffer)
- 55 secondes après détection
- Horodatage des vidéos (date et heure dans le nom du fichier)
- Période de surveillance configurable (ex : en dehors des heures de travail)
- Envoi d’alertes :
- Sur le site web (dashboard)
- Par e-mail
- Visualisation des vidéos via une interface web développée en Django
- Suppression automatique des vidéos après 30 jours

---

## 🖥️ Contenu du repository

Ce dépôt contient :

- Le code Python complet utilisé sur le Raspberry Pi pour :
  - la détection d’intrusion
  - la gestion du buffer vidéo
  - l’enregistrement et la gestion des vidéos
- Le site web (dashboard) développé avec Django
- Les scripts de communication entre le Raspberry Pi et le serveur
- Mon rapport de projet (pages 13 à 88)

---

## 🧰 Technologies utilisées
- Raspberry Pi 5
- Caméra Raspberry Pi (module caméra)
- Python
- TensorFlow Lite
- Django
- Samba (transfert des vidéos)

---

## 🎯 Objectif

Proposer une solution de surveillance fiable, automatisée et accessible via une interface web, permettant de renforcer la sécurité des infrastructures critiques comme les salles serveurs.

---

## ✔️ Liens

```md
[Mon GitHub](https://github.com/Divo-Code)

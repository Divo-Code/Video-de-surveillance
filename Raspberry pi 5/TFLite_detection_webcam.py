import os  # Importe le module os pour interagir avec le système de fichiers
import argparse  # Importe le module argparse pour gérer les arguments en ligne de commande
import cv2  # Importe OpenCV pour le traitement des images et vidéos
import numpy as np  # Importe NumPy pour les calculs sur les tableaux
import sys  # Importe le module sys pour interagir avec le système
import time  # Importe le module time pour gérer le temps et les délais
import importlib.util  # Importe importlib.util pour charger dynamiquement des modules
from threading import Thread  # Importe Thread pour exécuter des tâches en parallèle
from flask import Flask, render_template, Response  # Importe Flask pour créer une application web et gérer les réponses HTTP
from datetime import datetime  # Importe datetime pour manipuler les dates et heures
from collections import deque  # Importe deque pour créer une file de frames avec une taille maximale
import shutil  # Importe shutil pour les opérations sur les fichiers (copie, suppression, etc.)
import requests  # Importe requests pour envoyer des requêtes HTTP
from picamera2 import Picamera2  # Importe Picamera2 pour interagir avec la caméra Raspberry Pi
import subprocess  # Importe subprocess pour exécuter des commandes shell (comme ffmpeg)
import smtplib  # Importe smtplib pour envoyer des emails via SMTP
from email.mime.text import MIMEText  # Importe MIMEText pour créer le corps de l'email
from email.mime.multipart import MIMEMultipart  # Importe MIMEMultipart pour construire des emails avec plusieurs parties

class FluxVideo:
    """Gère le flux vidéo de la Picamera dans un thread séparé."""
    def __init__(self, resolution=(640, 480), framerate=30):  # Définit le constructeur avec résolution et framerate par défaut
        self.picam2 = Picamera2()  # Initialise un objet Picamera2 pour interagir avec la caméra
        config = self.picam2.create_preview_configuration(main={"size": resolution})  # Crée une configuration pour la caméra avec la résolution spécifiée
        self.picam2.configure(config)  # Applique la configuration à la caméra
        self.picam2.start()  # Démarre la caméra
        self.frame = None  # Initialise la variable pour stocker la frame courante
        self.stopped = False  # Initialise un drapeau pour contrôler l'arrêt du thread

    def demarrer(self):  # Méthode pour démarrer le flux vidéo
        """Démarre le thread qui lit les frames du flux vidéo."""
        Thread(target=self.mettre_a_jour, daemon=True).start()  # Lance un thread pour mettre à jour les frames en continu
        return self  # Retourne l'instance pour permettre le chaînage des méthodes

    def mettre_a_jour(self):  # Méthode pour capturer les frames en continu
        """Met à jour en continu la frame depuis la caméra."""
        while not self.stopped:  # Boucle tant que le drapeau stopped est False
            self.frame = self.picam2.capture_array()  # Capture une frame depuis la caméra et la stocke

    def lire(self):  # Méthode pour lire la frame courante
        """Retourne la frame la plus récente."""
        return self.frame  # Retourne la frame stockée

    def arreter(self):  # Méthode pour arrêter le flux vidéo
        """Arrête la caméra et le thread."""
        self.stopped = True  # Définit le drapeau stopped à True pour arrêter la boucle
        self.picam2.stop()  # Arrête la caméra

class DetecteurObjets:
    """Gère le chargement du modèle TensorFlow Lite et la détection d'objets."""
    def __init__(self, dossier_modele, nom_graphique='detect.tflite', nom_labels='labelmap.txt', 
                 seuil=0.5, resolution='1280x720', utiliser_tpu=False):  # Constructeur avec paramètres pour le modèle et la détection
        self.nom_modele = dossier_modele  # Stocke le chemin du dossier contenant le modèle
        self.nom_graphique = nom_graphique  # Stocke le nom du fichier du modèle TensorFlow Lite
        self.nom_labels = nom_labels  # Stocke le nom du fichier des labels
        self.seuil_confiance_min = float(seuil)  # Stocke le seuil minimum de confiance pour la détection
        self.resW, self.resH = map(int, resolution.split('x'))  # Extrait la largeur et hauteur de la résolution
        self.imW, self.imH = self.resW, self.resH  # Stocke les dimensions de l'image
        self.utiliser_tpu = utiliser_tpu  # Stocke l'option d'utilisation du TPU Coral
        self.frame_rate_calc = 1  # Initialise le calcul du taux de frames par seconde
        self.freq = cv2.getTickFrequency()  # Récupère la fréquence des ticks pour le calcul du FPS
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Définit le codec vidéo pour l'enregistrement
        self.video_writer = None  # Initialise l'objet pour écrire les vidéos
        self._initialiser_modele()  # Appelle la méthode pour initialiser le modèle

    def _initialiser_modele(self):  # Méthode pour initialiser le modèle TensorFlow Lite
        """Initialise le modèle TensorFlow Lite et les labels."""
        pkg = importlib.util.find_spec('tflite_runtime')  # Vérifie si tflite_runtime est disponible
        if pkg:  # Si tflite_runtime est trouvé
            from tflite_runtime.interpreter import Interpreter  # Importe Interpreter depuis tflite_runtime
            if self.utiliser_tpu:  # Si l'utilisation du TPU est activée
                from tflite_runtime.interpreter import load_delegate  # Importe load_delegate pour le TPU
        else:  # Si tflite_runtime n'est pas trouvé
            from tensorflow.lite.python.interpreter import Interpreter  # Importe Interpreter depuis tensorflow
            if self.utiliser_tpu:  # Si l'utilisation du TPU est activée
                from tensorflow.lite.python.interpreter import load_delegate  # Importe load_delegate depuis tensorflow

        if self.utiliser_tpu and self.nom_graphique == 'detect.tflite':  # Si le TPU est utilisé et le modèle est standard
            self.nom_graphique = 'edgetpu.tflite'  # Change le nom du modèle pour utiliser la version TPU

        chemin_courant = os.getcwd()  # Récupère le répertoire de travail actuel
        chemin_modele = os.path.join(chemin_courant, self.nom_modele, self.nom_graphique)  # Construit le chemin complet du modèle
        chemin_labels = os.path.join(chemin_courant, self.nom_modele, self.nom_labels)  # Construit le chemin complet des labels

        # Charger les labels
        with open(chemin_labels, 'r') as f:  # Ouvre le fichier des labels en lecture
            self.labels = [line.strip() for line in f.readlines()]  # Lit et stocke les labels en supprimant les espaces
        if self.labels[0] == '???':  # Si le premier label est '???'
            del(self.labels[0])  # Supprime ce label

        # Charger le modèle TensorFlow Lite
        if self.utiliser_tpu:  # Si le TPU est utilisé
            self.interpreter = Interpreter(model_path=chemin_modele,
                                          experimental_delegates=[load_delegate('libedgetpu.so.1.0')])  # Charge le modèle avec le délégué TPU
        else:  # Sinon
            self.interpreter = Interpreter(model_path=chemin_modele)  # Charge le modèle sans TPU
        self.interpreter.allocate_tensors()  # Alloue les tenseurs pour le modèle

        # Obtenir les détails du modèle
        self.input_details = self.interpreter.get_input_details()  # Récupère les détails des entrées du modèle
        self.output_details = self.interpreter.get_output_details()  # Récupère les détails des sorties du modèle
        self.hauteur = self.input_details[0]['shape'][1]  # Stocke la hauteur attendue par le modèle
        self.largeur = self.input_details[0]['shape'][2]  # Stocke la largeur attendue par le modèle
        self.modele_flottant = (self.input_details[0]['dtype'] == np.float32)  # Vérifie si le modèle utilise des nombres flottants
        self.moyenne_entree = 127.5  # Définit la moyenne pour normaliser les entrées
        self.ecart_type_entree = 127.5  # Définit l'écart-type pour normaliser les entrées

        # Déterminer les indices de sortie en fonction du type de modèle (TF1 ou TF2)
        outname = self.output_details[0]['name']  # Récupère le nom de la première sortie
        if 'StatefulPartitionedCall' in outname:  # Si c'est un modèle TF2
            self.boxes_idx, self.classes_idx, self.scores_idx = 1, 3, 0  # Définit les indices pour boîtes, classes et scores
        else:  # Si c'est un modèle TF1
            self.boxes_idx, self.classes_idx, self.scores_idx = 0, 1, 2  # Définit les indices pour boîtes, classes et scores

class EnvoyeurEmail:
    """Gère l'envoi des emails pour les alertes d'intrusion et les vidéos."""
    def __init__(self):  # Constructeur de la classe EnvoyeurEmail
        self.expediteur = "jcros849@gmail.com"  # Stocke l'adresse email de l'expéditeur
        self.mot_de_passe = "hkdjmdjwxlsxxwtl"  # Stocke le mot de passe pour l'authentification SMTP
        self.destinataire = "pacpacc@daouse.com"  # Stocke l'adresse email du destinataire
        self.serveur_smtp = "smtp.gmail.com"  # Stocke l'adresse du serveur SMTP
        self.port_smtp = 587  # Stocke le port du serveur SMTP

    def envoyer(self, condition, date_email):  # Méthode pour envoyer un email
        """Envoie un email selon la condition (1: intrusion, 2: vidéo disponible)."""
        if condition == 1:  # Si la condition est une alerte d'intrusion
            sujet = "Intrusion"  # Définit le sujet de l'email
            html = f"""\
                <html>
                <body style="text-align: center; font-family: Arial, sans-serif; font-size: 14px;">
                    <img src="https://i.ibb.co/99kcbRz0/3m.png" style="max-width: 150px; height: auto; margin-bottom: 20px;">
                    <p><b>Une intrusion a été détectée le {date_email}</b></p>
                    <p>Rendez-vous <a href="http://172.20.28.5:8000/camera/alertes/">ICI</a> pour voir toutes les informations</p>
                </body>
                </html>
                """  # Définit le corps HTML de l'email pour une alerte d'intrusion
        elif condition == 2:  # Si la condition est une vidéo disponible
            sujet = "Vidéo Intrusion Disponible !"  # Définit le sujet de l'email
            html = f"""\
                <html>
                <body style="text-align: center; font-family: Arial, sans-serif; font-size: 14px;">
                    <img src="https://i.ibb.co/99kcbRz0/3m.png" style="max-width: 150px; height: auto; margin-bottom: 20px;">
                    <p><b>Vidéo disponible !</b></p>
                    <p>Vidéo de la détection : <a href="http://172.20.28.5:8000/camera/enregistrements/lecture_video_camera1/Enregistrement_{date_email}.mp4">ICI</a></p><br>
                    <p>Retrouvez toutes les autres vidéos : <a href="http://172.20.28.5:8000/camera/enregistrements">ICI</a></p>
                </body>
                </html>
                """  # Définit le corps HTML de l'email pour une vidéo disponible

        msg = MIMEMultipart()  # Crée un objet email avec plusieurs parties
        msg['From'] = self.expediteur  # Définit l'expéditeur de l'email
        msg['To'] = self.destinataire  # Définit le destinataire de l'email
        msg['Subject'] = sujet  # Définit le sujet de l'email
        msg.attach(MIMEText(html, 'html'))  # Attache le corps HTML à l'email

        try:  # Essaie d'envoyer l'email
            serveur = smtplib.SMTP(self.serveur_smtp, self.port_smtp)  # Ouvre une connexion au serveur SMTP
            serveur.starttls()  # Active le mode TLS pour sécuriser la connexion
            serveur.login(self.expediteur, self.mot_de_passe)  # Authentifie l'utilisateur
            serveur.sendmail(self.expediteur, self.destinataire, msg.as_string())  # Envoie l'email
            serveur.quit()  # Ferme la connexion au serveur
            print("Le mail a été envoyé avec succès !")  # Affiche un message de succès
        except Exception as e:  # Capture les erreurs potentielles
            print(f"Le mail n'a pas pu être envoyé ! {e}")  # Affiche l'erreur

class ProcesseurVideo:
    """Gère l'enregistrement et la conversion des vidéos."""
    def envoyer_alerte(date, heure, condition, date_exact=None):  # Méthode statique pour envoyer une alerte à l'API
        """Envoie une alerte à l'API Django."""
        url = 'http://172.20.28.5:8000/camera/alertes/api/alert'  # Définit l'URL de l'API
        if condition == 1:  # Si la condition est une alerte d'intrusion
            data = {
                'numero_camera': '1',  # Définit le numéro de la caméra
                'date': date,  # Définit la date de l'alerte
                'heure': heure,  # Définit l'heure de l'alerte
            }
        elif condition == 2:  # Si la condition est une vidéo disponible
            video = f"http://172.20.28.5:8000/camera/enregistrements/lecture_video_camera1/Enregistrement_{date_exact}.mp4"  # Construit l'URL de la vidéo
            data = {
                'numero_camera': '1',  # Définit le numéro de la caméra
                'date': date,  # Définit la date de l'alerte
                'heure': heure,  # Définit l'heure de l'alerte
                'video_disponible': video,  # Ajoute l'URL de la vidéo
            }
        try:  # Essaie d'envoyer la requête à l'API
            response = requests.post(url, json=data)  # Envoie une requête POST avec les données
            if response.status_code == 201:  # Si la requête est réussie
                print("Alerte envoyée avec succès !")  # Affiche un message de succès
            else:  # Si la requête échoue
                print(f"Erreur lors de l'envoi de l'alerte : {response.status_code}")  # Affiche l'erreur
        except requests.exceptions.RequestException as e:  # Capture les erreurs de connexion
            print(f"Erreur de connexion : {e}")  # Affiche l'erreur

    def ecrire_buffer(buffer_copy, date_exact, imW, imH, fourcc):  # Méthode statique pour écrire un buffer vidéo
        """Écrit le buffer dans une vidéo et effectue la conversion."""
        video_chemin = f'/home/ciel/tflite1/videos/cam1/Enregistrement_{date_exact}_en_cours.mp4'  # Définit le chemin temporaire de la vidéo
        video_writer = cv2.VideoWriter(video_chemin, fourcc, 11, (imW, imH))  # Crée un objet VideoWriter
        for buffered_frame in buffer_copy:  # Parcourt les frames du buffer
            video_writer.write(buffered_frame)  # Écrit chaque frame dans la vidéo
        video_writer.release()  # Libère l'objet VideoWriter

        EnvoyeurEmail().envoyer(2, date_exact)  # Envoie un email pour signaler que la vidéo est disponible
        input_video_path = f'/home/ciel/tflite1/videos/cam1/Enregistrement_{date_exact}_en_cours.mp4'  # Chemin de la vidéo temporaire
        output_video_path = f'/home/ciel/tflite1/videos/cam1/Enregistrement_{date_exact}.mp4'  # Chemin de la vidéo finale
        ffmpeg_command = [
            'ffmpeg', '-i', input_video_path, '-c:v', 'libx264', '-preset', 'fast', '-crf', '22', output_video_path
        ]  # Définit la commande ffmpeg pour convertir la vidéo
        process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # Exécute la commande ffmpeg
        stdout, stderr = process.communicate()  # Récupère la sortie et les erreurs de la commande
        os.remove(input_video_path)  # Supprime la vidéo temporaire

        date = datetime.now().strftime("%Y-%m-%d")  # Récupère la date actuelle
        heure = datetime.now().strftime("%H:%M:%S")  # Récupère l'heure actuelle
        ProcesseurVideo.envoyer_alerte(date, heure, 2, date_exact)  # Envoie une alerte à l'API pour signaler la vidéo
        print("FIN !")  # Affiche un message de fin
        os.system(f'echo "rm /home/ciel/tflite1/videos/cam1/Enregistrement_{date_exact}.mp4" | at now + 30 days')  # Planifie la suppression de la vidéo après 30 jours

class ApplicationDetection:
    """Gère la détection continue et le flux vidéo Flask."""
    def __init__(self):  # Constructeur de la classe ApplicationDetection
        parser = argparse.ArgumentParser()  # Crée un analyseur d'arguments
        parser.add_argument('--modeldir', help='Dossier où se trouve le fichier .tflite', required=True)  # Ajoute l'argument pour le dossier du modèle
        parser.add_argument('--graph', help='Nom du fichier .tflite, si différent de detect.tflite', default='detect.tflite')  # Ajoute l'argument pour le nom du modèle
        parser.add_argument('--labels', help='Nom du fichier labelmap, si différent de labelmap.txt', default='labelmap.txt')  # Ajoute l'argument pour le fichier des labels
        parser.add_argument('--threshold', help='Seuil minimum de confiance pour afficher les objets détectés', default=0.5)  # Ajoute l'argument pour le seuil de confiance
        parser.add_argument('--resolution', help='Résolution souhaitée de la webcam en LxH', default='1280x720')  # Ajoute l'argument pour la résolution
        parser.add_argument('--edgetpu', help='Utiliser Coral Edge TPU Accelerator', action='store_true')  # Ajoute l'argument pour activer le TPU
        args = parser.parse_args()  # Analyse les arguments de la ligne de commande

        self.detecteur = DetecteurObjets(args.modeldir, args.graph, args.labels, args.threshold, args.resolution, args.edgetpu)  # Crée une instance de DetecteurObjets
        self.flux_video = FluxVideo(resolution=(self.detecteur.imW, self.detecteur.imH), framerate=11).demarrer()  # Crée et démarre un flux vidéo
        self.app = Flask(__name__)  # Crée une application Flask
        self.dernier_temps_detection = 0  # Initialise le temps de la dernière détection
        self.enregistrement = False  # Initialise l'état de l'enregistrement
        self.taille_buffer = 11 * 15  # Définit la taille du buffer (11 fps * 15 secondes)
        self.frame_buffer = deque(maxlen=self.taille_buffer)  # Crée une file pour stocker les frames
        self.date_exact = 0  # Initialise la date exacte pour les enregistrements
        self.date_email = 0  # Initialise la date pour les emails

    def detection_continue(self):  # Méthode pour effectuer la détection en continu
        """Effectue la détection continue des objets."""
        while True:  # Boucle infinie pour la détection
            t1 = cv2.getTickCount()  # Récupère le temps actuel pour calculer le FPS
            heure_actuelle = int(datetime.now().strftime("%H"))  # Récupère l'heure actuelle
            if 6 < heure_actuelle or heure_actuelle <= 19:  # Vérifie si l'heure est entre 7h et 19h (normalement entre 19h et 6h)
                frame1 = self.flux_video.lire()  # Lit la frame courante du flux vidéo
                if frame1 is None:  # Si aucune frame n'est disponible
                    time.sleep(0.01)  # Attend 10ms
                    continue  # Passe à l'itération suivante
                frame = frame1.copy()  # Crée une copie de la frame
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convertit la frame de RGB à BGR
                self.frame_buffer.append(frame_bgr)  # Ajoute la frame au buffer
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convertit la frame en RGB pour la détection
                frame_redimensionne = cv2.resize(frame_rgb, (self.detecteur.largeur, self.detecteur.hauteur))  # Redimensionne la frame pour le modèle
                input_data = np.expand_dims(frame_redimensionne, axis=0)  # Ajoute une dimension pour correspondre au format du modèle

                if self.detecteur.modele_flottant:  # Si le modèle utilise des nombres flottants
                    input_data = (np.float32(input_data) - self.detecteur.moyenne_entree) / self.detecteur.ecart_type_entree  # Normalise les données

                self.detecteur.interpreter.set_tensor(self.detecteur.input_details[0]['index'], input_data)  # Définit les données d'entrée pour le modèle
                self.detecteur.interpreter.invoke()  # Exécute l'inférence du modèle

                classes = self.detecteur.interpreter.get_tensor(self.detecteur.output_details[self.detecteur.classes_idx]['index'])[0]  # Récupère les classes détectées
                scores = self.detecteur.interpreter.get_tensor(self.detecteur.output_details[self.detecteur.scores_idx]['index'])[0]  # Récupère les scores de confiance

                if self.enregistrement:  # Si un enregistrement est en cours
                    temps_actuel = time.time()  # Récupère le temps actuel
                    if temps_actuel - self.dernier_temps_detection > 10:  # Si plus de 10 secondes se sont écoulées
                        buffer_copy = list(self.frame_buffer)  # Copie le buffer
                        Thread(target=ProcesseurVideo.ecrire_buffer, 
                               args=(buffer_copy, self.date_exact, self.detecteur.imW, self.detecteur.imH, self.detecteur.fourcc)).start()  # Lance l'écriture du buffer dans un thread
                        self.enregistrement = False  # Désactive l'enregistrement

                for i in range(len(scores)):  # Parcourt les scores de détection
                    if scores[i] > self.detecteur.seuil_confiance_min and scores[i] <= 1.0:  # Si le score est supérieur au seuil
                        if self.detecteur.labels[int(classes[i])] == 'person':  # Si l'objet détecté est une personne
                            temps_actuel = time.time()  # Récupère le temps actuel
                            if temps_actuel - self.dernier_temps_detection > 10:  # Si plus de 10 secondes depuis la dernière détection
                                print("Personne détectée !")  # Affiche un message
                                self.dernier_temps_detection = temps_actuel  # Met à jour le temps de la dernière détection
                                date = datetime.now().strftime("%Y-%m-%d")  # Récupère la date actuelle
                                heure = datetime.now().strftime("%H:%M:%S")  # Récupère l'heure actuelle
                                Thread(target=ProcesseurVideo.envoyer_alerte, args=(date, heure, 1)).start()  # Envoie une alerte d'intrusion
                                if not self.enregistrement:  # Si aucun enregistrement n'est en cours
                                    self.date_exact = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Définit la date exacte
                                    self.date_email = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")  # Définit la date pour l'email
                                    Thread(target=EnvoyeurEmail().envoyer, args=(1, self.date_email)).start()  # Envoie un email d'alerte
                                    self.enregistrement = True  # Active l'enregistrement

                t2 = cv2.getTickCount()  # Récupère le temps après la détection
                temps = (t2 - t1) / self.detecteur.freq  # Calcule le temps écoulé
                self.detecteur.frame_rate_calc = 1 / temps  # Calcule le FPS

    def generer_frames(self):  # Méthode pour générer des frames pour le flux vidéo
        """Génère les frames pour le flux vidéo."""
        while True:  # Boucle infinie pour générer les frames
            heure_affichage = datetime.now().strftime("%H:%M:%S")  # Récupère l'heure actuelle pour l'affichage
            frame = self.flux_video.lire()  # Lit la frame courante
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convertit la frame en BGR
            boxes = self.detecteur.interpreter.get_tensor(self.detecteur.output_details[self.detecteur.boxes_idx]['index'])[0]  # Récupère les boîtes de détection
            classes = self.detecteur.interpreter.get_tensor(self.detecteur.output_details[self.detecteur.classes_idx]['index'])[0]  # Récupère les classes détectées
            scores = self.detecteur.interpreter.get_tensor(self.detecteur.output_details[self.detecteur.scores_idx]['index'])[0]  # Récupère les scores de confiance

            for i in range(len(scores)):  # Parcourt les scores
                if scores[i] > self.detecteur.seuil_confiance_min and scores[i] <= 1.0:  # Si le score est supérieur au seuil
                    if self.detecteur.labels[int(classes[i])] == 'person':  # Si l'objet est une personne
                        ymin = int(max(1, (boxes[i][0] * self.detecteur.imH)))  # Calcule la coordonnée y minimale
                        xmin = int(max(1, (boxes[i][1] * self.detecteur.imW)))  # Calcule la coordonnée x minimale
                        ymax = int(min(self.detecteur.imH, (boxes[i][2] * self.detecteur.imH)))  # Calcule la coordonnée y maximale
                        xmax = int(min(self.detecteur.imW, (boxes[i][3] * self.detecteur.imW)))  # Calcule la coordonnée x maximale
                        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)  # Dessine un rectangle autour de la personne
                        object_name = self.detecteur.labels[int(classes[i])]  # Récupère le nom de l'objet
                        label = f'{object_name}: {int(scores[i]*100)}%'  # Crée une étiquette avec le nom et le score
                        labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)  # Calcule la taille du texte
                        label_ymin = max(ymin, labelSize[1] + 10)  # Ajuste la position du texte
                        cv2.rectangle(frame, (xmin, label_ymin - labelSize[1] - 10), 
                                     (xmin + labelSize[0], label_ymin + baseLine - 10), (255, 255, 255), cv2.FILLED)  # Dessine un fond pour le texte
                        cv2.putText(frame, label, (xmin, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)  # Affiche le texte

            cv2.putText(frame, "CAMERA 1", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)  # Affiche le texte "CAMERA 1"
            cv2.putText(frame, f'FPS: {self.detecteur.frame_rate_calc:.2f}', (1080, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)  # Affiche le FPS
            cv2.putText(frame, f' {heure_affichage}', (1080, 700), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3, cv2.LINE_AA)  # Affiche l'heure

            ret, buffer = cv2.imencode('.jpg', frame)  # Encode la frame en JPEG
            frame = buffer.tobytes()  # Convertit la frame en bytes
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Génère une réponse pour le flux vidéo

    def configurer_routes(self):  # Méthode pour configurer les routes Flask
        """Configure les routes Flask."""
        @self.app.route('/video_feed')  # Définit la route pour le flux vidéo
        def video_feed():
            return Response(self.generer_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')  # Retourne le flux vidéo

        @self.app.route('/')  # Définit la route pour la page d'accueil
        def index():
            return render_template('index.html')  # Rend le template index.html

    def executer(self):  # Méthode pour démarrer l'application
        """Démarre la détection et l'application Flask."""
        Thread(target=self.detection_continue).start()  # Lance la détection continue dans un thread
        self.configurer_routes()  # Configure les routes Flask
        self.app.run(host='0.0.0.0', port=2000)  # Lance le serveur Flask

if __name__ == '__main__':  # Vérifie si le script est exécuté directement
    app_detection = ApplicationDetection()  # Crée une instance de ApplicationDetection
    app_detection.executer()  # Lance l'application
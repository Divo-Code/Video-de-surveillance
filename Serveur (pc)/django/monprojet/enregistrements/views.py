import os
from django.shortcuts import render
from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.core.exceptions import ImproperlyConfigured
import time
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required(login_url='/admin/')
def liste_videos_total(request):
    chemin_videos = settings.SAMBA_CAMERA1
    chemin_videos2 = settings.SAMBA_CAMERA2
    chemin_videos3 = settings.SAMBA_CAMERA3
    chemin_videos4 = settings.SAMBA_CAMERA4
    error = None

    try:
        # Définir un délai d'attente
        timeout = 10  # Temps d'attente maximal en secondes
        start_time = time.time()
        
        # Tentative de connexion (ici juste une lecture pour voir si le dossier est accessible)
        while time.time() - start_time < timeout:
            if os.path.exists(chemin_videos) and os.path.exists(chemin_videos2) and os.path.exists(chemin_videos3) and os.path.exists(chemin_videos4):
                break
        
        else:  # Si le timeout est dépassé, renvoie une erreur
            error = "Impossible de se connecter au Raspberry Pi."

        # Liste des vidéos
        if error == None:
            video_camera1 = [f for f in os.listdir(chemin_videos) if f.endswith(".mp4")]
            video_camera2 = [f for f in os.listdir(chemin_videos2) if f.endswith(".mp4")]
            video_camera3 = [f for f in os.listdir(chemin_videos3) if f.endswith(".mp4")]
            video_camera4 = [f for f in os.listdir(chemin_videos4) if f.endswith(".mp4")]
            total = video_camera1 + video_camera2 + video_camera3 + video_camera4
            total.sort(reverse=True) # Par Ordre Croissant
        else:
            total = []

    except Exception as e:
        error = f"Erreur lors de la récupération des vidéos : {str(e)}"
        total = []

    return render(request, "enregistrements/index.html", {"total": total, "error": error})

def lire_video_total(request, filename):
    chemin_fichier = os.path.join(settings.SAMBA_CAMERA1, filename)
    chemin_fichier2 = os.path.join(settings.SAMBA_CAMERA2, filename)
    chemin_fichier3 = os.path.join(settings.SAMBA_CAMERA2, filename)
    chemin_fichier4 = os.path.join(settings.SAMBA_CAMERA2, filename)

    # Vérifier si le fichier existe avant d'essayer de le lire
    if os.path.exists(chemin_fichier):
        return FileResponse(open(chemin_fichier, "rb"), content_type="video/mp4")

    if os.path.exists(chemin_fichier2):
        return FileResponse(open(chemin_fichier2, "rb"), content_type="video/mp4")

    if os.path.exists(chemin_fichier3):
        return FileResponse(open(chemin_fichier3, "rb"), content_type="video/mp4")

    if os.path.exists(chemin_fichier4):
        return FileResponse(open(chemin_fichier4, "rb"), content_type="video/mp4")
    else:
        return HttpResponse("Fichier non trouvé", status=404)

def lire_video_camera1(request, filename):
    chemin_fichier = os.path.join(settings.SAMBA_CAMERA1, filename)

    # Vérifier si le fichier existe avant d'essayer de le lire
    if os.path.exists(chemin_fichier):
        return FileResponse(open(chemin_fichier, "rb"), content_type="video/mp4")
    else:
        return HttpResponse("Fichier non trouvé", status=404)

def lire_video_camera2(request, filename):
    chemin_fichier = os.path.join(settings.SAMBA_CAMERA2, filename)

    # Vérifier si le fichier existe avant d'essayer de le lire
    if os.path.exists(chemin_fichier):
        return FileResponse(open(chemin_fichier, "rb"), content_type="video/mp4")
    else:
        return HttpResponse("Fichier non trouvé", status=404)

def lire_video_camera3(request, filename):
    chemin_fichier = os.path.join(settings.SAMBA_CAMERA3, filename)

    # Vérifier si le fichier existe avant d'essayer de le lire
    if os.path.exists(chemin_fichier):
        return FileResponse(open(chemin_fichier, "rb"), content_type="video/mp4")
    else:
        return HttpResponse("Fichier non trouvé", status=404)

def lire_video_camera4(request, filename):
    chemin_fichier = os.path.join(settings.SAMBA_CAMERA4, filename)

    # Vérifier si le fichier existe avant d'essayer de le lire
    if os.path.exists(chemin_fichier):
        return FileResponse(open(chemin_fichier, "rb"), content_type="video/mp4")
    else:
        return HttpResponse("Fichier non trouvé", status=404)

def enregistrementscamera1(request):
    chemin_videos_camera1 = settings.SAMBA_CAMERA1
    error = None

    try:
        # Définir un délai d'attente
        timeout = 3  # Temps d'attente maximal en secondes
        start_time = time.time()
        
        # Tentative de connexion (ici juste une lecture pour voir si le dossier est accessible)
        while time.time() - start_time < timeout:
            if os.path.exists(chemin_videos_camera1):
                break
        
        else:  # Si le timeout est dépassé, renvoie une erreur
            error = "Impossible de se connecter au Raspberry Pi."

        # Liste des vidéos
        if error == None:
            videos_camera1 = [f for f in os.listdir(chemin_videos_camera1) if f.endswith(".mp4")]
            videos_camera1.sort(reverse=True) # Par Ordre Croissant
        else:
            videos_camera1 = []

    except Exception as e:
        error = f"Erreur lors de la récupération des vidéos : {str(e)}"
        videos_camera1 = []
    return render(request, 'enregistrements/camera1.html', {"videos_camera1": videos_camera1, "error": error})

def enregistrementscamera2(request):
    chemin_videos_camera2 = settings.SAMBA_CAMERA2
    error = None

    try:
        # Définir un délai d'attente
        timeout = 3  # Temps d'attente maximal en secondes
        start_time = time.time()
        
        # Tentative de connexion (ici juste une lecture pour voir si le dossier est accessible)
        while time.time() - start_time < timeout:
            if os.path.exists(chemin_videos_camera2):
                break
        
        else:  # Si le timeout est dépassé, renvoie une erreur
            error = "Impossible de se connecter au Raspberry Pi."

        # Liste des vidéos
        if error == None:
            videos_camera2 = [f for f in os.listdir(chemin_videos_camera2) if f.endswith(".mp4")]
            videos_camera2.sort(reverse=True) # Par Ordre Croissant
        else:
            videos_camera2 = []

    except Exception as e:
        error = f"Erreur lors de la récupération des vidéos : {str(e)}"
        videos_camera2 = []
    return render(request, 'enregistrements/camera2.html', {"videos_camera2": videos_camera2, "error": error})

def enregistrementscamera3(request):
    chemin_videos_camera3 = settings.SAMBA_CAMERA3
    error = None

    try:
        # Définir un délai d'attente
        timeout = 3  # Temps d'attente maximal en secondes
        start_time = time.time()
        
        # Tentative de connexion (ici juste une lecture pour voir si le dossier est accessible)
        while time.time() - start_time < timeout:
            if os.path.exists(chemin_videos_camera3):
                break
        
        else:  # Si le timeout est dépassé, renvoie une erreur
            error = "Impossible de se connecter au Raspberry Pi."

        # Liste des vidéos
        if error == None:
            videos_camera3 = [f for f in os.listdir(chemin_videos_camera3) if f.endswith(".mp4")]
            videos_camera3.sort(reverse=True) # Par Ordre Croissant
        else:
            videos_camera3 = []

    except Exception as e:
        error = f"Erreur lors de la récupération des vidéos : {str(e)}"
        videos_camera3 = []
    return render(request, 'enregistrements/camera3.html', {"videos_camera3": videos_camera3, "error": error})

def enregistrementscamera4(request):
    chemin_videos_camera4 = settings.SAMBA_CAMERA4
    error = None

    try:
        # Définir un délai d'attente
        timeout = 3  # Temps d'attente maximal en secondes
        start_time = time.time()
        
        # Tentative de connexion (ici juste une lecture pour voir si le dossier est accessible)
        while time.time() - start_time < timeout:
            if os.path.exists(chemin_videos_camera4):
                break
        
        else:  # Si le timeout est dépassé, renvoie une erreur
            error = "Impossible de se connecter au Raspberry Pi."

        # Liste des vidéos
        if error == None:
            videos_camera4 = [f for f in os.listdir(chemin_videos_camera4) if f.endswith(".mp4")]
            videos_camera4.sort(reverse=True) # Par Ordre Croissant
        else:
            videos_camera4 = []

    except Exception as e:
        error = f"Erreur lors de la récupération des vidéos : {str(e)}"
        videos_camera4 = []
    return render(request, 'enregistrements/camera4.html', {"videos_camera4": videos_camera4, "error": error})
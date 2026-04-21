from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import VisualisationCamera1, VisualisationCamera2, VisualisationCamera3, VisualisationCamera4

from django.shortcuts import render
from .models import VisualisationCamera1
from django.contrib.admin.views.decorators import staff_member_required

class IntrusionAlertView(APIView):
    def post(self, request, *args, **kwargs):
        # Récupérer les données de la requête
        numero_camera = request.data.get('numero_camera', '')
        date = request.data.get('date', '')
        heure = request.data.get('heure', '')
        video_disponible = request.data.get('video_disponible', '')
        #nom_camera = request.data.get('nom_camera', '')

        if numero_camera and date and heure:
            if int(numero_camera) == 1:
            # Créer un nouvel enregistrement dans la table `VisualisationCamera1`
                visualisation = VisualisationCamera1(
                    numero_camera=numero_camera,
                    date=date,
                    heure=heure,
                    video_disponible=video_disponible,
                )
                visualisation.save()

            if int(numero_camera) == 2:
            # Créer un nouvel enregistrement dans la table `VisualisationCamera2`
                visualisation = VisualisationCamera2(
                    numero_camera=numero_camera,
                    date=date,
                    heure=heure,
                    video_disponible=video_disponible,
                )
                visualisation.save()

            if int(numero_camera) == 3:
            # Créer un nouvel enregistrement dans la table `VisualisationCamera3`
                visualisation = VisualisationCamera3(
                    numero_camera=numero_camera,
                    date=date,
                    heure=heure,
                    video_disponible=video_disponible,
                )
                visualisation.save()

            if int(numero_camera) == 4:
            # Créer un nouvel enregistrement dans la table `VisualisationCamera4`
                visualisation = VisualisationCamera4(
                    numero_camera=numero_camera,
                    date=date,
                    heure=heure,
                    video_disponible=video_disponible,
                )
                visualisation.save()
            return Response({"message": "Alerte enregistrée avec succès!"}, status=status.HTTP_201_CREATED)
        return Response({"message": "Alerte manquante!"}, status=status.HTTP_400_BAD_REQUEST)



@staff_member_required(login_url='/admin/')
def afficher_alertes(request):
    alertes1 = VisualisationCamera1.objects.all().order_by('-id')
    alertes2 = VisualisationCamera2.objects.all().order_by('-id')
    alertes3 = VisualisationCamera3.objects.all().order_by('-id')
    alertes4 = VisualisationCamera4.objects.all().order_by('-id')

    alertes = list(alertes1) + list(alertes2) + list(alertes3) + list(alertes4)

    return render(request, 'alertes/index.html', {'alertes': alertes})


def alertescamera1(request):
    alertes = VisualisationCamera1.objects.all().order_by('-id')
    return render(request, 'alertes/camera1.html', {'alertes': alertes})

def alertescamera2(request):
    alertes = VisualisationCamera2.objects.all().order_by('-id')
    return render(request, 'alertes/camera2.html', {'alertes': alertes})

def alertescamera3(request):
    alertes = VisualisationCamera3.objects.all().order_by('-id')
    return render(request, 'alertes/camera3.html', {'alertes': alertes})

def alertescamera4(request):
    alertes = VisualisationCamera4.objects.all().order_by('-id')
    return render(request, 'alertes/camera4.html', {'alertes': alertes})
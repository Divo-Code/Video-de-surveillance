from django.urls import path
from .views import liste_videos_total, lire_video_total, lire_video_camera1, lire_video_camera2, lire_video_camera3, lire_video_camera4
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('lecture_video/<str:filename>/', lire_video_total, name='lecture_video'),  # Lire une vidéo spécifique de tous les enregistrements
    path('lecture_video_camera1/<str:filename>/', lire_video_camera1, name='lecture_video_camera1'),  # Lire une vidéo spécifique de la caméra 1
    path('lecture_video_camera2/<str:filename>/', lire_video_camera2, name='lecture_video_camera2'),  # Lire une vidéo spécifique de la caméra 2
    path('lecture_video_camera3/<str:filename>/', lire_video_camera3, name='lecture_video_camera3'),  # Lire une vidéo spécifique de la caméra 3
    path('lecture_video_camera4/<str:filename>/', lire_video_camera4, name='lecture_video_camera4'),  # Lire une vidéo spécifique de la caméra 4

    path('', liste_videos_total, name='liste_videos'),  # Affiche toutes les vidéos
    path('camera1/', views.enregistrementscamera1, name='camera1'),# Affiche toutes les vidéos de la caméra 1
    path('camera2/', views.enregistrementscamera2, name='camera2'),# Affiche toutes les vidéos de la caméra 2
    path('camera3/', views.enregistrementscamera3, name='camera3'),# Affiche toutes les vidéos de la caméra 3
    path('camera4/', views.enregistrementscamera4, name='camera4'),# Affiche toutes les vidéos de la caméra 4
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
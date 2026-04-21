from django.conf import settings
from django.urls import path, include
from . import views
from .views import index
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", index, name="index"),

    path('enregistrements/', include('enregistrements.urls')),

    path('alertes/', include('alertes.urls')),
    
]

# Servir les fichiers statiques en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
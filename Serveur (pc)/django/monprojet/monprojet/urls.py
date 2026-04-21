from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import home
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path("camera/", include("camera.urls")),
]

# Servir les fichiers statiques en mode développement


    
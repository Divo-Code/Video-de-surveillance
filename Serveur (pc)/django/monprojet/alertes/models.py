from django.db import models

# Classe mère réutilisable
class BaseVisualisationCamera(models.Model):
    numero_camera = models.TextField()
    date = models.TextField()
    heure = models.TextField()
    video_disponible = models.TextField()

    class Meta:
        abstract = True  # Ne pas créer de table pour cette classe

# Classe fille pour chaque caméra
class VisualisationCamera1(BaseVisualisationCamera):
    class Meta:
        db_table = 'alertes_visualisationcamera1'

class VisualisationCamera2(BaseVisualisationCamera):
    class Meta:
        db_table = 'alertes_visualisationcamera2'

class VisualisationCamera3(BaseVisualisationCamera):
    class Meta:
        db_table = 'alertes_visualisationcamera3'

class VisualisationCamera4(BaseVisualisationCamera):
    class Meta:
        db_table = 'alertes_visualisationcamera4'
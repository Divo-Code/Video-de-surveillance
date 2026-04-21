from django.urls import path
from .views import IntrusionAlertView
from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('api/alert', IntrusionAlertView.as_view(), name='intrusion_alert'),
    path('', views.afficher_alertes, name='alertes_index'),

    path('camera1/', views.alertescamera1, name='alertescamera1'),
    path('camera2/', views.alertescamera2, name='alertescamera2'),
    path('camera3/', views.alertescamera3, name='alertescamera3'),
    path('camera4/', views.alertescamera4, name='alertescamera4'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
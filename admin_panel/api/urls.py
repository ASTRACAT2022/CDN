from django.urls import path
from .views import RegisterNodeView, ConfigView

urlpatterns = [
    path('register/', RegisterNodeView.as_view(), name='register-node'),
    path('config/', ConfigView.as_view(), name='get-config'),
]
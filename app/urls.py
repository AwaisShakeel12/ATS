from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('ats', views.ats, name='ats'),
    
]
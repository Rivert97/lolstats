from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='summoners/index'),
    path('<str:region>/', views.index, name='summoners/index'),
    path('<str:region>/<str:summoner_name>/', views.detail, name='summoners/detail'),
]

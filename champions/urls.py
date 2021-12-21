from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:champion_identifier>/', views.detail, name='detail'),
]

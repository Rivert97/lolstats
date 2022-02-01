from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='champions/index'),
    path('<str:champion_identifier>/', views.detail, name='champions/detail'),
]

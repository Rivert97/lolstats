from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='summoners/index'),
    path('api/summoner/', views.summoner_api),
    path('api/summoner/<str:summonerid>', views.summoner_api),
    path('api/game/', views.game_api),
    path('api/game/<str:gameid>', views.game_api),
    path('<str:region>/', views.index, name='summoners/index'),
    path('<str:region>/<str:summoner_name>', views.detail, name='summoners/detail'),
]

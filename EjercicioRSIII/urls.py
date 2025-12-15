from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cargar_bd/', views.cargar_bd, name='cargar_bd'),
    path('cargar_recsys/', views.cargar_recsys, name='cargar_recsys'),
    path('peliculas_por_actor/', views.peliculas_por_actor, name='peliculas_por_actor'),
    path('usuarios_mas_activos/', views.usuarios_mas_activos, name='usuarios_mas_activos'),
    path('recomendar_peliculas/', views.recomendar_peliculas, name='recomendar_peliculas'),
    path('admin/', admin.site.urls),
]

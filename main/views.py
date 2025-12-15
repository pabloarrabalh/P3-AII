#encoding:utf-8

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
from main.models import Pelicula, Puntuacion
from main import populateDB, recommendations
from main.forms import FormularioConfirmacion, FormularioPeliculasPorActor, FormularioRecomendarPeliculas

def index(request):
    """
    Vista principal de la aplicación
    """
    return render(request, 'index.html', {'STATIC_URL': settings.STATIC_URL})

def cargar_bd(request):
    """
    Vista para cargar la base de datos desde el dataset
    Muestra un formulario de confirmación antes de proceder
    """
    formulario = FormularioConfirmacion()
    stats = None
    
    if request.method == 'POST':
        formulario = FormularioConfirmacion(request.POST)
        
        if formulario.is_valid():
            # Cargar la base de datos
            populateDB.populate()
            # Obtener estadísticas
            stats = populateDB.get_database_stats()
    
    return render(request, 'cargar_bd.html', {
        'formulario': formulario,
        'stats': stats,
        'STATIC_URL': settings.STATIC_URL
    })

def cargar_recsys(request):
    """
    Vista para cargar el sistema de recomendación
    """
    mensaje = None
    
    if request.method == 'POST':
        # Cargar las preferencias
        recommendations.loadPrefs()
        mensaje = "Sistema de recomendación cargado correctamente"
    
    return render(request, 'cargar_recsys.html', {
        'mensaje': mensaje,
        'STATIC_URL': settings.STATIC_URL
    })

def peliculas_por_actor(request):
    """
    Vista para mostrar películas por actor
    """
    formulario = FormularioPeliculasPorActor()
    peliculas = None
    actor_seleccionado = None
    num_peliculas = 0
    
    if request.method == 'POST':
        formulario = FormularioPeliculasPorActor(request.POST)
        
        if formulario.is_valid():
            actor_seleccionado = formulario.cleaned_data['actor']
            peliculas = recommendations.obtener_peliculas_por_actor(actor_seleccionado)
            num_peliculas = peliculas.count()
    
    return render(request, 'peliculas_por_actor.html', {
        'formulario': formulario,
        'peliculas': peliculas,
        'actor': actor_seleccionado,
        'num_peliculas': num_peliculas,
        'STATIC_URL': settings.STATIC_URL
    })

def usuarios_mas_activos(request):
    """
    Vista para mostrar los 5 usuarios más activos
    y los 3 usuarios más similares a cada uno
    """
    # Obtener los 5 usuarios más activos
    usuarios_activos = recommendations.getUsuariosMasActivos(n=5)
    
    # Para cada usuario, obtener los 3 más similares
    usuarios_con_similares = []
    for (id_usuario, num_peliculas) in usuarios_activos:
        similares = recommendations.getUsuariosSimilares(id_usuario, n=3)
        usuarios_con_similares.append({
            'id_usuario': id_usuario,
            'num_peliculas': num_peliculas,
            'similares': similares
        })
    
    return render(request, 'usuarios_mas_activos.html', {
        'usuarios': usuarios_con_similares,
        'STATIC_URL': settings.STATIC_URL
    })

def recomendar_peliculas(request):
    """
    Vista para recomendar películas a un usuario
    Recomienda 2 películas anteriores a una fecha dada
    """
    formulario = FormularioRecomendarPeliculas()
    recomendaciones = None
    usuario = None
    fecha = None
    
    if request.method == 'POST':
        formulario = FormularioRecomendarPeliculas(request.POST)
        
        if formulario.is_valid():
            usuario = formulario.cleaned_data['idUsuario']
            fecha = formulario.cleaned_data['fecha']
            
            # Obtener recomendaciones
            recs = recommendations.recomendar_peliculas_usuario(usuario, fecha, n=2)
            
            # Obtener detalles de las películas recomendadas
            recomendaciones = []
            for (rec, id_pelicula) in recs:
                try:
                    pelicula = Pelicula.objects.get(pk=id_pelicula)
                    recomendaciones.append({
                        'titulo': pelicula.titulo,
                        'fecha': pelicula.fecha,
                        'director': pelicula.director,
                        'actores': pelicula.actoresPrincipales,
                        'recomendacion': round(rec, 2)
                    })
                except Pelicula.DoesNotExist:
                    continue
    
    return render(request, 'recomendar_peliculas.html', {
        'formulario': formulario,
        'recomendaciones': recomendaciones,
        'usuario': usuario,
        'fecha': fecha,
        'STATIC_URL': settings.STATIC_URL
    })

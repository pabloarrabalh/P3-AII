#encoding:utf-8

from main.models import Pelicula, Puntuacion
from datetime import datetime
import os
from django.conf import settings

# Ruta absoluta al directorio de datos
path = os.path.join(settings.BASE_DIR, "data")

def populate():
    """
    Función principal para poblar la base de datos
    """
    m = populateMovies()
    populateRatings(m)

def populateMovies():
    """
    Carga las películas desde el archivo movies1.txt
    Formato: idPelicula \t Titulo \t Fecha \t Director \t ActoresPrincipales
    """
    Pelicula.objects.all().delete()
    
    lista_peliculas = []
    dict_peliculas = {}  # diccionario {idPelicula: objeto_pelicula}
    
    fileobj = open(os.path.join(path, "movies1.txt"), "r", encoding='utf-8')
    for line in fileobj.readlines():
        rip = line.strip().split('\t')
        if len(rip) != 5:
            continue
        
        # Parsear la fecha (formato YYYY-MM-DD)
        try:
            fecha = datetime.strptime(rip[2], '%Y-%m-%d').date()
        except:
            fecha = None
        
        pelicula = Pelicula(
            idPelicula=int(rip[0]),
            titulo=rip[1],
            fecha=fecha,
            director=rip[3],
            actoresPrincipales=rip[4]
        )
        lista_peliculas.append(pelicula)
        dict_peliculas[int(rip[0])] = pelicula
    
    fileobj.close()
    Pelicula.objects.bulk_create(lista_peliculas)
    
    return dict_peliculas

def populateRatings(m):
    """
    Carga las puntuaciones desde el archivo ratings.txt
    Formato: idUsuario \t idPelicula \t Puntuacion
    Usa el diccionario de películas para acelerar la carga
    """
    Puntuacion.objects.all().delete()
    
    lista = []
    fileobj = open(os.path.join(path, "ratings.txt"), "r", encoding='utf-8')
    for line in fileobj.readlines():
        rip = line.strip().split('\t')
        if len(rip) != 3:
            continue
        
        id_pelicula = int(rip[1])
        if id_pelicula in m:  # Verificar que la película existe
            lista.append(Puntuacion(
                idUsuario=int(rip[0]),
                pelicula=m[id_pelicula],
                puntuacion=int(rip[2])
            ))
    
    fileobj.close()
    Puntuacion.objects.bulk_create(lista)

def get_database_stats():
    """
    Devuelve estadísticas de la base de datos
    """
    num_peliculas = Pelicula.objects.count()
    num_puntuaciones = Puntuacion.objects.count()
    
    return {
        'peliculas': num_peliculas,
        'puntuaciones': num_puntuaciones
    }

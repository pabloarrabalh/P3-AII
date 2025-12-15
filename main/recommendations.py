#encoding:utf-8

from math import sqrt
from main.models import Puntuacion, Pelicula
from datetime import datetime


prefs = {}  
itemsim = {}  

def sim_pearson(prefs, p1, p2):
    """
    Calcula el coeficiente de correlación de Pearson entre p1 y p2
    """

    si = {}
    for item in prefs[p1]: 
        if item in prefs[p2]: 
            si[item] = 1

    if len(si) == 0: 
        return 0

    n = len(si)

    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])	

    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    
    if den == 0: 
        return 0

    r = num / den
    return r

def topMatches(prefs, person, n=5, similarity=sim_pearson):
    """
    Devuelve los mejores matches para person del diccionario prefs
    """
    scores = [(similarity(prefs, person, other), other) 
              for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]

def getRecommendations(prefs, person, similarity=sim_pearson):
    """
    Obtiene recomendaciones para una persona usando el promedio ponderado
    de las puntuaciones de los demás usuarios (filtrado colaborativo basado en usuarios)
    """
    totals = {}
    simSums = {}
    
    for other in prefs:

        if other == person: 
            continue
        
        sim = similarity(prefs, person, other)     

        if sim <= 0: 
            continue
        
        for item in prefs[other]:

            if item not in prefs[person] or prefs[person][item] == 0:
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                simSums.setdefault(item, 0)
                simSums[item] += sim

    if len(simSums) == 0:
        return []
    
    rankings = [(total / simSums[item], item) for item, total in totals.items()]
    rankings.sort()
    rankings.reverse()
    return rankings

def transformPrefs(prefs):
    """
    Transforma el diccionario de preferencias invirtiendo personas e items
    """
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            result[item][person] = prefs[person][item]
    return result

def loadPrefs():
    """
    Carga las preferencias desde la base de datos
    Formato: {idUsuario: {idPelicula: puntuacion}}
    """
    global prefs
    prefs = {}
    
    puntuaciones = Puntuacion.objects.all()
    for p in puntuaciones:
        usuario = p.idUsuario
        pelicula = p.pelicula.idPelicula
        puntuacion = p.puntuacion
        
        if usuario not in prefs:
            prefs[usuario] = {}
        prefs[usuario][pelicula] = puntuacion
    
    return prefs

def getUsuariosMasActivos(n=5):
    """
    Devuelve los n usuarios que más películas han puntuado
    Retorna: lista de tuplas (idUsuario, num_peliculas)
    """
    from django.db.models import Count
    
    usuarios = Puntuacion.objects.values('idUsuario').annotate(
        num_peliculas=Count('pelicula')
    ).order_by('-num_peliculas')[:n]
    
    return [(u['idUsuario'], u['num_peliculas']) for u in usuarios]

def getUsuariosSimilares(idUsuario, n=3):
    """
    Devuelve los n usuarios más similares a idUsuario
    Retorna: lista de tuplas (similaridad, idUsuario)
    """
    if idUsuario not in prefs:
        return []
    
    return topMatches(prefs, idUsuario, n=n, similarity=sim_pearson)

def recomendar_peliculas_usuario(idUsuario, fecha_limite=None, n=2):
    """
    Recomienda n películas a un usuario que no haya puntuado
    Si se proporciona fecha_limite, solo recomienda películas anteriores a esa fecha
    Usa filtrado colaborativo basado en usuarios
    Retorna: lista de tuplas (recomendacion, idPelicula)
    """
    if idUsuario not in prefs:
        return []
    
    recomendaciones = getRecommendations(prefs, idUsuario)
    
    if fecha_limite:
        peliculas_filtradas = []
        for (rec, id_pelicula) in recomendaciones:
            try:
                pelicula = Pelicula.objects.get(pk=id_pelicula)
                if pelicula.fecha and pelicula.fecha < fecha_limite:
                    peliculas_filtradas.append((rec, id_pelicula))
                    if len(peliculas_filtradas) >= n:
                        break
            except Pelicula.DoesNotExist:
                continue
        return peliculas_filtradas
    
    return recomendaciones[:n]

def obtener_actores_unicos():
    """
    Obtiene la lista de actores únicos de todas las películas
    """
    actores_set = set()
    peliculas = Pelicula.objects.all()
    
    for pelicula in peliculas:
        if pelicula.actoresPrincipales:
            actores = [actor.strip() for actor in pelicula.actoresPrincipales.split(',')]
            actores_set.update(actores)
    
    return sorted(list(actores_set))

def obtener_peliculas_por_actor(nombre_actor):
    """
    Obtiene todas las películas de un actor específico
    """
    peliculas = Pelicula.objects.filter(actoresPrincipales__icontains=nombre_actor)
    return peliculas

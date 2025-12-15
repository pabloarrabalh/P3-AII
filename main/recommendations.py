#encoding:utf-8
from django.db.models import Count
from math import sqrt
from main.models import Puntuacion, Pelicula
from datetime import datetime


prefs = {}  
itemsim = {}  

# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs, p1, p2):
    # Get the list of mutually rated items
    si = {}
    for item in prefs[p1]: 
        if item in prefs[p2]: 
            si[item] = 1

    # if they are no ratings in common, return 0
    if len(si) == 0: 
        return 0

    # Sum calculations
    n = len(si)

    # Sums of all the preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # Sums of the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])	

    # Sum of the products
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    # Calculate r (Pearson score)
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    
    if den == 0: 
        return 0

    r = num / den
    return r

# Returns the best matches for person from the prefs dictionary. 
# Number of results and similarity function are optional params.
def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other), other) 
              for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]

# Gets recommendations for a person by using a weighted average of every other user's rankings
def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}
    
    for other in prefs:
        # don't compare me to myself
        if other == person: 
            continue
        
        sim = similarity(prefs, person, other)
        
        # ignore scores of zero or lower
        if sim <= 0: 
            continue
        
        for item in prefs[other]:
            # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # Similarity * Score
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                # Sum of similarities
                simSums.setdefault(item, 0)
                simSums[item] += sim

    if len(simSums) == 0:
        return []
    
    # Create the normalized list
    rankings = [(total / simSums[item], item) for item, total in totals.items()]
    # Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings

def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            
            # Flip item and person
            result[item][person] = prefs[person][item]
    return result

def loadPrefs():
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

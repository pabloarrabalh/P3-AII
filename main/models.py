#encoding:utf-8

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Pelicula(models.Model):
    idPelicula = models.IntegerField(primary_key=True)
    titulo = models.TextField(verbose_name='Título')
    fecha = models.DateField(verbose_name='Fecha de Estreno')
    director = models.TextField(verbose_name='Director')
    actoresPrincipales = models.TextField(verbose_name='Actores Principales')

    def __str__(self):
        return self.titulo
    
    class Meta:
        ordering = ('titulo', )

class Puntuacion(models.Model):
    idUsuario = models.IntegerField(verbose_name='ID Usuario')
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE)
    puntuacion = models.IntegerField(
        verbose_name='Puntuación',
        validators=[MinValueValidator(10), MaxValueValidator(50)]
    )

    def __str__(self):
        return f"Usuario {self.idUsuario} - {self.pelicula.titulo}: {self.puntuacion}"
    
    class Meta:
        ordering = ('idUsuario', 'pelicula')
        unique_together = ('idUsuario', 'pelicula')

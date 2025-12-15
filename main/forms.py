#encoding:utf-8

from django import forms
from main.models import Pelicula
from main import recommendations

class FormularioConfirmacion(forms.Form):
    """
    Formulario de confirmación para cargar la base de datos
    """
    confirmacion = forms.BooleanField(
        label='¿Está seguro de que desea cargar la base de datos? Se borrarán todos los datos actuales.',
        required=True
    )

class FormularioPeliculasPorActor(forms.Form):
    """
    Formulario para seleccionar un actor
    """
    actor = forms.ChoiceField(
        label='Seleccione un actor',
        choices=[],
        widget=forms.Select(attrs={'class': 'uk-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super(FormularioPeliculasPorActor, self).__init__(*args, **kwargs)
        try:
            actores = recommendations.obtener_actores_unicos()
            self.fields['actor'].choices = [(actor, actor) for actor in actores]
        except:
            self.fields['actor'].choices = []

class FormularioRecomendarPeliculas(forms.Form):
    """
    Formulario para recomendar películas a un usuario
    """
    idUsuario = forms.IntegerField(
        label='ID de Usuario',
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'uk-input'})
    )
    
    fecha = forms.DateField(
        label='Fecha límite (dd/mm/aaaa)',
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(attrs={
            'class': 'uk-input',
            'placeholder': 'dd/mm/aaaa'
        })
    )

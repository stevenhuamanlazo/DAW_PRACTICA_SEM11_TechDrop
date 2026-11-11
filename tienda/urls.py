from django.urls import path
from . import views

app_name = 'tienda'

urlpatterns = [
    path('', views.home, name='home'),
    path('catalogo/', views.CatalogoView.as_view(), name='catalogo'),
]
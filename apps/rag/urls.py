from django.urls import path
from . import views

app_name = 'rag'
urlpatterns = [
    path('', views.ask, name='ask'),
]

from django.urls import path
from . import views


urlpatterns = [
    path('', views.favourites_view, name='favourites'),
    path('add_favourites/<item_id>/',
         views.add_favourites, name='add_favourites'),
    path('remove_favourites/<item_id>/<redirect_from>/',
         views.remove_favourites, name='remove_favourites'),
]
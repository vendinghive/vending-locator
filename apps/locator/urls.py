from django.urls import path
from . import views

app_name = 'locator'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('search/', views.search_locations, name='search_locations'),
    path('history/', views.search_history_view, name='search_history'),
]
from django.urls import path
from . import views

app_name = 'toolkit'

urlpatterns = [
    path('', views.toolkit_dashboard, name='dashboard'),
    path('generate/', views.generate_script, name='generate_script'),
    path('history/', views.script_history, name='script_history'),
]
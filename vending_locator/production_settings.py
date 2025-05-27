from .settings import *
import os

# Production settings
DEBUG = False
ALLOWED_HOSTS = ['vendinghive.pythonanywhere.com']  # Replace with your username

# Use MySQL database (PythonAnywhere provides MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vendinghive$vendinglocator',  # Replace yourusername
        'USER': 'vendinghive',  # Replace yourusername
        'PASSWORD': 'your_mysql_password',  # You'll set this later
        'HOST': 'vendinghive.mysql.pythonanywhere-services.com',  # Replace yourusername
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/home/vendinghive/vending_locator/staticfiles'  # Replace yourusername
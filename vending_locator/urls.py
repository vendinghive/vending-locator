# from django.contrib import admin
# from django.urls import path, include
# from django.shortcuts import redirect

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', lambda request: redirect('accounts:login')),
#     path('accounts/', include('apps.accounts.urls')),
#     path('subscriptions/', include('apps.subscriptions.urls')),
#     path('dashboard/', include('apps.locator.urls')),
#     path('toolkit/', include('apps.toolkit.urls')),
# ]
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def home_view(request):
    if request.user.is_authenticated:
        return redirect('locator:dashboard')
    else:
        return redirect('accounts:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('accounts/', include('apps.accounts.urls')),
    path('subscriptions/', include('apps.subscriptions.urls')),
    path('dashboard/', include('apps.locator.urls')),
    path('toolkit/', include('apps.toolkit.urls')),
]
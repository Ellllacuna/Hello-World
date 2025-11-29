"""
URL configuration for fileManagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from storage import views as storage_views

urlpatterns = [
    path('admin/', admin.site.urls),

    #dashboard
    path('', storage_views.dashboard, name='dashboard'),
    path('upload/', storage_views.upload_file, name='upload'),
    path('delete/<int:file_id>/', storage_views.delete_file, name='delete_file'),

    path('accounts/logout/', LogoutView.as_view(), name='logout'), #logout page
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', storage_views.signup, name='signup'), #for signup page
    path('profile/', storage_views.profile, name='profile'), #user profile
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


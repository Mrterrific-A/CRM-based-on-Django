"""luffy_crm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from stark.service.v1 import site
from web.views import account
from django.conf.urls import url,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('stark/', site.urls),
    path('login/', account.login, name='login'),
    path('logout/', account.logout, name='logout'),
    url(r'^rbac/', include(('rbac.urls', 'rbac'), namespace='rbac')),
    path('index/', account.index, name='index'),
]

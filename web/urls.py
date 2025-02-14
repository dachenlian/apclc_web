"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import re_path, path, include
import core.views

urlpatterns = [
    # re_path(r'^/$', include('core.urls', namespace='core')),
    path('admin/', admin.site.urls),
    re_path(r"^results/$", core.views.SearchListView.as_view(), name='results'),
    re_path(r'^$', core.views.HomeView.as_view(), name="home"),
    re_path('^ajax/collocation/$', core.views.collocation_view, name='collocation'),
    re_path(r'^ajax/similarity/$', core.views.similarity_view, name='similarity')
]

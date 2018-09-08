from django.urls.conf import path
from . import views

app_name = "core"

url_patterns = [
    path("", views.Home.as_view(), name='index'),
    path("results/", views.SearchListView.as_view(), name='results')
]
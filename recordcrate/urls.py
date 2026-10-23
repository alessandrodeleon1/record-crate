from django.urls import path

from . import views

app_name = "recordcrate"

urlpatterns = [
    path("", views.index, name="homepage"),
    path("listings/", views.listings, name='listings'),
]

from django.urls import path

from . import views

app_name = "recordcrate"

urlpatterns = [
    path("", views.index, name="homepage"),
    path("listings/", views.listings, name="listings"),
    path("random/", views.random_release, name="random_release"),
    path("listings/item/<int:item_id>/", views.item_detail, name="item_detail"),
    path("release/<int:release_id>/", views.release_detail, name="release_detail"),
    path("artist/<str:artist>/", views.artist_releases, name="artist_releases"),
    path(
        "users/<int:user_id>/collection/", views.user_collection, name="user_collection"
    ),
    path("users/<int:user_id>/orders/", views.order_list, name="order_list"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
]

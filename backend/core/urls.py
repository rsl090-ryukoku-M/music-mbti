from django.urls import path
from . import track_views
from . import views

urlpatterns = [
    path("dev/login", views.fake_login),
    path("tracks/search", track_views.tracks_search),
    path("diagnose_from_tracks", track_views.diagnose_from_tracks),
    path("result/<str:username>", views.result_json),
]

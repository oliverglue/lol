from django.urls import path
from .views import home, stats, sim, create_room, new_movie#join_room#session, new_movie, 
urlpatterns = [
        path("", home, name="home"),
        path("room/", create_room),
        #path("session/", session),
        path("session/new_movie", new_movie),
        path("stats/", stats),
        path("sim/", sim)
        ]
        
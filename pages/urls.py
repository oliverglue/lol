from django.urls import path
from .views import home, stats, sim, create_room, room, new_movie#join_room#session, new_movie, 
urlpatterns = [
        path("", home, name="home"),
        path("create_room/", create_room),
        path("room/", room),
        #path("session/", session),
        path("session/new_movie", new_movie),
        path("stats/", stats),
        path("sim/", sim)
        ]
        
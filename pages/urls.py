from django.urls import path
from .views import homePageView, homePageView_user1, homePageView_user2, homePageView_user3

urlpatterns = [
        path("", homePageView, name="home"),
        path("user1/", homePageView_user1),
        path("user1/LikeMovie/", homePageView_user1), 
        path("user2/", homePageView_user2),
        path("user2/LikeMovie/", homePageView_user2),
        path("user3/", homePageView_user3),
        path("user3/LikeMovie/", homePageView_user3),
        ]

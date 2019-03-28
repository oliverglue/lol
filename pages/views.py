from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
import numpy as np
import pandas as pd
import os 
import time
from .models import Database
import json as js


class backend():
    def __init__(self):
        self.all_movies = pd.read_csv("top_movies_new.csv")
        self.all_movies.set_index("const", inplace=True)
        self.similarity_matrix = pd.read_pickle("similarity_matrix")

        ##rooms are sqlite database with 
        ##(room_id, user_id, movies) as entries

    def recieve_movies(self, user_id, room_id):
        self.movies = {}
        #iterate over users in room_id, value is dict of (room_id, user_id, movies)
        for user in Database.objects.filter(room_id=room_id).values():
            self.movies[user["user_id"]] = pd.Series(eval(user["movies"]))

        #return dict with (keys,values) = (user, movies)

    def add_movie(self, user_id, room_id, movie_id, like):
        movies = Database.objects.filter(user_id=user_id, room_id=room_id).values()
        #check if user has seen any movies
        if movies.exists():
            #recieve movies in json string
            json_str = Database.objects.filter(user_id=user_id, room_id=room_id).values("movies")[0]["movies"]
           
            #convert json string to pd.series
            movies = pd.Series(eval(json_str))
            #add movie to pd.series
            movies[movie_id] = like
        else:
            movies = pd.Series(like, index=[movie_id])
        #send movies encoded as json 
        Database(user_id=user_id, room_id=room_id, movies=movies.to_json()).save()

    def new_movie(self, user_id, room_id):
        """
        1. if movie liked by other user, pick one of those
        2. else recommend a movie based on previous content 
        """
        if Database.objects.filter(room_id=room_id).exists():
            #recieve_movies
            self.recieve_movies(user_id, room_id)

            #check if liked by other users
            user_1 = self.movies.pop(user_id)
            #add other series to user_1, broadcast index and fill with 0 for user_1.
            #filter by union of isna() values
            for other_user in self.movies.keys():
                movie = self.movies[other_user]
                user_1 = user_1.add(movie, fill_value=0)[(user_1 + movie).isna()]
            if len(user_1) != 0:
                return np.random.choice(self.all_movies.index.values)#np.random.choice(user_1.index)

        return recommend_movie(user_id, room_id)

    def recommend_movie(self, user_id, room_id):
        return np.random.choice(self.all_movies.index.values)


back = backend()

def new_movie(request):
    """
    1. User GET-request with dict of (keys) = (user_id, room_id, movie_id, like)
    2. Add movie liked with add_movie()
    3. Recommend a new movie with new_movie()
    4. Return jsonResponse with all_movies[new_movie()]
    """
    tmp = {}    #iterate over (key, values) in the get-request
    for key in ["user_id", "room_id", "movie_id", "like"]:
        tmp[key] = request.GET[key]
    #add movie to db
    back.add_movie(tmp["user_id"], tmp["room_id"], tmp["movie_id"], tmp["like"])
    #recommend new movie
    i =  back.new_movie(tmp["user_id"], tmp["room_id"])
    #get info about movie as json
    json = back.all_movies.loc[int(i)].to_dict()
    json["const"] = str(i)
    json["year"] = str(json["year"])
    return JsonResponse(json)

def create_room(request):
    user_id = str(request.META.get("CSRF_COOKIE"))
    #assign random room_id, if create button
    if "create" in request.POST.keys():
        room_id = str(np.random.randint(100))
    elif "join" in request.POST.keys():
        room_id = request.POST["join"]
        #check if room_id does not exist
        if Database.objects.filter(room_id=room_id).exists() == False:
            return JsonResponse({"room_exists":False})#render(request, "home.html")
    const = np.random.choice(back.all_movies.index.values)
    json = back.all_movies.loc[const].to_dict()
    json["year"] = str(json["year"])
    json["const"] = str(const)
    return render(request, "session.html", {"room_id": room_id, "user_id":user_id, "json":(js.dumps(json))})

### Static pages ###
def home(request):
    return render(request, "home.html")

def stats(request):
    i = list(request.GET.dict().keys())[0]
    return HttpResponse(back.rooms[str(i)].to_html())

def sim(request):
    a = pd.DataFrame(back.sim, columns=["sum"])
    a["like"] = back.liked_sim 
    a["dislike"] = back.disliked_sim
    a = a.sort_values("sum", ascending=False)
    return HttpResponse(a.to_html())
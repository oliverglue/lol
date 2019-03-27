from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
import numpy as np
import pandas as pd
import os 
import time

class backend():
    """
    Attributes:
        rooms : dict[room_id:pd.DataFrame]
            all active rooms as keys and pandas dataframe as value
            columns: users, rows: movies
            e.g. users of a room is room[room_id].columns

        user : dict[user_id:room_id]
            keep track of users and rooms

        all_movies : pd.DataFrame(columns=title etc, rows=movies)

        all_movies : pd.DataFrame(columns=movies, rows=movies)
            e.g. movie i and j have a similarity value at [i,j]

    Methods:
        create_room(user_id):
            create pd.DataFrame in rooms with a random key(room_id)
            i.e. 1 column as the first user with user_id

        join_room(user_id, room_id):
            join a room with the given key if room_id exist 
            and user_id not in columns, append column as new user

        add_movie(user_id):
            add movie to row in rooms[room_id] for user_id

        new_movie(user_id):
            return new movie for user_id:
            (1) if another user liked a movie
            (2) else return content-based recommendation

        recommend_movie(user_id):
            content-based recommended movie to user_id 
            by looking at the history:
            ###TODO, improve###
            (sum of similarities for liked movies) - 
            (sum of similarities for disliked movies)
            
            
    """
    
    def __init__(self):
        self.rooms = {}
        self.users = {}
        self.all_movies = pd.read_csv("scrap_imdb_0_3000.csv")
        self.all_movies["plot"] = self.all_movies["plot"].apply(lambda x: eval(x)[0].split("::")[0])
        self.all_movies["cast"] = self.all_movies["cast"].apply(lambda x: eval(x)[:4])
        self.all_movies.set_index("const", inplace=True)
        self.similarity_matrix = pd.read_pickle("similarity_matrix")
        
    def create_room(self, user_id, room_id):
        self.rooms[room_id] = pd.DataFrame(columns=[user_id])
        self.users[user_id] = room_id
    
    def join_room(self, user_id, room_id):
        self.rooms[room_id] = self.rooms[room_id].assign(**{user_id:0})
        self.users[user_id] = room_id

    def add_movie(self, user_id, movie, like):
        room_id = self.users[user_id]
        users = self.rooms[room_id].keys()
        if movie in self.rooms[room_id].index:
            self.rooms[room_id].loc[movie,user_id] = like
        else:
            self.rooms[room_id].loc[movie] = [int(user_id == user)*like for user in users]
    
    def new_movie(self, user_id):
        room_id = self.users[user_id]
        movies = self.rooms[room_id][user_id]
        liked_movies = movies[movies == 0]
        if liked_movies.sum() != 0:
            return np.random.choice(liked_movies)
        else:
            return self.recommend_movie(user_id)
            
    def recommend_movie(self, user_id):
        room_id = self.users[user_id]
        movies = self.rooms[room_id][user_id]        
        
        self.liked_movies = movies[movies > 0].index.values
        self.disliked_movies = movies[movies < 0].index.values
        
        self.seen_movies = movies.index.values
        
        self.liked_sim = self.similarity_matrix.loc[self.liked_movies].sum().drop(self.seen_movies)
        self.disliked_sim = self.similarity_matrix.loc[self.disliked_movies].sum().drop(self.seen_movies)
        
        self.sim = self.liked_sim - 0.3*self.disliked_sim
        return self.sim.sort_values(ascending=False).index.values



back = backend()
def new_movie(request):
    t1 = time.time()

    liked_movie = int(request.GET["movie_id"])
    print(liked_movie)
    like = int(request.GET["like"])
    user_id = request.GET["user_id"]
    back.add_movie(user_id, liked_movie, like)

    i = back.new_movie(user_id)[0]
    json = back.all_movies.loc[i].to_dict()
    del json["Unnamed: 0"]
    json["const"] = str(back.all_movies.loc[i].name)
    json["year"] = str(json["year"])
    json["genres"] = str(", ".join(eval(json["genres"])[:3]))
    json["cast"] = str(", ".join(json["cast"][:4]))
    print(time.time() - t1)
    return JsonResponse(json)

def create_room(request):
    user_id = str(request.META.get('CSRF_COOKIE'))
    if  "create" in request.POST.keys():
        room_id = str(np.random.randint(100))
        back.create_room(user_id, room_id)
    elif "join" in request.POST.keys():
        room_id = request.POST["join"]
        if room_id in back.rooms.keys():
            back.join_room(user_id, room_id)
        else:
            return JsonResponse({"room_exists":False})#render(request, "home.html")
    return render(request, "session.html", {"room_id": room_id, "user_id":user_id})

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
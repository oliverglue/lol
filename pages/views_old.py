#from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
import numpy as np
import pandas as pd
import io
from IPython.display import display, HTML


class Users():
    def __init__(self, n_users, n_movies):
        self.n_users = n_users
        self.df = pd.DataFrame(columns=["movies"] + ["user"+str(x+1) for x in range(self.n_users)])
        self.df.set_index("movies", inplace=True)
        self.top_movies = np.arange(n_movies)

    def add_movie(self, user, movie, like):
    #check if movie is added by other user,
    #if true add 1 if liked
        if movie in self.df.index:
            self.df.loc[movie][user-1] = 1 * like
        #add list to row[movie]
        else:
            self.df.loc[movie] = [int(x == user-1)*like for x in range(3)]

    def liked_by_other(self, user):
        #recommend random movie
        user = "user"+str(user)
        boolean = (self.df[user] == 0)  & (self.df.sum(axis=1) > 0)
        return self.df.index[boolean].values
        #pick random movie

    def recommend_movie(self, user):
        self.liked = self.liked_by_other(user)
        #recommend random movie among liked_by_other
        if self.liked.sum() != 0:
            return np.random.choice(self.liked)
        else:
            return np.random.choice(np.setdiff1d(self.top_movies, self.df.index.values))

    def recommend_movie_content(self, similarity):
        
        self.liked_movies = users.df["user1"][users.df["user1"] > 0].index.values
        self.disliked_movies = users.df["user1"][users.df["user1"] < 0].index.values
        
        self.seen_movies = users.df["user1"].index.values
        
        self.liked_sim = similarity.loc[self.liked_movies].mean().sort_values(ascending=False)
        self.disliked_sim = similarity.loc[self.disliked_movies].mean().sort_values(ascending=False)
        
        self.liked_sim = self.liked_sim.drop(self.seen_movies)[:100]

        return self.liked_sim.index.values[0]


users = Users(3, 950)
n = []
movies = pd.read_csv("/home/glue/Dropbox/MovieMatch/scrap_imdb_0_3000.csv")
movies["plot"] = movies["plot"].apply(lambda x: eval(x)[0].split("::")[0])
movies["cast"] = movies["cast"].apply(lambda x: eval(x)[:4])
movies["title1"] = movies["title"]
movies = movies.set_index("title")

similarity = pd.read_pickle("/home/glue/Dropbox/MovieMatch/similarity_matrix")

def home(request):
    global n
    return render(request, "home.html")

def stats(request):
    return HttpResponse(users.df.to_html())
    
def sim(request):
    html = users.recommend_movie_content_sim(similarity).to_html()
    return HttpResponse(html)

def session(request): 
    global n
    new = (request.META["REMOTE_ADDR"])
    if new not in n:
        n.append(new)
    users.add_movie(1, "The Dark Knight", 1)
    users.add_movie(1, "The Dark Knight Rises", 1)
    return render(request, "session.html", {"user": "user_"+str(len(n))})

def newMovie(request):
    like = request.GET["like"]
    #i = np.random.randint(400)
    i = users.recommend_movie_content(similarity)
    users.add_movie(1, i, int(like))
    #print(JsonResponse(top_movies.loc[i].to_dict()))
    return render(request, "ajax.html", movies.loc[i].to_dict())
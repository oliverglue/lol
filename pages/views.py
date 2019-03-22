from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
import numpy as np
import pandas as pd



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
            self.df.loc[movie] = [int(x == user-1)*like for x in range(self.n_users)]

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

users = Users(3, 950)

def homePageView(request):  
    rendered = render_to_string("pick_user.html")
    return HttpResponse(rendered)

def homePageView_user1(request):
    r = users.recommend_movie(1)
    tmp = (list(request.GET.lists()))
    if len(tmp) == 1:
        tmp = tmp[0]
        movie, like = tmp[0], tmp[1][0]
        users.add_movie(1, movie, int(like))
    rendered = render_to_string("home.html", {"var":str(r), "abc":"user1"}) 
    return HttpResponse(rendered)
    
def homePageView_user2(request):
    r = users.recommend_movie(2)
    tmp = (list(request.GET.lists()))
    if len(tmp) == 1:
        tmp = tmp[0]
        movie, like = tmp[0], tmp[1][0]
        users.add_movie(2, movie, int(like))
    rendered = render_to_string("home.html", {"var":str(r), "abc":"user2"}) 
    return HttpResponse(rendered)
    
def homePageView_user3(request):
    r = users.recommend_movie(3)
    print(users.df)
    tmp = (list(request.GET.lists()))
    if len(tmp) == 1:
        tmp = tmp[0]
        movie, like = tmp[0], tmp[1][0]
        users.add_movie(3, movie, int(like))
    rendered = render_to_string("home.html", {"var":str(r), "abc":"user3"}) 
    return HttpResponse(rendered)


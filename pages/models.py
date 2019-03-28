from django.db import models

import pandas as pd 

class Database(models.Model):
	room_id = models.TextField("room_id", max_length=20)
	user_id = models.TextField("user_id", max_length=20)
	movies = models.TextField("movies", max_length=100000)



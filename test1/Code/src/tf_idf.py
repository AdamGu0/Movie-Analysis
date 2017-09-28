import pandas as pd
import numpy as np
import phase1util as putil
movie_actor = pd.read_csv("phase1_dataset/movie-actor.csv");
genome_tags = pd.read_csv("phase1_dataset/genome-tags.csv");
mltags = pd.read_csv("phase1_dataset/mltags.csv");
genres_movie = pd.read_csv("phase1_dataset/mlmovies.csv");
movie_actor.head();

actor_movie_dict = putil.getActorMovie(movie_actor.actorid,movie_actor.movieid,movie_actor.actor_movie_rank)
print(actor_movie_dict[369237])
movie_tag_dict = putil.getMoiveTag(mltags.movieid, mltags.tagid, mltags.timestamp)
print(movie_tag_dict[3963])

#Task two
genres_movie_dict = putil.getGenresMovie(genres_movie.genres, genres_movie.movieId)

#Task3 userId as input, print tag vector
user_tag_dict = putil.getUserTag(mltags.userid, mltags.tagid, mltags.timestamp)
print(user_tag_dict[146])
import pandas as pd
import src.phase1util as putil
import fileinput
from pathlib import Path
import sys
import src.actor as actor
import src.genre as genre
import src.user as user
import src.differentiate_genre as differentiate_genre
movie_actor = pd.read_csv("phase1_dataset/movie-actor.csv")
genome_tags = pd.read_csv("phase1_dataset/genome-tags.csv")
mltags = pd.read_csv("phase1_dataset/mltags.csv")
tag_name_dict = putil.buildTagNameDict(genome_tags)
genres_movie = pd.read_csv("phase1_dataset/mlmovies.csv")
mlratings = pd.read_csv("phase1_dataset/mlratings.csv")


def process(commands):
    command_name = commands[0]
    if command_name == 'print_actor_vector':
        actor.printActor(movie_actor, mltags, tag_name_dict, int(commands[1]), commands[2])
    elif command_name == 'print_genre_vector':
        genre.printGenre(genres_movie, mltags, tag_name_dict, commands[1], commands[2])
    elif command_name == 'print_user_vector':
        user.printUser(mlratings, mltags, tag_name_dict, int(commands[1]), commands[2])
    elif command_name == 'differentiate_genre':
        differentiate_genre.print_diff(genres_movie, mltags, tag_name_dict, commands[1], commands[2], commands[3])

command_name = sys.argv[1]
# if command_name == 'print_actor_vector':
#     actor.printActor(movie_actor, mltags, tag_name_dict, int(sys.argv[2]), sys.argv[3])
# elif command_name == 'print_genre_vector':
#     genre.printGenre(genres_movie, mltags,  tag_name_dict,sys.argv[2] ,sys.argv[3])
# elif command_name == 'print_user_vector':
#     user.printUser(mlratings, mltags, tag_name_dict, int(sys.argv[2]), sys.argv[3])
# elif command_name == 'differentiate genre':
#     differentiate_genre.print_diff(genres_movie, mltags, tag_name_dict, sys.argv[2], sys.argv[3], sys.argv[4])

command_file = Path(command_name)

if command_file.is_file():
    for line in fileinput.input():
        line = line.rstrip()
        process(line.split(' '))
else:
    process(sys.argv[1:len(sys.argv)])
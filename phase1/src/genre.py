import phase1util as putil
import pandas as pd
from pathlib import Path
import numpy as np
import math
genres_movie = pd.read_csv("phase1_dataset/mlmovies.csv")
mltags = pd.read_csv("phase1_dataset/mltags.csv")
genome_tags = pd.read_csv("phase1_dataset/genome-tags.csv")
tag_name_dict = putil.buildTagNameDict(genome_tags)


def calGenreTagTF(genre_tag_dict, genreid):
    tag_weight_TS_dict = putil.calTagWeight(genre_tag_dict, genreid, 'timestamp')
    return putil.normalize_tag_weight(tag_weight_TS_dict)

def calGenreTFIDF(genre_tag_dict, genreid):
    tag_weight_dict = calGenreTagTF(genre_tag_dict, genreid)
    tags = putil.getDocTagsById(genre_tag_dict, genreid)
    genre_tag_idf = putil.calDocFullIDF(genre_tag_dict, 'genre')
    return putil.computeIFIDF(tags,tag_weight_dict, genre_tag_idf )

def printGenre(genres_movie, mltags,  tag_name_dict, genreid,model):
    genre_tag_dict = prepareData(genres_movie, mltags)
    res = {}
    if model == 'TF':
        res = calGenreTagTF(genre_tag_dict, genreid)
    else:
        res = calGenreTFIDF(genre_tag_dict, genreid)
    putil.print_result(model, 'genre', genreid, tag_name_dict, res)

#return actor_tag_dict = {actorid:[{"tagid":, "timestamp":}}
def prepareData(genres_movie, mltags):
    outter_join = genres_movie.set_index("movieid").join(mltags.set_index("movieid"), how="outer")
    outter_join = outter_join.drop('userid', 1)
    outter_join = outter_join.drop('moviename', 1)
    outter_join.to_csv("out/genresoutterjoin.csv", index=False, encoding='utf-8')
    outter_join = pd.read_csv("out/genresoutterjoin.csv")
    # print(outter_join['actorid'][0])
    genres_tag_dict_file = Path("out/genres_tag_dict.npy")
    genres_tag_dict = {}
    if genres_tag_dict_file.is_file():
        genres_tag_dict = np.load('out/genres_tag_dict.npy').item()
    else:
        genres_tag_dict = dataframe_to_dict_by_key(outter_join, key='genres')
        np.save('out/genres_tag_dict.npy', genres_tag_dict)
    return genres_tag_dict

def dataframe_to_dict_by_key(dataframe, key = 'None'):
    dict = {}
    if key == 'None':
        pass
    else:
        for i in range(0, len(dataframe.index)):
            if i%10000 == 0:
                print(i)
            genre_str = dataframe[key][i]
            genres = genre_str.split('|')
            for genre in genres:
                if not genre in dict:
                    dict[genre] = []
                subdict = {}
                for col_name in list(dataframe):
                    if not col_name == key:
                        if col_name == 'tagid' and not math.isnan(dataframe[col_name][i]):
                            subdict[col_name] = int(dataframe[col_name][i])
                        else:
                            subdict[col_name] = dataframe[col_name][i]
                dict[genre].append(subdict)
    return dict

def findAllGenres(genres_movie):
    genres_index_dict = genres_movie.genres
    genre_cnt_dict = {}
    for index in genres_movie.genres.keys():
        genre_str = genres_index_dict[index]
        genres = genre_str.split('|')
        for genre in genres:
            if not genre in genre_cnt_dict:
                genre_cnt_dict[genre] = 0
            genre_cnt_dict[genre] += 1
    return genre_cnt_dict

printGenre(genres_movie, mltags,  tag_name_dict,'Horror' ,"TF-IDF")
printGenre(genres_movie, mltags,  tag_name_dict,'Horror' ,"TF")
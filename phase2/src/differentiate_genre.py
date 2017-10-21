from src.genre import prepareData
import src.phase1util as putil
import pandas as pd
import math

# genres_movie = pd.read_csv("phase1_dataset/mlmovies.csv")
# mltags = pd.read_csv("phase1_dataset/mltags.csv")
# genome_tags = pd.read_csv("phase1_dataset/genome-tags.csv")
# tag_name_dict = putil.buildTagNameDict(genome_tags)

def print_diff(genres_movie, mltags,  tag_name_dict, g1,g2, model):
    genres_tag_dict = prepareData(genres_movie, mltags)

    g1_res = {}
    g2_res = {}
    if model == 'TF-IDF-DIFF':
        print("TF-IDF-DIFF here")
        g1_res, g2_res= calTFIDFDIFF(g1, g2, genres_tag_dict)
    elif model == 'P-DIFF1':
        print("P-DIFF1")
        g1_res = calPDIFF(genres_tag_dict, g1, g2, PDIFF=1)
        g2_res = calPDIFF(genres_tag_dict, g2, g1, PDIFF=1)
    elif model == 'P-DIFF2':
        g1_res = calPDIFF(genres_tag_dict, g1, g2, PDIFF=2)
        g2_res = calPDIFF(genres_tag_dict, g2, g1, PDIFF=2)
    putil.print_result(model, 'genre_diff', g1, tag_name_dict, g1_res)
   # putil.print_result(model, 'genre_diff', g2, tag_name_dict, g2_res)


def mapMovieToGenre(genres_tag_dict, g1_g2_movie_tag_dict):
    genres_tag_movie = {}
    for genreid in genres_tag_dict:
        movielist = genres_tag_dict[genreid]
        for movie_dict in movielist:
            movieid = movie_dict['movieid']
            if movieid in g1_g2_movie_tag_dict:
                if not genreid in genres_tag_movie:
                    genres_tag_movie[genreid] = g1_g2_movie_tag_dict[movieid]
    return genres_tag_movie

#return {movieid :{tagid:cnt}} movie tag dic given by docid
def movieTag(doc_tag_dict, docid):
    doc_list =  doc_tag_dict[docid]
    movie_tag_dict = {}
    for item_dict in doc_list:
        movieid = item_dict['movieid']
        tagid = item_dict['tagid']
        if math.isnan(tagid):
            continue
        if not movieid in movie_tag_dict:
            movie_tag_dict[movieid] = {}
        if not tagid in movie_tag_dict[movieid]:
            movie_tag_dict[movieid][tagid] = 0
        movie_tag_dict[movieid][tagid] += 1
    return movie_tag_dict

def mergeG1G2(g1_movie_tag_dict, g2_movie_tag_dict):
    movie_tag_dict = dict(g1_movie_tag_dict)
    for movieid in g2_movie_tag_dict:
        if not movieid in movie_tag_dict:
            movie_tag_dict[movieid] = g2_movie_tag_dict[movieid]
        else:
            g2_tag_dict = g2_movie_tag_dict[movieid]
            for tagid in g2_tag_dict:
                if not tagid in movie_tag_dict[movieid]:
                    movie_tag_dict[movieid][tagid] = g2_tag_dict[tagid]
                else:
                    movie_tag_dict[movieid][tagid] += g2_tag_dict[tagid]
    return movie_tag_dict

def calTFIDFDIFF(g1, g2, genres_tag_dict):
    g1_movie_tag_dict = movieTag(genres_tag_dict, g1)
    g2_movie_tag_dict = movieTag(genres_tag_dict, g2)
    g1_g2_movie_tag_dict = mergeG1G2(g1_movie_tag_dict, g2_movie_tag_dict)
    genres_tag_movie = mapMovieToGenre(genres_tag_dict, g1_g2_movie_tag_dict)
    g1_TFIDF = putil.calDocTFIDF(genres_tag_dict, g1, 'genre', movie = True, movie_tag_dict = genres_tag_movie)
    g2_TFIDF = putil.calDocTFIDF(genres_tag_dict, g2, 'genre', movie = True, movie_tag_dict = g1_g2_movie_tag_dict)
    return g1_TFIDF, g2_TFIDF

def calPDIFF(genres_tag_dict, g1, g2, PDIFF = 1):
    g1_movie_tag_dict = movieTag(genres_tag_dict, g1)
    g2_movie_tag_dict = movieTag(genres_tag_dict, g2)
    g1_g2_movie_tag_dict = mergeG1G2(g1_movie_tag_dict, g2_movie_tag_dict)
    #all_tag_dict = getAllTags(g1_g2_movie_tag_dict)
    g1_tag_dict = getAllTags(g1_movie_tag_dict)
    #g2_tag_dict = getAllTags(g2_movie_tag_dict)

    M = len(g1_g2_movie_tag_dict)
    tag_weight_res = {}
    for tagid in g1_tag_dict:
        m1,m2 = cntMoviesContainTag(g1_g2_movie_tag_dict, tagid)
        if PDIFF == 1:
            R = len(g1_movie_tag_dict)
            r, _= cntMoviesContainTag(g1_movie_tag_dict, tagid)
            m = m1
        else:
            R = len(g2_movie_tag_dict)
            _, r = cntMoviesContainTag(g2_movie_tag_dict, tagid)
            m = m2
        if not tagid in tag_weight_res:
            tag_weight_res[tagid] = math.log((r+m/M)*(M-R-m+r+m/M)/((m-r+1)*(R-r+1)))*abs((r+m/M)/(R+1) - (m-r+m/M)/(M - R + 1))
    return tag_weight_res

def cntMoviesContainTag(movie_tag_dict, tag_id):
    cnt = 0
    notcnt = 0
    for movieid in movie_tag_dict:
        if tag_id in movie_tag_dict[movieid]:
            cnt += 1
        else:
            notcnt += 1
    return cnt, notcnt

def getAllTags(movie_tag_dict):
    all_tag_dict = {}
    for movieid in movie_tag_dict:
        for tag_id in movie_tag_dict[movieid]:
            if not tag_id in all_tag_dict:
                all_tag_dict[tag_id] = 1
            else:
                all_tag_dict[tag_id] += 1
    return all_tag_dict


# movie_actor = pd.read_csv("phase1_dataset/movie-actor.csv")
# genome_tags = pd.read_csv("phase1_dataset/genome-tags.csv")
# mltags = pd.read_csv("phase1_dataset/mltags.csv")
# tag_name_dict = putil.buildTagNameDict(genome_tags)
# genres_movie = pd.read_csv("phase1_dataset/mlmovies.csv")
# mlratings = pd.read_csv("phase1_dataset/mlratings.csv")
#
# print_diff(genres_movie, mltags,  tag_name_dict, 'Western','IMAX', 'TF-IDF-DIFF')



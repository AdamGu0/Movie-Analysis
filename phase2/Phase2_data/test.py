import numpy.linalg as linalg
import numpy as np
import src.phase1util as putil
from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD
from sklearn.decomposition import LatentDirichletAllocation as LDA
import pandas as pd
import src.genre as genre
import src.actor as actor
import math
from pathlib import Path


movie_actor = pd.read_csv("Phase2_data/movie-actor.csv")
genome_tags = pd.read_csv("Phase2_data/genome-tags.csv")
mltags = pd.read_csv("Phase2_data/mltags.csv")
tag_name_dict = putil.buildTagNameDict(genome_tags)
genres_movie = pd.read_csv("Phase2_data/mlmovies.csv")
mlratings = pd.read_csv("Phase2_data/mlratings.csv")
actor_imdb = pd.read_csv("Phase2_data/imdb-actor-info.csv")

#actor.printActor(movie_actor, mltags,  tag_name_dict,17838 ,"TF-IDF")
#return genre_list
def convertgenretoindex(genres_movie):
    genre_cnt_dict = genre.findAllGenres(genres_movie)
    return dict_to_list(genre_cnt_dict)

#return actor list
def convert_actor_to_index(actor_tag_dict):
    list = dict_to_list(actor_tag_dict)
    list.sort()
    return list

#return     a list of doc id
def dict_to_list(doc_dict):
    doc_list = []
    for doc_id in doc_dict:
        doc_list.append(doc_id)

    return doc_list

def reverse_index_doc(index_doc):
    doc_index = {}
    for index in range(len(index_doc)):
        doc_index[index_doc[index]] = index
    return doc_index

# must make sure no duplicates in index feature
def reverse_index_feature(index_feature):
    feature_index = {}
    for index in range(len(index_feature)):
        feature_index[index_feature[index]] = index
    return feature_index

#input      doc_id_dict     {index : doc_id}
#           feature_id_dict {index : feature_id}
#           value_matrix    {doc_id :{feature_id : value}}
# return 2 d nparray. with rows doc_id, cols feature_id
def build_matrix(doc_id_dict, feature_id_dict, value_matrix):
    matrix = []
    row = len(doc_id_dict)
    col = len(feature_id_dict)
    for i in (row):
        for j in range(col):
            doc_id = doc_id_dict[i]
            feature_id = feature_id_dict[j]
            matrix[i][i] = value_matrix[doc_id][feature_id]
    return matrix

#input doc_id_dict  {index : doc_id}
#
#return 2d matrix rows are doc_id, cols are feature_id
def calTFIDFMatrix(doc_id_list, feature_index_dict, doc_feature_dict, doc_name, feature_name = 'tag'):
    #initiate a matrix with row = doc_id_dict.length and col = feature_id_dict
    matrix = np.zeros((len(doc_id_list), len(feature_index_dict)))
    for i in range(len(doc_id_list)):
        # return {feature_id : weight}
        feature_weight_dict = putil.calDocFeatureTFIDF(doc_feature_dict, doc_id_list[i], doc_name, feature_name = feature_name)
        for feature in feature_weight_dict:
            matrix[i][feature_index_dict[feature]] = feature_weight_dict[feature]
    return matrix

def count_feature_by_id(doc_feature_dict, doc_id, feature_name):
    feature_list = list(doc_feature_dict[doc_id])
    # remove tag_id which is nan
    doc_tag_list = [x for x in feature_list if not math.isnan(x[feature_name +'id'])]
    feature_cnt_dict = {}
    for i in range(len(doc_tag_list)):
        if not doc_tag_list[i][feature_name +'id'] in feature_cnt_dict:
            feature_cnt_dict[doc_tag_list[i][feature_name +'id']] = 1
        else:
            feature_cnt_dict[doc_tag_list[i][feature_name +'id']] += 1
    return feature_cnt_dict

        #return 2d matrix rows are doc_id, cols are feature_id
def calCOUNTMatrix(doc_id_list, feature_index_dict, doc_feature_dict, feature_name = 'tag'):
    #initiate a matrix with row = doc_id_dict.length and col = feature_id_dict
    matrix = np.zeros((len(doc_id_list), len(feature_index_dict)))
    for i in range(len(doc_id_list)):
        # return {feature_id : cnt}
        feature_weight_dict = count_feature_by_id(doc_feature_dict, doc_id_list[i], feature_name)
        for feature in feature_weight_dict:
            matrix[i][feature_index_dict[feature]] = feature_weight_dict[feature]
    return matrix


def calSVD(matrix):
    U, s, V = linalg.svd(matrix, full_matrices=True)
    return U.dot(s)

def topKLatentTopic(matrix, k, doc_index, method):
    res = []
    feature_matrix = []
    if method == 'SVD':
        svd = TruncatedSVD(n_components=k)
        svd.fit(matrix.transpose())
        feature_matrix = svd.components_.transpose()
        res = feature_matrix[doc_index]
        res1 = svd
    elif method == 'PCA':
        pca = PCA(n_components=k)
        pca.fit(matrix.transpose())
        feature_matrix = pca.components_.transpose()
        res = feature_matrix[doc_index]
        res1 = pca
    elif method == 'LDA':
        lda = LDA(n_components=k)
        lda.fit(matrix.transpose())
        feature_matrix = lda.components_.transpose()
        res = feature_matrix[doc_index]
        res1 = lda
    res.sort()
    res[:] = res[::-1]
    return res, feature_matrix

#return     k smallest distance with doc_index
def get_distance(matrix, doc_index, k):
    vec = matrix[doc_index]

    #a list of tuple (index, distance)
    distance_list = []
    for index in range(len(matrix)):
        if not index == doc_index:
            dist = np.linalg.norm(vec - matrix[index])
            distance_list.append((index, dist))
    #sort the distance_list by distance in ascending order
    distance_list.sort(key=lambda tup: tup[1])
    return distance_list[0:k]

###task2
def dataframe_to_dict_by_key(dataframe, key = 'None', feature_name = 'genre'):
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
                        if col_name == feature_name and not math.isnan(dataframe[col_name][i]):
                            subdict[col_name] = int(dataframe[col_name][i])
                        else:
                            subdict[col_name] = dataframe[col_name][i]
                dict[genre].append(subdict)
    return dict

def prepare_genre_actor(genres_movie, movie_actor):
    outter_join = genres_movie.join(movie_actor.set_index("movieid"), how="outer", on='movieid')
    outter_join = outter_join.drop('moviename', 1)
    outter_join = outter_join.drop('year', 1)
    outter_join.to_csv("out/genresoutterjoin.csv", index=False, encoding='utf-8')
    outter_join = pd.read_csv("out/genresoutterjoin.csv")
    # print(outter_join['actorid'][0])
    # genres_tag_dict_file = Path("out/genres_tag_dict.npy")
    # genres_tag_dict = {}
    # if genres_tag_dict_file.is_file():
    #     genres_tag_dict = np.load('out/genres_tag_dict.npy').item()
    # else:
    genres_actor_dict = dataframe_to_dict_by_key(outter_join, key='genres', feature_name = 'actorid')
    #np.save('out/genres_tag_dict.npy', genres_tag_dict)
    return genres_actor_dict

genres_actor_dict = prepare_genre_actor(genres_movie, movie_actor)
actor_index_dict = reverse_index_feature(actor_imdb.id)
genre_list = convertgenretoindex(genres_movie)
genre_index_dict = reverse_index_doc(genre_list)
matrix = calTFIDFMatrix(genre_list, actor_index_dict, genres_actor_dict, 'genre', feature_name='actor')
cnt_matrix = calCOUNTMatrix(genre_list, actor_index_dict, genres_actor_dict, feature_name = 'actor')

top4SVD = topKLatentTopic(matrix, 4, 0, "SVD")
top4PCA = topKLatentTopic(matrix, 4, 0, "PCA")
top4LDA = topKLatentTopic(cnt_matrix, 4, 0, "LDA")
print()
print(topKLatentTopic(matrix, 4, 0, "PCA"))




###task4
#given a movie, first pick all the actors in this movie, then remove all the
def select_actors(movie_actor, movie_id):
    selected_df = movie_actor.loc[movie_actor['movieid'] == movie_id]
    selected_actor = selected_df['actorid']
    actor_dict = {}
    for actor_id in selected_actor:
        actor_dict[actor_id] = 0
    actor_list = []
    for actor_id in actor_dict:
        actor_list.append(actor_id)
    return actor_list

def delete_select(actor_list, selected_actor_list):
    new_actor_list = []
    for actor_id in actor_list:
        if not actor_id in selected_actor_list:
            new_actor_list.append(actor_id)
    return new_actor_list

selected_actor_list = select_actors(movie_actor, 3189)
actor_tag_dict = actor.prepareData(movie_actor, mltags)
tag_index_dict = reverse_index_feature(genome_tags.tagId)
actor_list = convert_actor_to_index(actor_tag_dict)
actor_list = delete_select(actor_list, selected_actor_list)
matrix = calTFIDFMatrix(actor_list, tag_index_dict, actor_tag_dict, 'actor')
cnt_matrix = calCOUNTMatrix(actor_list, tag_index_dict, actor_tag_dict)

top5SVD, svd_latent_matrix = topKLatentTopic(matrix, 5, 0, "SVD")
top5PCA, pca_latent_matrix = topKLatentTopic(matrix, 5, 0, "PCA")
top5LDA, lda_latent_matrix = topKLatentTopic(cnt_matrix, 5, 0, "LDA")

act_TFIDF_dist_list = get_distance(matrix, 0, 10)
act_svd_dist_list = get_distance(svd_latent_matrix, 0, 10)
act_pca_dist_list = get_distance(pca_latent_matrix, 0, 10)
act_lda_dist_list = get_distance(lda_latent_matrix, 0, 10)
###task 3


actor_tag_dict = actor.prepareData(movie_actor, mltags)
tag_index_dict = reverse_index_feature(genome_tags.tagId)
actor_list = convert_actor_to_index(actor_tag_dict)
matrix = calTFIDFMatrix(actor_list, tag_index_dict, actor_tag_dict, 'actor')
cnt_matrix = calCOUNTMatrix(actor_list, tag_index_dict, actor_tag_dict)

top5SVD, svd_latent_matrix = topKLatentTopic(matrix, 5, 0, "SVD")
top5PCA, pca_latent_matrix = topKLatentTopic(matrix, 5, 0, "PCA")
top5LDA, lda_latent_matrix = topKLatentTopic(cnt_matrix, 5, 0, "LDA")

act_TFIDF_dist_list = get_distance(matrix, 0, 10)
act_svd_dist_list = get_distance(svd_latent_matrix, 0, 10)
act_pca_dist_list = get_distance(pca_latent_matrix, 0, 10)
act_lda_dist_list = get_distance(lda_latent_matrix, 0, 10)

###task 1
genres_tag_dict = genre.prepareData(genres_movie, mltags)
tag_index_dict = reverse_index_feature(genome_tags.tagId)
genre_list = convertgenretoindex(genres_movie)
genre_index_dict = reverse_index_doc(genre_list)
matrix = calTFIDFMatrix(genre_list, tag_index_dict, genres_tag_dict, 'genre')
cnt_matrix = calCOUNTMatrix(genre_list, tag_index_dict, genres_tag_dict)

top4SVD = topKLatentTopic(matrix, 4, 0, "SVD")
top4PCA = topKLatentTopic(matrix, 4, 0, "PCA")
top4LDA = topKLatentTopic(cnt_matrix, 4, 0, "LDA")
print()
print(topKLatentTopic(matrix, 4, 0, "PCA"))
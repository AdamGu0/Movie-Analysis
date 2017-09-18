import phase1util as putil
import pandas as pd
from pathlib import Path
import numpy as np
import math

def printUser(mlratings, mltags, tag_name_dict, userid, model):
    user_tag_dict = prepareData(mlratings, mltags)
    res = {}
    if model == 'TF':
        res = putil.calDocTagTF(user_tag_dict, userid)
    else:
        res = putil.calDocTFIDF(user_tag_dict, userid, 'user')
    putil.print_result(model, 'user', userid, tag_name_dict, res)


# return actor_tag_dict = {actorid:[{"actor_movie_rank":, "tagid":, "timestamp":}}
def prepareData(mlratings, mltags):
    #mltags = mltags.drop('movieid', 1)
    # print(outter_join['actorid'][0])
    user_tag_dict_file = Path("out/user_tag_dict.npy")
    user_tag_dict = {}
    if user_tag_dict_file.is_file():
        user_tag_dict = np.load('out/user_tag_dict.npy').item()
    else:
        user_tag_dict = putil.dataframe_to_dict_by_key(mltags, key='userid')
        user_tag_dict = mergeusers(mlratings, user_tag_dict)
        np.save('out/user_tag_dict.npy', user_tag_dict)
    return user_tag_dict

def mergeusers(mlratings, user_tag_dict):
    rating_user_dict = get_mlrating_user(mlratings)
    for user_id in rating_user_dict.keys():
        if not user_id in user_tag_dict.keys():
            user_tag_dict[user_id] = []
        for movieid in rating_user_dict[user_id]:
            user_tag_dict[user_id].append({'movieid':movieid, 'tagid':math.nan, 'timestamp':math.nan})
    return user_tag_dict

def get_mlrating_user(mlratings):
    user_dict = {}
    for index in range(0, len(mlratings.userid)):
        if index % 10000 == 0:
            print(index)
        userid = mlratings.userid[index]
        if not userid in user_dict:
            user_dict[userid] = []
        user_dict[userid].append(mlratings.movieid[index])
    return user_dict

# printUser(mlratings, mltags, tag_name_dict, 146, 'TF')
# printUser(mlratings, mltags, tag_name_dict, 146, 'TF-IDF')

#
# #input  userid_dict    {index : user_id}
# #       tagid_dict      {index : tag_id}
# #       timestamp_dict  {index : timestamp}
# #Please note the lenght of movieid_dict, tagid_dict, timestamp_dict should be same
# #return user_tag_dict      {user_id:list_of_tuplep(tag_id,timestamps)}
# #                           the list is sorted by timestamps
# def getUserTag(userid_dict, tagid_dict, timestamp_dict):
#     user_tag_dict = {}
#     for i in range(0, len(userid_dict)):
#         user_id = userid_dict[i]
#         tag_id = tagid_dict[i]
#         timestamp = timestamp_dict[i]
#         if not user_id in user_tag_dict.keys():
#             user_tag_dict[user_id] = []
#         user_tag_dict[user_id].append((tag_id, timestamp))
#     # for user_id in user_tag_dict:
#     #     user_tag_dict[user_id].sort(key=lambda tup:tup[1], reverse=True)
#     return user_tag_dict
#
# def getUserTF(user_tag_dict):
#     user_tagVector = {}
#     for user_id in user_tag_dict:
#         user_tagVector[user_id] = getUserTFByUserId(user_tag_dict[user_id])
#     return user_tagVector
# #input user_tag_dict      {user_id:list_of_tuplep(tag_id,timestamps)}
# #return tag_weight_dict     {tag_id, tfidf}  the weight is normalized
# def getUserTFIDFByUserId(user_id, user_tag_dict):
#     #compute unnormalized weight for each tag for the specifed user
#     tag_list = user_tag_dict[user_id]
#     tag_list.sort(key=lambda tup:tup[1], reverse=True)
#     for i in range(0, len(tag_list)):
#         tag_list[i][1] = len(tag_list) - i
#     tag_weight_dict = putil.getTF(tag_list)
#     tags = {}
#     documents = {}
#     for user_id in user_tag_dict:
#         if not user_id in documents:
#             documents[user_id] = {}
#         tagTupleList = user_tag_dict[user_id]
#         for tagTuple in tagTupleList:
#             tag_id = tagTuple(0)
#             if not tag_id not in documents[user_id]:
#                 documents[user_id][tag_id] = 1
#             else:
#                 documents[user_id][tag_id] += 1
#             if tag_id not in tags:
#                 tags[tag_id] = 1
#             else:
#                 tags[tag_id] += 1
#     idf_dict = putil.getIDFList(documents, tags)
#     return putil.computeIFIDF(tags,tag_weight_dict, idf_dict )
#
# #return tag_weight_dict     {tag_id, weight}  the weight is normalized
# def getUserTFByUserId(user_id, user_tag_dict):
#     #compute unnormalized weight for each tag for the specifed user
#     tag_list = user_tag_dict[user_id]
#     tag_list.sort(key=lambda tup:tup[1], reverse=True)
#     for i in range(0, len(tag_list)):
#         tag_list[i][1] = len(tag_list) - i
#     return putil.getTF(tag_list)



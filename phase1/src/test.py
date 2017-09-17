import pandas as pd
import numpy as np
from pathlib import Path
import sys
print(sys.argv)
import math
movie_actor = pd.read_csv("phase1_dataset/movie-actor.csv");
genome_tags = pd.read_csv("phase1_dataset/genome-tags.csv");
mltags = pd.read_csv("phase1_dataset/mltags.csv");



caller = pd.DataFrame({'key': ['K0', 'K1', 'K2', 'K3', 'K4', 'K5', 'K5'],
                         'A': ['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A5'],
                         'C': ['1',  '1', '3', '3', '2', '2', '3']})

other = pd.DataFrame({'key': ['K0', 'K1', 'K6'],
                        'B': ['B0', 'B1', 'B6']})

def dataframe_to_dict_by_key(dataframe, key = 'None'):
    dict = {}
    if key == 'None':
        pass
    else:
        for i in range(0, len(dataframe.index)):
            if i%10000 == 0:
                print(i)
            if not dataframe[key][i] in dict:
                dict[dataframe[key][i]] = []
            subdict = {}
            for col_name in list(dataframe):
                if not col_name == key:
                    subdict[col_name] = dataframe[col_name][i]
            dict[dataframe[key][i]].append(subdict)
    return dict


# print(list(caller))
# print(dataframe_to_dict_by_key(caller, key = 'key'))
# print(other['key'][1])
# outter_join = caller.set_index("key").join(other.set_index("key"), how="outer")
# left_join = caller.set_index("key").join(other.set_index("key"))
left_join = movie_actor.set_index("movieid").join(mltags.set_index("movieid"))

outter_join = movie_actor.set_index("movieid").join(mltags.set_index("movieid"), how="outer")
outter_join = outter_join.drop('userid', 1)
outter_join.to_csv("out/outterjoin.csv", index=False, encoding='utf-8')
outter_join = pd.read_csv("out/outterjoin.csv");
#print(outter_join['actorid'][0])
actor_tag_dict_file = Path("out/actor_tag_dict.npy")
actor_tag_dict = {}
if actor_tag_dict_file.is_file():
    actor_tag_dict = np.load('out/actor_tag_dict.npy').item()
else:
    actor_tag_dict = dataframe_to_dict_by_key(outter_join, key = 'actorid')
    np.save('out/actor_tag_dict.npy', actor_tag_dict)
#actor_tag_dict = {actorid:[{"actor_movie_rank":, "tagid":, "timestamp":}}
print(actor_tag_dict)
def timeToNumber(time_str):
    num = 0
    for c in time_str:
        if c.isdigit():
            num = num * 10 + int(c)
    return num
print(timeToNumber("2007-11-20 20:16:15"))

def calActorTagTF(actor_tag_dict, actorid):
    tag_weight_TS_dict = calTagWeight(actor_tag_dict, actorid, 'timestamp')
    tag_weight_rank_dict = calTagWeight(actor_tag_dict, actorid, 'actor_movie_rank')
    actor_tag_tf_dict = {}
    for tagid in tag_weight_TS_dict.keys():
        actor_tag_tf_dict[tagid] = tag_weight_TS_dict[tagid] + tag_weight_rank_dict[tagid]
    return normalize_tag_weight(actor_tag_tf_dict)


#input  dict    docs_dict   {docid : [attributes]}
#       int     docid
#       str     attribute_str
#calculate the tag weight for docid based on attribute_str.
#return {tagid, weight}
def calTagWeight(docs_dict, docid, attribute_str):
    doc_tag_list = list(docs_dict[docid])
    tag_list = {}
    #remove tag_id which is nan
    for tag_TS in doc_tag_list:
        tag_id = tag_TS['tagid']
        if math.isnan(tag_id):
            doc_tag_list.remove(tag_TS)
    #sort the tag by TS in decending order
    doc_tag_list.sort(key=lambda tup: tup['timestamp'], reverse=True)
    max_attri = 0
    min_attri = 0
    if attribute_str == 'timestamp':
        min_attri = timeToNumber(doc_tag_list[len(doc_tag_list)-1][attribute_str])
    else:
        min_attri = doc_tag_list[len(doc_tag_list) - 1][attribute_str]
    for tag_TS in doc_tag_list:
        tag_id = tag_TS['tagid']
        if not tag_id in tag_list:
            tag_list[tag_id] = 0
        if attribute_str == 'timestamp':
            tag_list[tag_id] += (timeToNumber(tag_TS[attribute_str]) - min_attri)
        else:
            tag_TS[attribute_str] - min_attri
    #normalization
    tag_list = normalize_tag_weight(tag_list)
    return tag_list

#return {tagid, weight}
def tagTimeWeight(docs_dict, docid):
    doc_tag_list = list(docs_dict[docid])
    tag_list = {}
    #remove tag_id which is nan
    for tag_TS in doc_tag_list:
        tag_id = tag_TS['tagid']
        if math.isnan(tag_id):
            doc_tag_list.remove(tag_TS)
    #sort the tag by TS in decending order
    doc_tag_list.sort(key=lambda tup: tup['timestamp'], reverse=True)
    maxTS = timeToNumber(doc_tag_list[0]['timestamp'])
    minTS = timeToNumber(doc_tag_list[len(doc_tag_list)-1]['timestamp'])
    for tag_TS in doc_tag_list:
        tag_id = tag_TS['tagid']
        if not tag_id in tag_list:
            tag_list[tag_id] = 0
        tag_list[tag_id] += (timeToNumber(tag_TS['timestamp']) - minTS)
    #normalization
    tag_list = normalize_tag_weight(tag_list)
    return tag_list

#return {tagid, weight}
def tagRankWeight(docs_dict, docid):
    doc_tag_list = list(docs_dict[docid])
    tag_list = {}
    #remove tag_id which is nan
    for tag_TS in doc_tag_list:
        tag_id = tag_TS['tagid']
        if math.isnan(tag_id):
            doc_tag_list.remove(tag_TS)
    #sort the tag by TS in decending order
    doc_tag_list.sort(key=lambda tup: tup['actor_movie_rank'], reverse=True)
    maxRank = doc_tag_list[0]['actor_movie_rank']
    minRank = doc_tag_list[len(doc_tag_list)-1]['actor_movie_rank']
    for tag_TS in doc_tag_list:
        tag_id = tag_TS['tagid']
        if not tag_id in tag_list:
            tag_list[tag_id] = 0
        tag_list[tag_id] += tag_TS['actor_movie_rank'] - minRank
    #normalization
    tag_list = normalize_tag_weight(tag_list)
    return tag_list

def normalize_tag_weight(tag_list):
    values = tag_list.values()
    maxweight = max(values)
    minweight = min(values)
    for tag_id in tag_list.keys():
        tag_list[tag_id] = (tag_list[tag_id] - minweight) / (maxweight - minweight)
    return tag_list
tagTimeWeight(actor_tag_dict, 63934)
# left_join.to_csv("out/leftjoin.csv", index=False, encoding='utf-8')
# outter_join.to_csv("out/outterjoin.csv", index=False, encoding='utf-8')





docs = {"dd":{1:2,2:3, 3:2}, "ff":{2:3,4:5}}
print(docs["dd"])
for features in docs.values():
    print(features)
    featureId = 1
    if featureId in features:
        print(features[featureId])




















#create a dictionary of dictionary
num ={} #{1:3,2:{31:2}, 31:21, 3:{2 : 3}}
# if 3 in num.keys():
#     print(num[3][2])
# num.pop(1)
# print(num)
# num[4] = 44
# print(num)
moive_id = 1
actor_id = 2
actor_rank = 3
if not actor_id in num.keys():
    num[actor_id] = {}
num[actor_id][moive_id] = actor_rank
print(num)

a = [1, 2, 3]
for i in range(0, len(a)-1):
    print(a[i])



















#input  movieid_dict    {index : movie_id}
#       tagid_dict      {index : tag_id}
#       timestamp_dict  {index : timestamp}
#Please note the lenght of movieid_dict, tagid_dict, timestamp_dict should be same
#return movie_tag_dict      {movie_id:{tag_id:list_of_timestamps}}
def getMoiveTag(movieid_dict, tagid_dict, timestamp_dict):
    movie_tag_dict = {}
    for i in range(0, len(movieid_dict)):
        movie_id = movie_tag_dict[i]
        tag_id = tagid_dict[i]
        timestamp = timestamp_dict[i]
        if not movie_id in movie_tag_dict.keys():
            movie_tag_dict[tag_id] = []
        movie_tag_dict[movie_id][tag_id].append(timestamp)
    return movie_tag_dict


#input  actor_movie_dict    {actor_id:{movie_id, rank}}
#       movie_tag_dict      {movie_id:{tag_id:list_of_timestamps}}
#return actor_tag_dict      {actor_id:{tag_id:list_of(timestamps, rank)}}
def getActorTag(actor_movie_dict, movie_tag_dict):
    actor_tag_dict = {}
    for actor_id in actor_tag_dict:
        movieid_rank_dict = actor_movie_dict[actor_id]
        for movie_id in movieid_rank_dict:
            rank = movieid_rank_dict[movie_id]
            if movie_id in movie_tag_dict.keys():
                pass
        if not actor_id in actor_movie_dict.keys():
            actor_movie_dict[actor_id] = {}
            actor_movie_dict[actor_id][moive_id] = actor_rank
    return actor_tag_dict

#input   actorid_dict   {index : actor_id}
#        movieid_dict   {index : movie_id}
#        actorrank_dict {index : rank}
#Please note all the input dictionary should have the same length
#return  actor_movie_dict {actor_id:{movie_id, rank}}
def getActorMovie(actorid_dict, movieid_dict, actorrank_dict):
    len = len(actorid_dict)
    actor_movie_dict = {}
    for i in range(0, len):
        actor_id = actorid_dict[i]
        moive_id = movieid_dict[i]
        actor_rank = actorrank_dict[i]
        if not actor_id in actor_movie_dict.keys():
            actor_movie_dict[actor_id] = {}
            actor_movie_dict[actor_id][moive_id] = actor_rank
    return actor_movie_dict
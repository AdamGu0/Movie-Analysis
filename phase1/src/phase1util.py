import math
import numpy as np
from pathlib import Path


#input  dict    docs_dict   {docid : [attributes]}
#       int     docid
#       str     attribute_str
#calculate the tag weight for docid based on attribute_str.
#return {tagid, weight}
def calTagWeight(docs_dict, docid, attribute_str):
    doc_tag_list = list(docs_dict[docid])
    tag_list = {}
    #remove tag_id which is nan
    doc_tag_list = [x for x in doc_tag_list if not math.isnan(x['tagid'])]
    # for tag_TS in doc_tag_list:
    #     tag_id = tag_TS['tagid']
    #     if math.isnan(tag_id):
    #         doc_tag_list.remove(tag_TS)
    if len(doc_tag_list) == 0:
        return {}

    #sort the tag by TS in decending order
    doc_tag_list.sort(key=lambda tup: tup[attribute_str], reverse=True)
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
        sub = 0
        if attribute_str == 'timestamp':
            sub = (timeToNumber(tag_TS[attribute_str]) - min_attri)
        else:
            sub = tag_TS[attribute_str] - min_attri
        if sub == 0:
            sub = 0.000001
        tag_list[tag_id] += sub
    #normalization
    tag_list = normalize_tag_weight(tag_list)
    return tag_list


def normalize_tag_weight(tag_list):
    values = tag_list.values()
    values_sum = sum(values)
    if values_sum == 0:
        print("values_sum is 0, tag_list length is {}, tag_list is {}".format(len(tag_list), tag_list))
        return []
    for tag_id in tag_list.keys():
        tag_list[tag_id] = tag_list[tag_id]  / values_sum
    return tag_list

def timeToNumber(time_str):
    num = 0
    for c in time_str:
        if c.isdigit():
            num = num * 10 + int(c)
    return num

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
                    if col_name == 'tagid' and not math.isnan(dataframe[col_name][i]):
                        subdict[col_name] = int(dataframe[col_name][i])
                    else:
                        subdict[col_name] = dataframe[col_name][i]
            dict[dataframe[key][i]].append(subdict)
    return dict


#input   genre_dict     {index : genre}
#        movieid_dict   {index : movie_id}
#Please note all the input dictionary should have the same length
#return  genres_movie_dict {genre:[movie]}
def getGenresMovie(genre_dict, movieid_dict):
    genres_movie_dict = {}
    for i in range(0, len(genre_dict)):
        genre_id = genre_dict[i]
        moive_id = movieid_dict[i]
        if not genre_id in genres_movie_dict.keys():
            genres_movie_dict[genre_id] = []
        genres_movie_dict[genre_id].append(moive_id)
    return genres_movie_dict


#return    genres_tag_dict {genre_id : [(tag_id, timestamp)]}
def getGenresTag(genres_movie_dict, movie_tag_dict):
    genres_tag_dict = {}
    for genre_id in genres_movie_dict:
        if not genre_id not in genres_tag_dict:
            genres_movie_dict[genre_id] = []
            for movie_id in genres_movie_dict[genre_id]:
                for tag_id in movie_tag_dict[movie_id]:
                    TSlist = movie_tag_dict[movie_id][tag_id]
                    for ts in TSlist:
                        genres_movie_dict[genre_id].append((tag_id, ts))
    return genres_tag_dict


# def getTFAll(docs_tag_dict):
#     docs_tagVector = {}
#     for doc_id in docs_tag_dict:
#         docs_tagVector[doc_id] = getUserTFByUserId(docs_tag_dict[doc_id])
#     return docs_tagVector
#input user_tag_dict      {user_id:list_of_tuplep(tag_id,timestamps)}
#return tag_weight_dict     {tag_id, tfidf}  the weight is normalized
def getTFIDFById(id, docs_tag_dict):
    #compute unnormalized weight for each tag for the specifed user
    tag_list = docs_tag_dict[id]
    tag_list.sort(key=lambda tup:tup[1], reverse=True)
    for i in range(0, len(tag_list)):
        tag_list[i][1] = len(tag_list) - i
    tag_weight_dict = getTF(tag_list)
    tags = {}
    documents = {}
    for doc_id in docs_tag_dict:
        if not doc_id in documents:
            documents[doc_id] = {}
        tagTupleList = docs_tag_dict[doc_id]
        for tagTuple in tagTupleList:
            tag_id = tagTuple(0)
            if not tag_id not in documents[doc_id]:
                documents[doc_id][tag_id] = 1
            else:
                documents[doc_id][tag_id] += 1
            if tag_id not in tags:
                tags[tag_id] = 1
            else:
                tags[tag_id] += 1
    idf_dict = getIDFList(documents, tags)
    return computeIFIDF(tags,tag_weight_dict, idf_dict )


#input   actorid_dict   {index : actor_id}
#        movieid_dict   {index : movie_id}
#        actorrank_dict {index : rank}
#Please note all the input dictionary should have the same length
#return  actor_movie_dict {actor_id:{movie_id, rank}}
def getActorMovie(actorid_dict, movieid_dict, actorrank_dict):
    actor_movie_dict = {}
    for i in range(0, len(actorid_dict)):
        actor_id = actorid_dict[i]
        moive_id = movieid_dict[i]
        actor_rank = actorrank_dict[i]
        if not actor_id in actor_movie_dict.keys():
            actor_movie_dict[actor_id] = {}
        actor_movie_dict[actor_id][moive_id] = actor_rank
    return actor_movie_dict

#input  movieid_dict    {index : movie_id}
#       tagid_dict      {index : tag_id}
#       timestamp_dict  {index : timestamp}
#Please note the lenght of movieid_dict, tagid_dict, timestamp_dict should be same
#return movie_tag_dict      {movie_id:{tag_id:(list_of_timestamps)}}
def getMoiveTag(movieid_dict, tagid_dict, timestamp_dict):
    movie_tag_dict = {}
    for i in range(0, len(movieid_dict)):
        movie_id = movieid_dict[i]
        tag_id = tagid_dict[i]
        timestamp = timestamp_dict[i]
        if not movie_id in movie_tag_dict.keys():
            movie_tag_dict[movie_id] = {}
        if not tag_id in movie_tag_dict[movie_id].keys():
            movie_tag_dict[movie_id][tag_id] = []
        movie_tag_dict[movie_id][tag_id].append(timestamp)
    return movie_tag_dict


#return tags {tagid:count of docs which contains tagid
def prepForIDF(doc_tag_dict):
    tags = {}
    documents = {}
    for doc_id in doc_tag_dict:
        if not doc_id in documents:
            documents[doc_id] = {}
        tagList = doc_tag_dict[doc_id]
        for tag_attr in tagList:
            tag_id = tag_attr['tagid']
            if math.isnan(tag_id):
                continue
            if not tag_id in documents[doc_id]:
                documents[doc_id][tag_id] = 0
            documents[doc_id][tag_id] += 1
            if tag_id not in tags:
                tags[tag_id] = 1
            else:
                tags[tag_id] += 1
    return tags, documents

def computeIFIDF(tags,tag_weight_dict, idf_dict ):
    userTagifidf = {}
    tag_idf_dict = {}
    for tag_id in tags:
        tag_idf_dict[tag_id] = idf_dict[tag_id]
    tag_idf_dict = normalize_tag_weight(tag_idf_dict)
    for tag_id in tags:
        tf = tag_weight_dict[tag_id]
        idf = tag_idf_dict[tag_id]
        userTagifidf[tag_id] = tf*idf
    return normalize_tag_weight(userTagifidf)


#input  tag_list            [(tag_id, weight)] (may have multiple tags)
#return tag_weight_dict     {tag_id, weight}  the weight is normalized
def getTF(tag_list):
    length = len(tag_list)
    #for normalization
    sum = 0
    for i in range(0, length):
        sum += tag_list[i][1]

    tag_weight_dict = {}
    for i in range(0, length):
        tag_id = tag_list[i][0]
        weight = tag_list[i][1]
        if not tag_id in tag_weight_dict:
            tag_weight_dict[tag_id] = 0
        tag_weight_dict[tag_id] += weight/sum

    return tag_weight_dict



#input  documents   {docId:{featureId:count}}
#       features    [featureId]
#return idf_dict   {featureId : idf}
def getIDFList(documents, features):
    idf_dict = {}
    for featureId in features:
        idf_dict[featureId] = getIDF(documents, featureId)
    return idf_dict


#input  documents   {docId:{featureId:count}}
#       featureId
#return IDf = log(N/m)
#N = number of all the documents
#m = number of documents with fetures in it
def getIDF(documents, featureId):
    N = len(documents)
    m = 0
    for features in documents.values():
        if featureId in features.keys():
            m += 1
    res = -1
    if m != 0:
        res = math.log(N / m)
    return res

#return tag_list [tagid, tagname, weight] sorted by weight in decesending order
def convertDictToList(tag_weight_dict, tag_name_dict):
    tag_list = []
    for tagid in tag_weight_dict:
        tup = (tagid, tag_name_dict[tagid] ,tag_weight_dict[tagid])
        tag_list.append(tup)
    tag_list.sort(key=lambda tup: tup[2], reverse=True)
    return tag_list

#return {tagid, tagname}
def buildTagNameDict(genome_tags):
    tag_name_dict = {}
    for index in range(0, len(genome_tags.tagId)):
        tagid = genome_tags.tagId[index]
        tagname = genome_tags.tag[index]
        tag_name_dict[tagid] = tagname
    return tag_name_dict


def calFullIDF(doc_tag_dict):
    tags, documents = prepForIDF(doc_tag_dict)
    return getIDFList(documents, tags)


#return doc_tag_idf{tagid:idf}   all the tags appear in all the docs
def calDocFullIDF(doc_tag_dict, docname):
    doc_tag_idf_file = Path("out/{}_tag_idf.npy".format(docname))
    if doc_tag_idf_file.is_file():
        doc_tag_idf = np.load('out/{}_tag_idf.npy'.format(docname)).item()
    else:
        doc_tag_idf = calFullIDF(doc_tag_dict)
        np.save('out/{}_tag_idf.npy'.format(docname), doc_tag_idf)
    return doc_tag_idf

#return res {tag_id, count}
def getDocTagsById(doc_tag_dict, docid):
    res = {}
    for item in doc_tag_dict[docid]:
        tagid = item['tagid']
        if math.isnan(tagid):
            continue
        if not tagid in res:
            res[tagid] = 0
        res[tagid] += 1
    return res


def print_result(model, docname, docid, tag_name_dict, res):
    print("{}_id : {}, model : {}, format : <tag_id, tag_name, weight>".format(docname, docid, model))
    res = convertDictToList(res, tag_name_dict)
    for tup in res:
        print("{},{},{}".format(tup[0], tup[1], tup[2]))
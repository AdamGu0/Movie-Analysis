import phase1util as putil
import pandas as pd
from pathlib import Path
import numpy as np


# def calActorTagTF(actor_tag_dict, actorid):
#     tag_weight_TS_dict = putil.calTagWeight(actor_tag_dict, actorid, 'timestamp')
#     tag_weight_rank_dict = putil.calTagWeight(actor_tag_dict, actorid, 'actor_movie_rank')
#     actor_tag_tf_dict = {}
#     for tagid in tag_weight_TS_dict.keys():
#         actor_tag_tf_dict[tagid] = tag_weight_TS_dict[tagid] + tag_weight_rank_dict[tagid]
#     return putil.normalize_tag_weight(actor_tag_tf_dict)
#
# def calActorTFIDF(actor_tag_dict, actorid):
#     tag_weight_dict = calActorTagTF(actor_tag_dict, actorid)
#     tags = putil.getDocTagsById(actor_tag_dict, actorid)
#     actor_tag_idf = putil.calDocFullIDF(actor_tag_dict, 'actor')
#     return putil.computeIFIDF(tags,tag_weight_dict, actor_tag_idf )

# #return actor_tag_idf{tagid:idf}   all the tags appear in all the actors
# def calActorFullIDF(actor_tag_dict):
#     actor_tag_idf_file = Path("out/actor_tag_idf.npy")
#     if actor_tag_idf_file.is_file():
#         actor_tag_idf = np.load('out/actor_tag_idf.npy').item()
#     else:
#         actor_tag_idf = putil.calFullIDF(actor_tag_dict)
#         np.save('out/actor_tag_idf.npy', actor_tag_idf)
#     return actor_tag_idf
#
# #return res {tag_id, count}
# def getActorTagsById(actor_tag_dict, actorid):
#     res = {}
#     for item in actor_tag_dict[actorid]:
#         tagid = item['tagid']
#         if not tagid in res:
#             res[tagid] = 0
#         res[tagid] += 1
#     return res

def printActor(movie_actor, mltags,  tag_name_dict, actorid,model):
    actor_tag_dict = prepareData(movie_actor, mltags)

    res = {}
    if model == 'TF':
        res = putil.calDocTagTF(actor_tag_dict, actorid, isactor = True)
    else:
        res = putil.calDocTFIDF(actor_tag_dict, actorid, 'actor')
    putil.print_result(model, 'actor', actorid, tag_name_dict, res)


#return actor_tag_dict = {actorid:[{"actor_movie_rank":, "tagid":, "timestamp":}}
def prepareData(movie_actor, mltags):
    outter_join = movie_actor.set_index("movieid").join(mltags.set_index("movieid"), how="outer")
    outter_join = outter_join.drop('userid', 1)
    outter_join.to_csv("out/outterjoin.csv", index=False, encoding='utf-8')
    outter_join = pd.read_csv("out/outterjoin.csv");
    # print(outter_join['actorid'][0])
    actor_tag_dict_file = Path("out/actor_tag_dict.npy")
    actor_tag_dict = {}
    if actor_tag_dict_file.is_file():
        actor_tag_dict = np.load('out/actor_tag_dict.npy').item()
    else:
        actor_tag_dict = putil.dataframe_to_dict_by_key(outter_join, key='actorid')
        np.save('out/actor_tag_dict.npy', actor_tag_dict)
    return actor_tag_dict

# printActor(movie_actor, mltags,  tag_name_dict,1484 ,"TF-IDF")
# printActor(movie_actor, mltags,  tag_name_dict,1484 ,"TF")
import csv
import math
import os
import numpy as np
import logging
from scipy.io.matlab import loadmat
from sktensor import dtensor, cp_als
from tensorly.decomposition import parafac
import tensorly.backend as BE
from tensorly.kruskal_tensor import kruskal_to_tensor, kruskal_to_vec
from tensorly.__init__ import set_backend 
from sklearn.cluster import KMeans
import t2cd_helper as helper


#set_backend('numpy')
def do_t2c():
    ## load data from csv
    print(">Loading data。。。")
    movie_csv = csv.reader(open('Phase2_data/mlmovies.csv'))
    
    actor_csv = csv.reader(open('Phase2_data/imdb-actor-info.csv'))
    
    m_a_csv = csv.reader(open('Phase2_data/movie-actor.csv'))
    ## data preparation
    movie_data=[]
    actor_data=[]
    m_a_data=[]
     
    header = True
    for row in movie_csv:
        if header:
            header=False
            continue
        movie_data.append(row)
        
    header = True
    for row in actor_csv:
        if header:
            header=False
            continue
        actor_data.append(row)
        
    header = True
    for row in m_a_csv:
        if header:
            header=False
            continue
        m_a_data.append(row)
    
    
    movie_list=[]
    actor_list=[]
    year_list=[]
            
    for row in movie_data:
        movie_list.append(int(row[0]))
        year_list.append(int(row[2]))
        
    for row in actor_data:
        actor_list.append(int(row[0]))
      
    year_set=set(year_list)
    
    year_list=[]
    for y in year_set:
        year_list.append(y)
    
    movie_list.sort()    
    year_list.sort()
    actor_list.sort()
    
    
    
    # 1. create an actor-movie-year tensor 
    print(">Creating tensor。。。")
    la= len(actor_list)
    lm= len(movie_list)
    ly= len(year_list)  
    tensor=np.zeros((la,lm,ly)) 
    
    for a in range(0,la):
        for m in range(0,lm):
            for y in range(0,ly):
                actor=actor_list[a]
                movie=movie_list[m]
                year=year_list[y]
                for row in m_a_data:
                    if (movie==int(row[0]) and actor==int(row[1])):
                        for row2 in movie_data:
                            if (movie==int(row2[0]) and year==int(row2[2])):
                                tensor[a][m][y]=1.0
                                #print('bingo!')   
    
    #test print for taget actor, movie and year. Remove later
    '''
    ta=0
    tm=0
    ty=0
    
    for a in range(0,la):
        if(actor_list[a]==1072584):
            ta=a
    for m in range(0,lm):
        if(movie_list[m]==3189):
            tm=m
    for y in range(0,ly):
        if(year_list[y]==2000):
            ty=y
    print(ta)
    print(tm)
    print(ty)                 
    print(tensor[ta][tm][ty]) 
    '''
    #2. perform CP on the tensor with target rank 5 with ALS algorithm
    print(">Performing CP decomposition。。。")
    TX=dtensor(tensor)
    #set target rank to 5
    tr=5
    TN=BE.tensor(tensor)
    factors=parafac(TN, rank=5, n_iter_max=500, init='svd', tol=10e-5)
    factors_random=parafac(TN, rank=5, n_iter_max=500, init='random', tol=10e-5, random_state=1234, verbose=0)
    rec=kruskal_to_tensor(factors)
    rec_rand=kruskal_to_tensor(factors_random)
    error = BE.norm(rec - TN, 2)
    error /= BE.norm(TN, 2)
    error_rand = BE.norm(rec_rand - TN, 2)
    error_rand /= BE.norm(TN, 2)
    tol_norm_2 = 10e-2
    tol_max_abs = 10e-2
    
    #error tests, remove from the final version
    '''
    print("-------------------------------")
    print(error)
    print(error_rand)
    print("-------------------------------")
    print("actor factors")
    print(factors[0])
    print("-------------------------------")
    print("movie factors")
    print(factors[1])
    print("-------------------------------")
    print("year factors")
    print(factors[2])
    print("-------------------------------")
    '''
    
    #3. Compute weights of latent semantics, and print them
    actor_topicK=np.empty(la)
    movie_topicK=np.empty(lm)
    year_topicK=np.empty(ly)
    topic_weights=[]
    topic_actor_var=[]
    topic_movie_var=[]
    topic_year_var=[]
    var_actor_all=0
    var_movie_all=0
    var_year_all=0
    for k in range(0,tr):
        for ai in range(0,la):
            actor_topicK[ai]=factors[0][ai][k]
        for mi in range(0,lm):
            movie_topicK[mi]=factors[1][mi][k]
        for yi in range(0,ly):
            year_topicK[yi]=factors[2][yi][k]
            
        topic_actor_var.append(np.var(actor_topicK))
        topic_movie_var.append(np.var(movie_topicK))
        topic_year_var.append(np.var(year_topicK))
        
    actor_norm = [float(i)/sum(topic_actor_var) for i in topic_actor_var]
    movie_norm = [float(i)/sum(topic_movie_var) for i in topic_movie_var]
    year_norm = [float(i)/sum(topic_year_var) for i in topic_year_var]
    
    '''
    print(actor_norm)
    print(movie_norm)
    print(year_norm)
    '''
    for k in range(0,tr):
        topic_weights.append((k+1,actor_norm[k]+movie_norm[k]+year_norm[k]))
    
    topic_weights.sort(key=lambda x: x[1],reverse=True)
    
    print("-------------------------------")
    print(">Report the latent semantics in decreasing order:")
    for k in range(0,tr):
        print("topic"+str(topic_weights[k][0]))
    print("-------------------------------")
    
    #partition into 5 groups
    
    #Apply k-means clustering to each factor matrix. [TODO]Using cosine to measure similarity
    print(">Doing partitions...")
    '''
    actor1=factors[0][0]
    actor2=factors[0][1]
    print(actor1)
    print(actor2)
    cos_a1_a2=actor1.dot(actor2)
    print(cos_a1_a2)
    '''
    
    km1 = KMeans(n_clusters=5, init='k-means++', max_iter=500, n_init=1, verbose=False)
    km2 = KMeans(n_clusters=5, init='k-means++', max_iter=500, n_init=1, verbose=False)
    km3 = KMeans(n_clusters=5, init='k-means++', max_iter=500, n_init=1, verbose=False)
    factors1=factors[0]
    factors2=factors[1]
    factors3=factors[2]
    km1.fit(factors1)
    labels1 = km1.labels_
    km2.fit(factors2)
    labels2 = km2.labels_
    km3.fit(factors3)
    labels3 = km3.labels_
    #test print, remove from final version.
    '''
    print(len(labels1))
    print(labels1)
    print(len(labels2))
    print(labels2)
    print(len(labels3))
    print(labels3)
    '''
    #output results into csv files
    helper.group_csv_write("t2c_partition_actor.csv","actorID",actor_list,labels1)
    helper.group_csv_write("t2c_partition_movie.csv","movieID",movie_list,labels2)
    helper.group_csv_write("t2c_partition_year.csv","year",year_list,labels3)
    print("t2c_partition_actor.csv created.")
    print("t2c_partition_movie.csv created.")
    print("t2c_partition_year.csv created.")
    print("----------------------------------")

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
def do_t2d():
    ## load data from csv
    print(">Loading data。。。")
    
    movie_csv = csv.reader(open('Phase2_data/mlratings.csv'))
    
    tag_csv = csv.reader(open('Phase2_data/genome-tags.csv'))
    
    m_t_csv = csv.reader(open('Phase2_data/mltags.csv'))
    ## data preparation
    movie_data=[]
    tag_data=[]
    m_t_data=[]
     
    header = True
    for row in movie_csv:
        if header:
            header=False
            continue
        movie_data.append(row)
        
    header = True
    for row in tag_csv:
        if header:
            header=False
            continue
        tag_data.append(row)
        
    header = True
    for row in m_t_csv:
        if header:
            header=False
            continue
        m_t_data.append(row)
    
    
    movie_list=[]
    tag_list=[]
    rating_list=[]
            
    for row in movie_data:
        movie_list.append(int(row[0]))
        rating_list.append(int(row[3]))
        
    for row in tag_data:
        tag_list.append(int(row[0]))
    
    movie_set=set(movie_list)  
    rating_set=set(rating_list)
    
    rating_list=[]
    for y in rating_set:
        rating_list.append(y)
        
    movie_list=[]
    for m in movie_set:
        movie_list.append(m)
    
    movie_list.sort()    
    rating_list.sort()
    tag_list.sort()
    
    
    # 1. create an tag-movie-rating tensor 
    print(">Creating tensor。。。")
    la= len(tag_list)
    lm= len(movie_list)
    ly= len(rating_list)  
    tensor=np.zeros((la,lm,ly)) 
    
    for a in range(0,la):
        for m in range(0,lm):
            for y in range(0,ly):
                tag=tag_list[a]
                movie=movie_list[m]
                rating=rating_list[y]
                for row in m_t_data:
                    if (movie==int(row[1]) and tag==int(row[2])):
                        ratings=[]
                        for row2 in movie_data:
                            if (movie==int(row2[0])):
                                ratings.append(float(row2[3]))
    
                        if(len(ratings)!=0):  
                            avg_r=sum(ratings)/len(ratings)
                            if(float(rating) >= avg_r):
                                tensor[a][m][y]=1.0
                                #print('bingo!')
                                
    #test print for taget tag, movie and rating. Remove later                               
    '''                            
    ta=0
    tm=0
    ty=0
    
    for a in range(0,la):
        if(tag_list[a]==1128):
            ta=a
    for m in range(0,lm):
        if(movie_list[m]==7247):
            tm=m
    for y in range(0,ly):
        if(rating_list[y]==1):
            ty=y
    print(ta)
    print(tm)
    print(ty)                 
    print(tensor[ta][tm][ty]) 
    '''
    #2. perform CP on the tensor with target rank 5 with ALS algorithm
    print(">Performing CP decomposition。。。")
    tr=5
    TN=BE.tensor(tensor)
    #factors=parafac(TN, rank=tr, n_iter_max=500, init='svd', tol=10e-5)
    #factors_random=parafac(TN, rank=tr, n_iter_max=500, init='random', tol=10e-5, random_state=1234, verbose=0)
    factors=parafac(TN, rank=tr, n_iter_max=500, init='random', tol=10e-5, random_state=1234, verbose=0)
    rec=kruskal_to_tensor(factors)
    #rec_rand=kruskal_to_tensor(factors_random)
    error = BE.norm(rec - TN, 2)
    error /= BE.norm(TN, 2)
    #error_rand = BE.norm(rec_rand - TN, 2)
    #error_rand /= BE.norm(TN, 2)
    tol_norm_2 = 10e-2
    tol_max_abs = 10e-2
    
    #error tests, remove from the final version
    '''
    print("-------------------------------")
    print('error:')
    print(error)
    print(error_rand)
    print("-------------------------------")
    print("tag factors")
    print(factors[0])
    print("-------------------------------")
    print("movie factors")
    print(factors[1])
    print("-------------------------------")
    print("rating factors")
    print(factors[2])
    print("-------------------------------")
    '''
    
    #3. Compute weights of latent semantics, and print them
    tag_topicK=np.empty(la)
    movie_topicK=np.empty(lm)
    rating_topicK=np.empty(ly)
    topic_weights=[]
    topic_tag_var=[]
    topic_movie_var=[]
    topic_rating_var=[]
    var_tag_all=0
    var_movie_all=0
    var_rating_all=0
    for k in range(0,tr):
        for ai in range(0,la):
            tag_topicK[ai]=factors[0][ai][k]
        for mi in range(0,lm):
            movie_topicK[mi]=factors[1][mi][k]
        for yi in range(0,ly):
            rating_topicK[yi]=factors[2][yi][k]
            
        topic_tag_var.append(np.var(tag_topicK))
        topic_movie_var.append(np.var(movie_topicK))
        topic_rating_var.append(np.var(rating_topicK))
        
    tag_norm = [float(i)/sum(topic_tag_var) for i in topic_tag_var]
    movie_norm = [float(i)/sum(topic_movie_var) for i in topic_movie_var]
    rating_norm = [float(i)/sum(topic_rating_var) for i in topic_rating_var]
    
    '''
    print(tag_norm)
    print(movie_norm)
    print(rating_norm)
    '''
    for k in range(0,tr):
        topic_weights.append((k+1,tag_norm[k]+movie_norm[k]+rating_norm[k]))
    
    topic_weights.sort(key=lambda x: x[1],reverse=True)
    
    print("-------------------------------")
    print(">Report the latent semantics in decreasing order:")
    for k in range(0,tr):
        print("topic"+str(topic_weights[k][0]))
    print("-------------------------------")
    
    #partition into 5 groups
    
    #Apply k-means clustering to each ftag matrix. [TODO]Using cosine to measure similarity
    print(">Doing partitions。。。")
    '''
    tag1=factors[0][0]
    tag2=factors[0][1]
    print(tag1)
    print(tag2)
    cos_a1_a2=tag1.dot(tag2)
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
    helper.group_csv_write("t2d_partition_tag.csv","tagID",tag_list,labels1)
    helper.group_csv_write("t2d_partition_movie.csv","movieID",movie_list,labels2)
    helper.group_csv_write("t2d_partition_rating.csv","rating",rating_list,labels3)
    print("t2d_partition_tag.csv created.")
    print("t2d_partition_movie.csv created.")
    print("t2d_partition_rating.csv created.")
    print("---------------------------------------")
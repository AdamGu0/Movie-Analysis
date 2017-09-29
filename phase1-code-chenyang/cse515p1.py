import csv
import os
import argparse
import MySQLdb
import math
from datetime import datetime

dbuser="root"
dbpw="911016"
dbname="cse515p1"

#connect to database
def loaddata():
    print ("Connecting to the database...")
    db = MySQLdb.connect("localhost",dbuser,dbpw,dbname )    
    cursor = db.cursor()
    db.set_character_set('utf8')
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
     
    #load csv into database
    
    print ("Loading data from the csv files into the database。。。")
    
    #load table1-------------------------------------------------
    print ("Loading data from genometags。。。")
    cursor.execute("DROP TABLE IF EXISTS genometags;")
    sql="CREATE TABLE genometags(tagId CHAR(255),tag CHAR(255));"
    cursor.execute(sql);
    csv_data = csv.reader(open('phase1_dataset/genome-tags.csv'))
    
    header = True
        
    for row in csv_data:
        if header:
            header=False
            continue
        cursor.execute('INSERT INTO genometags(tagId, tag) VALUES(%s,%s)',row)
        
    #close the connection to the database.
    db.commit()
    
    #load table2-------------------------------------------------
    print ("Loading data from actorinfo。。。")
    cursor.execute("DROP TABLE IF EXISTS actorinfo;")
    sql="CREATE TABLE actorinfo(actorId CHAR(255),name CHAR(255),gender CHAR(255));"
    cursor.execute(sql);
    csv_data = csv.reader(open('phase1_dataset/imdb-actor-info.csv','r', encoding='UTF-8'))
    
    header = True
        
    for row in csv_data:
        if header:
            header=False
            continue
        cursor.execute('INSERT INTO actorinfo(actorId, name, gender) VALUES(%s,%s,%s)',row)
        
    #close the connection to the database.
    db.commit()
    
    #load table3-------------------------------------------------
    print ("Loading data from mlmovies。。。")
    cursor.execute("DROP TABLE IF EXISTS mlmovies;")
    sql="CREATE TABLE mlmovies(movieId CHAR(255),movieName CHAR(255),genres CHAR(255));"
    cursor.execute(sql);
    csv_data = csv.reader(open('phase1_dataset/mlmovies.csv'))
    
    header = True
        
    for row in csv_data:
        if header:
            header=False
            continue
        cursor.execute('INSERT INTO mlmovies(movieId, movieName, genres) VALUES(%s,%s,%s)',row)
        
    #close the connection to the database.
    db.commit()
    
    #load table4-------------------------------------------------
    print ("Loading data from mltags。。。")
    cursor.execute("DROP TABLE IF EXISTS mltags;")
    sql="CREATE TABLE mltags(userId CHAR(255),movieId CHAR(255),tagId CHAR(255),timestamp CHAR(255));"
    cursor.execute(sql);
    csv_data = csv.reader(open('phase1_dataset/mltags.csv'))
    
    header = True
        
    for row in csv_data:
        if header:
            header=False
            continue
        cursor.execute('INSERT INTO mltags(userId,movieId,tagId,timestamp) VALUES(%s,%s,%s,%s)',row)
        
    #close the connection to the database.
    db.commit()
    
    #load table5-------------------------------------------------
    print ("Loading data from mlratings。。。")
    cursor.execute("DROP TABLE IF EXISTS mlratings;")
    sql="CREATE TABLE mlratings(movieId CHAR(255),userId CHAR(255),imdbId CHAR(255),rating CHAR(255),timestamp CHAR(255));"
    cursor.execute(sql);
    csv_data = csv.reader(open('phase1_dataset/mlratings.csv'))
    
    header = True
        
    for row in csv_data:
        if header:
            header=False
            continue
        cursor.execute('INSERT INTO mlratings(movieId ,userId ,imdbId ,rating ,timestamp ) VALUES(%s,%s,%s,%s,%s)',row)
        
    #close the connection to the database.
    db.commit()
    
    #load table6-------------------------------------------------
    print ("Loading data from movieactor。。。")
    cursor.execute("DROP TABLE IF EXISTS movieactor;")
    sql="CREATE TABLE movieactor(movieId CHAR(255),actorId CHAR(255),actorMovieRank CHAR(255));"
    cursor.execute(sql);
    csv_data = csv.reader(open('phase1_dataset/movie-actor.csv'))
    
    header = True
        
    for row in csv_data:
        if header:
            header=False
            continue
        cursor.execute('INSERT INTO movieactor(movieId ,actorId ,actorMovieRank ) VALUES(%s,%s,%s)',row)
        
    #close the connection to the database.
    db.commit()
    
    #load table7-------------------------------------------------
    print ("Loading data from mlusers。。。")
    cursor.execute("DROP TABLE IF EXISTS mlusers;")
    sql="CREATE TABLE mlusers(userId CHAR(255));"
    cursor.execute(sql);
    csv_data = csv.reader(open('phase1_dataset/mlusers.csv'))
    
    header = True
        
    for row in csv_data:
        if header:
            header=False
            continue
        cursor.execute('INSERT INTO mlusers(userId) VALUES(%s)',row)
        
    #finish loading all the data
    print ("All the data loaded")
    db.commit()

    cursor.close()
    print ("Done")
    
    # close the database 
    db.close()
    
def print_actor_vector(i,m):
    print("Create tag vectors for actor {} in model {}".format(i,m))
    print ("Connecting to the database。。。")
    db = MySQLdb.connect("localhost",dbuser,dbpw,dbname )     
    cursor = db.cursor()
    db.set_character_set('utf8')
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    
    cursor.execute("DROP TABLE IF EXISTS tmpactortags;")
    sql="CREATE TABLE tmpactortags AS SELECT actorId, movieactor.movieId,tagId, actorMovieRank, mltags.timestamp FROM mltags LEFT JOIN movieactor ON mltags.movieId = movieactor.movieId WHERE actorId="+str(i)+";"
    cursor.execute(sql)
      
    #fetch all the required data to compute tf and tfidf         
    cursor.execute("SELECT COUNT(actorId) FROM actorinfo")  
    num_actor=cursor.fetchall()[0][0]
    #print(num_actor)
    cursor.execute("SELECT COUNT(tagId) FROM tmpactortags")  
    num_tag=cursor.fetchall()[0][0]
    #print(num_tag)
    cursor.execute("SELECT MAX(actorMovieRank) FROM tmpactortags")  
    max_rank=cursor.fetchall()[0][0]
    cursor.execute("SELECT MIN(actorMovieRank) FROM tmpactortags")  
    min_rank=cursor.fetchall()[0][0]
    range_rank=int(max_rank)-int(min_rank)
    cursor.execute("SELECT MAX(timestamp) FROM tmpactortags") 
    max_ts=cursor.fetchall()[0][0]
    cursor.execute("SELECT MIN(timestamp) FROM tmpactortags") 
    min_ts=cursor.fetchall()[0][0]
    max_ts=datetime.strptime(max_ts, "%Y-%m-%d %H:%M:%S")
    min_ts=datetime.strptime(min_ts, "%Y-%m-%d %H:%M:%S")
    range_ts=max_ts-min_ts

    #-----------------------------------------------------
    cursor.execute("DROP TABLE IF EXISTS tmpweights;")
    cursor.execute("CREATE TABLE tmpweights(tagId CHAR(255),weight CHAR(255));")
    
    cursor.execute("SELECT DISTINCT tagId FROM tmpactortags")
    results=cursor.fetchall()
    for row in results:
        #print("new tag---")
        tagId=row[0]
        cursor.execute("SELECT COUNT(tagId) FROM tmpactortags WHERE tagId="+str(tagId)+";")
        num_this=cursor.fetchall()[0][0]
        #compute weight factor base on timestamp
        cursor.execute("SELECT timestamp FROM tmpactortags WHERE tagId="+str(tagId)+" ORDER BY timestamp DESC;")
        ts_all=cursor.fetchall()
        cursor.execute("SELECT actorMovieRank FROM tmpactortags WHERE tagId="+str(tagId)+";")
        rank_all=cursor.fetchall()
        tf_up=0.0
        for x in range(0,int(num_this)):
            ts_this=ts_all[x][0]
            ts_this=datetime.strptime(ts_this, "%Y-%m-%d %H:%M:%S")
            ts_diff=ts_this-min_ts
            ts_w=0.9+(float(ts_diff.total_seconds())/float(range_ts.total_seconds()))/10.0
            
        #compute weight factor base on rank
            r_this=rank_all[x][0]
            r_diff=float(max_rank)-float(r_this)
            if range_rank==0:
                r_w=1
            else:
                r_w=0.9+(r_diff/float(range_rank))/10.0
                
            tf_up=tf_up+ts_w*r_w
            
            
        tf_this=tf_up/float(num_tag)
        
        weight=tf_this
        if m=="tfidf":
           cursor.execute("SELECT COUNT(DISTINCT actorId) FROM cse515p1.mltags JOIN movieactor ON mltags.movieId = movieactor.movieId WHERE tagId="+str(tagId)+";")
           num_actor_t=cursor.fetchall()[0][0]
           idf_this=math.log2(float(num_actor)/float(num_actor_t)) 
           weight=tf_this*idf_this
        cursor.execute("INSERT INTO tmpweights VALUES  ("+str(tagId)+", "+str(weight)+");")
    
    cursor.execute("SELECT SUM(weight) FROM tmpweights;")
    w_sum=cursor.fetchall()[0][0]
    cursor.execute("SELECT * FROM tmpweights ORDER BY weight DESC;")
    results=cursor.fetchall()
    print("--The {} tag vectors for actor {} are:".format(m, str(i)))    
    for row in results:
      tagId_p = row[0]
      weight_p = float(row[1])/float(w_sum)
      print ("<{},{}>".format(tagId_p,weight_p))
    db.commit()
    cursor.close()
    db.close()
    
    
    
def print_genre_vector(i,m):
    print("The tag vector of genre {} in model {}".format(i,m))
    print ("Connecting to the database。。。")
    db = MySQLdb.connect("localhost",dbuser,dbpw,dbname )     
    cursor = db.cursor()
    db.set_character_set('utf8')
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    
    cursor.execute("DROP TABLE IF EXISTS tmpgenretags;")
    sql="CREATE TABLE tmpgenretags AS SELECT mlmovies.movieId, tagId, genres,timestamp FROM mlmovies JOIN mltags ON mlmovies.movieId=mltags.movieId;"
    cursor.execute(sql)
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtsplit;")
    sql="CREATE TABLE tmpgtsplit (genres CHAR(255),movieId CHAR(255),tagId CHAR(255),timestamp CHAR(255));"
    cursor.execute(sql)
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtzero;")
    sql="CREATE TABLE tmpgtzero AS SELECT genres,movieId,tagId,timestamp FROM tmpgenretags WHERE genres NOT LIKE '%|%';"
    cursor.execute(sql)
    cursor.execute("INSERT INTO tmpgtsplit (genres,movieId,tagId,timestamp) SELECT genres,movieId,tagId,timestamp FROM tmpgtzero")
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtone;")
    sql="CREATE TABLE tmpgtone AS SELECT substring_index(substring_index(`genres`,'|',1),'|',-1) AS genres,movieId,tagId,timestamp FROM tmpgenretags WHERE genres LIKE '%|%';"
    cursor.execute(sql)
    cursor.execute("INSERT INTO tmpgtsplit (genres,movieId,tagId,timestamp) SELECT genres,movieId,tagId,timestamp FROM tmpgtone")
    
    cursor.execute("DROP TABLE IF EXISTS tmpgttwo;")
    sql="CREATE TABLE tmpgttwo AS SELECT substring_index(substring_index(`genres`,'|',2),'|',-1) AS genres,movieId,tagId,timestamp FROM tmpgenretags WHERE genres LIKE '%|%';"
    cursor.execute(sql)
    cursor.execute("INSERT INTO tmpgtsplit (genres,movieId,tagId,timestamp) SELECT genres,movieId,tagId,timestamp FROM tmpgttwo")
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtthree;")
    sql="CREATE TABLE tmpgtthree AS SELECT substring_index(substring_index(`genres`,'|',3),'|',-1) AS genres,movieId,tagId,timestamp FROM tmpgenretags WHERE genres LIKE '%|%|%';"
    cursor.execute(sql)
    cursor.execute("INSERT INTO tmpgtsplit (genres,movieId,tagId,timestamp) SELECT genres,movieId,tagId,timestamp FROM tmpgtthree")
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtfour;")
    sql="CREATE TABLE tmpgtfour AS SELECT substring_index(substring_index(`genres`,'|',4),'|',-1) AS genres,movieId,tagId,timestamp FROM tmpgenretags WHERE genres LIKE '%|%|%|%';"
    cursor.execute(sql)
    cursor.execute("INSERT INTO tmpgtsplit (genres,movieId,tagId,timestamp) SELECT genres,movieId,tagId,timestamp FROM tmpgtfour")
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtfive;")
    sql="CREATE TABLE tmpgtfive AS SELECT substring_index(substring_index(`genres`,'|',5),'|',-1) AS genres,movieId,tagId,timestamp FROM tmpgenretags WHERE genres LIKE '%|%|%|%|%';"
    cursor.execute(sql)
    cursor.execute("INSERT INTO tmpgtsplit (genres,movieId,tagId,timestamp) SELECT genres,movieId,tagId,timestamp FROM tmpgtfive")
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtsix;")
    sql="CREATE TABLE tmpgtsix AS SELECT substring_index(substring_index(`genres`,'|',6),'|',-1) AS genres,movieId,tagId,timestamp FROM tmpgenretags WHERE genres LIKE '%|%|%|%|%|%';"
    cursor.execute(sql)
    cursor.execute("INSERT INTO tmpgtsplit (genres,movieId,tagId,timestamp) SELECT genres,movieId,tagId,timestamp FROM tmpgtsix")
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtthis;")
    sql="CREATE TABLE tmpgtthis AS SELECT * FROM tmpgtsplit WHERE genres='"+str(i)+"';"
    cursor.execute(sql)
    db.commit()
    
    #fetch all the required data to compute tf and tfidf         
    cursor.execute("SELECT COUNT(DISTINCT(genres)) FROM tmpgtsplit;")  
    num_genre=cursor.fetchall()[0][0]
    #print(num_genre)
    cursor.execute("SELECT COUNT(tagId) FROM tmpgtthis")  
    num_tag=cursor.fetchall()[0][0]
    #print(num_tag)
    cursor.execute("SELECT MAX(timestamp) FROM tmpgtthis") 
    max_ts=cursor.fetchall()[0][0]
    cursor.execute("SELECT MIN(timestamp) FROM tmpgtthis") 
    min_ts=cursor.fetchall()[0][0]
    max_ts=datetime.strptime(max_ts, "%Y-%m-%d %H:%M:%S")
    min_ts=datetime.strptime(min_ts, "%Y-%m-%d %H:%M:%S")
    range_ts=max_ts-min_ts
     #-----------------------------------------------------
    cursor.execute("DROP TABLE IF EXISTS tmpweights;")
    cursor.execute("CREATE TABLE tmpweights(tagId CHAR(255),weight CHAR(255));")
    
    cursor.execute("SELECT DISTINCT tagId FROM tmpgtthis")
    results=cursor.fetchall()
    for row in results:
        tagId=row[0]
        cursor.execute("SELECT COUNT(tagId) FROM tmpgtthis WHERE tagId="+str(tagId)+";")
        num_this=cursor.fetchall()[0][0]
        #compute weight factor base on timestamp
        cursor.execute("SELECT timestamp FROM tmpgtthis WHERE tagId="+str(tagId)+" ORDER BY timestamp DESC;")
        ts_all=cursor.fetchall()
        tf_up=0.0
        for x in range(0,int(num_this)):
            ts_this=ts_all[x][0]
            ts_this=datetime.strptime(ts_this, "%Y-%m-%d %H:%M:%S")
            ts_diff=ts_this-min_ts
            ts_w=0.9+(float(ts_diff.total_seconds())/float(range_ts.total_seconds()))/10.0            
                
            tf_up=tf_up+ts_w
            
            
        tf_this=tf_up/float(num_tag)
       
        weight=tf_this
        if m=="tfidf":
           cursor.execute("SELECT COUNT(DISTINCT genres) FROM tmpgtsplit WHERE tagId="+str(tagId)+";")
           num_genre_t=cursor.fetchall()[0][0]
           idf_this=math.log2(float(num_genre)/float(num_genre_t)) 
           weight=tf_this*idf_this
        cursor.execute("INSERT INTO tmpweights VALUES  ("+str(tagId)+", "+str(weight)+");")
        
    cursor.execute("SELECT SUM(weight) FROM tmpweights;")
    w_sum=cursor.fetchall()[0][0]
    cursor.execute("SELECT * FROM tmpweights ORDER BY weight DESC;")
    results=cursor.fetchall()    
    
    print("--The {} tag vectors for genre {} are:".format(m, str(i)))
    for row in results:
      tagId_p = row[0]
      weight_p = float(row[1])/float(w_sum)
      print ("<{},{}>".format(tagId_p,weight_p))
      
    db.commit()
    cursor.close()
    db.close()
    
def print_user_vector(i,m):
    print("The tag vector of user {} in model {}".format(i,m))
    print ("Connecting to the database。。。")
    db = MySQLdb.connect("localhost",dbuser,dbpw,dbname )     
    cursor = db.cursor()
    db.set_character_set('utf8')
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    #print('create tmp1')
    cursor.execute("DROP TABLE IF EXISTS tmpuserwatch;")
    sql="CREATE TABLE tmpuserwatch AS SELECT userId, movieId FROM mltags;"
    cursor.execute(sql)
    cursor.execute("INSERT INTO tmpuserwatch (userId,movieId) SELECT userId,movieId FROM mlratings;")
    db.commit()
    cursor.execute("DROP TABLE IF EXISTS tmpmoviethis;")
    cursor.execute("CREATE TABLE tmpmoviethis AS SELECT DISTINCT(movieId) FROM tmpuserwatch WHERE userId="+str(i)+";")
    cursor.execute("DROP TABLE IF EXISTS tmpmovietagthis;")
    cursor.execute("CREATE TABLE tmpmovietagthis AS SELECT tmpmoviethis.movieId,tagId,timestamp FROM tmpmoviethis JOIN mltags ON tmpmoviethis.movieId=mltags.movieId;")
    db.commit()
    
    #fetch all the required data to compute tf and tfidf         
    cursor.execute("SELECT COUNT(DISTINCT(userId)) FROM mlusers;")  
    num_user=cursor.fetchall()[0][0]
    cursor.execute("SELECT COUNT(tagId) FROM tmpmovietagthis;")  
    num_tag=cursor.fetchall()[0][0]
    cursor.execute("SELECT MAX(timestamp) FROM tmpmovietagthis;") 
    max_ts=cursor.fetchall()[0][0]
    cursor.execute("SELECT MIN(timestamp) FROM tmpmovietagthis;") 
    min_ts=cursor.fetchall()[0][0]
    max_ts=datetime.strptime(max_ts, "%Y-%m-%d %H:%M:%S")
    min_ts=datetime.strptime(min_ts, "%Y-%m-%d %H:%M:%S")
    range_ts=max_ts-min_ts
     #-----------------------------------------------------
    cursor.execute("DROP TABLE IF EXISTS tmpweights;")
    cursor.execute("CREATE TABLE tmpweights(tagId CHAR(255),weight CHAR(255));")
    
    cursor.execute("SELECT DISTINCT(tagId) FROM tmpmovietagthis;")
    results=cursor.fetchall()
    for row in results:
        tagId=row[0]
        #print(tagId)
        cursor.execute("SELECT COUNT(tagId) FROM tmpmovietagthis WHERE tagId="+str(tagId)+";")
        num_this=cursor.fetchall()[0][0]
        #compute weight factor base on timestamp
        cursor.execute("SELECT timestamp FROM tmpmovietagthis WHERE tagId="+str(tagId)+" ORDER BY timestamp DESC;")
        ts_all=cursor.fetchall()
        
        tf_up=0.0
        for x in range(0,int(num_this)):
            ts_this=ts_all[x][0]
            ts_this=datetime.strptime(ts_this, "%Y-%m-%d %H:%M:%S")
            ts_diff=ts_this-min_ts
            ts_w=0.9+(float(ts_diff.total_seconds())/float(range_ts.total_seconds()))/10.0            
                
            tf_up=tf_up+ts_w
                
        tf_this=tf_up/float(num_tag)
        
        weight=tf_this
        if m=="tfidf":
           cursor.execute("SELECT COUNT(DISTINCT(tmpuserwatch.userId)) FROM tmpuserwatch LEFT JOIN mltags ON tmpuserwatch.movieId=mltags.movieId WHERE tagId="+str(tagId)+";")
           num_user_t=cursor.fetchall()[0][0]
           idf_this=math.log2(float(num_user)/float(num_user_t)) 
           weight=tf_this*idf_this
        cursor.execute("INSERT INTO tmpweights VALUES  ("+str(tagId)+", "+str(weight)+");")
        
    cursor.execute("SELECT SUM(weight) FROM tmpweights;")
    w_sum=cursor.fetchall()[0][0]
    cursor.execute("SELECT * FROM tmpweights ORDER BY weight DESC;")
    results=cursor.fetchall()    
    
    print("--The {} tag vectors for user {} are:".format(m, str(i)))
    for row in results:
      tagId_p = row[0]
      weight_p = float(row[1])/float(w_sum)
      print ("<{},{}>".format(tagId_p,weight_p))
      
    db.commit()
    cursor.close()
    db.close()
    
def differentiate_genre_vector(g1,g2,m):
    print("The tag vector of genre {}, {} in model {}".format(g1,g2,m))
    print ("Connecting to the database。。。")
    db = MySQLdb.connect("localhost",dbuser,dbpw,dbname )     
    cursor = db.cursor()
    db.set_character_set('utf8')
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    
    cursor.execute("DROP TABLE IF EXISTS tmpgenretags;")
    sql="CREATE TABLE tmpgenretags AS SELECT mlmovies.movieId, tagId, genres,timestamp FROM mlmovies JOIN mltags ON mlmovies.movieId=mltags.movieId;"
    cursor.execute(sql)
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtsplit;")
    sql="CREATE TABLE tmpgtsplit (genres CHAR(255),movieId CHAR(255),tagId CHAR(255),timestamp CHAR(255));"
    cursor.execute(sql)
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtzero;")
    sql="CREATE TABLE tmpgtzero AS SELECT genres,movieId,tagId,timestamp FROM tmpgenretags WHERE genres NOT LIKE '%|%';"
    cursor.execute(sql)
    cursor.execute("INSERT INTO tmpgtsplit (genres,movieId,tagId,timestamp) SELECT genres,movieId,tagId,timestamp FROM tmpgtzero")
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtone;")
    sql="CREATE TABLE tmpgtone AS SELECT substring_index(substring_index(`genres`,'|',1),'|',-1) AS genres,movieId,tagId,timestamp FROM tmpgenretags WHERE genres LIKE '%|%';"
    cursor.execute(sql)
    cursor.execute("INSERT INTO tmpgtsplit (genres,movieId,tagId,timestamp) SELECT genres,movieId,tagId,timestamp FROM tmpgtone")
    
    cursor.execute("DROP TABLE IF EXISTS tmpgttwo;")
    sql="CREATE TABLE tmpgttwo AS SELECT substring_index(substring_index(`genres`,'|',2),'|',-1) AS genres,movieId,tagId,timestamp FROM tmpgenretags WHERE genres LIKE '%|%';"
    cursor.execute(sql)
    cursor.execute("INSERT INTO tmpgtsplit (genres,movieId,tagId,timestamp) SELECT genres,movieId,tagId,timestamp FROM tmpgttwo")
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtthree;")
    sql="CREATE TABLE tmpgtthree AS SELECT substring_index(substring_index(`genres`,'|',3),'|',-1) AS genres,movieId,tagId,timestamp FROM tmpgenretags WHERE genres LIKE '%|%|%';"
    cursor.execute(sql)
    cursor.execute("INSERT INTO tmpgtsplit (genres,movieId,tagId,timestamp) SELECT genres,movieId,tagId,timestamp FROM tmpgtthree")
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtfour;")
    sql="CREATE TABLE tmpgtfour AS SELECT substring_index(substring_index(`genres`,'|',4),'|',-1) AS genres,movieId,tagId,timestamp FROM tmpgenretags WHERE genres LIKE '%|%|%|%';"
    cursor.execute(sql)
    cursor.execute("INSERT INTO tmpgtsplit (genres,movieId,tagId,timestamp) SELECT genres,movieId,tagId,timestamp FROM tmpgtfour")
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtfive;")
    sql="CREATE TABLE tmpgtfive AS SELECT substring_index(substring_index(`genres`,'|',5),'|',-1) AS genres,movieId,tagId,timestamp FROM tmpgenretags WHERE genres LIKE '%|%|%|%|%';"
    cursor.execute(sql)
    cursor.execute("INSERT INTO tmpgtsplit (genres,movieId,tagId,timestamp) SELECT genres,movieId,tagId,timestamp FROM tmpgtfive")
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtsix;")
    sql="CREATE TABLE tmpgtsix AS SELECT substring_index(substring_index(`genres`,'|',6),'|',-1) AS genres,movieId,tagId,timestamp FROM tmpgenretags WHERE genres LIKE '%|%|%|%|%|%';"
    cursor.execute(sql)
    cursor.execute("INSERT INTO tmpgtsplit (genres,movieId,tagId,timestamp) SELECT genres,movieId,tagId,timestamp FROM tmpgtsix")
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtthis;")
    sql="CREATE TABLE tmpgtthis AS SELECT * FROM tmpgtsplit WHERE genres='"+str(g1)+"';"
    cursor.execute(sql)
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtthistwo;")
    sql="CREATE TABLE tmpgtthistwo AS SELECT * FROM tmpgtsplit WHERE genres='"+str(g2)+"';"
    cursor.execute(sql)
    
    cursor.execute("DROP TABLE IF EXISTS tmpgtthisunion;")
    sql="CREATE TABLE tmpgtthisunion AS SELECT * FROM tmpgtsplit WHERE genres='"+str(g1)+"' OR genres='"+str(g2)+"';"
    cursor.execute(sql)
    
    cursor.execute("DROP TABLE IF EXISTS tmpunion;")
    sql="CREATE TABLE tmpunion AS SELECT tmpgtsplit.genres,tmpgtsplit.movieId,tmpgtsplit.tagId FROM tmpgtsplit JOIN tmpgtthisunion ON tmpgtthisunion.movieId=tmpgtsplit.movieId;"
    cursor.execute(sql)
    db.commit()
    
    #fetch all the required data to compute tf and tfidf         
    cursor.execute("SELECT COUNT(DISTINCT(genres)) FROM tmpunion;")     
    num_genre=cursor.fetchall()[0][0]
    #print(num_genre)
    cursor.execute("SELECT COUNT(tagId) FROM tmpgtthis")  
    num_tag=cursor.fetchall()[0][0]
    #print(num_tag)
    cursor.execute("SELECT MAX(timestamp) FROM tmpgtthis") 
    max_ts=cursor.fetchall()[0][0]
    cursor.execute("SELECT MIN(timestamp) FROM tmpgtthis") 
    min_ts=cursor.fetchall()[0][0]
    max_ts=datetime.strptime(max_ts, "%Y-%m-%d %H:%M:%S")
    min_ts=datetime.strptime(min_ts, "%Y-%m-%d %H:%M:%S")
    range_ts=max_ts-min_ts
     #-----------------------------------------------------
    cursor.execute("DROP TABLE IF EXISTS tmpweights;")
    cursor.execute("CREATE TABLE tmpweights(tagId CHAR(255),weight CHAR(255));")
    
    cursor.execute("SELECT DISTINCT tagId FROM tmpgtthis")
    results=cursor.fetchall()
    for row in results:
        tagId=row[0]
        cursor.execute("SELECT COUNT(tagId) FROM tmpgtthis WHERE tagId="+str(tagId)+";")
        num_this=cursor.fetchall()[0][0]
        #compute weight factor base on timestamp
        cursor.execute("SELECT timestamp FROM tmpgtthis WHERE tagId="+str(tagId)+" ORDER BY timestamp DESC;")
        ts_all=cursor.fetchall()
        tf_up=0.0
        for x in range(0,int(num_this)):
            ts_this=ts_all[x][0]
            ts_this=datetime.strptime(ts_this, "%Y-%m-%d %H:%M:%S")
            ts_diff=ts_this-min_ts
            ts_w=0.9+(float(ts_diff.total_seconds())/float(range_ts.total_seconds()))/10.0            
                
            tf_up=tf_up+ts_w
            
            
        tf_this=tf_up/float(num_tag)
       
        cursor.execute("SELECT COUNT(DISTINCT genres) FROM tmpunion WHERE tagId="+str(tagId)+";")
        num_genre_t=cursor.fetchall()[0][0]
        idf_this=math.log2(float(num_genre)/float(num_genre_t)) 
        weight_diff=tf_this*idf_this
        
        
        cursor.execute("SELECT COUNT(DISTINCT movieId) FROM tmpgtthis WHERE tagId="+str(tagId)+";")
        r_s_one=float(cursor.fetchall()[0][0])
        cursor.execute("SELECT COUNT(DISTINCT movieId) FROM tmpunion WHERE tagId="+str(tagId)+";")
        m_s_one=float(cursor.fetchall()[0][0])
        cursor.execute("SELECT COUNT(DISTINCT movieId) FROM tmpgtthis;")
        r_l_one=float(cursor.fetchall()[0][0])
        cursor.execute("SELECT COUNT(DISTINCT movieId) FROM tmpunion;")
        m_l_one=float(cursor.fetchall()[0][0])
        
        weight_one=1
        weight_two=1

        weight_one=math.log2((r_s_one+0.5/(r_l_one-r_s_one+1.0))/((m_s_one-r_s_one+0.5)/(m_l_one-m_s_one-r_l_one+r_s_one+1.0)))*math.fabs((r_s_one/r_l_one)-((m_s_one-r_s_one+0.5)/(m_l_one-r_l_one+1.0)))
        
        cursor.execute("SELECT COUNT(DISTINCT movieId) FROM tmpgtthistwo;")
        r_l_two=float(cursor.fetchall()[0][0])
        
        r_s_two=r_l_two-r_s_one

        m_s_two=m_l_one-m_s_one
        
        m_l_two=m_l_one
      
        weight_two=math.log2((r_s_two+0.5/(r_l_two-r_s_two+1.0))/((m_s_two-r_s_two+0.5)/(m_l_two-m_s_two-r_l_two+r_s_two+1.0)))*math.fabs((r_s_two/r_l_two)-((m_s_two-r_s_two+0.5)/(m_l_two-r_l_two+1.0)))
        
        if m=="TF-IDF-DIFF":
            cursor.execute("INSERT INTO tmpweights VALUES  ("+str(tagId)+", "+str(weight_diff)+");")
        elif m=="P-DIFF1":
            cursor.execute("INSERT INTO tmpweights VALUES  ("+str(tagId)+", "+str(weight_one)+");")  
        elif m=="P-DIFF2":
            cursor.execute("INSERT INTO tmpweights VALUES  ("+str(tagId)+", "+str(weight_two)+");")
        else:
            print("invalid mode")
    cursor.execute("SELECT SUM(weight) FROM tmpweights;")
    w_sum=cursor.fetchall()[0][0]
    cursor.execute("SELECT * FROM tmpweights ORDER BY weight DESC;")
    results=cursor.fetchall()    
    
    print("--The {} diff tag vectors for genre {} and genre {} are:".format(m, str(g1), str(g2)))
    for row in results:
      tagId_p = row[0]
      weight_p = float(row[1])
      weight_n = float(row[1])/float(w_sum)
      print ("<{},{}>".format(tagId_p,weight_p))
      
    db.commit()
    cursor.close()  
    db.close()   
    
def main():    
    #load data into database
    loaddata()
    
    var1,var2,var3="","",""
    e=False
    
    while e==False:
        args=input("Choose a task:").split();
        n=len(args)
        
        if n==3:
            task,var1,var2=args
        elif n==4:
            task,var1,var2,var3=args
        elif n==1:
            task=args
            if task=="exit":
                e=True
            else:
                print("invalid input")
        else: 
            print("invalid input")  
            
    
        
        if task=="print_actor_vector":
            print_actor_vector(var1,var2)
        elif task=="print_genre_vector":
            print_genre_vector(var1,var2)
        elif task=="print_user_vector":
            print_user_vector(var1,var2)
        elif task=="differentiate_genre_vector":
            differentiate_genre_vector(var1,var2,var3)
        else:
            print("invalid input")
        


main()

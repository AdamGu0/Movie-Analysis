import csv
import math
import time
import numpy
from sklearn.cluster import KMeans


def main():
    getMltags()
    getActorInfo()

    print('task 2a:')
    m = actorTagMatrix()
    simMat = m * m.T
    svd(simMat)

    print('task 2b:')
    svd(coActorMatrix())
    
def do_t2a():
    getMltags()
    getActorInfo()

    print('task 2a:')
    m = actorTagMatrix()
    simMat = m * m.T
    svd(simMat)
    
def do_t2b():
    getMltags()
    getActorInfo()

    print('task 2b:')
    svd(coActorMatrix())


def svd(martix):
    U, sigma, V = numpy.linalg.svd(martix)
    U = U[:, 0:3]
    sigma = sigma[0:3]
    print('actors\' degrees of memberships to top-3 latent semantics:\n', U)
    print('\nImportance of top 3 latent semantics:\n', sigma)

    estimator = KMeans(n_clusters=3)
    group = estimator.fit_predict(U)

    print('\nGroup labels for actors:\n')
    actorInfo = getActorInfo()
    groupInfo = ['', '', '']
    for actor in actorInfo:
        i = actorIndex[actor]
        groupInfo[group[i]] += actorInfo[actor][0] + '\n'

    print('Group 1:\n', groupInfo[0])
    print('Group 2:\n', groupInfo[1])
    print('Group 3:\n', groupInfo[2])


def actorTagMatrix():
    model = 'TF-IDF'
    global actorIndex, tagIndex, tagActor
    movieActor = getMovieActor()
    tagVectors = []

    for actor in getActorInfo():
        tagVectors.append([0 for i in range(len(tagIndex))])

    for row in getMltags():
        movie = row[1]
        tag = row[2]
        weight = row[3]
        actorWeights = movieActor[movie]
        for actor in actorWeights:
            v = tagVectors[actorIndex[actor]]
            v[tagIndex[tag]] += weight * actorWeights[actor]

    actorTagMat = numpy.mat(tagVectors)

    if model == 'TF-IDF':
        weights = [0 for i in range(len(tagIndex))]
        for tag in tagIndex:
            i = tagIndex[tag]
            count = len(numpy.nonzero(actorTagMat[:, i]))
            weights[i] = math.log(1.0 * len(actorIndex) / count)
        numpy.multiply(actorTagMat, weights)

    return actorTagMat


def coActorMatrix():
    global actorIndex
    coActorVectors = []
    for i in range(len(actorIndex)):
        coActorVectors.append([0 for i in range(len(actorIndex))])

    movieActor = getMovieActor()
    for movie in movieActor:
        actors = movieActor[movie]
        for actor1 in list(actors.keys()):
            i = actorIndex[actor1]
            weight1 = actors.pop(actor1)
            coActorVectors[i][i] += 0.5 * weight1 ** 2
            for actor2 in actors:
                j = actorIndex[actor2]
                coActorVectors[i][j] += weight1 * actors[actor2]
    mat = numpy.mat(coActorVectors)

    return mat + mat.T


def rankWeight(rank):
    if rank < 21:
        return 1.03 - 0.03 * rank
    return 0.4


# store csv files into gobal variables
movieActor = {}  # key: movieID, value: {actorID:weight}
mltags = ()
genomeTags = {}
tagActor = {}  # key: tagID, value:{actorID, ...}
allActors = set()
movieGenre = {}
tagGenre = {}  # key: tagID, value:set({genre, ...})
allGenres = set()
allUsers = set()
movieUser = {}  # key: movieID, value: {userID, ...}
tagMovie = {}  # key: tagID, value:{movieID, ...}
mlratings = ()
actorInfo = {}
tagIndex = {}  # key: tagID, value: index
actorIndex = {}


def getMovieActor():
    global movieActor  # key:movieID, value:{actorID:weight, ...}

    if len(movieActor) == 0:
        with open('Phase2_data/movie-actor.csv') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # ignore the title row
            for movie, actor, rank in reader:
                movie = int(movie)
                actors = movieActor.get(movie, {})
                actors[int(actor)] = rankWeight(int(rank))
                movieActor[movie] = actors
                global allActors
                allActors.add(actor)

    return movieActor


def getMltags():
    global mltags, allUsers, tagIndex

    if len(mltags) == 0:
        data = []
        maxTime = 0.0
        minTime = time.time()
        with open('Phase2_data/mltags.csv') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # ignore the title row
            for row in reader:
                user = int(row[0])
                tag = int(row[2])
                t = time.mktime(time.strptime(row[3], "%Y-%m-%d  %H:%M:%S"))  # format: 2007-08-27  18:16:41
                if maxTime < t:
                    maxTime = t
                if minTime > t:
                    minTime = t
                data.append([user, int(row[1]), tag, t])
                allUsers.add(user)
                if tag not in tagIndex:
                    tagIndex[tag] = len(tagIndex)

        for row in data:
            t = row[3]
            weight = 0.5 + 0.5 * (t - minTime) / (maxTime - minTime)
            row[3] = weight
        mltags = tuple(data)

    return mltags


def getMovieGenre():
    global movieGenre  # key:movieID, value:[genre, ...]

    if len(movieGenre) == 0:
        with open('Phase2_data/mlmovies.csv') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # ignore the title row
            for movie, name, genres in reader:
                movie = int(movie)
                genres = set(genres.split('|'))
                movieGenre[movie] = genres
                global allGenres
                allGenres = allGenres | genres
    return movieGenre


def getGenomeTags():
    global genomeTags

    if len(genomeTags) == 0:
        with open('Phase2_data/genome-tags.csv') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # ignore the title row
            for row in reader:
                genomeTags[int(row[0])] = row[1]

    return genomeTags


def getMlratings():
    global mlratings, allUsers

    if len(mlratings) == 0:
        data = []
        with open('Phase2_data/mlratings.csv') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # ignore the title row
            for row in reader:
                user = int(row[1])
                data.append((int(row[0]), user))
                allUsers.add(user)
        mlratings = tuple(data)

    return mlratings


def getActorInfo():
    global actorInfo, actorIndex

    if len(actorInfo) == 0:
        with open('Phase2_data/imdb-actor-info.csv') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # ignore the title row
            for actor, name, gender in reader:
                actorInfo[int(actor)] = (name, gender)
                actorIndex[int(actor)] = len(actorIndex)

    return actorInfo




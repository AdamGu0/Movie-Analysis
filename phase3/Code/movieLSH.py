import csv
import numpy
import math


def main():
    print('\nTask 3:\n')
    movieVectors = reduceDimension(createMovieVectors(), 500)
    print('Redeced data size: ', numpy.shape(movieVectors))

    params, hashTables = doHash(movieVectors)

    global movieIndex, movieName
    while True:
        s = input('\nPlease input movie ID: ')
        targetId = int(s)
        if targetId not in movieIndex:
            print('Movie not found.')
            continue
        index = movieIndex[targetId]
        vector = movieVectors[index]
        r = 0
        while r < 1:
            s = input('Please input number of similar movies needed: ')
            r = int(s)
        print('\nLooking for similar movies of \"', movieName[targetId], '\"...')
        result = hashFind(params, hashTables, vector)
        neighbors = sortNeighbors(movieVectors, result, vector)
        if r < len(neighbors):
            neighbors = neighbors[:r]
        print('\nSearch result:')
        for movieId, d in neighbors:
            print(movieId, movieName[movieId], d)


def sortNeighbors(vectors, indice, v):
    neighbors = []
    global movieIds
    for index in indice:
        d = numpy.linalg.norm(vectors[index] - v)
        neighbors.append((movieIds[index], d))
    neighbors.sort(key=lambda n: n[1])
    neighbors = neighbors[1:]  # exclude the target movie itself
    return(neighbors)


def hashFind(params, hashTables, vector):
    result = set()
    count = 0
    for i in range(len(params)):
        gParam = params[i]
        hashTable = hashTables[i]
        bucket = hashTable[gFunction(gParam, vector)]
        result = result | bucket
        count += len(bucket)
    print(count, ' movies found from hash tables, containing ', len(result), 'unique movies.')
    return(result)


def doHash(vectors):
    L = 0
    k = 0
    print('Please input parameters for LSH:')
    while L < 1:
        s = input('L = ')
        L = int(s)
    while k < 1:
        s = input('k = ')
        k = int(s)

    dimension = len(vectors[0])
    params = generateParameters(L, k, dimension)
    hashTables = []
    for i in range(L):
        gParam = params[i]
        hashTable = {}
        for index in range(len(vectors)):
            hashValue = gFunction(gParam, vectors[index])
            s = hashTable.get(hashValue, set())
            s.add(index)
            hashTable[hashValue] = s
        hashTables.append(hashTable)
    print('Hash tables created.')
    return(params, hashTables)


def gFunction(gParam, vector):
    k = len(gParam)
    hashValue = [0 for count in range(k)]
    for i in range(k):
        hashValue[i] = hashFunction(gParam[i], vector)
    hashValue = tuple(hashValue)
    return(hashValue)


def hashFunction(param, v):
    a = param[0]
    b = param[1]
    global w
    value = (numpy.dot(a, v) + b) / w
    return(math.floor(value))


def generateParameters(L, k, dimension):
    params = []
    for i in range(L):
        params.append(generateGParameter(k, dimension))
    return(params)


def generateGParameter(k, dimension):
    params = []
    for i in range(k):
        params.append(generateHashParameter(dimension))
    return(params)


def generateHashParameter(dimension):
    global w
    a = numpy.random.randn(dimension) + 3
    b = numpy.random.random_sample() * w
    return([a, b])


def reduceDimension(vectors, dimension):
    print('Reducing data dimension... Might need a few minutes.')
    U, sigma, V = numpy.linalg.svd(vectors)
    return(numpy.multiply(U[:, :dimension], sigma[:dimension]))


# create movie vectors in the following dimensions: year, genres, actors, tags
def createMovieVectors():
    movieGenre = getMovieGenre()
    movieActor = getMovieActor()
    mltags = getMltags()
    global movieIndex, genreIndex, actorIndex, tagIndex, movieYear
    dimension = 1 + len(genreIndex) + len(actorIndex) + len(tagIndex)
    vectors = [[0.0 for col in range(dimension)] for row in range(len(movieIndex))]

    y = movieYear.values()
    yMin = min(y)
    r = max(y) - yMin
    for movie in movieYear:
        #  value of year feature: 0 to 10
        vectors[movieIndex[movie]][0] = 10.0 * (movieYear[movie] - yMin) / r

    for movie in movieGenre:
        for genre in movieGenre[movie]:
            #  value of genre feature: 0 to 10
            vectors[movieIndex[movie]][1 + genreIndex[genre]] = 10

    offset = 1 + len(genreIndex)
    for movie in movieActor:
        actors = movieActor[movie]
        for actor in actors:
            vectors[movieIndex[movie]][offset + actorIndex[actor]] = actors[actor]

    offset += len(actorIndex)
    for movie, tag in mltags:
        w = vectors[movieIndex[movie]][offset + tagIndex[tag]]
        #  value of tag feature: 0 to 4
        vectors[movieIndex[movie]][offset + tagIndex[tag]] = w / 2 + 2

    print('Generated data size: ', numpy.shape(vectors))
    return vectors


#  value of actor feature: 5 to 10
def rankWeight(rank):
    if rank < 6:
        return 11 - rank
    return 5


# store csv files into gobal variables

movieActor = {}  # key: movieID, value: {actorID:weight}
movieGenre = {}  # key:movieID, value:[genre, ...]
movieYear = {}  # key:movieID, value:year
movieName = {}  # key:movieID, value:name
mltags = []
movieIds = []

# key: ID, value: index
movieIndex = {}
genreIndex = {}
actorIndex = {}
tagIndex = {}

actorInfo = {}
genomeTags = {}

w = 40  # parameter for hash function


def getMovieActor():
    global movieActor, actorIndex

    if len(movieActor) == 0:
        with open('../phase3_dataset/movie-actor.csv') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # ignore the title row
            for movie, actor, rank in reader:
                actor = int(actor)
                movie = int(movie)
                actors = movieActor.get(movie, {})
                actors[actor] = rankWeight(int(rank))
                movieActor[movie] = actors
                if actor not in actorIndex:
                    actorIndex[actor] = len(actorIndex)

    return movieActor


def getMltags():
    global mltags, tagIndex

    if len(mltags) == 0:
        with open('../phase3_dataset/mltags.csv') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # ignore the title row
            for row in reader:
                movie = int(row[1])
                tag = int(row[2])
                mltags.append([movie, tag])
                if tag not in tagIndex:
                    tagIndex[tag] = len(tagIndex)

    return mltags


def getMovieGenre():
    global movieGenre, movieIndex, genreIndex, movieYear, movieName, movieIds

    if len(movieGenre) == 0:
        with open('../phase3_dataset/mlmovies.csv') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # ignore the title row
            for movie, name, year, genres in reader:
                movie = int(movie)
                genres = set(genres.split('|'))
                movieGenre[movie] = genres
                movieIndex[movie] = len(movieIndex)
                movieIds.append(movie)
                movieYear[movie] = int(year)
                movieName[movie] = name

                for genre in genres:
                    if genre not in genreIndex:
                        genreIndex[genre] = len(genreIndex)
    return movieGenre


def getGenomeTags():
    global genomeTags

    if len(genomeTags) == 0:
        with open('../phase3_dataset/genome-tags.csv') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # ignore the title row
            for row in reader:
                genomeTags[int(row[0])] = row[1]

    return genomeTags


def getActorInfo():
    global actorInfo, actorIndex

    if len(actorInfo) == 0:
        with open('../phase3_dataset/imdb-actor-info.csv') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # ignore the title row
            for actor, name, gender in reader:
                actorInfo[int(actor)] = (name, gender)
                actorIndex[int(actor)] = len(actorIndex)

    return actorInfo


main()

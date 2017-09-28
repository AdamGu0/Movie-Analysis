import argparse
import csv
import math
import time


def print_actor_vector(args):
    actor = args.id
    model = args.model

    # find all movies related to the actor
    movies = {}  # key:movieID, value:rank weight
    movieActor = getMovieActor()
    for movie in movieActor:
        actors = movieActor[movie]
        if actor in actors:
            movies[movie] = actors[actor]

    if len(movies) == 0:
        print 'No tag related to this actor.'
        return

    # find all tags related to the movies
    tags = {}  # key: tagID, value: weight related to the actor
    global tagActor
    tagActorLen = len(tagActor)
    for row in getMltags():
        movie = row[1]
        if movie in movies:
            weight = movies[movie] * row[3]
            tag = row[2]
            tags[tag] = tags.get(tag, 0.0) + weight
        if model == 'TF-IDF':
            if tagActorLen == 0:
                tag = row[2]
                actors = getMovieActor()[movie]
                tagActor[tag] = tagActor.get(tag, set()) | set(actors.keys())

    if len(tags) == 0:
        print 'No tag related to this actor.'
        return

    # sort and print
    if model == 'TF-IDF':
        global allActors
        total = len(allActors)
        for tag in tags:
            weight = math.log(1.0 * total / len(tagActor[tag]))
            tags[tag] = tags[tag] * weight

    sortPrint(tags)


def print_genre_vector(args):
    genre = args.id
    model = args.model

    # find all movies related to the genre
    movies = set()  # {movie, ...}
    movieGenre = getMovieGenre()
    for movie in movieGenre:
        genres = movieGenre[movie]
        if genre in genres:
            movies.add(movie)

    if len(movies) == 0:
        print 'No tag related to this genre.'
        return

    # find all movies related to the movies
    tags = {}  # key: tagID, value: weight related to the genre
    global tagGenre
    tagGenreLen = len(tagGenre)
    for row in getMltags():
        movie = row[1]
        if movie in movies:
            weight = row[3]
            tag = row[2]
            tags[tag] = tags.get(tag, 0.0) + weight
        if model == 'TF-IDF':
            if tagGenreLen == 0:
                tag = row[2]
                tagGenre[tag] = tagGenre.get(tag, set()) | getMovieGenre()[movie]

    if len(tags) == 0:
        print 'No tag related to this actor.'
        return

    # sort and print
    if model == 'TF-IDF':
        global allGenres
        total = len(allGenres)
        for tag in tags:
            weight = math.log(1.0 * total / len(tagGenre[tag]))
            tags[tag] = tags[tag] * weight

    sortPrint(tags)


def print_user_vector(args):
    userID = args.id
    model = args.model
    tags = {}  # key: tagID, value: weight related to the user
    movies = set()
    global tagMovie, movieUser
    tagMovieLen = len(tagMovie)
    movieUserLen = len(movieUser)

    # find movies related to the user from mlratings.csv
    # also movie to user mapping for IDF
    mlratings = getMlratings()
    for row in mlratings:
        user = row[1]
        if user == userID:
            movies.add(row[0])
        if model == 'TF-IDF' and movieUserLen == 0:
            u = movieUser.get(row[0], set())
            u.add(user)
            movieUser[row[0]] = u

    # find movies related to the user from mltags.csv
    # also tag to movie mapping, movie to user mapping for IDF
    for row in getMltags():
        user = row[0]
        if user == userID:
            movies.add(row[1])
        if model == 'TF-IDF':
            if tagMovieLen == 0:
                tag = row[2]
                m = tagMovie.get(tag, set())
                m.add(row[1])
                tagMovie[tag] = m
            if movieUserLen == 0:
                u = movieUser.get(row[1], set())
                u.add(user)
                movieUser[row[1]] = u

    if len(movies) == 0:
        print 'No tag related to this actor.'
        return

    # add up weights of related movies
    for row in getMltags():
        movie = row[1]
        if movie in movies:
            tag = row[2]
            tags[tag] = tags.get(tag, 0.0) + row[3]

    # sort and print
    if model == 'TF-IDF':
        global allUsers
        totalUser = len(allUsers)
        for tag in tags:
            tagUser = set()  # users that has this tag
            m = tagMovie[tag]
            for movie in m:
                tagUser = tagUser | movieUser[movie]
            weight = math.log(1.0 * totalUser / len(tagUser))
            tags[tag] = tags[tag] * weight

    sortPrint(tags)


def differentiate_genre(args):
    movies1, movies2 = set(), set()
    movieGenre = getMovieGenre()
    for movie in movieGenre:
        genres = movieGenre[movie]
        if args.id1 in genres:
            movies1.add(movie)
        if args.id2 in genres:
            movies2.add(movie)

    eval(args.model.split('-')[-1] + '(movies1, movies2)')


def DIFF(movies1, movies2):  # TF-IDF-DIFF
    tags1, tagGenre = {}, {}
    # tags1: TF weights of movie1 ; tagGenre:{tag:genres that have this tag} ; tags: diff weights
    genres = set()
    movieGenre = getMovieGenre()
    movies = movies1 | movies2
    mltags = getMltags()
    for row in mltags:
        movie = row[1]
        if movie in movies:
            tag = row[2]
            g = movieGenre[movie]
            genres = genres | g
            tagGenre[tag] = tagGenre.get(tag, set()) | g
            if movie in movies1:
                tags1[tag] = tags1.get(tag, 0.0) + row[3]

    total = len(genres)
    for tag in tags1:
        tags1[tag] = tags1[tag] * math.log(1.0 * total / len(tagGenre[tag]))

    sortPrint(tags1)


def DIFF1(movies1, movies2):  # P-DIFF1
    tags1, tags = {}, {}
    # tags1: movies in movies1 containing each tag ; movies in movies1 | movies2 containing each tag
    movies = movies1 | movies2
    mltags = getMltags()
    for row in mltags:
        movie = row[1]
        if movie in movies:
            tag = row[2]
            m = tags.get(tag, set())
            m.add(movie)
            tags[tag] = m
            if movie in movies1:
                m = tags1.get(tag, set())
                m.add(movie)
                tags1[tag] = m

    weights = {}  # {tagID:weight, ...}
    M = len(movies)
    R = len(movies1)
    for tag in tags1:
        r1 = len(tags1[tag])
        m1 = len(tags[tag])
        weights[tag] = pdiff(r1, m1, R, M)

    sortPrint(weights)


def DIFF2(movies1, movies2):  # P-DIFF2
    tags1, tags = {}, {}
    # tags1: movies in movies1 containing each tag ; movies in movies1 | movies2 containing each tag
    movies = movies1 | movies2
    mltags = getMltags()
    for row in mltags:
        movie = row[1]
        if movie in movies:
            tag = row[2]
            m = tags.get(tag, set())
            m.add(movie)
            tags[tag] = m
            if movie in movies1:
                m = tags1.get(tag, set())
                m.add(movie)
                tags1[tag] = m

    weights = {}  # {tagID:weight, ...}
    M = len(movies)
    R = len(movies2)
    for tag in tags1:
        r1 = len(movies2 - tags1[tag])
        m1 = len(movies - tags[tag])
        weights[tag] = pdiff(r1, m1, R, M)

    sortPrint(weights)


def pdiff(r1, m1, R, M):
    m1r1 = 0.5 + m1 - r1
    mr = 1.0 + M - R
    r1 = 0.5 + r1
    R = 1.0 + R
    return math.log(r1 / (R - r1) / m1r1 * (mr - m1r1)) * abs(r1 / R - m1r1 / mr)


def sortPrint(tags):
    tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
    tagDict = getGenomeTags()
    for tagId, weight in tags:
        print '\n< ', tagDict[tagId], '(', tagId, '),    ', weight, ' >'


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


def getMovieActor():
    global movieActor  # key:movieID, value:{actorID:weight, ...}

    if len(movieActor) == 0:
        with open('phase1_dataset/movie-actor.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            reader.next()  # ignore the title row
            for movie, actor, rank in reader:
                movie = int(movie)
                actors = movieActor.get(movie, {})
                actors[int(actor)] = rankWeight(int(rank))
                movieActor[movie] = actors
                global allActors
                allActors.add(actor)

    return movieActor


def getMltags():
    global mltags, allUsers

    if len(mltags) == 0:
        data = []
        maxTime = 0.0
        minTime = time.time()
        with open('phase1_dataset/mltags.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            reader.next()  # ignore the title row
            for row in reader:
                user = int(row[0])
                t = time.mktime(time.strptime(row[3], "%Y-%m-%d  %H:%M:%S"))  # format: 2007-08-27  18:16:41
                if maxTime < t:
                    maxTime = t
                if minTime > t:
                    minTime = t
                data.append([user, int(row[1]), int(row[2]), t])
                allUsers.add(user)

        for row in data:
            t = row[3]
            weight = 0.5 + 0.5 * (t - minTime) / (maxTime - minTime)
            row[3] = weight
        mltags = tuple(data)

    return mltags


def getMovieGenre():
    global movieGenre  # key:movieID, value:[genre, ...]

    if len(movieGenre) == 0:
        with open('phase1_dataset/mlmovies.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            reader.next()  # ignore the title row
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
        with open('phase1_dataset/genome-tags.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            reader.next()  # ignore the title row
            for row in reader:
                genomeTags[int(row[0])] = row[1]

    return genomeTags


def getMlratings():
    global mlratings, allUsers

    if len(mlratings) == 0:
        data = []
        with open('phase1_dataset/mlratings.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            reader.next()  # ignore the title row
            for row in reader:
                user = int(row[1])
                data.append((int(row[0]), user))
                allUsers.add(user)
        mlratings = tuple(data)

    return mlratings


parser = argparse.ArgumentParser(description='analyze movie data using different vector models')
subparsers = parser.add_subparsers(help='commands')

actorParser = subparsers.add_parser('print_actor_vector', help='print weighted tag vectors for an actor')
actorParser.add_argument('id', type=int, help='the ID of the actor')
actorParser.add_argument('model', type=str, choices=['TF', 'TF-IDF'], help='the model used')

genreParser = subparsers.add_parser('print_genre_vector', help='print weighted tag vectors for an genre')
genreParser.add_argument('id', type=str, help='the name of the genre')
genreParser.add_argument('model', type=str, choices=['TF', 'TF-IDF'], help='the model used')

userParser = subparsers.add_parser('print_user_vector', help='print weighted tag vectors for an user')
userParser.add_argument('id', type=int, help='the ID of the user')
userParser.add_argument('model', type=str, choices=['TF', 'TF-IDF'], help='the model used')

diffParser = subparsers.add_parser('differentiate_genre',
    help='prints the differentiating tag vector for a given pair of genres')
diffParser.add_argument('id1', type=str, help='name of the first genre')
diffParser.add_argument('id2', type=str, help='name of the second genre')
diffParser.add_argument('model', type=str, choices=['TF-IDF-DIFF', 'P-DIFF1', 'P-DIFF2'], help='the model used')

while True:
    print '\n############################################################'
    userInput = raw_input('\nType -h for help. Type ctrl+c to exit.\nPlease input your command:\n')
    command = userInput.split()
    args = None
    try:
        args = parser.parse_args(command)
    except:
        continue

    eval(command[0] + '(args)')

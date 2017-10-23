# Matrix Generator for
# 1. Actor - Actor Similarity Matrix
# 2. CoActor - CoActor Matrix
# 3. Transition Matrix
# 4. Movie - Movie Similarity Matrix (Task 4)

import numpy as np
import os
import csv
import HelperFunctions as hpF


def actor_actor_matrix():
    # csv files
    file_a = os.path.join(os.pardir, "Phase2_data/imdb-actor-info.csv")
    file_b = os.path.join(os.pardir, "Phase2_data/genome-tags.csv")
    file_out = os.path.join(os.pardir, "Outputs/Actor-Actor-Similarity.csv")

    # Creating Actor(Objects)-Tag(Features) Matrix
    # Actor IDs
    all_actor_id = []
    # Tag IDs
    all_tag_id = []
    # Get all actors and all tags
    with open(file_a, 'r') as fa, open(file_b, 'r') as fb:
        reader_a = csv.reader(fa)
        reader_b = csv.reader(fb)
        # Skip the headers
        next(reader_a, None)
        next(reader_b, None)

        for row in reader_a:
            all_actor_id.append(row[0])

        for row in reader_b:
            all_tag_id.append(row[0])
    # End of Getting ActorIDs and TagIDs

    # Actor-TagVector 2-D List
    # Row - ActorIDs, same order(index) with all_actor_id list
    # Column - TagIDs, same order(index) with all_tag_id list
    # Values - Tag Weights
    actor_tag_list = []

    # Get the Tag Vector for each Actor
    for actor_id in all_actor_id:
        actor_tag_list.append(hpF.actor_tag_calculator(actor_id, all_tag_id))

    # Make the 2D List to Matrix, and get its Transpose
    matrix = np.matrix(actor_tag_list)
    matrix_t = matrix.getT()
    similarity_list = (matrix.dot(matrix_t)).tolist()

    # Output to csv file
    # Get Actor Names
    with open(file_a, 'r') as fa:
        reader_a = csv.reader(fa)
        next(reader_a, None)
        header = [' ']
        for row in reader_a:
            header.append(row[1])

    result_list = [header]
    for i in range(0, len(all_actor_id)):
        r = [header[i+1]] + similarity_list[i]
        result_list.append(r)

    # Output to CSV file
    hpF.write_csv(file_out, result_list)

    return similarity_list
# ------ End of Actor-Actor Matrix ------


def coactor_coactor_matrix():
    # csv files
    file_a = os.path.join(os.pardir, "Phase2_data/imdb-actor-info.csv")
    file_out = os.path.join(os.pardir, "Outputs/CoActor-CoActor-Matrix.csv")

    # Actor IDs
    all_actor_id = []
    # Get all actors and all tags
    with open(file_a, 'r') as fa:
        reader_a = csv.reader(fa)
        # Skip the headers
        next(reader_a, None)

        for row in reader_a:
            all_actor_id.append(row[0])
    # End of Getting ActorIDs

    # Actor-ActorVector 2-D List
    # Row - ActorIDs, same order(index) with all_actor_id list
    # Column - ActorIDs
    # Values - Num of movies which two actors (actor in Row, actor in Col) acted in together
    actor_actor_list = []

    # Fill each row
    for actor_id in all_actor_id:
        actor_actor_list.append(hpF.actor_coact_calculator(actor_id, all_actor_id))

    # Output to csv file
    # Get Actor Names
    with open(file_a, 'r') as fa:
        reader_a = csv.reader(fa)
        next(reader_a, None)
        header = [' ']
        for row in reader_a:
            header.append(row[1])

    result_list = [header]
    for i in range(0, len(all_actor_id)):
        r = [header[i + 1]] + actor_actor_list[i]
        result_list.append(r)

    # Output to CSV file
    hpF.write_csv(file_out, result_list)

    return actor_actor_list
# ------ End of CoActor-CoActor Matrix ------


# Transition Matrix Generator
# parameter : Object-Object Matrix
def transition_matrix(input_matrix):
    # Get the row number and column number
    row_num = len(input_matrix)

    # Input Matrix is Empty
    if row_num == 0:
        return None

    col_num = len(input_matrix[0])

    # Transition Matrix
    result_matrix = []

    # Create Transition Matrix based on Input Matrix
    # Traverse each Row of Input Matrix Twice
    # O(RowNum * ColNum) = O(N^2)
    for r in range(0, row_num):
        # Count Non-zero value in each Row
        # Used to Calculate values in Transition Matrix
        counter = 0
        # Value List for each Row
        row_list = []

        # Count the num of Non-zero values in each Row
        for c in range(0, col_num):
            # Diagonal values should not be counted
            if input_matrix[r][c] != 0 and r != c:
                counter += 1

        # Form Transition Matrix Row by Row
        for c in range(0, col_num):
            # Diagonal values in Transition Matrix are all zero
            if input_matrix[r][c] != 0 and r != c:
                row_list.append(1/counter)
            else:
                row_list.append(0)

        # Append each row
        result_matrix.append(row_list)
    # --- End of Out-Most Loop ---

    # Transpose the Matrix (Make Columns express the Transition Info)
    result_matrix = [list(i) for i in zip(*result_matrix)]
    # Return Transition Matrix
    return result_matrix
# ----- End of Transition Matrix Generation -----


def movie_movie_matrix(user_id):
    # csv files
    file_a = os.path.join(os.pardir, "Phase2_data/mltags.csv")
    file_b = os.path.join(os.pardir, "Phase2_data/mlratings.csv")
    file_c = os.path.join(os.pardir, "Phase2_data/mlmovies.csv")

    # Creating Movie(Objects)-Tag(Features) Matrix
    # Tags are from the movies that the given user watched
    # All Movie IDs
    all_movie_id = []
    # Movie IDs related to the given User
    user_movie_id = []
    # Tag IDs related to the Movies watched by given User
    user_tag_id = []
    # Get all movie IDs
    with open(file_c, 'r') as fc:
        reader_c = csv.reader(fc)
        next(reader_c, None)

        for row in reader_c:
            all_movie_id.append(row[0])
    # Get movie IDs related to given User, then get related Tags
    with open(file_a, 'r') as fa, open(file_b, 'r') as fb:
        reader_a = csv.reader(fa)
        reader_b = csv.reader(fb)
        # Skip the headers
        next(reader_a, None)
        next(reader_b, None)

        for row in reader_a:
            if row[0] == user_id:
                user_movie_id.append(row[1])

        for row in reader_b:
            if row[1] == user_id and row[0] not in user_movie_id:
                user_movie_id.append(row[0])

        # Get Tags related to the Movies which the User watched
        fa.seek(0)
        for row in reader_a:
            if row[1] in user_movie_id and row[2] not in user_tag_id:
                user_tag_id.append(row[2])

    # End of Getting ActorIDs and TagIDs

    # Movie-TagVector 2-D List
    # Row - MovieIDs, same order(index) with all_movie_id list
    # Column - TagIDs, same order(index) with user_tag_id list
    # Values - Tag Weights
    movie_tag_list = []

    # Get the Tag Vector for each Movie
    for movie_id in all_movie_id:
        movie_tag_list.append(hpF.movie_tag_calculator(movie_id, user_tag_id))

    # Make the 2D List to Matrix, and get its Transpose
    matrix = np.matrix(movie_tag_list)
    matrix_t = matrix.getT()
    similarity_list = (matrix.dot(matrix_t)).tolist()

    return similarity_list
# ------ End of Actor-Actor Matrix ------

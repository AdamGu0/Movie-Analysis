# Object Similarity Matrix Generator

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
# ------ End of CoActor-CoActor Matrix ------

# if __name__ == '__main__':
#     actor_actor_matrix()
#     coactor_coactor_matrix()

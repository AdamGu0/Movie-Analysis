# Object Similarity Matrix Generator

import numpy as np
import os
import csv
import math


def actor_tag_matrix():
    # csv files
    file_a = os.path.join(os.pardir, "Phase2_data/imdb-actor-info.csv")
    file_b = os.path.join(os.pardir, "Phase2_data/genome-tags.csv")
    file_c = os.path.join(os.pardir, "Phase2_data/movie-actor.csv")
    file_d = os.path.join(os.pardir, "Phase2_data/mltags.csv")

    # Creating Actor(Objects)-Tag(Features) Matrix
    # Actor IDs
    all_actor_id = []
    # Tag IDs
    all_tag_id = []
    # Get all actors and all tags
    with open(file_a, 'r') as fa, open(file_b, 'r') as fb:
        reader_a = csv.reader(fa)
        reader_b = csv.reader(fb)

        for row in reader_a:
            all_actor_id.append(row[0])

        for row in reader_b:
            all_tag_id.append(row[0])
    # End of Getting ActorIDs and TagIDs

    # Actor-TagVector Mapping, Key: ActorID, Value: Tag Vector
    actor_tag_dict = {}

    # Compute the Tag Vector for each Actor




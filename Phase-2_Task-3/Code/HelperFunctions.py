# Helper Functions

import csv
import os
from datetime import datetime


# Get Tag Vector for each Actor
def actor_tag_calculator(actor_id, all_tag_id):
    # Data files needed for calculating tag weights
    file_ma = os.path.join(os.pardir, "Phase2_data/movie-actor.csv")
    file_tag = os.path.join(os.pardir, "Phase2_data/mltags.csv")

    # Compute the Tag Weight that associate with Actor
    tw_dict = tag_weight_calculator(file_a=file_ma, file_b=file_tag, actor_id=actor_id)

    actor_tag_list = []

    # If Tag Weight is None
    if tw_dict is None:
        for i in range(0, len(all_tag_id)):
            actor_tag_list.append(0)
    # Else fill the weight value to relevant tag
    else:
        for i in range(0, len(all_tag_id)):
            if all_tag_id[i] in tw_dict:
                actor_tag_list.append(tw_dict.get(all_tag_id[i]))
            else:
                actor_tag_list.append(0)

    return actor_tag_list
# ----- End of Actor Tag Calculator -----


# Compute Tag Weights for each Actor
def tag_weight_calculator(file_a, file_b, actor_id):
    # Open Movie-Actor file
    with open(file_a, 'r') as fA:
        # Read Movie-Actor file
        reader_a = csv.reader(fA)
        # Skip the header
        next(reader_a, None)

        # movie_id list
        m_list = []
        # rank list
        r_list = []
        # All rank list
        all_r_list = []

        # Find all MovieIDs and Ranks associated with actor_id
        for row_a in reader_a:
            # Get all rank info
            all_r_list.append(row_a[2])

            if row_a[1] == actor_id:
                m_list.append(row_a[0])
                r_list.append(row_a[2])
    # ----- End of processing movie-actor file -----

    # If No Movie found, return None
    if len(m_list) == 0:
        return None

    # Normalize rank list to [0, 1], and map Weight(rank) to ranks
    r_dict = normalize_rank(all_r_list=all_r_list, r_list=r_list)  # dictionary for Rank : Weight(rank)

    # Process mltags file
    with open(file_b, newline='') as fB:
        # Read the mltags file
        reader_b = csv.reader(fB)
        # Skip the header
        next(reader_b, None)

        # All timestamp list
        all_ts_list = []
        # tag_id list
        t_list = []
        # timestamp list
        ts_list = []

        # Find all TagIDs and Timestamps associated with each movie_id
        for row_b in reader_b:
            # Track all timestamps
            all_ts_list.append(row_b[3])

            if row_b[1] in m_list:
                t_list.append(row_b[2])
                ts_list.append(row_b[3])

    # ----- End of processing mltags file -----

    # If No Tag found, return None
    if len(t_list) == 0:
        return None

    # Normalize timestamp list to [0, 1], and map Weight(timestamp) to timestamp
    ts_dict = normalize_timestamp(all_ts_list=all_ts_list, ts_list=ts_list)

    # Open movie-actor & mltags files for total weight calculation
    with open(file_a, 'r') as fA, open(file_b, 'r') as fB:
        reader_a = csv.reader(fA)
        reader_b = csv.reader(fB)
        # Tag - Weight dictionary
        tw_dict = {}
        # For each tag - timestamp associated with one movie
        for i in range(0, len(t_list)):
            # Reset the read position of files
            fB.seek(0)
            fA.seek(0)
            # Get its Weight(timestamp) and MovieID
            m_id = 0
            for row_b in reader_b:
                if row_b[2] == t_list[i] and row_b[3] == ts_list[i]:
                    m_id = row_b[1]
                    w_ts = ts_dict.get(ts_list[i])
            # Get the associated Weight(rank)
            for row_a in reader_a:
                if row_a[1] == actor_id and row_a[0] == m_id:
                    w_r = r_dict.get(row_a[2])
            # Put or Update the combined Weight of rank and timestamp
            # If a tag already exists, update it
            if t_list[i] in tw_dict:
                # 1 stands for TF weight(tag) (raw count)
                new_w = tw_dict.get(t_list[i]) + (1 + w_ts + w_r)
                tw_dict[t_list[i]] = new_w
            else:
                # 1 stands for TF weight(tag) (raw count)
                tw_dict[t_list[i]] = 1 + w_ts + w_r

    return tw_dict
# ----- End of Tag-Weight Calculator -----


# Helper Function for Rank Normalization
def normalize_rank(all_r_list, r_list):
    # Highest value of rank
    highest = int(max(all_r_list))
    # Lowest value of rank
    lowest = int(min(all_r_list))
    difference = highest - lowest
    r_dict = {}  # dictionary for Rank : Weight(rank)
    # Normalize each rank's weight
    for r in r_list:
        r_dict[r] = (highest - int(r)) / difference

    return r_dict
# ----- End of normalize_rank -----


# Helper Function for Timestamp Normalization
def normalize_timestamp(all_ts_list, ts_list):
    # Normalize timestamp list to [0, 1], and map Weight(timestamp) to timestamp
    # Get the max and min, then give the newest timestamp 1, oldest timestamp 0
    # First convert the str into datetime
    newest = datetime.strptime(max(all_ts_list), "%Y-%m-%d %H:%M:%S")
    oldest = datetime.strptime(min(all_ts_list), "%Y-%m-%d %H:%M:%S")
    dt_difference = newest - oldest
    ts_dict = {}
    # Normalize each timestamp's weight and map them with associated timestamp
    for ts in ts_list:
        if newest != oldest:
            ts_dict[ts] = (datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") - oldest) / dt_difference
        else:
            ts_dict[ts] = 1

    return ts_dict
# ----- End of normalize_timestamp -----


# Helper Function for Writing csv file
def write_csv(file_name, result_list):
    with open(file_name, 'w') as f:
        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)

        for r in result_list:
            writer.writerow(r)
# ----- End of write_csv -----


# Actor-CoActMovieNum
def actor_coact_calculator(actor_id, all_actor_id):
    file = os.path.join(os.pardir, "Phase2_data/movie-actor.csv")

    # Movie list of an Actor
    m_list = []
    # Co-Actor list
    coactor_list = []

    with open(file, 'r') as f:
        reader = csv.reader(f)

        # Get all movies which the Actor acted in
        for row in reader:
            if row[1] == actor_id:
                m_list.append(row[0])

        # Search the file again for every movie to find co-actors
        for m in m_list:
            f.seek(0)
            for row in reader:
                if row[0] == m and row[1] != actor_id:
                    coactor_list.append(row[1])
    # End of File Searching

    # The dictionary for co-actor (key), num of movies (value)
    actor_num_dict = {}
    for a in coactor_list:
        # If an actor is already in the dict, value + 1
        if a in actor_num_dict:
            actor_num_dict[a] = actor_num_dict.get(a) + 1
        else:
            actor_num_dict[a] = 1

    # Return list
    actor_num_list = []
    for i in range(0, len(all_actor_id)):
        if all_actor_id[i] in actor_num_dict:
            actor_num_list.append(actor_num_dict.get(all_actor_id[i]))
        else:
            actor_num_list.append(0)

    return actor_num_list
# ----- End of Actor - CoActMovieNum -----


# Rescale PR Vector
# Normalize to range [0, 1]
def pr_vector_rescale(pr_list):
    # Return list, in range of 0 to 1
    rescaled_list = []

    # Max PR Score and Min PR Score
    max_pr = max(pr_list)
    min_pr = min(pr_list)

    for pr in pr_list:
        norm_pr = (pr[0] - min_pr[0]) / (max_pr[0] - min_pr[0])
        rescaled_list.append(norm_pr)

    return rescaled_list
# ----- End of PR Vector Rescaling -----


# Movie-Tag Calculator
def movie_tag_calculator(movie_id, user_tag_id):
    # Movie and Tag are linked within mltags file
    file_tag = os.path.join(os.pardir, "Phase2_data/mltags.csv")

    # Result list
    result_list = []
    # Tag list of the given movie_id
    tag_list = []

    # Find all tags related to the given movie_id
    with open(file_tag, 'r') as f:
        reader = csv.reader(f)

        for row in reader:
            if row[1] == movie_id:
                tag_list.append(row[2])
    # End of File processing

    # Generate resulting tag vector for each movie
    for i in range(0, len(user_tag_id)):
        if user_tag_id[i] in tag_list:
            result_list.append(1)
        else:
            result_list.append(0)

    return result_list
# -- End of Movie-Tag Calculator

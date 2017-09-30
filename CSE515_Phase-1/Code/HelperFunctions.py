from datetime import datetime
import csv
import math
import os


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


# Helper Function for (Time-weighted) TF Calculation
def generate_tf(file_name, t_list, ts_list, ts_dict, time_weighted):
    with open(file_name, newline='') as f:
        reader = csv.reader(f)
        # Tag - Weight dictionary
        tw_dict = {}
        # Tag Raw Count dictionary
        tf_dict = {}
        # For each tag - timestamp associated with one movie
        for i in range(0, len(t_list)):
            # Reset the read position of files
            f.seek(0)
            # Get its Weight(timestamp) and MovieID
            for row in reader:
                if row[2] == t_list[i] and row[3] == ts_list[i]:
                    w_ts = ts_dict.get(ts_list[i])

            # Put or Update the combined Weight of rank and timestamp
            # If a tag already exists, update it
            if t_list[i] in tw_dict:
                # 1 stands for raw count of a tag
                new_w = tw_dict.get(t_list[i]) + (1 + w_ts)
                tw_dict[t_list[i]] = new_w
                # Update raw count by adding 1 to previous value
                new_tf = tf_dict.get(t_list[i]) + 1
                tf_dict[t_list[i]] = new_tf
            else:
                # 1 stands for raw count of a tag
                tw_dict[t_list[i]] = 1 + w_ts
                # Set raw count to 1
                tf_dict[t_list[i]] = 1

    if time_weighted:
        return tw_dict
    # If time_weighted is False, return raw count
    return tf_dict
# ----- End of generate_tf -----


def calculate_tf_idf(file_a, file_b, all_g_list, tw_dict, m_list_g1, m_list_g2):
    with open(file_a, newline='') as fA, open(file_b, newline='') as fB:
        reader_a = csv.reader(fA)
        reader_b = csv.reader(fB)
        # Genre 1 - Calculate the TF-IDF for each tag t
        for t in tw_dict:
            fA.seek(0)
            fB.seek(0)
            m_list = []
            g_t_list = []
            for row_b in reader_b:
                if (row_b[2] == t and
                        (row_b[1] in m_list_g1 or row_b[1] in m_list_g2) and
                        row_b[1] not in m_list):
                    m_list.append(row_b[1])
            for row_a in reader_a:
                if row_a[0] in m_list:
                    g_list = row_a[2].split('|')
                    for g in g_list:
                        if g not in g_t_list:
                            g_t_list.append(g)
            # Update TF-IDF weight
            w_tag = tw_dict.get(t) * math.log(len(all_g_list) / len(g_t_list), 2)
            tw_dict[t] = w_tag
# End of Calculate_tf_idf


# Get List that contains unique elements
def get_unique_list(input_list):
    result = []
    for e in input_list:
        if e not in result:
            result.append(e)

    return result
# End of get_unique_list


# Generate Tag-Movie Dict, used for P-DIFF1
def generate_tag_movies_dict(file_name, t_list, m_list):
    with open(file_name, newline='') as f:
        reader = csv.reader(f)
        tm_dict = {}
        for t in t_list:
            f.seek(0)
            # List of unique movies in certain genre
            unique_m_list = []
            for row in reader:
                if row[2] == t and row[1] in m_list and row[1] not in unique_m_list:
                    unique_m_list.append(row[1])
            # Update the value of the tag
            tm_dict[t] = len(unique_m_list)

    return tm_dict
# ----- End of convert_tag_movies_dict -----


# Calculate Weight Vector for P-DIFF1
def calculate_weight_p_diff_1(file, tm_dict_r, m_list_g1, m_list_g2):
    # Weight vector which will be returned
    tw_dict = {}

    # Total Unique Movies in Genre 1 - R
    unique_m_list = get_unique_list(m_list_g1)
    r_total = len(unique_m_list)

    # Total Unique Movies in Both Genre 1 and Genre 2 - M
    # Only need to add new movies in Genre 2 to unique_m_list
    for g in m_list_g2:
        if g not in unique_m_list:
            unique_m_list.append(g)
    m_total = len(unique_m_list)

    # If M - R == 0, i.e. total movies equals movies in Genre 1
    if m_total == r_total:
        print('No Discrimination Between Two Given Genres.')
        print('Because They Appears in Same Set of Movies.')
        return

    # Calculate weight vector
    with open(file=file, newline='') as f:
        reader = csv.reader(f)
        # For each tag in Genre1 (tm_dict_g1)
        for t in tm_dict_r:
            f.seek(0)
            # Number of movies in Genre 1 containing tag t
            r = tm_dict_r[t]
            # Number of movies in Genre 1 or Genre 2 containing tag t
            m = r
            # Find movies in Genre 2 with tag t
            # List of Unique Movies in Genre 2 which contain tag t
            m_t_total = []
            for row in reader:
                if row[2] == t and row[1] in m_list_g2 and row[1] not in m_t_total:
                    m_t_total.append(row[1])
            m += len(m_t_total)

            # if m == r, the tag is only relevant to genre 1
            if m == r:
                tw_dict[t] = 'This Tag is Only Relevant to Genre 1'
                continue
            # if r == r_total, tag t is too common in g1, it appears in every movie in g1
            # if M - m - R + r == 0, tag t is too common in g2, it appears in every movie in g2
            if r == 0 or r_total < 2 or r == r_total or m_total - m - r_total + r == 0:
                # P(f|Relevant)
                p_rel = (r + 0.5) / (r_total + 1)
                # P(f|Irrelevant)
                p_irrel = ((m - r) + 0.5) / (math.fabs(m_total - r_total) + 1)
            else:
                # P(f|Relevant)
                p_rel = r / r_total
                # P(f|Irrelevant)
                p_irrel = (m - r) / math.fabs(m_total - r_total)

            # Apply probabilistic weight
            numerator = p_rel * (1 - p_irrel)
            denominator = p_irrel * (1 - p_rel)
            tw_dict[t] = math.log(numerator / denominator, 2) * math.fabs(p_rel - p_irrel)

    return tw_dict
# ----- End of calculate_weight_p_diff_1 -----


# Calculate Weight Vector for P-DIFF1
def calculate_weight_p_diff_2(file, tm_dict_r, m_list_g1, m_list_g2):
    # Weight vector which will be returned
    tw_dict = {}

    # Total Unique Movies in Genre 2 - R
    unique_m_list = get_unique_list(m_list_g2)
    r_total = len(unique_m_list)

    # Total Unique Movies in Both Genre 1 and Genre 2 - M
    # Only need to add new movies in Genre 2 to unique_m_list
    for g in m_list_g1:
        if g not in unique_m_list:
            unique_m_list.append(g)
    m_total = len(unique_m_list)

    # If M - R == 0, i.e. total movies equals movies in Genre 1
    if m_total == r_total:
        print('No Discrimination Between Two Given Genres.')
        print('Because They Appears in Same Set of Movies.')
        return

    # Calculate weight vector
    with open(file=file, newline='') as f:
        reader = csv.reader(f)
        # For each tag in Genre1 (tm_dict_g1)
        for t in tm_dict_r:
            f.seek(0)
            # Number of movies in Genre 2, not containing tag t
            r = tm_dict_r[t]
            # Number of movies in Genre 1 or Genre 2, not containing tag t
            m = r
            # Find movies in Genre 1 which does not contain tag t
            # List of Unique Movies in Genre 1 which does not contain tag t
            m_t_total = []
            for row in reader:
                if row[2] != t and row[1] in m_list_g1 and row[1] not in m_t_total:
                    m_t_total.append(row[1])
            m += len(m_t_total)

            # if r_total == r, the tag is only relevant to genre 1
            # Because irrelevant movies are all in genre 2
            if r_total == r:
                tw_dict[t] = 'This Tag is Only Relevant to Genre 1'
                continue
            # if m == r, no movie in g1 does not contain t, all movies in g1 contain t
            # if M - m - R + r == 0, tag t totally irrelevant with g1
            if r == 0 or m == r or r_total < 2 or m_total - m - r_total + r == 0:
                # P(f|Relevant)
                p_rel = (r + 0.5) / (r_total + 1)
                # P(f|Irrelevant)
                p_irrel = ((m - r) + 0.5) / (math.fabs(m_total - r_total) + 1)
            else:
                # P(f|Relevant)
                p_rel = r / r_total
                # P(f|Irrelevant)
                p_irrel = (m - r) / math.fabs(m_total - r_total)

            # Apply probabilistic weight
            numerator = p_rel * (1 - p_irrel)
            denominator = p_irrel * (1 - p_rel)
            tw_dict[t] = math.log(numerator / denominator, 2) * math.fabs(p_rel - p_irrel)

    return tw_dict
# ----- End of calculate_weight_p_diff_1 -----

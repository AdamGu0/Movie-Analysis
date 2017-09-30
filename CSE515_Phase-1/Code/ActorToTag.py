import csv
import math
import HelperFunctions as helper
import os


# Function for Actor-Tag (Task 1)
def generate(actor_id, model):
    # CSV files
    # file_a = os.path.join(os.pardir, "phase1_dataset/movie-actor.csv")
    # ile_b = os.path.join(os.pardir, "phase1_dataset/mltags.csv")
    # file_c = os.path.join(os.pardir, "phase1_dataset/genome-tags.csv")
    # file_d = os.path.join(os.pardir, "phase1_dataset/imdb-actor-info.csv")
    # CSV files
    file_a = os.path.join(os.pardir, "phase1_testdata/movie-actor.csv")
    file_b = os.path.join(os.pardir, "phase1_testdata/mltags.csv")
    file_c = os.path.join(os.pardir, "phase1_testdata/genome-tags.csv")
    file_d = os.path.join(os.pardir, "phase1_testdata/imdb-actor-info.csv")
    # Output files
    file_tf = os.path.join(os.pardir, "Outputs/Actor2Tag-TF.csv")
    file_tf_idf = os.path.join(os.pardir, "Outputs/Actor2Tag-TF-IDF.csv")

    # All actors counter, means number of total documents
    all_a_count = 0
    if model == 'IDF':
        with open(file_d, newline='') as fD:
            # Read actor info
            reader_d = csv.reader(fD)

            for row_d in reader_d:
                if row_d[0] != 'actorid':
                    all_a_count += 1
    # ----- End of Counting Total Number of Actors -----

    # Open Movie-Actor file
    with open(file_a, newline='') as fA:
        # Read Movie-Actor file
        reader_a = csv.reader(fA)

        # movie_id list
        m_list = []
        # rank list
        r_list = []
        # All rank list
        all_r_list = []

        # Find all MovieIDs and Ranks associated with actor_id
        for row_a in reader_a:
            if row_a[1] == actor_id:
                m_list.append(row_a[0])
                r_list.append(row_a[2])
            if row_a[1] != 'actorid':
                all_r_list.append(row_a[2])
    # ----- End of processing movie-actor file -----

    # If actor_id invalid or does not exist
    if len(m_list) == 0:
        print('No Result for Given Actor due to Relevant MovieID Not Found')
        return

    # Normalize rank list to [0, 1], and map Weight(rank) to ranks
    r_dict = helper.normalize_rank(all_r_list=all_r_list, r_list=r_list)  # dictionary for Rank : Weight(rank)

    # Process mltags file
    with open(file_b, newline='') as fB:
        # Read the mltags file
        reader_b = csv.reader(fB)

        # All timestamp list
        all_ts_list = []
        # tag_id list
        t_list = []
        # timestamp list
        ts_list = []

        # Find all TagIDs and Timestamps associated with each movie_id
        for row_b in reader_b:
            if row_b[1] in m_list:
                t_list.append(row_b[2])
                ts_list.append(row_b[3])
            if row_b[2] != 'tagid':
                all_ts_list.append(row_b[3])

    # ----- End of processing mltags file -----

    # Normalize timestamp list to [0, 1], and map Weight(timestamp) to timestamp
    ts_dict = helper.normalize_timestamp(all_ts_list=all_ts_list, ts_list=ts_list)

    # Open movie-actor & mltags files for total weight calculation
    with open(file_a, newline='') as fA, open(file_b, newline='') as fB:
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

        # TF-IDF Model
        if model == 'IDF':
            for t in tw_dict:
                # List of unique actors who have the tag t
                a_list = []
                fA.seek(0)
                fB.seek(0)
                # The list of movieIDs which associate with tag t
                m_list.clear()
                for row_b in reader_b:
                    if row_b[2] == t:
                        m_list.append(row_b[1])
                # Find actors associated with tag t using movieIDs list
                for row_a in reader_a:
                    if row_a[0] in m_list and row_a[1] not in a_list:
                        a_list.append(row_a[1])
                # TF-IDF Weight for each tag
                w_tag = tw_dict.get(t) * math.log(all_a_count / len(a_list), 2)
                # Update the weight to TF-IDF weight
                tw_dict[t] = w_tag

    # ----- End of Weight Calculation -----

    # Process genome-tag file
    with open(file_c, newline='') as fC, open(file_d, newline='') as fD:
        # Read the genome_tags file
        reader_c = csv.reader(fC)
        reader_d = csv.reader(fD)
        # Get the Actor Info
        # If actor_id is invalid, No results
        actor_name = 'Does Not Exist'
        actor_gender = 'Does Not Exist'
        for row_d in reader_d:
            if row_d[0] == actor_id:
                actor_name = row_d[1]
                actor_gender = row_d[2]
        # Result list, contains header
        result = [['ActorInfo', actor_id, actor_name, actor_gender], ['Tag', 'Weight']]
        # Find the Tag associated with each TagID
        output_view = [(v, k) for k, v in tw_dict.items()]
        output_view.sort(reverse=True)
        for v, k in output_view:
            fC.seek(0)
            # Get Tag's text in File
            for row_c in reader_c:
                if row_c[0] == k:
                    result.append([row_c[1], v])
                    print("%s: %f" % (row_c[1], v))

    # ----- End of processing genome-tags file -----

    # Output to csv file
    if model == 'TF':
        helper.write_csv(file_name=file_tf, result_list=result)

    if model == 'IDF':
        helper.write_csv(file_name=file_tf_idf, result_list=result)

    print('Please Check Outputs Repository for Generated csv File')
# END of Generate Function

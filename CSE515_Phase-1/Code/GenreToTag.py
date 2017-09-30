import csv
import HelperFunctions as helper
import math
import os


# Function for Genre-Tag (Task 2)
def generate(genre, model):
    # CSV files
    # file_a = os.path.join(os.pardir, "phase1_dataset/mlmovies.csv")
    # file_b = os.path.join(os.pardir, "phase1_dataset/mltags.csv")
    # file_c = os.path.join(os.pardir, "phase1_dataset/genome-tags.csv")
    # CSV files
    file_a = os.path.join(os.pardir, "phase1_testdata/mlmovies.csv")
    file_b = os.path.join(os.pardir, "phase1_testdata/mltags.csv")
    file_c = os.path.join(os.pardir, "phase1_testdata/genome-tags.csv")
    # Output files
    file_tf = os.path.join(os.pardir, "Outputs/Genre2Tag-TF.csv")
    file_tf_idf = os.path.join(os.pardir, "Outputs/Genre2Tag-TF-IDF.csv")

    # Open these csv files using with statements
    with open(file_a, newline='') as fA:
        # Read mlmovies file
        reader_a = csv.reader(fA)

        # movie_id list
        m_list = []
        # All Genre Documents List
        all_g_list = []

        # Find all MovieIDs associated with genre
        for row_a in reader_a:
            if genre in row_a[2]:
                m_list.append(row_a[0])
            # Generate Genre Documents
            if row_a[2] != 'genres':
                g_list = row_a[2].split('|')
                for g in g_list:
                    if g not in all_g_list:
                        all_g_list.append(g)
    # ----- End of processing mlmovies file -----

    # If genre invalid or does not exist
    if len(m_list) == 0:
        print('No Result for Given Genre due to Relevant MovieID Not Found')
        return

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
    # Tag - Weight dictionary
    tw_dict = helper.generate_tf(file_name=file_b, t_list=t_list,
                                 ts_list=ts_list, ts_dict=ts_dict, time_weighted=True)

    # Open mlmovies and mltags files for TF-IDF weight calculation
    if model == 'IDF':
        with open(file_a, newline='') as fA, open(file_b, newline='') as fB:
            reader_a = csv.reader(fA)
            reader_b = csv.reader(fB)

        # TF-IDF Model
            for t in tw_dict:
                # To Count number of Genres which have tag t
                # First Need to find all Unique movieIDs that have tag t
                # Then count number of genres associated with MovieIDs
                fA.seek(0)
                fB.seek(0)
                # List of genres which have tag t
                g_t_list = []
                m_list.clear()
                # Find Unique movieIDs for tag t
                for row_b in reader_b:
                    if row_b[2] == t and row_b[1] not in m_list:
                        m_list.append(row_b[1])
                # Find Unique Genres associated with MovieID
                for row_a in reader_a:
                    if row_a[0] in m_list:
                        g_list = row_a[2].split('|')
                        for g in g_list:
                            if g not in g_t_list:
                                g_t_list.append(g)
                # TF-IDF Weight for each tag
                w_tag = tw_dict.get(t) * math.log(len(all_g_list) / len(g_t_list), 2)
                # Update TF-IDF weight
                tw_dict[t] = w_tag
    # ----- End of Weight Calculation -----

    # Process genome-tag file
    with open(file_c, newline='') as fC:
        # Read the genome_tags file
        reader_c = csv.reader(fC)
        # Result list, contains header
        result = [['Genre', genre], ['Tag', 'Weight']]
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

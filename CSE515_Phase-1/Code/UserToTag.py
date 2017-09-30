import csv
import HelperFunctions as helper
import math
import os


# Function for User-Tag (Task 3)
def generate(user_id, model):
    # CSV files
    # file_a = os.path.join(os.pardir, "phase1_dataset/mlratings.csv")
    # file_b = os.path.join(os.pardir, "phase1_dataset/mltags.csv")
    # file_c = os.path.join(os.pardir, "phase1_dataset/genome-tags.csv")
    # file_d = os.path.join(os.pardir, "phase1_dataset/mlusers.csv")
    # CSV files
    file_a = os.path.join(os.pardir, "phase1_testdata/mlratings.csv")
    file_b = os.path.join(os.pardir, "phase1_testdata/mltags.csv")
    file_c = os.path.join(os.pardir, "phase1_testdata/genome-tags.csv")
    file_d = os.path.join(os.pardir, "phase1_testdata/mlusers.csv")
    # Output files
    file_tf = os.path.join(os.pardir, "Outputs/User2Tag-TF.csv")
    file_tf_idf = os.path.join(os.pardir, "Outputs/User2Tag-TF-IDF.csv")

    # All users counter, N for IDF calculation
    all_u_count = 0
    if model == 'IDF':
        with open(file_d, newline='') as fD:
            # Reader for the file
            reader_d = csv.reader(fD)

            for row_d in reader_d:
                if row_d[0] != 'userid':
                    all_u_count += 1
    # ------ End of Processing mlusers file ------
    # Open mlratings file
    with open(file_a, newline='') as fA:
        # Read mlratings file
        reader_a = csv.reader(fA)

        # movie_id list
        m_list = []

        # Find all MovieIDs associated with user_id
        for row_a in reader_a:
            if row_a[1] == user_id:
                m_list.append(row_a[0])

    # ----- End of processing mlratings file -----

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

        # Find all MovieIDs associated with each user_id first
        for row_b in reader_b:
            # Count total tags number and timestamp for IDF calculation
            if row_b[2] != 'tagid':
                all_ts_list.append(row_b[3])
            # Check MovieIDs
            if row_b[0] == user_id:
                # Check whether the movie exists in m_list
                if row_b[1] in m_list:
                    continue
                m_list.append(row_b[1])

        # Find all tags and timestamps from m_list
        fB.seek(0)
        for row_b in reader_b:
            if row_b[1] in m_list:
                t_list.append(row_b[2])
                ts_list.append(row_b[3])

    # ----- End of processing mltags file -----

    # If user_id invalid or does not exist
    if len(t_list) == 0:
        print('No Result for the Given User due to Relevant TagID Not Found')
        return

    # Normalize timestamp list to [0, 1], and map Weight(timestamp) to timestamp
    ts_dict = helper.normalize_timestamp(all_ts_list=all_ts_list, ts_list=ts_list)

    # Tag-Weight dictionary (TF)
    tw_dict = helper.generate_tf(file_name=file_b, t_list=t_list,
                                 ts_list=ts_list, ts_dict=ts_dict, time_weighted=True)

    # Open mltags and mlratings files for TF-IDF weight calculation
    if model == 'IDF':
        with open(file_a, newline='') as fA, open(file_b, newline='') as fB:
            reader_a = csv.reader(fA)
            reader_b = csv.reader(fB)
            for t in tw_dict:
                # List of unique users, who have tag t
                u_list = []
                fA.seek(0)
                fB.seek(0)
                # MovieIDs that have tag t
                m_list.clear()
                # Find in mltags file
                for row_b in reader_b:
                    if row_b[2] == t:
                        m_list.append(row_b[1])
                        if row_b[0] not in u_list:
                            u_list.append(row_b[0])
                # Find in mlratings file
                for row_a in reader_a:
                    if row_a[0] in m_list and row_a[1] not in u_list:
                        u_list.append(row_a[1])
                # TF-IDF Weight for each tag
                w_tag = tw_dict.get(t) * math.log(all_u_count / len(u_list), 2)
                # Update TF-IDF weight
                tw_dict[t] = w_tag

    # ----- End of Weight Calculation -----

    # Process genome-tag file
    with open(file_c, newline='') as fC:
        # Read the genome_tags file
        reader_c = csv.reader(fC)
        # Result list, contains header
        result = [['UserID', user_id], ['Tag', 'Weight']]
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

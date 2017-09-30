import csv
import HelperFunctions as helper
import os


# Function for Genre Differentiation (Task 4)
def differentiate(genre1, genre2, model):
    # CSV files
    # file_a = os.path.join(os.pardir, "phase1_dataset/mlmovies.csv")
    # file_b = os.path.join(os.pardir, "phase1_dataset/mltags.csv")
    # file_c = os.path.join(os.pardir, "phase1_dataset/genome-tags.csv")
    # CSV files
    file_a = os.path.join(os.pardir, "phase1_testdata/mlmovies.csv")
    file_b = os.path.join(os.pardir, "phase1_testdata/mltags.csv")
    file_c = os.path.join(os.pardir, "phase1_testdata/genome-tags.csv")

    # Output files
    file_tf_idf_diff_g1 = os.path.join(os.pardir, "Outputs/GenreDifferentiation-TF-IDF-DIFF-g1.csv")
    file_tf_idf_diff_g2 = os.path.join(os.pardir, "Outputs/GenreDifferentiation-TF-IDF-DIFF-g2.csv")
    file_p_diff_1 = os.path.join(os.pardir, "Outputs/GenreDifferentiation-P-DIFF1.csv")
    file_p_diff_2 = os.path.join(os.pardir, "Outputs/GenreDifferentiation-P-DIFF2.csv")

    # Open these csv files using with statements
    with open(file_a, newline='') as fA:
        # Read mlmovies file
        reader_a = csv.reader(fA)

        # movie_id list for genre1 and genre2
        m_list_g1 = []
        m_list_g2 = []
        # Total Genres Documents List
        all_g_list = []

        # Find all MovieIDs associated with given genres
        for row_a in reader_a:
            if genre1 in row_a[2]:
                m_list_g1.append(row_a[0])
                g_list = row_a[2].split('|')
                for g in g_list:
                    if g not in all_g_list:
                        all_g_list.append(g)
            if genre2 in row_a[2]:
                m_list_g2.append(row_a[0])
                g_list = row_a[2].split('|')
                for g in g_list:
                    if g not in all_g_list:
                        all_g_list.append(g)
    # ----- End of Processing mlmovies file

    # Input check, genre1 and genre2 should both exist
    if len(m_list_g1) == 0 or len(m_list_g2) == 0:
        print('At Least One Input Genre Invalid due to Associated MovieID Not Found')
        return

    with open(file_b, newline='') as fB:
        reader_b = csv.reader(fB)

        # All timestamp list
        all_ts_list = []
        # tag_id list
        t_list_g1 = []
        t_list_g2 = []
        # timestamp list
        ts_list_g1 = []
        ts_list_g2 = []

        # Find all TagIDs and Timestamps associated with each movie_id
        for row_b in reader_b:
            # Movies which have g1
            if row_b[1] in m_list_g1:
                t_list_g1.append(row_b[2])
                ts_list_g1.append(row_b[3])
                if row_b[3] not in all_ts_list:
                    all_ts_list.append(row_b[3])
            # Movies which have g2
            if row_b[1] in m_list_g2:
                t_list_g2.append(row_b[2])
                ts_list_g2.append(row_b[3])
                if row_b[3] not in all_ts_list:
                    all_ts_list.append(row_b[3])

    # Normalize timestamps to [0, 1]
    # timestamp dict for g1
    ts_dict_g1 = helper.normalize_timestamp(all_ts_list=all_ts_list, ts_list=ts_list_g1)
    # timestamp dict for g2
    ts_dict_g2 = helper.normalize_timestamp(all_ts_list=all_ts_list, ts_list=ts_list_g2)

    if model == 'TF-IDF-DIFF':
        # Tag-weight dictionary
        tw_dict_g1 = helper.generate_tf(file_name=file_b, t_list=t_list_g1,
                                        ts_list=ts_list_g1, ts_dict=ts_dict_g1, time_weighted=True)
        tw_dict_g2 = helper.generate_tf(file_name=file_b, t_list=t_list_g2,
                                        ts_list=ts_list_g2, ts_dict=ts_dict_g2, time_weighted=True)

        # Calculate TF-IDF
        helper.calculate_tf_idf(file_a, file_b, all_g_list, tw_dict_g1, m_list_g1, m_list_g2)
        helper.calculate_tf_idf(file_a, file_b, all_g_list, tw_dict_g2, m_list_g1, m_list_g2)

        # Separately Output the results into 2 csv files
        # Process genome-tag file
        with open(file_c, newline='') as fC:
            # Read the genome_tags file
            reader_c = csv.reader(fC)
            # Result list, contains header
            result = [['Genre', genre1], ['Tag', 'Weight']]
            # Find the Tag associated with each TagID
            output_view = [(v, k) for k, v in tw_dict_g1.items()]
            output_view.sort(reverse=True)
            for v, k in output_view:
                fC.seek(0)
                # Get Tag's text in File
                for row_c in reader_c:
                    if row_c[0] == k:
                        result.append([row_c[1], v])
                        print("%s: %f" % (row_c[1], v))

        helper.write_csv(file_name=file_tf_idf_diff_g1, result_list=result)

        # Process genome-tag file
        with open(file_c, newline='') as fC:
            # Read the genome_tags file
            reader_c = csv.reader(fC)
            # Result list, contains header
            result = [['Genre', genre2], ['Tag', 'Weight']]
            # Find the Tag associated with each TagID
            output_view = [(v, k) for k, v in tw_dict_g2.items()]
            output_view.sort(reverse=True)
            for v, k in output_view:
                fC.seek(0)
                # Get Tag's text in File
                for row_c in reader_c:
                    if row_c[0] == k:
                        result.append([row_c[1], v])
                        print("%s: %f" % (row_c[1], v))

        helper.write_csv(file_name=file_tf_idf_diff_g2, result_list=result)
        print('Please Check the two Generated csv Files in Outputs repository')
        return
    # End of if statement TF-IDF-DIFF

    if model == 'P-DIFF1':
        # Get unique tag list
        t_unique_list_g1 = helper.get_unique_list(t_list_g1)

        # Then generate Tag-Movies_in_Genre dict
        tm_dict_g1 = helper.generate_tag_movies_dict(file_name=file_b, t_list=t_unique_list_g1, m_list=m_list_g1)

        # Calculate the weight vector of tags in Genre1
        w_vector = helper.calculate_weight_p_diff_1(file=file_b, tm_dict_r=tm_dict_g1,
                                                    m_list_g1=m_list_g1, m_list_g2=m_list_g2)
        # Process genome-tag file
        with open(file_c, newline='') as fC:
            # Read the genome_tags file
            reader_c = csv.reader(fC)
            # Result list, contains header
            result = [['Genre 1', genre1, 'Genre 2', genre2], ['Tag', 'Weight']]
            # Find the Tag associated with each TagID
            for k in w_vector:
                fC.seek(0)
                # Get Tag's text in File
                for row_c in reader_c:
                    if row_c[0] == k:
                        result.append([row_c[1], w_vector.get(k)])
                        print("%s: %s" % (row_c[1], w_vector.get(k)))

        helper.write_csv(file_p_diff_1, result_list=result)
        return

    if model == 'P-DIFF2':
        # Get unique tag list
        t_unique_list_g1 = helper.get_unique_list(t_list_g1)

        # Generate the Tag-Movie_in dict
        tm_dict_g2 = helper.generate_tag_movies_dict(file_name=file_b, t_list=t_unique_list_g1, m_list=m_list_g2)
        # And reverse it to the Tag-Movie_Not_in
        for t in tm_dict_g2:
            movie_not_in = len(m_list_g2) - tm_dict_g2.get(t)
            tm_dict_g2[t] = movie_not_in

        w_vector = helper.calculate_weight_p_diff_2(file=file_b, tm_dict_r=tm_dict_g2,
                                                    m_list_g1=m_list_g1, m_list_g2=m_list_g2)
        # Process genome-tag file
        with open(file_c, newline='') as fC:
            # Read the genome_tags file
            reader_c = csv.reader(fC)
            # Result list, contains header
            result = [['Genre 1', genre1, 'Genre 2', genre2], ['Tag', 'Weight']]
            # Find the Tag associated with each TagID
            for k in w_vector:
                fC.seek(0)
                # Get Tag's text in File
                for row_c in reader_c:
                    if row_c[0] == k:
                        result.append([row_c[1], w_vector.get(k)])
                        print("%s: %s" % (row_c[1], w_vector.get(k)))

        helper.write_csv(file_name=file_p_diff_2, result_list=result)
        return
# ----- End of differentiate Function -----

# Function Caller for Task 3 and Task 4

import MatrixGenerator as matrixG
import PersonalizedPageRank as pPR
import RWRPageRank as rwrPR
import HelperFunctions as hpF
import csv
import os


# Interface for Task 3a
def task_3_a(seed_list, alpha):
    # Get the index of each seed
    seed_index_list = []
    all_actor_list = []
    all_actor_name = []
    # Read File
    file_a = os.path.join(os.pardir, "Phase2_data/imdb-actor-info.csv")
    with open(file_a, 'r') as f:
        reader = csv.reader(f)
        # Skip the Header
        next(reader, None)

        for row in reader:
            all_actor_list.append(row[0])
            all_actor_name.append(row[1])
    # End of File reading

    # Get the index of each actor ID
    for j in range(0, len(all_actor_list)):
        if all_actor_list[j] in seed_list:
            seed_index_list.append(j)

    # Get Actor-Actor Similarity Matrix
    aa_matrix = matrixG.actor_actor_matrix()

    # Get transition matrix
    trans_list = matrixG.transition_matrix(aa_matrix)

    # Call Personalized PageRank
    # If alpha is not specified, run with predefined probability
    if alpha < 0.0 or alpha > 1.0:
        print("Alpha not specified, running with predefined value of 0.9")
        pr_result = rwrPR.rwr_page_rank(seeds=seed_index_list, trans_2d_list=trans_list)
    else:
        pr_result = rwrPR.rwr_page_rank(seeds=seed_index_list, trans_2d_list=trans_list, alpha=alpha)

    # Rescaling
    pr_result_scaled = hpF.pr_vector_rescale(pr_result)

    # Map, Sort, and Output the result
    # Key - Index in all_actor_list, Value - PR Value of the actor
    pr_dict = {}
    for i in range(0, len(pr_result_scaled)):
        pr_dict[i] = pr_result_scaled[i]

    output_view = [(v, k) for k, v in pr_dict.items()]
    output_view.sort(reverse=True)
    output_list = []
    counter = 0
    for v, k in output_view:
        if counter < 10 and k not in seed_index_list:
            output_list.append([all_actor_list[k], all_actor_name[k], v])
            print(all_actor_list[k], all_actor_name[k], v)
            counter += 1

    # Output
    file_out = os.path.join(os.pardir, "Outputs/Task-3-a.csv")
    hpF.write_csv(file_out, result_list=output_list)
# ----- End of Task_3_a -----


# Interface for Task 3b
def task_3_b(seed_list, alpha):
    # Get the index of each seed
    seed_index_list = []
    all_actor_list = []
    all_actor_name = []
    # Read File
    file_a = os.path.join(os.pardir, "Phase2_data/imdb-actor-info.csv")
    with open(file_a, 'r') as f:
        reader = csv.reader(f)
        # Skip the Header
        next(reader, None)

        for row in reader:
            all_actor_list.append(row[0])
            all_actor_name.append(row[1])
    # End of File reading

    # Get the index of each actor ID
    for j in range(0, len(all_actor_list)):
        if all_actor_list[j] in seed_list:
            seed_index_list.append(j)

    # Get Actor-Actor Similarity Matrix
    aa_matrix = matrixG.coactor_coactor_matrix()

    # Get transition matrix
    trans_list = matrixG.transition_matrix(aa_matrix)

    # Call Personalized PageRank
    # If alpha is not specified, run with predefined probability
    if alpha < 0.0 or alpha > 1.0:
        print("Alpha not specified, running with predefined value of 0.9")
        pr_result = rwrPR.rwr_page_rank(seeds=seed_index_list, trans_2d_list=trans_list)
    else:
        pr_result = rwrPR.rwr_page_rank(seeds=seed_index_list, trans_2d_list=trans_list, alpha=alpha)

    # Rescaling
    pr_result_scaled = hpF.pr_vector_rescale(pr_result)

    # Map, Sort, and Output the result
    # Key - Index in all_actor_list, Value - PR Value of the actor
    pr_dict = {}
    for i in range(0, len(pr_result_scaled)):
        pr_dict[i] = pr_result_scaled[i]

    output_view = [(v, k) for k, v in pr_dict.items()]
    output_view.sort(reverse=True)
    output_list = []
    counter = 0
    for v, k in output_view:
        if counter < 10 and k not in seed_index_list:
            output_list.append([all_actor_list[k], all_actor_name[k], v])
            print(all_actor_list[k], all_actor_name[k], v)
            counter += 1

    # Output
    file_out = os.path.join(os.pardir, "Outputs/Task-3-b.csv")
    hpF.write_csv(file_out, result_list=output_list)
# ----- End of Task_3_b -----


# Interface for Task 4
def task_4(user_id, alpha):
    # Get the index of each seed
    seed_index_list = []
    # Movie IDs related to the given User, seed list
    user_movie_id = []
    all_movie_list = []
    all_movie_name = []
    # csv files
    file_a = os.path.join(os.pardir, "Phase2_data/mltags.csv")
    file_b = os.path.join(os.pardir, "Phase2_data/mlratings.csv")
    file_c = os.path.join(os.pardir, "Phase2_data/mlmovies.csv")
    # Get all movie IDs
    with open(file_c, 'r') as fc:
        reader_c = csv.reader(fc)
        next(reader_c, None)

        for row in reader_c:
            all_movie_list.append(row[0])
            all_movie_name.append(row[1])
    # Get Seeds
    with open(file_a, 'r') as fa, open(file_b, 'r') as fb:
        reader_a = csv.reader(fa)
        reader_b = csv.reader(fb)
        # Skip the Header
        next(reader_a, None)
        next(reader_b, None)

        for row in reader_a:
            if row[0] == user_id:
                user_movie_id.append(row[1])

        for row in reader_b:
            if row[1] == user_id and row[0] not in user_movie_id:
                user_movie_id.append(row[0])
    # End of File reading

    # If seed list is empty
    if len(user_movie_id) == 0:
        print("The User Have Not Watched Any Movie")
        output_list = []
        for i in range(0, 5):
            output_list.append([all_movie_list[i], all_movie_name[i], 0.0])
            print(all_movie_list[i], all_movie_name[i], 0.0)
        return

    # Get the index of each actor ID
    for j in range(0, len(all_movie_list)):
        if all_movie_list[j] in user_movie_id:
            seed_index_list.append(j)

    # Get Movie-Movie Similarity Matrix
    mm_matrix = matrixG.movie_movie_matrix(user_id)

    # Get transition matrix
    trans_list = matrixG.transition_matrix(mm_matrix)

    # Call Personalized PageRank
    # If alpha is not specified, run with predefined probability
    if alpha < 0.0 or alpha > 1.0:
        print("Alpha not specified, running with predefined value of 0.9")
        pr_result = pPR.personalized_page_rank(seeds=seed_index_list, trans_2d_list=trans_list)
    else:
        pr_result = pPR.personalized_page_rank(seeds=seed_index_list, trans_2d_list=trans_list, alpha=alpha)

    # Rescaling
    pr_result_scaled = hpF.pr_vector_rescale(pr_result)

    # Map, Sort, and Output the result
    # Key - Index in all_actor_list, Value - PR Value of the actor
    pr_dict = {}
    for i in range(0, len(pr_result_scaled)):
        pr_dict[i] = pr_result_scaled[i]

    output_view = [(v, k) for k, v in pr_dict.items()]
    output_view.sort(reverse=True)
    output_list = []
    counter = 0
    for v, k in output_view:
        if counter < 5 and k not in seed_index_list:
            output_list.append([all_movie_list[k], all_movie_name[k], v])
            print(all_movie_list[k], all_movie_name[k], v)
            counter += 1

    # Output
    file_out = os.path.join(os.pardir, "Outputs/Task-4.csv")
    hpF.write_csv(file_out, result_list=output_list)
# ----- End of Task_4 -----

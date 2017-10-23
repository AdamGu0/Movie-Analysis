# Command Line Interface

import TaskCaller as tCaller

print('Type \'help\' or \'?\' to List Commands for Task 3 and Task 4')
print('Type \'exit\' or \'q\' to Quit The Application')
# Receive the input from User
while True:
    # Get and Parse the input
    str_in = input('--> ')
    str_in_list = str_in.split()

    if str_in == 'help' or str_in == '?':
        print('1. For Task 3a: task_3_a alpha')
        print('2. For Task 3b: task_3_b alpha')
        print('3. For Task 4: task_4 userID alpha')
        print('Alpha: The Probability of Walking Along Outgoing Edges')
    elif str_in == 'exit' or str_in == 'q':
        break
    # Call different function in different model
    elif len(str_in_list) == 2 and str_in_list[0] == 'task_3_a':
        print('Please Provide Seeds, Split by SPACE:')
        seed_in = input('--> ')
        seed_list = seed_in.split()
        tCaller.task_3_a(seed_list, float(str_in_list[1]))

    elif len(str_in_list) == 2 and str_in_list[0] == 'task_3_b':
        print('Please Provide Seeds, Split by SPACE:')
        seed_in = input('--> ')
        seed_list = seed_in.split()
        tCaller.task_3_b(seed_list, float(str_in_list[1]))

    elif len(str_in_list) == 3 and str_in_list[0] == 'task_4':
        tCaller.task_4(str_in_list[1], float(str_in_list[2]))

    else:
        print('Invalid Command')
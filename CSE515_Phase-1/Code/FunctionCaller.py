import ActorToTag as actorTag
import GenreToTag as genreTag
import UserToTag as userTag
import GenreDifferentiation as genreDiff

print('Type \'help\' or \'?\' to List Available Commands')
print('Type \'exit\' or \'q\' to Quit The Application')
# Receive the input from User
while True:
    # Get and Parse the input
    str_in = input('--> ')
    str_in_list = str_in.split()

    if str_in == 'help' or str_in == '?':
        print('1. For Actor-Tag Vector: print_actor_vector actorID model')
        print('2. For Genre-Tag Vector: print_genre_vector genre model')
        print('3. For User-Tag Vector: print_user_vector userID model')
        print('4. For Genres Differentiation: differentiate_genre genre1 genre2 model')
        print('Available Model for Commands #1, #2, and #3: \'TF\' or \'TF-IDF\'')
        print('Available Model for Command #4: \'TF-IDF-DIFF\', \'P-DIFF1\', or \'P-DIFF2\'')
    elif str_in == 'exit' or str_in == 'q':
        break
    # Call different function in different model
    elif len(str_in_list) == 3 and str_in_list[0] == 'print_actor_vector':
        if str_in_list[2].upper() == 'TF':
            actorTag.generate(str_in_list[1], 'TF')
        elif str_in_list[2].upper() == 'TF-IDF':
            actorTag.generate(str_in_list[1], 'IDF')
        else:
            print('Model Invalid, Please Choose From \'TF\' or \'TF-IDF\'')
    elif len(str_in_list) == 3 and str_in_list[0] == 'print_genre_vector':
        if str_in_list[2].upper() == 'TF':
            genreTag.generate(str_in_list[1], 'TF')
        elif str_in_list[2].upper() == 'TF-IDF':
            genreTag.generate(str_in_list[1], 'IDF')
        else:
            print('Model Invalid, Please Choose From \'TF\' or \'TF-IDF\'')
    elif len(str_in_list) == 3 and str_in_list[0] == 'print_user_vector':
        if str_in_list[2].upper() == 'TF':
            userTag.generate(str_in_list[1], 'TF')
        elif str_in_list[2].upper() == 'TF-IDF':
            userTag.generate(str_in_list[1], 'IDF')
        else:
            print('Model Invalid, Please Choose From \'TF\' or \'TF-IDF\'')
    elif len(str_in_list) == 4 and str_in_list[0] == 'differentiate_genre':
        if (str_in_list[3].upper() == 'TF-IDF-DIFF' or
                str_in_list[3].upper() == 'P-DIFF1' or
                str_in_list[3].upper() == 'P-DIFF2'):
            genreDiff.differentiate(str_in_list[1], str_in_list[2], str_in_list[3].upper())
        else:
            print('Model Invalid, Please Choose From \'TF-IDF-DIFF\', \'P-DIFF1\', or \'P-DIFF2\'')
    else:
        print('Invalid Command')

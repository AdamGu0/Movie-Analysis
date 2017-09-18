This project is under Python 3.6 with dependencies pandas and numpy. Please note the project will not work under Python 2.7.
After the environment is setup, go to Code director, and run 
		python src/phase1.py command. 
“command” can be a single command or a txt file of command as shown in the sample inputs below. All commands should be in the format given in the project description.  The code is tested on windows 10 and Ubuntu 14, but not tested on Mac OS. 

Sample inputs with a file:
		 python src/phase1.py testcase.txt
The following commands are in the testcase.txt:
print_actor_vector 1484 TF-IDF
print_actor_vector 1484 TF
print_genre_vector Western TF
print_genre_vector Western TF-IDF
print_user_vector 146 TF
print_user_vector 146 TF-IDF

Sample inputs with a command
python src/phase1.py print_actor_vector 1484 TF-IDF
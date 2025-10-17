#freeze command is used to print all installed packages with their versions
#it is used as follows:
#pip freeze
#best practice is to redirect the output to a requirements.txt file
#pip freeze > requirements.txt
#so that it can be used later to recreate the  same environment using
#pip install -r requirements.txt
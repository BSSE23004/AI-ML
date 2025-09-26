import os
import pyjokes
import pyttsx3


def startJoking():
    engine =  pyttsx3.init()
    joke = pyjokes.get_joke()
    engine.say(joke)
    engine.runAndWait()
    print(joke)


def print_directory_contents(dir_path):
    try:
        entries = os.listdir(dir_path)
    except FileNotFoundError:
        print(f"Error: Directory '{dir_path}' does not exist.")
        return
    except PermissionError:
        print(f"Error: Permission denied to access '{dir_path}'.")
        return

    print(f"Contents of directory '{dir_path}':")
    for entry in entries:
        print(entry)

if __name__ == "__main__":
    path = input("Enter directory path (or press Enter for current directory): ").strip()
    if path == "":
        path = "."  # current directory
    print_directory_contents(path)
    startJoking()

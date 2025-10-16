def myfunc():
    print("This is myfunc from module.py")

#comment the next line to see the difference
myfunc()

if __name__ == "__main__":
    print("module.py is being run directly")
    myfunc()
    print(__name__)#__name__ that tell that this file is being run directly or being imported
# if this file is being run directly __name__ will be __main__ else it will be module 
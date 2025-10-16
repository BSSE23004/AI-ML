from module import myfunc
#when we import the file the whole file is imported and (by default) executed
#if not protected by if __name__ == "__main__": block
#that is why we see the output of myfunc without calling it here
print(__name__)
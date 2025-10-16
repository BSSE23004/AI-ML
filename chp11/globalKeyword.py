a= 69

def changingGlobal():
    global a
    a = 420
    print(a)
print(a)
changingGlobal()
print(a)

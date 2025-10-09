f = open("chp9/filehandling.py", "r")
content = f.read()
print(content)
f.close()

f = open("chp9/newfile.txt", "w")
f.write("This is a new file.\n")
f.write("It contains multiple lines.\n")
f.close()
f = open("chp9/newfile.txt", "a")
f.write("This line is appended.\n")
f.close()
f = open("chp9/newfile.txt", "r")
print(f.read())
f.close()

f = open("chp9/newfile.txt", "r")
lines = f.readlines()
for line in lines:
    print(line.strip(),type(line))
f.close()

f = open("chp9/newfile.txt", "r")
print(f.readlines())
f.close()

#best practice is to use with statement because it automatically handles closing the file
with open("chp9/filehandling.py", "r") as f:
    content = f.read()
    print(content)
# no need to call f.close(), it's done automatically


data = ""
with open("chp9/newfile.txt", "r") as f:
    data = f.read()
newdata= data.replace("new","old")
print(newdata)
with open("chp9/newfile.txt", "w") as f:
    f.write(newdata)

# copying file
with open("chp9/newfile.txt", "r") as f:
    data = f.read()
with open("chp9/copyfile.txt", "w") as f:
    f.write(data)

# renaming and deleting files
import os
os.rename("chp9/copyfile.txt", "chp9/renamedfile.txt")
os.remove("chp9/renamedfile.txt")





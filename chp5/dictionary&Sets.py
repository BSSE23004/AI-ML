print('''Properties of Dictionary:
1. Dictionary is a collection which is unordered, changeable and indexed.
2. In Python dictionaries are written with curly brackets, and they have keys and values.
3. Dictionary items are presented in key:value pairs, and can be referred to by using the''')

marks = {
    "Math": 90,
    "Science": 85,
    "English": 88,
    "History": 92}
print(marks)
print(type(marks))#dict
print(marks["Math"])#90
print(marks["Science"])#85
print(marks["English"])#88
print(marks["History"])#92
print(marks.get("Math"))#90
print(marks.get("Science"))#85
print(marks.get("English"))#88
print(marks.get("History"))#92
print(marks.get("Geography"))#None
print(marks.get("Geography", "Not Found"))#Not Found
print(marks.keys())#dict_keys(['Math', 'Science', 'English', 'History'])
print(marks.values())#dict_values([90, 85, 88, 92])
print(marks.items())#dict_items([('Math', 90), ('Science', 85), ('English', 88), ('History', 92)])
marks["Math"] = 95
marks["Science"] = 90
marks["English"] = 89
marks["History"] = 93
print(marks)#{'Math': 95, 'Science': 90, 'English': 89, 'History': 93}
marks["Geography"] = 80
print(marks)#{'Math': 95, 'Science': 90, 'English': 89, 'History': 93, 'Geography': 80}
del marks["Geography"]
print("After Deleting Geography")
print(marks)#{'Math': 95, 'Science': 90, 'English': 89, 'History': 93}
marks.pop("Math")
print("After Popping Math")
print(marks)#{'Math': 95, 'Science': 90, 'English': 89}
marks.popitem()
print("After Popping Item")
print(marks)#{'Math': 95, 'Science': 90}
marks.clear()
print(marks)#{}
print(len(marks))#0

student = {
    "name": "John",
    "age": 20,
    "courses": ["Math", "Science"]}
print(student)#{'name': 'John', 'age': 20, 'courses':
print(type(student))#dict
print(student["name"])#John
print(student["age"])#20
print(student["courses"])#['Math', 'Science']
print(student.get("name"))#John
print(student.get("age"))#20
print(student.get("courses"))#['Math', 'Science']
print(student)
print(student.get("address", "Not Found"))#Not Found
student["age"] = 21
student["courses"].append("English")
print(student)#{'name': 'John', 'age': 21, 'courses':
#setdefault() method returns the value of a key (if the key is in dictionary). If not, it inserts the key with a specified value.
print(student.setdefault("address", "123 Main St"))#123 Main St
print(student)#{'name': 'John', 'age': 21, 'courses':
student.update({"age": 22, "name": "Jane"})
print(student)#{'name': 'Jane', 'age': 22, 'courses':
print(student.keys())#dict_keys(['name', 'age', 'courses', 'address'])
print(student.values())#dict_values(['Jane', 22, ['Math', 'Science', 'English'], '123 Main St']) 

print("------------------Sets------------------")
print('''Properties of Sets:
1. A set is a collection which is unordered, unchangeable*, and unindexed.
2. Sets are written with curly brackets.
3. Set items are unordered, unchangeable, and do not allow duplicate values.''')
set1 = {}
print(type(set1))#dict
set2 = {1, 2, 3}
print(type(set2))#set
fruits = {"apple", "banana", "cherry"}
print(fruits)#{'banana', 'cherry', 'apple'}
print(type(fruits))#set
print("Length of fruits: ",len(fruits))#3
print("\"banana\" in fruits","banana" in fruits)#True
print("\"grape\" in fruits","grape" in fruits)#False
fruits.add("orange")
print("After Adding orange")
print(fruits)#{'banana', 'cherry', 'orange', 'apple'}
fruits.remove("banana")
print("After Removing banana")
print(fruits)#{'cherry', 'orange', 'apple'}
fruits.discard("cherry")
print("After Discarding cherry")
print(fruits)#{'orange', 'apple'}
fruits.pop()
print("After Popping an item")
print(fruits)#remaining item
fruits.clear()
print("After Clearing the set")
print(fruits)#set()
del fruits
# print(fruits)#NameError: name 'fruits' is not defined
A = {"apple", "banana", "cherry"}
B = {"google", "microsoft", "apple"}
print("A,B",A,B)#{'banana', 'cherry', 'apple'} {'microsoft', 'google', 'apple'}
print("A.union(B)",A.union(B))#{'microsoft', 'banana', 'cherry', 'google', 'apple'}
print(" A.intersection(B)",A.intersection(B))#{'apple'}
print("A.symmetric_difference(B)",A.symmetric_difference(B))#{'microsoft', 'banana', 'cherry', 'google'}
print("A.difference(B)",A.difference(B))#{'banana', 'cherry'}
print(B.difference(A))#{'microsoft', 'google'}
print(A.isdisjoint(B))#False
C = {"kiwi", "mango"}
print("A.isdisjoint(C)",A.isdisjoint(C))#True
print("A.issubset(B)",A.issubset(B))#False
D = {"apple", "banana"}
print("D.issubset(A)",D.issubset(A))#True
print("A.issuperset(D)",A.issuperset(D))#True
E = {"apple", "kiwi"}
print("A.issuperset(E)",A.issuperset(E))#False
F = {"banana", "cherry", "apple", "kiwi", "mango"}
print("A.issubset(F)",A.issubset(F))#True
print("F.issuperset(A)",F.issuperset(A))#True
G = {"banana", "cherry", "apple", "kiwi", "mango"}
A.update(G)
print("After Updating A with G")
print(A)#{'banana', 'cherry', 'kiwi', 'mango',
print(B)#{'microsoft', 'google', 'apple'}
B.update(A)
print("After Updating B with A")
print(B)#{'microsoft', 'banana', 'kiwi', 'cherry',
print(A)#{'banana', 'cherry', 'kiwi', 'mango',
A.intersection_update(B)
print("After Intersection Update of A with B")
print(A)#{'banana', 'cherry', 'apple'}
print(B)#{'microsoft', 'banana', 'kiwi', 'cherry',
A.symmetric_difference_update(B)
print("After Symmetric Difference Update of A with B")
print(A)#{'microsoft', 'kiwi', 'apple', 'mango',
print(B)#{'microsoft', 'banana', 'kiwi', 'cherry',
A.difference_update(B)
print("After Difference Update of A with B")
print(A)#{'apple', 'mango'}
print(B)#{'microsoft', 'banana', 'kiwi', 'cherry',
A = {"apple", "banana", "cherry"}
B = {"google", "microsoft", "apple"}
print(A,B)#{'banana', 'cherry', 'apple'} {'microsoft', 'google', 'apple'}
print("A|B",A | B)#{'microsoft', 'banana', 'cherry', 'google', 'apple'}
print("A&B",A & B)#{'apple'}
print("A^B",A ^ B)#{'microsoft', 'banana', 'cherry', 'google'}
print("A-B",A - B)#{'banana', 'cherry'}
print("B-A",B - A)#{'microsoft', 'google'}
print("A<=B",A <= B)#False
D = {"apple", "banana"}
print("D<=A",D <= A)#True
print("A>=D",A >= D)#True
E = {"apple", "kiwi"}
print("E<=A",E <= A)#False

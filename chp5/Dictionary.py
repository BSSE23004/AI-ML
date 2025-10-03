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






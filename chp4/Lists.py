list1 = ["Ibrahim",'Abdul','''Sattar''',True,False,3.14,4,]
print(list1)
print(type(list1))

for item in list1:
    print(item," ",end="")
    print(type(item))

print("\nLength of list1 is: ",len(list1))
print("list1[0]: ",list1[0])
print("list1[1]: ",list1[1])
print("list1[2]: ",list1[2])
print("list1[3]: ",list1[3])
print("list1[4]: ",list1[4])
print("list1[5]: ",list1[5])
print("list1[6]: ",list1[6])
print("list1[-1]: ",list1[-1])
print("list1[-2]: ",list1[-2])
print("list1[-3]: ",list1[-3])
print("list1[-4]: ",list1[-4])
print("list1[-5]: ",list1[-5])
print("list1[-6]: ",list1[-6])
print("list1[-7]: ",list1[-7])
print("list1[0:3]: ",list1[0:3])
print("list1[2:5]: ",list1[2:5])
print("list1[::2]: ",list1[::2])
print("list1[1::2]: ",list1[1::2])
print("list1[::-1]: ",list1[::-1])

list1[0] = "Sabun"
list1[3] = "True"
print("After Updation: ",list1)
list1.append("New Item")
print("After Appending: ",list1)
list1.insert(1,"Inserted Item")
print("After Inserting: ",list1)
list1.remove("True")
print("After Removing: ",list1)
popped_item = list1.pop()
print("After Popping: ",list1)
print("Popped Item: ",popped_item)
list2 = [8,2,6,9,1,6,2]
print("List2: ",list2)
combined_list = list1 + list2
print("Combined List: ",combined_list)
list1.extend(list2)
print("List1 after extending with List2: ",list1)
list1.clear()
print("List1 after clearing: ",list1)
print("Length of List1 after clearing: ",len(list1))
print("Length of List2: ",len(list2))
list2.sort()
print("Sorted List2: ",list2)
list2.reverse()
print("Reversed List2: ",list2)
print("Index of 6 in List2: ",list2.index(6))
print("Count of 2 in List2: ",list2.count(2))


numbers = []

for i in range(1,11):
    numbers.append(int(input("Enter number "+str(i)+": ")))

numbers.sort()
print("Sorted Numbers: ",numbers)
print("Smallest Number: ",numbers[0])
print("Largest Number: ",numbers[-1])

#enumerate
print("Using enumerate:")
for index, value in enumerate(numbers):
    print(f"Index {index}: Value {value}")

#list comprehension
squared_numbers = [x**2 for x in numbers]
print("Squared Numbers using list comprehension: ",squared_numbers)
#filtering even numbers using list comprehension
even_numbers = [x for x in numbers if x%2==0]
print("Even Numbers using list comprehension: ",even_numbers)
#map to convert numbers to strings
string_numbers = list(map(str, numbers))
print("String Numbers using map: ",string_numbers)
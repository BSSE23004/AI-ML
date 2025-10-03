print("------------------Sets------------------")
print('''Properties of Sets:
1. A set is a collection which is unordered, unchangeable*, and unindexed.
2. Sets are written with curly brackets.
3. Set items are unordered, unchangeable, and do not allow duplicate values.
4. Sets cannot contain mutable items like lists, dictionaries, or other sets, but they can contain immutable items like strings, numbers, or tuples.''')
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
print("B.difference(A)",B.difference(A))#{'microsoft', 'google'}
print("A.isdisjoint(B)",A.isdisjoint(B))#False
C = {"kiwi", "mango"}
print("C",C)#{'kiwi', 'mango'}
print("A.isdisjoint(C)",A.isdisjoint(C))#True
print("A.issubset(B)",A.issubset(B))#False
D = {"apple", "banana"}
print("D",D)#{'banana', 'apple'}
print("D.issubset(A)",D.issubset(A))#True
print("A.issuperset(D)",A.issuperset(D))#True
E = {"apple", "kiwi"}
print("E",E)#{'kiwi', 'apple'}
print("A.issuperset(E)",A.issuperset(E))#False
F = {"banana", "cherry", "apple", "kiwi", "mango"}
print("F",F)#{'banana', 'cherry', 'kiwi', 'mango', 'apple'}
print("A.issubset(F)",A.issubset(F))#True
print("F.issuperset(A)",F.issuperset(A))#True
G = {"banana", "cherry", "apple", "kiwi", "mango"}
print("G",G)#{'banana', 'cherry', 'kiwi', 'mango', 'apple'}
A.update(G)
print("After Updating A with G")
print("A",A)#{'banana', 'cherry', 'kiwi', 'mango',
print("B",B)#{'microsoft', 'google', 'apple'}
B.update(A)
print("After Updating B with A")
print("B",B)#{'microsoft', 'banana', 'kiwi', 'cherry',
print("A",A)#{'banana', 'cherry', 'kiwi', 'mango',
A.intersection_update(B)
print("After Intersection Update of A with B")
print("A",A)#{'banana', 'cherry', 'apple'}
print("B",B)#{'microsoft', 'banana', 'kiwi', 'cherry',
A.symmetric_difference_update(B)
print("After Symmetric Difference Update of A with B")
print("A",A)#{'microsoft', 'kiwi', 'apple', 'mango',
print("B",B)#{'microsoft', 'banana', 'kiwi', 'cherry',
A.difference_update(B)
print("After Difference Update of A with B")
print("A",A)#{'apple', 'mango'}
print("B",B)#{'microsoft', 'banana', 'kiwi', 'cherry',
A = {"apple", "banana", "cherry"}
B = {"google", "microsoft", "apple"}
print("A,B",A,B)#{'banana', 'cherry', 'apple'} {'microsoft', 'google', 'apple'}
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

practiceSet = {69, "Sixty Nine", "69",69.69,69.0}
print(practiceSet)#{69, 'Sixty Nine', '69', 69.69}
print(len(practiceSet))#4
print(type(practiceSet))#set
practiceSet.clear()

uniqueNumbers = set()

for i in range(1, 11):
    num = int(input("Enter a number: "))
    uniqueNumbers.add(num)

print("Unique Numbers: ", uniqueNumbers)
print("Count of Unique Numbers: ", len(uniqueNumbers))

# practiceSet = {[1,2,3], (4,5,6), {7,8,9}}#TypeError: unhashable type: 'list'
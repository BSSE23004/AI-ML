for i in range(5):
    print("Iteration", i)

print("Loop finished")

for i in range(1,5):
    print("Iteration", i)
print("Loop finished")

count = 0
while count < 5:
    print("Count is", count)
    count += 1
print("While loop finished")

mixedList = [1, "two", 3.0, "four", 5]

for item in mixedList:
    print("Item:", item)
    print("Type:", type(item))
print("Finished iterating through mixedList")

i = 0
while (i<len(mixedList)):
    print("Item at index", i, "is", mixedList[i])
    i += 1
print("Finished iterating through mixedList with while loop")

#range function
#range(start, stop, step)
for i in range(0, 10, 2):
    print("Even number:", i)
print("Finished printing even numbers")

for i in "Ibrahim Abdul Sattar":
    print(i)
print("Finished iterating through string")

#for loop with else

for i in range(3):
    print("Iteration", i)
else:
    print("Loop completed without break")
print("Finished for loop with else")

#loop with break

for i in range(5):
    if i == 3:
        print("Breaking the loop at", i)
        break
    print("Iteration", i)
print("Finished loop with break")

#loop with continue
for i in range(5):
    if i == 2:
        print("Skipping iteration", i)
        continue
    print("Iteration", i)
print("Finished loop with continue")

#printing the table of given number

num = input("Enter a number to print its table: ")
num = int(num)
for i in range(1, 11):
    product = num * i
    print(f"{num} x {i} = {product}")   
print("Finished printing the table")

#program to check if a number is prime or not
number = int(input("Enter a number to check if it's prime: "))
is_prime = True
if number <= 1:
    is_prime = False
else:
    for i in range(2, int(number**0.5) + 1):
        if number % i == 0:
            is_prime = False
            break   
if is_prime:
    print(f"{number} is a prime number.")
else:
    print(f"{number} is not a prime number.")
print("Finished prime check")

#program to find the factorial of a number
num = int(input("Enter a number to find its factorial: "))
factorial = 1
for i in range(1, num + 1):
    factorial *= i
print(f"The factorial of {num} is {factorial}.")
print("Finished calculating factorial")

#print table in reverse order
num = int(input("Enter a number to print its table in reverse order: "))
for i in range(10, 0, -1):
    product = num * i
    print(f"{num} x {i} = {product}")
print("Finished printing the table in reverse order")

#program to find the sum of first n natural numbers
n = int(input("Enter a number to find the sum of first n natural numbers: "))
sum_n = 0
for i in range(1, n + 1):
    sum_n += i
print(f"The sum of the first {n} natural numbers is {sum_n}.")
print("Finished calculating the sum")
#program to print Fibonacci series up to n terms
n_terms = int(input("Enter the number of terms for Fibonacci series: "))
a, b = 0, 1
print("Fibonacci series:")
for _ in range(n_terms):
    print(a, end=' ')
    a, b = b, a + b
print("\nFinished printing Fibonacci series")

#program to print * pyramid of given rows
rows = int(input("Enter the number of rows for the pyramid: "))
for i in range(1, rows + 1):
    print('* ' * i)
print("Finished printing the pyramid")
#program to find the largest number in a list
numbers = [34, 12, 45, 67, 23, 89, 10]
largest = numbers[0]
for num in numbers:
    if num > largest:
        largest = num
print(f"The largest number in the list is {largest}.")
print("Finished finding the largest number")


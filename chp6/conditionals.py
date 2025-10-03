maths = int(input("Enter your maths marks: "))
science = int(input("Enter your science marks: "))
english = int(input("Enter your english marks: "))

total = maths + science + english
percentage = (total / 300) * 100

if percentage >= 90:
    grade = "A"
elif percentage >= 80:
    grade = "B"
elif percentage >= 70:
    grade = "C"
elif percentage >= 60:
    grade = "D"
elif percentage >= 50:
    grade = "E"
else:
    grade = "F"

print(f"Total Marks: {total}/300")
print(f"Percentage: {percentage:.2f}%")
print(f"Grade: {grade}")

spamMsg = input("Enter your message: ")
spamMsg = spamMsg.lower()
if spamMsg.find("make a lot of money") != -1:
    print("This is a spam message")
elif "buy now" in spamMsg:
    print("This is a spam message")
elif "subscribe this" in spamMsg:
    print("This is a spam message")
elif "click this" in spamMsg:
    print("This is a spam message")
else:
    print("This is not a spam message")

# Short Hand If ... Else
age = int(input("Enter your age: "))
status = "Eligible" if age >= 18 else "Not Eligible"
print(f"You are {status} to vote.")

# Nested If
num = int(input("Enter a number: "))
if num >= 0:
    if num == 0:
        print("You entered zero.")
    else:
        print("You entered a positive number.")
else:
    print("You entered a negative number.")

# Logical Operators
username = input("Enter your username: ")
password = input("Enter your password: ")
if username == "admin" and password == "12345":
    print("Login Successful")
else:
    print("Login Failed")

# Membership Operators
fruits = ["apple", "banana", "cherry"]
fruit = input("Enter a fruit name: ")
if fruit in fruits:
    print(f"{fruit} is available.")
else:
    print(f"{fruit} is not available.")

# Identity Operators
a = [1, 2, 3]
b = a
c = a[:]
print(a is b)  # True
print(a is c)  # False
print(a == c)  # True
print(a is not c)  # True
print(a != c)  # False
print(b is not c)  # True
print(b != c)  # False
print(a is not b)  # False
print(a != b)  # False
print(b is c)  # False
print(b == c)  # True
print(a is a)  # True
print(a == a)  # True
print(b is b)  # True
print(b == b)  # True
print(c is c)  # True
print(c == c)  # True

# Pass Statement
num = int(input("Enter a number: "))
if num > 0:
    pass  # Placeholder for future code
else:
    print("You entered a non-positive number.")
print("This is outside the if-else block.")


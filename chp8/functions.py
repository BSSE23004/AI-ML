def avg(numbers=[1,2,3]):
    return sum(numbers) / len(numbers) if numbers else 0

numbers = []

while True:
    entry = input("Enter a number (or 'done' to finish): ")
    if entry.lower() == 'done':
        break
    try:
        number = float(entry)
        numbers.append(number)
    except ValueError:
        print("Invalid input. Please enter a valid number.")

print(f"The average is: {avg(numbers)}")
print(f"The average without giving list is: {avg()} because default list is [1,2,3]")

def celcius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def fahrenheit_to_celcius(fahrenheit):
    return (fahrenheit - 32) * 5/9

temp = input("Enter temperature (e.g., 100C or 212F): ").strip()
if temp[-1].upper() == 'C':
    try:
        celsius = float(temp[:-1])
        fahrenheit = celcius_to_fahrenheit(celsius)
        print(f"{celsius}C is {fahrenheit:.2f}F")
    except ValueError:
        print("Invalid temperature format.")
elif temp[-1].upper() == 'F':
    try:
        fahrenheit = float(temp[:-1])
        celsius = fahrenheit_to_celcius(fahrenheit)
        print(f"{fahrenheit}F is {celsius:.2f}C")
    except ValueError:
        print("Invalid temperature format.")

print("Skipping new line", end='\t')
print("Skipping new line")
print("Skipping space", end=' ')
print("Skipping space")
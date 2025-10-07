def factorial(n):
    """Return n! (n factorial) for non-negative integer n."""
    if n < 0:
        raise ValueError("Negative values are not allowed.")
    if n == 0:
        return 1
    return n * factorial(n - 1)

number = int(input("Enter a non-negative integer to compute its factorial: "))
try:
    print(f"The factorial of {number} is: {factorial(number)}")
except ValueError as e:
    print(e)    

def fibonacci(n):
    """Return the nth Fibonacci number."""
    if n < 0:
        raise ValueError("Negative values are not allowed.")
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)

index = int(input("Enter a non-negative integer to compute its Fibonacci number: "))
try:
    print(f"The {index}th Fibonacci number is: {fibonacci(index)}")
except ValueError as e:
    print(e)




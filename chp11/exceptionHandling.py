#exception handling 
try:
    num1 = int(input("Enter a number: "))
    num2 = int(input("Enter another number: "))
    result = num1 / num2
    print(f"The result of {num1} divided by {num2} is {result}")
except Exception as e:
    print(f"An error occurred: {e}")

#specific exception handling
try:
    num1 = int(input("Enter a number: "))
    num2 = int(input("Enter another number: "))
    result = num1 / num2
    print(f"The result of {num1} divided by {num2} is {result}")
except ValueError:
    print("Invalid input. Please enter numeric values.")
except ZeroDivisionError:
    print("Error: Division by zero is not allowed.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

#using finally
#finally block used in functions 

def dividing_numbers(num1, num2):
    try:
        result = num1 / num2
    except ZeroDivisionError:
        return "Error: Division by zero is not allowed."
    else:
        return result
    finally:
        print("Execution of divide_numbers function completed.")

        
try:
    num1 = int(input("Enter a number: "))
    num2 = int(input("Enter another number: "))
    result = num1 / num2
    print(f"The result of {num1} divided by {num2} is {result}")
except ValueError:
    print("Invalid input. Please enter numeric values.")
except ZeroDivisionError:
    print("Error: Division by zero is not allowed.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    print("Execution completed.")

#raising exceptions
def divide_numbers(num1, num2):
    if num2 == 0:
        raise ValueError("Denominator cannot be zero.")
    return num1 / num2

try:
    num1 = int(input("Enter a number: "))
    num2 = int(input("Enter another number: "))
    result = divide_numbers(num1, num2)
    print(f"The result of {num1} divided by {num2} is {result}")
except ValueError as ve:
    print(f"ValueError: {ve}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")#exception handling 


try:
    num1 = int(input("Enter a number: "))
    num2 = int(input("Enter another number: "))
    result = num1 / num2
    print(f"The result of {num1} divided by {num2} is {result}")
except Exception as e:
    print(f"An error occurred: {e}")    

# with else

try:
    num1 = int(input("Enter a number: "))
    num2 = int(input("Enter another number: "))
    result = num1 / num2
except ValueError:
    print("Invalid input. Please enter numeric values.")
except ZeroDivisionError:
    print("Error: Division by zero is not allowed.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
else:
    print(f"The result of {num1} divided by {num2} is {result}")


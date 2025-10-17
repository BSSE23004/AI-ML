#lambda functions are small anonymous functions defined with the lambda keyword.
#They can take any number of arguments but can only have one expression.
#The expression is evaluated and returned when the function is called.
#Syntax: lambda arguments: expression
#Example 1: A simple lambda function that adds 10 to the input argument
add_10 = lambda x: x + 10
print(add_10(5))  # Output: 15
#Example 2: A lambda function that multiplies two arguments
multiply = lambda x, y: x * y
print(multiply(2, 3))  # Output: 6
#Example 3: Using a lambda function with the map() function to square each number in a list
numbers = [1, 2, 3, 4, 5]
squared_numbers = list(map(lambda x: x ** 2, numbers))
print(squared_numbers)  # Output: [1, 4, 9, 16, 25]
#Example 4: Using a lambda function with the filter() function to filter even numbers from a list
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
print(even_numbers)  # Output: [2, 4]
#Example 5: Using a lambda function with the sorted() function to sort a list of tuples based on the second element
tuples_list = [(1, 'b'), (2, 'a'), (3, 'c')]
sorted_tuples = sorted(tuples_list, key=lambda x: x[1])
print(sorted_tuples)  # Output: [(2, 'a'), (1, 'b'), (3, 'c')]
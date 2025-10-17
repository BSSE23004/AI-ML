#map() function applies a given function to all items in an input list (or any iterable) and returns a map object (which can be converted to a list).
#Syntax: map(function, iterable)
#Example 1: Using map() to double each number in a list
numbers = [1, 2, 3, 4, 5]
doubled_numbers = list(map(lambda x: x * 2, numbers))
print(doubled_numbers)  # Output: [2, 4, 6, 8, 10]

square = lambda x: x ** 2
squared_numbers = list(map(square, numbers))
print(squared_numbers)  # Output: [1, 4, 9, 16, 25]

#filter() function constructs an iterator from elements of an iterable for which a function returns true.
#Syntax: filter(function, iterable)
#Example 2: Using filter() to get only even numbers from a list
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
print(even_numbers)  # Output: [2, 4]

is_odd = lambda x: x % 2 != 0
odd_numbers = list(filter(is_odd, numbers))
print(odd_numbers)  # Output: [1, 3, 5]

#reduce() function from functools module applies a rolling computation to sequential pairs of values in a list.
#Syntax: reduce(function, iterable)
from functools import reduce
#Example 3: Using reduce() to compute the product of all numbers in a list
product = reduce(lambda x, y: x * y, numbers)
print(product)  # Output: 120
sum_function = lambda x, y: x + y
total_sum = reduce(sum_function, numbers)
print(total_sum)  # Output: 15

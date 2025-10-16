#walrus operator
#:=
#assign values to variables as part of a larger expression
#introduced in Python 3.8

#example without walrus operator
my_list = [1, 2, 3, 4, 5]
n = len(my_list)
if n > 3:
    print(f"List is too long ({n} elements, expected <= 3)")
#example with walrus operator
my_list = [1, 2, 3, 4, 5]
if (n := len(my_list)) > 3:
    print(f"List is too long ({n} elements, expected <= 3)")

#operator overloading

class Number:
    def __init__(self, value):
        self.value = value

    def __add__(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value)
        return NotImplemented

    def __repr__(self): # For a clear string representation
        return f"Number({self.value})"
# Example usage:
num1 = Number(10)
num2 = Number(20)
print("num1: ",num1)         # Output: Number(10)
print("num2: ",num2)         # Output: Number(20)
print("num1+num2: ",num1 + num2)  # Output: Number(30)
print("num1-num2: ",num1 - num2)  # Output: Number(-10)
# print("num1*num2: ",num1 * num2)  
# print("num1/num2: ",num1 / num2) 

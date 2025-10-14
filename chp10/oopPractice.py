class TwoDVector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return TwoDVector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return TwoDVector(self.x - other.x, self.y - other.y)

    def __repr__(self):
        return f"TwoDVector({self.x}, {self.y})"
    
class ThreeDVector(TwoDVector):
    def __init__(self, x, y, z):
        super().__init__(x, y)
        self.z = z

    def __add__(self, other):
        return ThreeDVector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return ThreeDVector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __repr__(self):
        return f"ThreeDVector({self.x}, {self.y}, {self.z})"
    
# Example usage:
v1 = TwoDVector(1, 2)
v2 = TwoDVector(3, 4)
print(v1 + v2)  # Output: TwoDVector(4, 6)
print(v1 - v2)  # Output: TwoDVector(-2, -2)
v3 = ThreeDVector(1, 2, 3)
v4 = ThreeDVector(4, 5, 6)
print(v3 + v4)  # Output: ThreeDVector(5, 7
print(v3 - v4)  # Output: ThreeDVector(-3, -3, -3)

class ComplexNumber:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __add__(self, other):
        return ComplexNumber(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other):
        return ComplexNumber(self.real - other.real, self.imag - other.imag)

    def __mul__(self, other):
        real_part = self.real * other.real - self.imag * other.imag
        imag_part = self.real * other.imag + self.imag * other.real
        return ComplexNumber(real_part, imag_part)

    def __truediv__(self, other):
        denom = other.real**2 + other.imag**2
        real_part = (self.real * other.real + self.imag * other.imag) / denom
        imag_part = (self.imag * other.real - self.real * other.imag) / denom
        return ComplexNumber(real_part, imag_part)

    def __repr__(self):
        return f"ComplexNumber({self.real}, {self.imag})"
    
# Example usage:
c1 = ComplexNumber(1, 2)
c2 = ComplexNumber(3, 4)
print(c1 + c2)  # Output: ComplexNumber(4, 6)
print(c1 - c2)  # Output: ComplexNumber(-2, -2)
print(c1 * c2)  # Output: ComplexNumber(-5, 10)
print(c1 / c2)  # Output: ComplexNumber(0.44,

class NDVector:
    def __init__(self, *components):
        self.components = components

    def __add__(self, other):
        return NDVector(*(a + b for a, b in zip(self.components, other.components)))#zip combines two iterables element-wise in this case two tuples

    def __sub__(self, other):
        return NDVector(*(a - b for a, b in zip(self.components, other.components)))

    def __repr__(self):
        return f"NDVector{self.components}"
    
    #6. Write __str__() method to print the vector as follows:
    #7i + 8j +10k
    #Assume vector of dimension 3 for this problem. y

    def __str__(self):
        labels = ['i', 'j', 'k','l','m','n','o','p','q','r','s','t']  # Extend as needed
        terms = [f"{comp}{labels[i]}" for i, comp in enumerate(self.components)]
        return " + ".join(terms)
    
    def __len__(self):
        return len(self.components)
    
# Example usage:
v5 = NDVector(1, 2, 3)
v6 = NDVector(4, 5, 6)
print(v5 + v6)  # Output: NDVector(5, 7, 9)
print(v5 - v6)  # Output: NDVector(-3, -3, -3)
print(v5)       # Output: 1i + 2j + 3k
v7  = NDVector(7, 8, 10,11,12)
print(v7)     # Output: 7i + 8j + 10k + 11l + 12m
print(len(v7))  # Output: 5
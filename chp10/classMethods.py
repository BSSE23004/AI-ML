#classMethod

class Apple:
    color= "Red"  # Class variable
    flavor= "Sweet"  # Class variable
    def __init__(self, color, flavor):
        self.color = color
        self.flavor = flavor

    @classmethod # Class method to display class info
    def print_apple_info(cls):
        # cls.color = "Brown"  # Modifying class variable
        # cls.flavor = "Rotted"  # Modifying class variable
        print(f"Apple class: {cls.__name__}, Color: {cls.color}, Flavor: {cls.flavor}")

    def print_info(self):
        print(f"Apple instance: Color: {self.color}, Flavor: {self.flavor}")

# Example usage
apple = Apple("Yellow", "Sour")
apple.color = "Green" 
apple.flavor = "Tart"
apple.print_apple_info()# Output: Apple class: Apple, Color: Red, Flavor: Sweet because class variables are accessed via cls
apple.print_info() # Output: Apple instance: Color: Green, Flavor: Tart because instance variables are accessed via self
print(Apple.color) # Output: Red because accessing through class
print(apple.color) # Output: Green because accessing through instance
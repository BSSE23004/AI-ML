# Method Resolution Order (MRO) and Diamond Problem Solution
# Using super() with *args and **kwargs for safe multiple inheritance
#super() functions used to access methods from the next class in the MRO

class Employee:
    def __init__(self, name, id, *args, **kwargs):
        # Employee only needs name and id, ignores extra args/kwargs
        print("Employee __init__ called")
        self.name = name
        self.id = id
        self.company = "TechCorp"

    def display(self):
        print(f"Name: {self.name}, ID: {self.id}, Company: {self.company}")

class Programmer(Employee):
    def __init__(self, name, id, language, *args, **kwargs):
        # Pass all args/kwargs up the chain for MRO safety
        super().__init__(name, id, *args, **kwargs)
        self.company = "CodeMasters"
        self.language = language

    def display(self):
        super().display()
        print(f"Programming Language: {self.language}")

class Manager(Employee):
    def __init__(self, name, id, team_size, *args, **kwargs):
        # Pass all args/kwargs up the chain for MRO safety
        super().__init__(name, id, *args, **kwargs)
        self.company = "BizLeaders"
        self.team_size = team_size

    def display(self):
        super().display()
        print(f"Team Size: {self.team_size}")

class TechLead(Programmer, Manager):
    def __init__(self, name, id, language, team_size, *args, **kwargs):
        # Pass all arguments up the chain; MRO will call Programmer then Manager then Employee
        super().__init__(name, id, language, team_size, *args, **kwargs)
        self.company = "TechLeadsInc"
        # team_size is set by Manager, but we can override or use it here if needed

    def display(self):
        super().display()
        print(f"Team Size: {self.team_size}")

# Example usage
print()
lead = TechLead("Diana", 104, "Java", 10)
lead.display()
print("type(lead):", type(lead))
print("MRO:", TechLead.__mro__)
print()
print('''args and kwargs are arguments that can be passed 
      to a function or method to allow for flexible
      and dynamic input handling. They are often used in scenarios
      involving inheritance, especially multiple inheritance,
      to ensure that all necessary parameters are passed up 
      the inheritance chain without explicitly defining them in every subclass.''')
print()
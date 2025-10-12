class Employee:
    def __init__(self, name, id):
        print("Employee __init__ called")
        self.name = name
        self.id = id
        self.company = "TechCorp"

    def display(self):
        print(f"Name: {self.name}, ID: {self.id}, Company: {self.company}")


class Programmer(Employee):
    def __init__(self, name, id, language):
        Employee.__init__(self,name, id)
        self.company = "CodeMasters"
        self.language = language

    def display(self):
        Employee.display(self)
        print(f"Programming Language: {self.language}")

class Manager(Employee):
    def __init__(self, name, id, team_size):
        Employee.__init__(self,name, id)
        self.company = "BizLeaders"
        self.team_size = team_size

    def display(self):
        Employee.display(self)
        print(f"Team Size: {self.team_size}")


# Example usage
print()
emp = Employee("Alice", 101)
emp.display()
print("type(emp):", type(emp))
print()
prog = Programmer("Bob", 102, "Python")
prog.display()
print("type(prog):", type(prog))
print()
mgr = Manager("Charlie", 103, 5)
mgr.display()
print("type(mgr):", type(mgr))
print()

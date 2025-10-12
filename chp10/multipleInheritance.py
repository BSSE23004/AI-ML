#Multiple inheritance
from inheritence import Employee, Programmer, Manager

class TechLead(Programmer, Manager):
    def __init__(self, name, id, language, team_size):
        Programmer.__init__(self, name, id, language)
        Manager.__init__(self, name, id, team_size)
        self.company = "TechLeadsInc"

    def display(self):
        Programmer.display(self)
        print(f"Team Size: {self.team_size}")

# Example usage
print()
lead = TechLead("Diana", 104, "Java", 10)
lead.display()
print("type(lead):", type(lead))
print("MRO:", TechLead.__mro__)
print()
print("Now this is giving diamond problem")
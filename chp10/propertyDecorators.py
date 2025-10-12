#property Decorators are used to make methods behave like attributes

class Employee:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.company = "CodeMasters"

    @property #it means that this method will be accessed like an attribute not a method
    def email(self):
        return f"{self.name.lower()}{self.id}@{self.company.lower()}.com"

    @property #make the following method a property
    def fullname(self):
        return f"{self.name} {self.id}"

    @fullname.setter #setter for the property fullname
    def fullname(self, name_id):#used as for example emp.fullname = "Ahmed 002"
        name, id = name_id.split(" ")
        self.name = name
        self.id = id

    @fullname.deleter# deleter for the property fullname
    def fullname(self):# used as for example del emp.fullname
        print("Delete Name!")
        self.name = None
        self.id = None

emp = Employee("Ibrahim", "001")
print(emp.email)  # Output: 
print(emp.fullname)  # Output: Ibrahim [001]
emp.fullname = "Abdul_Sattar 002"
print(emp.name)  # Output: Ahmed
print(emp.id)    # Output: 002
print(emp.email)  # Output:
del emp.fullname
print(emp.name)  # Output: None
print(emp.id)    # Output: None


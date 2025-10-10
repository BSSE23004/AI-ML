class Employee:

    def __init__(self, name="Sabun", age=19, salary="00", position="developer", department="IT"):#constructor method with parameters
        print("Employee object created with parameters")
        self.name = name
        self.age = age
        self.salary = salary
        self.position = position
        self.department = department

    def getInfo(self):#if dont use self it will not recieve the parameter that is passed when calling the method for example ibrahim.getInfo() changes to Employee.getInfo(ibrahim)
        print(f"Name: {self.name}, Age: {self.age}, Salary: {self.salary}, Position: {self.position}, Department: {self.department}, Car: {getattr(self, 'car', 'N/A')}")#using getattr to avoid error if car attribute is not present because it is not a class attribute
    
    @staticmethod #static method does not take self or cls as first parameter and can be called on the class or instance
    def greet():
        print("Hello, welcome to the company!")


ibrahim = Employee()
ibrahim.car = "Toyota"#adding object attribute
ibrahim.name = "Ibrahim"#object attribute have higher priority than class attribute
print(ibrahim.car,ibrahim.name, ibrahim.age, ibrahim.salary, ibrahim.position, ibrahim.department)
ibrahim.greet()
ibrahim.getInfo()

ali = Employee("Ali", 28, 60000, "Manager", "HR")
ali.getInfo()

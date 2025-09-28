import datetime

a= 'abc'
b= "abc"
c= '''abc'''
d= """abc"""
print(a,b,c,d)
practice = "Hello, World!"
print("practice= ",practice)
print("practice[0]= ",practice[0]) # H
print("practice[7]= ",practice[7]) # W
print("practice[-1]= ",practice[-1]) # !
print("practice[-6]= ",practice[-6]) # W
print("practice[0:5]= ",practice[0:5]) # Hello
print("practice[7:12]= ",practice[7:12]) # World
print("practice[:5]= ",practice[:5]) # Hello
print("practice[7:]= ",practice[7:]) # World!
print("practice[:]= ",practice[:]) # Hello, World!
print("practice[::2]= ",practice[::2]) # Hlo ol!
print("practice[1::2]= ",practice[1::2]) # el,Wrd
print("practice[::-1]= ",practice[::-1]) # !dlroW ,olleH
print("len(practice)= ",len(practice)) # 13
print("practice.lower()= ",practice.lower()) # hello, world!
print("practice.upper()= ",practice.upper()) # HELLO, WORLD!
print("practice.strip()= ",practice.strip()) # Hello, World!
print("practice.replace('H', 'h')= ",practice.replace("H", "h")) # hello, World!
print("practice.split(",")= ",practice.split(",")) # ['Hello', ' World!']
print("'Hello' in practice= ",'Hello' in practice) # True
print("'hello' in practice= ",'hello' in practice) # False
print("'World' not in practice= ",'World' not in practice) # False
print("'world' not in practice= ",'world' not in practice) # True
print("practice +  'How are you?'= ",practice +  "How are you?") # Hello, World! How are you?
print("practice * 2= ",practice * 2) # Hello, World!Hello, World!
print("practice.capitalize()= ",practice.capitalize()) # Hello, world!
print("practice.title()= ",practice.title()) # Hello, World!
print("practice.count('o')= ",practice.count("o")) # 2
print("practice.index('W')= ",practice.index("W")) # 7
print("practice.endswith('!')= ",practice.endswith("!")) # True
print("practice.startswith('H')= ",practice.startswith("H")) # True 
print("Current date and time: ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
doubleSpacedString = "    This  is  a  string  with  double  spaces  and  unstripped.    "
print("Original string: ", doubleSpacedString)
print("After strip(): ", doubleSpacedString.strip())
print("After removing double spaces: ", doubleSpacedString.replace("  ", " "))
print("Original string after replace() and strip() is still same because strings are immutable(unchangeable): ", doubleSpacedString)
replacingString = "Hello, <name> How are you?, We are happy to see you in our office, at date <date>."
name = input("Enter your name: ")
print(f"Hello, {name}!")
print(replacingString.replace("<name>", name).replace("<date>", datetime.datetime.now().strftime("%Y-%m-%d")))

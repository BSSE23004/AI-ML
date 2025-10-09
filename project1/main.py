import random
gameDictionary = {
    "s":1,
    "w":2,
    "g":3
}
computerDictionary = {
    1:"snake",
    2:"water",
    3:"gun"
}
userInput = input("Enter s for snake, w for water and g for gun: ")
myNumber = gameDictionary[userInput]
computerNumber = random.randint(1,3)
print(f"Computer chose {computerDictionary[computerNumber]}")
if myNumber == computerNumber:
    print("It's a tie")
elif (myNumber == 1 and computerNumber == 2) or (myNumber == 2 and computerNumber == 3) or (myNumber == 3 and computerNumber == 1):
    print("You win")
else:
    print("Computer wins")


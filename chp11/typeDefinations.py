from typing import List, Dict, Tuple, Set, Union
a : int = 4

b : float = 5.0

c : str = "hello"

d : bool = True

e : list[int] = [1, 2, 3]

f : dict[str, int] = {"one": 1, "two": 2}

g : tuple[int, str, float] = (1, "two", 3.0)

h : set[int] = {1, 2, 3}

i : Union[int, str] = "could be int or str"

def add(x: int, y: int) -> int:
    return x + y

print(type(add(2, 3)))#type definitions
print(type(a),type(b),type(c),type(d),type(e),type(f),type(g),type(h),type(i))
#specifying the expected data types of variables and function return values
import numpy as np
# print(np.__dict__)

#1D
arr = np.array([1, 2, 3, 4, 5])
print("type(arr)",type(arr))

#2D
arr2D = np.array([[1, 2, 3], [4, 5, 6]])
print("arr2D.shape",arr2D.shape)

#3D
arr3D = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
print("arr3D.shape",arr3D.shape)

#dtype
bool_arr = np.array([-1,0,1,2,3,4,5], dtype='bool')
complex_arr = np.array([-1,0,1,2,3,4,5], dtype='complex')
print(bool_arr.dtype," ", bool_arr)
print(complex_arr.dtype," ", complex_arr)

#arange function pronounced as (a-range) it means array range
arr_range = np.arange(1, 10, 2)# start, stop, step
print("arr_range",arr_range)

#reshape function it means changing the shape of an array
arr_reshaped = np.arange(1, 13).reshape(3, 4) # 3 rows, 4 columns
print("arr_reshaped",arr_reshaped)


#np.ones and np.zeros
#their purpose is to create arrays filled with ones or zeros
#that can be useful in various scenarios such as 
#initializing weights in machine learning models 
#or creating masks for image processing tasks.

ones_array = np.ones((2, 3)) # 2 rows, 3 columns
zeros_array = np.zeros((3, 2)) # 3 rows, 2 columns
print("ones_array:\n", ones_array)
print("zeros_array:\n", zeros_array)

#np.random
#it is commonly used in simulations, random sampling,
#and initializing random weights in machine learning algorithms.
#it give random numbers b/w 0 and 1

random_array = np.random.rand(2, 3) # 2 rows, 3 columns
print("random_array:\n", random_array)


#np.linspace pronounced as (line-space)
#it is often used in numerical simulations, plotting functions,
#and generating evenly spaced values for various applications.
#it gives evenly spaced numbers over a specified interval
linspace_array = np.linspace(0, 1, 5) # 5 evenly spaced numbers between 0 and 1
print("linspace_array:\n", linspace_array)

#np.identity
#it is commonly used in linear algebra computations,
#such as solving systems of linear equations,
#performing matrix operations, and initializing identity matrices for various algorithms.
#it creates an identity matrix
identity_matrix = np.identity(3) # 3x3 identity matrix
print("identity_matrix:\n", identity_matrix)







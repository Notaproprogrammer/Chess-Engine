from Final_Exam import *




bro = greetings("Tanish",19)
print(bro)
import math
dir(math)
pi = math.pi
print(pi)
po=math.pow(10,-1/3)
print(po)
print(math.sqrt(8))
print(math.log(33.115))
import numpy as np 
a = np.array([1,2,3])
b = np.array([2,3,5])
print(a+b)
print(np.inner(a,b))

print(a)
aa = [1,2,4]
print(aa)

for aaaaa in aa: 
    print(aaaaa,end=" \n")
    
table = [1,4,9,16,25,36]
for x in table: 
    print("sqrt(",x,")=",math.sqrt(x))
    
    
    

def factorial(base):
    result = 1 
    for i in range(base):
        result = result*(i+1)
    return result 
def factorial2(num):
    if num == 0: 
        return 1
    else:
        result = 1
        for i in range(1,num+1):
            result = result*i
        return result 
print(factorial2(5))
for i in range(0,1):
    print(i)
    
grades = [90,91,96.97,100]
maxval = grades[0]
for i in grades: 
    if i > maxval: 
        maxval = i
print(maxval)
#without duplicates
for a in range(1,3+1): #first loop
    for b in range(1,a+1): #second loop
        c2 = a**2 + b**2
        print(a, b, c2)
n1 = int(input("how many numbers you want to enter: "))
sum = 0.0
for i in range(n1): 
    x1 = float(input("Enter number: "))
    sum += x1 
result = sum/n1 
print(result)
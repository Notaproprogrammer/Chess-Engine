a = 5
b = 7 
print(f"5 + 7 is {a +b}")
c = 5.677899
print(round(c,3))

print(f"c is {c:.2f}")
d = 9
if type(d) is int:
    print(d)

def hello_world(name): 
    print("hello "+name)
hello_world("tanish")

def greetings(name,age):
    print("hey I am "+name+" and I am "+str(age)+" years old")
greetings("tanish",19)

if __name__ == "__main__":

    def potato(name,age,number,bro,yo):
        n=name
        a=age
        num=number
        b=bro
        y=yo
        print(n,a,num,b,y)
    print("'yo'")
    num1 = 1
    num2 = 5
    maxval = num1 if (num1>num2) else num2*4 - 2
    print(maxval)
    n1 = 7
    n2 = 8 
    n3 = 9
    print(max(n1,n2,n3))
    
    s1 = str([1,2,3])
    print(s1)
    print(False)
    
    def helloooo():
        print ("yo")
    print(helloooo())
class rectangle:
    pass
print(type(rectangle))



i1,i2,i3,i4 = ["yo","gng","was","gud"]
print(i1,i2,i3,i4)



f1 = open("Final_practice.txt","w")
f1.write("yo whats poppin gng\n")
f1.write("second_line\n")
f1.write("third_line\n")
f1.close()

f2=open("Final_practice.txt","r")
list = f2.readlines()
print(list)
for line in f2: 
    print(line.rstrip())
    
    
class Rectangle: 
    w = "Table"
    def __init__(self):
        self.t = 5
    

box1 = Rectangle()
print(box1.w)
Rectangle.w = "In my feelings"
print(box1.w)
list = [5,10,6]
list.remove(6)
print(list)
class Anatomy: 
    cont = 0 
    def __init__(self,a,b):
        self.a = a 
        self.b = b 
        Anatomy.cont += 1 
    def __del__(self):
        Anatomy.cont -= 1 
c1 = Anatomy(5,10)
c2 = Anatomy(10,5)
c3 = Anatomy(6,5)
print(c1.cont)
del c1 
print(c2.cont)
del c3
print(Anatomy.cont)
del c2
print(Anatomy.cont)

class tactical: 
    def __init__(self,x,y,z):
        self.x = x 
        self.y = y 
        self.z = z 
    @staticmethod
    def calculate_product(box):
        z = box.x*box.y*box.z
        return z 
box1 = tactical(5,6,7)
zval = tactical.calculate_product(box1)
print(zval)



class yo: 
    a = 50
    def __init__(self,a):
        self.a = a 

print(yo.a)


##using getter and setter methods and privatizing attributes:
class rectangle: 
    def __init__(self,h,w):
        self.__w = w 
        self.__h = h 
    def get_w(self): 
        return self.__w 
    def get_h(self): 
        return self.__h 
    def set_w(self,w):
        self.__w = w 
    def set_h(self,h):
        self.__h = h 
rect1 = rectangle(5,10)
rect1.set_h(50)
print(rect1.get_h())
def helo():
    return "hello world"
print(helo)
print(helo())
"""class line: 
    def __init__(self, length=0):
        self.set_length(length)
    def set_length(self,length):
        if length > 50: 
            length = 50 
        self.__length = length 
    def get_length(self):
        return self.__length 
    length = property(get_length,set_length)
l1 = line(45)
l1.length = 39
print(l1.get_length())"""

class line: 
    def __init__(self,length,condition=None):
        self.length = length 
        self.condition = condition 
    @property
    def length(self):
        return self.__length 
    @length.setter 
    def length(self,length):
        if length>50: 
            length = 50 
        self.__length = length 
    @property 
    def condition(self):
        return self.__condition 
    @condition.setter
    def condition(self,condition):
        if condition == None: 
            condition = "good"
        self.__condition = condition 

        
l1 = line(41,"alright")
l1.length = 45
l1.condition = "crazy" 
print(l1.length,l1.condition)

def product(*items): # any number of arguments
    result=1 # initialize result
    for item in items: # scan over arguments
        result=result*item
    return result
print(product(7,10,10,10000))
import random 
random.seed(9)
x = random.randint(5,10)
print(x)
y = random.randint(5,10)
print(y)
list = [125,234,221,231,234]
z = random.choice(list)
print(z)
import numpy as np 
a=np.random.seed(10)
h = np.random.random(5)
print(a)
print(h)
def yoyo(): 
    print("yoyo world")
v = yoyo()
f = np.random.uniform(-4.5,6.5,5)
print(f)
lst12=[12,243,56]
c=lst12.pop(0)
print(c)

lst331 = [(12,123),(2331,221),(441,556)]
print(lst331[2][1])

g = "hi my name is tanish".split("t")
for i in g: 
    print(i)
print(g[1])
 
g2 = "Hey my name is tanish and what is poppin Tanish"
s5 = set(g2)
print(s5)

s6 = set()
s6.add("hey")
s6.add("yo")
s6.add("bo")
s6.remove("bo")
print(s6)
print("yo"in s6)

dict = {"f":23,"a":51,"b":32}
for keys,values in dict.items(): 
    print(keys,values)
print(dict.get("f","Couldn't find it"))
dict2 = {"d":1,"c":5,"v":12}
dict.update(dict2)
print(dict)

dict3 = {"x":5,"y":4,"z":2}
dict3.update(dict2)
print(dict3)
dict3.clear() 
print(dict3)
 
 
a={2,5,6}
b={2,6,7}
print(a.union(b))
print(a|b)
print(a&b)
print(a-b)
print(a^b)

listttt5441 = [1,2,3,4,6,7]
for i in range(5,0,-1):
    listttt5441[i]=listttt5441[i-1]
print(listttt5441)
list = ["hey","apple","wasgud"]
list.sort() 
print(list)

list133 = [12,34,55,123,44,1,22,9,12]
#def bubble_sort(list):
    #n = len(list)
    #for i in range(n):
        #for j in range(n-1): 
            #if list[j]>list[j+1]:
                #list[j],list[j+1]=list[j+1],list[j]
        #n = n - 1 
    #return list 
#print(bubble_sort(list133))
#def bb_sort_efficient(list):
    #n = len(list)
    #sorted = True
    #while sorted == True and n>0: 
        #sorted = False 
        #for i in range(n-1):
            #if list[i]>list[i+1]:
                #sorted = True
                #list[i],list[i+1] = list[i+1],list[i]
        #n = n-1 
    #return list 
#print(bb_sort_efficient(list133))

"""def selection_sort(list):
    n = len(list)
    for i in range(n):
        min = i 
        for j in range(i+1,n):
            if list[j]< list[min]: 
                min = j 
        list[i],list[min]= list[min],list[i]
    return list """
            
            
    
   # return list 
#print(selection_sort(list133))
            
def insertion_sort(list):
    n = len(list)
    for i in range(1,n):
        key = list[i]
        j = i-1 
        while j>=0 and list[j]>key: 
            list[j+1]=list[j] #essentially list[i]=list[i-1]
            j = j -1 #swapping till either j>=0 and the value of j-1 > j 
        #when swapping done 
        list[j+1] = key 
    return list 
def insertion_sort2(list): 
    n = len(list)
    for i in range(1,n): 
        temp = list[i]
        j = i 
        while j>=1 and list[j-1]>temp: 
            list[j]=list[j-1]
            j = j-1 
        list[j]=temp 
    return list 
list = [12,45,12,32,12]
list.pop(0)
print(list)

def recsum(n):
    if n == 0: 
        return 0 
    else: 
        return n + recsum(n-1)
print(recsum(10))

def itsum(n):
    if n == 0: 
        return n 
    total = 0
    while n > 0:
        total = total + n 
        n = n -1 
    return total 
print(itsum(7))

def recfact(n):
    if n==0: # base step
       return 1
    else: # recursive step
        return n*recfact(n-1)
    
print(recfact(5))

for i in range(1,2):
    print(i)
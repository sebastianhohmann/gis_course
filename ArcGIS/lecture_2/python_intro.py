# ################################################################################

# # 1) commenting 

# # any statement preceded by a hash '#' symbol is commented out and ignored

# ################################################################################

# # 2) printing

# # print("whatever") to print things (most important debugging tool!)
# print('hello world')

# # we just printed a string
# # we can also print numbers (and other things)

# print(2)

# # strings can be enclosed in single or double quotes

# print("hello world")

# print('')
# print('')

# ################################################################################

# # 3) numbers and arithmetic

# # python recognizes integers and floats
# # they behave differently when we perform operations on them

# # integers
# print(2+2)
# print(5/2)
# # the 5/2 is integer division in python 2.x
# # in python 3, 5//2 is integer division
# # to get the remainder, use %
# print(5%2)

# # floats
# print(5.0/2)
# print(5/2.0)
# print(5.0/2.0)

# # we can perform other operations
# print(5-2) # subtraction
# print(5*2) # multiplication
# print(5**2) # power

# # we can switch between formats 
# print(float(5)/float(2))
# print(int(5.0)/int(2.0))

# # we can concatenate strings by "adding" them
# print("hello")
# print("world")
# print("hello " + "world")
# # or even multiplying them
# print(5*"hello ")

# print('')
# print('')

# ################################################################################

# # 4) variables

# # varialble assignment works with "="
# a = "hello "
# b = "world"
# print(a+b)
# a = 1
# print(a)
# a = a+2
# print(a)
# a += 2
# print(a)

# print('')
# print('')

# ################################################################################

# # 5) Boolean types and logical operations

# a = 1
# print(a == a)
# print(2>1)
# print(2>3)

# a = True
# b = False
# print(a and b)
# print(a or b)
# print(not a)

# print('')
# print('')

# ################################################################################

# # 6) lists and subsetting

# a = ['one', 3, 2, 'five']
# print(a)

# # lists are sub-setable
# print(a[1])
# # what is going on?
# # python uses zero-indexing!
# print(a[0])
# # now that we're at it, strings are also sub-setable
# # to subset a range, specify the position of the first character, 
# # a colon, then one more than the position of the last character
# b = 'hello world'
# print(b[0:2])
# print(b[0:5])


# # we can add to lists
# b = a + [4]
# print(b)
# a.append(4)
# print(a)

# # we can have nested lists
# a.append([1,2,3])
# print(a)

# print('')
# print('')

################################################################################

# 7) flow control

#we can use the range() function to create numerical lists quickly
a = range(10)
print(a)
print(list(a))
for k in a:
	print(k)

k = 0
while k < 10:
	print(k)
	k += 1

print('')

a = ['python', 'is', 'so', 'easy', '!']
for k in a:
	print(k)


print('')

k = 0
while k < 10:
	if k%2 == 0 and k%3 == 0:
		print("%s is divisible by 2 and by 3" % k)
	elif k%2 == 0:
		print("%d is divisible by 2" % k)
	elif k%3 == 0:
		print("%d is divisible by 3" % k)
	else:
		print("%d is neither divisible by 2 nor by 3" % k)
	k += 1

# # note the use of % to insert into strings - this is useful for debugging 
# # and showing the progress of long loops

print('')
print('')

# here is how to do "standard" loops where you refer to an element of a list
# with an index
a2 = ['one', 'two', 'three', 'four', 'five']

for idx, el in enumerate(a):
	print(idx, el, a[idx], a2[idx])

print('')
print('')

# # ################################################################################

# 8) Functions

# functions are defined with the "def" keyword,
# and return values specified after return.

def addtwo(x):
    return x+2

print(addtwo(2))

print('')
print('')

# # # ################################################################################

# # # # 9) Objects, Classses, Attributes and Methods

# # # # everything in python is an "object"
# # # # python is an example of an "objected oriented" programming language
# # # # OOP revolves around things called "classes", which can be thought of as
# # # # blueprints for making particular instances of themselves

# # # # lets see an example (taken from Jeff Knupp:
# # # # https://jeffknupp.com/blog/2014/06/18/improve-your-python-python-classes-and-object-oriented-programming/)

# # # class Customer(object):
# # #     """A customer of ABC Bank with a checking account. Customers have the
# # #     following properties:

# # #     Attributes:
# # #         name: A string representing the customer's name.
# # #         balance: A float tracking the current balance of the customer's account.
# # #     """

# # #     def __init__(self, name, balance=0.0):
# # #         """Return a Customer object whose name is *name* and starting
# # #         balance is *balance*."""
# # #         self.name = name
# # #         self.balance = balance

# # #     def withdraw(self, amount):
# # #         """Return the balance remaining after withdrawing *amount*
# # #         dollars."""
# # #         if amount > self.balance:
# # #             raise RuntimeError('Amount greater than available balance.')
# # #         self.balance -= amount
# # #         return self.balance

# # #     def deposit(self, amount):
# # #         """Return the balance remaining after depositing *amount*
# # #         dollars."""
# # #         self.balance += amount
# # #         return self.balance

# # # # let's create an object: an instance of the Customer class
# # # # which we will call c1
# # # c1 = Customer('John Johnson', 1000)
# # # # we can now print the ATTRIBUTES (the thing the object 'has')
# # # print(c1.name)
# # # print(c1.balance)
# # # # and can call the METHODS (the functions we have defined inside the class using 'def'
# # # # they are the things the object 'can do')
# # # c1.withdraw(500)
# # # print(c1.balance)

# # # # This probably went too fast - it is not a good idea to introduce OOP in the
# # # # first 20 minutes of learning python.
# # # # The reason we do so here is that arcpy, the "module" (see below) containing 
# # # # ArcGIS functionalities for python, makes use of attributes and methods.
# # # # For now, just remember that 

# # # # a) everything is an object
# # # # b) objects can have attributes and methods
# # # # c) you can call them from an object using the dot "." operator

# # # print('')
# # # print('')

# # # # ################################################################################

# # # NOTE: depending on your installation of python, you may need to install some 
# # # of the modules used in this section. Here is walkthrough of how to do this
# # # https://joelmccune.com/installing-python-packages-on-an-arcgis-python-installation/

# # 10) Modules

# # python is great because of modules. 
# # modules are libraries of code that greatly simplify your life
# # arcpy is such a module
# # before delving into arcpy, let's do one example using modules

# # modules are imported with "import modulename"
# # let's import the "os" module which allows you to interface with your operating
# # system

# import os

# # next, lets find the path we are currently working in (where this file is stored)
# # and create a new folder
# pwd = os.path.dirname(os.path.realpath(__file__))
# print(pwd)
# dlpath = pwd + "/newfolder"
# if not os.path.exists(dlpath):
#     os.makedirs(dlpath)

# # import another module: urllib
# # and dowload a file
# import urllib.request
# dlfilepath = dlpath + "//ne_10m_rivers_lake_centerlines.zip" 
# url = "http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/physical/ne_10m_rivers_lake_centerlines.zip"
# print('downloading rivers and lakes...')
# #urllib.request.urlretrieve(url, dlfilepath)

# print('done.')

# # and another module: zipfile, and unzip the file we downloaded
# import zipfile
# # zf = zipfile.ZipFile(dlfilepath, 'r')
# # zf.extractall(dlpath)

# # to remove a module, use 'del' (can also be used on variables, etc.)
# del urllib, zipfile

# # finally, lets remove everything in the directory that is not a zipfile:
# for fn in os.listdir(dlpath):
# 	if ".zip" not in fn:
# 		os.remove(os.path.join(dlpath,fn))

# del os

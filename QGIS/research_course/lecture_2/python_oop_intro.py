class Account(object):

	'''
	Class for bank account objects. Each account object has attributes
		- a name: a string with the name of the customer
		- a balance: a float tracking how much money the customer has in the bank
	We will also write two methods:
		- deposit
		- withdraw
	'''

	def __init__(self, name, balance=0):
		self.name = name
		self.balance = balance

	def deposit(self, amount):
		self.balance += amount

	def withdraw(self, amount):
		if self.balance >= amount:
			self.balance -= amount
		else:
			print('insufficient funds')


if __name__ == '__main__':

	sebs_account = Account('seb', 1000)

	print(sebs_account.name)
	print(sebs_account.balance)

	sebs_account.deposit(1000)
	print(sebs_account.balance)

	sebs_account.withdraw(5000)
	sebs_account.withdraw(500)
	print(sebs_account.balance)

class BankAccount(object):

	def __init__(self, name, balance):
		self.name = name
		self.balance = balance

	def deposit(self, amount):
		self.balance += amount

	def withdraw(self, amount):
		if amount > self.balance:
			print('insufficient funds')
		else:
			self.balance -= amount

sebs_account = BankAccount('seb', 1000)
print(sebs_account)
print(sebs_account.name)
print(sebs_account.balance)
sebs_account.deposit(1000)
print(sebs_account.balance)
sebs_account.withdraw(5000)
sebs_account.withdraw(500)
print(sebs_account.balance)

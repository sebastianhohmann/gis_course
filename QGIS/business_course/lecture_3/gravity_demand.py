import numpy as np
import pandas as pd

class GravityDemand(object):

	def __init__(self, odmat, supplier_names, demand):
		self.odmat = odmat
		self.supplier_names = supplier_names
		self.demand = demand

	def compute_demands(self):
		pullmat = 1 / self.odmat
		totpull = np.ones( (len(self.supplier_names), 1) ).dot( np.sum(pullmat, axis=0).reshape( (1, len(self.demand) ) ) )
		demand_mat = np.ones( (len(self.supplier_names), 1) ).dot( np.array(self.demand).reshape( (1, len(self.demand) ) ) )
		num = demand_mat * pullmat
		df = pd.DataFrame(np.concatenate([np.array(self.supplier_names).reshape((len(self.supplier_names), 1)),
										  np.sum(num / totpull, axis=1).reshape((len(self.supplier_names), 1))], axis=1),
						  columns=['supplier_id', 'demand'])
		return df








import pandas as pd
import numpy as np
import sys

wdir = 'C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/MBA/lecture_3/_workflow_2'
tube_in = '{}/_demand_points_tube.shp'.format(wdir)
tube_csv = '{}/_demand_points_tube.csv'.format(wdir)
shops_in = '{}/shops_nero_candidates.shp'.format(wdir)
odmat_csv = '{}/OD_matrix_tube_nero_candidates.csv'.format(wdir)

sys.path.append(wdir)

from gravity_demand import GravityDemand 

########################################
# Matrix From Layers
########################################
print('computing the origin-destination matrix')
alg_params = {
    'INPUT_END_FIELD': 'shopID',
    'INPUT_END_LAYER': shops_in,
    'INPUT_PROFILE': 7,
    'INPUT_PROVIDER': 0,
    'INPUT_START_FIELD': 'name',
    'INPUT_START_LAYER': tube_in,
    'OUTPUT': 'memory:'
}
odmat = processing.run('ORS Tools:matrix_from_layers', alg_params)['OUTPUT']

########################################
# Converting to pandas
########################################
print('converting-origin-desination matrix to pandas dataframe')
fieldnames = [field.name() for field in odmat.fields()]
tuplist = []
for f in odmat.getFeatures():
    tuplist.append( tuple((f[name] for name in fieldnames)) )
df = pd.DataFrame(tuplist, columns=fieldnames).sort_values(['FROM_ID', 'TO_ID']).reset_index(drop=True)
df.to_csv(odmat_csv, index=False)
df = pd.read_csv(odmat_csv)

########################################
# Getting names of shops, stations and 
# and the full origin-destination matrix
########################################
oddf = df.pivot(index='TO_ID', columns='FROM_ID', values='DIST_KM')
shops = list(oddf.index)
stations = list(oddf.columns)
full_odmat = oddf.values

########################################
# reading in the demands and converting
# to vector
########################################
demands = list(pd.read_csv(tube_csv)
            .sort_values(['name'])
            .reset_index(drop=True)
            .entry.values)

demand_vec = np.array(demands).reshape( (len(stations), 1) )

########################################
# Computing total demands with a loop
########################################
od1 = np.concatenate( (full_odmat[0,:].reshape( (1, len(stations)) ), full_odmat[2:,:]) )
od2 = np.concatenate( (full_odmat[1,:].reshape( (1, len(stations)) ), full_odmat[2:,:]) )
D1 = 0
D2 = 0
for j in range(od1.shape[1]):
    num1 = demand_vec[j] / od1[0,j]
    num2 = demand_vec[j] / od2[0,j]
    denom1 = 0
    denom2 = 0
    for k in range(od1.shape[0]):
        denom1 += 1 / od1[k,j]
        denom2 += 1 / od2[k,j]
    D1 += num1/denom1
    D2 += num2/denom2

print('total demand for shop 1 = {}'.format(D1[0]))
print('total demand for shop 2 = {}'.format(D2[0]))

#####################################################################
#####################################################################
# doing the same the oop-way with vectorized calculations
#####################################################################
#####################################################################

shops1 = [shops[0]] + shops[2:]
gd = GravityDemand(od1, shops1, demands)
demands_vector = gd.compute_demands()
print(demands_vector)

 
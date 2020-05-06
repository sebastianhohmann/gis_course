#########################################################################################
#########################################################################################
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
# print('preliminary setup')
# import sys
# import os

# from qgis.core import (
#     QgsApplication,
#     QgsSpatialIndex,
#     QgsVectorLayer
# )

# from qgis.analysis import QgsNativeAlgorithms

# # See https://gis.stackexchange.com/a/155852/4972 for details about the prefix 
# QgsApplication.setPrefixPath('C:/OSGeo4W64/apps/qgis', True)
# qgs = QgsApplication([], False)
# qgs.initQgis()

# # Add the path to Processing framework  
# sys.path.append('C:/OSGeo4W64/apps/qgis/python/plugins')

# # Import and initialize Processing framework
# import processing
# from processing.core.Processing import Processing
# Processing.initialize()
# QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
#########################################################################################
########################################################################################

################################################################################
# Finding polygon neighbors.
# Based on the script "neighbors.py" by Ujaval Gandhi
# https://www.qgistutorials.com/en/docs/find_neighbor_polygons.html
################################################################################

import csv

# set paths to inputs and outputs
mainpath = "C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_3/gis_data"
outpath = "{}/_output/".format(mainpath)
junkpath = "{}/junk".format(outpath)        

shpin = "{}/dyadcells.shp".format(junkpath)
outcsv = "{}/dyadpolyneighbors.csv".format(outpath)

# Replace the values below with values from your layer.
# For example, if your identifier field is called 'XYZ', then change the line
# below to _NAME_FIELD = 'XYZ'
_NAME_FIELD = 'cid'

# Names of the new neighbors field in the output table
_NEW_NEIGHBORS_FIELD = 'ncid'

layer = QgsVectorLayer(shpin, 'ogr')

# Create a dictionary of all features
feature_dict = {f.id(): f for f in layer.getFeatures()}

# Build a spatial index
index = QgsSpatialIndex()
for f in feature_dict.values():
    index.insertFeature(f)
    
# declaring a list to store all output
outlist = []

print('#################################################')
print('There are {} features to process'.format(len(feature_dict.values())))
print('#################################################')
pten = 0
while 10**pten < (len(feature_dict.values()) // 100):
    pten += 1
k = 0
# Loop through all features and find features that touch each feature
for f in feature_dict.values():
    # print('Working on {}'.format(f[_NAME_FIELD]))
    geom = f.geometry()
    # Find all features that intersect the bounding box of the current feature.
    # We use spatial index to find the features intersecting the bounding box
    # of the current feature. This will narrow down the features that we need
    # to check neighboring features.
    intersecting_ids = index.intersects(geom.boundingBox())
    # Initalize neighbors list and sum
    neighbors = []
    for intersecting_id in intersecting_ids:
        # Look up the feature from the dictionary
        intersecting_f = feature_dict[intersecting_id]

        # For our purpose we consider a feature as 'neighbor' if it touches or
        # intersects a feature. We use the 'disjoint' predicate to satisfy
        # these conditions. So if a feature is not disjoint, it is a neighbor.
        if (f != intersecting_f and
            not intersecting_f.geometry().disjoint(geom)):
            neighbors.append(intersecting_f[_NAME_FIELD])

    nl = [[f[_NAME_FIELD], i] for i in neighbors]
    
    outlist += nl
    k+=1
    if (k % 10**pten == 0):
        print('processed {} features'.format(k))
print('processed all features')

print('writing neighbors to csv')
with open(outcsv, mode = 'w', newline = '') as csv_file:
    fnms = [_NAME_FIELD, _NEW_NEIGHBORS_FIELD]
    writer = csv.DictWriter(csv_file, fieldnames = fnms)
    writer.writeheader()
    for nl in outlist:
        writer.writerow({_NAME_FIELD: nl[0], _NEW_NEIGHBORS_FIELD: nl[1]})

print('DONE!')
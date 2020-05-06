#########################################################################################
#########################################################################################
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
# print('preliminary setup')
# import sys
# import os

# from qgis.core import (
#     QgsApplication
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

# set paths to inputs and outputs
mainpath = "C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_3/gis_data"
outpath = "{}/_output/".format(mainpath)
junkpath = "{}/junk".format(outpath)

coastin = "{}/ne_10m_coastline/ne_10m_coastline.shp".format(mainpath)
dyads = "{}/dyadcells.shp".format(junkpath)
TEMP_xx = "{}/_TEMP_xx.shp".format(junkpath)

coastout = "{}/coast.shp".format(junkpath)
centroidsout = "{}/dyadcentroids.shp".format(junkpath)
distout = "{}/distance.shp".format(junkpath)
nearout = "{}/nearest.shp".format(junkpath)
testout = "{}/testout.shp".format(junkpath)
csvout = "{}/dyadcentroids_closest_coast.csv".format(outpath)

if not os.path.exists(junkpath):
    os.mkdir(junkpath)

#########################################################################
#########################################################################
# centroids and distance to coast
#########################################################################
#########################################################################

#########################################################
# Fix geometries
#########################################################
print('fixing geometries, coast')
fg1_dict = {
    'INPUT': coastin,
    'OUTPUT': 'memory:'
}
fixgeo_coast = processing.run('native:fixgeometries', fg1_dict)['OUTPUT']

#########################################################
# Fix geometries
#########################################################
print('fixing geometries, dyads')
fg2_dict = {
    'INPUT': dyads,
    'OUTPUT': 'memory:'
}
fixgeo_dyads = processing.run('native:fixgeometries', fg2_dict)['OUTPUT']

#########################################################
# Centroids
#########################################################
print('finding vcountry centroids')
cts_dict = {
    'ALL_PARTS': False,
    'INPUT': fixgeo_dyads,
    'OUTPUT': 'memory:'
}
dyads_centroids = processing.run('native:centroids', cts_dict)['OUTPUT']

#########################################################
# Add geometry attributes
#########################################################    
print('adding co-ordinates to centroids')    
aga1_dict = {
    'CALC_METHOD': 0,
    'INPUT': dyads_centroids,
    'OUTPUT': centroidsout
}
processing.run('qgis:exportaddgeometrycolumns', aga1_dict)

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields, coast')
allfields = [field.name() for field in fixgeo_coast.fields()]
keepfields = ['featurecla']
dropfields = [field for field in allfields if field not in keepfields]

df1_dict = {
    'COLUMN': dropfields,
    'INPUT': fixgeo_coast,
    'OUTPUT': coastout
}
processing.run('qgis:deletecolumn', df1_dict)

##################################################################
# v.distance
##################################################################
print('vector distance')
vd_dict = {
    'from': centroidsout,
    'from_type': [0],
    'to': coastout,
    'to_type': [1],
    'dmax': -1,
    'dmin': -1,
    'upload': [1],
    'column': ['xcoord'],
    'to_column': None,
    'from_output': nearout,
    'output': distout,
    'GRASS_REGION_PARAMETER': None,
    'GRASS_SNAP_TOLERANCE_PARAMETER': -1,
    'GRASS_MIN_AREA_PARAMETER': 0.0001,
    'GRASS_OUTPUT_TYPE_PARAMETER': 0,
    'GRASS_VECTOR_DSCO': '',
    'GRASS_VECTOR_LCO': '',
    'GRASS_VECTOR_EXPORT_NOCAT': False
}
processing.run('grass7:v.distance', vd_dict)

#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################

##################################################################
# Field calculator
##################################################################
print('adjusting the "cat" field in the nearest centroids to merge with distance lines')
fc1_dict = {
    'FIELD_LENGTH': 4,
    'FIELD_NAME': 'cat',
    'FIELD_PRECISION': 3,
    'FIELD_TYPE': 1,
    'FORMULA': 'attribute($currentfeature, \'cat\')-1',
    'INPUT': nearout,
    'NEW_FIELD': False,
    'OUTPUT': 'memory:'
}
centroids_fcalc_cellid = processing.run('qgis:fieldcalculator', fc1_dict)['OUTPUT']

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields, nearest (the co-ordinates get screwed up')
df3_dict = {
    'COLUMN': ['xcoord', 'ycoord'],
    'INPUT': centroids_fcalc_cellid,
    'OUTPUT': 'memory:'
}
centroids_cellid_dropfields = processing.run('qgis:deletecolumn', df3_dict)['OUTPUT']

##################################################################
# Join attributes by field value
##################################################################
print('merging the two tables: nearest and centroids: correct co-ordiantes')
jafv1_dict = {
    'DISCARD_NONMATCHING': False,
    'FIELD': 'cid',
    'FIELDS_TO_COPY': None,
    'FIELD_2': 'cid',
    'INPUT': centroidsout,
    'INPUT_2': centroids_cellid_dropfields,
    'METHOD': 1,
    'PREFIX': '',
    'OUTPUT': 'memory:'
}
centroids_cellid_atttabjoined = processing.run('native:joinattributestable', jafv1_dict)['OUTPUT']

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields, nearest and centroids merge')
df4_dict = {
    'COLUMN': ['cid_2'],
    'INPUT': centroids_cellid_atttabjoined,
    'OUTPUT': 'memory:'
}
joined_centroids_dropfieds = processing.run('qgis:deletecolumn', df4_dict)['OUTPUT']

##################################################################
# Join attributes by field value
##################################################################
print('merging the two tables: nearest (adjusted) and distance (this adds vcountries to each centroid-coast line)')
jafv2_dict = {
    'DISCARD_NONMATCHING': False,
    'FIELD': 'cat',
    'FIELDS_TO_COPY': None,
    'FIELD_2': 'cat',
    'INPUT': distout,
    'INPUT_2': joined_centroids_dropfieds,
    'METHOD': 1,
    'PREFIX': '',
    'OUTPUT': 'memory:'
}
distline_centroids_atttabjoined = processing.run('native:joinattributestable', jafv2_dict)['OUTPUT']

##################################################################
# Extract vertices
##################################################################   
print('extracting vertices (get endpoints of each line)')     
ev_dict = {
    'INPUT': distline_centroids_atttabjoined,
    'OUTPUT': 'memory:'
}
distline_centroids_extractverts = processing.run('native:extractvertices', ev_dict)['OUTPUT']

##################################################################
# Extract by attribute
##################################################################
print('keeping only vertices on coast')
eba_dict = {
    'FIELD': 'distance',
    'INPUT': distline_centroids_extractverts,
    'OPERATOR': 2,
    'VALUE': '0',
    'OUTPUT': 'memory:'
}
coast_vertices = processing.run('native:extractbyattribute', eba_dict)['OUTPUT']

##################################################################
# Field calculator
##################################################################
print('creating new field: centroid latitude (keep field names straight)')
fc2_dict = {
    'FIELD_LENGTH': 10,
    'FIELD_NAME': 'cent_lat',
    'FIELD_PRECISION': 10,
    'FIELD_TYPE': 0,
    'FORMULA': 'attribute($currentfeature, \'ycoord\')',
    'INPUT': coast_vertices,
    'NEW_FIELD': False,
    'OUTPUT': 'memory:'
}
coast_vertices_fcalc_centlat = processing.run('qgis:fieldcalculator', fc2_dict)['OUTPUT']

print('creating new field: centroid longitude (keep field names straight)')
fc3_dict = {
    'FIELD_LENGTH': 10,
    'FIELD_NAME': 'cent_lon',
    'FIELD_PRECISION': 10,
    'FIELD_TYPE': 0,
    'FORMULA': 'attribute($currentfeature, \'xcoord\')',
    'INPUT': coast_vertices_fcalc_centlat,
    'NEW_FIELD': False,
    'OUTPUT': 'memory:'
}
coast_vertices_fcalc_centlon = processing.run('qgis:fieldcalculator', fc3_dict)['OUTPUT']

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields')
allfields = [field.name() for field in coast_vertices_fcalc_centlon.fields()]
keepfields = ['cid', 'cent_lat', 'cent_lon']
dropfields = [field for field in allfields if field not in keepfields]

df5_dict = {
    'COLUMN': dropfields,
    'INPUT': coast_vertices_fcalc_centlon,
    'OUTPUT': 'memory:'
}
coast_vertices_dropfields = processing.run('qgis:deletecolumn', df5_dict)['OUTPUT']

#########################################################
# Add geometry attributes
#########################################################    
print('adding co-ordinates to coast points')    
aga2_dict = {
    'CALC_METHOD': 0,
    'INPUT': coast_vertices_dropfields,
    'OUTPUT': 'memory:'
}
coast_vertices_addgeo = processing.run('qgis:exportaddgeometrycolumns', aga2_dict)['OUTPUT']

##################################################################
# Field calculator
##################################################################
print('creating new field: coast latitude (keep field names straight)')
fc4_dict = {
    'FIELD_LENGTH': 10,
    'FIELD_NAME': 'coast_lat',
    'FIELD_PRECISION': 10,
    'FIELD_TYPE': 0,
    'FORMULA': 'attribute($currentfeature, \'ycoord\')',
    'INPUT': coast_vertices_addgeo,
    'NEW_FIELD': False,
    'OUTPUT': 'memory:'
}
coast_vertices_fcalc_coastlat = processing.run('qgis:fieldcalculator', fc4_dict)['OUTPUT']

print('creating new field: coast longitude (keep field names straight)')
fc5_dict = {
    'FIELD_LENGTH': 10,
    'FIELD_NAME': 'coast_lon',
    'FIELD_PRECISION': 10,
    'FIELD_TYPE': 0,
    'FORMULA': 'attribute($currentfeature, \'xcoord\')',
    'INPUT': coast_vertices_fcalc_coastlat,
    'NEW_FIELD': False,
    'OUTPUT': 'memory:'
}
coast_vertices_fcalc_coastlon = processing.run('qgis:fieldcalculator', fc5_dict)['OUTPUT']

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields')

df6_dict = {
    'COLUMN': ['xcoord', 'ycoord'],
    'INPUT': coast_vertices_fcalc_coastlon,
    'OUTPUT': csvout
}
processing.run('qgis:deletecolumn', df6_dict)

print('DONE!')
#########################################################################################
#########################################################################################
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
# print('preliminary setup')
# import sys
# import os

# from qgis.core import (
#     QgsApplication,
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
junkpath = "{}/_output/junk".format(mainpath)

vcountries = "{}/vcountries.shp".format(junkpath)
TEMP_wlds = "{}/_TEMP_wlds.shp".format(junkpath)
TEMP_int = "{}/_TEMP_int.shp".format(junkpath)
TEMP_xx = "{}/_TEMP_xx.shp".format(junkpath)
TEMP_nolangs = "{}/_TEMP_vcnolangs.shp".format(junkpath)
TEMP_withlangs = "{}/_TEMP_vcwithlangs.shp".format(junkpath)

########################################################################
########################################################################
# virtual countries not intersected by languages
########################################################################
########################################################################

#########################################################
# v.overlay
#########################################################
print('removing language polygons from virtual countries')
vov_dict = {
    '-t': False,
    'GRASS_MIN_AREA_PARAMETER': 0.0001,
    'GRASS_OUTPUT_TYPE_PARAMETER': 0,
    'GRASS_REGION_PARAMETER': None,
    'GRASS_SNAP_TOLERANCE_PARAMETER': -1,
    'GRASS_VECTOR_DSCO': '',
    'GRASS_VECTOR_EXPORT_NOCAT': False,
    'GRASS_VECTOR_LCO': '',
    'ainput': vcountries,
    'atype': 0,
    'binput': TEMP_wlds,
    'btype': 0,
    'operator': 2,
    'snap': 0,
    'output': TEMP_xx
}
processing.run('grass7:v.overlay', vov_dict)


#########################################################
# Fix geometries
#########################################################
print('fixing geometries, areas without languages')
fg_dict = {
    'INPUT': TEMP_xx,
    'OUTPUT': 'memory:'
}
fix_geo = processing.run('native:fixgeometries', fg_dict)['OUTPUT']

#########################################################
# Dissolve
#########################################################
print('dissolving by cell-id: areas without languages')
diss_dict = {
    'FIELD': 'a_cid',
    'INPUT': fix_geo,
    'OUTPUT': 'memory:'
}
dissolved = processing.run('native:dissolve', diss_dict)['OUTPUT']

#########################################################
# Field calculator
##########################################################
print('creating new field: copy of cell-id with original name: areas without languages')
fc_dict = {
    'FIELD_LENGTH': 4,
    'FIELD_NAME': 'cid',
    'FIELD_PRECISION': 0,
    'FIELD_TYPE': 1,
    'FORMULA': ' attribute($currentfeature, \'a_cid\')',
    'INPUT': dissolved,
    'NEW_FIELD': True,
    'OUTPUT': 'memory:'
}
field_calc = processing.run('qgis:fieldcalculator', fc_dict)['OUTPUT']


#########################################################
# Drop field(s)
#########################################################
print('dropping fields except the new cell-id: areas without languages')
# getting all attribute fields
allfields = [field.name() for field in field_calc.fields()]
keepfields = ['cid']
dropfields = [field for field in allfields if field not in keepfields]

df_dict = {
   'COLUMN': dropfields,
   'INPUT': field_calc,
   'OUTPUT': TEMP_nolangs
}
processing.run('qgis:deletecolumn', df_dict)


########################################################################
########################################################################
# cleaning up / harmonizing vcs with languages
########################################################################
########################################################################

#########################################################
# Fix geometries
#########################################################
print('fixing geometries, areas with languages')
fg_dict = {
    'INPUT': TEMP_int,
    'OUTPUT': 'memory:'
}
fix_geo = processing.run('native:fixgeometries', fg_dict)['OUTPUT']

#########################################################
# Dissolve
#########################################################
print('dissolving by cell-id: areas with languages')
diss_dict = {
    'FIELD': 'a_cid',
    'INPUT': fix_geo,
    'OUTPUT': 'memory:'
}
dissolved = processing.run('native:dissolve', diss_dict)['OUTPUT']

#########################################################
# Field calculator
##########################################################
print('creating new field: copy of cell-id with original name: areas with languages')
fc_dict = {
    'FIELD_LENGTH': 4,
    'FIELD_NAME': 'cid',
    'FIELD_PRECISION': 0,
    'FIELD_TYPE': 1,
    'FORMULA': ' attribute($currentfeature, \'a_cid\')',
    'INPUT': dissolved,
    'NEW_FIELD': True,
    'OUTPUT': 'memory:'
}
field_calc = processing.run('qgis:fieldcalculator', fc_dict)['OUTPUT']


#########################################################
# Drop field(s)
#########################################################
print('dropping fields except the new cell-id: areas with languages')
# getting all attribute fields
allfields = [field.name() for field in field_calc.fields()]
keepfields = ['cid']
dropfields = [field for field in allfields if field not in keepfields]

df_dict = {
   'COLUMN': dropfields,
   'INPUT': field_calc,
   'OUTPUT': TEMP_withlangs
}
processing.run('qgis:deletecolumn', df_dict)


print('DONE!')
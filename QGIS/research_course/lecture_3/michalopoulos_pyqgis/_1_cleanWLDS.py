#########################################################################################
#########################################################################################
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
# print('preliminary setup')
# import sys
# import os

# from qgis.core import (
#     QgsApplication, 
#     QgsVectorLayer,
#     QgsCoordinateReferenceSystem,
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
#########################################################################################

# set paths to inputs and outputs
mainpath = "C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_3/gis_data"
wldsin = "{}/langa.shp".format(mainpath)
outpath = "{}/_output/".format(mainpath)
wldsout = "{}/wlds_cleaned.shp".format(outpath)

if not os.path.exists(outpath):
	os.mkdir(outpath)

#########################################################
# Fix geometries
#########################################################
print('fixing geometries')
fixgeo_dict = {
    'INPUT': wldsin,
    'OUTPUT': 'memory:'
}
fix_geo = processing.run('native:fixgeometries', fixgeo_dict)['OUTPUT']    

#######################################################################
# Add autoincremental field
#######################################################################
print('adding autoincremental id-field')
aaicf_dict = {
    'FIELD_NAME': 'GID',
    'GROUP_FIELDS': None,
    'INPUT': fix_geo,
    'SORT_ASCENDING': True,
    'SORT_EXPRESSION': '',
    'SORT_NULLS_FIRST': False,
    'START': 1,
    'OUTPUT': 'memory:'
}
autoinc_id = processing.run('native:addautoincrementalfield', aaicf_dict)['OUTPUT'] 

#########################################################
# Field calculator
#########################################################
print('copying language name into a field with shorter attribute name')
fc_dict = {
    'FIELD_LENGTH': 10,
    'FIELD_NAME': 'lnm',
    'FIELD_PRECISION': 0,
    'FIELD_TYPE': 2,
    'FORMULA': ' attribute($currentfeature, \'NAME_PROP\')',
    'INPUT': autoinc_id,
    'NEW_FIELD': True,
    'OUTPUT': 'memory:'
}
field_calc = processing.run('qgis:fieldcalculator', fc_dict)['OUTPUT']

#########################################################
# Drop field(s)
#########################################################
print('dropping fields except GID, ID, lnm')
# getting all attribute fields
allfields = [field.name() for field in field_calc.fields()]
keepfields = ['GID', 'ID', 'lnm']
dropfields = [field for field in allfields if field not in keepfields]

df3_dict = {
   'COLUMN': dropfields,
   'INPUT': field_calc,
   'OUTPUT': wldsout
}
processing.run('qgis:deletecolumn', df3_dict)

print('DONE!')

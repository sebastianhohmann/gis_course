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
#########################################################################################

# set paths to inputs and outputs
mainpath = "C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_3/gis_data"
outpath = "{}/_output/".format(mainpath)
junkpath = "{}/_output/junk".format(mainpath)

dyads = "{}/dyadcells.shp".format(junkpath)
TEMP_wlds = "{}/_TEMP_wlds.shp".format(junkpath)
langs_dyad = "{}/langs_in_dyadcells.csv".format(outpath)        

#######################################################################
# Fix geometries
#######################################################################
print('fixing geometries, dyads')
fg1_dict = {
    'INPUT': dyads,
    'OUTPUT': 'memory:'
}
fixgeo_dyads = processing.run('native:fixgeometries', fg1_dict)['OUTPUT']

print('fixing geometries, wlds')
fg2_dict = {
    'INPUT': TEMP_wlds,
    'OUTPUT': 'memory:'
}
fixgeo_languages = processing.run('native:fixgeometries', fg2_dict)['OUTPUT']

#######################################################################
# Join attributes by location
#######################################################################
print('joining languages to dyad cells')
jal_dict = {
    'DISCARD_NONMATCHING': False,
    'INPUT': fixgeo_dyads,
    'JOIN': fixgeo_languages,
    'JOIN_FIELDS': None,
    'METHOD': 0,
    'PREDICATE': 0,
    'PREFIX': '',
    'OUTPUT': 'memory:'
}
dyads_languages_location_joined = processing.run('qgis:joinattributesbylocation', jal_dict)['OUTPUT']

#########################################################
# Drop field(s)
#########################################################
print('dropping fields except cell-id and GID')
# getting all attribute fields
allfields = [field.name() for field in dyads_languages_location_joined.fields()]
keepfields = ['cid', 'GID']
dropfields = [field for field in allfields if field not in keepfields]

df_dict = {
   'COLUMN': dropfields,
   'INPUT': dyads_languages_location_joined,
   'OUTPUT': langs_dyad
}
processing.run('qgis:deletecolumn', df_dict)

print('DONE!')

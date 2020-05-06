#########################################################################################
#########################################################################################
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
# print('preliminary setup')
# import sys
# import os

# from qgis.core import (
#     QgsApplication,
#     QgsProcessing
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
wlds = "{}/wlds_cleaned.shp".format(outpath)

outcsv = "{}/nlangs_vcountries.csv".format(outpath)
outshp = "{}/wlds_vcountries_int.shp".format(junkpath)

########################################################################
########################################################################
# number of languages per virtual country
########################################################################
########################################################################

#########################################################
# v.clean
#########################################################
print('cleaning the language data')
vc_dict = {
    '-b': False,
    '-c': False,
    'GRASS_MIN_AREA_PARAMETER': 0.0001,
    'GRASS_OUTPUT_TYPE_PARAMETER': 0,
    'GRASS_REGION_PARAMETER': None,
    'GRASS_SNAP_TOLERANCE_PARAMETER': 0.01,
    'GRASS_VECTOR_DSCO': '',
    'GRASS_VECTOR_EXPORT_NOCAT': False,
    'GRASS_VECTOR_LCO': '',
    'input': wlds,
    'threshold': '0.01',
    'tool': 1,
    'type': 4,
    'error': QgsProcessing.TEMPORARY_OUTPUT,
    'output': TEMP_wlds
}
processing.run('grass7:v.clean', vc_dict)


#########################################################
# v.overlay
#########################################################
print('intersecting languages and virtual countries')
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
    'operator': 0,
    'snap': 0,
    'output': TEMP_int
}
processing.run('grass7:v.overlay', vov_dict)

#########################################################
# Fix geometries
#########################################################
print('fixing geometries, intersection')
fg_dict = {
    'INPUT': TEMP_int,
    'OUTPUT': 'memory:'
}
fix_geo = processing.run('native:fixgeometries', fg_dict)['OUTPUT']

#######################################################################
# Dissolve
#######################################################################
# note we are doing this since the unit in wlds is language X country
print('dissolving by proper name')
diss_dict = {
    'FIELD': 'b_lnm;a_cid',
    'INPUT': fix_geo,
    'OUTPUT': 'memory:'
}
#processing.run('native:dissolve', diss_dict)
dissolved_by_propername = processing.run('native:dissolve', diss_dict)['OUTPUT']

#########################################################
# Statistics by categories
#########################################################
print('statistics by categories')        
sbc_dict = {
    'CATEGORIES_FIELD_NAME': 'a_cid',
    'INPUT': dissolved_by_propername,
    'VALUES_FIELD_NAME': None,
    'OUTPUT': outcsv
}
processing.run('qgis:statisticsbycategories', sbc_dict)

print('DONE!')
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
greg = "{}/greg_cleaned.shp".format(outpath)
wlds = "{}/wlds_cleaned.shp".format(outpath)
admin = "{}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp".format(mainpath)
outcsv = "{}/nlangs_country.csv".format(outpath)

#########################################################################
#########################################################################
# 1) number of languages per country
#########################################################################
#########################################################################

#########################################################
# Fix geometries
#########################################################
print('fixing geometries, languages')
fg1_dict = {
    'INPUT': wlds,
    'OUTPUT': 'memory:'
}
fixgeo_wlds = processing.run('native:fixgeometries', fg1_dict)['OUTPUT']

#########################################################
# Fix geometries
#########################################################
print('fixing geometries, countries')
fg2_dict = {
    'INPUT': admin,
    'OUTPUT': 'memory:'
}
fixgeo_countries = processing.run('native:fixgeometries', fg2_dict)['OUTPUT']

#########################################################
# Intersection
#########################################################
print('intersecting')
int_dict = {
    'INPUT': fixgeo_wlds,
    'INPUT_FIELDS': 'GID',
    'OVERLAY': fixgeo_countries,
    'OVERLAY_FIELDS': 'ADMIN',
    'OUTPUT': 'memory:'
}
intersection = processing.run('native:intersection', int_dict)['OUTPUT']

#########################################################
# Statistics by categories
#########################################################
print('statistics by categories')        
sbc_dict = {
    'CATEGORIES_FIELD_NAME': 'ADMIN',
    'INPUT': intersection,
    'VALUES_FIELD_NAME': None,
    'OUTPUT': outcsv
}
processing.run('qgis:statisticsbycategories', sbc_dict)

print('DONE!')
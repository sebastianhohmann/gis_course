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
#     QgsCoordinateReferenceSystem
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
admin_in = "{}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp".format(mainpath)
areas_out = "{}/_output/country_areas.csv".format(mainpath)

# defining world cylindrical equal area SR
crs_wcea = QgsCoordinateReferenceSystem('ESRI:54034')

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields')

# making a layer so we can get all attribute fields
worldlyr = QgsVectorLayer(admin_in, 'ogr')
allfields = [field.name() for field in worldlyr.fields()]
keepfields = ['ne_10m_adm', 'ADMIN', 'ISO_A3']
dropfields = [field for field in allfields if field not in keepfields]

drop_dict = {
    'COLUMN': dropfields,
    'INPUT': admin_in,
    'OUTPUT': 'memory:'
}
countries_drop_fields = processing.run('qgis:deletecolumn', drop_dict)['OUTPUT']

##################################################################
# Reproject layer
##################################################################
print('projecting to world cylindical equal area')
reproj_dict = {
    'INPUT': countries_drop_fields,
    'TARGET_CRS': crs_wcea,
    'OUTPUT': 'memory:'
}
countries_reprojected = processing.run('native:reprojectlayer', reproj_dict)['OUTPUT']

##################################################################
# Fix geometries
##################################################################
print('fixing geometries')
fixgeo_dict = {
    'INPUT': countries_reprojected,
    'OUTPUT': 'memory:'
}
countries_fix_geo = processing.run('native:fixgeometries', fixgeo_dict)['OUTPUT']

##################################################################
# Field calculator, output to csv
##################################################################
print('calculating country areas')
fcalc_dict = {
    'FIELD_LENGTH': 10,
    'FIELD_NAME': 'km2area',
    'FIELD_PRECISION': 3,
    'FIELD_TYPE': 0,
    'FORMULA': 'area($geometry)/1000000',
    'INPUT': countries_fix_geo,
    'NEW_FIELD': True,
    'OUTPUT': areas_out
}
processing.run('qgis:fieldcalculator', fcalc_dict)

print('DONE!')



#########################################################################################
#########################################################################################
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
# print('preliminary setup')
# import sys
# import os

# from qgis.core import (
#     QgsApplication,
#     QgsProcessing,
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
########################################################################################


# set paths to inputs and outputs
mainpath = "C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_3/gis_data"
outpath = "{}/_output/".format(mainpath)
junkpath = "{}/_output/junk".format(mainpath)
areas_out = "{}/vcareas.csv".format(outpath)
water_in = "{}/ne_10m_lakes/ne_10m_lakes.shp".format(mainpath)
TEMP_water = "{}/_TEMP_lakes.shp".format(junkpath)
TEMP_int_water = "{}/_TEMP_int_water.shp".format(junkpath)
water_out = "{}/vcwaterareas.csv".format(outpath)

TEMP_withlangs = "{}/_TEMP_vcwithlangs.shp".format(junkpath)

# defining world cylindrical equal area SR
crs_wcea = QgsCoordinateReferenceSystem('ESRI:54034')

########################################################################
########################################################################
# virtual country areas
########################################################################
########################################################################

##################################################################
# Fix geometries
##################################################################
print('fixing geometries')
fixgeo_dict = {
    'INPUT': TEMP_withlangs,
    'OUTPUT': 'memory:'
}
fix_geo = processing.run('native:fixgeometries', fixgeo_dict)['OUTPUT']

##################################################################
# Reproject layer
##################################################################
print('projecting to world cylindical equal area')
reproj_dict = {
    'INPUT': fix_geo,
    'TARGET_CRS': crs_wcea,
    'OUTPUT': 'memory:'
}
reprojected = processing.run('native:reprojectlayer', reproj_dict)['OUTPUT']

##################################################################
# Field calculator, output to csv
##################################################################
print('calculating virtual country areas')
fcalc_dict = {
    'FIELD_LENGTH': 10,
    'FIELD_NAME': 'km2area',
    'FIELD_PRECISION': 3,
    'FIELD_TYPE': 0,
    'FORMULA': 'area($geometry)/1000000',
    'INPUT': reprojected,
    'NEW_FIELD': True,
    'OUTPUT': areas_out
}
processing.run('qgis:fieldcalculator', fcalc_dict)

########################################################################
########################################################################
# water areas
########################################################################
########################################################################

#########################################################
# v.clean
#########################################################
print('cleaning the lakes data')
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
    'input': water_in,
    'threshold': '0.01',
    'tool': 1,
    'type': 4,
    'error': QgsProcessing.TEMPORARY_OUTPUT,
    'output': TEMP_water
}
processing.run('grass7:v.clean', vc_dict)

#########################################################
# v.overlay
#########################################################
print('intersecting water areas and virtual countries')
vov_dict = {
    '-t': False,
    'GRASS_MIN_AREA_PARAMETER': 0.0001,
    'GRASS_OUTPUT_TYPE_PARAMETER': 0,
    'GRASS_REGION_PARAMETER': None,
    'GRASS_SNAP_TOLERANCE_PARAMETER': -1,
    'GRASS_VECTOR_DSCO': '',
    'GRASS_VECTOR_EXPORT_NOCAT': False,
    'GRASS_VECTOR_LCO': '',
    'ainput': TEMP_withlangs,
    'atype': 0,
    'binput': TEMP_water,
    'btype': 0,
    'operator': 0,
    'snap': 0,
    'output': TEMP_int_water
}
processing.run('grass7:v.overlay', vov_dict)

#########################################################
# Fix geometries
#########################################################
print('fixing geometries, intersection')
fg_dict = {
    'INPUT': TEMP_int_water,
    'OUTPUT': 'memory:'
}
fix_geo = processing.run('native:fixgeometries', fg_dict)['OUTPUT']

#######################################################################
# Dissolve
#######################################################################
print('dissolving by cell-id')
diss_dict = {
    'FIELD': 'a_cid',
    'INPUT': fix_geo,
    'OUTPUT': 'memory:'
}
#processing.run('native:dissolve', diss_dict)
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
field_calc_id = processing.run('qgis:fieldcalculator', fc_dict)['OUTPUT']

##################################################################
# Reproject layer
##################################################################
print('projecting to world cylindical equal area')
reproj_dict = {
    'INPUT': field_calc_id,
    'TARGET_CRS': crs_wcea,
    'OUTPUT': 'memory:'
}
reprojected = processing.run('native:reprojectlayer', reproj_dict)['OUTPUT']

##################################################################
# Field calculator
##################################################################
print('calculating water intersection areas')
fcalc_dict = {
    'FIELD_LENGTH': 10,
    'FIELD_NAME': 'km2warea',
    'FIELD_PRECISION': 3,
    'FIELD_TYPE': 0,
    'FORMULA': 'area($geometry)/1000000',
    'INPUT': reprojected,
    'NEW_FIELD': True,
    'OUTPUT': 'memory:'
}
field_calc_area = processing.run('qgis:fieldcalculator', fcalc_dict)['OUTPUT']

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields: water intersection')
allfields = [field.name() for field in field_calc_area.fields()]
keepfields = ['cid', 'km2warea']
dropfields = [field for field in allfields if field not in keepfields]
df_dict = {
    'COLUMN': dropfields,
    'INPUT': field_calc_area,
    'OUTPUT': water_out
}
processing.run('qgis:deletecolumn', df_dict)

print('DONE!')


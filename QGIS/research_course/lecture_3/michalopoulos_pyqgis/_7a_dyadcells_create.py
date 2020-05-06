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
#########################################################################################

# set paths to inputs and outputs
mainpath = "C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_3/gis_data"
admin_in = "{}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp".format(mainpath)
junkpath = "{}/_output/junk".format(mainpath)
vcout = "{}/dyadcells.shp".format(junkpath)
TEMP_countries = "{}/_TEMP_countries.shp".format(junkpath)
TEMP_grid = "{}/_TEMP_grid.shp".format(junkpath)
TEMP_int = "{}/_TEMP_int.shp".format(junkpath)
TEMP_clean = "{}/_TEMP_clean.shp".format(junkpath)

# defining WGS 84 SR
crs_wgs84 = QgsCoordinateReferenceSystem('EPSG:4326')

if not os.path.exists(junkpath):
    os.mkdir(junkpath)

#######################################################################
# Create grid
#######################################################################
print('creating grid')
cg_dict = {
    'CRS': crs_wgs84,
    'EXTENT': '-180,180,-90,90',
    'HOVERLAY': 0,
    'HSPACING': 0.5,
    'TYPE': 2,
    'VOVERLAY': 0,
    'VSPACING': 0.5,
    'OUTPUT': 'memory:'
}
create_grid = processing.run('qgis:creategrid', cg_dict)['OUTPUT']

#######################################################################
# Add autoincremental field
#######################################################################
print('adding autoincremental id-field')
aaicf1_dict = {
    'FIELD_NAME': 'aux_id',
    'GROUP_FIELDS': None,
    'INPUT': create_grid,
    'SORT_ASCENDING': True,
    'SORT_EXPRESSION': '',
    'SORT_NULLS_FIRST': False,
    'START': 1,
    'OUTPUT': TEMP_grid
}
processing.run('native:addautoincrementalfield', aaicf1_dict)


#########################################################
# v.clean
#########################################################
print('cleaning the country data')
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
    'input': admin_in,
    'threshold': '0.01',
    'tool': 1,
    'type': 4,
    'error': QgsProcessing.TEMPORARY_OUTPUT,
    'output': TEMP_countries
}
processing.run('grass7:v.clean', vc_dict)


#########################################################
# v.overlay
#########################################################
# NOTE: this runs very slowly (on my machine it still computes)
# let me know if you are not able to and want to run the full code
# I can send you the output of this tool
print('intersecting grid and countries')
vov_dict = {
    '-t': False,
    'GRASS_MIN_AREA_PARAMETER': 0.0001,
    'GRASS_OUTPUT_TYPE_PARAMETER': 0,
    'GRASS_REGION_PARAMETER': None,
    'GRASS_SNAP_TOLERANCE_PARAMETER': -1,
    'GRASS_VECTOR_DSCO': '',
    'GRASS_VECTOR_EXPORT_NOCAT': False,
    'GRASS_VECTOR_LCO': '',
    'ainput': TEMP_grid,
    'atype': None,
    'binput': TEMP_countries,
    'btype': None,
    'operator': 0,
    'snap': 0,
    'output': TEMP_int
}
processing.run('grass7:v.overlay', vov_dict)

#######################################################################
# Fix geometries
#######################################################################
print('fixing cleaned up intersection geometries')
fg1_dict = {
    'INPUT': TEMP_int,
    'OUTPUT': 'memory:'
}
fix_geo_int_grid_countries = processing.run('native:fixgeometries', fg1_dict)['OUTPUT']

#########################################################
# Dissolve
#########################################################
print('dissolving by cell-id')
diss1_dict = {
   'FIELD': 'a_aux_id',
   'INPUT': fix_geo_int_grid_countries,
   'OUTPUT': 'memory:'
}
intersection_dissolved_cellid = processing.run('native:dissolve', diss1_dict)['OUTPUT']

#######################################################################
# Add autoincremental field
#######################################################################
print('adding another (final) autoincremental id-field')
aaicf2_dict = {
    'FIELD_NAME': 'cid',
    'GROUP_FIELDS': None,
    'INPUT': intersection_dissolved_cellid,
    'SORT_ASCENDING': True,
    'SORT_EXPRESSION': '',
    'SORT_NULLS_FIRST': False,
    'START': 1,
    'OUTPUT': 'memory:'
}
dissolved_with_cellid = processing.run('native:addautoincrementalfield', aaicf2_dict)['OUTPUT']

#######################################################################
# v.clean
#######################################################################
print('cleaning up the intersection')
vc_dict = {
    '-b': False,
    '-c': False,
    'GRASS_MIN_AREA_PARAMETER': 0.1,
    'GRASS_OUTPUT_TYPE_PARAMETER': 0,
    'GRASS_REGION_PARAMETER': None,
    'GRASS_SNAP_TOLERANCE_PARAMETER': 0.001,
    'GRASS_VECTOR_DSCO': '',
    'GRASS_VECTOR_EXPORT_NOCAT': False,
    'GRASS_VECTOR_LCO': '',
    'input': dissolved_with_cellid,
    'threshold': '',
    'tool': 10,
    'type': None,
    'error': QgsProcessing.TEMPORARY_OUTPUT,
    'output': TEMP_clean
}
processing.run('grass7:v.clean', vc_dict)

#######################################################################
# Fix geometries
#######################################################################
print('fixing cleaned up intersection geometries')
fg2_dict = {
    'INPUT': TEMP_clean,
    'OUTPUT': 'memory:'
}
fixgeo_dissolved_cellid = processing.run('native:fixgeometries', fg2_dict)['OUTPUT']

#######################################################################
# Dissolve
#######################################################################
print('dissolving again by cell-id')
diss2_dict = {
    'FIELD': 'cid',
    'INPUT': fixgeo_dissolved_cellid,
    'OUTPUT': 'memory:'
}
dissolved_with_cellid2 = processing.run('native:dissolve', diss2_dict)['OUTPUT']

#########################################################
# Drop field(s)
#########################################################
print('dropping fields except cell-id')
# getting all attribute fields
allfields = [field.name() for field in dissolved_with_cellid2.fields()]
keepfields = ['cid']
dropfields = [field for field in allfields if field not in keepfields]

df_dict = {
   'COLUMN': dropfields,
   'INPUT': dissolved_with_cellid2,
   'OUTPUT': vcout
}
processing.run('qgis:deletecolumn', df_dict)

print('DONE!')
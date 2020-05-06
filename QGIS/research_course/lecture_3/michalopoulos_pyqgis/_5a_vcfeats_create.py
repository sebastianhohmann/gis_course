#########################################################################################
#########################################################################################
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
# print('preliminary setup')
# import sys
# import os

# from qgis.core import (
#     QgsApplication,
#     QgsCoordinateReferenceSystem,
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
#########################################################################################

# set paths to inputs and outputs
mainpath = "C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_3/gis_data"
admin_in = "{}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp".format(mainpath)
junkpath = "{}/_output/junk".format(mainpath)
vcout = "{}/vcountries.shp".format(junkpath)
cleantemp = "{}/_TEMP_clean.shp".format(junkpath)

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
    'HSPACING': 2.5,
    'TYPE': 2,
    'VOVERLAY': 0,
    'VSPACING': 2.5,
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
    'OUTPUT': 'memory:'
}
grid_with_id = processing.run('native:addautoincrementalfield', aaicf1_dict)['OUTPUT']

#######################################################################
# Fix geometries
#######################################################################
print('fixing country geometries')
fg1_dict = {
    'INPUT': admin_in,
    'OUTPUT': 'memory:'
}
countries_fixgeo = processing.run('native:fixgeometries', fg1_dict)['OUTPUT']

#######################################################################
# Intersection
#######################################################################
print('intersecting countries and grid cells')
int_dict = {
    'INPUT': grid_with_id,
    'INPUT_FIELDS': 'aux_id',
    'OVERLAY': countries_fixgeo,
    'OVERLAY_FIELDS': 'ne_10m_adm',
    'OUTPUT': 'memory:'
}
grid_countries_int = processing.run('native:intersection', int_dict)['OUTPUT']

#########################################################
# Dissolve
#########################################################
print('dissolving by cell-id')
diss1_dict = {
   'FIELD': 'aux_id',
   'INPUT': grid_countries_int,
   'OUTPUT': 'memory:'
}
grid_country_dissolved_by_cell = processing.run('native:dissolve', diss1_dict)['OUTPUT']

#######################################################################
# Add autoincremental field
#######################################################################
print('adding another (final) autoincremental id-field')
aaicf2_dict = {
    'FIELD_NAME': 'cid',
    'GROUP_FIELDS': None,
    'INPUT': grid_country_dissolved_by_cell,
    'SORT_ASCENDING': True,
    'SORT_EXPRESSION': '',
    'SORT_NULLS_FIRST': False,
    'START': 1,
    'OUTPUT': 'memory:'
}
gri_country_dissolved_with_cellid = processing.run('native:addautoincrementalfield', aaicf2_dict)['OUTPUT']

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
    'input': gri_country_dissolved_with_cellid,
    'threshold': '',
    'tool': 10,
    'type': None,
    'error': QgsProcessing.TEMPORARY_OUTPUT,
    'output': cleantemp
}
processing.run('grass7:v.clean', vc_dict)

#######################################################################
# Fix geometries
#######################################################################
print('fixing cleaned up intersection geometries')
fg2_dict = {
    'INPUT': cleantemp,
    'OUTPUT': 'memory:'
}
cleaned_cells_fix_geo = processing.run('native:fixgeometries', fg2_dict)['OUTPUT']

#######################################################################
# Dissolve
#######################################################################
print('dissolving again by cell-id')
diss2_dict = {
    'FIELD': 'cid',
    'INPUT': cleaned_cells_fix_geo,
    'OUTPUT': 'memory:'
}
cleaned_cells_fix_geo_dissolve = processing.run('native:dissolve', diss2_dict)['OUTPUT']

#########################################################
# Drop field(s)
#########################################################
print('dropping fields except cell-id')
# getting all attribute fields
allfields = [field.name() for field in cleaned_cells_fix_geo_dissolve.fields()]
keepfields = ['cid']
dropfields = [field for field in allfields if field not in keepfields]

df_dict = {
   'COLUMN': dropfields,
   'INPUT': cleaned_cells_fix_geo_dissolve,
   'OUTPUT': vcout
}
processing.run('qgis:deletecolumn', df_dict)

print('DONE!')
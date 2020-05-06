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
# NOTE: if you run this script directly from the command line, you can specify relative
# paths, e.g. mainpath = "../gis_data", but this doesnt work with the QGIS python console
mainpath = "C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_2/gis_data"
suitin = "{}/suit/suit/hdr.adf".format(mainpath)
adm2in = "{}/USA_adm_shp/USA_adm2.shp".format(mainpath)
outpath = "{}/_output/counties_agrisuit.csv".format(mainpath)
junkpath = "{}/_output/junk".format(mainpath)
junkfile = "{}/_output/junk/agrisuit.tif".format(mainpath)
if not os.path.exists(mainpath + '/_output'):
    os.mkdir(mainpath + '/_output')
if not os.path.exists(junkpath):
    os.mkdir(junkpath)

# defining WGS 84 SR
crs_wgs84 = QgsCoordinateReferenceSystem("epsg:4326")

##################################################################
# Warp (reproject)
##################################################################
# note: Warp does not accept memory output
# could also specify: 'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
# this will create new files in your OS temp directory (in my (Windows) case:
# /user/Appdata/Local/Temp/processing_somehashkey
print('defining projection for the suitability data')
alg_params = {
    'DATA_TYPE': 0,
    'EXTRA': '',
    'INPUT': suitin,
    'MULTITHREADING': False,
    'NODATA': None,
    'OPTIONS': '',
    'RESAMPLING': 0,
    'SOURCE_CRS': None,
    'TARGET_CRS': crs_wgs84,
    'TARGET_EXTENT': None,
    'TARGET_EXTENT_CRS': None,
    'TARGET_RESOLUTION': None,
    'OUTPUT': junkfile
}
suit_proj = processing.run('gdal:warpreproject', alg_params)['OUTPUT']

##################################################################
# Drop field(s)
##################################################################
print('dropping fields from the county data')
alg_params = {
    'COLUMN': [' ISO','ID_0','NAME_0','ID_1','ID_2',
               'HASC_2','CCN_2','CCA_2','TYPE_2',
               'ENGTYPE_2','NL_NAME_2','VARNAME_2'],
    'INPUT': adm2in,
    'OUTPUT': 'memory:'
}
counties_fields_dropped = processing.run('qgis:deletecolumn', alg_params)['OUTPUT']

###################################################################
# Add autoincremental field
###################################################################
print('adding unique ID to county data')
alg_params = {
    'FIELD_NAME': 'cid',
    'GROUP_FIELDS': [''],
    'INPUT': counties_fields_dropped,
    'SORT_ASCENDING': True,
    'SORT_EXPRESSION': '',
    'SORT_NULLS_FIRST': False,
    'START': 1,
    'OUTPUT': 'memory:'
}
counties_fields_autoid = processing.run('native:addautoincrementalfield', alg_params)['OUTPUT']

###################################################################
# Zonal statistics
###################################################################
print('computing zonal stats')
alg_params = {
    'COLUMN_PREFIX': '_',
    'INPUT_RASTER': suit_proj,
    'INPUT_VECTOR': counties_fields_autoid,
    'RASTER_BAND': 1,
    'STATISTICS': 2
}
processing.run('native:zonalstatistics', alg_params)

###################################################################
# write to CSV
###################################################################
print('outputting the data')

with open(outpath, 'w') as output_file:
    fieldnames = [field.name() for field in counties_fields_autoid.fields()]
    line = ','.join(name for name in fieldnames) + '\n'
    output_file.write(line)
    for f in counties_fields_autoid.getFeatures():
        line = ','.join(str(f[name]) for name in fieldnames) + '\n'
        output_file.write(line)

print('DONE!')

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
suitin = "{}/suit/suit/hdr.adf".format(mainpath)
outpath = "{}/_output/".format(mainpath)
suitout = "{}/landquality.tif".format(outpath)

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
warp_dict = {
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
    'OUTPUT': suitout
}
processing.run('gdal:warpreproject', warp_dict)


##################################################################
# Extract projection
##################################################################
print('extracting the projection for land suitability')
extpr_dict = {
    'INPUT': suitout,
    'PRJ_FILE_CREATE': True
}
processing.run('gdal:extractprojection', extpr_dict)

print('DONE!')
#########################################################################################
#########################################################################################
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
# print('preliminary setup')
# import sys
# import os

# from qgis.core import (
#     QgsApplication,
#     QgsCoordinateReferenceSystem
# )

# from qgis.analysis import QgsNativeAlgorithms

# # See https://gis.stackexchange.com/a/155852/4972 for details about the prefix 
# QgsApplication.setPrefixPath('C:/OSGeo4W64/apps/qgis', True)
# qgs = QgsApplication([], False)
# qgs.initQgis()

# # Add the path to Processing framework  
# sys.path.append('C:/OSGeo4W64/apps/qgis/python/plugins')
# sys.path.append('C:/Users/se.4537/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins')

# # Import and initialize Processing framework
# import processing
# from processing.core.Processing import Processing
# Processing.initialize()
# QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
# from QNEAT3.Qneat3Provider import Qneat3Provider
# QgsApplication.processingRegistry().addProvider(Qneat3Provider())
#########################################################################################
#########################################################################################

# if run this from within QGIS python console, you have append the directory 
# containing geoprocess.py to the sys.path; that is:
import sys
# sys.path.append('/path/to/folder/containing/python_script')
# sys.path.append('C:\\Users\\giorg\\Dropbox (LBS Col_con)\\PoliteconGIS\\LBS_2020\\PhD\\lecture_5\\')
sys.path.append('C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_5')

from geoprocess import GeoProcess

# set paths to inputs and outputs
mainpath = "C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_5\\gis_data"
outpath = "{}/_output".format(mainpath)
junkpath = "{}/junk".format(outpath)

nw70 = "{}/lines_for_network_1870.shp".format(outpath)
nw90 = "{}/lines_for_network_1890.shp".format(outpath)
centroids = "{}/county_centroids.shp".format(outpath)

out70 = "{}/_odmat_1870.csv".format(outpath)



gp = GeoProcess()

###########################################################################
###########################################################################
###########################################################################

print('computing origin-destination matrix, 1870')

odmat70 = gp.odmat_nn(nw70, centroids, 'NHGISNAM', tolerance=10,
                      criterion='speed', speed_field='speed',
                      default_speed=6.966857)

print('output to csv, 1870')

gp.output_csv(odmat70, out70)

print('DONE!')







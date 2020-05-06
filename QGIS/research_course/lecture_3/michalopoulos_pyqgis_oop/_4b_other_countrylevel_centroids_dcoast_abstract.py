#########################################################################################
#########################################################################################
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
print('preliminary setup')
import sys
import os

from qgis.core import (
    QgsApplication
)

from qgis.analysis import QgsNativeAlgorithms

# See https://gis.stackexchange.com/a/155852/4972 for details about the prefix 
QgsApplication.setPrefixPath('C:/OSGeo4W64/apps/qgis', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Add the path to Processing framework  
sys.path.append('C:/OSGeo4W64/apps/qgis/python/plugins')

# Import and initialize Processing framework
import processing
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
#########################################################################################
#########################################################################################

from geoprocess import GeoProcess

# set paths to inputs and outputs
mainpath = "C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_3/gis_data"
outpath = "{}/_output".format(mainpath)
junkpath = "{}/junk".format(outpath)

coastin = "{}/ne_10m_coastline/ne_10m_coastline.shp".format(mainpath)
adminin = "{}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp".format(mainpath)

coastout = "{}/coast.shp".format(junkpath)
centroidsout = "{}/centroids.shp".format(junkpath)
distout = "{}/distance_counties.shp".format(junkpath)
nearout = "{}/nearest_countries.shp".format(junkpath)
csvout = "{}/centroids_closest_coast.csv".format(outpath)
testout = "{}/test_countries.shp".format(junkpath)

if not os.path.exists(junkpath):
    os.mkdir(junkpath)

gp = GeoProcess()

#########################################################################
#########################################################################
# 2) centroids and distance to coast
#########################################################################
#########################################################################

#########################################################
# Fix geometries
#########################################################
print('fixing geometries, countries')
fixgeo_countries = gp.fix_geometry(adminin)  

#########################################################
# Centroids
#########################################################
print('finding country centroids')
country_centroids = gp.centroids(fixgeo_countries)

#########################################################
# Closest coordinates from points to lines
#########################################################
result = gp.find_closest_coordinates_from_points_to_lines(country_centroids, coastin, intermediate_output_folder=junkpath,
											              input_id='ne_10m_adm', input_name='cent', line_name='coast', 	
											              verbose=True, output_object='memory:')

#########################################################
# Centroids
#########################################################
print('writing to csv')
gp.output_csv(result, csvout)

print('DONE!')
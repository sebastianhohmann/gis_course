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
distout = "{}/distance_countries.shp".format(junkpath)
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
print('fixing geometries, coast')
fixgeo_coast = gp.fix_geometry(coastin)  

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
# Add geometry attributes
#########################################################
print('adding co-ordinates to centroids')       
centroids_with_coordinates = gp.add_xycoordinates(country_centroids)

#########################################################
# Drop fields
#########################################################
print('dropping unnecessary fields, coast')
keepfields = ['featurecla']
gp.drop_fields(fixgeo_coast, keep_fields=keepfields, output_object=coastout)

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields, centroids')
keepfields = ['ne_10m_adm', 'ADMIN', 'ISO_A3', 'xcoord', 'ycoord']
gp.drop_fields(centroids_with_coordinates, keep_fields=keepfields, output_object=centroidsout)

##################################################################
# v.distance
##################################################################
print('vector distance: country centroids to coast')
gp.grass_v_distance(centroidsout, coastout, 'xcoord',
                    from_out=nearout, dist_out=distout)

##################################################################
# Adding constant
##################################################################
print('adjusting the "cat" field (subtracting 1) in the nearest centroids to merge with distance lines')
nearest_cat_adjust= gp.add_constant_to_attribute(nearout, 'cat', '-1')

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields, nearest (otherwise get duplicate co-ordinate names)')
dropfields=['xcoord', 'ycoord']
nearest_cat_adjust_dropfields = gp.drop_fields(nearest_cat_adjust, drop_fields=dropfields)

##################################################################
# Join attributes by field value
##################################################################
print('merging the two tables: nearest and centroids: correct co-ordiantes')
centroids_nearest_coast_joined = gp.join_attributes_table(centroidsout, nearest_cat_adjust_dropfields, 'ne_10m_adm')

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields, nearest and centroids merge')
dropfields=['ne_10m_adm_2', 'ADMIN_2', 'ISO_A3_2']
centroids_nearest_coast_joined_dropfields = gp.drop_fields(centroids_nearest_coast_joined, drop_fields=dropfields)

##################################################################
# Join attributes by field value
##################################################################
print('merging the two tables: nearest (adjusted) and distance (this adds countries to each centroid-coast line)')
centroids_nearest_coast_distance_joined = gp.join_attributes_table(distout, centroids_nearest_coast_joined_dropfields, 'cat')

##################################################################
# Extract vertices
##################################################################   
print('extracting vertices (get endpoints of each line)')     
extract_vertices = gp.extract_vertices(centroids_nearest_coast_distance_joined)

##################################################################
# Extract by attribute
##################################################################
print('keeping only vertices on coast')
extract_by_attribute = gp.extract_by_attribute(extract_vertices, 'distance', '>', 0)

#########################################################
# Copy attribute
#########################################################
print('creating new field: centroid latitude (keep field names straight)')
added_field_cent_lat = gp.copy_attribute(extract_by_attribute, 'ycoord', 'cent_lat')

#########################################################
# Copy attribute
#########################################################
print('creating new field: centroid longitude (keep field names straight)')
added_field_cent_lon = gp.copy_attribute(added_field_cent_lat, 'xcoord', 'cent_lon')

#########################################################
# Drop fields
#########################################################
print('dropping unnecessary fields')
keepfields = ['ne_10m_adm', 'ADMIN', 'ISO_A3', 'cent_lat', 'cent_lon']
centroids_lat_lon_drop_fields = gp.drop_fields(added_field_cent_lon, keep_fields=keepfields)

#########################################################
# Add geometry attributes
#########################################################
print('adding co-ordinates to centroids')       
add_geo_coast = gp.add_xycoordinates(centroids_lat_lon_drop_fields)

#########################################################
# Copy attribute
#########################################################
print('creating new field: coast_lon latitude (keep field names straight)')
added_field_coast_lat = gp.copy_attribute(add_geo_coast, 'ycoord', 'coast_lat')

#########################################################
# Copy attribute
#########################################################
print('creating new field: coast longitude (keep field names straight)')
added_field_coast_lon = gp.copy_attribute(added_field_coast_lat, 'xcoord', 'coast_lon')

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields')
dropfields=['xcoord', 'ycoord']
gp.drop_fields(added_field_coast_lon, drop_fields=dropfields, output_object=csvout)

print('DONE!')
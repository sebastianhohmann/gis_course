#########################################################################################
#########################################################################################
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
print('preliminary setup')
import sys
import os

from qgis.core import (
    QgsApplication,
    QgsVectorLayer,
    QgsCoordinateReferenceSystem
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
admin_in = "{}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp".format(mainpath)
areas_out = "{}/_output/country_areas.csv".format(mainpath)

# defining world cylindrical equal area SR
crs_wcea = QgsCoordinateReferenceSystem('ESRI:54034')

gp = GeoProcess()

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields')
keepfields = ['ne_10m_adm', 'ADMIN', 'ISO_A3']
countries_drop_fields = gp.drop_fields(admin_in, keep_fields=keepfields)

##################################################################
# Reproject layer
##################################################################
print('projecting to world cylindical equal area')
countries_reprojected = gp.reproject_layer(countries_drop_fields, 'ESRI:54034')

##################################################################
# Fix geometries
##################################################################
print('fixing geometries')
countries_fix_geo = gp.fix_geometry(countries_reprojected)

##################################################################
# Field calculator, output to csv
##################################################################
print('calculating areas, outputting to csv')
gp.add_area_attribute(countries_fix_geo, 'area', output_object=areas_out)

print('DONE!')



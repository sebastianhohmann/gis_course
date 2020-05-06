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
outpath = "{}/_output/".format(mainpath)
greg = "{}/greg_cleaned.shp".format(outpath)
wlds = "{}/wlds_cleaned.shp".format(outpath)
admin = "{}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp".format(mainpath)
outcsv = "{}/nlangs_country.csv".format(outpath)

gp = GeoProcess()

#########################################################
# Fix geometries
#########################################################
print('fixing geometries, languages')
fixgeo_wlds = gp.fix_geometry(wlds)  

#########################################################
# Fix geometries
#########################################################
print('fixing geometries, countries')
fixgeo_countries = gp.fix_geometry(admin)  

#########################################################
# Intersection
#########################################################
print('intersecting languages and countries')
intersection = gp.intersect_native(fixgeo_wlds, fixgeo_countries,
                                   input_fields_to_keep='GID',
                                   overlay_fields_to_keep='ADMIN')

#########################################################
# Statistics by categories
#########################################################
print('statistics by categories')        
gp.statistics_by_categories(intersection, categories_field_name='ADMIN',
                            values_field_name=None, output_object=outcsv)

print('DONE!')
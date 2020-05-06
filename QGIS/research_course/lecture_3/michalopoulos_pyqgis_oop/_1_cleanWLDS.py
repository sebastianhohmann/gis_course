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

# if run this from within QGIS python console, you have append the directory 
# containing geoprocess.py to the sys.path; that is:
import sys
sys.path.append('/path/to/folder/containing/python_script')

from geoprocess import GeoProcess

# set paths to inputs and outputs
mainpath = "C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_3/gis_data"
wldsin = "{}/langa.shp".format(mainpath)
outpath = "{}/_output/".format(mainpath)
wldsout = "{}/wlds_cleaned.shp".format(outpath)

if not os.path.exists(outpath):
	os.mkdir(outpath)

gp = GeoProcess()

#########################################################
# Fix geometries
#########################################################
print('fixing geometries')
fix_geo = gp.fix_geometry(wldsin)   

#########################################################
# Add autoincremental field
#########################################################
print('adding autoincremental id-field')
autoinc_id = gp.add_autoincremental_id(fix_geo, 'GID')

#########################################################
# Copy attribute
#########################################################
print('copying language name into a field with shorter attribute name')
language_name_copied = gp.copy_attribute(autoinc_id, 'NAME_PROP', 'lnm')

#########################################################
# Drop field(s)
#########################################################
print('dropping fields except GID, ID, lnm')
keepfields = ['GID', 'ID', 'lnm']
gp.drop_fields(language_name_copied, keep_fields=keepfields, output_object=wldsout)

print('DONE!')

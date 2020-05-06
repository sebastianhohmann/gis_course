#########################################################################################
#########################################################################################
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
print('preliminary setup')
import sys

from qgis.core import (
    QgsApplication, 
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
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

# set paths to inputs and outputs
mainpath = "C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_2/gis_data"
worldin = "{}/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp".format(mainpath)
outpath = "{}/_output/country_areas.csv".format(mainpath)

# defining WGS 84 SR and world cylindrical equal area
crs_wcea = QgsCoordinateReferenceSystem('ESRI:54034')

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields')

# making a layer so we can get all attribute fields
worldlyr = QgsVectorLayer(worldin, 'ogr')
allfields = [field.name() for field in worldlyr.fields()]
keepfields = ['ADMIN', 'ISO_A3']
dropfields = [field for field in allfields if field not in keepfields]

drop_dict = {
 'COLUMN': dropfields,
 'INPUT': worldin,
 'OUTPUT': 'memory:'
}
df = processing.run('qgis:deletecolumn', drop_dict)['OUTPUT']

##################################################################
# Reproject layer
##################################################################
print('projecting to world cylindical equal area')
reproj_dict = {
 'INPUT': df,
 'OPERATION': '',
 'TARGET_CRS': crs_wcea,
 'OUTPUT': 'memory:'
}
reproj = processing.run('native:reprojectlayer', reproj_dict)['OUTPUT']

##################################################################
# Fix geometries
##################################################################
print('fixing geometries')
fixgeo_dict = {
 'INPUT': reproj,
 'OUTPUT': 'memory:'
}
fixgeo = processing.run('native:fixgeometries', fixgeo_dict)['OUTPUT']

##################################################################
# Field calculator
##################################################################
print('calculating country areas')
fcalc_dict = {
 'FIELD_LENGTH': 10,
 'FIELD_NAME': 'km2area',
 'FIELD_PRECISION': 3,
 'FIELD_TYPE': 0,
 'FORMULA': 'area($geometry)/1000000',
 'INPUT': fixgeo,
 'NEW_FIELD': True,
 'OUTPUT': 'memory:'
}
fieldcalc = processing.run('qgis:fieldcalculator', fcalc_dict)['OUTPUT']

###################################################################
# write to CSV
###################################################################
print('outputting the data')

with open(outpath, 'w') as output_file:
    fieldnames = [field.name() for field in fieldcalc.fields()]
    line = ','.join(name for name in fieldnames) + '\n'
    output_file.write(line)
    for f in fieldcalc.getFeatures():
        line = ','.join(str(f[name]) for name in fieldnames) + '\n'
        output_file.write(line)

print('DONE!')


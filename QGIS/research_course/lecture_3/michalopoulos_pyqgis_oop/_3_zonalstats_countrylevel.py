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

elevation = "D:/backup_school/Research/IPUMS/_GEO/elrug/elevation/alt.bil"
tpbasepath = "D:/backup_school/Research/worldclim/World"
tpath = tpbasepath + "/temperature"
ppath = tpbasepath + "/precipitation"
temp = tpath + "/TOTtmean6090.tif"
prec = ppath + "/TOTprec6090.tif"
landqual = outpath + "/landquality.tif"
popd1500 = mainpath + "/HYDE/1500ad_pop/popd_1500AD.asc"
popd1990 = mainpath + "/HYDE/1990ad_pop/popd_1990AD.asc"
popd2000 = mainpath + "/HYDE/2000ad_pop/popd_2000AD.asc"
countries = mainpath + "/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"

outcsv = "{}/country_level_zs.csv".format(outpath)

RASTS = [elevation, temp, prec, landqual, popd1500, popd1990, popd2000]
PREFS = ['elev_', 'temp_', 'prec_', 'lqua_', 'pd15_', 'pd19_', 'pd20_']

# elevation, temperature, precipitation are very large raster files,
# take a long time to process. we will see faster processing methods at the end. 
# the code will still run (if you are patient)!
# for now, do only the last four rasters
RASTS = RASTS[3:]
PREFS = PREFS[3:]

gp = GeoProcess()

#########################################################
# Fix geometries
#########################################################
print('fixing geometries')
fix_geo = gp.fix_geometry(countries)   

#########################################################
# Drop fields
#########################################################
print('dropping fields except ADMIN, ISO_A3')
keepfields = ['ADMIN', 'ISO_A3']
drop_fields = gp.drop_fields(fix_geo, keep_fields=keepfields)

#########################################################
# Zonal statistics
#########################################################               
gp.zonal_statistics_as_csv(drop_fields, RASTS, PREFS, ['mean'], outcsv)

print('DONE!')
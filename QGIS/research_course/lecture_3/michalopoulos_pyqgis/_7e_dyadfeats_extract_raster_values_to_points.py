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
#     QgsVectorFileWriter,
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
########################################################################################

# set paths to inputs and outputs
mainpath = "C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_3/gis_data"

outpath = "{}/_output/".format(mainpath)
junkpath = "{}/junk".format(outpath)        

cents = "{}/dyadcentroids.shp".format(junkpath)

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

RASTS = [elevation, temp, prec, landqual, popd1500, popd1990, popd2000]
PREFS = ['elev_', 'temp_', 'prec_', 'lqua_', 'pd15_', 'pd19_', 'pd20_']

# elevation, temperature, precipitation are very large raster files,
# take a long time to process. we will see faster processing methods at the end. 
# the code will still run (if you are patient)!
# for now, do only the last four rasters
RASTS = RASTS[3:]
PREFS = PREFS[3:]
# RASTS = [RASTS[3]]
# PREFS = [PREFS[3]]

##################################################################
# Drop field(s)
##################################################################
print('dropping unnecessary fields')
drop_dict = {
    'COLUMN': ['xcoord', 'ycoord'],
    'INPUT': cents,
    'OUTPUT': 'memory:'
}
dropfields_cents = processing.run('qgis:deletecolumn', drop_dict)['OUTPUT']

# here we loop over the rasters
for idx, rast in enumerate(RASTS):

	pref = PREFS[idx]

	# rlayer = QgsRasterLayer(rast, "rasterlayer", "gdal")
	outcsv = "{}/dyads_evtp_{}.csv".format(outpath, pref[:-1])
	auxout = "{}/_TEMP_auxevtp.shp".format(junkpath)

	###################################################################
	# Add raster values to points
	###################################################################
	print('extracting raster values to points {}'.format(pref))
	rvtp_dict = {
	    'GRIDS': rast,
	    'RESAMPLING': 0,
	    'SHAPES': dropfields_cents,
	    'RESULT': auxout
	}
	processing.run('saga:addrastervaluestopoints', rvtp_dict)


	###################################################################
	# write to CSV
	###################################################################
	print('writing to csv {}'.format(pref))

	outlyr = QgsVectorLayer(auxout, 'ogr')
	with open(outcsv, 'w') as output_file:
	    fieldnames = [field.name() for field in outlyr.fields()]
	    line = ','.join(name for name in fieldnames) + '\n'
	    output_file.write(line)
	    for f in outlyr.getFeatures():
	        line = ','.join(str(f[name]) for name in fieldnames) + '\n'
	        output_file.write(line)

                        
print('DONE!')



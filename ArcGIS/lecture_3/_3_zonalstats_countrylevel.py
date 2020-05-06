# Import arcpy module
## Read the ArcGIS object ###
print "Launching ArcGIS 10.6.1"
import arcpy, os

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

maindir = "C:/Users/se.4537/Dropbox/PoliteconGIS/Lecture 3"
GISdir = maindir + "/GIS data"
outdir = "C:/Users/se.4537/Dropbox/PoliteconGIS/Bonn_2019/Lecture 3/Michalopoulos_2012/_output"

#### inputs ####
elevation = "D:/backup_school/Research/IPUMS/_GEO/elrug/elevation/alt.bil"
tpbasepath = "D:/backup_school/Research/worldclim/World"
tpath = tpbasepath + "/temperature"
ppath = tpbasepath + "/precipitation"
temp = tpath + "/TOTtmean6090.tif"
prec = ppath + "/TOTprec6090.tif"
landqual = maindir + "/results/landquality.tif"
popd1500 = GISdir + "/HYDE/1500ad_pop/popd_1500AD.asc"
popd1990 = GISdir + "/HYDE/1990ad_pop/popd_1990AD.asc"
popd2000 = GISdir + "/HYDE/2000ad_pop/popd_2000AD.asc"
countries = GISdir + "/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"

##### intermediates #####
_temp_elev = outdir + "/_temp_elev.dbf"
_temp_temp = outdir + "/_temp_temp.dbf"
_temp_prec = outdir + "/_temp_prec.dbf"
_temp_suit = outdir + "/_temp_suit.dbf"
_temp_pd15 = outdir + "/_temp_pd1500.dbf"
_temp_pd90 = outdir + "/_temp_pd1990.dbf"
_temp_pd00 = outdir + "/_temp_pd2000.dbf"

#### outputs #####
zs_elev = "zs_elev.txt"
zs_temp = "zs_temp.txt"
zs_prec = "zs_prec.txt"
zs_suit = "zs_suit.txt"
zs_pd15 = "zs_pd15.txt"
zs_pd90 = "zs_pd90.txt"
zs_pd00 = "zs_pd00.txt"


### GEOPROCESSING ###
RASTS = [elevation, temp, prec, landqual, popd1500, popd1990, popd2000]
DBFS = [_temp_elev, _temp_temp, _temp_prec, _temp_suit, _temp_pd15, _temp_pd90, _temp_pd00]
TXTS = [zs_elev, zs_temp, zs_prec, zs_suit, zs_pd15, zs_pd90, zs_pd00]

RASTS = RASTS[3:]
DBFS = DBFS[3:]
TXTS = TXTS[3:]

for i, rast in enumerate(RASTS):
	dbf = DBFS[i]
	txt = TXTS[i]
	rastnm = txt[-8:-4]
	
	print "computing zonal statistics as table for %s" % rastnm
	# Process: Zonal Statistics as Table
	arcpy.gp.ZonalStatisticsAsTable_sa(countries, "ne_10m_adm", rast, dbf, "DATA", "ALL")

	fms = arcpy.FieldMappings()
	fms.addTable(dbf)
	print "converting table to txt"
	# Process: Table to Table
	arcpy.TableToTable_conversion(dbf, outdir, txt, "", fms, "")

	del fms

# Final cleanup
print "deleting unnecessary intermediate files"
for fn in os.listdir(outdir):
    if "_temp_" in fn:
        fpath = outdir + "/" + fn
        os.remove(fpath)


print "Closing ArcGIS 10.6.1"
del arcpy, os

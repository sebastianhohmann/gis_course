# Import arcpy module
## Read the ArcGIS object ###
print "Launching ArcGIS 10.6.1"
import arcpy, os

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

maindir = "C:/Users/se.4537/Dropbox/PoliteconGIS/Lecture 3"
GISdir = maindir + "/GIS data"
outdir = "C:/Users/se.4537/Dropbox/PoliteconGIS/Montreal/Lecture 5/Michalopoulos_2012/_output"

# define WGS 1984 spatial reference
# and world cylindrical equal area spatial reference
wgs84 = arcpy.SpatialReference(4326)
wcea = arcpy.SpatialReference(54034)

#### inputs ####
# inputs: virtual countries and unmatched territories
vcountry = outdir + "/_TEMP_vcountry.shp"
unmatched = outdir + "/_TEMP_unmatched.shp"
# inputs: raster data
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
popcount = GISdir + "/gl_gpwv3_pcount_95_bil_25/glp95g.bil"

##### intermediates #####
_TEMP_elev = outdir + "/_TEMP_elev.dbf"
_TEMP_temp = outdir + "/_TEMP_temp.dbf"
_TEMP_prec = outdir + "/_TEMP_prec.dbf"
_TEMP_suit = outdir + "/_TEMP_suit.dbf"
_TEMP_pd15 = outdir + "/_TEMP_pd1500.dbf"
_TEMP_pd90 = outdir + "/_TEMP_pd1990.dbf"
_TEMP_pd00 = outdir + "/_TEMP_pd2000.dbf"
_TEMP_pc95 = outdir + "/_TEMP_pc1995.dbf"

_TEMP_elev_um = outdir + "/_TEMP_elev_um.dbf"
_TEMP_temp_um = outdir + "/_TEMP_temp_um.dbf"
_TEMP_prec_um = outdir + "/_TEMP_prec_um.dbf"
_TEMP_suit_um = outdir + "/_TEMP_suit_um.dbf"
_TEMP_pd15_um = outdir + "/_TEMP_pd1500_um.dbf"
_TEMP_pd90_um = outdir + "/_TEMP_pd1990_um.dbf"
_TEMP_pd00_um = outdir + "/_TEMP_pd2000_um.dbf"
_TEMP_pc95_um = outdir + "/_TEMP_pc1995_um.dbf"

#### outputs #####
zs_elev = "VC_zs_elev.txt"
zs_temp = "VC_zs_temp.txt"
zs_prec = "VC_zs_prec.txt"
zs_suit = "VC_zs_suit.txt"
zs_pd15 = "VC_zs_pd15.txt"
zs_pd90 = "VC_zs_pd90.txt"
zs_pd00 = "VC_zs_pd00.txt"
zs_pc95 = "VC_zs_pc95.txt"

um_zs_elev = "VCum_zs_elev.txt"
um_zs_temp = "VCum_zs_temp.txt"
um_zs_prec = "VCum_zs_prec.txt"
um_zs_suit = "VCum_zs_suit.txt"
um_zs_pd15 = "VCum_zs_pd15.txt"
um_zs_pd90 = "VCum_zs_pd90.txt"
um_zs_pd00 = "VCum_zs_pd00.txt"
um_zs_pc95 = "VCum_zs_pc95.txt"

#######################################################################
#######################################################################
#######################################################################

### GEOPROCESSING ###
RASTS = [elevation, temp, prec, landqual, popd1500, popd1990, popd2000, popcount]
DBFS = [_TEMP_elev, _TEMP_temp, _TEMP_prec, _TEMP_suit, _TEMP_pd15, _TEMP_pd90, _TEMP_pd00, _TEMP_pc95]
DBFSUM = [_TEMP_elev_um, _TEMP_temp_um, _TEMP_prec_um, _TEMP_suit_um, _TEMP_pd15_um, _TEMP_pd90_um, _TEMP_pd00_um, _TEMP_pc95_um]
TXTS = [zs_elev, zs_temp, zs_prec, zs_suit, zs_pd15, zs_pd90, zs_pd00, zs_pc95]
TXTSUM  = [um_zs_elev, um_zs_temp, um_zs_prec, um_zs_suit, um_zs_pd15, um_zs_pd90, um_zs_pd00, um_zs_pc95]

for i, rast in enumerate(RASTS):
	dbf = DBFS[i]
	dbfum = DBFSUM[i]
	txt = TXTS[i]
	txtum = TXTSUM[i]
	rastnm = txt[-8:-4]
	
	print "computing virtual country zonal statistics as table for %s" % rastnm
	# Process: Zonal Statistics as Table
	arcpy.gp.ZonalStatisticsAsTable_sa(vcountry, "cell25_id", rast, dbf, "DATA", "ALL")

	fms = arcpy.FieldMappings()
	fms.addTable(dbf)
	print "converting table to txt"
	# Process: Table to Table
	arcpy.TableToTable_conversion(dbf, outdir, txt, "", fms, "")
	del fms

	print "computing unmatched zonal statistics as table for %s" % rastnm
	# Process: Zonal Statistics as Table
	arcpy.gp.ZonalStatisticsAsTable_sa(unmatched, "cell25_id", rast, dbfum, "DATA", "ALL")

	fms = arcpy.FieldMappings()
	fms.addTable(dbf)
	print "converting table to txt"
	# Process: Table to Table
	arcpy.TableToTable_conversion(dbfum, outdir, txtum, "", fms, "")
	del fms	

### END OF GEOPROCESSING ###

# Final cleanup
print "deleting unnecessary intermediate files"
for fn in os.listdir(outdir):
    if "_TEMP_" in fn or ".txt.xml" in fn:
        fpath = outdir + "/" + fn
        os.remove(fpath)


fpath = outdir + "/schema.ini"
os.remove(fpath)


print "Closing ArcGIS 10.6.1"
del arcpy, os

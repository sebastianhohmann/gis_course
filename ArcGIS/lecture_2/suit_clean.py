# import the arcpy module
print "Launching ArcGIS 10.6"
import arcpy

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

# declaring folders, argis workspace environment and allowing for file overwrite
maindir = "C:/Users/se.4537/Dropbox/PoliteconGIS/Bonn_2019/Lecture 2"
GISdir = maindir + "/GIS data"
outdir = GISdir + "/_output"
arcpy.env.workspace = outdir 
arcpy.env.overwriteOutput = True

# define WGS 1984 spatial reference
wgs84 = arcpy.SpatialReference(4326)

# Local variables:
suitin = GISdir + "/suit/suit"
us_adm2 = GISdir + "/USA_adm_shp/USA_adm2.shp"


agrisuit = "agrisuit.tif"
agrisuit_rs = "agrisuitrs.tif"
counties = "counties.shp"
ctysuit_dbf = "county_suit.dbf"
ctysuit_csv = "county_suit.csv"

# Process: Copy Raster
print "making a backup copy of the agricultural suitability raster"
arcpy.CopyRaster_management(suitin, agrisuit, "", "", "-3.402823e+038", "NONE", "NONE", "", "NONE", "NONE", "TIFF", "NONE")

# Process: Define Projection
print "defining the projection of the agricultural suitability raster to WGS 1984"
arcpy.DefineProjection_management(agrisuit, wgs84)

# Process: Resample
print "resampling the agricultural suitability raster to finer resolution"
arcpy.Resample_management(agrisuit, agrisuit_rs, "2 2", "NEAREST")

# Process: Copy Features
print "making a backup copy of the US counties shapefile"
arcpy.CopyFeatures_management(us_adm2, counties, "", "0", "0", "0")

# Process: Delete Field
print "deleting unnecessary fields from the counties copy"
arcpy.DeleteField_management(counties, "ID_0;ISO;NAME_0;ID_1;ID_2;HASC_2;CCN_2;CCA_2;TYPE_2;ENGTYPE_2;NL_NAME_2;VARNAME_2")

# Process: Add Field
print "creating a unique id field for us counties"
arcpy.AddField_management(counties, "county_id", "SHORT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field
print "populating the county id field"
arcpy.CalculateField_management(counties, "county_id", "!FID!+1", "PYTHON_9.3", "")

# Process: Zonal Statistics as Table
print "computing zonal statistics as table"
arcpy.gp.ZonalStatisticsAsTable_sa(counties, "county_id", agrisuit_rs, ctysuit_dbf, "DATA", "MEAN")


fms = arcpy.FieldMappings()
fms.addTable(ctysuit_dbf)
print "converting table to csv"
# Process: Table to Table
arcpy.TableToTable_conversion(ctysuit_dbf, outdir, ctysuit_csv, "", fms, "")
del fms	

print "exiting ArcGIS"
del arcpy

import os
for fn in os.listdir(outdir):
	if '.csv' not in fn:
		try:
			os.remove(os.path.join(outdir, fn))
		except:
			continue
del os

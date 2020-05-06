print "Launching ArcGIS 10.6.1"
import arcpy

maindir = "C:/Users/se.4537/Dropbox/PoliteconGIS/Lecture 3"
GISdir = maindir + "/GIS data"
outdir = "C:/Users/se.4537/Dropbox/PoliteconGIS/Bonn_2019/Lecture 3/Michalopoulos_2012/_output"
arcpy.env.workspace = outdir 
arcpy.env.overwriteOutput = True

### Local variables ###
suit = GISdir + "/suit/suit"
landqual = "landquality.tif"

# define WGS 1984 spatial reference
wgs84 = arcpy.SpatialReference(4326)

# Process: Copy Raster
print "Copying raster"
arcpy.CopyRaster_management(suit, landqual, "", "", "-3,402823e+038", "NONE", "NONE", "", "NONE", "NONE")

# Process: Define Projection
print "Assigning WGS 1984"
arcpy.DefineProjection_management(landqual, wgs84)


### Release the memory ###
print "Closing ArcGIS 10.6.1"
del arcpy

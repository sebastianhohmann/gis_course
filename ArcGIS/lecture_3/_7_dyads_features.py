# Import arcpy module
## Read the ArcGIS object ###
print "Launching ArcGIS 10.6.1"
import arcpy, os

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

maindir = "C:/Users/se.4537/Dropbox/PoliteconGIS/Lecture 3"
GISdir = maindir + "/GIS data"
outdir = "C:/Users/se.4537/Dropbox/PoliteconGIS/Montreal/Lecture 5/Michalopoulos_2012/_output"
arcpy.env.workspace = outdir 
arcpy.env.overwriteOutput = True

# define WGS 1984 spatial reference
# and world cylindrical equal area spatial reference
wgs84 = arcpy.SpatialReference(4326)
wcea = arcpy.SpatialReference(54034)


#### inputs ####
countries = GISdir + "/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
coast = GISdir + "/ne_10m_coastline/ne_10m_coastline.shp"
lakes = GISdir + "/ne_10m_lakes/ne_10m_lakes.shp"
GREG = GISdir + "/GREG.shp"
# inputs: raster data
elevation = "D:/backup_school/Research/IPUMS/_GEO/elrug/elevation/alt.bil"
tpbasepath = "D:/backup_school/Research/worldclim/World"
tpath = tpbasepath + "/temperature"
ppath = tpbasepath + "/precipitation"
temp = tpath + "/TOTtmean6090.tif"
prec = ppath + "/TOTprec6090.tif"
landqual = maindir + "/results/landquality.tif"
popd1990 = GISdir + "/HYDE/1990ad_pop/popd_1990AD.asc"
popd2000 = GISdir + "/HYDE/2000ad_pop/popd_2000AD.asc"
popcount = GISdir + "/gl_gpwv3_pcount_95_bil_25/glp95g.bil"


# intermediates
fishnet05 = "_TEMP1_fishnet05.shp"
cell05 = "_TEMP1_cell05.shp"
cell05cyl = "_TEMP1_cell05cyl.shp"
cell05cent = "_TEMP1_cell05cent.shp"
cell05cent2 = "_TEMP1_cell05cent2.shp"
celllakes = "_TEMP1_cell_lakes.shp"
celllakescyl = "_TEMP1_cell_lakescyl.shp"
cell05act = "_TEMP1_cell05_act.shp"
cellneighbors = "_TEMP1_cellneighbors.dbf"
cell05cent2dbf = "_TEMP1_cell05cent2.dbf"
celllakesdbf = "_TEMP1_cell_lakes.dbf"
cell05actdbf = "_TEMP1_cell05_act.dbf"

# output
cellneigborstxt = "DYA_cellneighbors.txt"
cell05cent2txt = "DYA_cellcents.txt"
celllakestxt = "DYA_celllakes.txt"
cell05acttxt = "DYA_cellact.txt"

############################## Geoprocessing ##########################

####################################
# 1) create 0.5 x 0.5 cells
####################################

# Process: Create Fishnet
print "Creating 0.5x0.5 cells"
arcpy.CreateFishnet_management(fishnet05, "-180 -65", "-180 -55", "0,5", "0,5", "0", "0", "180 85", "NO_LABELS", "-180 -65 180 85", "POLYGON")

# Process: Define Projection
print "Defining projection for cells to WGS 1984"
arcpy.DefineProjection_management(fishnet05, wgs84)

# Process: Add Field
print "Adding unique cell-id to fishnet"
arcpy.AddField_management(fishnet05, "cell05_id", "LONG", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field
print "populating the cell-id"
arcpy.CalculateField_management(fishnet05, "cell05_id", "!FID!+1", "PYTHON_9.3", "")

###########################################
# 2) getting languages spoken in each cell
###########################################

# Process: Spatial Join
fms = arcpy.FieldMappings()
fms.addTable(fishnet05)
fms.addTable(GREG)
print "Obtaining languages spoken by spatial join of fishnet and GREG"
arcpy.SpatialJoin_analysis(fishnet05, GREG, cell05, "JOIN_ONE_TO_MANY", "KEEP_COMMON", fms, "INTERSECT", "", "")
del fms	

print "removing unnecessary fields from the spatial join"
fields = arcpy.ListFields(cell05) 
# manually enter field names to keep here
# include mandatory fields name such as OBJECTID (or FID), and Shape in keepfields
keepFields = ["FID", "Shape", "cell05_id", "G1ID", "G2ID", "G3ID"]
dropFields = [x.name for x in fields if x.name not in keepFields]
# delete fields
arcpy.DeleteField_management(cell05, dropFields)

##########################################################################
# 3) get area, water area, centroids and coordiates for cells
##########################################################################

# a) cell areas

# Process: Project
print "projecting cells to world cylindrical equal area"
arcpy.Project_management(cell05, cell05cyl, wcea)

# Process: Add Field
print "Adding field for cell areas"
arcpy.AddField_management(cell05cyl, "area", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field
print "calculating cell areas"
arcpy.CalculateField_management(cell05cyl, "area", "!SHAPE.AREA@SQUAREKILOMETERS!", "PYTHON_9.3", "")

# Process: Project
print "projecting cells back to WGS84"
arcpy.Project_management(cell05cyl, cell05, wgs84)

# b) adding coordinates

# Process: Feature to Point
print "Finding cell centroids"
arcpy.FeatureToPoint_management(cell05, cell05cent, "INSIDE")

# Process: Add XY Coordinates
print "Adding latitude (POINT_Y) and longitude (POINT_X) to cell centroids"
arcpy.AddXY_management(cell05cent)

# c) getting water area

# Process: Intersect
print "Intersect cells with lakes"
list_intersect = [cell05, lakes]
arcpy.Intersect_analysis(list_intersect, celllakes, "ALL", "", "INPUT")

# Process: Project
print "projecting cells / lakes to world cylindrical equal area"
arcpy.Project_management(celllakes, celllakescyl, wcea)

# Process: Add Field
print "Adding field for water areas"
arcpy.AddField_management(celllakescyl, "watarea", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field
print "calculating water areas"
arcpy.CalculateField_management(celllakescyl, "watarea", "!SHAPE.AREA@SQUAREKILOMETERS!", "PYTHON_9.3", "")

# Process: Project
print "projecting water areas back to WGS84"
arcpy.Project_management(celllakescyl, celllakes, wgs84)

print "removing unnecessary fields from water areas"
fields = arcpy.ListFields(celllakes) 
# manually enter field names to keep here
# include mandatory fields name such as OBJECTID (or FID), and Shape in keepfields
keepFields = ["FID", "Shape", "cell05_id", "watarea"]
dropFields = [x.name for x in fields if x.name not in keepFields]
# delete fields
arcpy.DeleteField_management(celllakes, dropFields)

# Process: Intersect
# note: "ALL" drops nothing from the intersection
print "intersecting cells and actual countries"
list_intersect = [cell05, countries]
arcpy.Intersect_analysis(list_intersect, cell05act, "ALL", "1 Meters", "INPUT")

print "removing unnecessary fields from intersection"
fields = arcpy.ListFields(cell05act) 
# manually enter field names to keep here
# include mandatory fields name such as OBJECTID (or FID), and Shape in keepfields
keepFields = ["FID", "Shape", "cell05_id", "ADMIN"]
dropFields = [x.name for x in fields if x.name not in keepFields]
# delete fields
arcpy.DeleteField_management(cell05act, dropFields)

###########################################################################
# 4) get raster values for every cell and intersect with actual countries
###########################################################################

# print "projecting the population rasters to WGS84"
arcpy.DefineProjection_management(popd1990, wgs84)
arcpy.DefineProjection_management(popd2000, wgs84)
arcpy.DefineProjection_management(popcount, wgs84)

# Process: Extract Multi Values to Points
# note the way we define a list of lists for "inrasts, first element of each (there can be more than one raster 
# with this tool) inner list is the raster name, the second is the name of the variable"
print "obtaining cell raster values with extract multi values to point"
inrasts = [[elevation, "elev"], [landqual, "suit"], [temp, "temp"], [prec, "prec"], [popd1990, "pd90"], [popd2000, "pd00"], [popcount, "pc95"]]
arcpy.gp.ExtractMultiValuesToPoints_sa(cell05cent, inrasts, "NONE")

# Process: Intersect
print "Intersect cell centroids and actual countries"
list_intersect = [cell05cent, countries]
arcpy.Intersect_analysis(list_intersect, cell05cent2, "ALL", "", "INPUT")

print "removing unnecessary fields from centroids"
fields = arcpy.ListFields(cell05cent2) 
# manually enter field names to keep here
# include mandatory fields name such as OBJECTID (or FID), and Shape in keepfields
keepFields = ["FID", "Shape", "ne_10m_adm", "ADMIN", "cell05_id", "POINT_X", "POINT_Y", "area", "G1ID", "G2ID", "G3ID", "elev", "suit", "temp", "prec", "pd90", "pd00", "pc95"]
dropFields = [x.name for x in fields if x.name not in keepFields]
# delete fields
arcpy.DeleteField_management(cell05cent2, dropFields)

# Process: Near
print "finding lat/lon of closest coast"
arcpy.Near_analysis(cell05cent2, coast, "", "LOCATION", "NO_ANGLE", "GEODESIC")
print "renaming the near coast xy-fields to latitude and longitude"
arcpy.AddField_management(cell05cent2, "coastLAT", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(cell05cent2, "coastLON", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(cell05cent2, "coastLAT", "!NEAR_Y!", "PYTHON_9.3", "")
arcpy.CalculateField_management(cell05cent2, "coastLON", "!NEAR_X!", "PYTHON_9.3", "")
arcpy.DeleteField_management(cell05cent2, ["NEAR_FID", "NEAR_DIST", "NEAR_X", "NEAR_Y"])

###########################################################################
# 5) use polygon neighbors to get dyadic structure
###########################################################################

# Process: Polygon Neighbors
print "obtaining the list of adjacent cell pairs using Polygon Neighbors"
arcpy.PolygonNeighbors_analysis(cell05, cellneighbors, "cell05_id", "NO_AREA_OVERLAP", "NO_BOTH_SIDES", "", "DECIMAL_DEGREES", "SQUARE_MILES")

###########################################################################
# 6) converting output to txt
###########################################################################

fms = arcpy.FieldMappings()
fms.addTable(cell05cent2dbf)
print "converting table to txt: centroids"
# Process: Table to Table
arcpy.TableToTable_conversion(cell05cent2dbf, outdir, cell05cent2txt, "", fms, "")
del fms

fms = arcpy.FieldMappings()
fms.addTable(celllakesdbf)
print "converting table to txt: water areas"
# Process: Table to Table
arcpy.TableToTable_conversion(celllakesdbf, outdir, celllakestxt, "", fms, "")
del fms

fms = arcpy.FieldMappings()
fms.addTable(cell05actdbf)
print "converting table to txt: cell/actual country intersection"
# Process: Table to Table
arcpy.TableToTable_conversion(cell05actdbf, outdir, cell05acttxt, "", fms, "")
del fms

# Process: Table to Table
# Note: Kudamatsu uses a workaround - maybe this tool did not exist yet
fms = arcpy.FieldMappings()
fms.addTable(cellneighbors)
print "converting table to txt: neighbors"
# Process: Table to Table
arcpy.TableToTable_conversion(cellneighbors, outdir, cellneigborstxt, "", fms, "")
del fms


########################## End of Geoprocessing ##########################

# Final cleanup
print "deleting unnecessary intermediate files"
for fn in os.listdir(outdir):
    if "_TEMP1_" in fn:
        fpath = outdir + "/" + fn
        os.remove(fpath)
    if ".txt.xml" in fn:
        fpath = outdir + "/" + fn
        os.remove(fpath)


### Release the memory ###
print "Closing ArcGIS 10.6.1"
del os, arcpy

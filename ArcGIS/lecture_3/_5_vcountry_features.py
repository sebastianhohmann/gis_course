# Import arcpy module
## Read the ArcGIS object ###
print "Launching ArcGIS 10.6.1"
import arcpy, os

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

maindir = "C:/Users/se.4537/Dropbox/PoliteconGIS/Lecture 3"
GISdir = maindir + "/GIS data"
outdir = "C:/Users/se.4537/Dropbox/PoliteconGIS/Bonn_2019/Lecture 3/Michalopoulos_2012/_output"
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
GREG = "greg_cleaned.shp"

# intermediates
fishnet25 = "_TEMP1_fishnet25.shp"
fish_country_int = "_TEMP1_fc_intersec.shp"
fish_GREG_int = "_TEMP1_fg_intersect.shp"
vcountry = "_TEMP_vcountry.shp"
vcgreg = "_TEMP_vcgreg.shp"
vcgregcyl = "_TEMP1_vcgreg_cyl.shp"
vcgreglakes = "_TEMP1_vcgreglakes.shp"
vcgreglakescyl = "_TEMP1_vcgreglakescyl.shp"
vcgregcent1 = "_TEMP1_vcgregcentroids1.shp"
vcgregcent2 = "_TEMP_vcgregcentroids2.shp"
union = "_TEMP1_union.shp"
unmatched = "_TEMP_unmatched.shp"
vcgregact = "_TEMP1_vcgregact.shp"

umdbf = "_TEMP_unmatched.dbf"
lakdbf = "_TEMP1_vcgreglakes.dbf"
centdbf = "_TEMP_vcgregcentroids2.dbf"
vcgregactdbf = "_TEMP1_vcgregact.dbf"

# output
umtxt = "VC_unmached.txt"
vccenttxt = "VC_vcgregcent.txt"
vclakestxt = "VC_vcgreglakes.txt"
vcgregacttxt = "VC_vcgregact.txt"

############################## Geoprocessing ##########################

####################################
# 1) create virtual countries
####################################

# Process: Create Fishnet
print "Creating 2.5x2.5 cells"
arcpy.CreateFishnet_management(fishnet25, "-180 -65", "-180 -55", "2,5", "2,5", "0", "0", "180 85", "NO_LABELS", "-180 -65 180 85", "POLYGON")

# Process: Define Projection
print "Defining projection for cells to WGS 1984"
arcpy.DefineProjection_management(fishnet25, wgs84)

# Process: Add Field
print "Adding unique cell-id to fishnet"
arcpy.AddField_management(fishnet25, "cell25_id", "SHORT", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field
print "populating the cell-id"
arcpy.CalculateField_management(fishnet25, "cell25_id", "!FID!+1", "PYTHON_9.3", "")

# Process: Intersect
# note: "ALL" drops nothing from the intersection
print "intersecting fishnet and countries"
list_intersect = [fishnet25, countries]
arcpy.Intersect_analysis(list_intersect, fish_country_int , "ALL", "1 Meters", "INPUT")

# Process: Dissolve
print "using dissolve on the intersection to obtain the virtual countries"
arcpy.Dissolve_management(fish_country_int, vcountry, "cell25_id", "", "MULTI_PART", "DISSOLVE_LINES")


#####################################################
# 2) obtain number of languages in virtual countries
#####################################################

# Process: Intersect
# note: "ALL" drops nothing from the intersection
print "intersecting fishnet and GREG"
list_intersect = [vcountry, GREG]
arcpy.Intersect_analysis(list_intersect, fish_GREG_int, "ALL", "1 Meters", "INPUT")

# Process: Dissolve
print "Obtaining number of languages spoken through dissolve"
arcpy.Dissolve_management(fish_GREG_int, vcgreg, "cell25_id", "FID_greg_c COUNT", "MULTI_PART", "DISSOLVE_LINES")

# Process: Intersect
# note: "ALL" drops nothing from the intersection
print "intersecting vcgreg and actual countries"
list_intersect = [vcgreg, countries]
arcpy.Intersect_analysis(list_intersect, vcgregact, "ALL", "1 Meters", "INPUT")


# #####################################################
# # 3) obtain areas without languages
# #####################################################

# Process: Union
print "Identifying no language area: union between fishnet and GREG"
list_union = [vcountry, GREG]
arcpy.Union_analysis(list_union, union, "ALL", "1 Meters", "GAPS")

# Process: Select
print "Identifying no language area: select places without FID_GREG"
arcpy.Select_analysis(union, unmatched, "\"FID_greg_c\" = -1")

###########################################################################
# 4) get area, water area, centroids and coordiates for virtual countries
###########################################################################

# a) vc areas

# Process: Project
print "projecting virtual countries to world cylindrical equal area"
arcpy.Project_management(vcgreg, vcgregcyl, wcea)

# Process: Add Field
print "Adding field for country areas"
arcpy.AddField_management(vcgregcyl, "area", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field
print "calculating country areas"
arcpy.CalculateField_management(vcgregcyl, "area", "!SHAPE.AREA@SQUAREKILOMETERS!", "PYTHON_9.3", "")

# Process: Project
print "projecting virtual countries back to WGS84"
arcpy.Project_management(vcgregcyl, vcgreg, wgs84)

# b) adding coordinates

# Process: Feature to Point
print "Finding virtual country centroids"
arcpy.FeatureToPoint_management(vcgreg, vcgregcent1, "INSIDE")

# Process: Add XY Coordinates
print "Adding latitude (POINT_Y) and longitude (POINT_X) to virtual country centroids"
arcpy.AddXY_management(vcgregcent1)

# c) getting water area

# Process: Intersect
print "Intersect virtual countries with lakes"
list_intersect = [vcgreg, lakes]
arcpy.Intersect_analysis(list_intersect, vcgreglakes, "ALL", "", "INPUT")

# Process: Project
print "projecting virtual countries/ lakes to world cylindrical equal area"
arcpy.Project_management(vcgreglakes, vcgreglakescyl, wcea)

# Process: Add Field
print "Adding field for water areas"
arcpy.AddField_management(vcgreglakescyl, "watarea", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field
print "calculating water areas"
arcpy.CalculateField_management(vcgreglakescyl, "watarea", "!SHAPE.AREA@SQUAREKILOMETERS!", "PYTHON_9.3", "")

# Process: Project
print "projecting water areas back to WGS84"
arcpy.Project_management(vcgreglakescyl, vcgreglakes, wgs84)

print "removing unnecessary fields from water areas"
fields = arcpy.ListFields(vcgreglakes) 
# manually enter field names to keep here
# include mandatory fields name such as OBJECTID (or FID), and Shape in keepfields
keepFields = ["FID", "Shape", "cell25_id", "watarea"]
dropFields = [x.name for x in fields if x.name not in keepFields]
# delete fields
arcpy.DeleteField_management(vcgreglakes, dropFields)


#########################################################
# 5) get additional variables for virtual countries
#########################################################

# Process: Intersect
print "Intersect virtual country centroids and actual countries"
list_intersect = [vcgregcent1, countries]
arcpy.Intersect_analysis(list_intersect, vcgregcent2, "ALL", "", "INPUT")

print "removing unnecessary fields from centroids"
fields = arcpy.ListFields(vcgregcent2) 
# manually enter field names to keep here
# include mandatory fields name such as OBJECTID (or FID), and Shape in keepfields
keepFields = ["FID", "Shape", "ne_10m_adm", "ADMIN", "cell25_id", "POINT_X", "POINT_Y", "COUNT_FID_", "area"]
dropFields = [x.name for x in fields if x.name not in keepFields]
# delete fields
arcpy.DeleteField_management(vcgregcent2, dropFields)

# Process: Near
print "finding lat/lon of closest coast"
arcpy.Near_analysis(vcgregcent2, coast, "", "LOCATION", "NO_ANGLE", "GEODESIC")
print "renaming the near coast xy-fields to latitude and longitude"
arcpy.AddField_management(vcgregcent2, "coastLAT", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(vcgregcent2, "coastLON", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(vcgregcent2, "coastLAT", "!NEAR_Y!", "PYTHON_9.3", "")
arcpy.CalculateField_management(vcgregcent2, "coastLON", "!NEAR_X!", "PYTHON_9.3", "")
arcpy.DeleteField_management(vcgregcent2, ["NEAR_FID", "NEAR_DIST", "NEAR_X", "NEAR_Y"])


##############################################################
# 6) output tables to txt
##############################################################


fms = arcpy.FieldMappings()
fms.addTable(umdbf)
print "converting unmatched table to txt"
# Process: Table to Table
arcpy.TableToTable_conversion(umdbf, outdir, umtxt, "", fms, "")
del fms

fms = arcpy.FieldMappings()
fms.addTable(centdbf)
print "converting virtual country centroids table to txt"
# Process: Table to Table
arcpy.TableToTable_conversion(centdbf, outdir, vccenttxt, "", fms, "")
del fms

fms = arcpy.FieldMappings()
fms.addTable(lakdbf)
print "converting virtual country lakes table to txt"
# Process: Table to Table
arcpy.TableToTable_conversion(lakdbf, outdir, vclakestxt, "", fms, "")
del fms

fms = arcpy.FieldMappings()
fms.addTable(vcgregactdbf)
print "converting vcgreg/actual intersection to txt"
# Process: Table to Table
arcpy.TableToTable_conversion(vcgregactdbf, outdir, vcgregacttxt, "", fms, "")
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

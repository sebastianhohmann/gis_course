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

wcea = arcpy.SpatialReference(54034)

#### inputs ####
countries = GISdir + "/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
coast = GISdir + "/ne_10m_coastline/ne_10m_coastline.shp"
GREG = "greg_cleaned.shp"

#### intermediats ####
int_GREG_countries = "_temp_int_GREG_countries.shp"
int_dissolved = "_temp_int_dissolved.shp"
dbf_dissolved = "_temp_int_dissolved.dbf"
temp_centroids = "_temp_centroids.shp"
dbf_centroids = "_temp_centroids.dbf"
ctries_projected = "_temp_countries_world_cylin_equal_area.shp"
ctries_projected_dbf = "_temp_countries_world_cylin_equal_area.dbf"

### outputs ####
nlangs = "nlangs_country.txt"
ctry_centroids = "centroids_country.txt"
ctry_areas = "country_areas.txt"

############################## Geoprocessing ##########################

#######################################################
# 1) number of languages per country
#######################################################

# Process: Intersect
# note: "ALL" drops nothing from the intersection
print "intersecting countries and GREG"
list_intersect = [countries, GREG]
arcpy.Intersect_analysis(list_intersect, int_GREG_countries, "ALL", "1 Meters", "INPUT")

# Process: Dissolve
print "Obtaining number of languages spoken through dissolve"
arcpy.Dissolve_management(int_GREG_countries, int_dissolved, "ADMIN", "FID_greg_c COUNT", "MULTI_PART", "DISSOLVE_LINES")

fms = arcpy.FieldMappings()
fms.addTable(dbf_dissolved)
print "converting table with number of languages to txt"
# Process: Table to Table
arcpy.TableToTable_conversion(dbf_dissolved, outdir, nlangs, "", fms, "")
del fms

#######################################################
# 2) finding centroids, distance to coast
#######################################################

# Process: Feature to Point
print "Finding country centroids"
arcpy.FeatureToPoint_management(countries, temp_centroids, "INSIDE")

# Process: Add XY Coordinates
print "Adding latitude (POINT_Y) and longitude (POINT_X) to country centroids"
arcpy.AddXY_management(temp_centroids)

print "removing unnecessary fields from centroids"
fields = arcpy.ListFields(temp_centroids) 
# manually enter field names to keep here
# include mandatory fields name such as OBJECTID (or FID), and Shape in keepfields
keepFields = ["FID", "Shape", "ne_10m_adm", "ADMIN", "POINT_X", "POINT_Y"]
dropFields = [x.name for x in fields if x.name not in keepFields]
# delete fields
arcpy.DeleteField_management(temp_centroids, dropFields)

# Process: Near
print "finding lat/lon of closest coast"
arcpy.Near_analysis(temp_centroids, coast, "", "LOCATION", "NO_ANGLE", "GEODESIC")
print "renaming the near coast xy-fields to latitude and longitude"
arcpy.AddField_management(temp_centroids, "coastLAT", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(temp_centroids, "coastLON", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(temp_centroids, "coastLAT", "!NEAR_Y!", "PYTHON_9.3", "")
arcpy.CalculateField_management(temp_centroids, "coastLON", "!NEAR_X!", "PYTHON_9.3", "")
arcpy.DeleteField_management(temp_centroids, ["NEAR_FID", "NEAR_DIST", "NEAR_X", "NEAR_Y"])

fms = arcpy.FieldMappings()
fms.addTable(dbf_centroids)
print "converting table with centroids to txt"
# Process: Table to Table
arcpy.TableToTable_conversion(dbf_centroids, outdir, ctry_centroids, "", fms, "")
del fms   

#######################################################
# 3) finding country areas
#######################################################

# Process: Project
print "projecting countries to world cylindrical equal area"
arcpy.Project_management(countries, ctries_projected, wcea)

# Process: Add Field
print "Adding field for country areas"
arcpy.AddField_management(ctries_projected, "area", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field
print "calculating country areas"
arcpy.CalculateField_management(ctries_projected, "area", "!SHAPE.AREA@SQUAREKILOMETERS!", "PYTHON_9.3", "")

print "removing unnecessary fields from countries with area"
fields = arcpy.ListFields(ctries_projected) 
# manually enter field names to keep here
# include mandatory fields name such as OBJECTID (or FID), and Shape in keepfields
keepFields = ["FID", "Shape", "ne_10m_adm", "ADMIN", "area"]
dropFields = [x.name for x in fields if x.name not in keepFields]
# delete fields
arcpy.DeleteField_management(ctries_projected, dropFields)

fms = arcpy.FieldMappings()
fms.addTable(ctries_projected_dbf)
print "converting table with centroids to txt"
# Process: Table to Table
arcpy.TableToTable_conversion(ctries_projected_dbf, outdir, ctry_areas, "", fms, "")
del fms   

########################## End of Geoprocessing ##########################

# Final cleanup
print "deleting unnecessary intermediate files"
for fn in os.listdir(outdir):
    if "_temp_" in fn:
        fpath = outdir + "/" + fn
        os.remove(fpath)


del arcpy, os
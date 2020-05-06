print "Launching ArcGIS 10.6.1"
import os, arcpy

maindir = "C:/Users/se.4537/Dropbox/PoliteconGIS/Lecture 3"
GISdir = maindir + "/GIS data"
outdir = "C:/Users/se.4537/Dropbox/PoliteconGIS/Bonn_2019/Lecture 3/Michalopoulos_2012/_output"
arcpy.env.workspace = outdir 
arcpy.env.overwriteOutput = True
#arcpy.CheckOutExtension("Spatial") 

### Local variables ###
GREG_in = GISdir + "/GREG.shp"
greg_copy = "_TEMP_greg_copy.shp"
greg_group2 = "_TEMP_greg_group2.shp"
greg_group3 = "_TEMP_greg_group3.shp"
greg_merge = "_TEMP_greg_merge.shp"
#greg_merge = "greg_merge.shp"
greg_dissolve = "greg_cleaned.shp"


############################## Geoprocessing ##########################

#############################################################
# 1) Create ID equal to ID of first language
# Drop polygons that have only one language
#############################################################

# Process: Copy Features
print "Keep the original data"
arcpy.CopyFeatures_management(GREG_in, greg_copy, "", "0", "0", "0")

# Process: Add Field
print "Create the field GID: language code 1/2"
arcpy.AddField_management(greg_copy, "GID", "SHORT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field
print "Create the field GID: language code 2/2; ID field is the ID of the first language in the polygon"
arcpy.CalculateField_management(greg_copy, "GID", "!G1ID!", "PYTHON_9.3", "")

# Process: Add Field (2)
print "Create the field SHORTNAME: language name short 1/2"
arcpy.AddField_management(greg_copy, "SHORTNAME", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (2)
print "Create the field SHORTNAME: language name short 2/2"
arcpy.CalculateField_management(greg_copy, "SHORTNAME", "!G1SHORTNAM!", "PYTHON_9.3", "")

# Process: Add Field (3)
print "Create the field LONGNAME: language name long 1/2"
arcpy.AddField_management(greg_copy, "LONGNAME", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (3)
print "Create the field LONGNAME: language name long 2/2"
arcpy.CalculateField_management(greg_copy, "LONGNAME", "!G1LONGNAM!", "PYTHON_9.3", "")

# Process: Select
print "Create 2nd language polygons (Drop polygons with only one language)"
arcpy.Select_analysis(greg_copy, greg_group2, "\"G2ID\" <> 0")

###############################################################################
# 2) Of the polygons with at least 2 Change ID equal to ID of second language
# drop those with at most 2 languages
###############################################################################

# # Process: Delete Field
# print "Deleting the GID field in the shapefile with polygons containing more than one language"
# arcpy.DeleteField_management(greg_group2, "GID")

# #Process: Add Field (4)
# print "Create the field GID for 2nd language polygons 1/2"
# arcpy.AddField_management(greg_group2, "GID", "SHORT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (4)
print "Create the field GID for 2nd language polygons 2/2"
arcpy.CalculateField_management(greg_group2, "GID", "!G2ID!", "PYTHON_9.3", "")

# Process: Add Field (5)
print "Create the field SHORTNAME for 2nd language polygons 1/2"
arcpy.AddField_management(greg_group2, "SHORTNAME", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (5)
print "Create the field SHORTNAME for 2nd language polygons 2/2"
arcpy.CalculateField_management(greg_group2, "SHORTNAME", "!G2SHORTNAM!", "PYTHON_9.3", "")

# Process: Add Field (6)
print "Create the field LONGNAME for 2nd language polygons 1/2"
arcpy.AddField_management(greg_group2, "LONGNAME", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (6)
print "Create the field LONGNAME for 2nd language polygons 2/2"
arcpy.CalculateField_management(greg_group2, "LONGNAME", "!G2LONGNAM!", "PYTHON_9.3", "")

# Process: Select (2)
print "Create 3rd language polygons (Drop polygons with at most two languages)"
arcpy.Select_analysis(greg_copy, greg_group3, "\"G3ID\" <> 0")

#######################################################################
# 3) Of the polygons with 3 Change ID equal to ID of third language
#######################################################################

# # Process: Delete Field
# print "Deleting the GID field in the shapefile with polygons containing three languages"
# arcpy.DeleteField_management(greg_group3, "GID")

# # Process: Add Field (7)
# print "Create the field GID for 3rd language polygons 1/2"
# arcpy.AddField_management(greg_group3, "GID", "SHORT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (7)
print "Create the field GID for 3rd language polygons 2/2"
arcpy.CalculateField_management(greg_group3, "GID", "!G3ID!", "PYTHON_9.3", "")

# Process: Add Field (8)
print "Create the field SHORTNAME for 3rd language polygons 1/2"
arcpy.AddField_management(greg_group3, "SHORTNAME", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (8)
print "Create the field SHORTNAME for 3rd language polygons 2/2"
arcpy.CalculateField_management(greg_group3, "SHORTNAME", "!G3SHORTNAM!", "PYTHON_9.3", "")

# Process: Add Field (9)
print "Create the field LONGNAME for 3rd language polygons 1/2"
arcpy.AddField_management(greg_group3, "LONGNAME", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (9)
print "Create the field LONGNAME for 3rd language polygons 2/2"
arcpy.CalculateField_management(greg_group3, "LONGNAME", "!G3LONGNAM!", "PYTHON_9.3", "")

#######################################################################
# 4)  Merging and dissolving the 1st, 2nd, and 3rd language polygons
#######################################################################

# Process: Merge
print "Merge 1st, 2nd, and 3rd language polygons"
polygon_list = [greg_copy, greg_group2, greg_group3]
arcpy.Merge_management(polygon_list, greg_merge, "")

# # Process: Dissolve
# print "Dissolve by language so each language has just one polygon"
# arcpy.Dissolve_management(greg_merge, greg_dissolve, "GID;SHORTNAME;LONGNAME", "", "MULTI_PART", "DISSOLVE_LINES")

# ########################## End of Geoprocessing ##########################

# # Final cleanup
# print "deleting unnecessary intermediate files"
# for fn in os.listdir(outdir):
#     if "_TEMP_" in fn:
#         fpath = outdir + "/" + fn
#         os.remove(fpath)

# ### Release the memory ###
# print "Closing ArcGIS"
# del arcpy, os

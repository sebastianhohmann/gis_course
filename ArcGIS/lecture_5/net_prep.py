# Name: MarketAccess_creation.py
# Description: Create a database that will be used to (manually) create a network database
#              
# Requirements: Spatial Analyst Extension 
# Author: Giorgio Chiovelli

#Import arcpy module
import arcpy
from arcpy import env
import os
import timeit

start = timeit.timeit()
print start

#Turn overwrite on
arcpy.CheckOutExtension("spatial")
#arcpy.CheckOutExtension("Network")
arcpy.env.overwriteOutput = True

print  "overwrite on"


# Local variables:
directory = "C:/Users/se.4537/Dropbox/PoliteconGIS/Bonn_2019/Lecture 5/GIS data/_workflow2/"

workspace1=directory+"dh.gdb/"
workspace2=directory+"modified.gdb/"
nad_us = arcpy.SpatialReference(102003)
dataset=workspace1
feature_dataset="dh_class"

# Set the local variables  
  
       


#Set working directory

# Create a personal dataset 
arcpy.CreateFileGDB_management(directory, "dh.gdb")
arcpy.CreateFileGDB_management(directory, "modified.gdb")
print  "fildegdb created"
# Create a feature dataset
arcpy.CreateFeatureDataset_management(workspace1,feature_dataset,nad_us)
print  "FeatureDataset created"


# Define a worspace
arcpy.env.workspace=workspace2
print  "Environment set"

#####################################################################################################
#####################################################################################################
#####################################################################################################
# 1) fixing rail geometries
#####################################################################################################
#####################################################################################################
#####################################################################################################
#Try statment, to avoid crashes
try:
    year=['1870','1890']
    print "list ok"
    
    for year in year:
        rail_check=directory+"rail"+str(year)+"_p.shp"
        
        

        arcpy.RepairGeometry_management(rail_check, "DELETE_NULL")
    
        print  "geometry repaired"

    

except Exception as e:
    # If an error occurred, print line number and error message
    import traceback, sys
    tb = sys.exc_info()[2]
    print "An error occured on line %i" % tb.tb_lineno
    print str(e)


#####################################################################################################
#####################################################################################################
#####################################################################################################
# 2) defining network parameters
#####################################################################################################
#####################################################################################################
#####################################################################################################
 
walk="0.231"
parameter_rail="0.0063"
parameter_river="0.0049"


#####################################################################################################
#####################################################################################################
#####################################################################################################
# 3) creating connections
#####################################################################################################
#####################################################################################################
#####################################################################################################


#####################################################################################################
#####################################################################################################
# 3.1) direct centroid to centroid connections
#####################################################################################################
#####################################################################################################


centroids=directory+"centroids_p.shp"
out_centroids=workspace2+"near_centroids"
centr_to_centr=workspace2+"centr_to_centr"

# defining WGS84 CRS
wgs84 = arcpy.SpatialReference(4326)

# Create near table with location for radius of 300 km
arcpy.GenerateNearTable_analysis(centroids, centroids, out_centroids, "300 Kilometers", "LOCATION", "NO_ANGLE", "ALL", "0", "GEODESIC")
print  "near table centroids done"

arcpy.XYToLine_management(out_centroids, centr_to_centr, "FROM_X", "FROM_Y", "NEAR_X", "NEAR_Y", "GEODESIC", "", wgs84)
print  "near table to line centroids done"

arcpy.AddField_management(centr_to_centr, "Parameter", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
print  "generate Parameter field centroids done"

arcpy.CalculateField_management(centr_to_centr, "Parameter", walk, "VB", "")
print  "calculate Parameter field centroids done"

arcpy.DeleteField_management(centr_to_centr, "FROM_X;FROM_Y;NEAR_X;NEAR_Y")
print  "delete fields centroids done"

arcpy.AddField_management(centr_to_centr, "Length", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
print  "generate Length field centroids done"

# to calculate c to c length, we dont need to project but can directly
# use geodesic length since they are straight lines

arcpy.CalculateField_management(centr_to_centr, "Length", "!shape.geodesicLength@KILOMETERS!", "PYTHON_9.3", "")
print  "calculate length in kilometers"

arcpy.AddField_management(centr_to_centr, "cost_hd", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
print  "generate Length field centroids done"

arcpy.CalculateField_management(centr_to_centr, "cost_hd", "([Length]*[Parameter])/1609.344",  "VB", "")
print  "calculate length in kilometers"


#####################################################################################################
#####################################################################################################
# 3.2) centroid to river connections
#####################################################################################################
#####################################################################################################

river=directory+"river_p.shp"
river_table=workspace2+"river_table"
cent_river=workspace2+"centr_river"


# Create near table with location for closest river
arcpy.GenerateNearTable_analysis(centroids, river, river_table, "", "LOCATION", "NO_ANGLE", "CLOSEST", "0", "GEODESIC")
print  "near table closest river done"

arcpy.XYToLine_management(river_table, cent_river, "FROM_X", "FROM_Y", "NEAR_X", "NEAR_Y", "GEODESIC", "", wgs84)
print  "near table to line closest river done"

arcpy.AddField_management(cent_river, "Parameter", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
print  "generate Parameter field closest river done"

arcpy.CalculateField_management(cent_river, "Parameter", walk, "VB", "")
print  "calculate Parameter field closest river done"

arcpy.DeleteField_management(cent_river, "FROM_X;FROM_Y;NEAR_X;NEAR_Y")
print  "delete fields centroids done"

arcpy.AddField_management(cent_river, "Length", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
print  "generate Length field river-centroids done"

arcpy.CalculateField_management(cent_river, "Length", "!shape.geodesicLength@KILOMETERS!", "PYTHON_9.3", "")
print  "calculate length in kilometers"

arcpy.AddField_management(centr_to_centr, "cost_hd", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
print  "generate Length field centroids done"

arcpy.CalculateField_management(centr_to_centr, "cost_hd", "([Length]*[Parameter])/1609.344",  "VB", "")
print  "calculate length in kilometers"

#####################################################################################################
#####################################################################################################
# 3.3) centroid to rail connections
#####################################################################################################
#####################################################################################################


try:
    year=['1870','1890']
    print "list ok"
    
    for year in year:

        rail=directory+"rail"+str(year)+"_p.shp"
        rail_table=workspace2+"rail_t"+str(year)
        cent_rail=workspace2+"centr_rail_"+str(year)
# Create near table with location for closest rail

        arcpy.GenerateNearTable_analysis(centroids, rail, rail_table, "", "LOCATION", "NO_ANGLE", "CLOSEST", "0", "GEODESIC")
        print "near table closest rail done"

        arcpy.XYToLine_management(rail_table, cent_rail, "FROM_X", "FROM_Y", "NEAR_X", "NEAR_Y", "GEODESIC", "", wgs84)
        print "near table to line closest rail done"

        arcpy.AddField_management(cent_rail, "Parameter", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print "generate Parameter field closest rail done"

        arcpy.CalculateField_management(cent_rail, "Parameter", walk, "VB", "")
        print "calculate Parameter field closest rail done"

        arcpy.DeleteField_management(cent_rail, "FROM_X;FROM_Y;NEAR_X;NEAR_Y")
        print "delete fields centroids done"

        arcpy.AddField_management(cent_rail, "Length", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print  "generate Length field centroids done"

        arcpy.CalculateField_management(cent_rail, "Length", "!shape.geodesicLength@KILOMETERS!", "PYTHON_9.3", "")
        print  "calculate length in kilometers"

        arcpy.AddField_management(cent_rail, "cost_hd", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print  "generate Length field centroids done"

        arcpy.CalculateField_management(cent_rail, "cost_hd", "([Length]*[Parameter])/1609.344",  "VB", "")
        print  "calculate length in kilometers"


except Exception as e:
    # If an error occurred, print line number and error message
    import traceback, sys
    tb = sys.exc_info()[2]
    print "An error occured on line %i" % tb.tb_lineno
    print str(e)


#####################################################################################################
#####################################################################################################
#####################################################################################################
# 4) setting parameters for rail and river
#####################################################################################################
#####################################################################################################
#####################################################################################################

#####################################################################################################
#####################################################################################################
# 4.1) setting parameter for rail
#####################################################################################################
#####################################################################################################


try:
    year=['1870','1890']
    print "list ok"
    
    for year in year:

        rail=directory+"rail"+str(year)+"_p.shp"
        rail2=workspace2+"rail_"+str(year)

# Let us set the parameter for Rail


        arcpy.CopyFeatures_management(rail, rail2, "", "0", "0", "0")
        print "copy"


        arcpy.AddField_management(rail2, "Parameter", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print "generate Parameter field river done"

        arcpy.CalculateField_management(rail2, "Parameter", parameter_rail, "VB", "")
        print "calculate Parameter field river done"

        arcpy.AddField_management(rail2, "Length", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print  "generate Length field centroids done"

        arcpy.CalculateField_management(rail2, "Length", "!shape.geodesicLength@KILOMETERS!", "PYTHON_9.3", "")
        print  "calculate length in kilometers"

        arcpy.AddField_management(rail2, "cost_hd", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print  "generate Length field centroids done"

        arcpy.CalculateField_management(rail2, "cost_hd", "([Length]*[Parameter])/1609.344",  "VB", "")
        print  "calculate length in kilometers"


except:
    print  "There is an error somewhere in the code"
    print  arcpy.GetMessages()


    
#####################################################################################################
#####################################################################################################
# 4.2) setting parameter for river
#####################################################################################################
#####################################################################################################

river2=workspace2+"river"

arcpy.CopyFeatures_management(river, river2, "", "0", "0", "0")
print  "copy"

arcpy.AddField_management(river2, "Parameter", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
print  "generate Parameter field river done"

arcpy.CalculateField_management(river2, "Parameter", parameter_river, "VB", "")
print  "calculate Parameter field river done"


#####################################################################################################
#####################################################################################################
#####################################################################################################
# 5) creating the raw shapefiles for the network
#####################################################################################################
#####################################################################################################
#####################################################################################################

before_database = timeit.timeit()
print  before_database - start

try:
    year=['1870','1890']
    print "list ok"
    
    for year in year:

        river3=workspace2+"river"
        rail70=workspace2+"rail_1870"
        rail90=workspace2+"rail_1890"
        cent_rail70=workspace2+"centr_rail_1870"
        cent_rail90=workspace2+"centr_rail_1890"
        cent_river1=workspace2+"centr_river"
        
        
        infeatures=[river3,cent_river1] 
        merge=workspace2+"merge_"+str(year)
        feat_to_line=workspace2+"net_"+str(year)
        print "it's all good man"

# merge all dataset (this is not exactly what DH do)

        arcpy.Merge_management(infeatures, merge)
        print  "merge done"

# Let us check that the splitting above did not alter  the quality of our lines and correct them
        arcpy.RepairGeometry_management(merge, "DELETE_NULL")
        print  "geometry repaired"

# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "centr_rail_Merge1"
#arcpy.ExtendLine_edit(merge, "", "EXTENSION")
#print "extend line done" 


# Feature to line allows us to split the different line shapefiles in segments for each line crossing [improvement from DH]
        arcpy.FeatureToLine_management(merge, feat_to_line, "", "ATTRIBUTES")
        print  "feature to line done"

        database_creation = timeit.timeit()
        print  database_creation - start

# Let us check that the splitting above did not alter  the quality of our lines and correct them
        arcpy.RepairGeometry_management(feat_to_line, "DELETE_NULL")
        print  "geometry repaired"

        arcpy.AddField_management(feat_to_line, "Length", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print  "generate Length field centroids done"

        arcpy.CalculateField_management(feat_to_line, "Length", "!shape.geodesicLength@KILOMETERS!", "PYTHON_9.3", "")
        print  "calculate length in kilometers"

        arcpy.AddField_management(feat_to_line, "cost_hd", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print  "generate Length field centroids done"

        arcpy.CalculateField_management(feat_to_line, "cost_hd", "([Length]*[Parameter])/1609.344",  "VB", "")
        print  "calculate length in kilometers"


#####################################################################################################
#####################################################################################################
#####################################################################################################
# 6) copy the final raw network into the database for network analysis
#####################################################################################################
#####################################################################################################
#####################################################################################################

        geodatabase=workspace1+feature_dataset

        in_features=centr_to_centr+";"+feat_to_line+";"+rail70+";"+rail90+";"+cent_rail70+";"+cent_rail90

        arcpy.FeatureClassToGeodatabase_conversion(in_features, geodatabase)
        print "feature to geodatabase"

except Exception as e:
    # If an error occurred, print line number and error message
    import traceback, sys
    tb = sys.exc_info()[2]
    print "An error occured on line %i" % tb.tb_lineno
    print str(e)


print "the network is ready to be constructed"


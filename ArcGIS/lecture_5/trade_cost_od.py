# Name: Network analysis application to DH in Missouri
# Description: Find the network of connected centroids in 1870 and 1890
#              and calculate statistics at the county level
# Requirements: Spatial and Network Analyst Extension 
# Author: Giorgio Chiovelli


#Import arcpy module
import arcpy
from arcpy import env
import os
import csv

#Turn overwrite on
arcpy.CheckOutExtension("spatial")
arcpy.CheckOutExtension("network")
arcpy.env.overwriteOutput = True

print "overwrite on"

directory="C:/Users/se.4537/Dropbox/PoliteconGIS/Bonn_2019/Lecture 5/GIS data/_workflow2/"
folder=directory+"trade_cost/"

workspace=directory+"dh.gdb/dh_class"
workspace2=directory+"modified.gdb/"


# Define a worspace
arcpy.env.workspace=workspace
# Set the local variables
 
# note: the two network datasets have to be called dh_1870 and dh_1890
try:
    

    year=['1870','1890']

    print "list ok"
    
    for year in year:
        networkdataset = workspace+"/dh_"+str(year)
        odname="dh"+year
        centroids=directory+"/centroids_p.shp"
        border=directory+"/border_p.shp"
        
        name="cost_dh_"+year

        out_k_routes=workspace2+"solve_"+str(year)
        csv=os.path.join(folder, name + ".txt")
        
    
    #defining elements for closest facilities
        impedanceAttribute = "cost_hd"
        


    
    


    # Create a OD Matrix

        layer=arcpy.MakeODCostMatrixLayer_na(networkdataset, odname, "cost_hd", "", "", "", "ALLOW_UTURNS", "", "NO_HIERARCHY", "", "STRAIGHT_LINES", "").getOutput(0)
        print odname + "OD matrix done done"

    # Load centroids as Origins 

        arcpy.AddLocations_na(layer, "Origins", centroids, "", "5000 Meters", "")

        print odname + "add origins done"

    # Load centroids as Destinations

        arcpy.AddLocations_na(layer, "Destinations", centroids, "", "5000 Meters", "")
        print odname +  "add destination done"



        # Imposing the border as uncrossable obstacle
        na_classes = arcpy.na.GetNAClassNames(layer, "INPUT")

        
        field_mappings = arcpy.na.NAClassFieldMappings(layer, na_classes["PolylineBarriers"])
        field_mappings["BarrierType"].defaultValue = 0 ## This is the value for restriction
        field_mappings["Attr_" + impedanceAttribute].defaultValue = 1

        arcpy.na.AddLocations(layer, "Line Barriers", border, field_mappings)
        print "border as barrier" + year + "done"

        
        


        

        
    # Solve for Best routes    
        solve=arcpy.na.Solve(layer,"SKIP","CONTINUE","#")
        print odname +  "solution for best route found"
    # Solve is stored as temporary file. To work with it we need to save it
    # Let us select the object from the list of layers
        routes_solved = arcpy.mapping.ListLayers(layer, "Lines")[0]
        print odname +  "solution for best route found"
    # Now copy the layer as a shapefile. This would make a permanent copy of the best route solution
        arcpy.CopyFeatures_management(routes_solved, out_k_routes)
        print "copy of solve done"



        

# Now let us export the results to csv format. The command below is better than "table to excel" to handle huge dataset.

        arcpy.ExportXYv_stats(out_k_routes, "OriginID;DestinationID;Total_cost_hd", "SEMI-COLON", csv, "ADD_FIELD_NAMES")
        print "csv"  + "created" 

    
    
    
        
        print "Script completed successfully"

except Exception as e:
    # If an error occurred, print line number and error message
    import traceback, sys
    tb = sys.exc_info()[2]
    print "An error occured on line %i" % tb.tb_lineno
    print str(e)



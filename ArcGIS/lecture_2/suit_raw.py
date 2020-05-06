# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# suit_raw2.py
# Created on: 2018-11-06 01:30:05.00000
#   (generated by ArcGIS/ModelBuilder)
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy


# Local variables:
USA_adm2_shp = "C:\\Users\\se.4537\\Dropbox\\PoliteconGIS\\Montreal\\Lecture 1\\GIS data\\USA_adm_shp\\USA_adm2.shp"
counties_shp = "C:\\Users\\se.4537\\Dropbox\\PoliteconGIS\\Montreal\\Lecture 1\\GIS data\\_output\\counties.shp"
counties_shp__2_ = counties_shp
counties_shp__3_ = counties_shp__2_
counties_shp__4_ = counties_shp__3_
suit = "C:\\Users\\se.4537\\Dropbox\\PoliteconGIS\\Montreal\\Lecture 1\\GIS data\\suit\\suit"
agrisuit_tif = "C:\\Users\\se.4537\\Dropbox\\PoliteconGIS\\Montreal\\Lecture 1\\GIS data\\_output\\agrisuit.tif"
agrisuit_rs_tif = "C:\\Users\\se.4537\\Dropbox\\PoliteconGIS\\Montreal\\Lecture 1\\GIS data\\_output\\agrisuit_rs.tif"
zs_dbf = "C:\\Users\\se.4537\\Dropbox\\PoliteconGIS\\Montreal\\Lecture 1\\GIS data\\_output\\zs.dbf"
zs_csv = zs_dbf
v_output = "C:\\Users\\se.4537\\Dropbox\\PoliteconGIS\\Montreal\\Lecture 1\\GIS data\\_output"

# Process: Copy Features
arcpy.CopyFeatures_management(USA_adm2_shp, counties_shp, "", "0", "0", "0")

# Process: Delete Field
arcpy.DeleteField_management(counties_shp, "ID_0;ISO;NAME_0;ID_1;ID_2;HASC_2;CCN_2;CCA_2;TYPE_2;ENGTYPE_2;NL_NAME_2;VARNAME_2")

# Process: Add Field
arcpy.AddField_management(counties_shp__2_, "cid", "SHORT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field
arcpy.CalculateField_management(counties_shp__3_, "cid", "!FID!+1", "PYTHON_9.3", "")

# Process: Copy Raster
arcpy.CopyRaster_management(suit, agrisuit_tif, "", "", "-3.402823e+38", "NONE", "NONE", "", "NONE", "NONE", "TIFF", "NONE")

# Process: Resample
arcpy.Resample_management(agrisuit_tif, agrisuit_rs_tif, "2 2", "NEAREST")

# Process: Zonal Statistics as Table
arcpy.gp.ZonalStatisticsAsTable_sa(counties_shp__4_, "cid", agrisuit_rs_tif, zs_dbf, "DATA", "MEAN")

# Process: Table to Table
arcpy.TableToTable_conversion(zs_dbf, v_output, "zs.csv", "", "cid \"cid\" true true false 0 Text 0 0 ,First,#,C:\\Users\\se.4537\\Dropbox\\PoliteconGIS\\Montreal\\Lecture 1\\GIS data\\_output\\zs.dbf,cid,-1,-1;MEAN \"MEAN\" true true false 0 Double 0 0 ,First,#,C:\\Users\\se.4537\\Dropbox\\PoliteconGIS\\Montreal\\Lecture 1\\GIS data\\_output\\zs.dbf,MEAN,-1,-1", "")

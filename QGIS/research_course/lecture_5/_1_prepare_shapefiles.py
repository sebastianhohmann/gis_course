#########################################################################################
#########################################################################################
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
# print('preliminary setup')
# import sys
# import os

# from qgis.core import (
#     QgsApplication,
#     QgsCoordinateReferenceSystem
# )

# from qgis.analysis import QgsNativeAlgorithms

# # See https://gis.stackexchange.com/a/155852/4972 for details about the prefix 
# QgsApplication.setPrefixPath('C:/OSGeo4W64/apps/qgis', True)
# qgs = QgsApplication([], False)
# qgs.initQgis()

# # Add the path to Processing framework  
# sys.path.append('C:/OSGeo4W64/apps/qgis/python/plugins')

# # Import and initialize Processing framework
# import processing
# from processing.core.Processing import Processing
# Processing.initialize()
# QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
#########################################################################################
#########################################################################################

import sys
sys.path.append('C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_5')

from geoprocess import GeoProcess

# set paths to inputs and outputs
# mainpath = "C:/Users/giorg/Dropbox (LBS Col_con)/PoliteconGIS/LBS_2020/PhD/lecture_5/gis_data"
mainpath = "C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_5/gis_data"
outpath = "{}/_output".format(mainpath)
junkpath = "{}/junk".format(outpath)

counties = "{}/missouri_p.shp".format(mainpath)
rail70 = "{}/rail1870_p.shp".format(mainpath)
rail90 = "{}/rail1890_p.shp".format(mainpath)
rivers = "{}/SteamboatNavigatedRivers.shp".format(mainpath)


from_centroids70 = "{}/from_centroids70.shp".format(junkpath)
distance_centroids70 = "{}/distance_centroids70.shp".format(junkpath)
from_centroids90 = "{}/from_centroids90.shp".format(junkpath)
distance_centroids90 = "{}/distance_centroids90.shp".format(junkpath)
t1 = "{}/_test1.shp".format(junkpath)
t2 = "{}/_test2.shp".format(junkpath)
out70 = "{}/lines_for_network_1870.shp".format(outpath)
out90 = "{}/lines_for_network_1890.shp".format(outpath)
outcent = "{}/county_centroids.shp".format(outpath)

if not os.path.exists(junkpath):
    os.mkdir(junkpath)

gp = GeoProcess()


###########################################################################
###########################################################################
###########################################################################

######################################################################
# reproject rivers, rail, and counties to WGS84
######################################################################
print('reprojecting rivers, rail, and counties to WGS84')
rail70wgs84 = gp.reproject_layer(rail70, 'EPSG:4326')
rail90wgs84 = gp.reproject_layer(rail90, 'EPSG:4326')
riverswgs84 = gp.reproject_layer(rivers, 'EPSG:4326')
countieswgs84 = gp.reproject_layer(counties, 'EPSG:4326')

######################################################################
# county centroids
######################################################################
print('finding county centroids')
centroids = gp.centroids(countieswgs84)

######################################################################
# adding indicators and dropping unnecessary fields
######################################################################
print('adding indicators')
rail70wgs84 = gp.add_constant_field(rail70wgs84, 'rail', 1)
rail90wgs84 = gp.add_constant_field(rail90wgs84, 'rail', 1)
riverswgs84 = gp.add_constant_field(riverswgs84, 'river', 1)
centroids = gp.add_constant_field(centroids, 'centroids', 1)

print('dropping unnecessary fields')
rail70wgs84 = gp.drop_fields(rail70wgs84, keep_fields=['rail'])
rail90wgs84 = gp.drop_fields(rail90wgs84, keep_fields=['rail'])
riverswgs84 = gp.drop_fields(riverswgs84, keep_fields=['river'])
centroids = gp.drop_fields(centroids, keep_fields=['centroids'])

######################################################################
# splitting with lines, snapping and unioning rivers and rail
######################################################################
print('splitting with lines, snapping and unioning rivers and rail')
rail70_split_rivers = gp.split_with_lines(rail70wgs84, riverswgs84)
rail90_split_rivers = gp.split_with_lines(rail90wgs84, riverswgs84)
rivers_split_rail70 = gp.split_with_lines(riverswgs84, rail70wgs84)
rivers_split_rail90 = gp.split_with_lines(riverswgs84, rail90wgs84)

rail70_snap_rivers = gp.snap_geometries(rail70_split_rivers, rivers_split_rail70, 0.01)
rail90_snap_rivers = gp.snap_geometries(rail90_split_rivers, rivers_split_rail90, 0.01)

rivers_split_rail70 = gp.fix_geometry(rivers_split_rail70)
rivers_split_rail90 = gp.fix_geometry(rivers_split_rail90)
rail70_snap_rivers = gp.fix_geometry(rail70_snap_rivers)
rail90_snap_rivers = gp.fix_geometry(rail90_snap_rivers)

rivers_split_rail70 = gp.multipart_to_singleparts(rivers_split_rail70)
rivers_split_rail90 = gp.multipart_to_singleparts(rivers_split_rail90)
rail70_snap_rivers = gp.multipart_to_singleparts(rail70_snap_rivers)
rail90_snap_rivers = gp.multipart_to_singleparts(rail90_snap_rivers)

union_railriver70 = gp.union(rivers_split_rail70, rail70_snap_rivers)
union_railriver90 = gp.union(rivers_split_rail90, rail90_snap_rivers)

######################################################################
# creating connector pieces, snapping, splitting and unioning
######################################################################
print('creating connector pieces, snapping, splitting and unioning, 1870')
gp.grass_v_distance(centroids, union_railriver70, 'centroids',
                    from_out=from_centroids70, dist_out=distance_centroids70)
connectors70 = gp.snap_geometries(distance_centroids70, union_railriver70, 0.01)
connectors70 = gp.fix_geometry(connectors70)
union_railriver70 = gp.fix_geometry(union_railriver70)
connectors70 = gp.multipart_to_singleparts(connectors70)
union_railriver70 = gp.multipart_to_singleparts(union_railriver70)
railrivers_split_connectors70 = gp.split_with_lines(union_railriver70, connectors70)
connectors_split_railrivers70 = gp.split_with_lines(connectors70, union_railriver70)
railrivers_split_connectors70 = gp.fix_geometry(railrivers_split_connectors70)
connectors_split_railrivers70 = gp.fix_geometry(connectors_split_railrivers70)
railrivers_split_connectors70 = gp.multipart_to_singleparts(railrivers_split_connectors70)
connectors_split_railrivers70 = gp.multipart_to_singleparts(connectors_split_railrivers70)
union70 = gp.union(connectors70, union_railriver70)

print('creating connector pieces, snapping, splitting and unioning, 1890')
gp.grass_v_distance(centroids, union_railriver90, 'centroids',
                    from_out=from_centroids90, dist_out=distance_centroids90)
connectors90 = gp.snap_geometries(distance_centroids90, union_railriver90, 0.01)
connectors90 = gp.fix_geometry(connectors90)
union_railriver90 = gp.fix_geometry(union_railriver90)
connectors90 = gp.multipart_to_singleparts(connectors90)
union_railriver90 = gp.multipart_to_singleparts(union_railriver90)
railrivers_split_connectors90 = gp.split_with_lines(union_railriver90, connectors90)
connectors_split_railrivers90 = gp.split_with_lines(connectors90, union_railriver90)
railrivers_split_connectors90 = gp.fix_geometry(railrivers_split_connectors90)
connectors_split_railrivers90 = gp.fix_geometry(connectors_split_railrivers90)
railrivers_split_connectors90 = gp.multipart_to_singleparts(railrivers_split_connectors90)
connectors_split_railrivers90 = gp.multipart_to_singleparts(connectors_split_railrivers90)
union90 = gp.union(connectors90, union_railriver90)


######################################################################
# re-projecting and calculating length of all pieces
######################################################################
print('reprojecting and calculating lengths')
union70 = gp.reproject_layer(union70, 'ESRI:102003')
union90 = gp.reproject_layer(union90, 'ESRI:102003')
union70 = gp.fix_geometry(union70)
union90 = gp.fix_geometry(union90)
union70 = gp.add_length_attribute(union70, 'len_km', field_precision=6)
union90 = gp.add_length_attribute(union90, 'len_km', field_precision=6)

formula = '''CASE
 WHEN ("cat" IS NOT NULL) AND ("river" IS NULL) AND ("rail" IS NULL) THEN 'trail'
 WHEN ("rail" = 1) AND ("river" IS NULL) THEN 'rail'
 WHEN ("river" = 1) THEN 'river'
END
'''
union70 = gp.generic_field_calculator(union70, 'type', 'str', formula)
union90 = gp.generic_field_calculator(union90, 'type', 'str', formula)

######################################################################
# calculating costs and final cleanup
######################################################################
print('calculating costs and final cleanup')
miles_per_km=0.6213712
dollars_per_mile_rail=0.0063
dollars_per_mile_river=0.0049
dollars_per_mile_trail=0.231
formula = '''CASE
 WHEN ("type" = 'trail') THEN "len_km"*{}
 WHEN ("type" = 'river') THEN "len_km"*{}
 WHEN ("type" = 'rail') THEN "len_km"*{}
END
'''.format(miles_per_km*dollars_per_mile_trail,
		   miles_per_km*dollars_per_mile_river,
		   miles_per_km*dollars_per_mile_rail)
union70 = gp.generic_field_calculator(union70, 'cost', 'float', formula, field_precision=6)
union90 = gp.generic_field_calculator(union90, 'cost', 'float', formula, field_precision=6)

################################################################
# QNEAT3 needs "speed", it does not handle "cost"
################################################################
# to calculate speed that, observe that
# cost_of_distance = length*cost_per_length
# time = length*time_per_length
# time = length/speed
# => speed = 1/time_per_length
# now equate time = cost
# length*cost_per_length = length*time_per_length
# cost_per_length = time_per_length
# cost_per_length = 1/speed
# speed = 1/cost_per_length
# note that we can do this since the gravity model does not care about units

formula = '''CASE
 WHEN ("type" = 'trail') THEN {}
 WHEN ("type" = 'river') THEN {}
 WHEN ("type" = 'rail') THEN {}
END 
'''.format(1/(miles_per_km*dollars_per_mile_trail),
		   1/(miles_per_km*dollars_per_mile_river),
		   1/(miles_per_km*dollars_per_mile_rail))
union70 = gp.generic_field_calculator(union70, 'speed', 'float', formula, field_precision=6)
union90 = gp.generic_field_calculator(union90, 'speed', 'float', formula, field_precision=6)

gp.drop_fields(union70, keep_fields=['len_km', 'type', 'cost', 'speed'], output_object=out70)
gp.drop_fields(union90, keep_fields=['len_km', 'type', 'cost', 'speed'], output_object=out90)

######################################################################
# making a copy of the centroids in the right projection 
######################################################################
print('making a copy of the centroids in the right projection ')

counties = gp.reproject_layer(counties, 'ESRI:102003')
centroids = gp.centroids(counties)
gp.drop_fields(centroids, keep_fields=['NHGISNAM'], output_object=outcent)


print('DONE!')











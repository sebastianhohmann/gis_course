wdir = 'C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/MBA/lecture_3/_workflow_2'
demand_in = '{}/_demand_points_census.shp'.format(wdir)
shops_in = '{}/candidate_shops.shp'.format(wdir)
shops_isochrones = '{}/shops_isochrones.shp'.format(wdir)
shops_isochrones_output = '{}/shops_isochrones_demand.csv'.format(wdir)

##################################
# Isochrones From Layer
##################################
print('Running Isochrones from layer')
alg_params = {
    'INPUT_FIELD': 'shopID',
    'INPUT_METRIC': 0,
    'INPUT_POINT_LAYER': shops_in,
    'INPUT_PROFILE': 7,
    'INPUT_PROVIDER': 0,
    'INPUT_RANGES': '1,2,3,5,10,15,20,25,30',
    'OUTPUT': shops_isochrones
}
processing.run('ORS Tools:isochrones_from_layer', alg_params)

##################################
# Join attributes by location
##################################
print('Joining isochrones to demand points')
alg_params = {
    'DISCARD_NONMATCHING': True,
    'JOIN': shops_isochrones,
    'INPUT': demand_in,
    'JOIN_FIELDS': [''],
    'METHOD': 0,
    'PREDICATE': [0],
    'PREFIX': '_',
    'OUTPUT': 'memory:'
}
shops_joined_isochrones = processing.run('native:joinattributesbylocation', alg_params)['OUTPUT']

##################################
# Drop field(s)
##################################
print('Dropping unnecessary fields from the location join')
all_fields = [field.name() for field in shops_joined_isochrones.fields()]
keep_fields = ['LSOA11NM', 'pop2011_al', '_shopID', '_AA_MINS']
drop_fields = [field for field in all_fields if field not in keep_fields]

alg_params = {
    'COLUMN': drop_fields,
    'INPUT': shops_joined_isochrones,
    'OUTPUT': 'memory:'
}
drop_fields = processing.run('qgis:deletecolumn', alg_params)['OUTPUT']

##################################
# Refactor fields
##################################
print('Refactoring fields')
alg_params = {
    'FIELDS_MAPPING': [{'expression': '"LSOA11NM"',
                        'length': 40,
                        'name': 'LSOA11NM',
                        'precision': 0,
                        'type': 10},
                       {'expression': '"pop2011_al"',
                        'length': 254,
                        'name': 'pop2011_al', 
                        'precision': 0, 
                        'type': 4}, 
                       {'expression': '"_shopID"', 
                        'length': 254, 
                        'name': '_shopID', 
                        'precision': 0, 
                        'type': 2}, 
                       {'expression': '"_AA_MINS"', 
                        'length': 10, 
                        'name': '_AA_MINS', 
                        'precision': 0, 
                        'type': 2}],
    'INPUT': drop_fields,
    'OUTPUT': 'memory:'
}
refactor_fields = processing.run('qgis:refactorfields', alg_params)['OUTPUT']

##################################
# Field calculator
##################################
print('Creating new field: shop-time-id')
alg_params = {
    'FIELD_LENGTH': 10,
    'FIELD_NAME': 'shop_t_id',
    'FIELD_PRECISION': 3,
    'FIELD_TYPE': 2,
    'FORMULA': 'tostring(_shopID) + \'_\' +  tostring(_AA_MINS)',
    'INPUT': refactor_fields,
    'NEW_FIELD': True,
    'OUTPUT': 'memory:'
}
field_calc = processing.run('qgis:fieldcalculator', alg_params)['OUTPUT']

##################################
# Field calculator
##################################
print('Creating new field: total demand by shop-time-id')
alg_params = {
    'FIELD_LENGTH': 10,
    'FIELD_NAME': 'total',
    'FIELD_PRECISION': 3,
    'FIELD_TYPE': 1,
    'FORMULA': ' sum(\"pop2011_al\",group_by:=\"shop_t_id\")',
    'INPUT': field_calc,
    'NEW_FIELD': True,
    'OUTPUT': 'memory:'
}
field_calc = processing.run('qgis:fieldcalculator', alg_params)['OUTPUT']

##################################
# Delete duplicates by attribute
##################################
print('Dropping duplicates by shop-time-id')
alg_params = {
    'FIELDS': 'shop_t_id',
    'INPUT': field_calc,
    'OUTPUT': 'memory:'
}
delete_dups_byattr = processing.run('native:removeduplicatesbyattribute', alg_params)['OUTPUT']

##################################
# Drop field(s)
##################################
print('Dropping unnecessary fields and saving final output')
all_fields = [field.name() for field in delete_dups_byattr.fields()]
keep_fields = ['_shopID', '_AA_MINS', 'total']
drop_fields = [field for field in all_fields if field not in keep_fields]
alg_params = {
    'COLUMN': drop_fields,
    'INPUT': delete_dups_byattr,
    'OUTPUT': shops_isochrones_output
}
processing.run('qgis:deletecolumn', alg_params)

print('DONE!')
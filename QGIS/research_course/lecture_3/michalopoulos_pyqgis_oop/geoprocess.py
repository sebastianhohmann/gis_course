#########################################################################################
#########################################################################################
# SETUP PREAMBLE FOR RUNNING STANDALONE SCRIPTS.
# NOT NECESSARY IF YOU ARE RUNNING THIS INSIDE THE QGIS GUI.
print('preliminary setup')
import sys
import os

from qgis.core import (
    QgsApplication, 
    QgsVectorLayer,
    QgsCoordinateReferenceSystem
)

from qgis.analysis import QgsNativeAlgorithms

# See https://gis.stackexchange.com/a/155852/4972 for details about the prefix 
QgsApplication.setPrefixPath('C:/OSGeo4W64/apps/qgis', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Add the path to Processing framework  
sys.path.append('C:/OSGeo4W64/apps/qgis/python/plugins')

# Import and initialize Processing framework
import processing
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
#########################################################################################
#########################################################################################

class GeoProcess(object):

	'''
	class with wrapper methods to shorten
	the writing of pyqgis geoprocessing code

	(c) 2020, Giorgio Chiovelli and Sebastian Hohmann  
	'''

	def __init__(self):
		pass

	def fix_geometry(self, input_object, output_object='memory:'):
		alg_params = {
			'INPUT': input_object,
			'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('native:fixgeometries', alg_params)['OUTPUT']
		else:
			processing.run('native:fixgeometries', alg_params)


	def add_autoincremental_id(self, input_object, id_field_name, output_object='memory:'):
		alg_params = {
		    'FIELD_NAME': id_field_name,
		    'GROUP_FIELDS': None,
		    'INPUT': input_object,
		    'SORT_ASCENDING': True,
		    'SORT_EXPRESSION': '',
		    'SORT_NULLS_FIRST': False,
		    'START': 1,
		    'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('native:addautoincrementalfield', alg_params)['OUTPUT'] 
		else:
			processing.run('native:addautoincrementalfield', alg_params)


	def drop_fields(self, input_object, drop_fields=None, keep_fields=None, output_object='memory:'):

		'''
		drop_fields can be called in two ways
		1) listing the fields to keep
		2) listing the fields to drop
		'''

		lyr = self.make_vector_layer(input_object)

		if keep_fields:
			all_fields = [field.name() for field in lyr.fields()]
			drop_fields = [field for field in all_fields if field not in keep_fields]

		alg_params = {
		   'COLUMN': drop_fields,
		   'INPUT': input_object,
		   'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('qgis:deletecolumn', alg_params)['OUTPUT'] 
		else:
			processing.run('qgis:deletecolumn', alg_params)



	def make_vector_layer(self, input_object):

		input_type = str(type(input_object))
		if 'QgsVectorLayer' in input_type:
			return input_object
		else:
			return QgsVectorLayer(input_object, 'ogr')


	def return_field_info(self, input_object, field_name):

		lyr = self.make_vector_layer(input_object)

		field_type_names = {}
		field_precisions = {}
		field_lengths = {}
		for field in lyr.fields():
			field_type_names[field.name()] = field.typeName()
			field_precisions[field.name()] = field.precision()
			field_lengths[field.name()] = field.length()
		field_type_name = field_type_names[field_name]
		field_precision = field_precisions[field_name]
		field_length = field_lengths[field_name]
		if field_type_name == 'double':
			field_type_name = 'float'
		field_types = {'float': 0, 'integer': 1, 'string': 2, 'date': 3}
		field_type = field_types[field_type_name.lower()] 

		return {'field_type_name': field_type_name,
				'field_precision': field_precision,
				'field_length': field_length,
				'field_type': field_type}

	def copy_attribute(self, input_object, old_attribute_name, new_attribute_name, output_object='memory:'):

		field_info = self.return_field_info(input_object, old_attribute_name)
		field_length = field_info['field_length']
		field_precision = field_info['field_precision']
		field_type = field_info['field_type']

		alg_params = {
		    'FIELD_LENGTH': field_length,
		    'FIELD_NAME': new_attribute_name,
		    'FIELD_PRECISION': field_precision,
		    'FIELD_TYPE': field_type,
		    'FORMULA': ' attribute($currentfeature, \'{}\')'.format(old_attribute_name),
		    'INPUT': input_object,
		    'NEW_FIELD': True,
		    'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('qgis:fieldcalculator', alg_params)['OUTPUT'] 
		else:
			processing.run('qgis:fieldcalculator', alg_params)


	def define_crs(self, crs_string_name):
		return QgsCoordinateReferenceSystem(crs_string_name)


	def reproject_layer(self, input_object, crs_string_name, output_object='memory:'):

		crs = self.define_crs(crs_string_name)

		alg_params = {
			'INPUT': input_object,
			'OPERATION': '',
			'TARGET_CRS': crs,
			'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('native:reprojectlayer', alg_params)['OUTPUT'] 
		else:
			processing.run('native:reprojectlayer', alg_params)


	def define_projection_for_raster(self, input_object, crs_string_name, output_object):

		'''
		define a crs for a raster without a crs
		uses gdal:warpreproject and so requires specifying an output
		then uses gdal:extracprojection to write the .prj file
		'''

		crs = self.define_crs(crs_string_name)
		alg_params = {
		    'DATA_TYPE': 0,
		    'EXTRA': '',
		    'INPUT': input_object,
		    'MULTITHREADING': False,
		    'NODATA': None,
		    'OPTIONS': '',
		    'RESAMPLING': 0,
		    'SOURCE_CRS': None,
		    'TARGET_CRS': crs,
		    'TARGET_EXTENT': None,
		    'TARGET_EXTENT_CRS': None,
		    'TARGET_RESOLUTION': None,
		    'OUTPUT': output_object
		}
		processing.run('gdal:warpreproject', alg_params)

		alg_params = {
		    'INPUT': output_object,
		    'PRJ_FILE_CREATE': True
		}
		processing.run('gdal:extractprojection', alg_params)


	def output_csv(self, input_object, csv_path):

		lyr = self.make_vector_layer(input_object)

		with open(csv_path, 'w') as output_file:
		    fieldnames = [field.name() for field in lyr.fields()]
		    line = ','.join(name for name in fieldnames) + '\n'
		    output_file.write(line)
		    for f in lyr.getFeatures():
		        line = ','.join(str(f[name]) for name in fieldnames) + '\n'
		        output_file.write(line)


	def zonal_statistics_as_csv(self, zones, raster_list, column_prefix_list, statistics_list, csv_path, verbose=True):

		available_stats = {
			'count': 0, 'sum': 1, 'mean': 2, 'median': 3,
			'std': 4, 'min': 5, 'max': 6, 'range': 7,
			'minority': 8, 'majority': 9, 'variety': 10,  'variance': 11
		}

		stats_to_compute = [available_stats[stat] for stat in statistics_list]

		for idr, raster in enumerate(raster_list):

			prefix = column_prefix_list[idr]
			if verbose:
				print('computing zonal statistics for {}'.format(prefix))
			
			alg_params = {
			    'COLUMN_PREFIX': prefix,
			    'INPUT_RASTER': raster,
			    'INPUT_VECTOR': zones,
			    'RASTER_BAND': 1,
			    'STATS': stats_to_compute
			}
			processing.run('qgis:zonalstatistics', alg_params)

		print('writing to csv')
		self.output_csv(zones, csv_path)


	def intersect_native(self,
						 input_object, overlay_object,
						 input_fields_to_keep=None, overlay_fields_to_keep=None,
						 output_object='memory:'):

		alg_params = {
		    'INPUT': input_object,
		    'INPUT_FIELDS': input_fields_to_keep,
		    'OVERLAY': overlay_object,
		    'OVERLAY_FIELDS': overlay_fields_to_keep,
		    'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('native:intersection', alg_params)['OUTPUT'] 
		else:
			processing.run('native:intersection', alg_params)


	def statistics_by_categories(self, input_object,
								 categories_field_name, values_field_name=None,
								 output_object='memory:'):
		alg_params = {
		    'CATEGORIES_FIELD_NAME': categories_field_name,
		    'INPUT': input_object,
		    'VALUES_FIELD_NAME': values_field_name,
		    'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('qgis:statisticsbycategories', alg_params)['OUTPUT'] 
		else:
			processing.run('qgis:statisticsbycategories', alg_params)



	def centroids(self, input_object, all_parts=False, output_object='memory:'):

		alg_params = {
		    'ALL_PARTS': all_parts,
		    'INPUT': input_object,
		    'OUTPUT': output_object
		}

		if output_object=='memory:':
			return processing.run('native:centroids', alg_params)['OUTPUT'] 
		else:
			processing.run('native:centroids', alg_params)


	def add_xycoordinates(self, input_object, output_object='memory:'):

		alg_params = {
		    'CALC_METHOD': 2,
		    'INPUT': input_object,
		    'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('qgis:exportaddgeometrycolumns', alg_params)['OUTPUT'] 
		else:
			processing.run('qgis:exportaddgeometrycolumns', alg_params)		


	def multipart_to_singleparts(self, input_object, output_object='memory:'):
		alg_params = {
		    'INPUT': input_object,
		    'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('native:multiparttosingleparts', alg_params)['OUTPUT'] 
		else:
			processing.run('native:multiparttosingleparts', alg_params)	


	def grass_v_distance(self, from_object, to_object,
						 upload_column, from_type=0, to_type=1,
						 from_out=False, dist_out=False):

		'''
		method creates new line segments from a from_object to a to_object
		by default, assumes from_object are points and to_object are lines.
		see grass7:v.distance api documentation for other options. 
		must specify shapefile paths for from_out and dist_out, otherwise error
		'''

		if not from_out or not dist_out:
			raise RuntimeError('You must specify from_out and dist_out')

		alg_params = {
		    'from': from_object,
		    'from_type': [from_type],
		    'to': to_object,
		    'to_type': [to_type],
		    'dmax': -1,
		    'dmin': -1,
		    'upload': [1],
		    'column': [upload_column],
		    'to_column': None,
		    'from_output': from_out,
		    'output': dist_out,
		    'GRASS_REGION_PARAMETER': None,
		    'GRASS_SNAP_TOLERANCE_PARAMETER': -1,
		    'GRASS_MIN_AREA_PARAMETER': 0.0001,
		    'GRASS_OUTPUT_TYPE_PARAMETER': 0,
		    'GRASS_VECTOR_DSCO': '',
		    'GRASS_VECTOR_LCO': '',
		    'GRASS_VECTOR_EXPORT_NOCAT': False
		}

		processing.run('grass7:v.distance', alg_params)


	def add_constant_to_attribute(self, input_object, attribute_name, constant, output_object='memory:'):

		field_info = self.return_field_info(input_object, attribute_name)
		field_length = field_info['field_length']
		field_precision = field_info['field_precision']
		field_type = field_info['field_type']

		alg_params = {
		    'FIELD_LENGTH': field_length,
		    'FIELD_NAME': attribute_name,
		    'FIELD_PRECISION': field_precision,
		    'FIELD_TYPE': field_type,
		    'FORMULA': 'attribute($currentfeature, \'{}\')+{}'.format(attribute_name, constant),
		    'INPUT': input_object,
		    'NEW_FIELD': False,
		    'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('qgis:fieldcalculator', alg_params)['OUTPUT'] 
		else:
			processing.run('qgis:fieldcalculator', alg_params)	


	def add_constant_field(self, input_object, attribute_name, constant_value, output_object='memory:'):

		if 'int' in str(type(constant_value)):
			field_type = 1
			field_len = 10
		elif 'float' in str(type(constant_value)) or 'double' in str(type(constant_value)):
			field_type = 0
			field_len = 10
		elif 'str' in str(type(constant_value)):
			field_type = 2
			field_len = len(constant_value)

		alg_params = {
			'FIELD_LENGTH': field_len,
			'FIELD_NAME': attribute_name,
			'FIELD_PRECISION': 3,
			'FIELD_TYPE': field_type,
			'FORMULA': '{}'.format(constant_value),
			'INPUT': input_object,
			'NEW_FIELD': True,
			'OUTPUT': output_object
		}

		if output_object=='memory:':
			return processing.run('qgis:fieldcalculator', alg_params)['OUTPUT'] 
		else:
			processing.run('qgis:fieldcalculator', alg_params)	


	def join_attributes_table(self, input_object, join_object, attribute_name, output_object='memory:'):

		'''
		does one-to-one matching and does not discard non-matching,
		change METHOD to 0 if you want one-to-many and
		DISCARD_NONMATCHING to True if you want to discard non-matching rows
		'''

		alg_params = {
		    'DISCARD_NONMATCHING': False,
		    'FIELD': attribute_name,
		    'FIELDS_TO_COPY': None,
		    'FIELD_2': attribute_name,
		    'INPUT': input_object,
		    'INPUT_2': join_object,
		    'METHOD': 1,
		    'PREFIX': '',
		    'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('native:joinattributestable', alg_params)['OUTPUT'] 
		else:
			processing.run('native:joinattributestable', alg_params)	


	def extract_vertices(self, input_object, output_object='memory:'):

		alg_params = {
		    'INPUT': input_object,
		    'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('native:extractvertices', alg_params)['OUTPUT'] 
		else:
			processing.run('native:extractvertices', alg_params)		


	def extract_by_attribute(self, input_object, field_name, operator_string, field_value, output_object='memory:'):

		operators = {'=': 0, 'neq': 1, '>': 2, 'geq': 3,
					 '<': 4, 'leq': 5, 'starts_with': 6, 'contains': 7,
					 'is_null': 8, 'is_not_null': 9, 'does_not_contain': 10}

		operator = operators[operator_string]
		field_value = '{}'.format(field_value)

		alg_params = {
		    'FIELD': field_name,
		    'INPUT': input_object,
		    'OPERATOR': operator,
		    'VALUE': field_value,
		    'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('native:extractbyattribute', alg_params)['OUTPUT'] 
		else:
			processing.run('native:extractbyattribute', alg_params)


	def split_with_lines(self, input_object, split_lines, output_object='memory:'):

		alg_params = {
			'INPUT': input_object,
			'LINES': split_lines,
			'OUTPUT': output_object
		}

		if output_object=='memory:':
			return processing.run('native:splitwithlines', alg_params)['OUTPUT'] 
		else:
			processing.run('native:splitwithlines', alg_params)


	def snap_geometries(self, input_object, reference_object, tolerance, output_object='memory:'):

		input_object = self.make_vector_layer(input_object)
		reference_object = self.make_vector_layer(reference_object)

		alg_params = {
			'BEHAVIOR': 0,
			'INPUT': input_object,
			'REFERENCE_LAYER': reference_object,
			'TOLERANCE': tolerance,
			'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('qgis:snapgeometries', alg_params)['OUTPUT'] 
		else:
			processing.run('qgis:snapgeometries', alg_params)


	def union(self, input_object, overlay_object, overlay_prefix='', output_object='memory:'):

		alg_params = {
            'INPUT': input_object,
            'OVERLAY': overlay_object,
            'OVERLAY_FIELDS_PREFIX': overlay_prefix,
            'OUTPUT': output_object
        }
		if output_object=='memory:':
			return processing.run('native:union', alg_params)['OUTPUT'] 
		else:
			processing.run('native:union', alg_params)


	def merge(self, input_list, output_object='memory:'):

		'''
		setting 'CRS': None means that take crs from first vector layer in list
		other vector layers will be reprojected to the same crs
		'''

		alg_params = {
			'CRS': None,
			'LAYERS': input_list,
			'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('native:mergevectorlayers', alg_params)['OUTPUT'] 
		else:
			processing.run('native:mergevectorlayers', alg_params)	

	def add_area_attribute(self, input_object, attribute_name, output_object='memory:'):

		alg_params = {
		    'FIELD_LENGTH': 10,
		    'FIELD_NAME': attribute_name,
		    'FIELD_PRECISION': 3,
		    'FIELD_TYPE': 0,
		    'FORMULA': 'area($geometry)/1000000',
		    'INPUT': input_object,
		    'NEW_FIELD': True,
		    'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('qgis:fieldcalculator', alg_params)['OUTPUT'] 
		else:
			processing.run('qgis:fieldcalculator', alg_params)

	def add_length_attribute(self, input_object, attribute_name, field_precision=3, output_object='memory:'):

		alg_params = {
		    'FIELD_LENGTH': 10,
		    'FIELD_NAME': attribute_name,
		    'FIELD_PRECISION': field_precision,
		    'FIELD_TYPE': 0,
		    'FORMULA': 'length($geometry)/1000',
		    'INPUT': input_object,
		    'NEW_FIELD': True,
		    'OUTPUT': output_object
		}
		if output_object=='memory:':
			return processing.run('qgis:fieldcalculator', alg_params)['OUTPUT'] 
		else:
			processing.run('qgis:fieldcalculator', alg_params)


	def generic_field_calculator(self, input_object, attribute_name,
	                             string_field_type, formula,
	                             field_precision=3, output_object='memory:'):

		if string_field_type=='float':
			field_type=0
		elif string_field_type=='int':
			field_type=1
		elif string_field_type=='str':
			field_type=2

		alg_params = {
		    'FIELD_LENGTH': 10,
		    'FIELD_NAME': attribute_name,
		    'FIELD_PRECISION': field_precision,
		    'FIELD_TYPE': field_type,
		    'FORMULA': formula,
		    'INPUT': input_object,
		    'NEW_FIELD': True,
		    'OUTPUT': output_object
		}

		if output_object=='memory:':
			return processing.run('qgis:fieldcalculator', alg_params)['OUTPUT'] 
		else:
			processing.run('qgis:fieldcalculator', alg_params)

	def find_closest_coordinates_from_points_to_lines(self, input_object, line_feature, intermediate_output_folder=None,
													  input_id=None, input_name=None, line_name=None, 	
													  verbose=True, output_object='memory:'):

		'''
		this meta-function returns a layer with five columns:
		- input_id: a feature uniquely identifying rows in the point-layer
		- input_lat: latitude of the input point feature
		- input_lon: longitude of the input point feature
		- line_lat: latitude of closest point on the line_feature
		- line_lon: longitude of the closest point on the line_feature 
		- the names of these can be changed through optional arguments
		'''

		if not input_id:
			raise RuntimeError('You must specify input_id')

		if not intermediate_output_folder:
			intermediate_output_folder = './'

		if not input_name:
			input_name = 'input'
		if not line_name:
			line_name = 'line'

		# Step 1: fixing geometry
		if verbose:
			print('fixing coordinates, {}'.format(input_name))
		points = self.fix_geometry(input_object)
		if verbose:
			print('fixing coordinates, {}'.format(line_name))
		lines = self.fix_geometry(line_feature)	

		# Step 2: dropping unnecessary fields from points and lines
		# and add xy-coords to points

		if verbose:
			print('fixing multi-part to singple parts problem, {}'.format(input_name))
		points = self.multipart_to_singleparts(points)
		if verbose:
			print('adding xy-coordinates, {}'.format(input_name))
		points = self.add_xycoordinates(points)
		if verbose:
			print('dropping unnecessary features, {}'.format(input_name))
		points = self.drop_fields(points, keep_fields=[input_id, 'xcoord', 'ycoord'])

		if verbose:
			print('dropping unnecessary features, {}'.format(line_name))
		first_line_field_name = [field.name() for field in lines.fields()][0][0]
		lines = self.drop_fields(lines, keep_fields=[first_line_field_name])

		# Step 3: running grass:v.distance
		if verbose:
			print('finding line segments with shortest distances to {}'.format(line_name))
		from_out_path = '{}/from_out.shp'.format(intermediate_output_folder)
		distance_out_path = '{}/distance_out.shp'.format(intermediate_output_folder)
		self.grass_v_distance(points, lines, 'xcoord',
                                 from_out=from_out_path, dist_out=distance_out_path)


		# step 4: cleaning up the from_out (the points) and merging with the original points
		if verbose:
			print('adjusting the "cat" column of the v.distance points for a lager merge')
		points_vdist = self.add_constant_to_attribute(from_out_path, 'cat', '-1')
		if verbose:
			print('removing ["xcoord", "ycoord"] from the v.distance points')
		points_vdist = self.drop_fields(points_vdist, drop_fields=['xcoord', 'ycoord'])
		if verbose: 
			print('joining v.distance points with the original points using column {}'.format(input_id))
		points = self.join_attributes_table(points, points_vdist, input_id)
		if verbose:
			print('removing the duplicate {} column'.format(input_id))
		keepfields=[input_id, 'xcoord', 'ycoord', 'cat']
		points = self.drop_fields(points, keep_fields=keepfields)


		# step 5: joining the cleaned points to the line segments, extract vertices from segments
		# and retain only those vertices located on the line feature on which we want to find the closest point
		if verbose:
			print('joining {} to line segments joining {} to closest {} using "cat"'.format(input_name, input_name, line_name))
		segments = self.join_attributes_table(distance_out_path, points, 'cat')	
		if verbose:
			print('extracting vertices from line segments')
		vertices = self.extract_vertices(segments)
		if verbose:
			print('retaining only the vertex on the {} for each {}'.format(line_name, input_name))
		vertices = self.extract_by_attribute(vertices, 'distance', '>', 0)


		# step 6: cleanup of point coordinates, adding closest point
		# coordinates and giving those a proper name as well
		if verbose:
			print('creating new field: {} latitude (keep field names straight)'.format(input_name))
		vertices = self.copy_attribute(vertices, 'ycoord', '{}_lat'.format(input_name))
		if verbose:
			print('creating new field: {} longitude (keep field names straight)'.format(input_name))		
		vertices = self.copy_attribute(vertices, 'xcoord', '{}_lon'.format(input_name))	
		if verbose:
			print('keeping only the fields {}, {}_lat, and {}_lon'.format(input_id, input_name, input_name))
		keepfields=[input_id, '{}_lat'.format(input_name), '{}_lon'.format(input_name)]
		vertices = self.drop_fields(vertices, keep_fields=keepfields)	

		if verbose:
			print('adding xy-coordinates to {} points'.format(line_name))
		vertices = self.add_xycoordinates(vertices)
		if verbose:
			print('creating new field: {} latitude (keep field names straight)'.format(line_name))
		vertices = self.copy_attribute(vertices, 'ycoord', '{}_lat'.format(line_name))
		if verbose:
			print('creating new field: {} longitude (keep field names straight)'.format(line_name))		
		vertices = self.copy_attribute(vertices, 'xcoord', '{}_lon'.format(line_name))	
		if verbose:
			print('dropping unnecessary fields and returning')
		dropfields=['xcoord', 'ycoord']
		return self.drop_fields(vertices, drop_fields=dropfields)


	def odmat_nn(self, network, points, id_field, tolerance=10, criterion='distance', speed_field=None, default_speed=None, output_object='memory:'):

		if criterion=='distance':
			strategy=0
		else:
			strategy=1

		alg_params = {
			'DEFAULT_DIRECTION': 2,
			'DEFAULT_SPEED': default_speed,
			'DIRECTION_FIELD': '',
			'ENTRY_COST_CALCULATION_METHOD': 1,
			'ID_FIELD': id_field,
			'INPUT': network,
			'POINTS': points,
			'SPEED_FIELD': speed_field,
			'STRATEGY': strategy,
			'TOLERANCE': tolerance,
			'VALUE_BACKWARD': '',
			'VALUE_BOTH': '',
			'VALUE_FORWARD': '',
			'OUTPUT': output_object
		}

		if output_object=='memory:':
			return processing.run('qneat3:OdMatrixFromPointsAsTable', alg_params)['OUTPUT'] 
		else:
			processing.run('qneat3:OdMatrixFromPointsAsTable', alg_params)






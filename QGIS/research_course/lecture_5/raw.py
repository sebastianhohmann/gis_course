"""
Model exported as python.
Name : model
Group : 
With QGIS : 31200
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Model(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSink('Test123', 'test123', type=QgsProcessing.TypeVectorLine, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # OD Matrix from Points as Table (n:n)
        alg_params = {
            'DEFAULT_DIRECTION': 2,
            'DEFAULT_SPEED': 6.966857,
            'DIRECTION_FIELD': '',
            'ENTRY_COST_CALCULATION_METHOD': 1,
            'ID_FIELD': 'NHGISNAM',
            'INPUT': 'C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_5/gis_data/_output/lines_for_network_1870.shp',
            'POINTS': 'C:/Users/se.4537/Dropbox/PoliteconGIS/LBS_2020/PhD/lecture_5/gis_data/_output/county_centroids.shp',
            'SPEED_FIELD': 'speed',
            'STRATEGY': 1,
            'TOLERANCE': 10,
            'VALUE_BACKWARD': '',
            'VALUE_BOTH': '',
            'VALUE_FORWARD': '',
            'OUTPUT': parameters['Test123']
        }
        outputs['OdMatrixFromPointsAsTableNn'] = processing.run('qneat3:OdMatrixFromPointsAsTable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Test123'] = outputs['OdMatrixFromPointsAsTableNn']['OUTPUT']
        return results

    def name(self):
        return 'model'

    def displayName(self):
        return 'model'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Model()

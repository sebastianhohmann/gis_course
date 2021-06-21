// Land cover classification with google earth engine
// code by Shaun R. Levick
// https://github.com/geospatialeco/GEARS/blob/master/Intro_RS_Lab7.md
// see also the youtube tutorial:
// https://www.youtube.com/watch?v=Yw2Ej11xbdk&list=PLf6lu3bePWHDi3-lrSqiyInMGQXM34TSV&index=7


// ############################################################
// LOAD AND DISPLAY DATA
// ############################################################

//Filter image collection for time window, spatial location, and cloud cover
var image = ee.Image(ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')
    .filterBounds(roi)
    .filterDate('2018-01-01', '2018-12-31')
    .sort('CLOUD_COVER')
    .first());

print(image);

//Add true-clour composite to map
Map.addLayer(image, {bands: ['B4', 'B3', 'B2'],min:0, max: 3000}, 'True colour image');  

//Centre the map on your region of interest
Map.centerObject(roi, 8);

// ############################################################
// DEFINE TRAINING SET, TRAIN CLASSIFIER, CLASSIFY IMAGE
// ############################################################

//Merge into one FeatureCollection and print details to console
var classNames = tW.merge(tU).merge(tF).merge(tA);
print(classNames, 'features for classification');

//Extract training data from select bands of the image, print to console
var bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7'];
var training = image.select(bands).sampleRegions({
  collection: classNames,
  properties: ['lc'],
  scale: 30
});
print(training, 'training set');

//Train classifier - e.g. cart, randomForest, svm
var classifier = ee.Classifier.smileCart().train({
  features: training,
  classProperty: 'lc',
  inputProperties: bands
});

//Run the classification
var classified = image.select(bands).classify(classifier);

//Add the classification to the map view, specify colours for classes
var visParams = {min: 0, max: 3, palette: ['blue', 'red', 'green','yellow']};
Map.addLayer(classified, visParams, 'classification');

// ############################################################
// DEFINE VALIDATION SET, COMPUTE ACCURACY AND CONFUSION MATRIX
// ############################################################

//Merge into one FeatureCollection
var valNames = vW.merge(vU).merge(vF).merge(vA);
print(valNames, 'features for validation');

var validation = classified.sampleRegions({
  collection: valNames,
  properties: ['lc'],
  scale: 30,
});
print(validation, 'validation set');

//Compare the landcover of your validation data against the classification result
var testAccuracy = validation.errorMatrix('lc', 'classification');
//Print the error matrix to the console
print('Validation error matrix: ', testAccuracy);
//Print the overall accuracy to the console
print('Validation overall accuracy: ', testAccuracy.accuracy());
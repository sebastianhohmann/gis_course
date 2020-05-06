/**
 * Function to mask clouds based on the pixel_qa band of Landsat 8 SR data.
 * @param {ee.Image} image input Landsat 8 SR image
 * @return {ee.Image} cloudmasked Landsat 8 image
 */
function maskL8sr(image) {
  // Bits 3 and 5 are cloud shadow and cloud, respectively.
  var cloudShadowBitMask = (1 << 3);
  var cloudsBitMask = (1 << 5);
  // Get the pixel QA band.
  var qa = image.select('pixel_qa');
  // Both flags should be set to zero, indicating clear conditions.
  var mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0)
                 .and(qa.bitwiseAnd(cloudsBitMask).eq(0));
  return image.updateMask(mask);
}

var minlat = 4.371;
var maxlat = 11.453;
var minlon = -3.501;
var maxlon = 1.614;
var boundbox = ee.Geometry.Rectangle([minlon, minlat, maxlon, maxlat]);

var startmonth = 1;
var endmonth = 12;

// importing landsat 8 collection 1 surface reflectance tier 1 image collection 
// filter by date
// filter by intersection of bounding box over ghana
// mask out shawdows and clouds
// retain only specified months of data per year

var ls8collection = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR")
  .filterDate("2014-01-01", "2019-01-01")
  .filterBounds(boundbox)
  .filter(ee.Filter.calendarRange(startmonth, endmonth, 'month'))
  .map(maskL8sr);

// creating a function to add an ndvi band
function addNDVI(img) {
  var ndvi = img.normalizedDifference(['B5', 'B4']).rename('NDVI');
  return img.addBands(ndvi);
}
// adding the ndvi band to each image from the collection
var with_ndvi = ls8collection.map(addNDVI);

// getting annual medians
// source:
// https://gis.stackexchange.com/questions/258344/

// Group by year, and then reduce within years by median();
// the result is an ImageCollection with one image for each
// year (including an ndvi band).

var years = ee.List.sequence(2014, 2018);
// var years = ee.List([2014, 2018]);
var byYear = ee.ImageCollection.fromImages(
      years.map(function (y) {
        return with_ndvi.filter(ee.Filter.calendarRange(y, y, 'year'))
                    .median()
                    .set('year', y);
}));
print(byYear, 'one image per year');


// Display a true color composite and ndvi for 2014.
var img = ee.Image(byYear.first());
var rgb_vis = {bands: ['B4', 'B3', 'B2'], min:0, max: 3000};
var ndvi_vis = {bands: ['NDVI'], min:0, max: 1, palette: ['blue', 'brown', 'green']};
Map.addLayer(img, rgb_vis, 'SR composite, RGB');
Map.addLayer(img, ndvi_vis, 'NDVI');

// centering the map display and setting the zoom factor
Map.setCenter(-1.6163, 6.6666, 6);

// adding the bounding box
// Map.addLayer(boundbox, {color: 'FF0000'}, 'bounding box');


// #########################################################################
// #########################################################################
// CALCULATING STATISTICS INSIDE REGIONS
// #########################################################################
// #########################################################################

// loading admin-2 boundaries of ghana as feature collection
// CHANGE TO YOUR USER NAME
var gha_admin2 = ee.FeatureCollection('users/YOUR_USERNAME_HERE/gadm36_GHA_2');
print(gha_admin2, 'ghana admin-2 boundaries');
Map.addLayer(gha_admin2, {color: 'FF0000'}, 'admin-2 boundaries');

// we only care about ndvi, not all bands:
var ndvi_by = byYear.select(['NDVI']);

// creating a function to compute mean ndvi by region
function zs_mean(image) {
  
  var mean_dict = image.reduceRegions({
    collection: gha_admin2,
    reducer: ee.Reducer.mean(),
    scale: 30
  });
  
  return mean_dict;
}

// large reductions like these can take time
// the script ran around 10 mins for me
// see here for a discussion (Noel Gorelick, one of EE's co-founders answering):
// https://gis.stackexchange.com/questions/297314

// #########################################################################
// CALCULATIONS FOR INDIVIDUAL YEARS
// #########################################################################

var listOfImages = ndvi_by.toList(ndvi_by.size());
print(zs_mean(ee.Image(ndvi_by.first())), 'ndvi by region, 2014');
print(zs_mean(ee.Image( listOfImages.get(1)  )), 'ndvi by region, 2015');

// #########################################################################
// EXPORTING CALCULATIONS TO GOOGLE DRIVE
// #########################################################################

var yrs = ['2014', '2015', '2016', '2017', '2018'];
var text = "gha_mean_ndvi_";
var y;
for (y = 0; y < yrs.length; y++) {
  var itertext = text + yrs[y];

  // Export the FeatureCollection.
  Export.table.toDrive({
    collection: zs_mean(ee.Image( listOfImages.get(y)  )),
    description: itertext,
    fileFormat: 'CSV',
    folder: 'ee_exports',
    fileNamePrefix: itertext,
    selectors: ['GID_2', 'NAME_1', 'NAME_2', 'mean']
  });
  
} 
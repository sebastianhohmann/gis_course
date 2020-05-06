// see this article here:
// https://earthobservatory.nasa.gov/images/146362/airborne-nitrogen-dioxide-plummets-over-china

// note: we are doing "before and after", of course to do this properly, you would do diff-in-diff

var minlat = 18.15;
var maxlat = 53.60;
var minlon = 73.68;
var maxlon = 135.11;
var boundbox = ee.Geometry.Rectangle([minlon, minlat, maxlon, maxlat]);

var mean_1 = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2")
	.filterDate("2020-01-01", "2020-01-20")
	.filterBounds(boundbox)
	.select('NO2_column_number_density')
	.mean();

var mean_2 = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_NO2")
	.filterDate("2020-02-10", "2020-02-25")
	.filterBounds(boundbox)
	.select('NO2_column_number_density')
	.mean();

var viz_params = {
	min: 0,
	max: 0.0005,
	palette : ['white', 'blue', 'yellow', 'red', 'brown']
};

Map.addLayer(mean_1, viz_params, 'Jan 01-20, 2020');
Map.addLayer(mean_2, viz_params, 'Feb 10-25, 2020');

// centering the map display and setting the zoom factor
Map.setCenter(116.383333, 39.916667, 5);


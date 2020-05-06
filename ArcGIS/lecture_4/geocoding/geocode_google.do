**************************************************************************		
* GEOCODING WITH STATA AND GOOGLE MAPS API
**************************************************************************	
* by sebastian hohmann, 2015
* note: google has daily query limit if 2500 per day
* if you need to geocode more observations, get a different ip
* requires insheetjson (to get it ssc install insheetjson)
**************************************************************************	

local folder "DRIVE:/path/to/your/folder"
cd "`folder'"

**************************************************************************	

insheet using "geocode_example.csv", names

* replace all white spaces with + in the location variables
gen auxcountry = subinstr(country," ","+",.)
gen auxregion = subinstr(region," ","+",.)
gen auxaddr = subinstr(address," ","+",.)

local nobs = _N

* define country, region, and address variables
local ctryvar auxcountry
local admvar auxregion
local addrvar auxaddr

gen str20 lat=""
gen str20 lng=""

local apikey "INSERT_YOUR_API_KEY_HERE"

* GEOCODING
forval i = 1/`nobs' {

	local ctry = `ctryvar'[`i']
	local admr = `admvar'[`i']
	local addr = `addrvar'[`i']
			
	local url https://maps.googleapis.com/maps/api/geocode/json?address=`addr'&components=administrative_area:`admr'|country:`ctry'&key=`apikey'
	
	*prevent google denying access due to overflood
	sleep 250
	
	local offs = `i'-1

	insheetjson lat lng using "`url'", table("results") col("geometry:location:lat" "geometry:location:lng") limit(1) offset(`offs')
	
	local status "geocoded `i' observations"
	di `"`status'"'
	
}

drop auxcountry-auxregion
destring lat, replace
destring lng, replace




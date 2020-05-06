**************************************************************************		
* GEOCODING WITH STATA AND GEONAMES API
**************************************************************************	
* by sebastian hohmann, 2015
* requires libjson, insheetjson packages
* these can be ssc installed
* you also need to sign up for a geonames username 
* http://www.geonames.org/login
* and activate the free webservices
* once you have your username, replace it 
* into xyz in line 25
**************************************************************************	


clear

local folder "DRIVE:/path/to/your/folder"
cd "`folder'"

insheet using "geocode_example.csv", comma names

local nobs = _N

* enter your username
local username xyz

* define country and address variables
local ctryvar country
local addrvar address

gen str20 lat=""
gen str20 lng=""

forval i = 1/`nobs' {

	local ctry = `ctryvar'[`i']
	local addr = `addrvar'[`i']
		
	*we get the address info from geonames into temp file
	
	local url http://api.geonames.org/searchJSON?q=`addr'&country=`ctry'&style=full&operator=OR&featureClass=P&featureClass=A&maxRows=10&isNameRequired=true&username=`username'
	
	*prevent geonames denying access due to overflood
	sleep 1800
	
	local offs = `i'-1

	insheetjson lat lng using "`url'", table("geonames") col("lat" "lng") limit(1) offset(`offs')

}

destring lat, replace
destring lng, replace

/* jshint esversion:6 */

const fs = require('fs');
const zipcodes = require('zipcodes');
const anyjson = require('any-json');

const ct_file = process.argv[2];
const out_file = process.argv[3];

anyjson.decode(fs.readFileSync(ct_file), 'csv').then((results) => {
  for (const loc of results) {
    let location = zipcodes.lookup(loc.zip.slice(0, 5));
    if (!location) {
      const lookup = zipcodes.lookupByName(loc.city, loc.state) || [];
      location = lookup.length > 0 ? lookup[0] : undefined;
    }
    if (location && location.latitude) {
      loc.latitude = location.latitude;
      loc.longitude = location.longitude;
    } else {
      console.log(`'${loc.city}, ${loc.state} ${loc.zip}'`);
    }
  }
  
  fs.writeFileSync(out_file, JSON.stringify(results, null, 2));
});
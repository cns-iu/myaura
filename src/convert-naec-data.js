/* jshint esversion:6 */

const fs = require('fs');
const cheerio = require('cheerio');

const naec_file = process.argv[2];
const out_file = process.argv[3];

const naec_data = JSON.parse(fs.readFileSync(naec_file)).results.map((n) => {
  const $ = cheerio.load(n.results_html);
  n.id = `NAEC:${n.id}`;
  n.name = $('.loc-results__name').text();
  n.url = $('.loc-results__name a').attr('href');
  n.facility = $('.info__subitem--hospital_name').text();
  n.level = $('.info__subitem--level').text();
  n.demographic = $('.info__subitem--demographic').text();
  n.phone = $('.info__subitem--phone').text();
  n.director = $('.info__subitem--med-dir').text();
  n.codirector = $('.info__subitem--co-med-dir').text();

  const location = ($('.info__subitem--aadress').text() || '').split(',', 2);
  if (location.length == 2) {
    n.address = $('.info__subitem--address_1').text();
    n.city = location[0];
    n.state = location[1].split(' ').slice(0, -1).join(' ').trim();
    n.zip = location[1].split(' ').slice(-1)[0].trim();
  } else {
    console.log($('.info__subitem--aadress').text());
    console.log(location);
  }
  n.latitude = n.lat;
  n.longitude = n.lng;

  n.results_html = undefined;
  n.infowin_html = undefined;
  n.distance = undefined;
  n.lat = undefined;
  n.lng = undefined;
  
  return n;
});

fs.writeFileSync(out_file, JSON.stringify(naec_data, null, 2));

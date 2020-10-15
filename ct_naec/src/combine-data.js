/* jshint esversion:6 */

const fs = require('fs');

const ct_file = process.argv[2];
const naec_file = process.argv[3];
const out_file = process.argv[4];

const ct_data = JSON.parse(fs.readFileSync(ct_file)).map(n => Object.assign({type: "clinical_trials"}, n));
const naec_data = JSON.parse(fs.readFileSync(naec_file)).map(n => Object.assign({type: "naec_doctors"}, n));

const ct_keys = Object.keys(ct_data[0]);
const naec_keys = Object.keys(naec_data[0]);
const shared_keys = naec_keys.filter(k => ct_keys.includes(k));

function remap(arr, keys) {
  return arr.map(item => keys.reduce((acc, key) => (acc[key] = item[key], acc), {}));
}

const shared_data = remap(ct_data.concat(naec_data), shared_keys);

fs.writeFileSync(out_file, JSON.stringify(shared_data, null, 2));

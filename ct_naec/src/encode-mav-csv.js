/* jshint esversion:6 */

const fs = require('fs');
const anyjson = require('any-json');

const json_file = process.argv[2];
const out_file = process.argv[3];

const data = JSON.parse(fs.readFileSync(json_file));

for (const row of data) {
  for (const key of Object.keys(row)) {
    switch (key) {
      case 'type':
        switch (row.type) {
          case 'clinical_trials':
            row.type$$color = '#0000ff';
            row.type$$shape = 'circle';
            row.type$$areaSize = 50;
            row.type$$transparency = 0.5;
            break;
          case 'naec_doctors':
            row.type$$color = '#ff0000';
            row.type$$shape = 'cross';
            row.type$$areaSize = 30;
            row.type$$transparency = 0.5;
            break;
        }
        break;
    }
  }
}

// fs.writeFileSync(out_file, JSON.stringify({csvData: data}, null, 2));

anyjson.encode(data, 'csv').then((csvString) => {
  fs.writeFileSync(out_file, csvString);
});

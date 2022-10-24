# osm-emapa-address-diff
[Przeczytaj po polsku](README.md).

A tool for comparing addresses in OpenStreetMap and specified e-map server.
Allows simple data analysis and detection of address discrepancies.

## Features
- Downloading current data from e-mapa/OpenStreetMap.
- Counting the type of objects from OSM data.
- Address tags distribution in OSM data (allows tracking of missing key/value data).
- Duplicate address detection.
- Detection of missing addresses in OpenStreetMap (including erroneous ones) from the e-mapa.
- Detection of excess addresses in OpenStreetMap (including erroneous ones) that do not exist in the e-mapa.
- Saving of detected address inconsistencies to files (.geojson and .txt).

## Usage
The tool requires to be installed [Pythona3](https://www.python.org/) with dependencies defined in [requirements.txt](requirements.txt).

`pip install -r requirements.txt`

To run the program, enter the command below, where \<teryt_terc\> should be replaced with the corresponding
7 character identifier of the commune (gmina).
It can be found in the administrative boundaries relation in OpenStreetMap
under the _teryr:terc_ tag or e.g. [here](https://eteryt.stat.gov.pl/eTeryt/rejestr_teryt/udostepnianie_danych/baza_teryt/uzytkownicy_indywidualni/wyszukiwanie/wyszukiwanie.aspx).

`python main.py <teryt_terc>`

The program may end with an error moments after launching if it turns out that the selected commune (gmina) does not use the e-mapa.
The tool uses the [public address data list](https://integracja.gugik.gov.pl/daneadresowe/) from GUGiK.

If the teryt_terc is successful and the OSM data is retrieved, the application will print (into terminal) report of the address analysis and create 4 files in the `out/<teryt_terc>/` directory:
- emapa_addresses_all.geojson – contains all addresses from the e-mapa parsed to OSM format.
- emapa_addresses_raw.csv – raw data in CSV format downloaded from the e-mapa.
- emapa_addresses_missing.geojson – contains missing addresses from the e-mapa parsed to OSM format.
- osm_addresses_excess.txt – contains a list of OSM object identifiers in the format \[n,w,r\]\<object id\> (np. w123), separated by commas, which can be loaded in [JOSM](https://josm.openstreetmap.de/) using the "Download object" feature (CTRL + SHIT + O).
- osm_addresses_duplicates.txt – contains a list of OSM object identifiers in the format same as excess addresses, but each line is for 1 address.

Other launch arguments can be shown by using:

`python main.py -h`

## License
[MIT](LICENSE)

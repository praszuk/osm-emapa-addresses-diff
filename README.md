# osm-emapa-address-diff
[Read in English](README.en.md).

Narzędzie do porównywania adresów w OpenStreetMap i wybranej e-mapy.
Umożliwia prostą analizę danych i wykrycie niezgodności w adresacji.

## Funkcjonalności
- Pobieranie aktualnych danych z e-mapy/OpenStreetMap
- Zliczanie typu obiektów z danych OSM
- Użycie poszczególnych tagów adresowych w danych OSM (pozwala śledzić braki danych kluczy i wartości)
- Wykrywanie duplikatów adresów.
- Wykrywanie brakujących adresów w OpenStreetMap (w tym błędnych) względem e-mapy.
- Wykrywanie nadmiarowych adresów w OpenStreetMap (w tym błędnych), które nie istnieją w e-mapie.
- Zapis wykrytych niezgodności adresowych do plików (.geojson oraz .txt)

## Użycie
Narzędzie wymaga zainstalowanego [Pythona3](https://www.python.org/) z zależniościami z [requirements.txt](requirements.txt)

`pip install -r requirements.txt`

Aby uruchomić program należy wpisać polecenie poniżej, gdzie \<teryt_terc\> należy zastąpić odpowiednim
7 znakowym identyfikatorem danej gminy. Można go znaleźć w relacji granic administracyjnych w OpenStreetMap
pod tagiem _teryr:terc_ albo np. [tutaj](https://eteryt.stat.gov.pl/eTeryt/rejestr_teryt/udostepnianie_danych/baza_teryt/uzytkownicy_indywidualni/wyszukiwanie/wyszukiwanie.aspx).

`python main.py <teryt_terc>`

Program może zakończyć się błędem chwilę po uruchomieniu, jeśli okaże się, że wybrana gmina nie korzysta z e-mapy.
Narzędzie korzysta z [publicznej liście danych adresowych](https://integracja.gugik.gov.pl/daneadresowe/) od GUGiK.

Jeśli sprawdzenie terytu_terc się powiedzie i dane OSM zostaną pobrane, aplikacja wyświetli tekstowy raport z analizy adresów oraz utworzy 4 pliki w katalogu `out/<teryt_terc>/`:
- emapa_addresses_all.geojson – zawiera wszystkie adresy z e-mapy sparsowane do formatu OSM.
- emapa_addresses_raw.csv – dane nieprzetworzone w formacie CSV pobrane od e-mapy
- emapa_addresses_missing.geojson – zawiera brakujące adresy z e-mapy sparsowane do formatu OSM.
- osm_addresses_excess.txt – zawiera listę identyfikatorów obiektów OSM w formacie \[n,w,r\]\<id obiektu\> (np. w123), rozdzieloną przecinkami, którą można wczytać w [JOSM](https://josm.openstreetmap.de/) korzystając z funkcjonalności "Pobierz obiekt" (CTRL + SHIT + O).
- osm_addresses_duplicates.txt – zawiera listę identyfikatorów obiektów OSM w takim samym formacie jak adresy nadmiarowe, ale na każdą linię pliku przypada 1 adres.

Inne opcje uruchomieniowe można wyświetlić wpisując:

`python main.py -h`

## Licencja
[MIT](LICENSE)

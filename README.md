## python-sxgeo
Python интерфейс для работы с базой данных [Sypex Geo](http://sypexgeo.net/ru/about/)

### Sypex Geo
Это база местоположений IP-адресов (IP-сетей), преимущественно для стран СНГ в очень компактном формате. 
Результатом поиска IP-адреса в базе являются:
```
- Координаты местонахождения – широта и долгота в WGS84
- Название города/региона/страны
- ОКАТО/ОКТМО/КОАТУУ/СОАТО коды
- iso/timezone/continent
- [geoname_id](http://www.geonames.org/manual.html)
```

### Usage
```
>>> from sxgeo import SxAPI
>>> api = SxAPI('SxGeoCityMax.dat')
>>> iploc = api.locate('8.8.8.8')

>>> print iploc 
SxRecord(region_seek=6789, country_id=225, id=5375480, lat=37.38605, lon=-122.08385, 
name_ru='Маунтин-Вью', name_en='', okato='')

>>> region = api.region_info(iploc.region_seek)
>>> print region
SxRecord(country_seek=9395, id=5332921, lat=37.25, lon=-119.75, 
name_ru='Калифорния', name_en='', iso='', timezone='', okato='')
```

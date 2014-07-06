python-sxgeo
============

Python API for sypexgeo database

Usage
=====

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

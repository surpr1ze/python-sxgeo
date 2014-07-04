# -*- coding: utf-8 -*-

import os
import sys
import re
import mmap
import bisect
from struct import pack, unpack, calcsize as sizeof
from socket import inet_aton, inet_ntoa

from sxgeo import SxError, StructModel, SX_TYPE_COUNTRY, SX_TYPE_REGION, SX_TYPE_CITY


class SxAPI(object):

    def __init__(self, dbfile, sxident='SxG'):
        self.fd = os.open(dbfile, os.O_RDONLY | os.O_NONBLOCK)
        self.db = mmap.mmap(self.fd, os.SEEK_SET, prot=mmap.PROT_READ)
        
        ident = self.db.read(len(sxident))
        assert ident == sxident, 'Missing `{ident}` ident in dbfile'.format(ident=sxident)

        self.db.seek(len(sxident))

        fields = '/'.join(
            (
                'B:version',
                'L:created',
                'B:db_type',
                'B:charset',
                'B:idx_octets_count',
                'H:idx_blocks_count',
                'H:idx_block_size',
                'L:net_ranges_count',
                'B:id_datatype_size',
                'H:region_record_size',
                'H:city_record_size',
                'L:region_cat_size',
                'L:city_cat_size',
                'H:country_record_size',
                'L:country_cat_size',
                'H:pack_format_size'
            )
        )

        header = StructModel('DBHeader', fields, sxstruct=False)
        header_fmt = '{order}{spec}'.format(
            order=header.byteorder,
            spec=''.join(header.struct)
        )
        meta = header.create(self.db.read(sizeof(header_fmt)))

        self.models = []
        for x in self.db.read(meta.pack_format_size).split(b'\0'):
            self.models.append(StructModel('SxRecord', x, byteorder='<'))

        self.idx_net_ranges = unpack(
            '>{0}L'.format(meta.idx_octets_count),
            self.db.read(meta.idx_octets_count * 4)
        )
        self.idx_blocks = unpack(
            '>{0}L'.format(meta.idx_blocks_count),
            self.db.read(meta.idx_blocks_count * 4)
        )
        
        self.net_blocks_offset = self.db.tell()
        self.net_block_record_size = meta.id_datatype_size + 3
        self.db_region_offset = self.net_blocks_offset + meta.net_ranges_count * self.net_block_record_size
        self.db_cities_offset = self.db_region_offset + meta.region_cat_size

        self.DBMeta = meta
    
    def locate(self, ipv4, region=False):
        numeric = inet_aton(ipv4)
        octet, = unpack('!B', numeric[0])

        if octet in (0, 10, 127) or octet >= self.DBMeta.idx_octets_count:
            return None

        lo = self.idx_net_ranges[octet-1]
        hi = self.idx_net_ranges[octet]

        idx = bisect.bisect_left(self, numeric[1:], lo=lo, hi=hi) - 1
        pointer = self.db_cities_offset + self.__getitem__(idx, geoname=True)

        record_struct = self.db[pointer:pointer+self.DBMeta.city_record_size]
        record_model = self.models[SX_TYPE_CITY]

        return record_model.create(record_struct)

    def region_info(self, offset):
        offset = offset + self.db_region_offset

        record_struct = self.db[offset:offset+self.DBMeta.region_record_size]
        record_model = self.models[SX_TYPE_REGION]

        return record_model.create(record_struct)

    def __getitem__(self, idx, geoname=False):
        idx = idx if idx >= 0 else len(self) + idx
        offset = idx * self.net_block_record_size + self.net_blocks_offset

        if geoname:
            res, = unpack('>I', b'\0'+self.db[offset+3:offset+self.net_block_record_size])
        else:
            res = self.db[offset:offset+3]

        return res

    def __iter__(self):
        for idx in range(len(self)):
            yield self.__getitem__(idx)

    def __len__(self):
        return self.DBMeta.net_ranges_count

    def __repr__(self):
        return '<%s[mmap] object at %r>' % (self.__class__.__name__, hex(id(self)))


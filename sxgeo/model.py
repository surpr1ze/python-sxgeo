# -*- coding: utf-8 -*-

import os
import re
import sys
import mmap
import bisect
from struct import pack, unpack, calcsize as sizeof
from operator import itemgetter


def StructModel(typename, specstring, byteorder='>', sxstruct=True):

    mapping = {
        re.compile('t'): r'b',
        re.compile('T'): r'B',
        re.compile('s'): r'h',
        re.compile('S'): r'H',
        re.compile('m'): r'i',
        re.compile('M'): r'3B',
        re.compile('i'): r'l',
        re.compile('I'): r'L',
        re.compile('c(\d)'): r'\1s',
        re.compile('b'): r'{:d}s'
    }

    struct = []
    fields = []

    for dt, fn in (e.split(':') for e in specstring.split('/')):
        fields.append(fn)

        if sxstruct:
            for expr, repl in mapping.iteritems():
                if expr.search(dt):
                    dt = expr.sub(repl, dt)
                    break
        
        struct.append(dt)

    typeclass = """class {typename}(tuple):

        __slots__ = ()

        def __new__(cls, {args}):
            return tuple.__new__(cls, ({args}))

        @classmethod
        def create(cls, package, new=tuple.__new__, len=len):
            repacked = []
            order = cls.byteorder
            
            for e in cls.struct:
                if e == '{{:d}}s':
                    for idx, byte in enumerate(package):
                        if byte == ZERO_BYTE:
                            break

                    e = e.format(idx)
                    unpacked, = unpack(order+e, package[:idx])

                elif e == '3B':
                    unpacked, = unpack(order+e.replace('3B', 'I'), package[:sizeof(order+e)] + ZERO_BYTE)
 
                elif e[0] == 'N':
                    precision = int(e[1:])
                    e = 'i'
                    unpacked, = unpack(order+e, package[:sizeof(order+e)])
                    unpacked /= 10. ** precision

                elif e[0] == 'n':
                    precision = int(e[1:])
                    e = 'h'
                    unpacked, = unpack(order+e, package[:sizeof(order+e)])
                    unpacked /= 10. ** precision
                else:
                    unpacked, = unpack(order+e, package[:sizeof(order+e)])

                package = package[sizeof(order+e):]
                repacked.append(unpacked)

            result = new(cls, repacked)
            if len(result) != {numfields:d}:
                raise TypeError('Expected {numfields:d} arguments, got {{gotfields:d}}'.format(gotfields=len(result)))

            return result

        def __repr__(self):
            return '{typename}({repr_fields})' % self

        byteorder = '{byteorder}'
        struct = {struct}

    {properties}
    """
    
    property_fmt = """
        {name} = property(itemgetter({index}))
    """

    repr_fields = ', '.join(['{0}=%r'.format(field) for field in fields])
    properties = ''.join(
        [property_fmt.format(name=name, index=index) for index, name in enumerate(fields)]
    )

    typedef = typeclass.format(
        typename=typename,
        numfields=len(fields),
        args=repr(fields).replace("'", "")[1:-1],
        repr_fields=repr_fields,
        properties=properties,
        byteorder=byteorder,
        struct=tuple(struct)
    )
   
    namespace = dict(
        itemgetter=itemgetter,
        property=property,
        tuple=tuple,
        properties=properties,
        unpack=unpack,
        sizeof=sizeof,
        ZERO_BYTE=b'\0',
        __name__=sys._getframe().f_code.co_name
    )

    exec typedef in namespace
    return namespace[typename]

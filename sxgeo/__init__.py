# -*- coding: utf-8 -*-

__all__=['api', 'errors', 'model']

SX_TYPE_COUNTRY = 0
SX_TYPE_REGION = 1
SX_TYPE_CITY = 2

from .errors import SxError
from .model import StructModel
from .api import SxAPI

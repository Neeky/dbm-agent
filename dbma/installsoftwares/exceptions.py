# -*- encoding: utf8 -*-

from dbma.exceptions import DBMABaseException

class PkgNotExistsException(DBMABaseException):
    """
    软件包找不到
    """
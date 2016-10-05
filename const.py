# -*- coding: utf-8 -*-
"""File that has all constants (including the configuration)"""

import config
from config import configuration
from config import db_credentials

class Const:
	# ID feature name
	ID_STR = configuration.ID_STR

	# Link label value
	LINK_NORMATIVA = '<a href="file:///{:s}">Veure normativa</a>'

	# Query result columns 
	REFCAT = 0
	AREA = 1
	ADRECA = 2
	CODI_CLASSI = 3
	DESCR_CLASSI = 4
	CODI_ZONES = 5
	PERCENT_ZONES = 6
	CODI_SECTOR = 7
	DESCR_SECTOR = 8

	# Database credentials generation
	DB_CREDENTIALS = "host={} port={} dbname={} user={} password={}".format(
		db_credentials.host,
		db_credentials.port,
		db_credentials.dbname,
		db_credentials.user,
		db_credentials.password)

	# Info query
	QUERY = 'SELECT * FROM ficha_urbanistica(%s);'


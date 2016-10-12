# -*- coding: utf-8 -*-
"""File that has all constants (including the configuration)"""

import config
from config import configuration
from config import db_credentials

class Const:
	"""Constains all the constants used in the plugin."""

	# Internal ID field name
	ID_STR = configuration.ID_STR

	# Link labels value (it is formatted later on)
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

	# PDF composite index
	PDF_UBICACIO = 0
	PDF_ZONES = 1


	# Database credentials generation
	DB_CREDENTIALS = "host={} port={} dbname={} user={} password={}".format(
		db_credentials.host,
		db_credentials.port,
		db_credentials.dbname,
		db_credentials.user,
		db_credentials.password)

	# Query the infrmation from the database
	MAIN_QUERY = 'SELECT * FROM ficha_urbanistica(%s);'
	QUALI_QUERY = 'SELECT * FROM qualificacio_general WHERE id = %s;'
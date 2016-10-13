# -*- coding: utf-8 -*-
"""File that has all constants (including the configuration)"""

import config
from config import db_credentials

class Const:
	"""Constains all the constants used in the plugin."""
	# Link labels value (it is formatted later on)
	LINK_NORMATIVA = u"<a href='file:///{:s}'>Veure normativa</a>"
	LINK_COND = u"<a href='{:s}condicions_generals.htm'>Condicions Generals</a>"
	LINK_DOT = u"<a href='{:s}dotacio_aparcament.htm'>Dotació mínima d'aparcaments</a>"
	LINK_REG = u"<a href='{:s}regulacio_aparcament.htm'>Regulació particular de l'ús d'aparcaments</a>"
	LINK_FINCA = u"<a href='{:s}param_finca.htm'>Paràmetres Finca</a>"
	LINK_EDIF = u"<a href='{:s}param_edificacio.htm'>Paràmetres Edificació</a>"

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
	PDF_UBICACIO = u'Fitxa 1 - Ubicació'
	PDF_ZONES = u'Fitxa 2 - Zones'


	# Database credentials generation
	DB_CREDENTIALS = "host={} port={} dbname={} user={} password={}".format(
		db_credentials.host,
		db_credentials.port,
		db_credentials.dbname,
		db_credentials.user,
		db_credentials.password)

	# Query the infrmation from the database
	MAIN_QUERY = 'SELECT * FROM data.ficha_urbanistica(%s);'
	QUALI_QUERY = 'SELECT * FROM qualificacio_general WHERE id = %s;'
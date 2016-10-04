# -*- coding: utf-8 -*-
"""Main file of the project ficha_urbanistica. This contains the main class as well as all the importan work."""

# TODO add imports

import os
import psycopg2
import db_credentials
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ui.form import Ui_dialogName

DB_CREDENTIALS = "host={} port={} dbname={} user={} password={}".format(
	db_credentials.host,
	db_credentials.port,
	db_credentials.dbname,
	db_credentials.user,
	db_credentials.password)
LAYER_NAME = ""
ID_STR = "ninterno"
REPORTS_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/reports/"


class FichaUrbanistica:
	"""Main class of the project ficha_urbanistica"""


	def __init__(self, iface):
		"""Contructor"""

		# Saving iface to be reachable from the other functions
		self.iface = iface

		self.plugin_dir = os.path.dirname(__file__)
		self.pluginName = os.path.basename(self.plugin_dir)


		# Connecting to the database
		try:
			# Cedentials in the credentials file. The credentials should not be uploaded to the public repository
			self.conn = psycopg2.connect(DB_CREDENTIALS)
			self.cursor = self.conn.cursor()
		except psycopg2.DatabaseError as e:
			print u'Error al connectar amb la base de dades.'
			print '{:s}'.format(e)
			print ''
			print u'No es carregarà el plugin.'
			return # This return means there is no trigger set

		self.icon = None
		self.action = None



	def initGui(self):
		"""Called when the gui must be generated."""

		# Find and safe the plugin's icon
		filename = os.path.abspath(os.path.join(self.plugin_dir, 'icon.png'))
		self.icon = QIcon(str(filename))

		# Add menu and toolbar entries (basically allows to activate it)
		self.action = QAction(self.icon, tr("Ficha urbanística"), self.iface.mainWindow())
		QObject.connect(self.action, SIGNAL('triggered()'), self.run)
		self.iface.addToolBarIcon(self.action)
		self.iface.addPluginToMenu(qu("Ficha urbanística"), self.action)



	def unload(self):
		"""Called when the plugin is being unloaded."""
		self.iface.removePluginMenu(qu("Ficha urbanística"), self.action)
		self.iface.removeToolBarIcon(self.action)



	def run(self):
		"""Called when the plugin's icon is pressed."""
		
		# Get the active layer (where the selected form is).
		layer = self.iface.activeLayer()

		# Make sure it is the layer we think it is.
		#if layer.name() != LAYER_NAME:
		#	return


		# single feature
		features = layer.selectedFeatures()
		if len(features) != 1:
			return
		self.openForm(features[0][ID_STR])

		# Multiple feature support
		# if len(features) < 1:
		#	return
		# elif len(features) == 1:
		#	openForm(features[0][ID_STR])
		# else:
		#	while feature in features:
		#		thread.start_new_thread(openform, (feature[ID_STR]))



	def openForm(self, id):
		"""Opens the form which shows the information to the user."""

		# This function supports multiple instances

		# Query the necesary information
		info = self.queryInfo(id)

		dialog = QDialog(None, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
		dialog.ui = Ui_dialogName()
		dialog.ui.setupUi(dialog)

		dialog.setAttribute(Qt.WA_DeleteOnClose)
		dialog.setWindowIcon(self.icon)

		REFCAT = 0
		AREA = 1
		ADRECA = 2
		CODI_CLASSI = 3
		DESCR_CLASSI = 4
		CODI_ZONES = 5
		PERCENT_ZONES = 6
		CODI_SECTOR = 7
		DESCR_SECTOR = 8

		# Set values to the data
		dialog.ui.refcat.setText(u'{}'.format( info[REFCAT] ))
		dialog.ui.ninterno.setText(u'{}'.format(id))
		dialog.ui.area.setText(u'{}'.format( info[AREA] ))
		dialog.ui.txtAdreca.setText(u'{}'.format( info[ADRECA] ))

		if info[7] is not None:
			dialog.ui.txtSector.setText(u'{} - {}'.format( info[CODI_SECTOR], info[DESCR_SECTOR] ))
			dialog.ui.lblSector.setText(self.sectorLink('{}'.format(info[CODI_SECTOR])))
		else:
			dialog.ui.lblSector.setHidden(True)

		dialog.ui.txtClass.setText(u'{} - {}'.format( info[CODI_CLASSI], info[DESCR_CLASSI] ))
		dialog.ui.lblClass.setText(self.classiLink('{}'.format( info[CODI_CLASSI] )))


		codes = info[CODI_ZONES]
		percents = info[PERCENT_ZONES]

		if len(codes) >= 1:
			dialog.ui.txtClau_1.setText(u'{}'.format(str(codes[0])))
			dialog.ui.txtPer_1.setText(u'{:02.2f}'.format(percents[0]))
			dialog.ui.lblOrd_1.setText(u'{}'.format(self.ordLink(codes[0])))


		if len(codes) >= 2:
			dialog.ui.txtClau_2.setText(u'{}'.format(str(codes[1])))
			dialog.ui.txtPer_2.setText(u'{:02.2f}'.format(percents[1]))
			dialog.ui.lblOrd_2.setText(u'{}'.format(self.ordLink(codes[1])))
		else:
			dialog.ui.txtClau_2.setHidden(True)
			dialog.ui.txtPer_2.setHidden(True)
			dialog.ui.lblOrd_2.setHidden(True)


		if len(codes) >= 3:
			dialog.ui.txtClau_3.setText(u'{}'.format(str(codes[2])))
			dialog.ui.txtPer_3.setText(u'{:02.2f}'.format(percents[2]))
			dialog.ui.lblOrd_3.setText(u'{}'.format(self.ordLink(codes[2])))
		else:
			dialog.ui.txtClau_3.setHidden(True)
			dialog.ui.txtPer_3.setHidden(True)
			dialog.ui.lblOrd_3.setHidden(True)


		if len(codes) >= 4:
			dialog.ui.txtClau_4.setText(u'{}'.format(str(codes[3])))
			dialog.ui.txtPer_4.setText(u'{:02.2f}'.format(percents[3]))
			dialog.ui.lblOrd_4.setText(u'{}'.format(self.ordLink(codes[3])))
		else:
			dialog.ui.txtClau_4.setHidden(True)
			dialog.ui.txtPer_4.setHidden(True)
			dialog.ui.lblOrd_4.setHidden(True)

		# TODO add functionality to buttons
		# btnParcelaPdf -> ubicacio
		# btnClauPdf_1 -> zones

		dialog.exec_()



	def queryInfo(self, id):
		"""Querys the information on the database."""
		self.cursor.execute(u'SELECT * FROM ficha_urbanistica(%s);', [id])
		return self.cursor.fetchall()[0]


	def sectorLink(self, id):
		return 'link' # TODO

	def classiLink(self, id):
		return '<a>link</a>' # TODO

	def ordLink(self, code):
		return '<a>link</a>' # TODO






# Utilities

# Unicode QString generator function
try:
    qu = QtCore.QString.fromUtf8
except AttributeError:
    def qu(s):
        return s

# Qt translate function
try:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, QApplication.UnicodeUTF8)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)
def tr(text):
    return _translate("export_gml_catastro_espanya", text, None)


# Returns a QVector of QgsPoints which are the vertex
def getVertex(geometry):
    current = geometryToVector(geometry)
    while len(current) > 0 and type(current[0]) is not QgsPoint:
        temp = []
        for sub in current:
            for e in sub:
                temp.append(e)
        current = temp
    return current

# Converts the geometry into a QVector of its type
def geometryToVector(geometry):
    if geometry.wkbType() == QGis.WKBPolygon:
        return geometry.asPolygon()

    elif geometry.wkbType() == QGis.QPolygonF:
        return geometry.asQPolygonF().toPolygon()

    elif geometry.wkbType() == QGis.WKBMultiPolygon:
        return geometry.asMultiPolygon()

    elif geometry.wkbType() == QGis.WKBMultiPoint:
        return geometry.asMultiPoint()

    elif geometry.wkbType() == QGis.WKBPoint:
        return geometry.asPoint()

    elif geometry.wkbType() == QGis.WKBLineString:
        return geometry.asPolyline()

    elif geometry.wkbType() == QGis.WKBMultiLineString:
        return geometry.asMultiPolyline()

    else:
        return []
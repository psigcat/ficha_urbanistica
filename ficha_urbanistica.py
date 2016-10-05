# -*- coding: utf-8 -*-
"""Main file of the project ficha_urbanistica. This contains the main class as well as all the importan work."""

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


class FichaUrbanistica:
	"""Main class of the project ficha_urbanistica"""


	def __init__(self, iface):
		"""Contructor"""

		# Saving iface to be reachable from the other functions
		self.iface = iface

		self.plugin_dir = os.path.dirname(__file__)
		self.pluginName = os.path.basename(self.plugin_dir)

		# Save and make, if they don't exist, the docs folders.
		docs = os.path.join(self.plugin_dir, 'docs')
		self.sector_folder = os.path.join(docs, '')
		self.classi_folder = os.path.join(docs, '')
		self.ord_folder = os.path.join(docs, '')

		# Save, make and empty the folders for the resulting PDF.
		reports = os.path.join(self.plugin_dir, 'reports')
		self.ubicacio_folder = os.path.join(reports, 'ubicacio')
		self.permisos_folder = os.path.join(reports, 'permisos')
		createFolder(reports)
		createFolder(self.ubicacio_folder)
		emptyFolder(self.ubicacio_folder)
		createFolder(self.permisos_folder)
		emptyFolder(self.permisos_folder)



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

		# Make dialog and set its atributes
		dialog = QDialog(None, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
		dialog.ui = Ui_dialogName()
		dialog.ui.setupUi(dialog)
		dialog.setFixedSize(dialog.size())
		dialog.setAttribute(Qt.WA_DeleteOnClose)
		dialog.setWindowIcon(self.icon)

		# Constants that define the row of the result mapped on it meaning
		REFCAT = 0
		AREA = 1
		ADRECA = 2
		CODI_CLASSI = 3
		DESCR_CLASSI = 4
		CODI_ZONES = 5
		PERCENT_ZONES = 6
		CODI_SECTOR = 7
		DESCR_SECTOR = 8

		# Show data
		dialog.ui.refcat.setText(u'{}'.format( info[REFCAT] ))
		dialog.ui.ninterno.setText(u'{}'.format(id))
		dialog.ui.area.setText(u'{}'.format( info[AREA] ))
		dialog.ui.txtAdreca.setText(u'{}'.format( info[ADRECA] ))

		if info[7] is not None: # It may not be part of any sector
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

		# SHow the dialog (execute it)
		dialog.exec_()



	def queryInfo(self, id):
		"""Querys the information on the database."""
		#self.cursor.fetchall(); # ignore any residual information (should never do anything)
		self.cursor.execute(u'SELECT * FROM ficha_urbanistica(%s);', [id])
		return self.cursor.fetchone()


	def sectorLink(self, id):
		return '<a href="file:///{:s}/{:s}.html">Veure Normativa classificaci&oacute;</a>'.format(self.sector_folder, id)

	def classiLink(self, id):
		return '<a href="file:///{:s}/{:s}.html">Veure Normativa classificaci&oacute;</a>'.format(self.classi_folder, id)

	def ordLink(self, code):
		return '<a href="file:///{:s}/{:s}.html">Veure Normativa classificaci&oacute;</a>'.format(self.ord_folder, id)






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
    return _translate("ficha_urbanistica", text, None)


def createFolder(folder):
	"""Makes a folder unless it does already exist."""
	if not os.folder.exists(folder):
		os.makedirs(folder)

def emptyFolder(folder):
	"""Removes all the files and subfolders in a folder."""
	for f in os.listdir(forlder):
		os.remove(f)
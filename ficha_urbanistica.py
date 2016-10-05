# -*- coding: utf-8 -*-
"""Main file of the project ficha_urbanistica. This contains the main class as well as all the importan work."""

import os
import psycopg2
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from const import Const


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
		reports_path = os.path.join(self.plugin_dir, 'reports')
		self.ubicacio_folder = os.path.join(reports_path, 'ubicacio')
		self.permisos_folder = os.path.join(reports_path, 'permisos')
		createFolder(reports_path)
		createFolder(self.ubicacio_folder)
		emptyFolder(self.ubicacio_folder)
		createFolder(self.permisos_folder)
		emptyFolder(self.permisos_folder)



		# Connecting to the database
		try:
			# Cedentials in the credentials file. The credentials should not be uploaded to the public repository
			self.conn = psycopg2.connect(Const.DB_CREDENTIALS)
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

		# single feature
		features = layer.selectedFeatures()
		if len(features) != 1:
			return

		feature = features[0]
		id_index = feature.fieldNameIndex(Const.ID_STR)
		if id_index >= 0:
			self.openForm(feature[id_index])



	def openForm(self, id):
		"""Opens the form which shows the information to the user."""

		# This function supports multiple instances

		# Query the necesary information
		info = self.queryInfo(id)

		# Make dialog and set its atributes
		dialog = QDialog(None, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
		dialog.ui = Ui_dialogName()
		dialog.ui.setupUi(dialog)
		dialog.setAttribute(Qt.WA_DeleteOnClose)
		dialog.setWindowIcon(self.icon)
		dialog.setFixedSize(dialog.size())


		# Show data
		dialog.ui.refcat.setText(u'{}'.format( info[Const.REFCAT] ))
		dialog.ui.ninterno.setText(u'{}'.format(id))
		dialog.ui.area.setText(u'{}'.format( info[Const.AREA] ))
		dialog.ui.txtAdreca.setText(u'{}'.format( info[Const.ADRECA] ))

		if info[7] is not None: # It may not be part of any sector
			dialog.ui.txtSector.setText(u'{} - {}'.format( info[Const.CODI_SECTOR], info[Const.DESCR_SECTOR] ))
			dialog.ui.lblSector.setText(self.sectorLink('{}'.format(info[Const.CODI_SECTOR])))
		else:
			dialog.ui.lblSector.setHidden(True)

		dialog.ui.txtClass.setText(u'{} - {}'.format( info[Const.CODI_CLASSI], info[Const.DESCR_CLASSI] ))
		dialog.ui.lblClass.setText(self.classiLink('{}'.format( info[Const.CODI_CLASSI] )))


		codes = info[Const.CODI_ZONES]
		percents = info[Const.PERCENT_ZONES]

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



		# PDF generation functions
		def makeShowUbicacioPdf(): # TODO
			pass

		def makeShowZonesPdf(): # TODO
			pass

		# Connect the click signal to the functions
		QObject.connect(dialog.ui.btnParcelaPdf, SIGNAL("clicked()"), makeShowUbicacioPdf)
		QObject.connect(dialog.ui.btnClauPdf_1, SIGNAL("clicked()"), makeShowZonesPdf)

		# SHow the dialog (execute it)
		dialog.exec_()



	def queryInfo(self, id):
		"""Querys the information on the database."""
		#self.cursor.fetchall(); # ignore any residual information (should never do anything)
		self.cursor.execute(Const.QUERY, [id])
		return self.cursor.fetchone()


	def sectorLink(self, id):
		filename = '{:s}.html'.format(id)
		return Const.LINK_NORMATIVA.format(os.path.join(self.sector_folder, filename))

	def classiLink(self, id):
		filename = '{:s}.html'.format(id)
		return Const.LINK_NORMATIVA.format(os.path.join(self.classi_folder, filename))

	def ordLink(self, code):
		filename = '{:s}.html'.format(code)
		return Const.LINK_NORMATIVA.format(os.path.join(self.ord_folder, filename))


	def webDialog(self, url): # TODO
		pass






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
	if not os.path.exists(folder):
		os.makedirs(folder)

def emptyFolder(folder):
	"""Removes all the files and subfolders in a folder."""
	for f in os.listdir(folder):
		os.remove(f)
# -*- coding: utf-8 -*-
"""Main file of the project ficha_urbanistica. This contains the main class as well as all the importan work."""

import os
import sys
import psycopg2
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from const import Const

from ui.form import Ui_Form
from ui.docs_view import Ui_DocsView


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
		self.sector_folder = os.path.join(docs, 'sectors')
		self.classi_folder = os.path.join(docs, 'classificacio')
		self.ord_folder = os.path.join(docs, 'ordenacions')

		# Save, make and empty the folders for the resulting PDF.
		reports_path = os.path.join(self.plugin_dir, 'reports')
		self.ubicacio_folder = os.path.join(reports_path, 'ubicacio')
		self.zones_folder = os.path.join(reports_path, 'zones')
		createFolder(reports_path)
		createFolder(self.ubicacio_folder)
		emptyFolder(self.ubicacio_folder)
		createFolder(self.zones_folder)
		emptyFolder(self.zones_folder)

		self.settings = QSettings("PSIG", "ficha_urbanistica")


		# Connecting to the database
		try:
			# Cedentials in the credentials file. The credentials should not be uploaded to the public repository
			self.conn = psycopg2.connect(Const.DB_CREDENTIALS)
			self.cursor = self.conn.cursor()
		except psycopg2.DatabaseError as e:
			print u'Error al connectar amb la base de dades.'
			print '{:s}'.format(e)
			print ''
			print u'No es carregara el plugin.'
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
		dialog = self.initDialog(Ui_Form)
		dialog.setFixedSize(dialog.size())


		# Show data
		dialog.ui.refcat.setText(u'{}'.format( info[Const.REFCAT] ))
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
			dialog.ui.lblOrd_1.linkActivated.connect(self.webDialog)


		if len(codes) >= 2:
			dialog.ui.txtClau_2.setText(u'{}'.format(str(codes[1])))
			dialog.ui.txtPer_2.setText(u'{:02.2f}'.format(percents[1]))
			dialog.ui.lblOrd_2.setText(u'{}'.format(self.ordLink(codes[1])))
			dialog.ui.lblOrd_2.linkActivated.connect(self.webDialog)
		else:
			dialog.ui.txtClau_2.setHidden(True)
			dialog.ui.txtPer_2.setHidden(True)
			dialog.ui.lblOrd_2.setHidden(True)


		if len(codes) >= 3:
			dialog.ui.txtClau_3.setText(u'{}'.format(str(codes[2])))
			dialog.ui.txtPer_3.setText(u'{:02.2f}'.format(percents[2]))
			dialog.ui.lblOrd_3.setText(u'{}'.format(self.ordLink(codes[2])))
			dialog.ui.lblOrd_3.linkActivated.connect(self.webDialog)
		else:
			dialog.ui.txtClau_3.setHidden(True)
			dialog.ui.txtPer_3.setHidden(True)
			dialog.ui.lblOrd_3.setHidden(True)


		if len(codes) >= 4:
			dialog.ui.txtClau_4.setText(u'{}'.format(str(codes[3])))
			dialog.ui.txtPer_4.setText(u'{:02.2f}'.format(percents[3]))
			dialog.ui.lblOrd_4.setText(u'{}'.format(self.ordLink(codes[3])))
			dialog.ui.lblOrd_4.linkActivated.connect(self.webDialog)
		else:
			dialog.ui.txtClau_4.setHidden(True)
			dialog.ui.txtPer_4.setHidden(True)
			dialog.ui.lblOrd_4.setHidden(True)



		# PDF generation functions
		def makeShowUbicacioPdf():
			ubicacioComposition = self.iface.activeComposers()[Const.PDF_UBICACIO].composition()
			filename = os.path.join(self.zones_folder, '{}.pdf'.format(id));
			if ubicacioComposition.exportAsPDF(filename):
				openFile(filename)
			else:
				print "No s'ha pogut fer."

		def makeShowZonesPdf(): # TODO
			pass

		# Connect the click signal to the functions
		dialog.ui.lblClass.linkActivated.connect(self.webDialog)
		dialog.ui.btnParcelaPdf.clicked.connect(makeShowUbicacioPdf)
		dialog.ui.btnClauPdf_1.clicked.connect(makeShowZonesPdf)

		# SHow the dialog (execute it)
		dialog.exec_()



	def queryInfo(self, id):
		"""Querys the information on the database."""
		#self.cursor.fetchall(); # ignore any residual information (should never do anything)
		self.cursor.execute(Const.QUERY, [id])
		return self.cursor.fetchone()


	def sectorLink(self, id):
		filename = '{:s}.htm'.format(id)
		return Const.LINK_NORMATIVA.format(os.path.join(self.sector_folder, filename))

	def classiLink(self, id):
		filename = '{:s}.htm'.format(id)
		return Const.LINK_NORMATIVA.format(os.path.join(self.classi_folder, filename))

	def ordLink(self, code):
		filename = '{:s}.htm'.format(code)
		return Const.LINK_NORMATIVA.format(os.path.join(self.ord_folder, filename))


	def webDialog(self, url):
		dialog = self.initDialog(Ui_DocsView, Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowMaximizeButtonHint)
		dialog.ui.webView.setUrl(QUrl(url))

		# TODO export & print
		def printBtn():
			printer = self.askPrinter()
			if printer is not None:
				#printer.setPageMargins(left, top, right, bottom, QPrinter.Millimeter)
				dialog.ui.webView.print_(printer)

		def exportPDF():
			printer = self.getPDFPrinter(
				os.path.splitext(os.path.basename(url))[0] # Get name without extension
			)
			if printer is not None:
				#printer.setPageMargins(left, top, right, bottom, QPrinter.Millimeter)
				dialog.ui.webView.print_(printer)

		dialog.ui.imprimirBtn.clicked.connect(printBtn)
		dialog.ui.pdfBtn.clicked.connect(exportPDF)

		dialog.exec_()


	def initDialog(self, Class, flags=Qt.WindowSystemMenuHint | Qt.WindowTitleHint):
		"""Initializes a Dialog with the usual parameters of this plugin."""
		# This function makes the code more pretty
		dialog = QDialog(None, flags)
		dialog.ui = Class()
		dialog.ui.setupUi(dialog)
		dialog.setAttribute(Qt.WA_DeleteOnClose)
		dialog.setWindowIcon(self.icon)
		dialog.setWindowModality(Qt.WindowModal)
		return dialog

	def getPDFPrinter(self, name):
		printer = QPrinter(QPrinter.HighResolution)
		path = QFileDialog.getSaveFileName(
			None,
			None,
			os.path.join(
				self.settings.value("save path", os.path.expanduser("~")),      #default folder
				name+".pdf" #default filename
			),
			"PDF (*.pdf)"
		)
		if path is not None and path != "":
			self.settings.setValue("save path", os.path.dirname(path))
			printer.setOutputFileName(path)
			return printer
		else:
			return None

	def askPrinter(self):
		printer = QPrinter()
		select = QPrintDialog(printer)
		if select.exec_():
			return printer
		else:
			return None







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
		os.remove(os.path.join(folder, f))

def openFile(path):
	"""Opens a file with the default application."""

	# Multiple OS support
	if sys.platform.startswith('darwin'):
		subprocess.Popen(['open', path])
	elif os.name == 'nt':
		os.startfile(path)
	elif os.name == 'posix':
		subprocess.Popen(['xdg-open', path])

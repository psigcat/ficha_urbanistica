# -*- coding: utf-8 -*-
"""Main file of the project ficha_urbanistica. This contains the main class as well as all the importan work."""

import os
import sys
import io
import ConfigParser
import psycopg2
from PyQt4 import QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

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


		# Find and safe the plugin's icon
		filename = os.path.abspath(os.path.join(self.plugin_dir, 'icon.png'))
		self.icon = QIcon(str(filename))

		self.style_doc_path = os.path.join(self.plugin_dir, 'config/selected_style.qml')

		self.action = None

		self.projectChange()

	def projectChange(self):
		# Check if there is an actual project
		if not QgsProject.instance().title():
			return
		
		self.project_folder = QgsProject.instance().homePath()
		if not self.project_folder:
			self.project_folder = self.plugin_dir

		config_file = os.path.join(self.project_folder, 'ficha_urbanistica.conf')

		try:
			self.config = Config(config_file)
		except IOError:
			self.error(u"No s'ha trobat el fitxer de configuració del plugin.")
			return

		# Save and make, if they don't exist, the docs folders.
		self.sector_folder = os.path.join(self.config.docs_folder, 'sectors')
		self.classi_folder = os.path.join(self.config.docs_folder, 'classificacio')
		self.ord_folder = os.path.join(self.config.docs_folder, 'ordenacions')

		# Disconnect the server
		self.cursor = None
		self.conn = None

		# Get the credentials
		service_uri = getServiceUri(self.config.service)

		if not service_uri:
			self.error(u"Hi ha algun error a la configuració del servei de la base de dades.")
			return

		# Connecting to the database
		try:
			self.conn = psycopg2.connect(service_uri)
			self.cursor = self.conn.cursor()
		except psycopg2.DatabaseError as e:
			self.error(u'Error al connectar amb la base de dades.')




	def initGui(self):
		"""Called when the gui must be generated."""

		self.tool = FichaUrbanisticaTool(self.iface.mapCanvas(), self)

		# Add menu and toolbar entries (basically allows to activate it)
		self.action = QAction(self.icon, tr("Ficha urbanística"), self.iface.mainWindow())
		self.action.setCheckable(True)
		QObject.connect(self.action, SIGNAL('triggered()'), self.activateTool)
		self.iface.addToolBarIcon(self.action)
		self.iface.addPluginToMenu(qu("Ficha urbanística"), self.action)
		self.iface.mapCanvas().mapToolSet.connect(self.deactivateTool)


	def activateTool(self):
		"""Called when the plugin icon is toggled on"""
		self.iface.mapCanvas().setMapTool(self.tool)
		self.action.setChecked(True)


	def deactivateTool(self):
		"""Called when the plugin icon is toggled off"""
		self.action.setChecked(False)


	def unload(self):
		"""Called when the plugin is being unloaded."""
		self.iface.removePluginMenu(qu("Ficha urbanística"), self.action)
		self.iface.removeToolBarIcon(self.action)



	def run(self):
		"""Called when the plugin's icon is pressed."""

		if not hasattr(self, 'config'):
			self.projectChange()
			# check if projectChange was successful
			if not hasattr(self, 'config'):
				return
		
		# Get the active layer (where the selected form is).
		layer = self.iface.activeLayer()
		if layer is None:
			return

		# single feature
		features = layer.selectedFeatures()
		if len(features) != 1:
			return

		feature = features[0]
		id_index = feature.fieldNameIndex(self.config.plot_id)

		if id_index < 0:
			return;


		# Query the necesary information
		#self.cursor.fetchall(); # ignore any residual information (should never do anything)
		self.cursor.execute(Const.MAIN_QUERY, [feature[id_index]])
		info = self.cursor.fetchone()

		# Make dialog and set its atributes
		dialog = self.initDialog(Ui_Form)
		dialog.setFixedSize(dialog.size())

		# Static links
		dialog.ui.lblCondGenerals.setText(Const.LINK_COND.format(self.config.docs_folder))
		dialog.ui.lblCondGenerals.linkActivated.connect(self.webDialog)
		
		dialog.ui.lblDotacioAparc.setText(Const.LINK_DOT.format(self.config.docs_folder))
		dialog.ui.lblDotacioAparc.linkActivated.connect(self.webDialog)
		
		dialog.ui.lblRegulacioAparc.setText(Const.LINK_REG.format(self.config.docs_folder))
		dialog.ui.lblRegulacioAparc.linkActivated.connect(self.webDialog)
		
		dialog.ui.lblParamFinca.setText(Const.LINK_FINCA.format(self.config.docs_folder))
		dialog.ui.lblParamFinca.linkActivated.connect(self.webDialog)
		
		dialog.ui.lblParamEdificacio.setText(Const.LINK_EDIF.format(self.config.docs_folder))
		dialog.ui.lblParamEdificacio.linkActivated.connect(self.webDialog)
		


		# Show data
		dialog.ui.refcat.setText(u'{}'.format( info[Const.REFCAT] ))
		dialog.ui.area.setText(u'{}'.format( info[Const.AREA] ))
		dialog.ui.txtAdreca.setText(u'{}'.format( info[Const.ADRECA] ))

		if info[Const.CODI_SECTOR] is not None: # It may not be part of any sector
			dialog.ui.txtSector.setText(u'{} - {}'.format( info[Const.CODI_SECTOR], info[Const.DESCR_SECTOR] ))
			dialog.ui.lblSector.setText(self.sectorLink('{}'.format(info[Const.CODI_SECTOR])))
		else:
			dialog.ui.lblSector.setHidden(True)

		dialog.ui.txtClass.setText(u'{} - {}'.format( info[Const.CODI_CLASSI], info[Const.DESCR_CLASSI] ))
		dialog.ui.lblClass.setText(self.classiLink('{}'.format( info[Const.CODI_CLASSI] )))


		codes = info[Const.CODI_ZONES]
		percents = info[Const.PERCENT_ZONES]
		general_codes = info[Const.CODI_GENERAL_ZONES]

		if len(codes) >= 1:
			dialog.ui.txtClau_1.setText(u'{}'.format(str(codes[0])))
			dialog.ui.txtPer_1.setText(u'{:02.2f}'.format(percents[0]))
			dialog.ui.lblOrd_1.setText(u'{}'.format(self.ordLink(general_codes[0])))
			dialog.ui.lblOrd_1.linkActivated.connect(self.webDialog)


		if len(codes) >= 2:
			dialog.ui.txtClau_2.setText(u'{}'.format(str(codes[1])))
			dialog.ui.txtPer_2.setText(u'{:02.2f}'.format(percents[1]))
			dialog.ui.lblOrd_2.setText(u'{}'.format(self.ordLink(general_codes[1])))
			dialog.ui.lblOrd_2.linkActivated.connect(self.webDialog)
		else:
			dialog.ui.txtClau_2.setHidden(True)
			dialog.ui.txtPer_2.setHidden(True)
			dialog.ui.lblOrd_2.setHidden(True)


		if len(codes) >= 3:
			dialog.ui.txtClau_3.setText(u'{}'.format(str(codes[2])))
			dialog.ui.txtPer_3.setText(u'{:02.2f}'.format(percents[2]))
			dialog.ui.lblOrd_3.setText(u'{}'.format(self.ordLink(general_codes[2])))
			dialog.ui.lblOrd_3.linkActivated.connect(self.webDialog)
		else:
			dialog.ui.txtClau_3.setHidden(True)
			dialog.ui.txtPer_3.setHidden(True)
			dialog.ui.lblOrd_3.setHidden(True)


		if len(codes) >= 4:
			dialog.ui.txtClau_4.setText(u'{}'.format(str(codes[3])))
			dialog.ui.txtPer_4.setText(u'{:02.2f}'.format(percents[3]))
			dialog.ui.lblOrd_4.setText(u'{}'.format(self.ordLink(general_codes[3])))
			dialog.ui.lblOrd_4.linkActivated.connect(self.webDialog)
		else:
			dialog.ui.txtClau_4.setHidden(True)
			dialog.ui.txtPer_4.setHidden(True)
			dialog.ui.lblOrd_4.setHidden(True)



		# PDF generation functions
		def makeShowUbicacioPdf():
			# Make temporary layer
			vl = self.iface.addVectorLayer("Polygon?crs=epsg:25831&field=id:integer&index=yes", "temp_print_polygon", "memory")
			vl.loadNamedStyle(self.style_doc_path)
			pr = vl.dataProvider()

			fet = QgsFeature()
			fet.setGeometry(QgsGeometry(feature.geometry())) #copy the geometry
			pr.addFeatures([fet])
			vl.updateExtents()

			moveLayer(vl, 0)

			def refreshed():
				# Disconnect signal
				self.iface.mapCanvas().mapCanvasRefreshed.disconnect(refreshed)

				# Get composition
				composition = None
				for item in self.iface.activeComposers():
					if item.composerWindow().windowTitle() == Const.PDF_UBICACIO:
						composition = item.composition()
						break

				if composition is None:
					return

				# Set values
				QgsExpressionContextUtils.setProjectVariable('refcat', info[Const.REFCAT])
				QgsExpressionContextUtils.setProjectVariable('area', '{:.0f}'.format(info[Const.AREA]))
				QgsExpressionContextUtils.setProjectVariable('adreca', info[Const.ADRECA])


				# Set main map to the propper position
				main_map = composition.getComposerItemById('Mapa principal')
				centerMap(main_map, feature)

				# Make PDF
				filename = os.path.join(self.zones_folder, '{}.pdf'.format(info[Const.REFCAT]));
				if composition.exportAsPDF(filename):
					openFile(filename)
				else:
					self.error(u"No s'ha pogut convertir a PDF.")

				# Delete temporary layer
				QgsMapLayerRegistry.instance().removeMapLayers( [vl.id()] )

				# Repaint again
				self.iface.mapCanvas().refresh()

			self.iface.mapCanvas().mapCanvasRefreshed.connect(refreshed)
			self.iface.mapCanvas().refresh()

		def makeShowZonesPdf(): # TODO
			pass

		# Connect the click signal to the functions
		dialog.ui.lblClass.linkActivated.connect(self.webDialog)
		dialog.ui.btnParcelaPdf.clicked.connect(makeShowUbicacioPdf)
		dialog.ui.btnClauPdf_1.clicked.connect(makeShowZonesPdf)

		# SHow the dialog (execute it)
		dialog.exec_()




	def webDialog(self, url):
		dialog = self.initDialog(Ui_DocsView, Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowMaximizeButtonHint)
		dialog.ui.webView.setUrl(QUrl(url))

		# TODO export & print
		def printBtn():
			printer = askPrinter()
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

	def sectorLink(self, id):
		filename = '{:s}.htm'.format(id)
		return Const.LINK_NORMATIVA.format(os.path.join(self.sector_folder, filename))

	def classiLink(self, id):
		filename = '{:s}.htm'.format(id)
		return Const.LINK_NORMATIVA.format(os.path.join(self.classi_folder, filename))

	def ordLink(self, code):
		filename = '{:s}.htm'.format(code)
		return Const.LINK_NORMATIVA.format(os.path.join(self.ord_folder, filename))


	def error(self, msg):
		# The QGis documentation recommends using the more user-friendly QGIS Message Bar
		# instead of modal message boxes to show information to the user
		self.iface.messageBar().pushMessage("Error", msg, level=QgsMessageBar.CRITICAL)

		# messageBox = QMessageBox(QMessageBox.Critical, tr("Error"), msg)
		# messageBox.setWindowIcon(self.icon)
		# messageBox.exec_()



class Config:
	"""Class that loads and shows the configuration"""

	def __init__(self, file):

		with open(file) as f:
			config_sample = f.read()

		config = ConfigParser.RawConfigParser()
		config.readfp(io.BytesIO(config_sample))

		for service in config.sections():

			if config.has_option(service, 'docs_folder'):
				docs = config.get(service, 'docs_folder')
				if os.path.isabs(docs):
					self.docs_folder = docs
				else:
					self.docs_folder = os.path.join(os.path.dirname(file), docs)
			else:
				self.docs_folder = os.path.join(os.path.dirname(__file__), 'html')

			if config.has_option(service, 'service'):
				self.service = config.get(service, 'service')

			if config.has_option(service, 'id_name'):
				self.plot_id = config.get(service, 'id_name')
			else:
				self.plot_id = 'id'


class FichaUrbanisticaTool(QgsMapTool):
	def __init__(self, canvas, plugin):
		super(QgsMapTool, self).__init__(canvas)
		self.canvas = canvas
		self.plugin = plugin
		self.setCursor(Qt.PointingHandCursor)

	def canvasReleaseEvent(self, e):
		layer = self.canvas.currentLayer()
		if layer is None:
			return

		point = e.mapPoint()

		radius = self.canvas.mapUnitsPerPixel()

		# FIXME: It selects two features when clicking at an edge...
		rect = QgsRectangle(point.x(), point.y(), point.x() + radius, point.y() + radius)
		layer.selectByRect(rect)
		self.plugin.run()


# Utilities

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


def get_pgservices_conf(path):
	r = {}
	if not path:
		return r

	try:
		with open(path) as file:
			config_sample = file.read()
	except IOError:
		return r

	config = ConfigParser.RawConfigParser()
	config.readfp(io.BytesIO(config_sample))

	for service in config.sections():
		if (config.has_option(service, 'host') and
			config.has_option(service, 'dbname') and
			config.has_option(service, 'user') and
			config.has_option(service, 'password')):

				if config.has_option(service, 'port'):
					port = config.get(service, 'port')
				else:
					port = '5432'

				r[service] = u'host={} port={} dbname={} user={} password={}'.format(
					config.get(service, 'host'),
					port,
					config.get(service, 'dbname'),
					config.get(service, 'user'),
					config.get(service, 'password')
				)

	return r

def getServiceUri(config_service):
	this_folder = os.path.dirname(__file__)
	# Look at the pg_config files
	pg_services =      get_pgservices_conf( os.path.join(this_folder, 'config', 'pg_service.conf')                )
	pg_services = dict(get_pgservices_conf( os.path.expanduser('~/.pg_service.conf')                              ).items() + pg_services.items())
	pg_services = dict(get_pgservices_conf( os.path.join(os.environ.get('PGSYSCONFDIR') or '', 'pg_service.conf') ).items() + pg_services.items())
	pg_services = dict(get_pgservices_conf( os.environ.get('PGserviceFILE')                                       ).items() + pg_services.items())

	if config_service:
		return pg_services.get(config_service)
	elif len(pg_services) == 1:
		return pg_services.values()[0]


def centerMap(map, feature):
	newExtent = centerRect(map.extent(), feature.geometry().boundingBox().center())
	map.setNewExtent(newExtent)

def centerRect(rect, point):
	hw = rect.width() / 2
	hh = rect.height() / 2
	xMin = point.x() - hw
	xMax = point.x() + hw
	yMin = point.y() - hh
	yMax = point.y() + hh
	return type(rect)(xMin, yMin, xMax, yMax)

def moveLayer(layer, pos):
	root = QgsProject.instance().layerTreeRoot()
	node = root.findLayer(layer.id())
	clone = node.clone()
	parent = node.parent()
	parent.insertChildNode(pos, clone)
	parent.removeChildNode(node)

def askPrinter():
	printer = QPrinter()
	select = QPrintDialog(printer)
	if select.exec_():
		return printer
	else:
		return None

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
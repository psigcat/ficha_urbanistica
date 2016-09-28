"""Main file of the project ficha_urbanistica. This contains the main class as well as all the importan work."""

# TODO add imports

import os
import psycopg2
import db_credentials

from copy import deepcopy

from PyQt4.uic import loadUi

DB_CREDENTIALS = "host={} port={} dbname={} user={} password={}".format(db_credentials.host, db_credentials.port, db_credentials.dbname, db_credentials.user, db_credentials.password)
LAYER_NAME = ""
ID_STR = "ninterno"
REPORTS_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/reports/"


class FichaUrbanistica:
	"""Main class of the project ficha_urbanistica"""


	def _init_(self, iface):
		"""Contructor"""

		# Saving iface to be reachable from the other functions
		self.iface = iface


		# Connecting to the database
		try:
			self.conn = psycopg2.connect(DB_CREDENTIALS) # Cedentials in the credentials file. The credentials should not be uploaded to the public repository
			self.cursor = conn.cursor()
		except psycopg2.DatabaseError e:
			print u'Error al connectar amb la base de dades.'
			print '{:s}'.format(e)
			print ''
			print u'No es carregarà el plugin.'
			return # This return means there is no trigger set

		self.ui = None
		self.icon = None
		self.action = None



	def initGui(self):
		"""Called when the gui must be generated."""

        # Find and safe the plugin's icon
        filename = os.path.abspath(os.path.join(self.plugin_dir, 'icon.png'))
        self.icon = QIcon(str(filename))

		# Get the ui
		uiFile = QFile(os.path.dirname(os.path.abspath(__file__))+'/ui/form.ui')
		uiFile.open(QFile.ReadOnly)
		self.ui = loadUi(uiFile)
		uiFile.close();

        # Add menu and toolbar entries (basically allows to activate it)
        self.action = QAction(self.icon, tr("Ficha urbanística"), self.iface.mainWindow())
        QObject.connect(self.action, SIGNAL('triggered()'), self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(qu("Ficha urbanística"), self.action)



	def unlaod(self):
		"""Called when the plugin is being unloaded."""
        self.iface.removePluginMenu(qu("Ficha urbanística"), self.action)
        self.iface.removeToolBarIcon(self.action)



	def run(self):
		"""Called when the plugin's icon is pressed."""
		
		# Get the active layer (where the selected form is).
		layer = self.iface.activeLayer()

		# Make sure it is the layer we think it is.
		if (layer.name() != LAYER_NAME)
			return


		# single feature
		if len(features) != 1:
            return
		openForm(features[0][ID_STR])

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
		info = queryInfo(id)

		dialog = QDialog(None, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
		dialog.ui = deepcopy(self.ui)
		dialog.ui.setupUi(dialog)

		# Set values to the data
		dialog.refcat.setText('{}'.format(info['refcat']))
		dialog.ninterno.setText('{}'.format(id))
		dialog.area.setText('{}'.format(info['area']))
		dialog.txtAdreca.setText('{}'.format(info['adreca']))

		dialog.txtSector.setText('{} - {}'.format(info['codi_sector'], info['descr_sector']))
		dialog.lblSector.setText(sectorLink('{}'.format(info['codi_sector'])))

		dialog.txtClass.setText('{} - {}'.format(info['codi_classi'], info['descr_classi']))
		dialog.lblClass.setText(classiLink('{}'.format(info['codi_classi'])))


		codes = info['codi_zones']
		percents = info['percent_zones']

		if len(codes) >= 1:
			dialog.txtClau_1.setText('{}'.format(codes[0]))
			dialog.txtPer_1.setText('{}'.format(percents[0]))
			dialog.lblOrd_1.setText('{}'.format(ordLink(codes[0])))


		if len(codes) >= 2:
			dialog.txtClau_2.setText('{}'.format(codes[1]))
			dialog.txtPer_2.setText('{}'.format(percents[1]))
			dialog.lblOrd_2.setText('{}'.format(ordLink(codes[1])))
		else
			dialog.txtClau_2.setHidden(True)
			dialog.txtPer_2.setHidden(True)
			dialog.lblOrd_2.setHidden(True)


		if len(codes) >= 3:
			dialog.txtClau_3.setText('{}'.format(codes[2]))
			dialog.txtPer_3.setText('{}'.format(percents[2]))
			dialog.lblOrd_3.setText('{}'.format(ordLink(codes[2])))
		else
			dialog.txtClau_3.setHidden(True)
			dialog.txtPer_3.setHidden(True)
			dialog.lblOrd_3.setHidden(True)


		if len(codes) >= 4:
			dialog.txtClau_4.setText('{}'.format(codes[3]))
			dialog.txtPer_4.setText('{}'.format(percents[3]))
			dialog.lblOrd_4.setText('{}'.format(ordLink(codes[3])))
		else
			dialog.txtClau_4.setHidden(True)
			dialog.txtPer_4.setHidden(True)
			dialog.lblOrd_4.setHidden(True)

		# TODO add functionality to buttons
		# btnParcelaPdf -> ubicacio
		# btnClauPdf_1 -> zones

		dialog.exec()



	def queryInfo(self, id):
		"""Querys the information on the database."""
		self.cursor.execute("SELECT * FROM data.ficha_urbanistica({:s});".format(id))
		return self.cursor.fetchall()[0]
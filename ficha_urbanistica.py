"""Main file of the project ficha_urbanistica. This contains the main class as well as all the importan work."""

# TODO add imports
import credentials

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

		# Container for all the query information 
		self.info = None;



	def initGui(self):
		"""Called when the gui must be generated."""

		pass



	def unlaod(self):
		"""Called when the plugin is being unloaded."""

		pass



	def run(self):
		"""Called when the plugin's icon is pressed."""

		pass



	def querySelectedInfo(self):
		"""Querys all the necesary information from the database about the selection."""

		# Get the selection# Gets the selected layer
        layer = self.iface.activeLayer()

        # If the selected layer is not the correct type, do nothing and return
        if layer == None or layer.type() != QgsMapLayer.VectorLayer:
            return

        # Get the selected feature AKA plot). Only a single one (end if there are none or more).
        features = layer.selectedFeatures()
        if len(features) != 1:
            return
		feature = features[0]

		# Query the information and save it to info
		self.cursor.execute("SELECT ficha_tecnica({:s});".format(feature["ninterno"]))
		self.info = self.cursor.fetchall()
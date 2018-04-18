# -*- coding: utf-8 -*-
"""Main file of the project ficha_urbanistica. This contains the main class as well as all the important work."""

import codecs
import ConfigParser
import errno
import io
import os
import psycopg2
import subprocess
import sys

from PyQt4 import QtCore
from PyQt4.QtCore import QObject, QSettings, Qt, QUrl, SIGNAL
from PyQt4.QtGui import QAction, QApplication, QCursor, QDialog, QFileDialog, QIcon, QPainter, QPixmap, QPrinter, QPrintDialog
from qgis.core import QgsExpressionContextUtils, QgsFeature, QgsGeometry, QgsMapLayerRegistry, QgsMessageLog, QgsProject, QgsRectangle
from qgis.gui import QgsMapTool, QgsMessageBar

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

        self.settings = QSettings("PSIG", "ficha_urbanistica")

        # Find and safe the plugin's icon
        filename = os.path.abspath(os.path.join(self.plugin_dir, 'icon.png'))
        self.icon = QIcon(str(filename))

        self.style_doc_path = os.path.join(self.plugin_dir, 'Styles', 'selected_parcel.qml')
        
        self.action = None

        self.dialog = None

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

        self.reports_folder = os.path.join(self.project_folder, 'informes')
        try:
            os.makedirs(self.reports_folder)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

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
        except psycopg2.DatabaseError:
            self.error(u'Error al connectar amb la base de dades.')

    def initGui(self):
        """Called when the gui must be generated."""

        self.tool = FichaUrbanisticaTool(self.iface.mapCanvas(), self)

        # Add menu and toolbar entries (basically allows to activate it)
        self.action = QAction(self.icon, u"Fitxa urbanística", self.iface.mainWindow())
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
        if len(features) < 1:
            return
        elif len(features) > 1:
            layer.setSelectedFeatures([features[0].id()])

        feature = features[0]
        id_index = feature.fieldNameIndex(self.config.plot_id)

        if id_index < 0:
            return

        # Query the necesary information
        # self.cursor.fetchall(); # ignore any residual information (should never do anything)        
        self.cursor.execute(Const.MAIN_QUERY, [int(feature[id_index])])
        info = self.cursor.fetchone()

        # Make dialog and set its atributes
        if self.dialog:
            self.dialog.close()
        self.dialog = self.initDialog(Ui_Form)
        self.dialog.setFixedSize(self.dialog.size())

        # Static links
        self.dialog.ui.lblCondGenerals.setText(Const.LINK_COND.format(self.config.docs_folder))
        self.dialog.ui.lblCondGenerals.linkActivated.connect(self.webDialog)

        self.dialog.ui.lblDotacioAparc.setText(Const.LINK_DOT.format(self.config.docs_folder))
        self.dialog.ui.lblDotacioAparc.linkActivated.connect(self.webDialog)

        self.dialog.ui.lblRegulacioAparc.setText(Const.LINK_REG.format(self.config.docs_folder))
        self.dialog.ui.lblRegulacioAparc.linkActivated.connect(self.webDialog)

        self.dialog.ui.lblParamFinca.setText(Const.LINK_FINCA.format(self.config.docs_folder))
        self.dialog.ui.lblParamFinca.linkActivated.connect(self.webDialog)

        self.dialog.ui.lblParamEdificacio.setText(Const.LINK_EDIF.format(self.config.docs_folder))
        self.dialog.ui.lblParamEdificacio.linkActivated.connect(self.webDialog)

        # Show data
        self.dialog.ui.refcat.setText(u'{}'.format(info[Const.REFCAT]))
        self.dialog.ui.area.setText((u'{}'.format(round(info[Const.AREA], 1))).rstrip('0').rstrip('.'))
        self.dialog.ui.txtAdreca.setText(u'{}'.format(info[Const.ADRECA]))

        if info[Const.CODI_SECTOR] is not None:  # It may not be part of any sector
            self.dialog.ui.txtSector.setText(u'{} - {}'.format(info[Const.CODI_SECTOR], info[Const.DESCR_SECTOR]))
            self.dialog.ui.lblSector.setText(self.sectorLink('{}'.format(info[Const.CODI_SECTOR])))
            self.dialog.ui.lblSector.linkActivated.connect(self.webDialog)
        else:
            self.dialog.ui.lblSector.setHidden(True)

        self.dialog.ui.txtClass.setText(u'{} - {}'.format(info[Const.CODI_CLASSI], info[Const.DESCR_CLASSI]))
        self.dialog.ui.lblClass.setText(self.classiLink('{}'.format(info[Const.CODI_CLASSI])))

        codes = info[Const.CODI_ZONES]
        percents = info[Const.PERCENT_ZONES]
        general_codes = info[Const.CODI_GENERAL_ZONES]

        for i in range(0, 4):
            txtClau = getattr(self.dialog.ui, 'txtClau_{}'.format(i + 1))
            txtPer = getattr(self.dialog.ui, 'txtPer_{}'.format(i + 1))
            lblOrd = getattr(self.dialog.ui, 'lblOrd_{}'.format(i + 1))
            try:
                txtClau.setText(u'{}'.format(codes[i]))
            except IndexError:
                txtClau.setHidden(True)
            try:
                txtPer.setText(u'{:02.2f}'.format(percents[i]))
            except IndexError:
                txtPer.setHidden(True)
            try:
                lblOrd.setText(u'{}'.format(self.ordLink(general_codes[i])))
                lblOrd.linkActivated.connect(self.webDialog)
            except IndexError:
                lblOrd.setHidden(True)

        # PDF generation functions
        def makeShowUbicacioPdf():
            # Make temporary layer
            vl = self.iface.addVectorLayer("Polygon?crs=epsg:25831&field=id:integer&index=yes", "temp_print_polygon", "memory")
            vl.loadNamedStyle(self.style_doc_path)
            vl.setName(u"Parcel·la seleccionada")
            pr = vl.dataProvider()

            fet = QgsFeature()
            fet.setGeometry(QgsGeometry(feature.geometry()))  # copy the geometry
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

                # Add temporal layer to composition
                legend = composition.getComposerItemById('Llegenda')
                legend_root = legend.modelV2().rootGroup()
                legend_root.insertLayer(0, vl)

                # Make PDF
                filename = os.path.join(self.reports_folder, '{}_ubicacio.pdf'.format(info[Const.REFCAT]))
                if composition.exportAsPDF(filename):
                    openFile(filename)
                else:
                    self.error(u"No s'ha pogut convertir a PDF.")

                # Delete temporary layer
                legend_root.removeLayer(vl)
                QgsMapLayerRegistry.instance().removeMapLayers([vl.id()])

                # Repaint again
                self.iface.mapCanvas().refresh()

            self.iface.mapCanvas().mapCanvasRefreshed.connect(refreshed)
            self.iface.mapCanvas().refresh()

        def makeShowZonesPdf():
            self.cursor.execute(Const.ZONES_QUERY, [int(feature[id_index])])
            rows = (row for row in self.cursor.fetchall() if row[Const.ZONES_COLUMNS.index('per_int')] >= 3)

            composition = None
            for item in self.iface.activeComposers():
                if item.composerWindow().windowTitle() == Const.PDF_ZONES:
                    composition = item.composition()
                    break
            if composition is None:
                return

            filename = os.path.join(self.reports_folder, '{}_zones.pdf'.format(info[Const.REFCAT]))
            printer = QPrinter()
            composition.beginPrintAsPDF(printer, filename)
            composition.beginPrint(printer, False)
            painter = QPainter()
            painter.begin(printer)

            first = True
            for data in rows:
                if first:
                    first = False
                else:
                    printer.newPage()
                for i, column in enumerate(Const.ZONES_COLUMNS):
                    QgsExpressionContextUtils.setProjectVariable(column, data[i])
                if info[Const.CODI_SECTOR] is not None:
                    QgsExpressionContextUtils.setProjectVariable('sec_descripcio', u'{} - {}'.format(info[Const.CODI_SECTOR], info[Const.DESCR_SECTOR]))
                else:
                    QgsExpressionContextUtils.setProjectVariable('sec_descripcio', None)
                QgsExpressionContextUtils.setProjectVariable('cla_descripcio', u'{} - {}'.format(info[Const.CODI_CLASSI], info[Const.DESCR_CLASSI]))
                composition.refreshItems()
                composition.doPrint(printer, painter)

            painter.end()
            openFile(filename)

        def destroyDialog():
            self.dialog = None

        # Connect the click signal to the functions
        self.dialog.ui.lblClass.linkActivated.connect(self.webDialog)
        self.dialog.ui.btnParcelaPdf.clicked.connect(makeShowUbicacioPdf)
        self.dialog.ui.btnClauPdf_1.clicked.connect(makeShowZonesPdf)
        self.dialog.destroyed.connect(destroyDialog)

        # SHow the dialog (execute it)
        self.dialog.exec_()

    def webDialog(self, url):
        QgsMessageLog.logMessage("Opened url: " + url)

        dialog = self.initDialog(Ui_DocsView, Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowMaximizeButtonHint)
        dialog.ui.webView.setUrl(QUrl(url))

        # TODO export & print
        def printBtn():
            printer = askPrinter()
            if printer is not None:
                # printer.setPageMargins(left, top, right, bottom, QPrinter.Millimeter)
                dialog.ui.webView.print_(printer)

        def exportPDF():
            printer = self.getPDFPrinter(
                os.path.splitext(os.path.basename(url))[0]  # Get name without extension
            )
            if printer is not None:
                # printer.setPageMargins(left, top, right, bottom, QPrinter.Millimeter)
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
                self.settings.value("save path", os.path.expanduser("~")),  # default folder
                name + ".pdf"  # default filename
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
        filepath = os.path.join(self.ord_folder, filename)
        if os.path.isfile(filepath):
            return Const.LINK_ORDENACIO.format(filepath, code)
        else:
            return code

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
        config = ConfigParser.RawConfigParser()
        try:
            config.readfp(codecs.open(file, 'r', 'utf8'))
        except UnicodeDecodeError:  #unicode error 
            config.readfp(codecs.open(file, 'r', 'cp1252'))

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

            if config.has_option(service, 'layer_name'):
                self.layer_name = config.get(service, 'layer_name')
            else:
                self.layer_name = None


class FichaUrbanisticaTool(QgsMapTool):
    def __init__(self, canvas, plugin):
        super(QgsMapTool, self).__init__(canvas)
        self.canvas = canvas
        self.plugin = plugin
        self.setCursor(QCursor(QPixmap(os.path.join(plugin.plugin_dir, 'cursor.png')), 1, 1))

    def canvasReleaseEvent(self, e):
        # Activate config layer
        if self.plugin.config.layer_name:
            registry = QgsMapLayerRegistry.instance()
            layer = registry.mapLayersByName(self.plugin.config.layer_name)[0]
            self.plugin.iface.setActiveLayer(layer)

        layer = self.canvas.currentLayer()
        if layer is None:
            return

        point = e.mapPoint()

        radius = self.canvas.mapUnitsPerPixel()

        rect = QgsRectangle(point.x(), point.y(), point.x() + radius, point.y() + radius)
        layer.selectByRect(rect)
        self.plugin.run()


# Utilities

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
    pg_services = get_pgservices_conf(os.path.join(this_folder, 'config', 'pg_service.conf'))
    pg_services = dict(get_pgservices_conf(os.path.expanduser('~/.pg_service.conf')).items() + pg_services.items())
    pg_services = dict(get_pgservices_conf(os.path.join(os.environ.get('PGSYSCONFDIR') or '', 'pg_service.conf')).items() + pg_services.items())
    pg_services = dict(get_pgservices_conf(os.environ.get('PGserviceFILE')).items() + pg_services.items())

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

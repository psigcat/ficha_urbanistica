# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'docs_view.ui'
#
# Created: Thu Oct 06 14:47:32 2016
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_DocsView(object):
    def setupUi(self, DocsView):
        DocsView.setObjectName(_fromUtf8("DocsView"))
        DocsView.resize(627, 480)
        self.verticalLayout = QtGui.QVBoxLayout(DocsView)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.imprimirBtn = QtGui.QPushButton(DocsView)
        self.imprimirBtn.setObjectName(_fromUtf8("imprimirBtn"))
        self.horizontalLayout.addWidget(self.imprimirBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.webView = QtWebKit.QWebView(DocsView)
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.verticalLayout.addWidget(self.webView)

        self.retranslateUi(DocsView)
        QtCore.QMetaObject.connectSlotsByName(DocsView)

    def retranslateUi(self, DocsView):
        DocsView.setWindowTitle(_translate("DocsView", "Visor de documents", None))
        self.imprimirBtn.setText(_translate("DocsView", "Imprimir", None))

from PyQt4 import QtWebKit

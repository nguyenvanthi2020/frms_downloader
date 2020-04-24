# -*- coding: utf-8 -*-
"""
/***************************************************************************
 frms_downloader
                                 A QGIS plugin
 This plugin to download FMRS Map
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-04-21
        git sha              : $Format:%H$
        copyright            : (C) 2020 by IFEE
        email                : nguyenvanthi@ifee.edu.vn
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
#from qgis.core import QgsVectorLayer, QgsDataSourceUri
from PyQt5.QtCore import QTimer
from PyQt5.QtSql import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
# Initialize Qt resources from file resources.py
from .resources import *
from qgis.gui import QgsMessageBar
from qgis.core import *
# Import the code for the DockWidget
from .frms_downloader_dockwidget import frms_downloaderDockWidget
import os.path
import psycopg2
import socket
import subprocess
from subprocess import Popen
import os
from itertools import groupby
import pathlib
from pathlib import Path
import osgeo.gdal  # NOQA
from osgeo import gdal, ogr
from .frms_libraries import *

class frms_downloader:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'frms_downloader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&FRMS Downloader')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'frms_downloader')
        self.toolbar.setObjectName(u'frms_downloader')

        #print "** INITIALIZING frms_downloader"

        self.pluginIsActive = False
        self.dockwidget = None

    def laydanhsachtinh(self):
        self.dockwidget.inProvince.clear()
        tentinh = self.dockwidget.inProvince.currentText()      
        if self.dockwidget.inProvince.currentIndex() == 0:
            _crs = "EPSG:3405"
        else:
            _crs = self.prj_crs(tentinh)
        tinhs = docdstinh()
        if self.dockwidget.langEng.isChecked():
            self.dockwidget.inProvince.addItems(['-- Select a Province --'])
        else:
            self.dockwidget.inProvince.addItems(['-- Chọn tỉnh --'])
        for tinh in tinhs:
            tname = tinh['TINH']
            tcode = tinh['MATINH']
            self.dockwidget.inProvince.addItems([tname])

    def laydanhsachhuyen(self):
        self.dockwidget.inDistrict.clear()
        tentinh = self.dockwidget.inProvince.currentText()
        
        if self.dockwidget.inProvince.currentIndex() == 0:
            _crs = "EPSG:3405"
        else:
            _crs = self.prj_crs(tentinh)
        self.dockwidget.outProjection.setCrs(QgsCoordinateReferenceSystem(_crs))
        listhuyen = docdshuyen()
        if self.dockwidget.langEng.isChecked():
            self.dockwidget.inDistrict.addItems(['-- Select a District --'])
        else:
            self.dockwidget.inDistrict.addItems(['-- Chọn huyện --'])
        for chon in listhuyen:
            if chon['TINH'] == tentinh:
                hname = chon['HUYEN']
                hcode = chon['MAHUYEN']
                self.dockwidget.inDistrict.addItems([hname])

    def laydanhsachxa(self):
        self.dockwidget.inCommune.clear()
        tentinh = self.dockwidget.inProvince.currentText()
        tenhuyen = self.dockwidget.inDistrict.currentText()

        listxa = docdsxa()
        if self.dockwidget.langEng.isChecked():
            self.dockwidget.inCommune.addItems(['-- Select a Commune --'])
        else:
            self.dockwidget.inCommune.addItems(['-- Chọn xã --'])
        for xachon in listxa:
            if xachon['HUYEN'] == tenhuyen:
                xname = xachon['XA']
                xcode = xachon['MAXA']
                self.dockwidget.inCommune.addItems([xname])
    def laymacode(self):
        tenxa = self.dockwidget.inCommune.currentText()
        tenhuyen = self.dockwidget.inDistrict.currentText()
        tentinh = self.dockwidget.inProvince.currentText()
        if self.dockwidget.inCommune.currentIndex() > 0:
            listxa = docdsxa()
            for xachon in listxa:
                if xachon['XA'] == tenxa:
                    if xachon['HUYEN'] == tenhuyen:
                        if xachon['TINH'] == tentinh:
                            code = xachon['MAXA']
                            syn = 'commune_code = ' + code
                            return syn
                            
        elif self.dockwidget.inDistrict.currentIndex() > 0:
            listhuyen = docdshuyen()
            for huyenchon in listhuyen:
                if huyenchon['TINH'] == tentinh:
                    if huyenchon['HUYEN'] == tenhuyen:
                        code = huyenchon['MAHUYEN']
                        syn = 'district_code = ' + code
                        return syn
        else:
            listtinh = docdstinh()
            for tinhchon in listtinh:
                if tinhchon['TINH'] == tentinh:
                    code = tinhchon['MATINH']
                    syn = 'province_code = ' + code
                    return syn
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('frms_downloader', message)
    def check_conn(self):
        # Check postgres is running
        inhost = self.set_defauled()["host"]
        inport = self.dockwidget.inPort.text()
        indatabase = "data_forest"
        inuser = self.dockwidget.inUsername.text()
        inpass = self.dockwidget.inPassword.text()
        try:
            conn = psycopg2.connect(database = indatabase, user = inuser, password= inpass, host = inhost, port= inport)
            cursor = conn.cursor()
            self.dockwidget.btn_start.setEnabled(False)
            self.dockwidget.btn_stop.setEnabled(True)
            self.iface.messageBar().pushMessage(
                "You are connecting to the " + inhost,
                level=Qgis.Success, duration=20)
        except:
            self.dockwidget.btn_start.setEnabled(True)
            self.dockwidget.btn_stop.setEnabled(False)
            self.iface.messageBar().pushMessage(
                "Cannot connecting to the " + inhost,
                level=Qgis.Critical, duration=20)
    def start_db(self):
        inhost = self.set_defauled()["host"]
        start_dir = QFileDialog.getExistingDirectory(caption="Choose Postgres folder",directory="",options=QFileDialog.ShowDirsOnly)
        start_part = f'{start_dir}/startlocaldb.bat'
        #subprocess.call([start_part])
        subprocess.Popen(start_part, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        self.dockwidget.btn_start.setEnabled(False)
        self.dockwidget.btn_stop.setEnabled(True)
        self.iface.messageBar().pushMessage(
            "You are connecting to the " + inhost,
            level=Qgis.Success, duration=20)
    def stop_db(self):
        inhost = self.set_defauled()["host"]
        start_dir = QFileDialog.getExistingDirectory(caption="Choose Postgres folder",directory="",options=QFileDialog.ShowDirsOnly)
        start_part = f'{start_dir}/stoplocaldb.bat'
        #subprocess.call([start_part])
        subprocess.Popen(start_part, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        self.dockwidget.btn_start.setEnabled(True)
        self.dockwidget.btn_stop.setEnabled(False)
        self.iface.messageBar().pushMessage(
            "You are disconnected to the " + inhost,
            level=Qgis.Warning, duration=20)
    def save_as(self):
        # dir = QFileDialog.getExistingDirectory(caption="Choose a folder", directory="",
        #                                        options=QFileDialog.ShowDirsOnly)
        dir = QFileDialog.getSaveFileName(caption="Save F:xile",directory = "", filter= "Shape file(*.shp)", options = QFileDialog.Options() )[0]

        self.dockwidget.outPath.setText(dir)
    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/frms_downloader/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'FRMS Downloader'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING frms_downloader"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD frms_downloader"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&frms_downloader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING frms_downloader"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = frms_downloaderDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)
            self.dockwidget.langEng.clicked.connect(self.language)
            self.dockwidget.langVie.clicked.connect(self.language)
            self.dockwidget.btn_checkcon.clicked.connect(self.check_conn)
            self.dockwidget.btn_start.clicked.connect(self.start_db)
            self.dockwidget.btn_stop.clicked.connect(self.stop_db)
            self.dockwidget.btn_browse.clicked.connect(self.save_as)
            self.dockwidget.inHost.addItems(['LOCAL', 'VNFOREST'])
            self.dockwidget.inHost.currentIndexChanged.connect(self.set_defauled)
            self.dockwidget.inPort.setText("5433")
            self.dockwidget.inUsername.setText("postgres")
            self.dockwidget.inPassword.setText("vidagis")
            self.dockwidget.langEng.clicked.connect(self.laydanhsachtinh)
            self.dockwidget.langVie.clicked.connect(self.laydanhsachtinh)
            self.laydanhsachtinh()
            self.laydanhsachhuyen()
            self.laydanhsachxa()
            self.dockwidget.inProvince.currentIndexChanged.connect(self.laydanhsachhuyen)
            self.dockwidget.inDistrict.currentIndexChanged.connect(self.laydanhsachxa)  
            self.dockwidget.btn_download.clicked.connect(self.download_map)
            #_crs = self.prj_crs()
            self.dockwidget.outProjection.setCrs(QgsCoordinateReferenceSystem('EPSG:3405'))
            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
            
    def download_map(self):
        inhost = self.set_defauled()["host"]
        inport = self.dockwidget.inPort.text()
        indatabase = "data_forest"
        inuser = self.dockwidget.inUsername.text()
        inpass = self.dockwidget.inPassword.text()       
        outpath = self.dockwidget.outPath.text()
        crs = self.dockwidget.outProjection.crs()
        _tinh = self.dockwidget.inProvince.currentText()
        if _tinh == "-- Select a Province --":
            self.iface.messageBar().pushMessage(
            "Cannot download your map! Let's choose a Province and try download again",
            level=Qgis.Warning, duration=20)
        else:
            code = self.laymacode()
            sql = query(code)
            bname = os.path.split(outpath)[1]
            fname = os.path.splitext(bname)[0]        
         
            try: 
                uri = QgsDataSourceUri()
                uri.setConnection(inhost, inport, indatabase, inuser, inpass)
                uri.setDataSource("", u'(%s\n)' % sql, "geom", "", "tt")
                vlayer = QgsVectorLayer(uri.uri(),fname,"postgres")
                QgsVectorFileWriter.writeAsVectorFormat(vlayer, outpath, "UTF-8", crs, "ESRI Shapefile")
                shp =  QgsVectorLayer(outpath, fname, 'ogr')
                layer = QgsProject.instance().addMapLayer(shp)
                self.iface.messageBar().pushMessage(
                "Your map was downloaded sucessfully and strored in " + outpath,
                level=Qgis.Success, duration=20)
            except:
                self.iface.messageBar().pushMessage(
                "Cannot download your map",
                level=Qgis.Warning, duration=20)
        
    def prj_crs(self, _tinh):
        _dstinh = docdstinh()
        for tinh in _dstinh:
            if tinh['TINH'] == _tinh:
                _crs = tinh['CRS']
                return _crs
    def set_defauled(self):
        ind = self.dockwidget.inHost.currentIndex()
        if ind == 0:
            host = "localhost"
            use = "postgres"
            pas = "vidagis"
            port = "5433"
            self.dockwidget.inPort.setText(port)
            self.dockwidget.inUsername.setText(use)
            self.dockwidget.inPassword.setText(pas)
            defaul = {
            "host": host,
            "use": use,
            "pas": pas,
            "port": port
            }
            return defaul
            
        else:
            host = "vnforest.gov.vn"
            use = ""
            pas = ""
            port = "5433"
            self.dockwidget.inPort.setText(port)
            self.dockwidget.inUsername.setText(use)
            self.dockwidget.inPassword.setText(pas)
            defaul = {
            "host": host,
            "use": use,
            "pas": pas,
            "port": port
            }
            return defaul
    def language(self):
        if self.dockwidget.langEng.isChecked():
            self.dockwidget.lbl_lang.setText('Language')
            self.dockwidget.lbl_database.setText('Connection')
            self.dockwidget.lbl_host.setText('Host')
            self.dockwidget.lbl_port.setText('Port')
            self.dockwidget.lbl_username.setText('Username')
            self.dockwidget.lbl_password.setText('Password')
            self.dockwidget.lbl_province.setText('Province')
            self.dockwidget.lbl_district.setText('District')
            self.dockwidget.lbl_commune.setText('Commune')
            self.dockwidget.lbl_saveas.setText('Save as')
            self.dockwidget.btn_checkcon.setText('CHECK')
            self.dockwidget.btn_start.setText('START')
            self.dockwidget.btn_stop.setText('STOP')
            self.dockwidget.btn_browse.setText('BROWSE')
            self.dockwidget.btn_download.setText('DOWNLOAD')
        else:
            self.dockwidget.lbl_lang.setText('Ngôn ngữ')
            self.dockwidget.lbl_database.setText('Kết nối')
            self.dockwidget.lbl_host.setText('Máy chủ')
            self.dockwidget.lbl_port.setText('Cổng')
            self.dockwidget.lbl_username.setText('Tài khoản')
            self.dockwidget.lbl_password.setText('Mật khẩu')
            self.dockwidget.lbl_province.setText('Tỉnh')
            self.dockwidget.lbl_district.setText('Huyện')
            self.dockwidget.lbl_commune.setText('Xã')
            self.dockwidget.lbl_saveas.setText('Lưu thành')
            self.dockwidget.btn_checkcon.setText('KIỂM TRA')
            self.dockwidget.btn_start.setText('KHỞI ĐỘNG')
            self.dockwidget.btn_stop.setText('DỪNG')
            self.dockwidget.btn_browse.setText('DUYỆT')
            self.dockwidget.btn_download.setText('TẢI XUỐNG')        
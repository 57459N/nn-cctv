# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
    QMenu, QMenuBar, QSizePolicy, QSpacerItem,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1920, 1080)
        self.actionSaveSave = QAction(MainWindow)
        self.actionSaveSave.setObjectName(u"actionSaveSave")
        self.actionLoadSave = QAction(MainWindow)
        self.actionLoadSave.setObjectName(u"actionLoadSave")
        self.actionVSDroidcam = QAction(MainWindow)
        self.actionVSDroidcam.setObjectName(u"actionVSDroidcam")
        self.actionVSCameraByIndex = QAction(MainWindow)
        self.actionVSCameraByIndex.setObjectName(u"actionVSCameraByIndex")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(30, 60, 1821, 931))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.MainHLayout = QHBoxLayout()
        self.MainHLayout.setObjectName(u"MainHLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.TextLabel = QLabel(self.verticalLayoutWidget)
        self.TextLabel.setObjectName(u"TextLabel")
        self.TextLabel.setMaximumSize(QSize(300, 16777215))

        self.verticalLayout_2.addWidget(self.TextLabel)

        self.StudentsListLayout = QVBoxLayout()
        self.StudentsListLayout.setObjectName(u"StudentsListLayout")

        self.verticalLayout_2.addLayout(self.StudentsListLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.MainHLayout.addLayout(self.verticalLayout_2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.MainHLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.MainHLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1920, 33))
        self.menuMenu = QMenu(self.menubar)
        self.menuMenu.setObjectName(u"menuMenu")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        self.menuVideo_sourse = QMenu(self.menuSettings)
        self.menuVideo_sourse.setObjectName(u"menuVideo_sourse")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuMenu.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menuMenu.addAction(self.actionSaveSave)
        self.menuMenu.addAction(self.actionLoadSave)
        self.menuSettings.addAction(self.menuVideo_sourse.menuAction())
        self.menuVideo_sourse.addAction(self.actionVSDroidcam)
        self.menuVideo_sourse.addAction(self.actionVSCameraByIndex)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionSaveSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.actionLoadSave.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.actionVSDroidcam.setText(QCoreApplication.translate("MainWindow", u"Droidcam", None))
        self.actionVSCameraByIndex.setText(QCoreApplication.translate("MainWindow", u"Camera by index", None))
        self.TextLabel.setText(QCoreApplication.translate("MainWindow", u"List of Students", None))
        self.menuMenu.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuSettings.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.menuVideo_sourse.setTitle(QCoreApplication.translate("MainWindow", u"Video sourse", None))
    # retranslateUi


# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'NotesBrowser.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_dlg_NotesBrowser(object):
    def setupUi(self, dlg_NotesBrowser):
        if not dlg_NotesBrowser.objectName():
            dlg_NotesBrowser.setObjectName(u"dlg_NotesBrowser")
        dlg_NotesBrowser.resize(1294, 696)
        self.verticalLayout_4 = QVBoxLayout(dlg_NotesBrowser)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.splitter = QSplitter(dlg_NotesBrowser)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.w_notes_list = QWidget(self.splitter)
        self.w_notes_list.setObjectName(u"w_notes_list")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_notes_list.sizePolicy().hasHeightForWidth())
        self.w_notes_list.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QVBoxLayout(self.w_notes_list)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.l_identifier = QLabel(self.w_notes_list)
        self.l_identifier.setObjectName(u"l_identifier")

        self.verticalLayout_3.addWidget(self.l_identifier)

        self.tw_identifier = QTreeWidget(self.w_notes_list)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.tw_identifier.setHeaderItem(__qtreewidgetitem)
        self.tw_identifier.setObjectName(u"tw_identifier")
        self.tw_identifier.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tw_identifier.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tw_identifier.setIndentation(10)
        self.tw_identifier.header().setVisible(False)

        self.verticalLayout_3.addWidget(self.tw_identifier)

        self.splitter.addWidget(self.w_notes_list)
        self.w_notes = QWidget(self.splitter)
        self.w_notes.setObjectName(u"w_notes")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(30)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.w_notes.sizePolicy().hasHeightForWidth())
        self.w_notes.setSizePolicy(sizePolicy1)
        self.verticalLayout = QVBoxLayout(self.w_notes)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.w_labels = QHBoxLayout()
        self.w_labels.setObjectName(u"w_labels")
        self.l_notes = QLabel(self.w_notes)
        self.l_notes.setObjectName(u"l_notes")

        self.w_labels.addWidget(self.l_notes)

        self.l_notesRight = QLabel(self.w_notes)
        self.l_notesRight.setObjectName(u"l_notesRight")

        self.w_labels.addWidget(self.l_notesRight)


        self.verticalLayout.addLayout(self.w_labels)

        self.w_contents = QTextEdit(self.w_notes)
        self.w_contents.setObjectName(u"w_contents")

        self.verticalLayout.addWidget(self.w_contents)

        self.splitter.addWidget(self.w_notes)

        self.verticalLayout_4.addWidget(self.splitter)


        self.retranslateUi(dlg_NotesBrowser)

        QMetaObject.connectSlotsByName(dlg_NotesBrowser)
    # setupUi

    def retranslateUi(self, dlg_NotesBrowser):
        dlg_NotesBrowser.setWindowTitle(QCoreApplication.translate("dlg_NotesBrowser", u"Product Browser", None))
        self.l_identifier.setText(QCoreApplication.translate("dlg_NotesBrowser", u"Notes:", None))
        self.l_notes.setText(QCoreApplication.translate("dlg_NotesBrowser", u"Note:", None))
        self.l_notesRight.setText("")
    # retranslateUi


#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''Pychemqt, Chemical Engineering Process simulator
Copyright (C) 2009-2017, Juan José Gómez Romera <jjgomera@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.'''


###############################################################################
# Dialog to common data entry
#   -InputTableWidget: Widget for table data
#   -InputTableDialog: Dialog for table data
#   -eqDIPPR: Widget for select DIPPR equation
###############################################################################


import os

from PyQt5 import QtCore, QtGui, QtWidgets
from numpy import loadtxt

from lib.unidades import Temperature
from UI.widgets import Entrada_con_unidades, Tabla


class eqDIPPR(QtWidgets.QWidget):
    """Custom widget to define DIPPR equation input"""
    def __init__(self, value, parent=None):
        super(eqDIPPR, self).__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QtWidgets.QLabel(QtWidgets.QApplication.translate(
            "pychemqt", "Eq DIPPR") + " "))
        self.eqDIPPR = QtWidgets.QSpinBox()
        self.eqDIPPR.setValue(value)
        self.eqDIPPR.setRange(1, 9)
        self.eqDIPPR.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.eqDIPPR.setFixedWidth(50)
        txt = QtWidgets.QApplication.translate("pychemqt", "Equation") + "\n"
        txt += "\t1:\tY = A+B*T+C*T²+D*T³+E*T⁴\n"
        txt += "\t2:\tY = exp(A+B*T+C*ln(T)+D*T^E)\n"
        txt += "\t3:\tY = A*T^(B/(1+C*T+D*T^2))\n"
        txt += "\t4:\tY = A+B*exp(-C/T^D)\n"
        txt += "\t5:\tY = A + B/T + C/T³ + D/T⁸ + E/T⁹\n"
        txt += "\t6:\tY = A/(B^(1+(1-T/C)^D)\n"
        txt += "\t7:\tY = A*(1-Tr)^(B+C*Tr+D*Tr²+E*Tr³)\n"
        txt += "\t8:\tY = A+ B*((C/T)/sinh(C/T))² + D*((E/T)/cosh(E/T))²\n"
        txt += "\t9:\tY = A²/Tr+B-2ACTr-ADTr²-C²Tr³/3-CDTr⁴/2-D²Tr⁵/5\n"
        txt += QtWidgets.QApplication.translate("pychemqt", "where") + ":\n"
        txt += "\t" + QtWidgets.QApplication.translate(
            "pychemqt", "Y Property to fit") + "\n"
        txt += "\t" + QtWidgets.QApplication.translate(
            "pychemqt", "T temperature in Kelvin") + "\n"
        txt += "\t" + QtWidgets.QApplication.translate(
            "pychemqt", "Tr: reduced temperature T/Tc") + "\n"
        txt += "\t" + QtWidgets.QApplication.translate(
            "pychemqt", "A,B,C,D,E parameters")
        self.eqDIPPR.setToolTip(txt)
        layout.addWidget(self.eqDIPPR)
        layout.addStretch()

    @property
    def value(self):
        return self.eqDIPPR.value

    def setValue(self, value):
        self.eqDIPPR.setValue(value)

    def clear(self):
        self.eqDIPPR.clear()


class InputTableWidget(QtWidgets.QWidget):
    """Table data input dialog"""
    def __init__(self, columnas, data=None, t=[], property=[],
                 horizontalHeader=[], title="", DIPPR=False, hasTc=0,
                 Tc=None, eq=1, parent=None):
        """
        data: mrray with original data
        t: values for x column, generally temperature
        property: values for 2...n columns
        horizontalHeader: List with column title
        DIPPR: boolean to show DIPPR widget
        hasTc: boolean to show critical temperature (some DIPPR eq need it)
        Tc: value for critical temperature
        eq: Value for DIPPR equation
        """
        super(InputTableWidget, self).__init__(parent)
        self.columnas = columnas
        self.title = title
        gridLayout = QtWidgets.QGridLayout(self)
        gridLayout.setContentsMargins(0, 0, 0, 0)
        openButton = QtWidgets.QPushButton(QtGui.QIcon(QtGui.QPixmap(
            os.environ["pychemqt"]+"/images/button/fileOpen.png")), "")
        openButton.setToolTip(QtWidgets.QApplication.translate(
            "pychemqt", "Load data from a file"))
        openButton.clicked.connect(self.open)
        gridLayout.addWidget(openButton, 1, 1)
        saveButton = QtWidgets.QPushButton(QtGui.QIcon(QtGui.QPixmap(
            os.environ["pychemqt"]+"/images/button/fileSave.png")), "")
        saveButton.setToolTip(QtWidgets.QApplication.translate(
            "pychemqt", "Save data to a file"))
        saveButton.clicked.connect(self.save)
        gridLayout.addWidget(saveButton, 1, 2)
        clearButton = QtWidgets.QPushButton(QtGui.QIcon(QtGui.QPixmap(
            os.environ["pychemqt"]+"/images/button/clear.png")), "")
        clearButton.setToolTip(QtWidgets.QApplication.translate(
            "pychemqt", "Clear data"))
        clearButton.clicked.connect(self.delete)
        gridLayout.addWidget(clearButton, 1, 3)
        gridLayout.addItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed), 1, 4)

        self.tabla = Tabla(self.columnas, horizontalHeader=horizontalHeader,
                           verticalHeader=False, stretch=False)
        self.tabla.setConnected()
        if data:
            self.tabla.setData(data)
            self.tabla.addRow()
        elif t and property:
            self.tabla.setColumn(0, t)
            self.tabla.setColumn(1, property)
        gridLayout.addWidget(self.tabla, 2, 1, 1, 4)

        if DIPPR:
            self.eqDIPPR = eqDIPPR(eq)
            gridLayout.addWidget(self.eqDIPPR, 3, 1, 1, 4)
            self.eqDIPPR.eqDIPPR.valueChanged.connect(self.showTc)

            self.labelTc = QtWidgets.QLabel("Tc: ", self)
            gridLayout.addWidget(self.labelTc, 4, 1)
            self.tc = Entrada_con_unidades(Temperature, value=Tc)
            gridLayout.addWidget(self.tc, 4, 2, 1, 3)
            self.showTc(1)

    def showTc(self, value):
        """Show/hide Tc widget"""
        self.labelTc.setVisible(value in (7, 9))
        self.tc.setVisible(value in (7, 9))

    def open(self):
        """Load data from a test file"""
        fname, ext = QtWidgets.QFileDialog.getOpenFileName(
            self,
            QtWidgets.QApplication.translate("pychemqt", "Open text file"),
            "./")
        if fname:
            try:
                # Numpy raise error if use the fname directly and find a
                # non-latin1 character, inclusive in comment lines
                with open(fname, "rb") as file:
                    data = loadtxt(file)
                self.delete()
                self.tabla.setData(data)
            except ValueError as er:
                # Raise a error msg if the file can load by loadtxt, the user
                # can select any type of file and the input error is possible
                title = QtWidgets.QApplication.translate(
                    "pychemqt", "Failed to load file")
                msg = fname + "\n" + er.args[0]
                QtWidgets.QMessageBox.critical(self, title, msg)

    def save(self):
        """Save currend data of table to a file"""
        fname, ext = QtWidgets.QFileDialog.getSaveFileName(
            self,
            QtWidgets.QApplication.translate("pychemqt", "Save data to file"),
            "./")
        if fname:
            with open(fname, 'w') as file:
                file.write("#"+self.title+"\n")
                file.write("#")
                for i in range(self.tabla.columnCount()):
                    item = self.tabla.horizontalHeaderItem(i)
                    file.write(item.text()+"\t")
                file.write("\n")
                data = self.data
                for fila in range(len(data)):
                    for columna in range(self.tabla.columnCount()):
                        file.write(str(data[fila][columna])+"\t")
                    file.write("\n")

    def delete(self):
        """Clear table"""
        self.tabla.setRowCount(0)
        self.tabla.clearContents()
        self.tabla.addRow()

    @property
    def data(self):
        return self.tabla.getData()

    def column(self, column, magnitud=None, unit="conf"):
        """
        column: column to get
        magnitud: magnitud to get the values
        unit: unit of the values in table"""
        data = self.tabla.getColumn(column)
        if magnitud is not None:
            data = [magnitud(x, unit) for x in data]
        return data


class InputTableDialog(QtWidgets.QDialog):
    """Dialog to config thermal method calculations"""
    def __init__(self, columnas=2, help=False, helpFile="", **kwargs):
        """
        title: window title
        help: boolean to show help button
        helpFile: Path for help file, file or url
        """
        parent = kwargs.get("parent", None)
        super(InputTableDialog, self).__init__(parent)
        title = kwargs.get("title", "")
        self.setWindowTitle(title)
        self.helpFile = helpFile
        self.setWindowTitle(QtWidgets.QApplication.translate(
            "pychemqt", "Moody diagram configuration"))
        layout = QtWidgets.QVBoxLayout(self)
        self.widget = InputTableWidget(columnas, **kwargs)
        layout.addWidget(self.widget)
        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        if help:
            self.buttonBox.addButton(QtWidgets.QDialogButtonBox.Help)
            self.buttonBox.helpRequested.connect(self.ayuda)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

    def ayuda(self):
        """Show help file"""
        url = QtCore.QUrl(self.helpFile)
        QtGui.QDesktopServices.openUrl(url)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    titulo = "Distribución de tamaño de sólidos"
    encabezado = ["Diametro, μm", "Fracción másica", "acumulado"]
    ui = InputTableDialog(horizontalHeader=encabezado, title=titulo, help=True,
                          DIPPR=True, helpFile=os.environ["pychemqt"] +
                          "/docs/_build/lib.reaction.html")
    ui.show()
    sys.exit(app.exec_())

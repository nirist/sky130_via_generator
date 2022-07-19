#!/usr/bin/env python3

"""
    This Python script controlled with a GUI is used to generate layout
    of vias or via stacks for usage in the magIC VLSI layout tool with
    the open source SkyWater 130nm technology.
    
    Copyright (C) 2022 Nikola Ristic https://github.com/nirist

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import pathlib
import os as os

from PyQt5 import QtCore, QtWidgets, QtGui

# ---------------------- DRC RULES FOR VIAS ----------------------

# via1 rules
via1w = 26 # minimal width (square via)
via1d = 32 # minimal distance between 2 vias (from lower left corner of one to another)
via1b = 3 # minimal distance to m1 and m2 border

# via2 rules
via2w = 26
via2d = 40
via2b = 5

# via3 rules
via3w = 32
via3d = 40
via3b = 5

# via4 rules
via4w = 118
via4d = 160
via4b = 12

via_rules = []
via_rules.append([via1w, via1d, via1b])
via_rules.append([via2w, via2d, via2b])
via_rules.append([via3w, via3d, via3b])
via_rules.append([via4w, via4d, via4b])

log_text = ""

def generate_via(start_metal, end_metal, w, h):
    if not os.path.exists(str(pathlib.Path(__file__).parent.resolve()) + '/.magicrc'):
        update_log('Place your .magicrc file in the same path as this script.')
        return
    
    start_metal = start_metal + 1
    end_metal = end_metal + 1
    try:
        w = int(w)
        h = int(h)
    except ValueError:
        update_log("Check width and height.")
        return
    
    if start_metal >= end_metal:
        update_log("Start layer should be lower than end layer.")
        return
    
    
    # array for holding commands in strings
    commands = []
    commands.append('magic -dnull -noconsole << EOF')
    
    via_array = []
    for i in range(start_metal, end_metal):
        via_array.append(i)
        t = via_array[0]
        via_array[0] = via_array[-1]
        via_array[-1] = t
    
    # start from highest metal so that the via dimensions can be adjusted according to the worst condition for size of the topmost layer
    for via in via_array:
        # check if 1 via can fit horizontally and vertically
        w_ok = False
        h_ok = False
        wide = w > h
        
        if w > via_rules[via-1][0] + 2*via_rules[via-1][2]:
            w_ok = True
        else:
            w = via_rules[via-1][0] + 2*via_rules[via-1][2]
        if h > via_rules[via-1][0] + 2*via_rules[via-1][2]:
            h_ok = True
        else:
            h = via_rules[via-1][0] + 2*via_rules[via-1][2]
            
        # if both are at minimum increase one dimension to fit 2 vias
        if (w < 2*via_rules[via-1][0] + via_rules[via-1][1] + 2*via_rules[via-1][2]) and (h < 2*via_rules[via-1][0] + via_rules[via-1][1] + 2*via_rules[via-1][2]):
            if wide:
                w = 2*via_rules[via-1][0] + via_rules[via-1][1] + 2*via_rules[via-1][2]
            else:
                h = 2*via_rules[via-1][0] + via_rules[via-1][1] + 2*via_rules[via-1][2]
        
        
        # number of vias that can fit horizontally/vertically
        w_num_vias = (w - 2*via_rules[via-1][2] + via_rules[via-1][1] - via_rules[via-1][0])//via_rules[via-1][1]
        h_num_vias = (h - 2*via_rules[via-1][2] + via_rules[via-1][1] - via_rules[via-1][0])//via_rules[via-1][1]
        
        # start of lowest leftmost via
        w_start = (w - w_num_vias*via_rules[via-1][1] + (via_rules[via-1][1] - via_rules[via-1][0]))//2
        h_start = (h - h_num_vias*via_rules[via-1][1] + (via_rules[via-1][1] - via_rules[via-1][0]))//2
        
        # paint required metals
        commands.append('box size ' + str(w) + ' ' + str(h))
        commands.append('paint m' + str(via))
        commands.append('paint m' + str(via + 1))
        
        # set box size and move to starting location
        commands.append('box size ' + str(via_rules[via-1][0]) + ' ' + str(via_rules[via-1][0]))
        commands.append('move u ' + str(h_start))
        commands.append('move r ' + str(w_start))
        
        # move and paint all vias
        for i in range(h_num_vias):
            for j in range(w_num_vias):
                commands.append('paint v' + str(via))
                commands.append('move r ' + str(via_rules[via-1][1]))
            commands.append('move l ' + str(via_rules[via-1][1]*w_num_vias))
            commands.append('move u ' + str(via_rules[via-1][1]))
            
        # reset cursor box position
        commands.append('move d ' + str(via_rules[via-1][1]*h_num_vias + h_start))
        commands.append('move l ' + str(w_start))
    
    # make via name and check if same exists
    via_name = 'viaM' + str(start_metal) + 'M' + str(end_metal) + 'W' + str(w) + 'H' + str(h) + '.mag'
    via_path = ui.destPath.toPlainText()
    
    if os.path.exists(via_path + '/' + via_name):
        update_log('Same via already exists on destination path.')
        return
    
    # make path if necessary
    if not os.path.exists(via_path):
        os.makedirs(via_path)

    commands.append('save ' + via_path + '/' + via_name)
    commands.append('quit -noprompt')
    commands.append('EOF')
    
    # generate temporary magic shell script, run it and delete it afterwards
    script_name = 'temp.sh'
    with open(script_name, 'w') as f:
        for command in commands:
            f.write(command + '\n')
        
    os.system('chmod +x ' + script_name)
    os.system('./' + script_name)
    os.system('rm ' + script_name)
            
    update_log("Generated via M" + str(start_metal) + "-M" + str(end_metal) + " of size [" + str(w) + ", " + str(h) + "] at " + via_path + '/' + via_name)
    
    return

    
def update_log(text):
    global log_text
    log_text = log_text + text + "\n"
    ui.log.setText(log_text)
    
def open_licence():
    Licence.show()
    
    try:
        with open('LICENCE') as f:
            ui_licence.textBrowser.setPlainText(f.read())
    except FileNotFoundError:
        ui_licence.textBrowser.setPlainText('LICENCE file not found. View licence at https://www.gnu.org/licenses/gpl-3.0.html')
      

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(496, 544)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.height = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.height.setGeometry(QtCore.QRect(160, 150, 71, 25))
        self.height.setObjectName("height")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(20, 130, 51, 21))
        self.label_4.setObjectName("label_4")
        self.endLayer = QtWidgets.QComboBox(self.centralwidget)
        self.endLayer.setGeometry(QtCore.QRect(160, 100, 71, 25))
        self.endLayer.setObjectName("endLayer")
        self.endLayer.addItem("")
        self.endLayer.addItem("")
        self.endLayer.addItem("")
        self.endLayer.addItem("")
        self.endLayer.addItem("")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(160, 80, 71, 21))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(160, 130, 61, 21))
        self.label_3.setObjectName("label_3")
        self.destPath = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.destPath.setGeometry(QtCore.QRect(20, 30, 451, 31))
        self.destPath.setObjectName("destPath")
        self.width = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.width.setGeometry(QtCore.QRect(20, 150, 71, 25))
        self.width.setObjectName("width")
        self.startLayer = QtWidgets.QComboBox(self.centralwidget)
        self.startLayer.setGeometry(QtCore.QRect(20, 100, 71, 25))
        self.startLayer.setObjectName("startLayer")
        self.startLayer.addItem("")
        self.startLayer.addItem("")
        self.startLayer.addItem("")
        self.startLayer.addItem("")
        self.startLayer.addItem("")
        self.generateButton = QtWidgets.QPushButton(self.centralwidget)
        self.generateButton.setGeometry(QtCore.QRect(20, 190, 75, 23))
        self.generateButton.setObjectName("generateButton")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 80, 71, 21))
        self.label.setObjectName("label")
        self.log = QtWidgets.QTextBrowser(self.centralwidget)
        self.log.setGeometry(QtCore.QRect(20, 240, 451, 241))
        self.log.setObjectName("log")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(20, 220, 47, 20))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(20, 10, 101, 21))
        self.label_6.setObjectName("label_6")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 496, 21))
        self.menubar.setObjectName("menubar")
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLicence = QtWidgets.QAction(MainWindow)
        self.actionLicence.setObjectName("actionLicence")
        self.menuAbout.addAction(self.actionLicence)
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "sky130_via_generator"))
        self.label_4.setText(_translate("MainWindow", "Width:"))
        self.endLayer.setItemText(0, _translate("MainWindow", "M1"))
        self.endLayer.setItemText(1, _translate("MainWindow", "M2"))
        self.endLayer.setItemText(2, _translate("MainWindow", "M3"))
        self.endLayer.setItemText(3, _translate("MainWindow", "M4"))
        self.endLayer.setItemText(4, _translate("MainWindow", "M5"))
        self.label_2.setText(_translate("MainWindow", "End layer:"))
        self.label_3.setText(_translate("MainWindow", "Height:"))
        self.startLayer.setItemText(0, _translate("MainWindow", "M1"))
        self.startLayer.setItemText(1, _translate("MainWindow", "M2"))
        self.startLayer.setItemText(2, _translate("MainWindow", "M3"))
        self.startLayer.setItemText(3, _translate("MainWindow", "M4"))
        self.startLayer.setItemText(4, _translate("MainWindow", "M5"))
        self.generateButton.setText(_translate("MainWindow", "Generate"))
        self.label.setText(_translate("MainWindow", "Start layer:"))
        self.label_5.setText(_translate("MainWindow", "Log:"))
        self.label_6.setText(_translate("MainWindow", "Destination path:"))
        self.menuAbout.setTitle(_translate("MainWindow", "About"))
        self.actionLicence.setText(_translate("MainWindow", "Licence"))
        
class Ui_Licence(object):
    def setupUi(self, Licence):
        Licence.setObjectName("Licence")
        Licence.resize(490, 658)
        self.textBrowser = QtWidgets.QPlainTextEdit(Licence)
        self.textBrowser.setGeometry(QtCore.QRect(10, 10, 471, 641))
        self.textBrowser.setObjectName("textBrowser")

        self.retranslateUi(Licence)
        QtCore.QMetaObject.connectSlotsByName(Licence)

    def retranslateUi(self, Licence):
        _translate = QtCore.QCoreApplication.translate
        Licence.setWindowTitle(_translate("Licence", "Licence"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Main
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    # Licence
    Licence = QtWidgets.QWidget()
    ui_licence = Ui_Licence()
    ui_licence.setupUi(Licence)

    # make Tab not type \t for easy manuverability with keyboard
    ui.width.setTabChangesFocus(True)
    ui.height.setTabChangesFocus(True)
    ui.destPath.setTabChangesFocus(True)
    
    # add action to generateButton
    ui.generateButton.clicked.connect(lambda:generate_via(ui.startLayer.currentIndex() , ui.endLayer.currentIndex(), ui.width.toPlainText(), ui.height.toPlainText()))
    
    # add action to Licence
    ui.actionLicence.triggered.connect(lambda:open_licence())
    # fill path with current run path of script on start
    script_path = pathlib.Path(__file__).parent.resolve()
    ui.destPath.setPlainText(str(script_path))
       
    update_log('sky130_via_generator Copyright (C) 2022 Nikola Ristic https://github.com/nirist')
    update_log('This program comes with ABSOLUTELY NO WARRANTY.')
    update_log('This is free software, and you are welcome to redistribute it under certain conditions.')
    update_log('For details about the licence check the About section.')
    update_log('')
    update_log('This program is used to generate .mag files of vias for sky130 technology.')
    update_log('Make sure your .magicrc file is present in the location of the script.')
    update_log('')

    MainWindow.show()
    sys.exit(app.exec_())

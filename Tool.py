'''
Created on Aug 21, 2017
'''
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os
import time

import getAITS, getVReturn, getTrucks, insertVR_new, putResult


class Gui(QWidget):
    p1 = False
    p2 = False

    def __init__(self):
        super(Gui, self).__init__()
        self.initUI()

    def initUI(self):
        font = QFont("Microsoft YaHei", 16)

        self.label1 = QLabel("AITS派车结果:")
        self.label2 = QLabel("VR信息:")

        self.le1 = QLineEdit()
        self.le1.setFocusPolicy(Qt.NoFocus)
        self.le2 = QLineEdit()
        self.le2.setFocusPolicy(Qt.NoFocus)

        self.btn1 = QPushButton("选择文件")
        self.btn1.clicked.connect(self.selectAITS)
        self.btn2 = QPushButton("选择文件")
        self.btn2.clicked.connect(self.selectVR)
        self.btn3 = QPushButton("开始")
        self.btn3.setEnabled(False)
        self.btn3.clicked.connect(self.start)

        font_list = [self.label1, self.label2, self.le1, self.le2,
                     self.btn1, self.btn2, self.btn3]

        for w in font_list:
            w.setFont(font)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        l1 = QHBoxLayout()
        l1.addWidget(self.label1)
        l1.addStretch()
        main_layout.addLayout(l1)

        l2 = QHBoxLayout()
        l2.addWidget(self.le1)
        l2.addWidget(self.btn1)
        main_layout.addLayout(l2)

        l3 = QHBoxLayout()
        l3.addWidget(self.label2)
        l3.addStretch()
        main_layout.addLayout(l3)

        l4 = QHBoxLayout()
        l4.addWidget(self.le2)
        l4.addWidget(self.btn2)
        main_layout.addLayout(l4)

        main_layout.addStretch()
        l5 = QHBoxLayout()
        l5.addStretch()
        l5.addWidget(self.btn3)
        l5.addStretch()
        main_layout.addLayout(l5)
        main_layout.addStretch()

        self.setFixedSize(550, 250)

    def selectAITS(self):
        path = QFileDialog.getOpenFileName(self,"Open File Dialog","./",
                                           "Excel Files(*.xls;*.xlsx);;All Files(*.*)")
        self.le1.setText(path[0])

        if path[0]:
            self.p1 = True
        else:
            self.p1 = False

        if self.p1 and self.p2:
            self.btn3.setEnabled(True)
        else:
            self.btn3.setEnabled(False)

    def selectVR(self):
        path = QFileDialog.getOpenFileName(self,"Open File Dialog","./",
                                           "Excel Files(*.xls;*.xlsx);;All Files(*.*)")
        self.le2.setText(path[0])

        if path[0]:
            self.p2 = True
        else:
            self.p2 = False

        if self.p1 and self.p2:
            self.btn3.setEnabled(True)
        else:
            self.btn3.setEnabled(False)

    def start(self):
        self.btn3.setEnabled(False)

        AITS_name = self.le1.text()
        VR_name = self.le2.text()

        #读取AITS、VR和货车的数据
        getAITS.main1(AITS_name)
        print('AITS')
        getVReturn.main1(VR_name)
        print('VR')
        getTrucks.main1()
        print('truck')

        #派车方案调整、结果输出
        insertVR_new.main()
        putResult.main()
        print('All done')

        #需要一些收尾，temp文件删除等工作
        os.remove('tempA.txt')
        os.remove('tempV.txt')
        os.remove('tempT.txt')
        os.remove('output.txt')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    g = Gui()
    g.show()
    sys.exit(app.exec_())

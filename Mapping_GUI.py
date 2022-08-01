# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 08:53:23 2022

@author: REC3WX
"""

from PySide6.QtWidgets import QWidget, QPushButton, QFileDialog, QApplication, QLineEdit, QGridLayout, QLabel, QMessageBox, QPlainTextEdit, QFrame, QStyle
from PySide6.QtGui import QFont
from PySide6.QtCore import Slot, Qt
from lxml import etree
import re
import sys
import subprocess
import qdarktheme
# import PySide6
# import os

class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle('单据号补完工具 v0.3   - Made by REC3WX')
        pixmapi  = QStyle.SP_FileDialogContentsView
        icon = self.style().standardIcon(pixmapi)
        self.setWindowIcon(icon)
        self.setFixedSize(700, 300)
        

        self.fld_xml = QLabel('金税系统导出XML文件:')
        self.btn_xml = QPushButton('打开')
        self.btn_xml.clicked.connect(self.openxmlDialog)
        self.line_xml = QLineEdit()
        self.line_xml.setFixedWidth(400)
        self.line_xml.setClearButtonEnabled(True)
        #self.line_xml.setAcceptDrops(True)
        self.fld_txt = QLabel('批量导入结果TXT文件:')
        self.btn_txt = QPushButton('打开')
        self.btn_txt.clicked.connect(self.opentxtDialog)
        self.line_txt = QLineEdit()
        self.line_txt.setFixedWidth(400)
        self.line_txt.setClearButtonEnabled(True)
        #self.line_txt.setAcceptDrops(True)
        self.btn_start = QPushButton('开始')
        self.btn_start.clicked.connect(self.start)
        self.fld_result = QLabel('运行日志:')
        self.text_result = QPlainTextEdit()
        self.text_result.setReadOnly(True)
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.btn_show = QPushButton('打开结果文件')
        self.btn_show.clicked.connect(self.reset)
        self.btn_reset = QPushButton('清空')
        self.btn_reset.clicked.connect(self.reset)
        
        self.layout = QGridLayout()
        self.layout.addWidget((self.fld_xml), 0, 0)
        self.layout.addWidget((self.line_xml), 0, 1)
        self.layout.addWidget((self.btn_xml), 0, 2)
        self.layout.addWidget((self.fld_txt), 1, 0)
        self.layout.addWidget((self.line_txt), 1, 1)
        self.layout.addWidget((self.btn_txt), 1, 2)
        self.layout.addWidget((self.line), 2, 0, 1, 2)
        self.layout.addWidget((self.fld_result), 3, 0)
        self.layout.addWidget((self.text_result), 4, 0, 5, 2)
        self.layout.addWidget((self.btn_start), 5, 2, 1, 1)
        self.layout.addWidget((self.btn_show), 6, 2, 1, 1)
        self.layout.addWidget((self.btn_reset), 7, 2, 1, 1)

        self.setLayout(self.layout)

    @Slot()
    def openxmlDialog(self):
        # 生成文件对话框对象
        dialog = QFileDialog()
        # 设置文件过滤器，这里是任何文件，包括目录噢
        dialog.setFileMode(QFileDialog.ExistingFile)
        # 设置显示文件的模式，这里是详细模式
        dialog.setViewMode(QFileDialog.Detail)
        dialog.setNameFilter("XML文件 (*.xml)")
        if dialog.exec():
            fileNames = dialog.selectedFiles()
            self.line_xml.setText(fileNames[0])

    def opentxtDialog(self):
        # 生成文件对话框对象
        dialog = QFileDialog()
        # 设置文件过滤器，这里是任何文件，包括目录噢
        dialog.setFileMode(QFileDialog.ExistingFile)
        # 设置显示文件的模式，这里是详细模式
        dialog.setViewMode(QFileDialog.Detail)
        dialog.setNameFilter("TXT文件 (*.txt)")
        if dialog.exec():
            fileNames = dialog.selectedFiles()
            self.line_txt.setText(fileNames[0])

    def start(self):
        pattern = re.compile(r"单据号\d{10}")

        if self.line_xml.text() == '' or self.line_txt.text() == '':
            self.msgbox_err('错误', '文件选择有误，请重新选择！')
        else:
            xml = etree.parse(self.line_xml.text())  # 读取xml文件
            root = xml.getroot()  # 获取根节点

            for fphm in root.xpath('//Fphm'):
                for ancestor in fphm.iterancestors('Fp'):
                    djh = ancestor.find('./Djh')
                    # print('-----------', djh.text, '-----------')
                    with open(self.line_txt.text(), "r", encoding="gb2312") as mapping:
                        data = mapping.readlines()
                        for line in data:
                            if fphm.text in line:
                                try:
                                    hit = pattern.findall(line)[0]
                                    djh.text = hit[-10:]
                                    xml.write(self.line_xml.text(),
                                              pretty_print=True)
                                    success_text = str(
                                        f'修改成功！！发票号码 {fphm.text} 对应的单据号为 {djh.text}')
                                    self.text_result.appendPlainText(
                                        success_text)
                                except IndexError:
                                    # if not map:
                                    error_text = (
                                        f'匹配错误！！发票号码 {fphm.text} 未匹配到单据号，请检查TXT文件')
                                    self.text_result.appendPlainText(
                                        error_text)

    def msgbox_err(self, title, text):
        tip = QMessageBox(self)
        tip.setIcon(QMessageBox.Critical)
        tip.setWindowFlag(Qt.FramelessWindowHint)
        tip.setWindowTitle('错误')
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(9)
        tip.setFont(font)
        tip.setText(text)
        tip.exec()
        
    def showxml(self):
        if not self.text_result.toPlainText() == '':
            subprocess.Popen(
                ['C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                 self.line_xml.text()]
            )
        else:
            self.msgbox_err('错误', '请运行程序后再查看结果！')
            
    def reset(self):
        self.line_xml.setText('')
        self.line_txt.setText('')
        self.text_result.clear()
        
#dirname = os.path.dirname(PySide6.__file__)
#if not dirname == '':
#    plugin_path = os.path.join(dirname, 'plugins', 'platforms')
#    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()
app.setStyleSheet(qdarktheme.load_stylesheet())
font = QFont()
font.setFamily("Microsoft YaHei")
font.setPointSize(10)
app.setFont(font)
widget = MyWidget()
widget.show()
app.exec()

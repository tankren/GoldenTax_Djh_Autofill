from PySide6.QtWidgets import QWidget, QPushButton, QFileDialog, QApplication, QLineEdit, QGridLayout, QLabel, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, Slot
from lxml import etree
import re, os

class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        my_icon = QIcon()
        my_icon.addFile('icon.png')
        self.setWindowTitle('单据号补完工具 v0.1   - Made by Charlie')
        self.setWindowIcon(my_icon)

        self.fld_xml = QLabel('金税系统导出XML文件:')
        self.btn_xml = QPushButton('选择')
        self.btn_xml.clicked.connect(self.openxmlDialog)
        self.line_xml = QLineEdit()
        self.line_xml.setFixedWidth(300)
        self.line_xml.setClearButtonEnabled(True)
        #self.line_xml.setAcceptDrops(True)
        self.fld_txt = QLabel('批量导入结果TXT文件:')
        self.btn_txt = QPushButton('选择')
        self.btn_txt.clicked.connect(self.opentxtDialog)
        self.line_txt = QLineEdit()
        self.line_txt.setFixedWidth(300)
        self.line_txt.setClearButtonEnabled(True)
        #self.line_txt.setAcceptDrops(True)
        self.btn_start = QPushButton('开始')
        self.btn_start.clicked.connect(self.start)

        self.layout = QGridLayout()
        self.layout.addWidget((self.fld_xml), 0, 0)
        self.layout.addWidget((self.line_xml), 0, 1)
        self.layout.addWidget((self.btn_xml), 0, 2)
        self.layout.addWidget((self.fld_txt), 1, 0)
        self.layout.addWidget((self.line_txt), 1, 1)
        self.layout.addWidget((self.btn_txt), 1, 2)        
        self.layout.addWidget((self.btn_start), 2, 3)  

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
        if dialog.exec_():
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
        if dialog.exec_():
            fileNames = dialog.selectedFiles()
            self.line_txt.setText(fileNames[0])            

    def start(self):
        pattern = re.compile(r"\d{10}")

        if self.line_xml.text == '' or  self.line_txt.text == '':
            self.msgbox('错误', '请重新选择文件！')
        else:
            xml = etree.parse(self.line_xml.text)  # 读取xml文件
            root = xml.getroot()  # 获取根节点

            for fphm in root.xpath('//Fphm'):
                for ancestor in fphm.iterancestors('Fp'):
                    djh = ancestor.find('./Djh')
                    with open(self.line_txt.text, "r", encoding="gb2312") as mapping:
                        data = mapping.readlines()
                        for line in data:
                            if fphm.text in line:
                                map = pattern.findall(line)[0]
                                if not map:
                                    # print('发票号码',fphm.text,'未匹配到单据号')
                                    logger.info(f'发票号码{fphm.text}未匹配到单据号')
                                else:
                                    # print('匹配到的单据号为:',map,'修改XML单据号...')
                                    logger.info(f'匹配到的单据号为: {map} 修改XML单据号...')
                                    djh.text = map
                                    # newxml=xmlfile+'_new.xml'
                                    xml.write(xmlfile, pretty_print=True)
                                    # print('修改成功!!')
                                    logger.info('修改成功!!')
                            else:
                                self.message.error

    def msgbox(self, title, text):
        tip = QMessageBox()
        tip.setWindowTitle(title)
        tip.setText(text)
        tip.exec()

app = QApplication()
widget = MyWidget()
widget.show()
app.exec()

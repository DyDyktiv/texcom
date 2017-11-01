import sys
import os
import os.path
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QLineEdit, QPushButton, QGridLayout, \
    QCheckBox, QProgressBar, QFileDialog


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(480, 300)
        self.setWindowTitle('DOS-XML-MDB Converter')

        self.inBase = QLabel('Конвертируемая база данных:', self)
        self.inMode = QComboBox(self)
        self.inMode.addItems(['dos', 'xml', 'MDB'])
        self.inPath = QLineEdit(os.getcwd(), self)
        self.inPathPushDialog = QPushButton('Выбрать...', self)
        self.inPathPushDialog.clicked.connect(self.inputPath)
        self.inInfo = QLabel('', self)

        self.outBase = QLabel('Сохраниеть как:', self)
        self.outMode = QComboBox(self)
        self.outMode.addItems(['xml', 'MDB'])
        self.outPath = QLineEdit(os.path.expandvars('%APPDATA%'), self)
        self.outPathPushDialog = QPushButton('Выбрать...', self)
        self.outPathPushDialog.clicked.connect(self.outputPath)
        self.outInfo = QLabel('', self)

        self.hmode = QCheckBox('Сохранить структуру базы данных?', self)
        self.start = QPushButton('Приступить', self)
        self.progbar = QProgressBar(self)
        self.progbar.setValue(0)
        self.toInfo = QLabel('', self)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.inBase, 0, 0, 1, 3)
        grid.addWidget(self.inMode, 1, 0)
        grid.addWidget(self.inPath, 1, 1)
        grid.addWidget(self.inPathPushDialog, 1, 2)
        grid.addWidget(self.inInfo, 2, 0, 1, 3)

        grid.addWidget(self.outBase, 3, 0, 1, 3)
        grid.addWidget(self.outMode, 4, 0)
        grid.addWidget(self.outPath, 4, 1)
        grid.addWidget(self.outPathPushDialog, 4, 2)
        grid.addWidget(self.outInfo, 5, 0, 1, 3)

        grid.addWidget(self.hmode, 6, 0, 1, 3)
        grid.addWidget(self.start, 7, 0, 1, 3)
        grid.addWidget(self.progbar, 8, 0, 1, 3)
        grid.addWidget(self.toInfo, 9, 0, 1, 3)

        self.setLayout(grid)
        self.show()

    def inputPath(self):
        file = os.path.normpath(QFileDialog.getExistingDirectory(self))
        self.inPath.setText(file)

    def outputPath(self):
        file = os.path.normpath(QFileDialog.getExistingDirectory(self))
        self.outPath.setText(file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

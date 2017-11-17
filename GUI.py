import sys
import os
import os.path
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QLineEdit, QPushButton, QGridLayout, \
    QCheckBox, QProgressBar, QFileDialog, QDialog


import tc_analize
import tc_classes


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
        self.start.clicked.connect(self.startWork)
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

    def startWork(self):
        self.start.blockSignals(True)
        intype = self.inMode.currentText()
        inpath = os.path.normpath(self.inPath.text()).replace('\\', '/')

        outtype = self.outMode.currentText()
        outpath = os.path.normpath(self.outPath.text()).replace('\\', '/')

        strapt = self.hmode.isChecked()

        '''
        print('Input database:')
        print('Type:', intype)
        print('Path:', inpath)
        print('Output database')
        print('Type:', outtype)
        print('Path', outpath)
        print('Mode:', strapt)
        #'''

        analize = tc_analize.analize(inpath, intype)

        errorcount = 0
        errorpath = os.path.join(outpath, 'errors.log')
        ferror = open(errorpath, 'w', encoding='utf-8')
        ferror.close()
        size = 0
        self.progbar.setValue(1)
        p = analize.fullsize//99
        for f in analize.files:
            f.read(intype)
            if f.error:
                errorcount += 1
                ferror = open(errorpath, 'a', encoding='utf-8')
                if intype == 'dos':
                    ferror.write('{} {} {}\n'.format(f.dos_name, f.error.name, f.error.note))
                ferror.close()
            else:
                f.save(outtype, outpath)
            size += f.size
            self.progbar.setValue(1 + size//p)
        if errorcount == 0:
            os.remove(errorpath)
        self.infodialog(len(analize.files), errorcount)
        self.start.blockSignals(False)

    def infodialog(self, all, errors=None):
        d = QDialog()
        d.setWindowTitle("info")
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(QLabel('Обработано файлов: {}'.format(all)), 0, 0)
        if errors:
            grid.addWidget(QLabel('Успешно: {}'.format(all-errors)), 1, 0)
            grid.addWidget(QLabel('Список ошибок в errors.log'), 2, 0)
        else:
            grid.addWidget(QLabel('Ошибок нет', 1, 0)
        d.setLayout(grid)
        d.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

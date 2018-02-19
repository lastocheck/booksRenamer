import requests, os, sys, urllib, re
from PyQt5 import QtCore, QtWidgets, QtGui

class MyLineEdit(QtWidgets.QLineEdit):

    mousePressedSignal = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, *args):
        QtWidgets.QLineEdit.__init__(self, *args)

    def mousePressEvent(self, event):
        self.mousePressedSignal.emit(event.pos())

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init()

    def init(self):
                
        client = QtWidgets.QWidget()
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(client)
        scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.grid = QtWidgets.QGridLayout()
        client.setLayout(self.grid)
        self.setCentralWidget(scrollArea)

        #self.setCentralWidget(QtWidgets.QWidget(self))
        #self.grid = QtWidgets.QGridLayout()
        #self.centralWidget().setLayout(self.grid)

        self.statusBar()

        self.fileTextBox = MyLineEdit()
        self.fileTextBox.setMinimumWidth(300)
        self.fileTextBox.setReadOnly(True)
        self.fileTextBox.setPlaceholderText("Choose a folder")
        self.fileTextBox.mousePressedSignal.connect(self.showFileDialog)

        self.grid.addWidget(self.fileTextBox, 0, 0, 1, 2)

        self.setWindowTitle("xd")
        self.show()

    def showFileDialog(self):
        self.folderName = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose a directory")
        self.fileTextBox.setText(self.folderName)
        #self.fileTextBox.setText("C:/Users/foxy/Documents/xd")
        self.showBooks()

    def showBooks(self):
        if self.fileTextBox.text() == '':
            return

        rowCount = 1
        maxWidth = 0
        with os.scandir(self.fileTextBox.text()) as it:
            for entry in it:
                if entry.name.endswith("fb2"):
                    self.grid.addWidget(QtWidgets.QLabel(entry.name), rowCount, 1)
                    edit = QtWidgets.QLineEdit(self.translate(entry.name))
                    #edit.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)  
                    fm = QtGui.QFontMetrics(edit.fontMetrics())
                    width = fm.width(edit.text()) + 10
                    edit.setFixedWidth(width)
                    if width > maxWidth:
                        maxWidth = width

                    self.grid.addWidget(edit, rowCount, 2)
                    rowCount += 1
        self.setMinimumSize(maxWidth*2 + 50, 500)
        self.createRenameButton(rowCount)

    def createRenameButton(self, rowCount):
        self.renameButton = QtWidgets.QPushButton("Rename")
        self.renameButton.clicked.connect(self.rename)
        self.grid.addWidget(self.renameButton, rowCount, 1, 1, 2)

    def rename(self):
        print(self.grid.itemAtPosition(5, 1).widget().text())
        print(self.grid.rowCount())
        for row in range(1, self.grid.rowCount()-1):
            filename = self.folderName + '/' + self.grid.itemAtPosition(row, 1).widget().text()
            newname = self.folderName + '/' + self.grid.itemAtPosition(row, 2).widget().text()
            os.rename(filename, newname)

        print("success")
        succMessage = QtWidgets.QMessageBox()
        succMessage.setWindowTitle("Success")
        succMessage.setText("Renaming complete! Do you want to exit?")
        succMessage.setStandardButtons(QtWidgets.QMessageBox.Yes)
        succMessage.addButton(QtWidgets.QMessageBox.No)
        succMessage.setDefaultButton(QtWidgets.QMessageBox.Yes)
        if (succMessage.exec_() == QtWidgets.QMessageBox.Yes):
            print("QtWidgets.QApplication.quit()")
            QtWidgets.QApplication.quit()


    def translate(self, text):
        text = text[:text.find('.')]
        text = text.replace("_", " — ")
        text = text.replace("-", " ")
        #args = {"key" : "trnsl.1.1.20180217T163734Z.fcd0705176f17e04.77ef79b3ade14fb4d188e45c474fd60ab789d21e", "text" : text, "lang" : "ru", "format" : "plain"}
        #r = requests.post("https://translate.yandex.net/api/v1.5/tr/translate", data=args)
        #text = r.text[82:-21]
        
        capitalDouble = {u'Zh' : u'Ж', u'Ts' : u'Ц', u'Ch' : u'Ч', u'Sh' : u'Ш', u'Yu' : u'Ю', u'Ya' : u'Я'}
        double = {u'zh' : u'ж', u'ts' : u'ц', u'ch' : u'ч', u'sh' : u'ш', u'yu' : u'ю', u'ya' : u'я'}
        small = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e',
        'з':'z','и':'i','к':'k','л':'l','м':'m','н':'n',
        'о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h',
        'ц':'c'}
        capital = {}
        for key in small.keys():
            capital[key.upper()] = small[key].upper()

        

        #tranlating capital two-character letters
        for twoletters, value in capitalDouble.items():
            for m in re.finditer(twoletters, text):
                text = text[:m.start()] + value + text[m.end():]

        #translating small two-character letters
        for twoletters, value in double.items():
            index = 0
            while index < len(text):
                index = text.find(twoletters, index)
                if index == -1:
                    break
                text = text[:index] + value + text[index + 2:]
                index += 1

        for cyrillic, latin in capital.items():
            text = text.replace(latin, cyrillic) 

        #translating one-character small letters
        for cyrillic, latin in small.items():
            text = text.replace(latin, cyrillic) 
        
        #translating "y" letters
        index = 0
        while index < len(text):
            index = text.find('y', index)
            if index == -1:
                break

            if index+1 != len(text):
                replacement = 'й' if text[index+1] == ' ' else 'ы'
            else:
                replacement =  'й'
            text = text[:index] + replacement + text[index + 1:]
            index += 1

        text = text + '.fb2'
        return text
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())


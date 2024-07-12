import sys
import cv2
import os
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow,QMenuBar,QMenu,QAction,QWidget,QGridLayout, QPushButton,QFileDialog, QMessageBox)
from PyQt5.QtGui import QImage,QPixmap
from model import PredictionModel
from PIL import Image

class Window(QMainWindow):
    CAMERA = 0
    FOLDER = 1
    def __init__(self,parent=None):
        super().__init__(parent)
        self.initMainWindow()
        self.source = Window.CAMERA
        self.path = ''
        self.camera = cv2.VideoCapture(0)
        self.imageFileList = []
        self.imageIndex = 0
        self.score = 0
        self.readingFolderImages = False
        self.addTimer()
        self.model = PredictionModel()
        #self.model.load()
        # print(self.model.predict(Image.open('img.jpg')))
        #print(self.model.predict('1.png'))
    
    def addTimer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.timerHandler)
        self.count = 0

    def timerHandler(self):
        self.updateImage()
        
    def updateImage(self):
        try:
            fn = self.imageFileList[self.imageIndex % len(self.imageFileList)]
            self.imageIndex = self.imageIndex + 1
            frame = cv2.imread(fn)
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ConvertToQtFormat = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
            qimg = ConvertToQtFormat.scaled(900, 700)
            self.imgLabel.setPixmap(QPixmap.fromImage(qimg))
            self.scoreImage(fn)
            if self.imageIndex == len(self.imageFileList):
                self.readingFolderImages = False
                self.timer.stop()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("No matching image found")
                msg.setWindowTitle("Drawn!!!")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
        except Exception as e:
            print(e)
        
     
    def imgFolderActionHandler(self): 
        try:
            self.path = QFileDialog.getExistingDirectory(self,caption="Select images folder")
            files = os.listdir(self.path)
            fl = []
            for f in files:
                if f.endswith('.jpg') | f.endswith('.png'):
                    fl.append(self.path+'/'+f)
            self.imageFileList = fl
            if len(self.imageFileList) < 1:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Please select a folder with at least one image")
                msg.setWindowTitle("Image folder selection error")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                self.readingFolderImages = True
                self.imageIndex = 0
                self.timer.start()
        except Exception as e:
            print(e)
    
    def updateScore(self,s):
        self.score = s
        print(self.score)
        print('updating socre')
        self.scoreValueLabel.setText(str(int(self.score)))
    
    def endGame(self):
        self.readingFolderImages = False
        self.timer.stop()

    def scoreImage(self,img):
        # read image for score
        # if score same end game self.endGame()
        res = self.model.predict(img)
        try:
            if res[0] == res[1]:
                print('end')
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Game ends!!! Both have value "+str(int(res[0].item())+1))
                msg.setWindowTitle("!!!OVER!!!")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                self.endGame()
            else:
                self.score = self.score + res[0] + res[1] + 2
                self.updateScore(self.score.item())
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(str(e))
            msg.setWindowTitle("image processing error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        

    def startButtonHandler(self):
        if self.readingFolderImages:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Reading from images folder")
            msg.setWindowTitle("Wait!!!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            self.updateScore(0)
            self.startButton.setText('START')
    
    def scoreButtonHandler(self):
        if self.readingFolderImages:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Reading from images folder")
            msg.setWindowTitle("Wait!!!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            if self.score == 0:
                self.startButton.setText('START')
            else:
                self.startButton.setText('RESTART')
            ret,frame = self.camera.read()
            if ret:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = cv2.flip(img, 1)
                ConvertToQtFormat = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
                qimg = ConvertToQtFormat.scaled(900, 700)
                self.imgLabel.setPixmap(QPixmap.fromImage(qimg))
                self.scoreImage(frame)

    def initMainWindow(self):
        self.setWindowTitle("Two Dice Game using Object Detection")
        self.resize(900, 768)
        self.centralWidget = QWidget(self)
        self.centralWidgetLayout = QGridLayout()
        self.startButton = QPushButton(self)
        self.startButton.setText('START')
        self.scoreButton = QPushButton(self)
        self.scoreButton.setText('SCORE')
        self.startButton.clicked.connect(self.startButtonHandler)
        self.scoreButton.clicked.connect(self.scoreButtonHandler)
        self.folderReadButton = QPushButton(self)
        self.folderReadButton.setText('Test Folder Images')
        self.startButton.clicked.connect(self.startButtonHandler)
        self.folderReadButton.clicked.connect(self.imgFolderActionHandler)
        self.imgLabel = QLabel("Central label")
        self.scoreLabel = QLabel("Score : ")
        self.scoreValueLabel =  QLabel("0")
        self.centralWidgetLayout.addWidget(QLabel(''),0,0,1,1)
        self.centralWidgetLayout.addWidget(self.scoreLabel,0,1,1,1)
        self.centralWidgetLayout.addWidget(self.scoreValueLabel,0,2,1,1)
        self.centralWidgetLayout.addWidget(self.imgLabel,1,0,10,3)
        self.centralWidgetLayout.addWidget(self.startButton,11,0,1,1)
        self.centralWidgetLayout.addWidget(self.scoreButton,11,1,1,1)
        self.centralWidgetLayout.addWidget(self.folderReadButton,11,2,1,1)
        self.centralWidget.setLayout(self.centralWidgetLayout)
        self.setCentralWidget(self.centralWidget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
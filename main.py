# main_app.py

import sys
from os import path

import cv2
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUiType
from PyQt5.QtGui import QPixmap, QImage
from imageDisplay import ImageDisplay

FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "design.ui"))

class MainApp(QMainWindow, FORM_CLASS):

    def __init__(self, parent=None):
        super().__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Image Mixer")
        self.verticalSlider_1.valueChanged.connect(self.on_changed)
        self.verticalSlider_2.valueChanged.connect(self.on_changed)
        self.verticalSlider_3.valueChanged.connect(self.on_changed)
        self.verticalSlider_4.valueChanged.connect(self.on_changed)
        self.labels = [self.label_2, self.label_3, self.label_4, self.label_5]

        self.verticalSlider_1.setValue(0)
        self.verticalSlider_2.setValue(0)
        self.verticalSlider_3.setValue(0)
        self.verticalSlider_4.setValue(0)
        # Create instances of ImageDisplay for each label
        self.image_display1 = ImageDisplay(self.imageLabel1, self.imageComponent1, self.imageComboBox1,self.label_2,self.comboBox_5,self.outputImage1,self.outputImage2)
        self.image_display2 = ImageDisplay(self.imageLabel2, self.imageComponent2, self.imageComboBox2,self.label_3, self.comboBox_5,self.outputImage1,self.outputImage2)
        self.image_display3 = ImageDisplay(self.imageLabel3, self.imageComponent3, self.imageComboBox3,self.label_4,self.comboBox_5 ,self.outputImage1,self.outputImage2)
        self.image_display4 = ImageDisplay(self.imageLabel4, self.imageComponent4, self.imageComboBox4,self.label_5, self.comboBox_5,self.outputImage1,self.outputImage2)
        # Assign the label and component attributes separately
        self.image_display_label1 = self.image_display1.label
        self.image_component1 = self.image_display1.image_component

        self.newimage =None
        self.image_display_label2 = self.image_display2.label
        self.image_component2 = self.image_display2.image_component

        self.image_display_label3 = self.image_display3.label
        self.image_component3 = self.image_display3.image_component

        self.image_display_label4 = self.image_display4.label
        self.image_component4 = self.image_display4.image_component


        # Connect the double-clicked signal to the corresponding on_label_double_clicked function
        self.imageLabel1.mouseDoubleClickEvent = self.image_display1.on_label_double_clicked
        self.imageLabel2.mouseDoubleClickEvent = self.image_display2.on_label_double_clicked
        self.imageLabel3.mouseDoubleClickEvent = self.image_display3.on_label_double_clicked
        self.imageLabel4.mouseDoubleClickEvent = self.image_display4.on_label_double_clicked

        # Connect the combo box change signal to the handle_combobox_change function
        self.imageComboBox1.currentIndexChanged.connect(self.image_display1.handle_combobox_change)
        self.imageComboBox2.currentIndexChanged.connect(self.image_display2.handle_combobox_change)
        self.imageComboBox3.currentIndexChanged.connect(self.image_display3.handle_combobox_change)
        self.imageComboBox4.currentIndexChanged.connect(self.image_display4.handle_combobox_change)
        # Connect the combination signal to the combination function
        self.radioButton1.setChecked(True)
        self.radioButton1.toggled.connect(self.on_changed)
        self.radioButton2.toggled.connect(self.changelabel)
        self.pushButton.clicked.connect(lambda :self.press_Apply(self.newimage))

    def changelabel(self):
        if self.radioButton2.isChecked():
            for label in self.labels:
                label.setText("Real/Imaginary")
        else:
            for label in self.labels:
                label.setText("Magnitude/Phase")

    def press_Apply(self,newimage):
        
        index = self.comboBox_5.currentIndex()
        
        resized_image = cv2.resize(newimage, (1500, 500), interpolation=cv2.INTER_AREA)
        
        height, width = resized_image.shape
        bytes_per_line = width
        q_image = QImage(resized_image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)
        

        if index==0 :
            scaled_pixmap = pixmap.scaled(self.outputImage1.size(), aspectRatioMode=Qt.KeepAspectRatio)
            self.outputImage1.setPixmap(scaled_pixmap)
        else:
            scaled_pixmap = pixmap.scaled(self.outputImage2.size(), aspectRatioMode=Qt.KeepAspectRatio)
            self.outputImage2.setPixmap(scaled_pixmap)

    def on_changed(self):
            # Fetch current indexes of other comboboxes    
            slider_1 = self.verticalSlider_1.value()
            slider_2 = self.verticalSlider_2.value()
            slider_3 = self.verticalSlider_3.value()
            slider_4 = self.verticalSlider_4.value()
            
            if self.radioButton1.isChecked():
                index = 0
            else:
                index = 1
            
    # Fetch current indexes of other comboboxes
            self.newimage = ImageDisplay.combination(self.image_display1, self.image_display2, self.image_display3, self.image_display4,
                                    index, slider_1, slider_2, slider_3, slider_4)
            self.newimage = cv2.normalize(self.newimage, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)




def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
